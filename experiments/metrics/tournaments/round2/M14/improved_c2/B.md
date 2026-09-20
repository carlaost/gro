# M14 Expansion: Reference-landscape completeness (cycle 2, revision B)

## Changes (cycle 2)

This revision is a direct, targeted fix of the four weaknesses the round-2 critique named against `exp1` (Rank 2), keeping the two things the critique explicitly called out as best-in-field: the single dominant `external_coverage` term and the asymmetric high-relevance `miss_penalty`.

1. **`trace_landscape` now touches the external landscape.** Previously it only scored internal prose specificity of decision/dead_end/pivot nodes — a *reference-landscape* metric's trace term must verify that abandoned paths correspond to externally-surfaced inferior/contradicted/overturned approaches, not just that the ARA wrote confident-sounding prose about its own dead ends. Added `trace_external_grounding`: token/entity overlap between trace node text and the external candidate set's titles/abstracts/relations, split into a grounded-dead-end credit and an ungrounded-claim penalty.
2. **`contra_recall` no longer collapses to 0 when the contradiction gold set `K` is empty.** The brief explicitly warns against expecting refutations from every genre. Added a genre-sensitive default: if search succeeded and found zero qualifying contradictions, the ARA gets partial credit for genre-appropriate silence rather than being scored as if it missed real contradictions. The default degrades toward 0 only when the external API failed, not when it succeeded and found nothing.
3. **Close-neighbor recall denominator is capped and importance-ranked (top-25) instead of the full LLM-selected set (cap 80).** Recalling against up to 80 papers implicitly expects an ARA to cite an unrealistic number of works and understates focused-but-complete ARAs. The separate `miss_penalty` for uncited very-high-relevance papers is kept and strengthened — misses are now weighted by relation type (missing a `refutes`/`baseline` neighbor costs more than missing `background`), preserving the metric's best Goodhart-resistance feature while fixing the denominator-inflation problem.
4. **Added a conceptual-coverage tier** (analogous to exp2's idea, but hardened per the exp2 critique so it does not inherit exp2's hole): an ARA that correctly *describes* an external finding without a formal citation now earns partial credit, gated on a **specific matching artifact** (a number, named method, dataset, or cohort that also appears in the external paper's abstract/tldr) — not topic overlap — and capped so conceptual coverage cannot exceed 35% of total covered weight (a real footprint should still be mostly direct, checkable citations).

Everything else (availability-first scoring, penalize-don't-skip, the citation-stuffing/search-overfitting/hiding-contradictions/fabricated-specificity/genre-mismatch countermeasures) is retained from the round-1 proposal and re-verified against `04_problem.md` and the brief below.

## Expanded reasoning

Reference-landscape completeness measures whether the ARA's problem framing is anchored in the actual surrounding literature, not just in whatever citations happened to appear in the source paper's abstract or introduction. Good science should locate its question where prior work actually left uncertainty: it should identify the closest technical neighbors, the main supporting traditions, direct baselines, reused datasets or methods, and relevant contradictory or limiting results. This metric is net-new because it verifies that landscape externally through Semantic Scholar / Undermind-style search, instead of trusting the ARA's internal citations alone — per the brief, this is "the single biggest hole" neither round-1 nor the ARA verifier reaches, and it ranked top-10 specifically for being net-new and tightly scoped. This revision protects that scoping by keeping one dominant external-coverage term rather than diluting it across many components (the failure mode that sank the `exp4`/`exp3` critiques).

The primary signal is the alignment among three layers, matching `04_problem.md` and the brief's cross-references:

- `logic/problem.md` (§4 shape): Observation blocks (`Statement`/`Evidence`/`Implication`), Gap blocks (`Statement`/`Caused by`/`Existing attempts`/`Why they fail`), Key Insight, Assumptions — should cite a specific, non-generic pre-existing landscape, not `Evidence: Abstract` restatements (§4's own documented degradation signal).
- `logic/related_work.md` (§6 shape): the typed dependency graph should preserve both high-delta citations and a brief full citation footprint.
- `trace/exploration_tree.yaml` (§8 shape): decisions, dead ends, pivots, and the starting question should reflect real prior alternatives and known failures **when the external search actually surfaces them** — not merely read as internally specific.

The metric rewards ARAs that name close prior work, explain how each close work imports, bounds, extends, baselines, or refutes the target paper, and connect those references to concrete gaps and decisions. It especially rewards explicit contradiction handling: prior findings with opposite conclusions, failed approaches, negative baselines, known limitations, or subgroup-specific exceptions — scored against what the external search genuinely turns up for that genre, never against a fixed per-paper refutation quota. It does not reward citation volume by itself, and it now also credits genuine landscape awareness expressed without a formal citation, provided that awareness is anchored to a checkable artifact rather than vague topic overlap.

Missing or thin inputs are never skipped. Availability is part of the score. If `related_work.md` is missing, unparseable, or lacks a brief footprint tier, the score falls. If `problem.md` uses only `Evidence: Abstract`, generic "prior work is limited" language, or a key insight that simply restates the method name, the score falls. If `trace/exploration_tree.yaml` is missing or has no useful decisions/dead ends where external literature clearly shows abandoned or inferior paths, the score falls — but a genre where the external search finds no comparably strong alternative paths is not punished as if a file were missing. External API failure is penalized as verifier unavailability, more harshly than a genuine, search-confirmed absence of contradictions or alternative paths, and this asymmetry is now made explicit in both the contradiction and trace terms (fix #2 and #1 above), not just in the top-level availability term.

### Failure modes and gaming routes

- **Citation stuffing**: adding many background references without typed deltas. Countered by weighting close-neighbor recall (against a capped, importance-ranked gold set, fix #3) and typed role quality above raw count.
- **Search-term overfitting**: mentioning trendy keywords to retrieve a broad island. Countered by deriving queries from the problem observations/gaps/key insight and checking semantic overlap at paper-title/abstract level.
- **Hiding contradictions**: citing only supportive work. Countered by an explicit contradiction/bounds search and a missed-neighbor penalty, with genre-sensitive scoring so absence-of-contradiction genres aren't falsely flagged (fix #2) and so hiding a real contradiction is distinguishable from a genre that has none.
- **Fabricated specificity**: giving detailed RW blocks for references that are not close or not used. Countered by DOI/title normalization and Semantic Scholar match checks.
- **Genre mismatch**: expecting dead ends or refutations from papers that do not report them. Countered by scoring trace coverage and contradiction recall as genre-sensitive modifiers gated on `api_available`, while still penalizing missing files and unsupported explicit nodes.
- **Conceptual-coverage gaming (new, hardened against the exp2 failure mode)**: vaguely name-dropping a concept to claim "I covered that" without a real citation. Countered by requiring a specific matching artifact (number/named method/dataset/cohort also present in the external paper's abstract/tldr) before any conceptual-coverage credit is granted, and by capping conceptual coverage at 35% of total covered weight so it can only ever be a supplement to direct citations, never a substitute.
- **Trace-grounding gaming (new)**: writing confident, specific-sounding prose about a "dead end" that has no correspondent in the external candidate set. Countered by requiring token/entity overlap with an externally retrieved paper before a dead_end/pivot node earns landscape-grounding credit; ungrounded but internally "explicit" nodes are penalized, not merely un-rewarded.

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
   - **(new)** a separate list of "checkable artifacts" per O/G/Insight block: numbers, named methods, dataset names, cohort names — used only for conceptual-coverage matching (fix #4), never for recall itself.

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

Deterministic use: discard candidates with `relevance < 0.55` unless they are in the target paper's own reference list; define close-neighbor set `L` as candidates with `is_close_neighbor=true` or `relevance >= 0.72`. **(fix #3)** Rank `L` by `importance = 0.6*relevance + 0.4*relation_weight` (`relation_weight`: `refutes`=1.0, `baseline`=0.9, `imports`=0.8, `bounds`=0.7, `extends`=0.6, `background`=0.3) and cap the *recall gold set* `L_top` at the top 25 by `importance`; retain the full capped-80 `L` separately only as the pool from which `miss_penalty` draws (so an ARA cannot dodge the miss penalty just because a very-high-relevance paper falls outside the top-25 recall denominator). Define contradiction set `K` as candidates with `is_contradictory_or_limiting=true` and `relevance >= 0.60`, capped at 40.

### Conceptual-coverage matching (new, fix #4)

For each candidate in `L` not matched by DOI/title to any ARA citation:
1. Extract the candidate's key checkable artifacts from its abstract/tldr (numbers, named methods, dataset/cohort names) via the same extraction used for the ARA's own blocks.
2. Check whether any ARA `problem.md` O/G/Insight block's checkable-artifact list intersects the candidate's checkable-artifact list (exact or near-exact string/number match, not topic embedding similarity).
3. If yes, mark the candidate `conceptually_covered=True` with `coverage_weight = 0.5 * importance` (half credit relative to a full formal citation, since it lacks a checkable typed delta).
4. `conceptual_covered_weight = sum(coverage_weight for conceptually_covered candidates)`; `direct_covered_weight` from DOI/title-matched candidates in `L_top ∪ K` at full `importance`. Cap: `conceptual_covered_weight ≤ 0.35 * (direct_covered_weight + conceptual_covered_weight)`; excess conceptual weight is discarded before scoring, not redistributed.

### Trace external grounding (new, fix #1)

For each `decision`/`dead_end`/`pivot` node in the parsed trace:
1. Build `node_text` from `title`/`hypothesis`/`failure_mode`/`lesson`/`choice`/`alternatives`/`trigger`.
2. Compute token/entity overlap (Jaccard over normalized noun-phrase/entity sets) between `node_text` and each candidate in `L ∪ K`'s title+abstract/tldr.
3. A node is `externally_grounded=True` if its best overlap ≥ 0.20 Jaccard against a candidate with `relation` in `{baseline, bounds, refutes}` (i.e., the abandoned path/pivot corresponds to a real externally-inferior or contradicted approach), or the node carries a `source_refs` entry that DOI/title-matches a candidate in `L ∪ K`.
4. A node is `ungrounded_explicit` if `support_level == "explicit"` and it is a `decision`/`dead_end`/`pivot` type but not `externally_grounded` and has no `source_refs` at all — this is the same "explicit-without-refs" penalty class as before, now specifically checked against the external set rather than assumed absent.

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

def score_m14(parsed, external):
    """
    parsed keys:
      problem_available, related_available, trace_available, metadata_available: bool
      observations, gaps: list[dict]
      key_insight: dict
      related_full, related_brief: list[dict]
      trace_nodes: list[dict]
      artifacts_by_block: dict[block_id -> set[str]]   # checkable artifacts, new
    external keys:
      close_neighbors: list[dict]        # L, each w/ relevance, relation, title, abstract_or_tldr
      contradiction_neighbors: list[dict]  # K
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
    close = external.get("close_neighbors", [])
    contra = external.get("contradiction_neighbors", [])
    api_ok = bool(external.get("api_available"))

    # fix #3: capped, importance-ranked recall gold set (top-25), separate from the full miss-penalty pool
    close_ranked = sorted(close, key=importance, reverse=True)
    close_top = close_ranked[:25]
    close_top_keys = {citation_key(r) for r in close_top if citation_key(r)}
    close_recall = len(ara_keys & close_top_keys) / max(1, len(close_top_keys)) if close_top_keys else (0.7 if api_ok else 0.0)

    contra_keys = {citation_key(r) for r in contra if citation_key(r)}
    if contra_keys:
        contra_recall = len(ara_keys & contra_keys) / len(contra_keys)
    else:
        # fix #2: genre-sensitive default. Search ran and found nothing contradictory -> partial credit
        # for genre-appropriate silence, not a penalty. Only degrade toward 0 if search itself failed.
        contra_recall = 0.75 if api_ok else 0.0

    # weighted, asymmetric miss penalty (kept + strengthened): misses weighted by relation importance
    high_rel_misses = [r for r in close if citation_key(r) not in ara_keys and r.get("relevance", 0) >= 0.85]
    weighted_miss = sum(importance(r) for r in high_rel_misses)
    miss_penalty = clamp(weighted_miss / 6.0)

    # fix #4: conceptual coverage, gated on a specific matching artifact, capped at 35% of covered weight
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
    conceptual_bonus = soft_count(conceptual_weight_capped * 10, 8) * 0.5  # bounded supplement, not primary

    external_coverage = (
        0.50 * close_recall +
        0.25 * contra_recall +
        0.10 * soft_count(len(ara_keys & close_top_keys), 15) +
        0.10 * api_ok +
        0.05 * conceptual_bonus
        - 0.28 * miss_penalty
    )
    external_coverage = clamp(external_coverage)

    nodes = parsed.get("trace_nodes", [])
    decisionish = [n for n in nodes if n.get("type") in {"decision", "dead_end", "pivot"}]
    trace_text = " ".join(
        " ".join(str(n.get(k, "")) for k in ["title", "hypothesis", "failure_mode", "lesson", "choice", "alternatives", "trigger"])
        for n in decisionish
    )

    # fix #1: trace term now checks external grounding, not just internal prose specificity
    ext_pool = close + contra
    grounded = []
    ungrounded_explicit = []
    for n in decisionish:
        node_text = " ".join(str(n.get(k, "")) for k in ["title", "hypothesis", "failure_mode", "lesson", "choice", "alternatives", "trigger"])
        has_ref_match = bool(n.get("source_refs")) and any(citation_key({"title_or_label": ref}) in ara_keys for ref in n.get("source_refs", []))
        best_overlap = max((jaccard_tokens(node_text, (r.get("title", "") + " " + r.get("abstract_or_tldr", ""))) for r in ext_pool), default=0.0)
        best_rec = max(ext_pool, key=lambda r: jaccard_tokens(node_text, r.get("title", "") + " " + r.get("abstract_or_tldr", "")), default=None)
        strong_relation_hit = best_overlap >= 0.20 and best_rec is not None and best_rec.get("relation") in {"baseline", "bounds", "refutes"}
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

    thin_penalty = 0.0
    if parsed.get("related_available") and len(full) <= 2 and len(brief) == 0:
        thin_penalty += 0.12
    if parsed.get("problem_available") and obs and all(ABSTRACT_ONLY.search(o.get("Evidence", "")) for o in obs):
        thin_penalty += 0.10
    if not api_ok:
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
            "close_recall_top25": round(close_recall, 4),
            "contradiction_recall": round(contra_recall, 4),
            "weighted_missed_high_relevance": round(weighted_miss, 4),
            "conceptual_covered_weight_capped": round(conceptual_weight_capped, 4),
            "trace_grounded_nodes": len(grounded),
            "trace_ungrounded_explicit_nodes": len(ungrounded_explicit),
        }
    }
```

### Interpretation

- `0.85-1.00`: strong landscape coverage; the ARA names most close external neighbors (by importance-ranked recall), captures typed deltas, includes contradicting/bounding work where discoverable, and its trace's abandoned paths are externally corroborated.
- `0.60-0.85`: usable but incomplete; usually misses some top-25 close neighbors, has weak brief-footprint coverage, or its trace claims dead ends the external search cannot corroborate.
- `0.35-0.60`: thin; internal citations exist but external search exposes important omissions, generic gap framing, or ungrounded explicit trace nodes.
- `<0.35`: abstract-only or structurally unavailable landscape; should not be used as evidence of novelty without recompilation.

## Why this is hard to Goodhart

The score depends on independent external retrieval, relation classification, and a weighted, asymmetric high-relevance missed-neighbor penalty that now also accounts for relation type (refuting/baseline misses cost more than background misses). Adding references helps only if they match a capped, importance-ranked close-neighbor set and carry specific typed deltas — inflating the citation list beyond the top-25 importance-ranked gold set buys nothing. Vague or stuffed citations raise counts but not recall, contradiction coverage, or specificity. The new conceptual-coverage tier cannot be gamed by vague name-dropping because it requires a concrete matching artifact shared with the external paper's own abstract/tldr, and it is capped at 35% of covered weight so it can only supplement, never replace, direct typed citations. The new trace-grounding check means an ARA cannot claim confident, specific-sounding dead ends for credit unless they correspond to something the external search actually surfaced as a real baseline/bound/refutation — internal narrative polish alone no longer buys trace score. Genre-sensitive defaults for contradiction recall and trace grounding are explicitly conditioned on `api_available`, so a compiler cannot earn the same partial credit by disabling search that it would earn from a genuine, search-confirmed absence of contradictions. Fabricated relationships are checked against DOI/title identity and candidate abstracts. Missing fields never disappear from the denominator, so a compiler cannot improve the score by omitting `related_work.md` or `trace/exploration_tree.yaml`.
