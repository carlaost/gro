# V3 per-metric improvement plan (build-ready)

Derived from `critiques-round2.md` (RC1–RC11) and `v3-spec.md`, made concrete against the actual
V1 parser API (`research/metrics/compute_metrics.py`) and the compiler model
(`compiler-model.md`, ground truth). The **spine** (`compute_metrics_v3.py`) is built and runs
end-to-end against pending stubs. This plan is the contract for the three module files.

## Architecture (spine — DONE)
- **Two axes (RC10):** `paper_rankers` (extractive, de-fabricated — the only things ranked) vs
  `artifact_trust` (homogenization + compiler-determined signals → geometric-mean weight `w`; `w`
  never lowers a paper's own rank, only scales its library contribution and flags low-trust).
- **Validity ⟂ variance (RC1):** every paper ranker reports `{variance_verdict, validity_verdict,
  usable}`; `usable = discriminating AND validity ∈ {validated, source_bound}`. No bare
  "discriminating".
- **Genre (RC8/RC9):** three-tier (gold labels win; Tier-C word-boundary rules over structured
  fields as audit/fallback), fine→coarse→pairwise ladder with `K_MIN=3`, never a singleton ranking.
- **Module loading:** graceful — a missing/broken module or unavailable LLM/MCP degrades to
  `pending`, so partial builds still run.

---

## Module A — `detectors.py` (RC3, RC4, RC5)

### RC3 `dead_end_density` — count only genuine, author-documented dead-ends
A `tree_nodes` entry of `type == "dead_end"` counts iff ALL hold, else `synthetic` (excluded):
1. `support_level == "explicit"`; AND
2. `source_refs` point to a real failed/abandoned attempt — EXCLUDE refs matching
   `/(Table|Outcome|Abstract|§?\s*[34]\.|Results|Discussion|Conclusion)/`; AND
3. `hypothesis` is NOT a negation/mirror of a `headline_claims` statement (if `hypothesis ≈
   NOT(supported claim)`, it's a reframed conclusion → synthetic); AND
4. `coarse == "SYNTHESIS"` ⇒ default to synthetic unless 1–3 strongly hold (reviews/meta-analyses/
   guidelines structurally have no exploration process).
`value = genuine_dead_ends / n_claims`. `source_binding_ratio = genuine / (genuine+synthetic)`.
`validity`: `source_bound` if any genuine; `invalid_fabricated` if ratio == 0 (all synthetic).
**Wave-1 acceptance:** che26 N11/N12 (source_refs Table 2/§4.1, hypothesis = NOT(supported)) →
synthetic → che26 `value → 0`, validity `invalid_fabricated`.

### RC4 `corrective_science` — credit only evidence-addressing edges
An `rw_blocks` edge counts as corrective iff: `type ∈ {refutes, bounds}` AND `claims_affected`
non-empty AND `delta` contains contrastive language
`/(contradict|fails to replicate|overturn|did not hold|lower than reported|not reproducible|refut|revises? down)/i`.
Weight `refutes` > `bounds`. Baseline-naming scores 0 (`type` contains `baseline`, or delta is
"prior standard we improve on"). `value` = weighted count; `n_corrective_edges` = qualifying edges.
`validity`: `source_bound` if any genuine edge, else `invalid_fabricated`.
**Acceptance:** refutes=0 corpus-wide + che26 RW14 is a synthesis conclusion → corrective ~0 across
the corpus (the honest signal that this corpus does little corrective work).

### RC5 `negative_result_share` — detect nulls by semantics, not `status`
A claim is a negative finding if `statement` matches
`/(no significant difference|did not differ|was not associated|failed to|no correlation|not superior|did not improve|no benefit|non-?significant|cohen'?s d\s*<\s*0\.2|auc\s*(=|of)?\s*0\.5\d*|CI[^.]*cross)/i`.
`value = (negative-finding claims + refuted claims + genuine dead-ends[RC3]) / n_claims` (do NOT
double-count a claim already caught by RC3). `validity = pending_sem` (regex approximates a [sem]
pass). **Acceptance:** woj25 C04 ("fails to differentiate", "Cohen's d < 0.2", AUC 0.514) counts.

---

## Module B — `grounding.py` (RC6, RC7)

### RC6 `grounding_trust` — reclassify to the artifact-trust axis + explicit trust classes
Reuse V2's `verified_grounding` shape (re-open the cited in-repo `.md`, check the «quote» is present
after NFKC + dash-fold + whitespace-collapse). This is an ARTIFACT-TRUST signal (spine already routes
it), NOT a paper ranker. Replace the old `None` with an explicit `trust_class`:
`self_contained` (quotes cite in-repo evidence), `pdf_pointer` (cite paper.pdf/§), `no_parseable_quotes`,
`no_source`, or `mixed`. `value` = verified ratio over checkable quotes; `coverage` = #checkable;
`self_contained_ratio` = checkable / present. A quote missing due to extraction/format routes to the
trust_class (`quote_not_found_extraction`), NOT to a grounding failure. PyMuPDF PDF resolution is an
OPTIONAL coverage booster inside this axis only (3 PDFs missing → never corpus-wide); gate behind
availability.

### RC7 `semantic_grounding` — does the quote SUPPORT the number? (paper ranker)
If a frozen `logic/grounding_findings.yaml` exists (per-(number,quote) `verdict/value_match/polarity_ok/
context_match`), score deterministically: `grounded = string_present ∧ verdict==supports ∧
value_match∈{exact,rounded,derived} ∧ polarity_ok ∧ context_match`. If an LLM [sem] pass is available,
emit those findings first (use a DIFFERENT model than the compiler — avoid self-grading). If neither is
available, return `value="pending", validity="pending_sem"` — do NOT fabricate. Honest note: low yield
on this well-compiled corpus; it's a guardrail for worse ARAs.

---

## Module C — `external.py` (RC2 — the BLOCKER, honest partial)

Corpus-level. `external_validation(all_ctx)`:
1. **ClinicalTrials.gov concordance** (MCP if reachable): for each trial-linked ARA (n≈4), pull the
   registered primary endpoint/result, label the central claim `concordant/discordant/neutral`. Cache
   raw JSON under `external_cache/<nct>.json`. Unreachable → `pending` (never fabricate).
2. **Retraction/EoC lookup** (Europe PMC/PMC via WebFetch): run, report `degenerate` (all 2025–26,
   clean, zero variance).
3. **Expert labels**: if `expert_labels.yaml` (n≈12) exists, Spearman ρ vs a paper ranker + STATE the
   circularity caveat (labeler ≈ author). Else `pending`.
`summary` encodes the master ruling: held-out powered validation is NOT achievable at n=12 → mark
`pending: larger heterogeneous code-shipping corpus`; do not launder underpowered ρ as "validated".

---

## RC11 (spine/doc) — DONE in routing; also correct `metrics-directions.md` row 5 to "dropped in V2,
not implemented (spec-completeness is [sem], deferred)". Handled outside the modules.

## Round-3 handback
After all three modules land: rerun `compute_metrics_v3.py`, read `comparison_v2_v3.md` against each
acceptance criterion above, and expect **0–1 usable paper-rankers** — the validity gate working.
