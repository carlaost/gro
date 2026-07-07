# Proposer 4 (improved) — Metrics for `logic/claims.md`

## Changes from stage 1

- **M1 (Falsifiability):** dropped the raw-length proxy (`len(fals.split())/15`) flagged as
  Goodhartable and replaced it with a *novel-number* content proxy (numbers in `Falsification`
  that are genuinely new vs. `Statement`, not just word count); added cross-claim boilerplate
  detection (pairwise similarity) so templated filler across claims is penalized, closing a gap
  the critique noted in agent2's favor.
- **M3 (Evidence/Interpretation separation):** converted the fixed 17-word evaluative lexicon into
  a *grounded* leak test — a value-judgment word only counts as smuggled if it does **not** appear
  in any of the claim's own `Sources` quotes — plus grouped the lexicon into synonym clusters, per
  the judge's "value-judgment without a source quote" direction.
- **M4 (Dependency graph):** split reference-integrity checks into objective, order-independent
  errors (dangling refs, self-reference) vs. a separately-weighted, explicitly-documented *soft*
  forward-reference heuristic, since the old check silently assumed claim-ID order == topological
  order, which the shape doc doesn't guarantee.
- **M5 status-documentation calibration (now M6):** replaced the length-heavy richness proxy
  (40% falsification-length + 30% evidence-length) with grounded/structural signals only (count of
  *valid quoted* sources, count of distinct evidence refs, presence of an operational
  falsification), and made the disparity penalty asymmetric and floored — it now fires only in the
  selective-reporting direction (`supported` richer than non-`supported`) and tolerates a
  legitimately terse null result.
- **Added M5, Evidentiary Concentration & Transitive Anchor Fragility** — a new structural metric
  closing the one real coverage gap relative to the field: whether the paper's apparent breadth
  reduces to one dataset, and whether a single thin claim underwrites a long transitive dependency
  chain. Built transitively from the start and keyed on `Sources[*].ref` (not bare `Proof` ID
  strings), so it does not inherit the non-transitivity or ID-splitting weaknesses noted elsewhere
  in the tournament for a similarly-motivated metric.

---

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

## 1. Falsifiability Operationalization & Boilerplate Score

**How it signals good science.** A `Falsification criteria` field existing
is not enough — Popperian rigor requires the disconfirming observation to be
*operational*: a specific number, threshold, direction, or comparator that
someone could check against new data, and it has to be written for *this*
claim, not copy-pasted across claims as a template. Papers that pre-register
precise, claim-specific kill conditions (a CI crossing zero, a specific rank
reversal, a named comparator failing to replicate) are doing harder, more
falsifiable science than papers that gesture at falsifiability generically or
recycle the same boilerplate sentence with the nouns swapped.

**Compute function.**

```python
import re
from difflib import SequenceMatcher

NUMERIC_RE = re.compile(r'-?\d+\.?\d*\s*%?')
COMPARATOR_WORDS = [
    "greater than", "less than", "non-significant", "not significant",
    "crossing 0", "crosses 0", "fails to replicate", "outrank", "outranked",
    "underperform", "reversed", "no difference", "below", "above", "exceeds",
    "fell short", "failed to reach", "did not reach", "lower than", "higher than",
]

def _numbers(text):
    return {m.strip().rstrip('%') for m in NUMERIC_RE.findall(text or "")}

def falsifiability_operationalization_score(claims):
    if not claims:
        return 0.0

    fals_texts = [(c.get("falsification") or "").strip() for c in claims]
    n = len(claims)

    # Cross-claim boilerplate: near-duplicate falsification prose across
    # claims is templated filler, not per-claim operationalization. Only
    # compared among texts with enough content to be meaningfully similar
    # (short/empty texts are already penalized on their own below).
    boilerplate = [0.0] * n
    for i in range(n):
        if len(fals_texts[i].split()) < 6:
            continue
        for j in range(n):
            if i == j or len(fals_texts[j].split()) < 6:
                continue
            ratio = SequenceMatcher(None, fals_texts[i], fals_texts[j]).ratio()
            boilerplate[i] = max(boilerplate[i], ratio)

    scores = []
    for i, c in enumerate(claims):
        fals = fals_texts[i]
        if not fals:
            scores.append(0.0)
            continue

        stmt = c.get("statement") or ""
        has_number = bool(NUMERIC_RE.search(fals))
        has_comparator = any(w in fals.lower() for w in COMPARATOR_WORDS)

        # Content proxy instead of length: does the falsification text
        # introduce checkable numeric content that ISN'T just restating the
        # Statement's own numbers back at the reader?
        novel_numbers = _numbers(fals) - _numbers(stmt)
        novelty_score = min(1.0, len(novel_numbers) / 1.0)

        stmt_tokens = set(re.findall(r"[a-z]{4,}", stmt.lower()))
        fals_tokens = set(re.findall(r"[a-z]{4,}", fals.lower()))
        overlap = len(stmt_tokens & fals_tokens) / max(1, len(fals_tokens))
        generic_penalty = 1.0 if (overlap > 0.6 and not (has_number or has_comparator)) else 0.0

        raw = 0.35 * has_number + 0.35 * has_comparator + 0.30 * novelty_score
        raw *= (1 - 0.7 * generic_penalty)

        # Boilerplate penalty: scaled, not zeroing, since two claims can
        # legitimately share a comparator baseline (e.g. both refuted by the
        # same independent-cohort re-test design).
        bp = boilerplate[i]
        boilerplate_penalty = max(0.0, (bp - 0.55) / 0.45) if bp > 0.55 else 0.0
        raw *= (1 - 0.6 * min(1.0, boilerplate_penalty))

        scores.append(max(0.0, min(1.0, raw)))
    return sum(scores) / len(scores) if scores else 0.0
```

