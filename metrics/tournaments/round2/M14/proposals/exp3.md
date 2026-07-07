# M14: Reference-landscape completeness

## Metric expansion

Reference-landscape completeness measures whether the ARA's problem layer and related-work layer locate the paper in the real surrounding literature rather than only reciting the paper's own favored citations. A strong ARA should show what was empirically known before the work, what remained unresolved, which prior attempts failed or were bounded, and which external papers a competent literature-search agent would surface as relevant. This is net-new because the ordinary artifact validator can check internal structure and trace hygiene, but it does not independently ask whether the literature landscape itself is complete.

The metric primarily scores `logic/problem.md`, with cross-checks against `logic/related_work.md` and `trace/exploration_tree.yaml`. It rewards:

- Observations in `logic/problem.md` whose `Evidence` fields contain specific Introduction/prior-work citation chains or section references, not just `Abstract`.
- Gaps that name existing attempts and explain their specific failure modes.
- A related-work graph that includes full `RW##` blocks for technically important citations and a brief tier for the wider citation footprint.
- Explicit coverage of contradicting, bounding, baseline, refuting, or failed-prior-work references where the paper or external search landscape indicates they exist.
- Agreement between the ARA's stated problem/gaps and an external literature search neighborhood for the paper topic.
- Exploration-tree nodes whose questions, decisions, experiments, dead ends, and pivots reflect the same literature terrain, especially rejected or failed paths that future agents should not rediscover.

The metric must not reward raw citation count alone. A long list of generic background references with no typed deltas is weaker than a smaller but well-typed landscape that captures the key baselines, imports, bounds, and contradictions. It must also not require `refutes` edges or `dead_end` nodes when the source and search landscape do not support them; absence is penalized only when contradiction/failure/baseline evidence is discoverable and the ARA omits it. Missing or thin artifacts are never skipped: they receive explicit low availability and coverage scores.

Assumption: the compute workflow receives either a paper identifier/title/abstract alongside the ARA artifact directory, or enough metadata to query external literature services. If metadata is missing, the external-landscape subscore is penalized rather than marked not applicable.

## Failure modes and gaming routes

Common failures:

- `problem.md` Observations are abstract-only restatements with `Evidence: Abstract`.
- Gaps say prior work is "limited" without naming attempts or why they fail.
- `related_work.md` has only a few `RW##` blocks and no brief citation-footprint tier.
- The ARA cites only papers already highlighted by the source authors and misses nearby high-relevance works surfaced by Semantic Scholar or Undermind.
- Contradicting, bounding, or baseline papers appear in search results but are absent from both `problem.md` and `related_work.md`.
- The exploration tree starts from the paper's method rather than from where the literature left off.
- The tree has no literature-grounded decisions or dead ends even though the paper/search landscape contains explicit rejected alternatives, failed baselines, or overturned prior claims.

Gaming routes and defenses:

- Padding citations is limited by scoring typed deltas, DOI/arXiv identifiers, and overlap with independently retrieved search results.
- Over-labeling many papers as `refutes` is limited by requiring contradiction evidence from the ARA text or external abstracts/snippets.
- Copying a search-result bibliography without integrating it is limited by separate problem-gap and related-work-typing scores.
- Hiding missing data behind "not available" is prevented by the hard rule that missing/thin inputs score down.

## Generation / compute workflow

### Inputs

Required artifact paths, relative to one ARA root:

- `logic/problem.md`
- `logic/related_work.md`
- `trace/exploration_tree.yaml`

Required metadata fields:

- `paper_title`: string
- `paper_abstract`: string, may be empty but penalized
- `paper_doi`: string, may be empty
- `paper_year`: integer or string, may be empty

Optional metadata fields:

- `source_references`: list of references from the source paper, if available
- `source_keywords`: list of topic terms

No input is skipped. Empty or missing files/metadata are represented as empty strings/lists and receive availability penalties.

### External calls

1. Semantic Scholar paper lookup:

```text
Query: paper_title OR paper_doi
Return: canonical paper id, title, abstract, year, authors, fieldsOfStudy, references, citations, influentialCitationCount
```

If `paper_doi` is absent, query by exact title. If no canonical paper is found, set `canonical_found = False` and score the external lookup components as zero except for any search results obtainable from the title query.

2. Semantic Scholar landscape query:

