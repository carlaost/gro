# Proposer 4 — Metrics for `logic/claims.md`

All functions assume a parsed representation of one artifact's claims as
`claims: List[Claim]`, where:

```python
# Claim = {
#   "id": "C01",
#   "title": str,
#   "statement": str,
#   "status": str,              # "hypothesis" | "supported" | "refuted",
#                                # possibly with a parenthetical qualifier
#   "falsification": str,       # "Falsification criteria" prose
#   "proof": List[str],         # experiment ref ids, e.g. ["E01"]
#   "evidence_basis": str,
#   "interpretation": str,      # "" / None if the (optional) field was omitted
#   "dependencies": List[str],  # claim ids this claim depends on, [] if "none"
#   "sources": List[Source],
#   "tags": List[str],
# }
# Source = {
#   "value": str,      # exact text in backticks
#   "ref": str,         # file-or-section-ref
#   "locator": str,     # the (...) locator, e.g. "Table 2, Outcome 1, Rank 1"
#   "quote": str,       # text inside «...»; "" if missing/bare path
#   "tag": str,         # "input" | "result"
#   "pending": bool,    # True if this was a [pending: ...] entry
# }
```

All scores are in `[0, 1]`; higher = more "good science" signal. Every
function below is written so that a missing/thin/empty input (empty
`sources`, empty `interpretation`, empty `claims` list, no non-`supported`
claims, etc.) is a **penalized outcome it computes to**, not a case it skips.

---

## 1. Falsifiability Operationalization Score

**How it signals good science.** A `Falsification criteria` field existing
is not enough — Popperian rigor requires the disconfirming observation to be
*operational*: a specific number, threshold, direction, or comparator that
someone could check against new data. "This claim is refuted if the results
don't hold" is unfalsifiable in practice even though the field is populated.
Papers that pre-register precise kill conditions (a CI crossing zero, a
specific rank reversal, a named comparator failing to replicate) are doing
harder, more falsifiable science than papers that gesture at falsifiability
generically.

**Compute function.**

```python
import re

NUMERIC_RE = re.compile(r'-?\d+\.?\d*\s*%?')
COMPARATOR_WORDS = [
    "greater than", "less than", "non-significant", "not significant",
    "crossing 0", "crosses 0", "fails to replicate", "outrank", "outranked",
    "underperform", "reversed", "no difference", "below", "above", "exceeds",
    "fell short", "failed to reach", "did not reach", "lower than", "higher than",
]

def falsifiability_operationalization_score(claims):
    scores = []
    for c in claims:
        fals = (c.get("falsification") or "").strip()
        if not fals:
            scores.append(0.0)
            continue
        has_number = bool(NUMERIC_RE.search(fals))
        has_comparator = any(w in fals.lower() for w in COMPARATOR_WORDS)
        stmt_tokens = set(re.findall(r"[a-z]{4,}", (c.get("statement") or "").lower()))
        fals_tokens = set(re.findall(r"[a-z]{4,}", fals.lower()))
        overlap = len(stmt_tokens & fals_tokens) / max(1, len(fals_tokens))
        # High overlap with the Statement AND no number/comparator means the
        # field is just restating the claim ("refuted if this isn't true"),
        # not specifying an operational alternative outcome.
        generic_penalty = 1.0 if (overlap > 0.6 and not (has_number or has_comparator)) else 0.0
        length_score = min(1.0, len(fals.split()) / 15.0)
        raw = 0.45 * has_number + 0.35 * has_comparator + 0.2 * length_score
        raw *= (1 - 0.7 * generic_penalty)
        scores.append(max(0.0, min(1.0, raw)))
    return sum(scores) / len(scores) if scores else 0.0
```

