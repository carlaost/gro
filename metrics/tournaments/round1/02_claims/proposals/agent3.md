# Proposer 3 — Metrics over `logic/claims.md`

Input assumption for all functions below: the artifact is parsed into a list `claims`, one
`dict` per `## C{NN}` block, of the form:

```python
claim = {
    "id": "C01",                      # e.g. "C01"
    "title": "...",
    "statement": "...",               # markdown-prose string, mandatory
    "status": "supported",            # or "hypothesis" / "refuted", may carry "(qualifier)"
    "falsification_criteria": "...",  # markdown-prose, mandatory
    "proof": ["E01"],                 # list[str] experiment ref-ids, may be empty
    "evidence_basis": "...",          # markdown-prose, mandatory
    "interpretation": "" ,            # markdown-prose, OPTIONAL (may legitimately be empty)
    "dependencies": ["C01"],          # list[str] claim ids, or [] / ["none"]
    "sources": [                      # list of dicts, one per load-bearing value
        {"value": "0.859", "ref": "evidence/tables/table2.md",
         "locator": "Table 2, Outcome 1, Rank 1",
         "quote": "p217_MS (0.859)",     # None/"" if bare path or [pending: ...]
         "tag": "result"},               # "input" | "result" | "pending"
        ...
    ],
    "tags": ["p-tau217", "mass spectrometry", ...],
}
```

Every metric below is computed per-claim then averaged/aggregated over the artifact
(`claims: list[dict]`). Per the hard constraint, no function ever returns `None`/`"N/A"` — a
missing or empty mandatory field always resolves to a low numeric score, never a skip.

---

## 1. Grounding Completeness & Fidelity Score (GCFS)

**How it signals good science**: The single strongest, most falsifiable-relevant discipline this
artifact enforces is that every load-bearing number in a claim's `Statement` traces to a specific,
quoted location (`Sources`, Rule 16). A claim that quotes numbers but doesn't ground them, or
grounds them only with bare paths / unresolved `[pending: ...]` tags, is unverifiable in exactly the
place it matters most — the numbers a reader would use to check the paper's own math. Good science,
operationalized here, means every quantity a claim leans on is independently traceable to a verbatim
source string, not just narratively asserted.

**Compute function**:

```python
import re

def grounding_fidelity_score(claim: dict) -> float:
    num_pattern = re.compile(r'-?\d+\.?\d*\s*(?:%|\(95% CI[^)]*\))?')
    candidates = {m.strip() for m in num_pattern.findall(claim.get("statement", "")) if m.strip()}
    sources = claim.get("sources") or []

    if not candidates:
        # A "precise, falsifiable" statement with zero quantities in it is itself a defect —
        # not exempt from scoring, just scored low.
        return 0.15

    if not sources:
        # Mandatory grounding field entirely absent: hard fail, not "N/A".
        return 0.0

    matched = 0
    quote_penalty = 0.0
    for cand in candidates:
        hit = next((s for s in sources
                    if cand in s.get("value", "") or s.get("value", "") in cand), None)
        if hit is None:
            continue
        tag, quote = hit.get("tag"), hit.get("quote")
        if tag == "pending" or not quote:
            quote_penalty += 0.5   # honest-but-incomplete: half credit only
        else:
            matched += 1

    coverage = matched / len(candidates)
    fidelity_penalty = quote_penalty / len(candidates)
    return round(max(0.0, coverage - fidelity_penalty), 3)


def artifact_grounding_score(claims: list) -> float:
    if not claims:
        return 0.0
    return round(sum(grounding_fidelity_score(c) for c in claims) / len(claims), 3)
```

**What the function does & why**: For each claim, it pulls every number-like token out of
`Statement`, then checks whether `Sources` contains a matching entry with an actual verbatim
`quote` (not a bare path, not a `[pending: ...]` placeholder). Coverage is the fraction of
statement numbers that are properly grounded; unresolved/pending entries get half credit rather
than full or zero, because the shape doc explicitly treats `[pending: ...]` as honest disclosure
rather than a shortcut — it shouldn't score identically to a clean grounded value, but it also
shouldn't be punished as hard as silently omitting the source. Claims with no numbers at all, or
no `Sources` block at all, are scored low directly rather than excluded, satisfying the hard
constraint.

**Why it's hard to Goodhart**: You cannot inflate this score by adding sources that don't
textually match a number in the statement (the matcher requires substring correspondence to the
actual claimed value), and you cannot inflate it by piling on `[pending]` placeholders (they're
capped at half credit). The only way to score well is to actually go get and quote the real
number from the real table/figure — which is the behavior the metric is trying to induce in the
first place.

---

## 2. Falsifiability Operationalization Index (FOI)

