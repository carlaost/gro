## Changes (cycle 2)

This is a repair pass on exp1 (Rank 1 / joint winner), not a redesign. The judge named exp1 the
strongest design because its headline score is almost entirely external-grounding (dual-index
search, disclosure asymmetry, structural-only impact) with internal structure demoted to an
availability multiplier — and explicitly said: *"the framework is right; the arithmetic needs
repair."* This revision touches only the arithmetic and the two under-specified integration points
the judge flagged, and leaves every "crown jewel" untouched:

1. **Fixed the composite bug that made the retrieval-confidence discount inert.** The old
   `effective_strength` formula collapsed a searchable-but-empty-search unit to `0.0` (full
   novelty) instead of the intended *provisional, confidence-capped* novelty. Rewritten as an
   explicit four-regime function (`unsearchable`, `retrieval_failed`, `searched_empty`,
   `searched_with_hits`) with a worked unit-test table for all four (§6.2b).
2. **Added a fourth regime the original design didn't distinguish: retrieval API failure vs. a
   clean empty result.** A Semantic Scholar timeout or an Undermind 5xx returns an empty list
   exactly like a genuine "searched both indexes, found nothing" — but the old code scored both
   identically at `conf=0.6` (provisional novelty). That rewards infrastructure flakiness with the
   same credit as a real negative search. Failure is now its own outcome, scored as worst-case
   (§6.2a), never as evidence of novelty.
3. **Repaired `n_dependent_claims` against the actual `claims.md` schema**, not an invented one.
   The old code matched Gap IDs directly against `Claims[].dependencies` — but per
   `DATA_SHAPES.md §2`, `Dependencies` is a list of *other claim IDs* (`[C01]` or `none`); it never
   contains Gap refs. There is no field in `claims.md` that names which Gap a claim addresses, so
   the old traversal was checking a relationship the schema cannot express and would silently
   return zero for every artifact. §6.3b below defines a real, deterministic gap→claim edge (concept
   -vocab term overlap, reusing the same controlled-vocabulary lookup `extract_novelty_units`
   already uses for query terms — no new free-text step) plus a well-defined transitive closure over
   the real `Dependencies` graph.
4. **Made the [sem] contract concrete** (§6.2a): exact endpoint, request/response shape, and
   dedup rule for both Semantic Scholar and Undermind, plus what "strong overlap" means
   operationally (`overlap_degree ∈ {substantial, identical}`, i.e. `_OVERLAP_TO_STRENGTH ≥ 0.7`).
5. **Removed a duplicate/inconsistent LLM call.** The original computed `unit_prior_art_strength`
   (one LLM pass per candidate) and then re-ran `judge_overlap` a second time per candidate to
   build the `strong` list for the disclosure check — double cost, and a source of
   self-contradictory verdicts for the same (unit, candidate) pair if the judge call has any
   sampling variance. Both now read from a single cached `judge_all_candidates` pass (§6.3a).
6. **Unchanged, by design**: the dual-index requirement (§6.2 of exp1), the fixed
   artifact-driven unit set (KI/Gaps/anchor-claim/method), the self-disclosure asymmetry
   (0.05 disclosed vs. 0.30 undisclosed, §6.4), the structural-only impact rubric (Prompt B, fed
   only `n_dependent_claims` + `n_trials`, never prose), the `Status`-based impact dampening, and
   the availability multiplier (§6.5). These were the parts the judge singled out as "crown jewels";
   nothing below touches their logic, only their inputs where a bug fed them wrong numbers.

---

## Repaired sections (supersede the corresponding sections of exp1)

### §6.2a — External retrieval contract (concrete, with failure handling)

Both calls are now specified precisely enough to implement without guessing at parameters, and
both return a tagged **outcome**, not just a hit list — this is what makes regime 2 below
(`retrieval_failed`) possible at all.