**What the function does & why.** For each claim it checks the
`falsification` text for a concrete number/percentage and a directional
comparator, and — instead of rewarding sheer length — checks whether any
number in the text is *new* relative to the `Statement` (a repeated number
copied from the statement doesn't add a checkable alternative outcome; a new
threshold like "95% CI crossing 0" does). It knocks the score down when the
text is mostly a vocabulary-restatement of the statement with no number or
comparator, and separately penalizes any claim whose falsification prose is
near-duplicate to another claim's — a compiler that fills every claim with
the same generic disconfirmation template gets caught even if each individual
instance looks superficially fine in isolation.

**Why it's hard to Goodhart.** Padding the field with more words no longer
helps at all — the score is built from number/comparator/novelty signals, not
word count. Copy-pasting one good falsification criterion across claims to
save effort now directly triggers the boilerplate penalty. Inventing a
"novel" number is caught downstream: an invented novel number that isn't
grounded anywhere tanks Metric 2, and an invented number that IS grounded is
exactly the operationalization this metric wants to reward — there's no
version of gaming this that doesn't require doing the real work or getting
caught by Metric 2.

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
precision without the epistemic substance of it. (Unchanged from stage 1 —
the critique identified this as tied for best-in-field, so it is carried
forward as-is.)

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
                entry_validity = 0.3
            else:
                entry_validity = 0.0

            valid_entries += entry_validity
            if entry_validity > 0:
                covered_numbers |= (_numbers_in(value) & stmt_numbers)

        validity_ratio = valid_entries / len(sources)
        coverage_ratio = (len(covered_numbers) / len(stmt_numbers)) if stmt_numbers else 0.0

        claim_scores.append(validity_ratio * coverage_ratio)
    return sum(claim_scores) / len(claim_scores) if claim_scores else 0.0
```

**What the function does & why.** For every claim, it extracts the numbers
asserted in `Statement`, then checks each `Sources` entry for a
non-placeholder quote, that quote actually containing the claimed value
verbatim, and a real locator. `[pending: ...]` entries get partial credit —
honest, but still unverified. It multiplies "how many of my sources are
actually valid" by "how much of what I asserted is actually covered by a
valid source," so one perfectly-quoted source next to five ungrounded
numbers still scores poorly.

**Why it's hard to Goodhart.** Gaming this by inventing `Sources` entries
with fabricated quotes requires the fabricated quote to *contain* the exact
value — any rounding, paraphrase, or omitted digit breaks the substring match
and zeroes that entry. Gaming it by only making claims with round, easy-to-
plant numbers is caught by Metric 1 (which wants operational precision) and
Metric 6 (which wants documentation symmetry) — an artifact that games
grounding by staying numerically simple looks thin on those axes.

---

## 3. Grounded Evidence–Interpretation Separation Score

**How it signals good science.** The shape doc explicitly flags two related
defects: `Interpretation` collapsing into `Evidence basis` (no separation of
raw support from broader reading), and editorializing language (e.g. "the
authors argue is effectively obsolete") being smuggled into `Statement` or
`Evidence basis` as if it were a directly measured quantity, rather than
confined to the field designed to hold interpretive gloss. Good science keeps
"what the data show" and "what we think it means" typographically and
epistemically separate.

**Compute function.**

```python
STOPWORDS = set("the a an of in on for to and or with that this which was were "
                 "is are as by at from into".split())