**What the function does & why.** For each claim it checks the
`falsification` text for (a) a concrete number/percentage, (b) a directional
comparator word, and (c) enough length to actually spell out a scenario. It
then computes how much the falsification text merely echoes the statement's
own vocabulary rather than introducing a new, checkable condition — if it's
mostly a restatement with no number or comparator, the score is knocked down
by up to 70%. An empty field scores zero outright rather than being excluded.
Averaging over all claims rewards artifacts that operationalize falsification
consistently, not just for one showcase claim.

**Why it's hard to Goodhart.** A compiler can't cheaply inflate this by just
copy-pasting a number into the field — the number has to differ enough from
the statement's own vocabulary (the overlap penalty) to count as a genuine
alternative outcome, and it still has to coexist with the other metrics below
(e.g., grounding fidelity checks that numbers appearing anywhere are
traceable). Padding every claim with a fake precise-sounding threshold that
isn't grounded in `Sources` will look good here but tank Metric 2.

---

## 2. Grounding Fidelity & Numeric Coverage Score

**How it signals good science.** The artifact's central discipline (per the
shape doc's "Grounding discipline", Rule 16) is that every load-bearing
number in a `Statement` traces to a verbatim quote at a specific locator.
This is the mechanism that makes a claim auditable rather than merely
assertive — it's the difference between "the paper says X" and "here is
exactly where X came from, in the paper's own words." A claim that states
precise numbers but backs them with bare paths, missing quotes, or numbers
that don't actually appear in the cited text is doing the rhetorical work of
precision without the epistemic substance of it.

**Compute function.**

```python
NUM_TOKEN_RE = re.compile(r'\d+\.?\d*')

def _numbers_in(text):
    return set(NUM_TOKEN_RE.findall(text or ""))

def grounding_fidelity_score(claims):
    claim_scores = []
    for c in claims:
        stmt_numbers = _numbers_in(c.get("statement", ""))
        sources = c.get("sources") or []
        if not sources:
            # No grounding entries at all: maximal failure, regardless of how
            # many numbers the Statement asserts.
            claim_scores.append(0.0)
            continue

        valid_entries = 0.0
        covered_numbers = set()
        for s in sources:
            quote = (s.get("quote") or "").strip()
            value = (s.get("value") or "").strip()
            locator = (s.get("locator") or "").strip()
            is_pending = bool(s.get("pending")) or quote.lower().startswith("pending")
            quote_ok = bool(quote) and not is_pending
            value_in_quote = quote_ok and value != "" and value in quote

            if quote_ok and value_in_quote and locator:
                entry_validity = 1.0
            elif is_pending:
                # Honest about an unverified source, but still a real gap --
                # rewarded relative to silent fabrication, penalized relative
                # to a verified quote.
                entry_validity = 0.3
            else:
                entry_validity = 0.0  # bare path / missing quote / value not verbatim

            valid_entries += entry_validity
            if entry_validity > 0:
                covered_numbers |= (_numbers_in(value) & stmt_numbers)

        validity_ratio = valid_entries / len(sources)
        # A quantitative, falsifiable claim with zero numbers to ground is
        # itself a weak case for this artifact type -- scored as no coverage,
        # not skipped as "nothing to check."
        coverage_ratio = (len(covered_numbers) / len(stmt_numbers)) if stmt_numbers else 0.0

        claim_scores.append(validity_ratio * coverage_ratio)
    return sum(claim_scores) / len(claim_scores) if claim_scores else 0.0
```

**What the function does & why.** For every claim, it extracts the numbers
asserted in `Statement`, then checks each `Sources` entry for three things: a
non-placeholder quote, that quote actually containing the claimed value
verbatim, and a real locator. `[pending: ...]` entries get partial (not
zero, not full) credit — the shape doc explicitly frames pending as "honesty,
not a shortcut," but it's still an unverified number. It then multiplies
"how many of my sources are actually valid" by "how much of what I asserted
is actually covered by a valid source" — a claim can't score well by having
one perfectly-quoted source next to five numbers nobody grounded.