```text
Query: top 500 papers using the canonical paper title, abstract keywords, and source title terms.
Filter preference: same broad field, papers published no later than the source paper year for prior-landscape coverage; include later survey/replication papers only in a separate diagnostic list and do not require the ARA to cite them.
Return: paperId, title, year, authors, venue, abstract, citationCount, influentialCitationCount, embedding or relevance score, DOI/arXiv where available.
```

3. k-nearest-neighbor / island construction:

Use Semantic Scholar embeddings if exposed. Otherwise compute sentence-transformer embeddings over `title + abstract` for returned papers and the source paper. Keep the top 500 nearest papers, then cluster with HDBSCAN or agglomerative clustering. Label each paper with one or more roles using deterministic rules plus an LLM classifier when abstracts are available.

LLM classifier prompt for each candidate paper:

```text
You are classifying whether a candidate paper belongs in the prior literature landscape for a scientific paper.

SOURCE TITLE:
{paper_title}

SOURCE ABSTRACT:
{paper_abstract}

CANDIDATE TITLE:
{candidate_title}

CANDIDATE ABSTRACT:
{candidate_abstract}

Return strict JSON:
{
  "relevance": 0|1|2|3,
  "role": ["imports"|"bounds"|"baseline"|"extends"|"refutes"|"background"],
  "contradiction_or_failure": true|false,
  "reason": "one sentence"
}

Use relevance 3 only for papers that a careful related-work section should almost certainly discuss.
Use contradiction_or_failure true only when the candidate reports a conflicting result, failed approach, rejected baseline, or boundary condition directly relevant to the source.
```

Parse only valid JSON. Invalid or missing LLM output gives that candidate `relevance = 0`; it is not silently removed.

4. Undermind-style search:

```text
Query: "Find the most relevant prior and contradicting literature for: {paper_title}. Focus on papers before {paper_year}, baselines, failed or conflicting results, datasets/methods imported, and works that bound the claims."
Return: ranked papers with short rationales.
```

Normalize all external results by DOI/arXiv first, then title-fuzzy match with normalized lowercase titles and author-year fallback.

### Deterministic parsing

Parse `logic/problem.md` into:

- observations: headings `### O{N}` plus `Statement`, `Evidence`, `Implication`
- gaps: headings `### G{N}` plus `Statement`, `Caused by`, `Existing attempts`, `Why they fail`
- key insight: `Insight`, `Derived from`, `Enables`
- assumptions: `A{N}:`

Parse `logic/related_work.md` into:

- full RW blocks: `## RW{NN}` with `DOI`, `Type`, `Delta/What changed`, `Delta/Why`, `Claims affected`, `Adopted elements`
- brief-tier references: bullets under any non-`RW##` citation-footprint/background/supporting-reference section

Parse `trace/exploration_tree.yaml` into all nodes under `tree`, preserving `type`, `support_level`, `source_refs`, and type-specific fields.

### Scoring function

Final score is a 0-100 integer:

- 15 points: artifact and metadata availability
- 20 points: problem-layer prior-landscape depth
- 25 points: related-work graph completeness and typing
- 25 points: external search recall and contradiction coverage
- 10 points: exploration-tree alignment with the literature landscape
- 5 points: anti-padding precision

Missing or unparsable inputs receive zero for the affected components. They are not excluded from denominators.