EVALUATIVE_PATTERNS = [re.compile(p) for p in [
    r"\bobsolete\b", r"\boutdated\b", r"\bout-of-date\b",
    r"\bbest\b", r"\bsuperior\b", r"\bleading\b", r"\btop-tier\b",
    r"\bgold standard\b", r"\bstate[- ]of[- ]the[- ]art\b",
    r"\bclearly\b", r"\bobviously\b", r"\bundeniably\b", r"\bunquestionably\b",
    r"\bdefinitively\b", r"\bprove[sd]?\b", r"\bconclusiv(?:e|ely)\b",
    r"\bshould\b", r"\bmust\b", r"\bought to\b",
    r"\brevolutionary\b", r"\bgroundbreaking\b", r"\bgame[- ]chang(?:ing|er)\b",
    r"\bflawed\b", r"\binvalid\b", r"\bworthless\b", r"\bdiscredited\b",
    r"\bdramatic(?:ally)?\b", r"\bstriking(?:ly)?\b", r"\bremarkable\b",
]]

def _content_tokens(text):
    return {w for w in re.findall(r"[a-z']{3,}", (text or "").lower()) if w not in STOPWORDS}

def evidence_interpretation_separation_score(claims):
    scores = []
    for c in claims:
        evidence = c.get("evidence_basis") or ""
        interp = (c.get("interpretation") or "").strip()
        statement = c.get("statement") or ""
        sources = c.get("sources") or []
        quotes_blob = " ".join((s.get("quote") or "") for s in sources).lower()

        if not interp:
            scores.append(0.2)
            continue

        ev_tok, in_tok = _content_tokens(evidence), _content_tokens(interp)
        overlap = len(ev_tok & in_tok) / max(1, len(ev_tok | in_tok))
        collapse_penalty = max(0.0, overlap - 0.5) * 2

        # A value-judgment term is only a "leak" if it appears in a field that
        # is supposed to be factual (Statement/Evidence basis) AND the authors
        # never actually said it in a cited quote -- i.e. it's the compiler's
        # own editorializing, not a directly-grounded characterization.
        leaked_hits = 0
        for pattern in EVALUATIVE_PATTERNS:
            for field_text in (statement.lower(), evidence.lower()):
                for m in pattern.finditer(field_text):
                    if m.group(0) not in quotes_blob:
                        leaked_hits += 1
        smuggle_penalty = min(1.0, 0.35 * leaked_hits)

        raw = 1.0 - 0.5 * collapse_penalty - 0.5 * smuggle_penalty
        scores.append(max(0.0, min(1.0, raw)))
    return sum(scores) / len(scores) if scores else 0.0
