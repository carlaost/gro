# M14 Expansion: Reference-landscape completeness (cycle 3, revision B — final)

## Changes (cycle 3)

This is the final pass. It addresses every cycle-3 direction the round-2 critique named against this
lineage (former `exp1`, Rank 2 in cycle 2), while keeping the three things two rounds of critique have
now confirmed as this proposal's strongest, most Goodhart-resistant features: the single dominant
`external_coverage` term, the asymmetric relation-weighted `miss_penalty`, and the capped
importance-ranked top-25 recall gold set.

1. **Conceptual-coverage tier reweighted so it is a real signal, not cosmetic (cycle-3 direction 1).**
   In cycle 2, `conceptual_bonus` entered `external_coverage` at a `0.05` sub-weight and was itself
   halved (`soft_count(...) * 0.5`), so the entire tier — extraction, gating, capping — could move the
   final score by at most ~1.75%. It is now a first-class `0.18` sub-term inside `external_coverage`
   with the dampener removed, so genuine uncited-but-anchored landscape awareness can move the final
   score by up to ~6.3% (`0.18 * 0.35`). The 35%-of-covered-weight cap and the specific-artifact gate
   (now hardened, see #2) still bound the abuse case; the difference is that satisfying the gate now
   actually earns something.
2. **Explicit, disciplined, shared checkable-artifact extractor (cycle-3 direction 2, and the shared
   cross-lineage theme).** Cycle 2 said conceptual-coverage matching used "the same extraction used for
   the ARA's own blocks" without ever defining that extraction, and left `r.get("artifacts", [])` on
   candidates assumed pre-populated by nothing in particular. `extract_artifacts()` is now fully
   specified: it excludes bare years and unit-less generic integers, requires numeric anchors to carry
   a decimal, an `n=` count, or a unit; requires named-entity anchors to be mixed-alphanumeric tokens,
   multi-word proper-noun phrases (with a common-word/section-heading stoplist on the first token), or
   3–8 letter acronyms (excluding a small stoplist of non-distinctive all-caps words) — explicitly
   excluding bare two-letter disease/domain abbreviations like "AD" that the critique flagged as a
   plausible false-match risk. It is applied identically to ARA `problem.md` blocks and to every
   external candidate's title+abstract/tldr, with an explicit population step in "External calls" so
   `candidate["artifacts"]` is never silently empty.
3. **`trace_external_grounding` tightened (cycle-3 direction 3).** The Jaccard floor is raised from
   `0.20` to `0.32`; a node is now grounded via Jaccard only if it *also* shares a checkable artifact
   (via the same extractor from #2) with the best-matching candidate, and only if that best match leads
   the second-best candidate by a `>=0.05` margin — closing the "generic same-subfield overlap clears a
   low bar" gaming route the critique identified, where a confidently-written, topically-adjacent dead
   end could clear 0.20 Jaccard without truly corresponding to the externally-inferior approach it
   claims.
4. **`api_available` collapsed to a single scoring location (cycle-3 direction 4).** Cycle 2 rewarded/
   penalized a clean vs. failed search in three places: a standalone `+0.10 * api_ok` term inside
   `external_coverage`, a `+0.05` line in `thin_penalty` when it failed, and implicitly again through
   `contra_recall`'s and `trace_landscape`'s own `api_ok`-gated defaults. The standalone
   `external_coverage` term and the `thin_penalty` line are both removed; `api_available` now enters the
   score exactly once, as a `0.20` component of `availability` (which the critique itself named as "the
   natural home"). `contra_recall`, `close_recall`, and `trace_landscape` keep their own already-present
   `api_ok`-gated *defaults* (governing what "no evidence" means), which is a different function from a
   standalone reward/penalty term and is retained.
5. **`has_ref_match` now resolves against the external candidate set, not the ARA's own citations
   (cycle-3 direction 5).** Cycle 2's check — `citation_key(ref) in ara_keys` — only confirmed that a
   trace node's `source_refs` entry matched something the ARA cited *somewhere*, which is circular and
   proves nothing about external grounding. It now checks `citation_key(ref) in ext_keys`, where
   `ext_keys` is built from `L ∪ K` (the external candidate pool), so a source-ref match actually
   delivers the "corresponds to an externally-surfaced approach" guarantee the fix claims.
6. **Relation-type assignment made robust to classification failure (shared cycle-3 theme).** The
   critique noted that both lineages have a load-bearing `relation_type` that neither fully specifies
   under degraded conditions. In this design, `relation_type` was always sourced from the per-candidate
   LLM classification prompt (independent of whether Undermind is available), which avoids sibling A's
   specific failure mode (an empty pool when Undermind is off) — but the classification call itself can
   still fail per-candidate. This revision adds an explicit fallback (`relation="background"`,
   `relevance=0.5`, `classification_failed=True`) and a degraded-run rule: if more than 30% of `L ∪ K`
   has `classification_failed=True`, the run is treated as `api_available=False` for scoring purposes
   even though raw retrieval succeeded, since `miss_penalty`, `importance`, and the trace relation gate
   all silently mis-score if classification quietly degrades to "everything is background."

Everything else — availability-first scoring, penalize-don't-skip, the six named countermeasures
(citation-stuffing, search-term-overfitting, hiding-contradictions, fabricated-specificity,
genre-mismatch, conceptual-coverage-gaming), and the cycle-2 fixes (external trace grounding at all,
genre-sensitive `contra_recall`, capped importance-ranked recall, gated conceptual tier) — is retained
and re-verified against `04_problem.md` and the brief below.

## Expanded reasoning

Reference-landscape completeness measures whether the ARA's problem framing is anchored in the actual
surrounding literature, not just in whatever citations happened to appear in the source paper's abstract
or introduction. Good science should locate its question where prior work actually left uncertainty: it
should identify the closest technical neighbors, the main supporting traditions, direct baselines,
reused datasets or methods, and relevant contradictory or limiting results. This metric is net-new
because it verifies that landscape externally through Semantic Scholar / Undermind-style search, instead
of trusting the ARA's internal citations alone — per the brief, this is "the single biggest hole"
neither round-1 nor the ARA verifier reaches, and it ranked top-10 specifically for being net-new and
tightly scoped. Three cycles in, the design keeps one dominant external-coverage term rather than
diluting it across many components (the failure mode that sank the `exp4`/`exp3` critiques in round 1),
and every hardening pass has been a targeted repair of a specific leak, not new surface area.

The primary signal is the alignment among three layers, matching `04_problem.md` and the brief's
cross-references:

- `logic/problem.md` (§4 shape): Observation blocks (`Statement`/`Evidence`/`Implication`), Gap blocks
  (`Statement`/`Caused by`/`Existing attempts`/`Why they fail`), Key Insight, Assumptions — should cite a
  specific, non-generic pre-existing landscape, not `Evidence: Abstract` restatements (§4's own
  documented degradation signal).
- `logic/related_work.md` (§6 shape): the typed dependency graph should preserve both high-delta
  citations and a brief full citation footprint.
- `trace/exploration_tree.yaml` (§8 shape): decisions, dead ends, pivots, and the starting question
  should reflect real prior alternatives and known failures **when the external search actually surfaces
  them** — not merely read as internally specific, and not merely resolve against the ARA's own
  bibliography.

The metric rewards ARAs that name close prior work, explain how each close work imports, bounds,
extends, baselines, or refutes the target paper, and connect those references to concrete gaps and
decisions. It especially rewards explicit contradiction handling: prior findings with opposite
conclusions, failed approaches, negative baselines, known limitations, or subgroup-specific exceptions —
scored against what the external search genuinely turns up for that genre, never against a fixed
per-paper refutation quota. It does not reward citation volume by itself, and it credits genuine
landscape awareness expressed without a formal citation only when that awareness is anchored to a
checkable, distinctive artifact rather than vague topic overlap — and, as of cycle 3, that credit is
large enough to matter rather than a rounding error.

Missing or thin inputs are never skipped. Availability is part of the score. If `related_work.md` is
missing, unparseable, or lacks a brief footprint tier, the score falls. If `problem.md` uses only
`Evidence: Abstract`, generic "prior work is limited" language, or a key insight that simply restates the
method name, the score falls. If `trace/exploration_tree.yaml` is missing or has no useful
decisions/dead ends where external literature clearly shows abandoned or inferior paths, the score
falls — but a genre where the external search finds no comparably strong alternative paths is not
punished as if a file were missing. External API failure — including a classification degradation where
retrieval succeeded but relation-typing silently failed on most candidates (fix #6) — is penalized once,
explicitly, inside `availability`, and the affected downstream terms (`contra_recall`, `close_recall`,
`trace_landscape`) fall back to their own genre-sensitive defaults rather than being penalized a second
or third time for the same failure.

### Failure modes and gaming routes

- **Citation stuffing**: adding many background references without typed deltas. Countered by weighting
  close-neighbor recall (against a capped, importance-ranked gold set) and typed role quality above raw
  count.
- **Search-term overfitting**: mentioning trendy keywords to retrieve a broad island. Countered by
  deriving queries from the problem observations/gaps/key insight and checking semantic overlap at
  paper-title/abstract level.
- **Hiding contradictions**: citing only supportive work. Countered by an explicit contradiction/bounds
  search and a missed-neighbor penalty, with genre-sensitive scoring so absence-of-contradiction genres
  aren't falsely flagged, and so hiding a real contradiction is distinguishable from a genre that has
  none.
- **Fabricated specificity**: giving detailed RW blocks for references that are not close or not used.
  Countered by DOI/title normalization and Semantic Scholar match checks.
- **Genre mismatch**: expecting dead ends or refutations from papers that do not report them. Countered
  by scoring trace coverage and contradiction recall as genre-sensitive modifiers gated on
  `api_available`, while still penalizing missing files and unsupported explicit nodes.
- **Conceptual-coverage gaming**: vaguely name-dropping a concept to claim "I covered that" without a
  real citation. Countered by requiring a specific matching artifact from the disciplined shared
  extractor (fix #2) — which excludes bare years, unit-less numbers, and generic short abbreviations —
  before any conceptual-coverage credit is granted, and by capping conceptual coverage at 35% of total
  covered weight so it can only ever supplement direct citations, never substitute for them. Because the
  tier now carries real weight (fix #1), this gate is load-bearing rather than decorative.
- **Trace-grounding gaming**: writing confident, specific-sounding prose about a "dead end" that has no
  correspondent in the external candidate set, or that only vaguely overlaps a same-subfield abstract.
  Countered by a raised Jaccard floor, a required shared checkable-artifact match, and a required
  best-match margin over the runner-up candidate (fix #3), plus an external (not internal) identity
  check on any declared `source_refs` (fix #5).
- **Relation-type laundering (new, cycle-3 hardened)**: a compiler could quietly let LLM
  relation-classification fail or default everything to `background`, silently emptying the
  high-importance miss-penalty pool and the trace relation gate — a free pass dressed up as a clean run.
  Countered by explicit `classification_failed` tracking and a 30%-failure threshold that forces the run
  to be scored as a degraded (`api_available=False`) run (fix #6).
- **Availability double-dipping**: previously, a clean or failed search was rewarded/penalized in three
  separate places, which both over-weighted a single binary and created room for a compiler to make
  strategic bets about which term mattered most. `api_available` now scores in exactly one place (fix
  #4), removing that surface entirely.

This composes well with internal verifier metrics because it tests a different boundary: not whether the
ARA is internally grounded, but whether its grounding covers the externally visible scientific
neighborhood. It should be run after structural parsing metrics and before novelty/gap metrics; its
output can supply a calibrated "landscape coverage" prior for those later metrics.

## Concrete generation/compute workflow

### Inputs

Required artifact texts, assumed requested from one compiled ARA root:

- `logic/problem.md` using the §4 shape: Observation blocks, Gap blocks, Key Insight, Assumptions.
- `logic/related_work.md` using the §6 shape: `RW##` full blocks plus any brief citation footprint
  section.
- `trace/exploration_tree.yaml` using the §8 shape: YAML `tree:` nodes.
- Optional metadata supplied by the runner if available: target paper title, DOI/arXiv ID, abstract,
  authors, year, venue. If unavailable, derive search queries from `problem.md` and penalize metadata
  absence in `availability` (see Scoring function).

Assumption if the runner exposes only the primary artifact: score the cross-layer terms as missing/thin
rather than N/A. The metric brief names §6 and §8, so a production runner should pass them.

### Parse and normalize

1. Parse `problem.md` by markdown headings:
   - observations: `### O\d+`, fields `Statement`, `Evidence`, `Implication`
   - gaps: `### G\d+`, fields `Statement`, `Caused by`, `Existing attempts`, `Why they fail`
   - key insight fields `Insight`, `Derived from`, `Enables`
   - assumptions: `A\d+:`
2. Parse `related_work.md`:
   - full blocks: `## RW\d+`, `DOI`, `Type`, `Delta / What changed`, `Delta / Why`, `Claims affected`,
     `Adopted elements`
   - brief citations: bullets under headings containing `Background`, `supporting`, `Additional citation
     footprint`, or `brief`
3. Parse `exploration_tree.yaml` with a YAML parser. Flatten all nodes recursively through `children`;
   retain `also_depends_on`.
4. Normalize citations into records:
   - `doi_norm`: lowercase DOI if present and not "Not specified"
   - `title_or_label`: heading text or bold author-year label
   - `role_text`: concatenated type, delta, adopted elements, brief role
   - `source_layer`: `problem_evidence`, `related_full`, `related_brief`, `trace_source_ref`
5. Extract ARA query terms from:
   - top 8 noun phrases from observation/gap/key-insight statements
   - explicit study objects, methods, biomarkers, datasets, baselines, populations, outcomes
   - target title/abstract when available
   - **checkable artifacts, per O/G/Insight block**: `artifacts_by_block[block_id] = extract_artifacts(
     concat(Statement, Evidence, Implication or Caused by/Existing attempts/Why they fail or
     Insight/Enables))`, using the shared extractor defined below. Used only for conceptual-coverage
     matching and trace-artifact matching, never for recall itself.

### Shared checkable-artifact extractor (cycle-3 hardening, fix #2)

One extractor, used identically on ARA-side text (`problem.md` blocks, trace node text) and
external-side text (candidate title + abstract/tldr). It is deliberately conservative: it must surface
tokens a vague topical paraphrase would *not* naturally contain.

```python
import re

UNIT_NUM_RE = re.compile(
    r"\bn\s*=\s*\d+\b"
    r"|\b\d+\.\d+\b"
    r"|\b\d+(?:\.\d+)?\s?(%|mg|ml|kg|mm|cm|nm|pg/ml|ng/ml|years?|yrs?|months?|days?|hours?|hrs?)\b",
    re.I,
)
BARE_YEAR_RE = re.compile(r"^(19|20)\d{2}$")
MIXED_ALNUM_RE = re.compile(r"\b(?=[A-Za-z0-9-]*\d)(?=[A-Za-z0-9-]*[A-Za-z])[A-Za-z][A-Za-z0-9-]{2,}\b")
ACRONYM_RE = re.compile(r"\b[A-Z]{3,8}\b")
MULTIWORD_PROPER_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b")

GENERIC_ACRONYM_STOP = {
    "THE", "AND", "FOR", "ARE", "WAS", "ALL", "NOT", "ONE", "TWO", "USA", "AKA",
}
STOPWORD_CAP_START = {
    "the", "introduction", "abstract", "results", "methods", "method", "study",
    "table", "figure", "background", "discussion", "conclusion", "paper",
    "article", "this", "these", "those", "data", "analysis", "approach",
    "overview", "summary", "review", "appendix",
}

def norm_artifact(s):
    return re.sub(r"\s+", " ", s.strip().lower())

def extract_artifacts(text):
    """
    Distinctive, checkable artifacts only: numbers with units/decimals/counts, mixed-alphanumeric
    named entities (p-tau217, GPT4, BRCA1), 3-8 letter acronyms excluding a short generic stoplist
    (deliberately excludes 2-letter disease/domain abbreviations like "AD"), and multi-word proper-noun
    phrases whose first token is not a section-heading/common word. Bare years are excluded everywhere.
    A vague topical paraphrase of a subject should not, by construction, reproduce these tokens.
    """
    if not text:
        return set()
    arts = set()
    for m in UNIT_NUM_RE.finditer(text):
        arts.add(norm_artifact(m.group(0)))
    for m in MIXED_ALNUM_RE.finditer(text):
        tok = m.group(0)
        if BARE_YEAR_RE.match(tok):
            continue
        arts.add(norm_artifact(tok))
    for m in ACRONYM_RE.finditer(text):
        tok = m.group(0)
        if tok in GENERIC_ACRONYM_STOP:
            continue
        arts.add(norm_artifact(tok))
    for m in MULTIWORD_PROPER_RE.finditer(text):
        phrase = m.group(0)
        if phrase.split()[0].lower() in STOPWORD_CAP_START:
            continue
        arts.add(norm_artifact(phrase))
    return {a for a in arts if not BARE_YEAR_RE.match(a)}
```

### External calls

All external calls return structured JSON and are cached by target DOI/title plus query string.

1. Semantic Scholar target lookup:
   - Query: target DOI if available, else target title.
   - Fields: `paperId,title,abstract,year,authors,externalIds,references,citations,embedding,tldr,
     fieldsOfStudy`
   - Output: target paper identity and its reference list where available.
2. Semantic Scholar k-nearest / island search:
   - Query 1: target title + abstract, embedding nearest papers if API supports vector/recommendations.
   - Query 2: `"key insight terms" AND "gap terms"` from parsed problem fields.
   - Query 3: each major `G#` statement plus domain/population/outcome terms.
   - Keep up to 500 candidate papers after dedupe by DOI/paperId/title.
3. Contradiction/bounds search:
   - For each top gap and key insight, query:
     - `(<domain terms>) (<method/object terms>) contradict OR inconsistent OR failed OR limitation OR
       negative OR no improvement OR baseline`
     - `(<main method/object>) versus <baseline terms>`
   - Keep up to 100 candidate papers, merged into the same candidate set with a flag
     `contradiction_query=True`.
4. Undermind or equivalent deep literature search, if available:
   - Prompt/query:
     ```
     Find the most relevant prior and contemporaneous scientific works for this paper's problem framing.
     Target: {title_or_derived_problem}
     Problem observations: {O statements}
     Gaps: {G statements}
     Key insight: {key insight}
     Return JSON list of papers with title, DOI/arXiv, year, relevance 0-1, relation type
     in {imports,bounds,baseline,extends,refutes,background}, and whether it contradicts or limits
     the target's premise.
     ```
   - Use returned relevance only after DOI/title dedupe; do not accept prose claims without bibliographic
     identity.
5. **Artifact population (cycle-3 addition, fix #2).** For every candidate now in the merged pool
   (Semantic Scholar island + contradiction search + Undermind, deduped), compute
   `candidate["artifacts"] = extract_artifacts(candidate["title"] + " " + candidate.get("abstract_or_tldr", ""))`
   using the identical extractor defined above. This step is mandatory and runs before any conceptual-
   coverage or trace-grounding matching; a candidate with `artifacts` unset is treated as `set()`, never
   as "match anything."

### LLM semantic classification

Use an LLM only to classify relevance and relation type where metadata/abstract text is available. The
LLM output is converted into deterministic scores. This classification runs regardless of whether
Undermind is available — it is the sole source of `relation_type` in S2-only mode, so the miss-penalty
pool and trace relation gate do not depend on Undermind being on.

Prompt for each candidate, batched:

```text
You are scoring literature-landscape relevance for an ARA.
Target problem:
Observations: {O statements}
Gaps: {G statements}
Key insight: {insight}

Candidate paper:
Title: {title}
Abstract/TLDR: {abstract_or_tldr}
Year: {year}

Return JSON only:
{
  "relevance": 0.0-1.0,
  "relation": "imports|bounds|baseline|extends|refutes|background|unrelated",
  "is_close_neighbor": true|false,
  "is_contradictory_or_limiting": true|false,
  "rationale": "one short sentence"
}
```

Deterministic use: discard candidates with `relevance < 0.55` unless they are in the target paper's own
reference list; define close-neighbor set `L` as candidates with `is_close_neighbor=true` or
`relevance >= 0.72`. Rank `L` by `importance = 0.6*relevance + 0.4*relation_weight`
(`relation_weight`: `refutes`=1.0, `baseline`=0.9, `imports`=0.8, `bounds`=0.7, `extends`=0.6,
`background`=0.3) and cap the *recall gold set* `L_top` at the top 25 by `importance`; retain the full
capped-80 `L` separately only as the pool from which `miss_penalty` draws (so an ARA cannot dodge the
miss penalty just because a very-high-relevance paper falls outside the top-25 recall denominator).
Define contradiction set `K` as candidates with `is_contradictory_or_limiting=true` and
`relevance >= 0.60`, capped at 40.

#### Relation-type degradation handling (cycle-3 addition, fix #6)

If the classification call for a candidate fails, times out, or returns invalid/unparseable JSON:
assign `relation = "background"`, `relevance = 0.5`, and set `classification_failed = True` on that
candidate. Do not drop the candidate from `L`/`K` — dropping it would silently shrink the recall
denominator, which is its own Goodhart route. Instead, after classification completes over the full
pool:

```python
def classification_degraded(pool):
    if not pool:
        return False
    failed = sum(1 for r in pool if r.get("classification_failed"))
    return (failed / len(pool)) > 0.30
```

If `classification_degraded(L + K)` is true, the run's `api_available` flag is forced to `False` for
scoring purposes even if retrieval itself succeeded, because a run where relation-typing silently failed
on most candidates cannot support `miss_penalty`, `importance` ranking, or the trace relation gate — all
three would otherwise report a spuriously clean landscape.

### Conceptual-coverage matching (fix #4 from cycle 2; extractor and weighting hardened in cycle 3, fixes
#1 and #2)

For each candidate in `L` not matched by DOI/title to any ARA citation:

1. Read `candidate["artifacts"]` (populated in External calls step 5, using `extract_artifacts`).
2. Check whether any ARA `problem.md` O/G/Insight block's `artifacts_by_block[block_id]` (also from
   `extract_artifacts`, parsed in step 5 of Parse and normalize) intersects the candidate's artifact set.
   Exact normalized-string match — the extractor's job is to make this exact match meaningful, not the
   matching logic's job to be fuzzy.
3. If yes, mark the candidate `conceptually_covered=True` with `coverage_weight = 0.5 * importance`
   (half credit relative to a full formal citation, since it lacks a checkable typed delta).
4. `conceptual_covered_weight = sum(coverage_weight for conceptually_covered candidates)`;
   `direct_covered_weight` from DOI/title-matched candidates in `L_top ∪ K` at full `importance`. Cap:
   `conceptual_covered_weight ≤ 0.35 * (direct_covered_weight + conceptual_covered_weight)`; excess
   conceptual weight is discarded before scoring, not redistributed. Unlike cycle 2, the resulting
   `conceptual_bonus` is no longer damped by an extra `* 0.5` and carries a full `0.18` sub-weight inside
   `external_coverage` (see Scoring function) — the cap is now the only ceiling on this tier's influence,
   which is the point: the guard should be doing real work, not decorating a term that can't move.

### Trace external grounding (fix #1 from cycle 2; floor, artifact requirement, and margin added in
cycle 3, fix #3; identity resolution corrected in cycle 3, fix #5)

For each `decision`/`dead_end`/`pivot` node in the parsed trace:

1. Build `node_text` from `title`/`hypothesis`/`failure_mode`/`lesson`/`choice`/`alternatives`/`trigger`.
2. Build `ext_pool = L ∪ K` and `ext_keys = {citation_key(r) for r in ext_pool}` — the external identity
   set. `has_ref_match` is `True` only if a `source_refs` entry DOI/title-resolves into `ext_keys`
   (**not** into the ARA's own `ara_keys`, which cycle 2 incorrectly used and which only proved internal
   self-consistency).
3. Compute `node_artifacts = extract_artifacts(node_text)` with the shared extractor.
4. Compute Jaccard token overlap between `node_text` and every candidate's title+abstract/tldr in
   `ext_pool`; rank candidates by overlap. Let `best_overlap`/`best_rec` be the top match and
   `second_overlap` the runner-up's overlap (0 if none).
5. A node is `externally_grounded=True` if `has_ref_match`, **or** all of:
   - `best_overlap >= 0.32` (raised from 0.20 — same-subfield abstracts routinely share ~0.15-0.25 on
     raw 4-char tokens, so 0.20 was gameable by topical adjacency alone),
   - `best_rec.relation in {baseline, bounds, refutes}`,
   - `node_artifacts & best_rec["artifacts"]` is non-empty (the node and the candidate must share at
     least one distinctive checkable artifact — a named method, dataset, cohort, or quantified figure —
     not just overlapping vocabulary), and
   - `best_overlap - second_overlap >= 0.05` (the match must clearly lead the field; a near-tie against
     several same-subfield candidates is not treated as a confident correspondence to one real abandoned
     approach).
6. A node is `ungrounded_explicit` if `support_level == "explicit"` and it is a `decision`/`dead_end`/
   `pivot` type but not `externally_grounded` and has no `source_refs` at all.

### Scoring function

Python reference implementation against parsed records:

```python
import math
import re
from collections import Counter

GENERIC_FAIL = re.compile(r"\b(prior work|previous studies|limited|unclear|not well understood|further research)\b", re.I)
ABSTRACT_ONLY = re.compile(r"^\s*(abstract|title|not specified)\s*$", re.I)

RELATION_WEIGHT = {
    "refutes": 1.0, "baseline": 0.9, "imports": 0.8,
    "bounds": 0.7, "extends": 0.6, "background": 0.3, "unrelated": 0.0,
}

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def soft_count(n, target):
    return clamp(math.log1p(max(n, 0)) / math.log1p(target))

def norm_id(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def citation_key(rec):
    return (rec.get("doi_norm") or norm_id(rec.get("title_or_label", "")))[:120]

def jaccard_tokens(a, b):
    ta, tb = set(re.findall(r"[a-z0-9]{4,}", (a or "").lower())), set(re.findall(r"[a-z0-9]{4,}", (b or "").lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def block_specificity(text):
    if not text:
        return 0.0
    tokens = re.findall(r"[A-Za-z0-9_.-]+", text)
    has_number = bool(re.search(r"\b\d+(?:\.\d+)?\b", text))
    has_named_entityish = sum(1 for t in tokens if len(t) > 3 and (t[0].isupper() or any(c.isdigit() for c in t)))
    generic_penalty = 0.35 if GENERIC_FAIL.search(text) and len(tokens) < 35 else 0.0
    return clamp(0.35 * soft_count(len(tokens), 45) + 0.35 * soft_count(has_named_entityish, 6) + 0.15 * has_number + 0.15 - generic_penalty)

def importance(rec):
    return clamp(0.6 * rec.get("relevance", 0.0) + 0.4 * RELATION_WEIGHT.get(rec.get("relation", "background"), 0.3))

def classification_degraded(pool):
    if not pool:
        return False
    failed = sum(1 for r in pool if r.get("classification_failed"))
    return (failed / len(pool)) > 0.30

# extract_artifacts(), UNIT_NUM_RE, BARE_YEAR_RE, MIXED_ALNUM_RE, ACRONYM_RE, MULTIWORD_PROPER_RE,
# GENERIC_ACRONYM_STOP, STOPWORD_CAP_START, norm_artifact() as defined above (fix #2).

def score_m14(parsed, external):
    """
    parsed keys:
      problem_available, related_available, trace_available, metadata_available: bool
      observations, gaps: list[dict]
      key_insight: dict
      related_full, related_brief: list[dict]
      trace_nodes: list[dict]
      artifacts_by_block: dict[block_id -> set[str]]   # via extract_artifacts, populated at parse time
    external keys:
      close_neighbors: list[dict]        # L, each w/ relevance, relation, title, abstract_or_tldr, artifacts
      contradiction_neighbors: list[dict]  # K, same shape
      api_available: bool                # raw retrieval success signal, pre-degradation-check
    """
    close = external.get("close_neighbors", [])
    contra = external.get("contradiction_neighbors", [])
    ext_pool = close + contra
    # fix #6: relation-classification degradation forces api_available False even if retrieval succeeded
    api_ok = bool(external.get("api_available")) and not classification_degraded(ext_pool)

    # fix #4: api_ok now scores in exactly one place — here, inside availability.
    availability = (
        0.25 * bool(parsed.get("problem_available")) +
        0.30 * bool(parsed.get("related_available")) +
        0.15 * bool(parsed.get("trace_available")) +
        0.10 * bool(parsed.get("metadata_available")) +
        0.20 * api_ok
    )

    obs = parsed.get("observations", [])
    gaps = parsed.get("gaps", [])
    insight = parsed.get("key_insight") or {}
    evidence_depth = [0.0 if ABSTRACT_ONLY.search(o.get("Evidence", "")) else block_specificity(o.get("Evidence", "")) for o in obs]
    gap_depth = [
        0.5 * block_specificity(g.get("Existing attempts", "")) + 0.5 * block_specificity(g.get("Why they fail", ""))
        for g in gaps
    ]
    problem_depth = (
        0.30 * soft_count(len(obs), 4) +
        0.25 * soft_count(len(gaps), 3) +
        0.20 * (sum(evidence_depth) / max(1, len(evidence_depth))) +
        0.15 * (sum(gap_depth) / max(1, len(gap_depth))) +
        0.10 * block_specificity(insight.get("Insight", ""))
    ) if parsed.get("problem_available") else 0.0

    full = parsed.get("related_full", [])
    brief = parsed.get("related_brief", [])
    type_counts = Counter((r.get("Type", "") or "").split()[0] for r in full)
    relation_diversity = len(set(t for t in type_counts if t in {"imports", "bounds", "baseline", "extends", "refutes"})) / 5
    full_quality = sum(block_specificity(" ".join([
        r.get("Type", ""), r.get("What changed", ""), r.get("Why", ""), r.get("Adopted elements", "")
    ])) for r in full) / max(1, len(full))
    brief_tier = 1.0 if len(brief) >= 5 else (0.45 if len(brief) > 0 else 0.0)
    related_depth = (
        0.25 * soft_count(len(full), 12) +
        0.20 * soft_count(len(brief), 25) +
        0.25 * full_quality +
        0.15 * relation_diversity +
        0.15 * brief_tier
    ) if parsed.get("related_available") else 0.0

    ara_keys = {citation_key(r) for r in full + brief if citation_key(r)}
    ext_keys = {citation_key(r) for r in ext_pool if citation_key(r)}  # fix #5: external identity set

    # capped, importance-ranked recall gold set (top-25), separate from the full miss-penalty pool
    close_ranked = sorted(close, key=importance, reverse=True)
    close_top = close_ranked[:25]
    close_top_keys = {citation_key(r) for r in close_top if citation_key(r)}
    close_recall = len(ara_keys & close_top_keys) / max(1, len(close_top_keys)) if close_top_keys else (0.7 if api_ok else 0.0)

    contra_keys = {citation_key(r) for r in contra if citation_key(r)}
    if contra_keys:
        contra_recall = len(ara_keys & contra_keys) / len(contra_keys)
    else:
        # genre-sensitive default: search ran and found nothing contradictory -> partial credit for
        # genre-appropriate silence, not a penalty. Only degrade toward 0 if search itself failed
        # (including the classification-degradation case folded into api_ok above).
        contra_recall = 0.75 if api_ok else 0.0

    # weighted, asymmetric miss penalty: misses weighted by relation importance
    high_rel_misses = [r for r in close if citation_key(r) not in ara_keys and r.get("relevance", 0) >= 0.85]
    weighted_miss = sum(importance(r) for r in high_rel_misses)
    miss_penalty = clamp(weighted_miss / 6.0)

    # fix #2: disciplined shared extractor: artifacts_by_block and candidate["artifacts"] both come
    # from extract_artifacts(), populated at parse time / in External calls step 5 respectively.
    artifacts_by_block = parsed.get("artifacts_by_block", {})
    all_ara_artifacts = set()
    for s in artifacts_by_block.values():
        all_ara_artifacts |= set(s)
    direct_covered_weight = sum(importance(r) for r in close_top + contra if citation_key(r) in ara_keys)
    conceptual_weight = 0.0
    for r in close:
        if citation_key(r) in ara_keys:
            continue
        cand_artifacts = set(r.get("artifacts", []))
        if cand_artifacts & all_ara_artifacts:
            conceptual_weight += 0.5 * importance(r)
    total_covered = direct_covered_weight + conceptual_weight
    cap = 0.35 * total_covered
    conceptual_weight_capped = min(conceptual_weight, cap) if total_covered > 0 else 0.0
    # fix #1: lifted out of the damped 0.05 sub-slot; full-strength bounded supplement now at 0.18 weight below
    conceptual_bonus = soft_count(conceptual_weight_capped * 10, 8)

    # fix #4: standalone api_ok reward term removed from external_coverage (it now lives only in availability)
    external_coverage = clamp(
        0.48 * close_recall +
        0.24 * contra_recall +
        0.10 * soft_count(len(ara_keys & close_top_keys), 15) +
        0.18 * conceptual_bonus
        - 0.28 * miss_penalty
    )

    nodes = parsed.get("trace_nodes", [])
    decisionish = [n for n in nodes if n.get("type") in {"decision", "dead_end", "pivot"}]
    trace_text = " ".join(
        " ".join(str(n.get(k, "")) for k in ["title", "hypothesis", "failure_mode", "lesson", "choice", "alternatives", "trigger"])
        for n in decisionish
    )

    grounded = []
    ungrounded_explicit = []
    for n in decisionish:
        node_text = " ".join(str(n.get(k, "")) for k in ["title", "hypothesis", "failure_mode", "lesson", "choice", "alternatives", "trigger"])
        node_artifacts = extract_artifacts(node_text)

        # fix #5: source_refs must resolve into the EXTERNAL candidate set, not the ARA's own citations
        has_ref_match = bool(n.get("source_refs")) and any(
            citation_key({"title_or_label": ref}) in ext_keys for ref in n.get("source_refs", [])
        )

        ranked = sorted(
            ((jaccard_tokens(node_text, r.get("title", "") + " " + r.get("abstract_or_tldr", "")), r) for r in ext_pool),
            key=lambda x: x[0], reverse=True,
        )
        best_overlap, best_rec = ranked[0] if ranked else (0.0, None)
        second_overlap = ranked[1][0] if len(ranked) > 1 else 0.0

        # fix #3: raised floor (0.20 -> 0.32), requires a shared checkable artifact, requires the best
        # match to clearly lead the runner-up (margin >= 0.05) rather than tying several candidates
        artifact_hit = bool(best_rec) and bool(node_artifacts & set(best_rec.get("artifacts", [])))
        margin_ok = (best_overlap - second_overlap) >= 0.05
        strong_relation_hit = (
            best_overlap >= 0.32
            and best_rec is not None
            and best_rec.get("relation") in {"baseline", "bounds", "refutes"}
            and artifact_hit
            and margin_ok
        )

        if strong_relation_hit or has_ref_match:
            grounded.append(n)
        elif n.get("support_level") == "explicit" and not n.get("source_refs"):
            ungrounded_explicit.append(n)

    trace_landscape = (
        0.20 * soft_count(len(nodes), 8) +
        0.25 * soft_count(len(decisionish), 4) +
        0.15 * block_specificity(trace_text) +
        0.25 * (soft_count(len(grounded), 3) if api_ok else 0.5 * soft_count(len(grounded), 3)) +
        0.15 * (1.0 - clamp(len(ungrounded_explicit) / 3))
    ) if parsed.get("trace_available") else 0.0

    # Penalize-don't-skip: absent/thin layers remain zero in their components and availability is explicit.
    raw = (
        0.15 * availability +
        0.18 * problem_depth +
        0.22 * related_depth +
        0.35 * external_coverage +
        0.10 * trace_landscape
    )

    # fix #4: the old `if not api_ok: thin_penalty += 0.05` line is removed — api_ok is now scored
    # exactly once, in `availability`, and must not also be double-penalized here.
    thin_penalty = 0.0
    if parsed.get("related_available") and len(full) <= 2 and len(brief) == 0:
        thin_penalty += 0.12
    if parsed.get("problem_available") and obs and all(ABSTRACT_ONLY.search(o.get("Evidence", "")) for o in obs):
        thin_penalty += 0.10

    return {
        "score": round(clamp(raw - thin_penalty), 4),
        "components": {
            "availability": round(availability, 4),
            "problem_depth": round(problem_depth, 4),
            "related_depth": round(related_depth, 4),
            "external_coverage": round(external_coverage, 4),
            "trace_landscape": round(trace_landscape, 4),
            "thin_penalty": round(thin_penalty, 4),
            "close_recall_top25": round(close_recall, 4),
            "contradiction_recall": round(contra_recall, 4),
            "weighted_missed_high_relevance": round(weighted_miss, 4),
            "conceptual_covered_weight_capped": round(conceptual_weight_capped, 4),
            "conceptual_bonus": round(conceptual_bonus, 4),
            "trace_grounded_nodes": len(grounded),
            "trace_ungrounded_explicit_nodes": len(ungrounded_explicit),
            "api_ok_effective": api_ok,
            "classification_degraded": classification_degraded(ext_pool),
        }
    }
```

### Interpretation

- `0.85-1.00`: strong landscape coverage; the ARA names most close external neighbors (by
  importance-ranked recall), captures typed deltas, includes contradicting/bounding work where
  discoverable, and its trace's abandoned paths are externally corroborated by a real, margin-clear,
  artifact-matched candidate.
- `0.60-0.85`: usable but incomplete; usually misses some top-25 close neighbors, has weak brief-footprint
  coverage, or its trace claims dead ends the external search cannot corroborate to the tightened
  standard.
- `0.35-0.60`: thin; internal citations exist but external search exposes important omissions, generic
  gap framing, or ungrounded explicit trace nodes.
- `<0.35`: abstract-only or structurally unavailable landscape; should not be used as evidence of novelty
  without recompilation.

## Why this is hard to Goodhart

The score depends on independent external retrieval, relation classification, and a weighted,
asymmetric high-relevance missed-neighbor penalty that accounts for relation type (refuting/baseline
misses cost more than background misses). Adding references helps only if they match a capped,
importance-ranked close-neighbor set and carry specific typed deltas — inflating the citation list
beyond the top-25 importance-ranked gold set buys nothing. Vague or stuffed citations raise counts but
not recall, contradiction coverage, or specificity.

The conceptual-coverage tier cannot be gamed by vague name-dropping: it requires a concrete matching
artifact from a shared extractor that explicitly excludes bare years, unit-less generic numbers, and
short generic abbreviations (including exactly the two-letter disease/domain abbreviation class that
sank a comparable guard in the sibling lineage), and it is capped at 35% of covered weight — but because
it now carries a real `0.18` sub-weight rather than a damped `0.05`, satisfying that gate is worth doing,
which is what makes the gate itself load-bearing rather than cosmetic.

The trace-grounding check means an ARA cannot claim confident, specific-sounding dead ends for credit
unless they correspond to something the external search actually surfaced as a real baseline/bound/
refutation: the match must clear a raised Jaccard floor, share a distinctive checkable artifact with
that specific candidate, and beat the runner-up candidate by a clear margin — internal narrative polish,
generic same-subfield vocabulary overlap, or a near-tie among several topically adjacent papers no
longer buys trace score. A declared `source_refs` entry only grounds a node if it resolves into the
external candidate identity set, not merely into the ARA's own bibliography, closing a circular-proof
route from cycle 2.

Genre-sensitive defaults for contradiction recall and trace grounding are explicitly conditioned on a
single, non-duplicated `api_available` signal, so a compiler cannot earn the same partial credit by
disabling search that it would earn from a genuine, search-confirmed absence of contradictions — and
that signal now also folds in relation-classification health, so a compiler cannot quietly let relation
typing collapse to "everything is background" and still be scored as a clean run. Fabricated
relationships are checked against DOI/title identity and candidate abstracts. Missing fields never
disappear from the denominator, so a compiler cannot improve the score by omitting `related_work.md` or
`trace/exploration_tree.yaml`. And because `api_available` now scores in exactly one place instead of
three, there is no longer a strategic surface where a compiler could bet on one of the three redundant
terms mattering more than the others to the eventual scoring pipeline.
