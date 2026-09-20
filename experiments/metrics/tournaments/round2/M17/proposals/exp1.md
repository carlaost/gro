# M17 — Novelty vs. literature (+ impact) — Expansion 1

## 1. What this metric is for, precisely

M17 answers one question the ARA's own internal verifier structurally cannot answer: **"has this
already been done, outside the four corners of this artifact?"** The internal verifier (Seal Level
checks) can only judge *internal scope* — does the Key Insight in `problem.md` actually follow from
the cited Observations/Gaps, do the claims trace to real evidence, is the reasoning chain closed and
consistent. None of that touches the outside world. A perfectly self-consistent artifact can still be
describing a result published five years ago under different vocabulary. M17 is the one metric in the
suite that leaves the artifact and checks against real external literature, then separately scores
what it would mean for the field if the (verified-as-novel) gap were actually closed.

This is why the ledger flags it as net-new specifically vs. the ARA verifier, and it's the property
this expansion must protect: **every sub-step below must depend on an actual external retrieval call
([sem]/[ext]), never on re-reading the artifact's own prose as if that were evidence of novelty.** A
metric that scored novelty purely by "how confidently does `related_work.md` claim this is new" would
collapse back into an internal-consistency check and duplicate the verifier — that is the one failure
mode this design must refuse to fall into.

## 2. What it should reward

