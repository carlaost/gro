# M14 Expansion: Reference-landscape completeness

## Expanded reasoning

Reference-landscape completeness measures whether the ARA's problem framing is anchored in the actual surrounding literature, not just in whatever citations happened to appear in the source paper's abstract or introduction. Good science should locate its question where prior work actually left uncertainty: it should identify the closest technical neighbors, the main supporting traditions, direct baselines, reused datasets or methods, and relevant contradictory or limiting results. This metric is net-new because it verifies that landscape externally through Semantic Scholar / Undermind-style search, instead of trusting the ARA's internal citations alone.

The primary signal is the alignment among three layers:

- `logic/problem.md`: observations, gaps, key insight, and assumptions should cite a specific, non-generic pre-existing landscape.
- `logic/related_work.md`: the typed dependency graph should preserve both high-delta citations and a brief full citation footprint.
- `trace/exploration_tree.yaml`: decisions, dead ends, pivots, and the starting question should reflect real prior alternatives and known failures when the field exposes them.

The metric should reward ARAs that name close prior work, explain how each close work imports, bounds, extends, baselines, or refutes the target paper, and connect those references to concrete gaps and decisions. It should especially reward explicit contradiction handling: prior findings with opposite conclusions, failed approaches, negative baselines, known limitations, or subgroup-specific exceptions. It should not reward citation volume by itself. A long reference list with vague one-line roles, no deltas, no claim/gap connections, or no externally discoverable close neighbors is weak. Likewise, it must not punish a paper merely because it has few explicit `refutes` edges; contradiction coverage is scored against the external landscape and the source genre, not against a fixed expectation that every paper refutes something.

Missing or thin inputs are never skipped. Availability is part of the score. If `related_work.md` is missing, unparseable, or lacks a brief footprint tier, the score falls. If `problem.md` uses only `Evidence: Abstract`, generic "prior work is limited" language, or a key insight that simply restates the method name, the score falls. If `trace/exploration_tree.yaml` is missing or has no useful decisions/dead ends where external literature clearly shows abandoned or inferior paths, the score falls. External API failure is also penalized mildly as verifier unavailability, but not as harshly as an ARA that fails to expose citations.

Failure modes and gaming routes:

- Citation stuffing: adding many background references without typed deltas. Countered by weighting close-neighbor recall and typed role quality above raw count.
- Search-term overfitting: mentioning trendy keywords to retrieve a broad island. Countered by deriving queries from the problem observations/gaps/key insight and checking semantic overlap at paper-title/abstract level.
- Hiding contradictions: citing only supportive work. Countered by an explicit contradiction/bounds search and a missed-neighbor penalty.
- Fabricated specificity: giving detailed RW blocks for references that are not close or not used. Countered by DOI/title normalization and Semantic Scholar match checks.
- Genre mismatch: expecting dead ends from papers that do not report them. Countered by scoring trace coverage as a genre-sensitive modifier, while still penalizing missing files and unsupported explicit nodes.

This composes well with internal verifier metrics because it tests a different boundary: not whether the ARA is internally grounded, but whether its grounding covers the externally visible scientific neighborhood. It should be run after structural parsing metrics and before novelty/gap metrics; its output can supply a calibrated "landscape coverage" prior for those later metrics.

## Concrete generation/compute workflow

### Inputs

Required artifact texts, assumed requested from one compiled ARA root:

- `logic/problem.md` using the §4 shape: Observation blocks, Gap blocks, Key Insight, Assumptions.
- `logic/related_work.md` using the §6 shape: `RW##` full blocks plus any brief citation footprint section.
- `trace/exploration_tree.yaml` using the §8 shape: YAML `tree:` nodes.
- Optional metadata supplied by the runner if available: target paper title, DOI/arXiv ID, abstract, authors, year, venue. If unavailable, derive search queries from `problem.md` and penalize metadata absence in the search-confidence term.

Assumption if the runner exposes only the primary artifact: score the cross-layer terms as missing/thin rather than N/A. The metric brief names §6 and §8, so a production runner should pass them.

### Parse and normalize

1. Parse `problem.md` by markdown headings:
   - observations: `### O\d+`, fields `Statement`, `Evidence`, `Implication`
   - gaps: `### G\d+`, fields `Statement`, `Caused by`, `Existing attempts`, `Why they fail`
   - key insight fields `Insight`, `Derived from`, `Enables`
   - assumptions: `A\d+:`