**Why it's hard to Goodhart.** Gaming this by inventing lots of `Sources`
entries with fabricated quotes requires the fabricated quote to *contain* the
exact value — any laziness (rounding, paraphrase, omitted digits) breaks the
substring match and zeroes that entry. Gaming it by only ever making claims
with round, easy-to-plant numbers is caught by Metric 1 (which wants
operational precision) and Metric 5 (which wants documentation symmetry
across claim types) — an artifact that games grounding by keeping claims
numerically simple will look suspiciously thin on those axes.

---

## 3. Evidence–Interpretation Separation & Value-Smuggling Score

**How it signals good science.** The shape doc explicitly flags two related
defects: `Interpretation` collapsing into `Evidence basis` (no separation of
raw support from broader reading), and editorializing language (e.g. "the
authors argue is effectively obsolete") being smuggled into `Statement` or
`Evidence basis` as if it were a directly measured quantity, rather than
confined to the field designed to hold interpretive gloss. Good science keeps
"what the data show" and "what we think it means" typographically and
epistemically separate so a downstream reader can accept the former while
disputing the latter.

**Compute function.**

```python
STOPWORDS = set("the a an of in on for to and or with that this which was were "
                 "is are as by at from into".split())
EVALUATIVE_TERMS = [
    "obsolete", "clearly", "definitively", "proves", "conclusively", "best",
    "superior", "groundbreaking", "should", "must", "undeniably",
    "revolutionary", "flawed", "invalid", "worthless", "gold standard",
    "state of the art",
]

def _content_tokens(text):
    return {w for w in re.findall(r"[a-z']{3,}", (text or "").lower()) if w not in STOPWORDS}

def evidence_interpretation_separation_score(claims):
    scores = []
    for c in claims:
        evidence = c.get("evidence_basis") or ""
        interp = (c.get("interpretation") or "").strip()
        statement = c.get("statement") or ""

        if not interp:
            # Interpretation is schema-optional, but an artifact that never
            # exercises the field designed to isolate synthesis from evidence
            # cannot be verified as keeping them apart -- scored thin, not
            # skipped as not-applicable.
            scores.append(0.2)
            continue

        ev_tok, in_tok = _content_tokens(evidence), _content_tokens(interp)
        overlap = len(ev_tok & in_tok) / max(1, len(ev_tok | in_tok))
        collapse_penalty = max(0.0, overlap - 0.5) * 2  # >50% shared vocab -> collapsing

        smuggle_hits = (sum(t in statement.lower() for t in EVALUATIVE_TERMS) +
                        sum(t in evidence.lower() for t in EVALUATIVE_TERMS))
        smuggle_penalty = min(1.0, 0.4 * smuggle_hits)

        raw = 1.0 - 0.5 * collapse_penalty - 0.5 * smuggle_penalty
        scores.append(max(0.0, min(1.0, raw)))
    return sum(scores) / len(scores) if scores else 0.0
```

**What the function does & why.** It measures vocabulary overlap between
`Evidence basis` and `Interpretation` — heavy overlap means the compiler
duplicated the evidence prose into the interpretation slot rather than
actually synthesizing anything, which the shape doc treats as a quality
defect. Separately, it scans `Statement` and `Evidence basis` (the two fields
that are supposed to be strictly factual/measured) for evaluative or
totalizing language — words that belong in a hedged `Interpretation`, not in
a field presenting itself as a directly grounded fact. Missing
`Interpretation` entirely is scored at a fixed low value rather than excluded,
per the hard constraint.

**Why it's hard to Goodhart.** Simply deleting `Interpretation` to dodge the
collapse-penalty check triggers the fixed missing-field penalty instead — you
can't escape by omission. Padding `Interpretation` with paraphrased synonyms
to avoid the overlap check still has to avoid using evaluative words in
`Statement`/`Evidence basis`, which is a separate, independently-checked
condition; gaming one axis (say, moving all evaluative language into
`Interpretation` to score well here) has no cost on this metric alone but
produces a paper whose `Statement`s are barer and more literal, which the
`Falsifiability` metric (Metric 1) tends to reward, not punish — so this
particular interaction is not self-defeating by itself, which is exactly why
it's combined with grounding and calibration below.

---

## 4. Dependency Graph Coherence Score

**How it signals good science.** Cumulative science builds later findings on
properly cited earlier ones — a genuine research narrative has a directed,
acyclic structure where dependent claims still carry their own evidence
rather than merely inheriting the credibility of an anchor claim. Claims that
depend on each other circularly, that reference a later claim that hasn't
been established yet, or that lean on prior claims while contributing zero
grounding of their own are structurally weaker than a claim graph that is a
clean DAG with each node pulling its own evidentiary weight.

**Compute function.**

```python
def dependency_graph_coherence_score(claims):
    if not claims:
        return 0.0

    ids = [c["id"] for c in claims]
    index = {cid: i for i, cid in enumerate(ids)}
    graph = {c["id"]: (c.get("dependencies") or []) for c in claims}

    # 1. Cycle detection.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {cid: WHITE for cid in ids}
    has_cycle = [False]

    def dfs(u):
        color[u] = GRAY
        for v in graph.get(u, []):
            if v not in color:
                continue  # dangling reference, handled below
            if color[v] == GRAY:
                has_cycle[0] = True
            elif color[v] == WHITE:
                dfs(v)
        color[u] = BLACK

    for cid in ids:
        if color[cid] == WHITE:
            dfs(cid)
    if has_cycle[0]:
        return 0.0  # circular justification invalidates the whole structure

    # 2. Forward/dangling reference penalty.
    total_refs = bad_refs = 0
    for c in claims:
        for d in (c.get("dependencies") or []):
            total_refs += 1
            if d not in index or index[d] >= index[c["id"]]:
                bad_refs += 1
    ref_penalty = (bad_refs / total_refs) if total_refs else 0.0

    # 3. Free-riding penalty: leaning on prior claims while supplying no
    #    grounding of one's own is re-assertion, not incremental evidence.
    dependents = free_riders = 0
    for c in claims:
        if c.get("dependencies"):
            dependents += 1
            if not (c.get("sources") or []):
                free_riders += 1
    free_rider_penalty = (free_riders / dependents) if dependents else 0.0

    # 4. Flat-list penalty: in a multi-claim ARA, zero declared dependencies
    #    anywhere means no cumulative structure is shown at all -- penalized,
    #    not treated as neutral/not-applicable.
    flat_list_penalty = 1.0 if (len(ids) > 1 and dependents == 0) else 0.0

    score = 1.0 - 0.4 * ref_penalty - 0.35 * free_rider_penalty - 0.25 * flat_list_penalty
    return max(0.0, min(1.0, score))
```

**What the function does & why.** It treats `Dependencies` across all claims
as edges of a directed graph and runs a standard three-color DFS to detect
cycles — any cycle zeroes the whole score, since circular support means no
claim in the cycle is actually independently justified. It then penalizes
dependencies that point forward or nowhere (compiler/ordering errors), claims
that depend on others but bring zero `Sources` of their own (free-riding on
borrowed credibility), and — for multi-claim artifacts — the complete absence
of any dependency structure at all, which would mean the "paper" is really
just a flat list of unrelated assertions with no shown cumulative reasoning.

**Why it's hard to Goodhart.** Adding dependency edges everywhere to avoid
the flat-list penalty risks tripping the cycle check or the free-rider check
(a dependent claim still needs its own sources to avoid that penalty) — you
can't cheaply add structure without also adding grounding, and adding
grounding is exactly what Metric 2 independently rewards, so this pushes in
the same direction rather than against it.

---

## 5. Status–Documentation Calibration Score

**How it signals good science.** Genuine scientific practice documents
disconfirming or still-open results with the same rigor as confirmed ones —
a "supported" claim getting three sources and a detailed falsification
criterion while a "hypothesis" or "refuted" claim gets a throwaway sentence
signals that documentation effort tracked what the authors wanted to
emphasize, not what's true. The shape doc itself notes `Status` skews heavily
toward `supported` in practice; this metric treats the total absence of any
non-`supported` claim as a mild penalty scaled to how many claims exist,
rather than as an unremarkable default — a paper that never surfaces an
ablation, disconfirmed prior, or an explicit still-open hypothesis across
many claims is a paper that plausibly held its results to the standard of
"list what worked," not "list what we tested."

**Compute function.**

```python
def _status_richness(c):
    fals = c.get("falsification") or ""
    evidence = c.get("evidence_basis") or ""
    sources = c.get("sources") or []
    return (
        min(1.0, len(fals.split()) / 15.0) * 0.4 +
        min(1.0, len(evidence.split()) / 20.0) * 0.3 +
        min(1.0, len(sources) / 2.0) * 0.3
    )

def _base_status(status_str):
    s = (status_str or "").lower()
    for base in ("supported", "refuted", "hypothesis"):
        if s.startswith(base):
            return base
    return "unknown"

def status_calibration_score(claims):
    if not claims:
        return 0.0

    groups = {}
    for c in claims:
        groups.setdefault(_base_status(c.get("status")), []).append(_status_richness(c))
    group_avgs = {k: sum(v) / len(v) for k, v in groups.items() if v}
    if not group_avgs:
        return 0.0

    disparity_penalty = 0.0
    if len(group_avgs) >= 2:
        disparity_penalty = max(group_avgs.values()) - min(group_avgs.values())

    n = len(claims)
    non_supported = sum(1 for c in claims if _base_status(c.get("status")) != "supported")
    monoculture_penalty = min(0.4, 0.06 * n) if non_supported == 0 else 0.0

    unknown_status_penalty = 0.5 * (len(groups.get("unknown", [])) / n)

    score = 1.0 - 0.5 * disparity_penalty - monoculture_penalty - unknown_status_penalty
    return max(0.0, min(1.0, score))
```

**What the function does & why.** It buckets claims by normalized status
(stripping parenthetical qualifiers), computes a cheap "documentation
richness" proxy per claim from falsification length, evidence length, and
source count, and averages richness within each status bucket. It then
penalizes a large gap between the best- and worst-documented status buckets
(asymmetric scrutiny), separately penalizes the case where every single claim
is `supported` (scaled up with claim count, since a 6-claim paper with zero
hedged/refuted claims is more suspicious than a 1-claim one), and penalizes
unparseable/unknown status strings outright rather than ignoring them.

**Why it's hard to Goodhart.** A compiler can't dodge the monoculture penalty
by manufacturing a token "hypothesis" claim, because that claim still has to
clear the same richness bar as the `supported` ones or it drags the disparity
penalty up instead — there's no free way to satisfy "have a non-supported
claim" without also satisfying "document it as well as the rest."

---

## Joint hardness to Goodhart

Each metric targets a different failure mode — operational precision (1),
traceability (2), separation of fact from gloss (3), structural cumulativeness
(4), and documentation symmetry across outcomes (5) — and they pull against
each other's cheap exploits: padding falsification text with invented
thresholds (helps 1) is worthless or actively harmful unless those numbers are
genuinely quoted somewhere (2); adding dependency edges to look cumulative (4)
requires each dependent claim to still carry its own sources, which is graded
independently by (2); moving evaluative language out of `Statement` into
`Interpretation` to score well on (3) tends to make `Statement` barer and more
literal, which (1) rewards but only if the resulting falsification text still
carries a real number/comparator, not just fewer words; and manufacturing a
token non-`supported` claim to dodge the monoculture penalty in (5) only helps
if that claim is documented as richly as the rest, which is exactly what (5)
is also checking directly. There is no single edit to a claims.md file that
improves all five scores at once without doing the underlying work: adding a
real, quoted, precisely-thresholded, symmetrically-documented, properly
chained claim.