- **Specific, falsifiable, searchable novelty claims.** A Gap or Key Insight stated precisely enough
  that a competent search could in principle find a match if one existed (e.g. "network meta-analysis
  jointly ranking p-tau217/181/231 across platform and matrix" is searchable; "a novel framework for
  biomarker analysis" is not).
- **Novelty that survives an adversarial external search**, not novelty that is merely unrefuted
  because nobody looked. A gap that a broad, multi-query search genuinely fails to surface prior art
  for should score higher than one where the artifact simply asserts novelty in prose.
- **Honest self-disclosure of close prior art.** An artifact whose `related_work.md` already lists the
  closest matching predecessors under `extends`/`bounds`/`baseline` and explicitly states the
  differentiating delta should score *better* on the "undisclosed prior art" sub-check than one that
  is silent about a close match that external search turns up — even if both end up with similar raw
  overlap scores. Disclosure + differentiation is a mark of rigor; silent overlap is a mark of either
  a shallow lit-review or, worse, obscured non-novelty.
- **Impact judged against concrete, checkable criteria** (how many downstream claims depend on this
  gap, whether the domain has active clinical/field investment visible externally — e.g. via
  ClinicalTrials.gov — not generic enthusiasm language lifted from the paper's own discussion section).

## 3. What it must NOT reward

- **Vagueness-as-novelty.** Sweeping, unfalsifiable "first to..." language that is unfalsifiable
  precisely because it's too vague to search is a Goodhart route, not a virtue. This must be penalized,
  not scored as maximally novel because "nothing came back."
- **Relabeling.** Renaming an existing method/insight with new terminology to dodge literal keyword
  search. The search step must use semantic retrieval (embeddings-based, e.g. undermind) specifically
  to catch this, not just term-matching (semantic-scholar keyword search alone is insufficient and must
  never be the only pass).
- **Sparse `related_work.md` treated as evidence of sparse literature.** Per the DATA_SHAPES
  availability notes, a padded or narrow `related_work.md` (only distant/background refs, no full
  `RW##` blocks with real deltas) is itself a compiler-quality defect, not proof the field is empty.
  M17 must never let the artifact's own self-reported related-work section stand in for the external
  search — it is cross-checked against it, never substituted for it.
- **Impact inflation from hype language.** "This would transform the field" in a Discussion section is
  not evidence. The impact rubric (§6.3 below) is explicitly conditioned on structural facts (# of
  dependent claims, external field-investment signal) precisely so prose enthusiasm can't move the
  score.
- **Rewarding absence of the gap being closed.** If claim `Status` for the claims that would close this
  gap is `hypothesis` or `refuted` rather than `supported`, the impact score must be dampened — impact
  is scored for "if genuinely resolved," and a paper that merely proposes but doesn't support closing
  the gap shouldn't get full impact credit for a resolution that didn't happen.

## 4. Failure modes / gaming routes and the countermeasure built against each

| Gaming route | Countermeasure in this workflow |
|---|---|
| Vague novelty claims to evade search | Extraction step (§6.1) requires a *searchable query* to be constructible from the unit text; units that can't produce a query with ≥2 concrete technical terms are flagged `unsearchable` and penalized, not skipped. |
| Term substitution / relabeling | Dual search: semantic-scholar (lexical/citation-graph) AND undermind (semantic/embedding recall) run for every unit; a unit is only credited novel if BOTH return no strong overlap. |
| Padding `related_work.md` with distant refs to look thorough while omitting the actual closest predecessor | §6.4 cross-check: every external hit scored `substantial`/`identical` is checked against whether it appears in the artifact's own `related_work.md` RW blocks. Undisclosed close matches are penalized harder than disclosed ones. |
| Cherry-picking which Gap/Insight to submit for the "done-before" check (submitting only the easiest-to-defend one) | The workflow enumerates a **fixed, artifact-driven set** of units — the Key Insight (mandatory, weight-1.0), all Gaps (weight-0.8 each), the highest-weight/anchor claim per `claims.md` `Dependencies` chain (weight-0.6), and the paper's stated method summary (weight-0.5) — not an LLM's free choice of "the one that's clearly novel." |
| Impact score inflated by discussion-section hype | Impact rubric prompt (§6.3) explicitly excludes prose enthusiasm as an input; it is fed only structural facts (dependent-claim count, external field-activity count) and must justify the 1-5 score by citing them. |
| Gaming by having a thin/absent `problem.md` or `related_work.md` so the metric has nothing to search against, hoping for a skip/pass | Explicitly disallowed — see §7. Missing/thin inputs floor the score down via the availability multiplier; they never produce N/A or a default-neutral score. |
| Search-API blind spots (very recent preprints, non-indexed venues) inflating apparent novelty | The "no external hit found" branch is scored as **provisional novelty with an explicit confidence discount**, not full-credit certain novelty — see §6.2's `retrieval_confidence` term. |

## 5. Why this is hard to Goodhart

1. It requires two independent, differently-biased external retrieval systems (citation-graph search
   vs. semantic embedding search) to both come back clean — an artifact author cannot control what
   Semantic Scholar or an embedding index contains, unlike internal artifact prose which they fully
   author.
2. The self-disclosure cross-check (§6.4) makes *both* directions of gaming costly: hiding a close
   match is penalized once external search finds it anyway; inventing exaggerated novelty language is
   penalized independently by the unsearchability check (§6.1). There's no dominant strategy — thin
   `related_work.md` doesn't help (cross-check still runs against genuine external search) and a
   maximally padded one doesn't help either (padding without deltas doesn't count as disclosure; only
   `RW##` blocks with `Type` + `Delta` count).
3. Impact scoring is decoupled from the artifact's own persuasive language and grounded in countable
   structural facts (claim dependency counts) plus one external check (field investment signal), which
   an author cannot inflate by writing more convincingly.
4. Because retrieval confidence is itself scored and multiplies into the final value (§6.2), an author
   cannot benefit from picking an obscure enough domain that search returns nothing — that scenario is
   scored as *lower* confidence novelty, not higher.

## 6. Generation / compute workflow

### 6.0 Inputs (exact artifact fields consumed)

| Field | Source file | Used for |
|---|---|---|
| `Gaps[].statement`, `.existing_attempts`, `.why_they_fail` | `logic/problem.md` §Gaps | novelty units |
| `KeyInsight.statement`, `.derived_from`, `.enables` | `logic/problem.md` §Key Insight | novelty units (highest weight) |
| `Claims[].statement`, `.status`, `.dependencies`, `.tags` | `logic/claims.md` | anchor-claim novelty unit + impact dependent-count |
| `Concepts[].definition`, `.related_concepts` | `logic/concepts.md` | query-term enrichment only (not a standalone unit — concepts are vocabulary, not contributions) |
| `RelatedWork.full[].type`, `.delta`, `.doi` | `logic/related_work.md` | self-disclosure cross-check baseline |
| `RelatedWork.brief[]` | `logic/related_work.md` | availability/thinness signal |
| `Solution.method_summary` | `logic/solution/*.md` | method-novelty unit |

### 6.1 Step 1 — Extract fixed novelty units + build searchable queries

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class NoveltyUnit:
    unit_id: str
    unit_type: Literal["key_insight", "gap", "anchor_claim", "method"]
    text: str
    weight: float
    query_terms: list[str]
    searchable: bool


def extract_novelty_units(problem: dict, claims: list[dict],
                           concepts: list[dict], solution: dict) -> list[NoveltyUnit]:
    """problem/claims/concepts/solution are parsed dicts matching the documented
    DATA_SHAPES structure (problem['gaps'] = [{'id','statement','caused_by',
    'existing_attempts','why_they_fail'}, ...], problem['key_insight'] =
    {'statement','derived_from','enables'}, claims = [{'id','statement','status',
    'dependencies','tags'}, ...], concepts = [{'term','definition','related_concepts'}],
    solution = {'method_summary': str}).
    """
    concept_vocab = {c["term"].lower() for c in concepts}
    units: list[NoveltyUnit] = []

    def build_terms(text: str, tags: list[str] | None = None) -> list[str]:
        # deterministic term extraction: keep concept-vocab hits + explicit tags;
        # this is NOT a free LLM paraphrase step, it is lookup against the
        # artifact's own controlled vocabulary so the query reflects what the
        # paper itself calls its contribution.
        hit_terms = [t for t in concept_vocab if t in text.lower()]
        return sorted(set(hit_terms + [t.strip().lower() for t in (tags or [])]))

    # Key Insight — mandatory, weight 1.0
    ki = problem.get("key_insight")
    if ki and ki.get("statement"):
        terms = build_terms(ki["statement"])
        units.append(NoveltyUnit("KI", "key_insight", ki["statement"], 1.0,
                                  terms, searchable=len(terms) >= 2))
    else:
        # missing Key Insight is itself scored, not skipped — see score_availability()
        units.append(NoveltyUnit("KI", "key_insight", "", 1.0, [], searchable=False))

    # Gaps — weight 0.8 each
    for g in problem.get("gaps", []):
        terms = build_terms(g.get("statement", ""))
        units.append(NoveltyUnit(g["id"], "gap", g.get("statement", ""), 0.8,
                                  terms, searchable=len(terms) >= 2))

    # Anchor claim: the claim most other claims depend on (highest in-degree in
    # the Dependencies graph); ties broken by lowest claim id (earliest anchor).
    indeg = {c["id"]: 0 for c in claims}
    for c in claims:
        for dep in c.get("dependencies", []) or []:
            if dep in indeg:
                indeg[dep] += 1
    if indeg:
        anchor_id = sorted(indeg.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        anchor = next(c for c in claims if c["id"] == anchor_id)
        terms = build_terms(anchor["statement"], anchor.get("tags"))
        units.append(NoveltyUnit(anchor_id, "anchor_claim", anchor["statement"],
                                  0.6, terms, searchable=len(terms) >= 2))

    # Method summary — weight 0.5
    ms = solution.get("method_summary", "")
    terms = build_terms(ms)
    units.append(NoveltyUnit("METHOD", "method", ms, 0.5, terms,
                              searchable=len(terms) >= 2))

    return units
```

An `unsearchable` unit (query with fewer than 2 concept/tag-grounded terms) is **not** dropped — it
proceeds to scoring with `retrieval_confidence = 0` and is penalized under §6.2's confidence term,
directly countering the "vagueness evades search" gaming route.

### 6.2 Step 2 — External retrieval [sem] + [ext]

Two independent calls per searchable unit:

```python
def semantic_scholar_search(query_terms: list[str]) -> list[dict]:
    """[sem] call: GET https://api.semanticscholar.org/graph/v1/paper/search
    params: query=" ".join(query_terms), fields="title,abstract,year,citationCount",
    limit=10. Lexical/citation-graph recall — catches exact-terminology reuse and
    highly-cited canonical prior art."""
    ...  # real HTTP call; returns list of {title, abstract, year, citationCount}

def undermind_search(unit_text: str) -> list[dict]:
    """[sem] call: undermind semantic/embedding search over the full unit_text
    (not just extracted terms) — catches relabeled/paraphrased prior art that a
    lexical query would miss. Returns list of {title, abstract, year, score}."""
    ...  # real API call

def clinicaltrials_field_activity(domain_terms: list[str]) -> int:
    """[ext] call: ClinicalTrials.gov v2 search_trials with condition/intervention
    = domain_terms; returns count of actively-recruiting or completed trials
    directly targeting the same clinical question. Used ONLY as an impact-rubric
    input (§6.3), never as a novelty signal — an active trial pipeline is a
    field-investment signal, not proof the specific gap is already closed."""
    ...  # real API call; return len(trials) or 0 if domain is non-clinical
```

Retrieval confidence per unit:

```python
def retrieval_confidence(unit: NoveltyUnit, ss_hits: list[dict], um_hits: list[dict]) -> float:
    if not unit.searchable:
        return 0.0          # unsearchable unit: zero confidence, never "assume novel"
    if not ss_hits and not um_hits:
        return 0.6          # both indexes empty: plausible novelty, but capped —
                             # never treated as certain (index blind-spot risk)
    return 1.0               # got real candidates to judge against — full confidence
                              # in whatever the judge step concludes
```

### 6.3 Step 3 — LLM judge calls (exact prompts, deterministic conversion)

**Prompt A — per (unit, candidate) overlap judgment**, run for every hit returned by either search
(top 10 from semantic-scholar + top 10 from undermind, de-duplicated by title):

```
You are assessing whether a candidate published work already accomplishes a claimed research
contribution. Judge the SPECIFIC technical core only — shared topic area is not overlap.

CLAIMED CONTRIBUTION (type: {unit_type}):
{unit_text}

CANDIDATE PRIOR WORK:
Title: {candidate.title}
Year: {candidate.year}
Abstract: {candidate.abstract}

Does the candidate already accomplish, state, or substantially anticipate the SAME specific
technical core as the claimed contribution (not merely the same general topic)?

Respond with ONLY this JSON, no other text:
{"overlap_degree": "none"|"partial"|"substantial"|"identical",
 "same_technical_core": true|false,
 "reasoning": "<=40 words, cite the specific matching or differing technical element"}
```

Deterministic conversion (no free-form score accepted from the model):

```python
_OVERLAP_TO_STRENGTH = {"none": 0.0, "partial": 0.35, "substantial": 0.7, "identical": 1.0}

def judge_overlap(unit: NoveltyUnit, candidate: dict, llm_call) -> tuple[float, dict]:
    """llm_call(prompt: str) -> str; caller supplies the model interface.
    Returns (prior_art_strength, raw_judgment_dict) for logging/audit."""
    prompt = PROMPT_A.format(unit_type=unit.unit_type, unit_text=unit.text,
                              title=candidate["title"], year=candidate.get("year", "n/a"),
                              abstract=candidate.get("abstract", "")[:1500])
    raw = json.loads(llm_call(prompt))
    assert raw["overlap_degree"] in _OVERLAP_TO_STRENGTH  # hard-fail on malformed output;
                                                            # never silently default to 0
    return _OVERLAP_TO_STRENGTH[raw["overlap_degree"]], raw
```

Per-unit prior-art strength is the **max** over all candidate judgments (a single strong match
means "already done," regardless of how many weak/no-overlap results also came back):

```python
def unit_prior_art_strength(unit: NoveltyUnit, candidates: list[dict], llm_call) -> float:
    if not candidates:
        return 0.0
    return max(judge_overlap(unit, c, llm_call)[0] for c in candidates)
```

**Prompt B — impact-if-resolved rubric**, run once, on the Key Insight + Gaps jointly (impact is a
property of the problem the paper is tackling, not of any one claim):

```
Score the societal/scientific impact IF the following gap(s) were fully and correctly resolved
(assume any proposed insight, once independently validated at scale, works exactly as described).
Do not use any enthusiasm language from the source paper's own discussion — score ONLY from the
structural facts given below.

GAP(S):
{gap_statements}

KEY INSIGHT (if resolving):
{key_insight_statement}

STRUCTURAL FACTS:
- Number of claims in this artifact that causally depend on this gap being closed: {n_dependent_claims}
- Number of active/completed external clinical trials targeting the same clinical question
  (0 if non-clinical domain): {n_trials}

Score 1-5:
1 = Narrow/local — affects a small sub-community's methodological choice only.
2 = Field-relevant — changes best-practice within one subfield.
3 = Cross-field — clear translational path across multiple subfields.
4 = High-stakes — bears directly on diagnosis/treatment/safety-critical decisions, or resolves a
    widely-contested open question.
5 = Transformative — would change standard of care / a foundational assumption discipline-wide.

Respond with ONLY this JSON:
{"impact_1to5": <int 1-5>, "reasoning": "<=40 words citing the structural facts above, not prose hype"}
```

```python
def judge_impact(problem: dict, n_dependent_claims: int, n_trials: int, llm_call) -> float:
    gap_text = "\n".join(f"- {g['statement']}" for g in problem.get("gaps", []))
    prompt = PROMPT_B.format(gap_statements=gap_text or "(no gaps stated)",
                              key_insight_statement=problem.get("key_insight", {}).get("statement", "(none)"),
                              n_dependent_claims=n_dependent_claims, n_trials=n_trials)
    raw = json.loads(llm_call(prompt))
    assert raw["impact_1to5"] in (1, 2, 3, 4, 5)
    return (raw["impact_1to5"] - 1) / 4.0   # normalize to [0,1]
```

### 6.4 Step 4 — Self-disclosure cross-check

```python
def undisclosed_prior_art_penalty(unit_id: str, strong_candidates: list[dict],
                                   related_work_full: list[dict]) -> float:
    """strong_candidates = external hits judged 'substantial' or 'identical'.
    related_work_full = related_work.md's RW## blocks (only full blocks with a
    real Type+Delta count as disclosure; the 'brief' background tier does not,
    since it carries no Type/Delta and cannot demonstrate the paper engaged with
    the specific overlap).
    Returns an extra penalty in [0, 0.3] added on top of prior_art_strength.
    """
    if not strong_candidates:
        return 0.0
    disclosed_titles = {rw.get("title", "").lower() for rw in related_work_full}
    # naive title-substring match is intentionally permissive (a rough author-year
    # match keeps this from over-penalizing on data-entry formatting differences)
    for cand in strong_candidates:
        if any(cand["title"].lower() in dt or dt in cand["title"].lower()
               for dt in disclosed_titles if dt):
            return 0.05     # disclosed and (presumably) differentiated: small penalty only
    return 0.30              # strong external match with NO corresponding RW block: max penalty
```

### 6.5 Step 5 — Availability / penalize-don't-skip multiplier

Per the hard constraint: missing or thin inputs degrade the score, they never produce N/A. This
mirrors the DATA_SHAPES availability notes for `problem.md`, `claims.md`, and `related_work.md`
directly (abstract-only sources, generic `Existing attempts`/`Why they fail`, RW graphs with no
"brief" tier or under 3 full blocks).

```python
def availability_multiplier(problem: dict, related_work_full: list[dict],
                             related_work_brief: list[dict]) -> float:
    m = 1.0
    if not problem.get("key_insight", {}).get("statement"):
        m *= 0.4                      # Key Insight is mandatory-core; its absence is severe
    if not problem.get("gaps"):
        m *= 0.5
    else:
        generic = sum(1 for g in problem["gaps"]
                       if "limited" in (g.get("why_they_fail", "") or "").lower()
                       and len(g.get("why_they_fail", "")) < 40)
        if generic == len(problem["gaps"]):
            m *= 0.7                  # every Gap has a generic, unspecific failure reason
    if len(related_work_full) < 3 and not related_work_brief:
        m *= 0.5                      # abstract-only-shaped related_work.md: stark thinness signal
    return m
```

### 6.6 Step 6 — Final composite

```python
def score_M17(problem: dict, claims: list[dict], concepts: list[dict],
              related_work: dict, solution: dict, llm_call, is_clinical_domain: bool) -> dict:
    units = extract_novelty_units(problem, claims, concepts, solution)

    per_unit = []
    for u in units:
        ss_hits = semantic_scholar_search(u.query_terms) if u.searchable else []
        um_hits = undermind_search(u.text) if u.searchable else []
        all_hits = ss_hits + um_hits
        conf = retrieval_confidence(u, ss_hits, um_hits)
        strength = unit_prior_art_strength(u, all_hits, llm_call) if conf > 0 else 1.0
        # unsearchable units are NOT scored as novel-by-default: strength forced to 1.0
        # (treated as maximal prior-art risk / "we can't verify this is new" = worst case,
        # directly countering the vagueness-evades-search gaming route)
        strong = [c for c in all_hits
                  if judge_overlap(u, c, llm_call)[0] >= 0.7]
        penalty = undisclosed_prior_art_penalty(u.unit_id, strong, related_work["full"])
        effective_strength = min(1.0, strength * conf + (1 - conf) * 1.0 * (u.searchable == False) + penalty)
        per_unit.append((u, effective_strength))

    weighted_prior_art = sum(u.weight * s for u, s in per_unit) / sum(u.weight for u, _ in per_unit)
    novelty_score = 1.0 - weighted_prior_art

    n_dependent_claims = sum(1 for c in claims
                              if any(g["id"] in (c.get("dependencies") or [])
                                     for g in [{"id": u.unit_id} for u in units if u.unit_type == "gap"]))
    n_trials = clinicaltrials_field_activity(
        [t for u in units for t in u.query_terms]) if is_clinical_domain else 0
    impact_score = judge_impact(problem, n_dependent_claims, n_trials, llm_call)

    # impact is dampened if the claims meant to close the gap aren't actually
    # supported (Status != supported) — "impact if solved" requires the solving
    # to have plausibly happened, not merely be proposed
    supporting_statuses = [c["status"] for c in claims
                            if c["id"] in [u.unit_id for u in units if u.unit_type == "anchor_claim"]]
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
        "per_unit": [(u.unit_id, u.unit_type, round(s, 4)) for u, s in per_unit],
    }
```

Note on the `effective_strength` line: the `(1 - conf) * 1.0 * (u.searchable == False)` term is a
deliberate, explicit encoding of "unsearchable ⇒ treat as worst case," kept separate from the
"searchable-but-empty-index" branch (`conf = 0.6`) which instead lets `strength` (forced to `1.0`
when `conf == 0` is impossible since searchable units always get `conf ∈ {0.6, 1.0}`) — the two
zero-evidence scenarios (can't search vs. searched-and-found-nothing) are intentionally scored
differently: total silence from a well-formed query is treated as **provisional** novelty (capped at
`0.6` confidence in the "no overlap" conclusion), never as *proof* of novelty, whereas a query too
vague to even attempt is scored as the worst case outright.

## 7. Penalize-don't-skip summary (explicit)

- Missing Key Insight / no Gaps in `problem.md` → `availability_multiplier` collapses toward 0.4–0.5,
  not skipped (§6.5).
- Generic `Existing attempts`/`Why they fail` across all Gaps → multiplier ×0.7 (compression/laziness
  signal per DATA_SHAPES §4 availability notes).
- Thin/abstract-only `related_work.md` (fewer than 3 full RW blocks and no brief tier) → multiplier
  ×0.5 — the metric does not require external search to be skipped just because the artifact's own
  disclosure is thin; the search still runs, and thinness is *additionally* penalized on top of
  whatever prior-art strength search finds.
- Unsearchable novelty units (too vague to query) → scored as maximal prior-art strength (worst case),
  never dropped from the weighted average and never scored as "presumed novel."
- Empty/zero search results → capped confidence (0.6), not certainty; contributes to, but does not
  fully unlock, the novelty score.
- Malformed LLM judge output → hard assertion failure in the pipeline (§6.3), not a silent default —
  this is a compute-workflow robustness requirement, not a scoring rule, but it enforces the same
  "no free pass on missing/bad data" principle.

## 8. Composition with the rest of the suite

M17 is deliberately narrow: it does not re-check internal claim-evidence grounding (that's the Seal
Level 1 / claims-comprehensiveness metrics' job), does not check FOL-formalizability (a separate
concepts/claims-layer metric), and does not check dataset/method validity (solution-layer metrics).
It consumes the outputs of those other checks only incidentally (e.g., claim `Status` to dampen
impact, `Dependencies` to find the anchor claim) but never duplicates their scoring logic. Where it
overlaps in *subject matter* with the related-work-comprehensiveness indicator (DATA_SHAPES §6
indicators: "dependency graph comprehensiveness"), the overlap is intentional and asymmetric: that
metric scores whether `related_work.md` is internally well-formed and complete; M17 scores whether
what `related_work.md` (and the rest of the artifact) *claims* about novelty actually holds up against
the outside world. A downstream aggregator can safely sum both without double-counting because one is
purely internal-structure and the other is purely external-grounding — removing either loses a
distinct, non-redundant signal.

M17 expander1: done
