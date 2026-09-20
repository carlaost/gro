# M14 expansion: Reference-landscape completeness

## Metric reasoning

Reference-landscape completeness measures whether the ARA's problem layer places the work in the real surrounding literature rather than only echoing the source paper's own framing. Good science is not just internally coherent; it is situated against the best-known prior results, nearby methods, failed or contradictory findings, and the actual alternatives a competent search would reveal. This metric rewards an ARA that cites the relevant literature island, names contradictory or limiting work, and gives enough citation breadth for a downstream agent to trust that the stated observations, gaps, and key insight are not an artifact of a narrow source read.

The primary artifact is `logic/problem.md`, because the Observations, Gaps, Key Insight, and Assumptions are where missing literature most directly distorts the research question. `logic/related_work.md` is the citation-footprint cross-check: it should preserve the full typed dependency graph, including full `RW##` blocks and a brief tier for background/supporting references. `trace/exploration_tree.yaml` is a second cross-check: if the surrounding literature contains clear abandoned approaches, failed baselines, pivots, or contradictions, the exploration tree should expose them where the source supports that interpretation.

The metric should reward:

- Observations grounded in section-level prior-work citations rather than abstract-only paraphrase.
- Gaps that name concrete existing attempts and specific failure modes.
- A related-work graph with typed technical deltas for primary dependencies and a brief tier covering the broader citation footprint.
- Inclusion of search-discovered nearest-neighbor papers, especially papers that contradict, bound, or materially qualify the source paper's framing.
- Explicit links from problem claims to related-work entries and trace nodes where prior failed paths or alternatives matter.
- Accurate treatment of literature roles: `imports`, `bounds`, `baseline`, `extends`, and `refutes` should be used for what the cited work actually does.

The metric must not reward:

- Long citation lists with no technical role, DOI/arXiv identifier, or claim relevance.
- Generic "prior work is limited" language where the literature has named methods, cohorts, baselines, or failure modes.
- Inflating `refutes` or `dead_end` edges when the source paper and search results only support ordinary extension or comparison.
- Coverage of only the source paper's references when external search reveals obvious, highly similar missing work.
- Coverage of only the newest papers while missing canonical background that defines the problem.
- Abstract-only citation footprints that look structurally complete but have no real Introduction/Methods grounding.

The assessment-critique notes make the design stricter than a normal citation-count metric. The edge of M14 is that neither round-1 nor the verifier reaches external literature, so the central signal is external search recall and contradiction/bounding awareness. Redundancy with internal ARA validation is avoided by not merely asking whether citations are syntactically present. The metric asks whether the cited landscape matches what Semantic Scholar, k-nearest-neighbor literature search, and an Undermind-style search agent surface for the paper's problem. Verifier-overlap is limited to using ARA fields as inputs; the scoring itself depends on outside literature coverage and role alignment.

## Failure modes and gaming routes

The main gaming route is citation padding: adding many plausible references without demonstrating why they matter. The workflow counters this by scoring unique externally discovered targets, role labels, DOI/arXiv recoverability, and overlap between external targets and ARA claims, not raw citation volume.

A second route is cherry-picking only supportive references. The workflow therefore gives a dedicated contradiction/bounds score and penalizes externally surfaced papers that contain opposing results, negative baselines, or limitations absent from the ARA.

A third route is hiding behind unavailable data. The metric assumes artifact fields and external-call outputs are score inputs. Missing `problem.md`, missing `related_work.md`, unparseable `exploration_tree.yaml`, failed external calls, thin citations, or absent DOI/title metadata all score down. Nothing becomes N/A.

A fourth route is over-inventing. An ARA might add unsupported refutation or dead-end claims to look comprehensive. The workflow penalizes unsupported explicit trace nodes and role labels that are not textually justified by the ARA fields or the external abstract/title snippets.

## Generation/compute WORKFLOW

### Inputs

Required artifact inputs, all scored for availability:

- `logic/problem.md`: parse Observations `O{N}`, Gaps `G{N}`, Key Insight, and Assumptions.
- `logic/related_work.md`: parse full `RW##` blocks, DOI/arXiv IDs, type labels, deltas, claims affected, adopted elements, and any brief/background citation tier.
- `trace/exploration_tree.yaml`: parse `tree`, node types, `support_level`, `source_refs`, `title`, `description`/`result`/`choice`/`hypothesis` fields.
- Optional paper metadata available to the evaluator from the ARA run: paper title, DOI/arXiv ID, abstract, venue/year. If absent, derive a fallback query from `problem.md` Key Insight plus top Observation titles and score the metadata-availability component down.

External calls:

- `[ext] Semantic Scholar paper lookup` for the source paper metadata and citation graph.
- `[ext] Semantic Scholar recommendations/search` for nearest relevant papers.
- `[ext] Undermind-style literature search` for broader literature island, contradictions, and missing canonical papers.
- `[sem] LLM role classifier` only for deterministic JSON extraction from external abstracts/snippets into role labels and contradiction flags. The score uses the JSON after schema validation, not free-form prose.

### Parsing steps

1. Read `logic/problem.md`. Extract citation-like spans from `**Evidence**`, author-year mentions, DOI/arXiv strings, and section references. Count Observations, Gaps, and Gaps with non-generic `Existing attempts` and `Why they fail`.
2. Read `logic/related_work.md`. Extract full references from `RW##` headings and brief/background bullets. Normalize each reference to `{title_or_author_year, year, doi_or_arxiv, type, delta_text, claims_affected, adopted_elements, tier}`.
3. Read `trace/exploration_tree.yaml`. Validate YAML parse and collect nodes whose type is `decision`, `dead_end`, or `pivot`; collect titles and source refs.
4. Build `ara_reference_set` from all normalized references in `problem.md` and `related_work.md`. Deduplicate by DOI/arXiv when present, else by normalized author-year/title token key.
5. Build `ara_problem_terms` from Observation titles/statements, Gap statements, Existing attempts, Why they fail, Key Insight, and Assumptions.

### External search procedure

#### Semantic Scholar source lookup

Query:

```text
title:"{paper_title}" DOI:"{doi_if_available}" arXiv:"{arxiv_if_available}"
```

If title/DOI/arXiv metadata is missing, query:

```text
{top_8_problem_terms_from_key_insight_and_observations}
```

Return fields: `paperId`, `title`, `year`, `authors`, `abstract`, `externalIds`, `references`, `citations`, `s2FieldsOfStudy`, `embedding` if available.

Scored handling: no match or failed call sets `source_lookup_available = 0`; fallback query may still find candidates but loses the metadata subscore.

#### Semantic Scholar k-NN / literature island

If `paperId` or embedding is available, retrieve:

- top 200 recommended papers or embedding-nearest papers;
- top 150 references from the source paper;
- top 150 citing papers, prioritizing title/abstract similarity to `ara_problem_terms`.

If no `paperId` is available, run keyword search using the fallback query and retrieve top 300 results.

Filter to a candidate pool of up to 500 by cosine/title-abstract similarity to `ara_problem_terms`, recency/citation balance, and shared field-of-study. Keep canonical older papers by allowing high citation count to override low recency.

#### Undermind-style search

Prompt/query:

```text
We are evaluating whether an ARA captured the true literature landscape for this paper/problem.
Source paper metadata:
Title: {paper_title_or_missing}
DOI/arXiv: {doi_or_arxiv_or_missing}
Abstract or reconstructed problem: {abstract_or_key_insight_plus_observations}

Find the most relevant surrounding literature, including:
1. canonical prior work that defines the problem;
2. closest methodological or empirical predecessors;
3. datasets/cohorts/tools/baselines the paper depends on;
4. papers with contradictory, negative, or bounding findings;
5. highly similar papers a competent search bot would surface but that may not be cited by the source.

Return strict JSON with up to 80 entries:
[
  {
    "title": "...",
    "authors": ["..."],
    "year": 2024,
    "doi_or_arxiv": "... or null",
    "role": "canonical|nearest_neighbor|dataset_or_tool|baseline|contradicts|bounds|extends|background",
    "why_relevant": "...",
    "evidence_snippet": "...",
    "confidence": 0.0
  }
]
```