2. Parse `related_work.md`:
   - full blocks: `## RW\d+`, `DOI`, `Type`, `Delta / What changed`, `Delta / Why`, `Claims affected`, `Adopted elements`
   - brief citations: bullets under headings containing `Background`, `supporting`, `Additional citation footprint`, or `brief`
3. Parse `exploration_tree.yaml` with a YAML parser. Flatten all nodes recursively through `children`; retain `also_depends_on`.
4. Normalize citations into records:
   - `doi_norm`: lowercase DOI if present and not "Not specified"
   - `title_or_label`: heading text or bold author-year label
   - `role_text`: concatenated type, delta, adopted elements, brief role
   - `source_layer`: `problem_evidence`, `related_full`, `related_brief`, `trace_source_ref`
5. Extract ARA query terms from:
   - top 8 noun phrases from observation/gap/key-insight statements
   - explicit study objects, methods, biomarkers, datasets, baselines, populations, outcomes
   - target title/abstract when available

### External calls

All external calls return structured JSON and are cached by target DOI/title plus query string.

1. Semantic Scholar target lookup:
   - Query: target DOI if available, else target title.
   - Fields: `paperId,title,abstract,year,authors,externalIds,references,citations,embedding,tldr,fieldsOfStudy`
   - Output: target paper identity and its reference list where available.
2. Semantic Scholar k-nearest / island search:
   - Query 1: target title + abstract, embedding nearest papers if API supports vector/recommendations.
   - Query 2: `"key insight terms" AND "gap terms"` from parsed problem fields.
   - Query 3: each major `G#` statement plus domain/population/outcome terms.
   - Keep up to 500 candidate papers after dedupe by DOI/paperId/title.
3. Contradiction/bounds search:
   - For each top gap and key insight, query:
     - `(<domain terms>) (<method/object terms>) contradict OR inconsistent OR failed OR limitation OR negative OR no improvement OR baseline`
     - `(<main method/object>) versus <baseline terms>`
   - Keep up to 100 candidate papers, merged into the same candidate set with a flag `contradiction_query=True`.
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
   - Use returned relevance only after DOI/title dedupe; do not accept prose claims without bibliographic identity.

### LLM semantic classification

Use an LLM only to classify relevance and relation type where metadata/abstract text is available. The LLM output is converted into deterministic scores.

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

Deterministic use: discard candidates with `relevance < 0.55` unless they are in the target paper's own reference list; define close-neighbor set `L` as candidates with `is_close_neighbor=true` or `relevance >= 0.72`, capped at 80 highest relevance. Define contradiction set `K` as candidates with `is_contradictory_or_limiting=true` and `relevance >= 0.60`, capped at 40.

### Scoring function

Python reference implementation against parsed records:

```python
import math
import re
from collections import Counter

GENERIC_FAIL = re.compile(r"\b(prior work|previous studies|limited|unclear|not well understood|further research)\b", re.I)
ABSTRACT_ONLY = re.compile(r"^\s*(abstract|title|not specified)\s*$", re.I)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def soft_count(n, target):
    return clamp(math.log1p(max(n, 0)) / math.log1p(target))

def jaccard(a, b):
    return len(a & b) / max(1, len(a | b))

def norm_id(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def citation_key(rec):
    return (rec.get("doi_norm") or norm_id(rec.get("title_or_label", "")))[:120]

def block_specificity(text):
    if not text:
        return 0.0
    tokens = re.findall(r"[A-Za-z0-9_.-]+", text)
    has_number = bool(re.search(r"\b\d+(?:\.\d+)?\b", text))
    has_named_entityish = sum(1 for t in tokens if len(t) > 3 and (t[0].isupper() or any(c.isdigit() for c in t)))
    generic_penalty = 0.35 if GENERIC_FAIL.search(text) and len(tokens) < 35 else 0.0
    return clamp(0.35 * soft_count(len(tokens), 45) + 0.35 * soft_count(has_named_entityish, 6) + 0.15 * has_number + 0.15 - generic_penalty)

def score_m14(parsed, external):
    """
    parsed keys:
      problem_available: bool
      related_available: bool
      trace_available: bool
      observations, gaps: list[dict]
      key_insight: dict
      related_full, related_brief: list[dict]
      trace_nodes: list[dict]
      metadata_available: bool
    external keys:
      close_neighbors: list[dict]  # DOI/title/relevance/relation/is_in_source_refs if known
      contradiction_neighbors: list[dict]
      api_available: bool
    """
    availability = (
        0.30 * bool(parsed.get("problem_available")) +
        0.35 * bool(parsed.get("related_available")) +
        0.20 * bool(parsed.get("trace_available")) +
        0.15 * bool(parsed.get("metadata_available"))
    )

    obs = parsed.get("observations", [])
    gaps = parsed.get("gaps", [])
    insight = parsed.get("key_insight") or {}
    evidence_depth = []
    for o in obs:
        ev = o.get("Evidence", "")
        evidence_depth.append(0.0 if ABSTRACT_ONLY.search(ev) else block_specificity(ev))
    gap_depth = [
        0.5 * block_specificity(g.get("Existing attempts", "")) +
        0.5 * block_specificity(g.get("Why they fail", ""))
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
    close = external.get("close_neighbors", [])
    contra = external.get("contradiction_neighbors", [])
    close_keys = {citation_key(r) for r in close if citation_key(r)}
    contra_keys = {citation_key(r) for r in contra if citation_key(r)}
    close_recall = len(ara_keys & close_keys) / max(1, len(close_keys))
    contra_recall = len(ara_keys & contra_keys) / max(1, len(contra_keys))
    high_rel_misses = [r for r in close if citation_key(r) not in ara_keys and r.get("relevance", 0) >= 0.85]
    miss_penalty = clamp(len(high_rel_misses) / 10)
    external_coverage = (
        0.55 * close_recall +
        0.25 * contra_recall +
        0.10 * soft_count(len(ara_keys & close_keys), 25) +
        0.10 * bool(external.get("api_available"))
        - 0.25 * miss_penalty
    )
    external_coverage = clamp(external_coverage)

    nodes = parsed.get("trace_nodes", [])
    decisionish = [n for n in nodes if n.get("type") in {"decision", "dead_end", "pivot"}]
    explicit_without_refs = [
        n for n in nodes
        if n.get("support_level") == "explicit" and not n.get("source_refs")
        and n.get("type") in {"experiment", "decision", "dead_end"}
    ]
    trace_text = " ".join(
        " ".join(str(n.get(k, "")) for k in ["title", "hypothesis", "failure_mode", "lesson", "choice", "alternatives", "trigger"])
        for n in decisionish
    )
    trace_landscape = (
        0.25 * soft_count(len(nodes), 8) +
        0.30 * soft_count(len(decisionish), 4) +
        0.25 * block_specificity(trace_text) +
        0.20 * (1.0 - clamp(len(explicit_without_refs) / 3))
    ) if parsed.get("trace_available") else 0.0

    # Penalize-don't-skip: absent/thin layers remain zero in their components and availability is explicit.
    raw = (
        0.15 * availability +
        0.20 * problem_depth +
        0.25 * related_depth +
        0.30 * external_coverage +
        0.10 * trace_landscape
    )

    thin_penalty = 0.0
    if parsed.get("related_available") and len(full) <= 2 and len(brief) == 0:
        thin_penalty += 0.12
    if parsed.get("problem_available") and obs and all(ABSTRACT_ONLY.search(o.get("Evidence", "")) for o in obs):
        thin_penalty += 0.10
    if not external.get("api_available"):
        thin_penalty += 0.05

    return {
        "score": round(clamp(raw - thin_penalty), 4),
        "components": {
            "availability": round(availability, 4),
            "problem_depth": round(problem_depth, 4),
            "related_depth": round(related_depth, 4),
            "external_coverage": round(external_coverage, 4),
            "trace_landscape": round(trace_landscape, 4),
            "thin_penalty": round(thin_penalty, 4),
            "close_recall": round(close_recall, 4),
            "contradiction_recall": round(contra_recall, 4),
            "missed_high_relevance_neighbors": len(high_rel_misses),
        }
    }
```

### Interpretation

- `0.85-1.00`: strong landscape coverage; the ARA names most close external neighbors, captures typed deltas, and includes contradicting/bounding work where discoverable.
- `0.60-0.85`: usable but incomplete; usually misses some close neighbors, has weak brief-footprint coverage, or underexplains failures/bounds.
- `0.35-0.60`: thin; internal citations exist but external search exposes important omissions or generic gap framing.
- `<0.35`: abstract-only or structurally unavailable landscape; should not be used as evidence of novelty without recompilation.

## Why this is hard to Goodhart

The score depends on independent external retrieval, relation classification, and high-relevance missed-neighbor penalties. Adding references helps only if they match close external neighbors and carry specific typed deltas. Vague or stuffed citations raise counts but not recall, contradiction coverage, or specificity. Fabricated relationships are checked against DOI/title identity and candidate abstracts. Missing fields never disappear from the denominator, so a compiler cannot improve the score by omitting `related_work.md` or `trace/exploration_tree.yaml`.