**How it signals good science**: A `Falsification criteria` field that just restates "this could
be wrong" is not falsifiable in Popper's sense — it gives no operational test. Good science
specifies *what observation, under what comparison, would flip the verdict* — a rival method
outranking the winner, a CI crossing zero, a hazard ratio failing a threshold. This metric scores
how operational (quantitative, comparator-bearing, unhedged) each claim's falsification criteria
actually is, independent of whether the claim ultimately turned out "supported."

**Compute function**:

```python
def falsifiability_operationalization(claim: dict) -> float:
    fc = (claim.get("falsification_criteria") or "").strip()
    if not fc:
        return 0.0  # mandatory field missing -> hard fail, not skipped

    has_number_or_stat = bool(re.search(
        r'\d|CI|p\s*[<>=]|significan|AUC|hazard ratio|threshold|non-significant', fc, re.I))
    has_comparator = bool(re.search(
        r'\b(if|unless|refuted|outranked|failed to|lower than|higher than|crossed?|reversed?|'
        r'non-significant)\b', fc, re.I))
    length_ok = len(fc.split()) >= 8
    hedge_terms = len(re.findall(r'\b(might|could|maybe|somewhat|possibly|perhaps)\b', fc, re.I))

    score = (0.4 * has_number_or_stat) + (0.3 * has_comparator) + (0.3 * length_ok)
    score -= 0.1 * hedge_terms
    return round(max(0.0, min(1.0, score)), 3)


def artifact_falsifiability_score(claims: list) -> float:
    if not claims:
        return 0.0
    return round(sum(falsifiability_operationalization(c) for c in claims) / len(claims), 3)
```

**What the function does & why**: It checks each falsification criterion for three positive
signals (a quantitative/statistical anchor, an explicit comparator/conditional structure, and
enough length to actually specify a scenario rather than a one-liner) and one negative signal
(hedge words that soften an otherwise operational claim back into vagueness). An empty field
scores zero outright — falsification criteria are mandatory, so absence is a defect, not a
missing-data case to be excluded.

**Why it's hard to Goodhart**: Padding the field with word count alone only buys 0.3 of the 1.0;
you also need real statistical/comparator vocabulary, which is cheap to fake individually but
expensive to fake *consistently* across a whole claims file without it reading as nonsense next to
the actual `Statement`/`Evidence basis` (which a downstream cross-check, or a human skim, would
catch as inconsistent). Hedge-word detection specifically penalizes the laziest gaming strategy
(restating the claim with "might not hold" appended).

---

## 3. Refutation & Negative-Result Honesty Rate (RNHR)

**How it signals good science**: The shape doc itself notes `Status` skews heavily to `supported`
because compilers extract what a paper reports as its findings. That skew is a property of the
*paper*, not just the compiler, and it's diagnostic: a paper (and by extension its compiled claims
set) that never surfaces a `hypothesis` (untested prediction carried forward) or a `refuted`
(explicitly disconfirmed expectation, failed ablation) is exhibiting exactly the confirmation
pattern associated with publication bias / selective reporting. Real, honest science usually has
at least one place where an expectation didn't pan out or a result is still open. This metric
rewards that diversity and penalizes monoculture, scaled by how many chances the paper had to show
it.

**Compute function**:

```python
def status_honesty_score(claims: list) -> float:
    if not claims:
        return 0.0
    n = len(claims)
    statuses = [c.get("status", "").split("(")[0].strip().lower() for c in claims]
    refuted = statuses.count("refuted")
    hypothesis = statuses.count("hypothesis")
    non_supported_rate = (refuted + hypothesis) / n

    if non_supported_rate == 0:
        # More claims with zero diversity = more suspicious, not less.
        monoculture_penalty = min(0.6, 0.08 * n)
        base = 0.5 - monoculture_penalty
    else:
        base = 0.5 + 0.5 * min(1.0, non_supported_rate / 0.3)

    # Hedged "supported (qualifier)" status with no Interpretation to carry the caveat
    # is a smaller-scale version of the same honesty failure.
    hedged_uninterpreted = sum(
        1 for c in claims
        if "(" in c.get("status", "") and "supported" in c.get("status", "").lower()
        and not (c.get("interpretation") or "").strip()
    )
    base -= 0.05 * hedged_uninterpreted
    return round(max(0.0, min(1.0, base)), 3)
```

**What the function does & why**: It computes the fraction of claims whose status is anything
other than `supported`. Zero such claims triggers a penalty that grows with the total claim count
(an 8-claim, 100%-supported artifact is a stronger monoculture signal than a 3-claim one, since
there were more opportunities for a null result to surface). Any nonzero diversity gets rewarded
on a scale capped at ~30% non-supported (beyond that, it's not obviously "more honest," just a
different kind of paper). It also separately dings claims that carry a hedge in the status enum
(e.g., `supported (interpretation-limited by female sample size)`) but leave that hedge
uninterpreted, i.e., unexplained anywhere.