Output validation: discard entries without title and year. Keep entries without DOI/arXiv but assign lower match confidence. If the tool fails, `undermind_available = 0` and the external-recall components that depend on it receive zero contribution rather than being skipped.

### Semantic role classifier

For each external candidate in the merged pool, run a constrained classifier on title/abstract/snippet plus ARA problem terms.

Prompt:

```text
Classify this paper's role relative to the target research problem.
Target problem terms:
{ara_problem_terms}

Candidate:
Title: {title}
Year: {year}
Abstract/snippet: {abstract_or_snippet}

Return only JSON:
{
  "is_relevant": true|false,
  "relevance": 0.0,
  "role": "canonical|nearest_neighbor|dataset_or_tool|baseline|contradicts|bounds|extends|background|irrelevant",
  "contradiction_or_bound": true|false,
  "reason": "short phrase"
}
```

Determinization:

- Parse JSON only; invalid JSON becomes `is_relevant=false`, `relevance=0`.
- Clamp `relevance` to `[0,1]`.
- Keep candidates with `is_relevant=true` and `relevance >= 0.55`.
- Sort by `max(relevance, confidence)`, citation count percentile, and recency-adjusted similarity.
- Select `external_gold_set`: top 60 relevant papers, capped at 20 background-only papers and requiring all `contradicts`/`bounds` entries above threshold unless more than 15 exist.

### Scoring function

Final metric range is `[0, 1]`. Missing or thin inputs reduce the score directly.