```python
import json
import math
import re
from collections import Counter
from difflib import SequenceMatcher

def norm_title(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower()).strip()

def fuzzy_same(a, b):
    a, b = norm_title(a), norm_title(b)
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() >= 0.90

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def availability_score(problem_text, related_text, tree_obj, metadata):
    score = 0.0
    score += 0.25 if problem_text.strip() else 0.0
    score += 0.25 if related_text.strip() else 0.0
    score += 0.20 if isinstance(tree_obj, dict) and isinstance(tree_obj.get("tree"), list) else 0.0
    score += 0.15 if metadata.get("paper_title") else 0.0
    score += 0.10 if metadata.get("paper_abstract") else 0.0
    score += 0.05 if metadata.get("paper_doi") or metadata.get("source_references") else 0.0
    return 15.0 * score

def problem_depth_score(parsed_problem):
    obs = parsed_problem.get("observations", [])
    gaps = parsed_problem.get("gaps", [])
    if not obs and not gaps:
        return 0.0
    obs_specific = 0
    obs_citation_rich = 0
    for o in obs:
        evidence = o.get("evidence", "")
        if evidence and evidence.lower().strip() != "abstract":
            obs_specific += 1
        if len(re.findall(r"\b[A-Z][A-Za-z-]+ et al\.,? \d{4}[a-z]?\b|\b10\.\d{4,9}/", evidence)) >= 2:
            obs_citation_rich += 1
    gap_specific = 0
    for g in gaps:
        attempts = g.get("existing_attempts", "")
        fail = g.get("why_they_fail", "")
        if len(attempts.split()) >= 5 and len(fail.split()) >= 8 and "limited" not in fail.lower():
            gap_specific += 1
    insight = parsed_problem.get("key_insight", {})
    derived = insight.get("derived_from", "")
    insight_chain = 1.0 if re.search(r"\bO\d+\b", derived) and (re.search(r"\bG\d+\b", derived) or len(derived.split(",")) >= 2) else 0.0
    obs_part = 0.45 * (obs_specific / max(1, len(obs)))
    citation_part = 0.20 * (obs_citation_rich / max(1, len(obs)))
    gap_part = 0.25 * (gap_specific / max(1, len(gaps)))
    insight_part = 0.10 * insight_chain
    return 20.0 * clamp(obs_part + citation_part + gap_part + insight_part)

def related_work_score(parsed_rw):
    full = parsed_rw.get("rw_blocks", [])
    brief = parsed_rw.get("brief_refs", [])
    if not full and not brief:
        return 0.0
    type_counts = Counter((b.get("type") or "").split()[0].lower() for b in full)
    typed = sum(1 for b in full if b.get("type") and b.get("what_changed") and b.get("why"))
    identifiers = sum(1 for b in full if b.get("doi") and "not specified" not in b.get("doi", "").lower())
    type_diversity = len(set(t for t in type_counts if t in {"imports", "bounds", "baseline", "extends", "refutes"}))
    full_depth = min(1.0, len(full) / 12.0)
    typed_quality = typed / max(1, len(full))
    id_quality = identifiers / max(1, len(full))
    brief_tier = 1.0 if len(brief) >= 5 else len(brief) / 5.0
    diversity = min(1.0, type_diversity / 3.0)
    return 25.0 * clamp(0.25 * full_depth + 0.30 * typed_quality + 0.15 * id_quality + 0.15 * brief_tier + 0.15 * diversity)

def match_external_to_ara(external_papers, ara_refs):
    matched = []
    for p in external_papers:
        p_doi = (p.get("doi") or "").lower()
        p_title = p.get("title", "")
        hit = False
        for r in ara_refs:
            r_doi = (r.get("doi") or "").lower()
            if p_doi and r_doi and p_doi == r_doi:
                hit = True
                break
            if fuzzy_same(p_title, r.get("title", "")):
                hit = True
                break
        matched.append(hit)
    return matched

def external_recall_score(external_landscape, parsed_problem, parsed_rw):
    ara_refs = parsed_rw.get("all_refs", [])
    top_required = [p for p in external_landscape if p.get("relevance", 0) >= 3]
    important = top_required[:50]
    contradiction = [p for p in external_landscape if p.get("contradiction_or_failure")]
    if not external_landscape:
        return 0.0
    matched = match_external_to_ara(important, ara_refs)
    recall = sum(matched) / max(1, len(important))
    contradiction_matches = match_external_to_ara(contradiction, ara_refs)
    contradiction_recall = sum(contradiction_matches) / max(1, len(contradiction))
    problem_text = " ".join(
        [g.get("existing_attempts", "") + " " + g.get("why_they_fail", "") for g in parsed_problem.get("gaps", [])]
    ).lower()
    problem_mentions_contradiction = 1.0 if re.search(r"fail|contradict|inconsistent|baseline|bound|limited|refut", problem_text) else 0.0
    # If no contradiction candidates were found, do not require them; if search fails entirely, score is already zero.
    contradiction_component = 1.0 if not contradiction else 0.75 * contradiction_recall + 0.25 * problem_mentions_contradiction
    return 25.0 * clamp(0.65 * recall + 0.35 * contradiction_component)

def tree_alignment_score(tree_obj, external_landscape):
    nodes = []
    def walk(items):
        for n in items or []:
            nodes.append(n)
            walk(n.get("children", []))
    if isinstance(tree_obj, dict):
        walk(tree_obj.get("tree", []))
    if not nodes:
        return 0.0
    question_nodes = [n for n in nodes if n.get("type") == "question"]
    decision_nodes = [n for n in nodes if n.get("type") == "decision"]
    dead_nodes = [n for n in nodes if n.get("type") == "dead_end"]
    sourced = [n for n in nodes if n.get("source_refs")]
    contradiction_exists = any(p.get("contradiction_or_failure") for p in external_landscape)
    q = 1.0 if question_nodes else 0.0
    d = min(1.0, len(decision_nodes) / 2.0)
    dead = (min(1.0, len(dead_nodes) / 1.0) if contradiction_exists else 1.0)
    source_quality = len(sourced) / max(1, len(nodes))
    return 10.0 * clamp(0.25 * q + 0.25 * d + 0.25 * dead + 0.25 * source_quality)

def anti_padding_score(parsed_rw, external_landscape):
    ara_refs = parsed_rw.get("all_refs", [])
    if not ara_refs:
        return 0.0
    external_matches = match_external_to_ara(external_landscape[:500], ara_refs)
    # Precision is estimated over ARA refs by reversing the comparison.
    supported = 0
    for r in ara_refs:
        for p in external_landscape[:500]:
            if ((r.get("doi") and p.get("doi") and r.get("doi").lower() == p.get("doi").lower())
                    or fuzzy_same(r.get("title", ""), p.get("title", ""))):
                supported += 1
                break
    precision = supported / max(1, len(ara_refs))
    typed_refs = len(parsed_rw.get("rw_blocks", [])) / max(1, len(ara_refs))
    return 5.0 * clamp(0.75 * precision + 0.25 * min(1.0, typed_refs * 2.0))

def reference_landscape_completeness(problem_text, related_text, tree_obj, metadata,
                                     parsed_problem, parsed_rw, external_landscape):
    score = 0.0
    score += availability_score(problem_text, related_text, tree_obj, metadata)
    score += problem_depth_score(parsed_problem)
    score += related_work_score(parsed_rw)
    score += external_recall_score(external_landscape, parsed_problem, parsed_rw)
    score += tree_alignment_score(tree_obj, external_landscape)
    score += anti_padding_score(parsed_rw, external_landscape)
    return int(round(clamp(score / 100.0) * 100))
```