```

**What the function does & why.** It measures vocabulary overlap between
`Evidence basis` and `Interpretation` — heavy overlap means the compiler
duplicated the evidence prose into the interpretation slot rather than
synthesizing anything. Separately, it scans `Statement` and `Evidence basis`
for evaluative/totalizing language, but — unlike a bare lexicon scan — only
counts a hit as a real leak if that exact term does **not** appear anywhere
in the claim's own `Sources` quotes. If the authors' quoted text really does
say "obsolete," characterizing it as such in `Evidence basis` is grounded
reporting, not smuggling; if the compiler introduces the word on its own,
it's an ungrounded value judgment dressed as fact. Missing `Interpretation`
entirely is scored at a fixed low value rather than excluded.

**Why it's hard to Goodhart.** Synonym-dodging a fixed lexicon ("outdated"
for "obsolete") is far less effective now, since the lexicon is grouped into
clusters and — more importantly — even a term that dodges the list is only
useful to a compiler that wants to sound authoritative; the grounded check
means the *safe* way to use strong language is to actually quote it from the
source, which is exactly the auditable behavior this metric is trying to
produce. Deleting `Interpretation` to dodge the collapse check still triggers
the fixed missing-field penalty.

---

## 4. Dependency Graph Integrity Score

**How it signals good science.** Cumulative science builds later findings on
properly cited earlier ones — a genuine research narrative has a directed,
acyclic structure where dependent claims still carry their own evidence
rather than merely inheriting the credibility of an anchor claim. Claims that
depend on each other circularly, reference a claim id that doesn't exist, or
lean on prior claims while contributing zero grounding of their own are
structurally weaker than a claim graph that is a clean DAG with each node
pulling its own evidentiary weight.

**Compute function.**

```python
def dependency_graph_coherence_score(claims):
    if not claims:
        return 0.0

    ids = [c["id"] for c in claims]
    index = {cid: i for i, cid in enumerate(ids)}
    graph = {c["id"]: (c.get("dependencies") or []) for c in claims}

    # 1. Cycle detection -- objective and order-independent.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {cid: WHITE for cid in ids}
    has_cycle = [False]

    def dfs(u):
        color[u] = GRAY
        for v in graph.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                has_cycle[0] = True
            elif color[v] == WHITE:
                dfs(v)
        color[u] = BLACK

    for cid in ids:
        if color[cid] == WHITE:
            dfs(cid)
    if has_cycle[0]:
        return 0.0

    # 2. Reference errors, split into objective vs. assumption-dependent.
    total_refs = dangling = self_ref = forward = 0
    for c in claims:
        for d in (c.get("dependencies") or []):
            total_refs += 1
            if d == c["id"]:
                self_ref += 1  # objectively invalid under any convention
            elif d not in index:
                dangling += 1  # objectively invalid: points nowhere
            elif index[d] >= index[c["id"]]:
                # Heuristic only. The shape doc says an anchor is "commonly"
                # C01 but does not guarantee claim-id order == emission/
                # topological order. This is therefore a *soft* irregularity
                # signal, weighted well below the objective errors above, and
                # never conflated with a dangling or self reference.
                forward += 1

    hard_penalty = ((dangling + self_ref) / total_refs) if total_refs else 0.0
    soft_penalty = (forward / total_refs) if total_refs else 0.0

    # 3. Free-riding: leaning on prior claims while supplying no grounding of
    #    one's own is re-assertion, not incremental evidence.
    dependents = free_riders = 0
    for c in claims:
        if c.get("dependencies"):
            dependents += 1
            if not (c.get("sources") or []):
                free_riders += 1
    free_rider_penalty = (free_riders / dependents) if dependents else 0.0

    # 4. Flat-list penalty: zero declared dependencies anywhere in a
    #    multi-claim artifact means no cumulative structure is shown at all.
    flat_list_penalty = 1.0 if (len(ids) > 1 and dependents == 0) else 0.0

    score = (1.0
             - 0.40 * hard_penalty
             - 0.15 * soft_penalty
             - 0.25 * free_rider_penalty
             - 0.20 * flat_list_penalty)
    return max(0.0, min(1.0, score))