```python
import re
import yaml
from collections import Counter

GENERIC_FAIL_PATTERNS = [
    r"\bprior work (is|was|has been) limited\b",
    r"\bmore research is needed\b",
    r"\bnot well understood\b",
    r"\blimited evidence\b",
]

def norm_key(s):
    s = (s or "").lower()
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"doi:\s*", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())

def doi_key(ref):
    doi = (ref.get("doi_or_arxiv") or ref.get("doi") or "").lower().strip()
    return doi or None

def ref_key(ref):
    return doi_key(ref) or norm_key((ref.get("title") or ref.get("author_year") or "") + " " + str(ref.get("year") or ""))

def clamp(x):
    return max(0.0, min(1.0, float(x)))

def parse_problem(problem_md):
    observations = re.findall(r"^###\s+O\d+:", problem_md or "", flags=re.M)
    gaps = re.findall(r"^###\s+G\d+:", problem_md or "", flags=re.M)
    evidence_fields = re.findall(r"\*\*Evidence\*\*:\s*(.+)", problem_md or "")
    existing_attempts = re.findall(r"\*\*Existing attempts\*\*:\s*(.+)", problem_md or "")
    why_fail = re.findall(r"\*\*Why they fail\*\*:\s*(.+)", problem_md or "")
    citation_spans = []
    for ev in evidence_fields:
        citation_spans.extend(re.findall(r"[A-Z][A-Za-z-]+ et al\.,\s*\d{4}[a-z]?", ev))
        citation_spans.extend(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", ev))
    generic_gap_count = 0
    for text in existing_attempts + why_fail:
        if any(re.search(p, text.lower()) for p in GENERIC_FAIL_PATTERNS):
            generic_gap_count += 1
    abstract_only = sum(1 for ev in evidence_fields if norm_key(ev) == "abstract")
    return {
        "observation_count": len(observations),
        "gap_count": len(gaps),
        "evidence_count": len(evidence_fields),
        "citation_spans": citation_spans,
        "existing_attempts_count": len(existing_attempts),
        "why_fail_count": len(why_fail),
        "generic_gap_count": generic_gap_count,
        "abstract_only_evidence_count": abstract_only,
        "text": problem_md or "",
    }

def parse_related_work(rw_md):
    refs = []
    for block in re.split(r"(?=^##\s+RW\d+:)", rw_md or "", flags=re.M):
        m = re.match(r"^##\s+(RW\d+):\s*(.+)", block, flags=re.M)
        if not m:
            continue
        ref_id, label = m.groups()
        doi = re.search(r"\*\*DOI\*\*:\s*(.+)", block)
        typ = re.search(r"\*\*Type\*\*:\s*(.+)", block)
        delta = re.search(r"What changed:\s*(.+)", block)
        claims = re.search(r"\*\*Claims affected\*\*:\s*(.+)", block)
        refs.append({
            "id": ref_id,
            "author_year": label.strip(),
            "doi_or_arxiv": None if not doi else doi.group(1).strip(),
            "type": "" if not typ else typ.group(1).strip().lower(),
            "delta_text": "" if not delta else delta.group(1).strip(),
            "claims_affected": "" if not claims else claims.group(1).strip(),
            "tier": "full",
        })
    brief_refs = re.findall(r"^\s*-\s+\*\*(.+?)\*\*\s*(?:\((.*?)\))?\s*[—-]\s*(.+)", rw_md or "", flags=re.M)
    for label, doi, role in brief_refs:
        refs.append({
            "author_year": label.strip(),
            "doi_or_arxiv": (doi or "").strip(),
            "type": "brief",
            "delta_text": role.strip(),
            "claims_affected": "",
            "tier": "brief",
        })
    has_brief_tier = bool(re.search(r"Background|supporting references|Additional citation footprint|brief", rw_md or "", flags=re.I))
    return {"refs": refs, "has_brief_tier": has_brief_tier, "text": rw_md or ""}

def parse_trace(trace_yaml_text):
    try:
        data = yaml.safe_load(trace_yaml_text or "") or {}
    except Exception:
        return {"parse_ok": False, "nodes": [], "strategic_nodes": []}
    nodes = []
    def walk(items):
        for n in items or []:
            nodes.append(n)
            walk(n.get("children") or [])
    walk(data.get("tree") or [])
    strategic = [n for n in nodes if n.get("type") in {"decision", "dead_end", "pivot"}]
    explicit_without_refs = [
        n for n in nodes
        if n.get("support_level") == "explicit" and not n.get("source_refs")
    ]
    return {
        "parse_ok": isinstance(data.get("tree"), list),
        "nodes": nodes,
        "strategic_nodes": strategic,
        "explicit_without_refs": explicit_without_refs,
    }

def weighted_recall(ara_refs, external_gold):
    ara_keys = {ref_key(r) for r in ara_refs if ref_key(r)}
    if not external_gold:
        return 0.0
    total_w = 0.0
    hit_w = 0.0
    for g in external_gold:
        role = g.get("role")
        w = {
            "contradicts": 1.5,
            "bounds": 1.4,
            "nearest_neighbor": 1.25,
            "dataset_or_tool": 1.2,
            "baseline": 1.15,
            "canonical": 1.1,
            "extends": 1.0,
            "background": 0.65,
        }.get(role, 1.0)
        total_w += w
        if ref_key(g) in ara_keys:
            hit_w += w
    return hit_w / total_w if total_w else 0.0

def contradiction_coverage(ara_refs, external_gold):
    targets = [g for g in external_gold if g.get("role") in {"contradicts", "bounds"} or g.get("contradiction_or_bound")]
    if not targets:
        return 0.65  # no contradiction surfaced; modest credit, not full credit
    ara_keys = {ref_key(r) for r in ara_refs if ref_key(r)}
    hit = sum(1 for g in targets if ref_key(g) in ara_keys)
    return hit / len(targets)

def role_alignment(ara_refs):
    if not ara_refs:
        return 0.0
    full = [r for r in ara_refs if r.get("tier") == "full"]
    if not full:
        return 0.15
    typed = [r for r in full if r.get("type") and r.get("type") != "brief"]
    with_delta = [r for r in full if len(norm_key(r.get("delta_text"))) >= 8]
    with_claims = [r for r in full if r.get("claims_affected") and "none" not in r.get("claims_affected", "").lower()]
    return clamp(0.45 * len(typed) / len(full) + 0.35 * len(with_delta) / len(full) + 0.20 * len(with_claims) / len(full))

def problem_grounding(problem):
    obs = problem["observation_count"]
    gaps = problem["gap_count"]
    if obs == 0 and gaps == 0:
        return 0.0
    section_grounded = max(0, problem["evidence_count"] - problem["abstract_only_evidence_count"])
    evidence_score = clamp(section_grounded / max(1, obs))
    citation_score = clamp(len(set(problem["citation_spans"])) / max(4, obs * 2))
    gap_specificity = clamp((problem["existing_attempts_count"] + problem["why_fail_count"] - problem["generic_gap_count"]) / max(1, gaps * 2))
    return clamp(0.40 * evidence_score + 0.30 * citation_score + 0.30 * gap_specificity)

def breadth_score(rw, problem):
    refs = rw["refs"]
    full_count = sum(1 for r in refs if r.get("tier") == "full")
    brief_count = sum(1 for r in refs if r.get("tier") == "brief")
    type_counts = Counter(r.get("type", "").split()[0] for r in refs)
    count_score = clamp((full_count / 12.0) * 0.65 + (brief_count / 20.0) * 0.35)
    tier_score = 1.0 if rw["has_brief_tier"] and brief_count > 0 else 0.45
    diversity_score = clamp(len([t for t in type_counts if t in {"imports", "bounds", "baseline", "extends", "refutes"}]) / 4.0)
    abstract_penalty = 1.0 - clamp(problem["abstract_only_evidence_count"] / max(1, problem["evidence_count"]))
    return clamp((0.45 * count_score + 0.25 * tier_score + 0.30 * diversity_score) * abstract_penalty)

def trace_literature_link_score(trace, external_gold):
    if not trace["parse_ok"]:
        return 0.0
    strategic = trace["strategic_nodes"]
    if not strategic:
        return 0.25
    text = norm_key(" ".join(str(n.get(k, "")) for n in strategic for k in ["title", "choice", "hypothesis", "failure_mode", "trigger", "lesson"]))
    cb_terms = [norm_key(g.get("title", "")) for g in external_gold if g.get("role") in {"contradicts", "bounds", "baseline"}]
    hits = 0
    for term in cb_terms:
        words = [w for w in term.split() if len(w) > 4][:5]
        if words and sum(1 for w in words if w in text) >= min(2, len(words)):
            hits += 1
    unsupported_penalty = clamp(len(trace["explicit_without_refs"]) / max(1, len(trace["nodes"])))
    if not cb_terms:
        base = clamp(len(strategic) / 4.0)
    else:
        base = hits / len(cb_terms)
    return clamp(base * (1.0 - unsupported_penalty))

def availability_score(problem_md, rw_md, trace_yaml_text, external_status):
    artifact_bits = [
        bool(problem_md and problem_md.strip()),
        bool(rw_md and rw_md.strip()),
        bool(trace_yaml_text and trace_yaml_text.strip()),
    ]
    external_bits = [
        bool(external_status.get("source_lookup_available")),
        bool(external_status.get("semantic_scholar_available")),
        bool(external_status.get("undermind_available")),
    ]
    return 0.55 * (sum(artifact_bits) / 3.0) + 0.45 * (sum(external_bits) / 3.0)

def score_m14(problem_md, related_work_md, trace_yaml_text, external_gold_set, external_status):
    problem = parse_problem(problem_md)
    rw = parse_related_work(related_work_md)
    trace = parse_trace(trace_yaml_text)
    ara_refs = rw["refs"]
    recall = weighted_recall(ara_refs, external_gold_set)
    contradict = contradiction_coverage(ara_refs, external_gold_set)
    grounding = problem_grounding(problem)
    breadth = breadth_score(rw, problem)
    alignment = role_alignment(ara_refs)
    trace_links = trace_literature_link_score(trace, external_gold_set)
    avail = availability_score(problem_md, related_work_md, trace_yaml_text, external_status)
    return clamp(
        0.25 * recall +
        0.15 * contradict +
        0.15 * grounding +
        0.15 * breadth +
        0.10 * alignment +
        0.10 * trace_links +
        0.10 * avail
    )
```