### Penalize-don't-skip rules

- Missing `logic/problem.md`: availability loses its problem-file points and problem-depth score is zero.
- Missing `logic/related_work.md`: availability loses its related-work points, related-work score is zero, external recall against ARA references is zero, and anti-padding score is zero.
- Missing or invalid `trace/exploration_tree.yaml`: availability loses its tree points and tree-alignment score is zero.
- Missing `paper_title`, `paper_abstract`, `paper_doi`, or source references: availability loses metadata points and external lookup becomes weaker or zero.
- External call failure: `external_landscape = []`, so external recall is zero. The metric does not mark the case N/A.
- Invalid LLM JSON for a candidate: candidate gets zero relevance; it is retained as a failed evaluation record, not silently removed.
- Abstract-only evidence is treated as available but thin, so it receives partial availability and low depth.

## Why this is hard to Goodhart

The score triangulates three independent surfaces: the ARA's problem reasoning, its typed citation graph, and an external search neighborhood. A compiler cannot get a high score by merely adding many citations, because those citations must have typed roles, identifiers, technical deltas, and overlap with papers independently surfaced by search. It cannot get a high score by writing polished gap prose alone, because omissions of high-relevance external papers and contradicting work reduce recall. It also cannot invent contradictions or dead ends cheaply, because the workflow checks whether those roles are supported by search metadata, abstracts, and source refs.

The metric is still bounded: it depends on search quality, metadata availability, and abstract quality from external services. Those weaknesses are handled as explicit scoring penalties rather than exclusions.

## Composition with the rest of the suite

This metric complements structural validators by adding an external-literature axis. Shape checks can tell whether `problem.md`, `related_work.md`, and `exploration_tree.yaml` are well formed; this metric asks whether they cover the real prior-work landscape. It also composes with problem-quality metrics by distinguishing a genuine gap from a gap created by missing citations, and with trace metrics by checking whether decisions and dead ends are grounded in known prior attempts. Its strongest unique contribution is catching ARAs that are internally coherent but scientifically under-situated.