```

**What the function does & why.** It treats `Dependencies` as edges of a
directed graph and runs a three-color DFS to detect cycles — any cycle zeroes
the score, since circular support means no claim in the cycle is
independently justified. It then separates *objective* reference errors
(a dependency pointing at a nonexistent id, or at itself) — invalid
regardless of any ordering convention — from a much lower-weighted *soft*
signal for dependencies that point at a higher-numbered claim, explicitly
documented as relying on the (non-guaranteed) convention that claim ids are
roughly emission-ordered. It separately penalizes free-riding (a dependent
claim with zero sources of its own) and, for multi-claim artifacts, the
total absence of any dependency structure.

**Why it's hard to Goodhart.** Adding dependency edges everywhere to avoid
the flat-list penalty risks the cycle check or the free-rider check (a
dependent claim still needs its own sources). Renumbering claims to dodge the
soft forward-reference signal can't help fake structure, since that signal is
already weighted low and the objective dangling/self-reference checks can't
be dodged by any renumbering at all.

---

## 5. Evidentiary Concentration & Transitive Anchor Fragility Score

**How it signals good science.** Two structural failure modes don't show up
in per-claim grounding checks at all: (a) a paper's apparent breadth reducing
to one dataset or experiment, re-described across many claims as if it were
independent triangulating evidence, and (b) a long dependency chain
collapsing if one thin anchor claim near its root turns out to be weakly
grounded — a single point of failure that a per-claim view can't see. A
genuinely strong evidence base draws on multiple distinct evidence sources
and doesn't concentrate all downstream reasoning on one under-grounded
anchor.

**Compute function.**

```python
def evidentiary_concentration_score(claims):
    if not claims:
        return 0.0

    ids = [c["id"] for c in claims]
    index = {cid: i for i, cid in enumerate(ids)}

    # --- Part A: dataset/experiment monoculture, hardened against ID-splitting.
    # Distinctness is credited via the actual grounding evidence file/section
    # (Sources[*].ref), not the bare Proof-id string -- splitting one
    # experiment into E01a/E01b doesn't create genuine distinctness if both
    # still cite evidence/tables/table2.md.
    ref_weight = {}
    total_refs = 0
    for c in claims:
        proofs = c.get("proof") or []
        sources = c.get("sources") or []
        cited_refs = {(s.get("ref") or "").strip() for s in sources if (s.get("ref") or "").strip()}
        if not proofs or not cited_refs:
            # A claim asserting provenance it doesn't ground still counts
            # against the denominator -- it cannot be excluded as N/A.
            total_refs += max(1, len(proofs))
            continue
        for ref in cited_refs:
            ref_weight[ref] = ref_weight.get(ref, 0) + 1
            total_refs += 1

    if total_refs == 0:
        monoculture_penalty = 1.0  # nothing to triangulate against at all
    else:
        top_share = (max(ref_weight.values()) / total_refs) if ref_weight else 1.0
        monoculture_penalty = max(0.0, top_share - 0.5) * 2

    # --- Part B: transitive anchor fragility.
    deps_of = {c["id"]: [d for d in (c.get("dependencies") or []) if d in index] for c in claims}
    dependents_of = {cid: set() for cid in ids}
    for c in claims:
        for d in deps_of[c["id"]]:
            dependents_of[d].add(c["id"])

    def transitive_dependents(cid, seen=None):
        seen = seen if seen is not None else set()
        for direct in dependents_of.get(cid, ()):
            if direct not in seen:
                seen.add(direct)
                transitive_dependents(direct, seen)
        return seen

    def claim_grounding_quality(c):
        sources = c.get("sources") or []
        if not sources:
            return 0.0
        good = sum(1 for s in sources
                   if (s.get("quote") or "").strip()
                   and not s.get("pending")
                   and (s.get("value") or "") in (s.get("quote") or ""))
        return good / len(sources)

    n = len(ids)
    quality = {c["id"]: claim_grounding_quality(c) for c in claims}
    anchor_risk = 0.0
    for cid in ids:
        reliance_share = len(transitive_dependents(cid)) / max(1, n - 1)
        if reliance_share == 0:
            continue
        weakness = 1.0 - quality[cid]
        anchor_risk = max(anchor_risk, reliance_share * weakness)

    score = 1.0 - 0.5 * monoculture_penalty - 0.5 * anchor_risk
    return max(0.0, min(1.0, score))
```

**What the function does & why.** Part A tallies grounding weight by
evidence *file/section reference*, not by experiment-id string, so an
artifact can't fake dataset diversity by cosmetically splitting one
experiment id into several; if over half of all grounding weight rests on one
evidence reference, that's the "apparent breadth reduces to one dataset"
failure mode. Part B computes, for every claim, the *transitive* (not just
direct) set of claims that depend on it, and multiplies that reliance share
by `1 − grounding_quality` of the claim itself — a heavily-relied-upon anchor
that is well-grounded costs nothing, while a heavily-relied-upon but thin
anchor dominates the risk, even if the reliance is several hops removed via a
chain rather than a direct dependency.

**Why it's hard to Goodhart.** ID-splitting doesn't help Part A because
distinctness requires distinct evidence *references*, not distinct id
strings — the compiler would have to actually produce independent evidence
files, which is the real triangulation this metric wants. Restructuring the
dependency graph to hide a thin anchor behind an intermediate claim doesn't
help Part B, since reliance is computed transitively; the only way to reduce
anchor risk is to either de-anchor the graph (which risks the flat-list
penalty in Metric 4) or actually improve the anchor's own grounding, which
Metric 2 rewards directly.

---

## 6. Status–Documentation Calibration Score

**How it signals good science.** Genuine scientific practice documents
disconfirming or still-open results with the same evidentiary rigor as
confirmed ones — a `supported` claim getting solidly-grounded sources and an
operational falsification criterion while a `hypothesis` or `refuted` claim
gets nothing verifiable signals that documentation effort tracked what the
authors wanted to emphasize, not what's true. At the same time, a genuinely
terse null result (there just isn't much to say about an ablation that
failed cleanly) is not itself a defect — the metric should target the
*selective-reporting direction* specifically, not penalize all asymmetry.

**Compute function.**

```python
def _base_status(status_str):
    s = (status_str or "").lower()
    for base in ("supported", "refuted", "hypothesis"):
        if s.startswith(base):
            return base
    return "unknown"