```python
from dataclasses import dataclass
from typing import Literal
import time

RetrievalLevel = Literal["unsearchable", "retrieval_failed", "searched_empty", "searched_with_hits"]

@dataclass
class RetrievalResult:
    outcome: Literal["success", "failure"]
    hits: list[dict]   # [{"title": str, "abstract": str, "year": int|None, "doi": str|None,
                        #   "source": "semantic_scholar"|"undermind", "native_score": float}]


def call_semantic_scholar(query_terms: list[str], retries: int = 1, timeout_s: float = 8.0) -> RetrievalResult:
    """[sem] call.
    GET https://api.semanticscholar.org/graph/v1/paper/search
    params: {"query": " ".join(query_terms), "fields": "title,abstract,year,citationCount,externalIds",
             "limit": 10}
    On HTTP 200: map each result to {"title","abstract","year","doi": externalIds.get("DOI"),
    "source":"semantic_scholar","native_score": 1.0}  (S2 doesn't return a relevance float on the
    plain search endpoint, so native_score is a constant placeholder — it is NEVER used to decide
    overlap, only the LLM judge's overlap_degree is; native_score exists solely for audit logs).
    On timeout / non-2xx: retry once with exponential backoff (2s), then return
    RetrievalResult(outcome="failure", hits=[]) — never silently return an empty-success result on
    a failed call, since that is exactly the ambiguity this cycle-2 fix removes (see §6.2b).
    """
    ...  # real HTTP call with the retry/backoff/failure-tagging behavior described above


def call_undermind(unit_text: str, retries: int = 1, timeout_s: float = 15.0) -> RetrievalResult:
    """[sem] call — embedding/semantic recall over the FULL unit text (not extracted terms), to
    catch relabeled/paraphrased prior art a lexical query would miss.
    POST https://api.undermind.ai/v1/search
    headers: {"Authorization": f"Bearer {UNDERMIND_API_KEY}", "Content-Type": "application/json"}
    body: {"query": unit_text, "top_k": 10, "corpus": "all"}
    response: {"results": [{"title": str, "abstract": str, "year": int|None, "doi": str|None,
                             "relevance_score": float in [0,1]}, ...]}
    Map each result to {"title","abstract","year","doi","source":"undermind",
    "native_score": relevance_score}.
    On timeout / non-2xx after retries: RetrievalResult(outcome="failure", hits=[]) — same rule
    as semantic-scholar; a failed embedding search must never look like "searched, found nothing."
    """
    ...  # real HTTP call


def clinicaltrials_field_activity(domain_terms: list[str]) -> int:
    """[ext] — unchanged from exp1 §6.2: ClinicalTrials.gov v2 search_trials, impact-rubric input
    only, never a novelty signal."""
    ...


def dedup_candidates(ss_hits: list[dict], um_hits: list[dict]) -> list[dict]:
    """Merge the two hit lists into the candidate pool judged in §6.3a. Dedup key is DOI when
    present on both sides; otherwise a normalized title (lowercased, whitespace-collapsed,
    trailing punctuation stripped). Title-only dedup is intentionally permissive enough to collapse
    a preprint and its later journal version (same prior art, should not be judged twice) but never
    collapses across genuinely different titles even if topically similar — that judgment is left
    entirely to the LLM overlap call in §6.3a, not to string matching.
    """
    seen: dict[str, dict] = {}
    for hit in ss_hits + um_hits:
        key = hit.get("doi") or " ".join(hit.get("title", "").lower().split()).rstrip(".")
        if key not in seen:
            seen[key] = hit
    return list(seen.values())
```

"Strong overlap" (used by the disclosure cross-check, §6.4, and by the retrieval-failure/empty
distinction) is defined operationally, not impressionistically: a candidate is "strong" iff its
Prompt-A `overlap_degree` is `"substantial"` or `"identical"`, i.e. `_OVERLAP_TO_STRENGTH[...] >= 0.7`
(unchanged mapping from exp1 §6.3). Nothing about that mapping needed repair — only how the strength
value gets *combined* into the final score did (§6.2b, §6.3a).

### §6.2b — Retrieval confidence, rewritten as an explicit four-regime function

This directly targets the judge's Weakness #1 ("a well-formed query that finds nothing still
scores full novelty, contradicting §6.2's design narrative") and closes the retrieval-failure gap
noted in Change 2 above.