### Component interpretation

- `weighted_recall` is the core net-new signal: whether externally surfaced relevant papers appear in the ARA reference landscape.
- `contradiction_coverage` prevents supportive-only landscapes from scoring high.
- `problem_grounding` checks whether `problem.md` uses real prior-work citations and specific failure modes.
- `breadth_score` checks full plus brief related-work coverage, type diversity, and abstract-only degradation.
- `role_alignment` rewards technical deltas and claim-linked typed edges instead of citation padding.
- `trace_literature_link_score` rewards literature-aware decisions, dead ends, and pivots while penalizing explicit trace nodes without source refs.
- `availability_score` implements penalize-don't-skip: missing artifacts or failed external calls lower the score.

### Missing-context handling

The supplied M14 brief references `§4 problem (cross §6,§8)`. The allowed primary shape file provides §4, and the allowed aggregate shape file provides §6 `logic/related_work.md` and §8 `trace/exploration_tree.yaml`. No required section was unavailable. If an evaluator lacks paper metadata, Semantic Scholar access, Undermind access, `related_work.md`, or `exploration_tree.yaml` during actual computation, that unavailability must be recorded in `external_status` or empty artifact inputs and scored down by the function above rather than skipped.

## Why it is hard to Goodhart

This metric is hard to Goodhart because high scores require agreement between three independent surfaces: the ARA's internal problem framing, the related-work dependency graph, and external literature retrieval. A model can add citations, but it cannot easily know which missing papers a k-NN/Undermind search will surface, which of them contradict or bound the paper, and how those papers should map to Gaps, deltas, claims, and trace decisions. Citation padding has limited value because role alignment, DOI/title normalization, contradiction coverage, and external weighted recall dominate raw count.