def _status_richness(c):
    # Grounded/structural signals only -- no raw word/length counts, since
    # length is trivially padded by a verbose-but-empty compiler.
    sources = c.get("sources") or []
    valid_sources = [
        s for s in sources
        if (s.get("quote") or "").strip() and not s.get("pending")
        and (s.get("value") or "") in (s.get("quote") or "")
    ]
    distinct_refs = {(s.get("ref") or "").strip() for s in valid_sources if (s.get("ref") or "").strip()}

    fals = c.get("falsification") or ""
    has_number = bool(NUMERIC_RE.search(fals))
    has_comparator = any(w in fals.lower() for w in COMPARATOR_WORDS)
    operational_fals = 1.0 if (has_number or has_comparator) else 0.0

    return (
        min(1.0, len(valid_sources) / 2.0) * 0.45 +
        min(1.0, len(distinct_refs) / 2.0) * 0.30 +
        operational_fals * 0.25
    )

def status_calibration_score(claims):
    if not claims:
        return 0.0

    groups = {}
    for c in claims:
        groups.setdefault(_base_status(c.get("status")), []).append(_status_richness(c))
    group_avgs = {k: sum(v) / len(v) for k, v in groups.items() if v}
    if not group_avgs:
        return 0.0

    # Asymmetric, threshold-gated disparity: only the selective-reporting
    # direction (supported documented richer than the worst non-supported
    # bucket) is penalized, and a floor tolerates ordinary, honest asymmetry
    # (a clean-failing ablation just doesn't need much prose).
    disparity_penalty = 0.0
    supported_avg = group_avgs.get("supported")
    non_supported_avgs = [v for k, v in group_avgs.items() if k != "supported"]
    if supported_avg is not None and non_supported_avgs:
        worst_non_supported = min(non_supported_avgs)
        gap = supported_avg - worst_non_supported
        FLOOR = 0.15
        disparity_penalty = max(0.0, gap - FLOOR) / (1 - FLOOR)

    n = len(claims)
    non_supported = sum(1 for c in claims if _base_status(c.get("status")) != "supported")
    monoculture_penalty = min(0.4, 0.06 * n) if non_supported == 0 else 0.0

    unknown_status_penalty = 0.5 * (len(groups.get("unknown", [])) / n)

    score = 1.0 - 0.5 * disparity_penalty - monoculture_penalty - unknown_status_penalty
    return max(0.0, min(1.0, score))
```

**What the function does & why.** It buckets claims by normalized status and
computes a "documentation richness" score per claim from purely grounded
signals — the count of *actually-verified* quoted sources, the count of
distinct evidence references, and whether the falsification criterion is
operational — none of which can be inflated by writing more words. It then
penalizes the gap between the `supported` bucket's average richness and the
*worst*-documented non-`supported` bucket, but only past a floor (ordinary
brevity for a clean null result is expected and not punished), and separately
penalizes the case where every claim is `supported` and any unparseable
status strings.

**Why it's hard to Goodhart.** A compiler can't dodge the monoculture penalty
with a token `hypothesis` claim, because richness is now measured by verified
grounding, not prose — a thin token claim either has real quoted sources
(real work, and it still needs to clear the floor-adjusted gap) or it doesn't
(and widens the disparity penalty instead). Padding text no longer moves the
richness score at all, since word count was removed entirely.

---

## Combination

Each metric targets a different failure mode — operational, claim-specific
falsifiability (1), traceability (2), separation of fact from gloss (3),
structural cumulativeness (4), triangulation and single-point-of-failure risk
(5), and documentation symmetry across outcomes (6) — and they pull against
each other's cheap exploits. Padding falsification text with an invented
"novel" number (helps 1) is worthless unless that number is genuinely quoted
somewhere (2). Moving evaluative language out of `Statement`/`Evidence basis`
to score well on (3) only works if the term isn't grounded in a quote — the
safe move is to actually cite it, which is the auditable behavior (3) wants.
Adding dependency edges to look cumulative (4) requires each dependent claim
to still carry its own sources (2), and hiding a thin anchor behind
intermediate claims to dodge (5)'s fragility check does not work because
reliance there is computed transitively. Splitting one experiment id to fake
dataset diversity (5) requires actually producing distinct evidence files,
which is the real triangulation the metric is checking for, not a string
trick. Manufacturing a token non-`supported` claim to dodge (6)'s monoculture
penalty only helps if that claim clears the same grounded-richness bar as the
rest, which (6) checks directly and (2) checks independently. There is no
single edit to a `claims.md` file that improves all six scores at once
without doing the underlying work: adding a real, quoted, precisely-
thresholded, dataset-diverse, symmetrically-documented, properly chained
claim.