```python
UNKNOWN_INDEX_RISK_PRIOR = 0.5
# Deliberately the maximally-uninformative prior (coin-flip), not 0.0. A clean run of BOTH
# independent indexes coming back empty is real evidence of novelty, but capped evidence — it must
# land strictly between "no reliable signal at all" (unsearchable / retrieval_failed, forced to the
# worst case, 1.0) and "we actually found and judged candidates" (real judged strength). Using 0.0
# here would silently resurrect the exact bug this cycle-2 fixes.


def retrieval_level(unit_searchable: bool, ss: "RetrievalResult", um: "RetrievalResult") -> RetrievalLevel:
    if not unit_searchable:
        return "unsearchable"
    if ss.outcome == "failure" or um.outcome == "failure":
        # Either index failing to answer is treated as "we could not determine this," not as a
        # partial pass on whichever index did respond — a half-completed dual-index check is not
        # the dual-index guarantee the design relies on for its anti-relabeling property.
        return "retrieval_failed"
    if not ss.hits and not um.hits:
        return "searched_empty"
    return "searched_with_hits"


def unit_effective_strength(level: RetrievalLevel, judged: list[tuple[dict, float, dict]],
                             disclosure_penalty: float) -> float:
    """judged = output of judge_all_candidates() (§6.3a); only non-empty when
    level == 'searched_with_hits'. disclosure_penalty comes from §6.4, unchanged, and is only
    ever non-zero when there were strong candidates to check disclosure against."""
    if level in ("unsearchable", "retrieval_failed"):
        # No reliable signal in either direction. Per penalize-don't-skip (§7), absence of a
        # verdict is never scored as favorable; both cases collapse to worst-case prior-art risk.
        return 1.0
    if level == "searched_empty":
        conf = 0.6
        strength = 0.0   # no candidates exist to judge
        blended = conf * strength + (1 - conf) * UNKNOWN_INDEX_RISK_PRIOR
        return min(1.0, blended + disclosure_penalty)   # disclosure_penalty is always 0.0 here —
                                                          # nothing to disclose against
    # searched_with_hits: full confidence in whatever the judge concluded
    strength = max((s for _, s, _ in judged), default=0.0)
    return min(1.0, strength + disclosure_penalty)
```

**Unit test table (the four regimes), replacing the muddled inline arithmetic from exp1:**