**Why it's hard to Goodhart**: You cannot cheaply inflate this by relabeling a claim `refuted` or
`hypothesis` when its own `Statement`/`Evidence basis` clearly reports a positive, confirmed
result — that mismatch is directly checkable by cross-reading the same claim's `Statement` and
`Falsification criteria` fields (an inconsistency detector any reviewer or paired metric would
catch immediately, since falsification criteria for a genuinely `refuted` claim should describe
what *did* happen, not what would falsify it). The penalty structure also can't be gamed by simply
producing fewer claims to shrink `n`, because thinness is exactly what other proposed metrics
(and this panel's general stance) already penalize.

---

## 4. Evidence–Interpretation Separation / Editorializing Leakage (EILS)

**How it signals good science**: The shape doc explicitly flags this failure mode: `Interpretation`
collapsing into `Evidence basis`, and reviewing/meta-analysis claims smuggling the *authors'*
value judgment (e.g., "effectively obsolete") into what should be a neutral restatement of what the
cited evidence directly shows. Good science keeps "what the data show" cleanly separated from
"what we think it means." A claims file that lets evaluative/rhetorical language bleed into
`Evidence basis` is asserting interpretation as if it were fact — precisely the kind of
overclaiming a rigor review should catch.

**Compute function**:

```python
_EDITORIAL = re.compile(
    r'\b(obsolete|clearly|surprisingly|remarkabl\w*|best|worst|novel|groundbreaking|'
    r'undoubtedly|proves?|definitively|the only|superior|inferior|effectively \w+)\b', re.I)

def separation_score(claim: dict) -> float:
    eb = (claim.get("evidence_basis") or "").strip()
    interp = (claim.get("interpretation") or "").strip()

    if not eb:
        return 0.0  # mandatory field missing -> hard fail

    eb_hits = _EDITORIAL.findall(eb)
    if not interp:
        # No Interpretation field to carry evaluative language: fine if Evidence basis is
        # itself clean, but if editorializing leaked in with nowhere clean to land, that's
        # the worst case, not a neutral "N/A."
        return 0.15 if eb_hits else 0.8

    leakage_penalty = 0.15 * len(eb_hits)
    return round(max(0.0, 1.0 - leakage_penalty), 3)


def artifact_separation_score(claims: list) -> float:
    if not claims:
        return 0.0
    return round(sum(separation_score(c) for c in claims) / len(claims), 3)
```

**What the function does & why**: It scans `Evidence basis` for a fixed vocabulary of
evaluative/superlative language that belongs to interpretation, not observation. If such language
appears and there's no `Interpretation` field to properly house it, the claim scores near zero —
the worst combination (a value judgment stated as observed fact, undisclosed as opinion anywhere).
If `Evidence basis` is clean, the claim scores well whether or not `Interpretation` exists (since
`Interpretation` is genuinely optional per the shape doc), capped slightly below 1.0 to reflect
that we can't positively confirm separation discipline was ever tested when there's nothing to
separate. If `Interpretation` exists, leakage into `Evidence basis` is penalized proportionally to
how much evaluative language it contains.

**Why it's hard to Goodhart**: The cheap gaming move — deleting `Interpretation` entirely so there's
"nothing to leak into it" — doesn't help, because a clean `Evidence basis` with no `Interpretation`
only scores 0.8, not 1.0, and if the editorializing language is baked into the `Evidence basis`
text itself (which is where the actual paper-derived phrasing usually lives, per the che26 example
in the shape doc), removing the `Interpretation` field doesn't remove the leakage — it just removes
the one place that leakage could have been legitimately quarantined. The vocabulary list also
targets words that tend to appear precisely where authors are already editorializing in their own
papers, so suppressing them changes what the claim *says*, not just how it's labeled.

---

## 5. Dependency Graph Integrity & Non-Laundering Depth (DGIL)

**How it signals good science**: `Dependencies` links claims into a reasoning structure — later
claims building on "anchor" claims. Good science shows its work as an argument graph: claims that
build on each other while each still contributing its *own* new evidence (`Proof`). Two structural
failure modes indicate bad science even when every individual claim field looks fine in isolation:
(a) referential/logical breakage — dependency chains that point to nonexistent claims or that
cycle back on themselves (circular support: "C03 is true because C05, which relies on C03"), and
(b) **claim laundering** — a claim that formally "depends on" an earlier one but cites no
experimental evidence of its own beyond what its parent already cited, effectively restating the
same result as if it were an independent additional finding, inflating the apparent number of
supported claims without inflating actual evidence.

**Compute function**:

```python
def dependency_graph_score(claims: list) -> float:
    if not claims:
        return 0.0

    ids = {c["id"] for c in claims}
    edges = {}
    dangling = 0
    for c in claims:
        deps = [d for d in (c.get("dependencies") or []) if d.lower() != "none"]
        edges[c["id"]] = deps
        dangling += sum(1 for d in deps if d not in ids)

    def has_cycle() -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {cid: WHITE for cid in ids}
        def visit(u):
            color[u] = GRAY
            for v in edges.get(u, []):
                if v not in color:
                    continue
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and visit(v):
                    return True
            color[u] = BLACK
            return False
        return any(color[cid] == WHITE and visit(cid) for cid in ids)

    n = len(claims)
    connected = sum(1 for c in claims if edges[c["id"]])
    isolation_rate = 1 - connected / n  # fully atomized claim set: no argumentative structure

    laundered = 0
    for c in claims:
        deps = edges[c["id"]]
        if not deps:
            continue
        own_proof = set(c.get("proof") or [])
        parent_proof = set()
        for d in deps:
            parent = next((p for p in claims if p["id"] == d), None)
            if parent:
                parent_proof |= set(parent.get("proof") or [])
        if own_proof and own_proof.issubset(parent_proof):
            laundered += 1
    laundering_rate = laundered / n

    score = 1.0
    score -= 0.5 if has_cycle() else 0.0
    score -= 0.4 * (dangling / n)
    score -= 0.3 * isolation_rate
    score -= 0.3 * laundering_rate
    return round(max(0.0, score), 3)
```

**What the function does & why**: It rebuilds the claim dependency graph and checks it for
correctness (no dangling references to claim IDs that don't exist) and acyclicity (no circular
justification). It also measures isolation — an artifact where every claim's `Dependencies` is
`none` gets penalized, because a genuinely well-reasoned multi-claim paper usually has *some*
anchor/derived structure (per the shape doc's own convention), and a flat list of unconnected
one-off assertions is a weaker piece of scientific argument than an integrated one. Finally, it
flags "laundering": a claim that lists a dependency but whose own `Proof` list contributes nothing
beyond what its parent(s) already cited — i.e., it isn't independently supported, it's a restatement
dressed up as an additional finding.

**Why it's hard to Goodhart**: Adding fake `Dependencies` links to look "integrated" directly risks
tripping the cycle detector or the laundering check (since a fabricated dependency with no matching
new `Proof` is exactly what laundering detection flags). Removing all `Dependencies` to avoid
laundering risk instead trips the isolation penalty. The only way to score well on all three
sub-checks simultaneously is to have a claim graph that is both connected *and* has each node
backed by genuinely distinct experimental evidence — which is what a well-structured, well-evidenced
paper actually looks like.

---

## Why the combination is jointly hard to game

Each metric leans on a different field or cross-field relationship, chosen so that a change made to
inflate one score creates exposure on another:

- Padding `Sources` with fabricated or loosely-matching entries to raise **GCFS** produces exactly
  the kind of unverifiable/pending grounding that also drags down **DGIL**'s implicit reliance on
  real `Proof` linkage, since fabricated sources rarely trace to a genuine experiment.
- Writing longer, statistic-flavored **falsification criteria** (to raise **FOI**) but leaving the
  underlying `Status`/`Evidence basis` untouched creates a `Statement`-vs-`Falsification criteria`
  mismatch that **RNHR**'s consistency logic (refuted/hypothesis claims needing falsification
  language describing what *did* happen) is positioned to expose.
- Relabeling claims as `refuted`/`hypothesis` purely to raise **RNHR** without changing their
  `Statement` or `Evidence basis` breaks the evidentiary story those fields tell, which is exactly
  what **EILS** and **GCFS** are reading when they score those same fields.
- Stripping `Interpretation` to dodge **EILS** leakage detection increases the isolation/atomicity
  feel of the artifact and does nothing to help — and can hurt — **DGIL**, since a paper with no
  interpretive synthesis also tends to show weaker anchor/dependent claim structure.
- Fabricating `Dependencies` to raise **DGIL**'s connectivity term is directly caught by its own
  laundering and dangling-reference checks, and any invented parent-claim `Proof` overlap is exactly
  the kind of unverifiable evidence trail **GCFS** independently penalizes.

In short: every field in `claims.md` is read by at least two of these five metrics from a different
angle (surface content vs. cross-reference vs. structural graph position), so a single-field edit
made to game one score tends to either leave a second, differently-angled metric exposed, or to
directly trip the metric it was meant to help.