The metric also makes unsupported richness costly. Invented dead ends, overclaimed `refutes` edges, and explicit trace nodes without source refs reduce the score. Abstract-only or thin compiles cannot hide behind structurally valid markdown because evidence depth, brief-tier coverage, typed deltas, and external recall are all scored.

## Composition with the suite

M14 composes as the suite's external-literature recall check. Internal verifier-style metrics can test whether fields are well formed, traceable, and logically consistent; M14 tests whether the ARA's world model includes the literature a competent search would find. It complements problem-quality metrics by asking whether Observations and Gaps are grounded in the actual field, complements dependency-graph metrics by testing external completeness rather than graph syntax, and complements trace metrics by checking whether decisions and abandoned paths reflect known baselines and contradictory work.

Because M14 penalizes missing/thin inputs and failed external retrieval, it also supplies a useful floor signal: an ARA compiled from only an abstract may remain syntactically coherent, but it should score poorly on reference-landscape completeness.

## Compliance check

- Read required file `research/metrics/v3/tournament2/EXPAND_BRIEF.md`.
- Read required file `research/metrics/v3/tournament2/M14/brief.md`.
- Read required file `research/metrics/v3/tournament/shapes/04_problem.md`.
- Also read allowed cross-layer sections §6 and §8 from `research/metrics/v3/tournament/DATA_SHAPES.md`.
- Did not read any other metrics' files, round-1 winners, or critique documents.
- Wrote this expansion to `research/metrics/v3/tournament2/M14/proposals/exp4.md`.
- Included all expansion elements required by `EXPAND_BRIEF.md`: reasoning, rewards/non-rewards, failure modes/gaming, assessment-critique implications, concrete generation/compute workflow, external calls and prompts, deterministic scoring function, Goodhart resistance, and suite composition.