| Regime | Setup | `level` | Computation | `effective_strength` | `novelty` contribution |
|---|---|---|---|---|---|
| Unsearchable | query has <2 concept/tag terms; search never runs | `unsearchable` | forced worst case | `1.0` | `0.0` |
| Retrieval failed | S2 or Undermind times out after retry | `retrieval_failed` | forced worst case | `1.0` | `0.0` |
| Searched, empty | both indexes queried successfully, 0 hits total | `searched_empty` | `0.6·0 + 0.4·0.5 = 0.20` | `0.20` | `0.80` (capped, provisional — never `1.0`) |
| Searched, hits, all `none` | candidates returned, judge says no technical-core overlap | `searched_with_hits` | `max(strengths)=0.0` | `0.00` | `1.00` (deserved full credit — this is the *only* regime that earns full novelty, because it's the only one with real evidence) |
| Searched, hits, one `substantial`, disclosed | as above but one hit judged 0.7, cited in `related_work.md` | `searched_with_hits` | `0.7 + 0.05 = 0.75` | `0.75` | `0.25` |
| Searched, hits, one `substantial`, undisclosed | same hit, absent from `related_work.md` | `searched_with_hits` | `0.7 + 0.30 = 1.00` | `1.00` | `0.00` |

Note the ordering this produces, which is exactly the property the judge's design narrative wanted
and the old arithmetic failed to deliver: `searched_empty` (0.80 novelty) now scores **strictly
below** `searched_with_hits`+`none` (1.00 novelty) — a well-formed search that comes back totally
clean is better evidence of novelty than one where the query never got a chance to run — while both
score **above** `unsearchable`/`retrieval_failed` (0.0 novelty), which are never rewarded.

### §6.3a — Judge calls, cached once per candidate

Prompt A and its deterministic conversion (`_OVERLAP_TO_STRENGTH`, `judge_overlap`) are unchanged
from exp1 §6.3 — that machinery was not the bug. What's fixed is that it now runs exactly once per
(unit, candidate) pair instead of twice:

```python
def judge_all_candidates(unit: "NoveltyUnit", candidates: list[dict], llm_call) -> list[tuple[dict, float, dict]]:
    """Single pass: returns [(candidate, prior_art_strength, raw_judgment), ...]. Both the
    max-strength computation and the disclosure cross-check (§6.4) read from this cached list —
    neither re-invokes the LLM. Prevents the double-call inconsistency risk the judge implicitly
    flagged by calling the old design 'genuinely muddled.'"""
    return [(c, *judge_overlap(unit, c, llm_call)) for c in candidates]
```

### §6.3b — `n_dependent_claims`, repaired against the real `claims.md` schema

Per `DATA_SHAPES.md §2`, `Claims[].Dependencies` is a list of **other claim IDs** (e.g. `[C01]`, or
`none`) — it never contains Gap refs, and no field in `claims.md` names which Gap a claim
addresses. The old code's `g["id"] in (c.get("dependencies") or [])` check was therefore comparing
against a relationship the schema cannot express; it would return zero dependent claims for every
real artifact, not merely "brittle" as the judge charitably put it.

The fix defines a real edge in two deterministic steps, reusing infrastructure the workflow already
has (no new free-text/LLM step, so no new gaming surface):

```python
def gap_dependent_claim_ids(gap_statement: str, claims: list[dict], concept_vocab: set[str]) -> set[str]:
    """Step 1 — direct link: a claim is directly linked to a Gap if the Gap's own controlled-
    vocabulary query terms (built via the SAME `build_terms` lookup extract_novelty_units already
    uses — concept_vocab intersected with the Gap's Statement, i.e. the artifact's own controlled
    vocabulary, never a free paraphrase) appear in that claim's Tags or Statement.

    Step 2 — transitive closure over the REAL Dependencies graph: `Dependencies` lists the claim
    IDs a given claim depends on. If claim X lists claim Y in its Dependencies, and Y is directly
    linked to the Gap, then X causally depends on the Gap being closed too — X's own argument
    presupposes Y's, so it inherits Y's dependency. This is a reverse-edge (X depends on Y ⇒ X is
    downstream of Y) breadth-first closure.
    """
    gap_terms = set(build_terms(gap_statement))
    if not gap_terms:
        return set()

    def claim_tags(c: dict) -> set[str]:
        tags = c.get("tags") or []
        if isinstance(tags, str):
            tags = tags.split(",")
        return {t.strip().lower() for t in tags}

    direct = {
        c["id"] for c in claims
        if gap_terms & claim_tags(c) or any(t in c.get("statement", "").lower() for t in gap_terms)
    }

    # reverse-dependency index: claim_id -> set of claims that list it in their own Dependencies
    downstream_of: dict[str, set[str]] = {c["id"]: set() for c in claims}
    for c in claims:
        for dep in c.get("dependencies") or []:
            if dep in downstream_of:
                downstream_of[dep].add(c["id"])

    closure = set(direct)
    frontier = list(direct)
    while frontier:
        cid = frontier.pop()
        for nxt in downstream_of.get(cid, ()):
            if nxt not in closure:
                closure.add(nxt)
                frontier.append(nxt)
    return closure


def compute_n_dependent_claims(units: list["NoveltyUnit"], claims: list[dict],
                                concept_vocab: set[str]) -> int:
    """Union across all Gap units (not summed per-gap — a claim depending on two gaps still
    counts once; impact is about how much of the artifact's claim structure sits on top of THIS
    problem being resolved, not a multiplicity count)."""
    dependent: set[str] = set()
    for u in units:
        if u.unit_type == "gap":
            dependent |= gap_dependent_claim_ids(u.text, claims, concept_vocab)
    return len(dependent)
```

If a Gap's terms match nothing in `claims.md` at all (`gap_dependent_claim_ids` returns empty),
`n_dependent_claims` legitimately can be `0` for that gap — this is then fed honestly into Prompt B
(§6.3 of exp1, unchanged) as a real structural fact ("this gap has zero claims resting on it"),
which correctly pulls the impact score down rather than being masked by a miscounting bug that
silently always returned zero and made the signal meaningless in both directions.

### §6.6 — Final composite, reassembled with the repairs

Everything else — weights, availability multiplier, `Status`-based impact dampening, the 0.6/0.4
novelty/impact blend — is unchanged from exp1 §6.6.

```python
def score_M17(problem: dict, claims: list[dict], concepts: list[dict],
              related_work: dict, solution: dict, llm_call, is_clinical_domain: bool) -> dict:
    concept_vocab = {c["term"].lower() for c in concepts}
    units = extract_novelty_units(problem, claims, concepts, solution)

    per_unit = []
    for u in units:
        if not u.searchable:
            level, judged, penalty = "unsearchable", [], 0.0
        else:
            ss = call_semantic_scholar(u.query_terms)
            um = call_undermind(u.text)
            level = retrieval_level(u.searchable, ss, um)
            if level == "searched_with_hits":
                candidates = dedup_candidates(ss.hits, um.hits)
                judged = judge_all_candidates(u, candidates, llm_call)
                strong = [c for c, s, _ in judged if s >= 0.7]
                penalty = undisclosed_prior_art_penalty(u.unit_id, strong, related_work["full"])
            else:
                judged, penalty = [], 0.0
        effective_strength = unit_effective_strength(level, judged, penalty)
        per_unit.append((u, effective_strength, level))

    weighted_prior_art = sum(u.weight * s for u, s, _ in per_unit) / sum(u.weight for u, _, _ in per_unit)
    novelty_score = 1.0 - weighted_prior_art

    n_dependent_claims = compute_n_dependent_claims(units, claims, concept_vocab)
    n_trials = clinicaltrials_field_activity(
        [t for u in units for t in u.query_terms]) if is_clinical_domain else 0
    impact_score = judge_impact(problem, n_dependent_claims, n_trials, llm_call)

    # unchanged from exp1: impact is dampened if the claims meant to close the gap aren't
    # actually supported
    anchor_ids = [u.unit_id for u in units if u.unit_type == "anchor_claim"]
    supporting_statuses = [c["status"] for c in claims if c["id"] in anchor_ids]
    if supporting_statuses and all(s != "supported" for s in supporting_statuses):
        impact_score *= 0.5

    avail_mult = availability_multiplier(problem, related_work["full"], related_work["brief"])

    raw = 0.6 * novelty_score + 0.4 * impact_score
    final = avail_mult * raw

    return {
        "score": round(final, 4),
        "novelty_score": round(novelty_score, 4),
        "impact_score": round(impact_score, 4),
        "availability_multiplier": round(avail_mult, 4),
        "n_dependent_claims": n_dependent_claims,
        "per_unit": [(u.unit_id, u.unit_type, level, round(s, 4)) for u, s, level in per_unit],
    }
```

`per_unit` now also reports each unit's retrieval `level` in the audit output — a reviewer can see
directly whether a given unit's novelty credit came from a genuine clean search
(`searched_with_hits`) versus a provisional empty-search discount (`searched_empty`) versus a
worst-case default (`unsearchable`/`retrieval_failed`), which was not distinguishable in exp1's
output at all.

## §7 — Penalize-don't-skip summary, updated

All six bullets from exp1 §7 hold unchanged. One is added:

- **Retrieval API failure (timeout/non-2xx after retry) on either Semantic Scholar or Undermind** →
  scored identically to an unsearchable unit (`effective_strength = 1.0`, worst-case prior-art
  risk), never conflated with a genuine "searched both indexes cleanly and found nothing" result
  (`searched_empty`, capped at 0.80 novelty) and never defaulting to a neutral or lenient score. A
  network blip must never be worth more than a real negative search, and must never be worth more
  than nothing at all.
