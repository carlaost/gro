# Can the anchored and judged GRO tiers be computed against external ground truth? A partial s7.1 experiment over six Alzheimer's ARAs

## Abstract

The prior deterministic-tier experiment stayed inside the artifact: it converted eight prose-blocked metrics into structural joins over LLM-authored sidecars, ran them corpus-wide with no network, and concluded — as the parent v3 tournament had — that a self-contained metric "cannot, in principle, verify anything about the world outside that file." This experiment does the opposite thing on purpose. It is a partial run of the spec's s7.1 step — *validate the anchored and judged tiers against external ground truth* — and it **leaves the artifact**, issuing live calls to PubMed and ClinicalTrials.gov to resolve references, check novelty against the indexed literature, join trial claims to their registered outcomes, and search for retractions. Over six Alzheimer's-domain ARAs the anchored/judged operations are computable against real external records: 64 of 67 sampled references resolved to matching PubMed entries, both donanemab papers joined to NCT04437511 and its registered endpoints, novelty verdicts spread across the full spectrum, and zero retractions surfaced. The tiers therefore *compute* against external truth and *differentiate* legitimate papers on quality/novelty axes. But the honest limit is decisive: this corpus contains zero known-bad papers — no retractions, near-total reference resolvability, no concealed outcome switching — so it validates external computability and surfaces concordance gaps, but it is **not** a good-versus-bad discrimination test. That still needs a labelled contrast set. All extensions and all external lookups here are LLM-mediated.

## 1. What is different from the prior experiment

The deterministic-tier experiment (`EXPERIMENT_PAPER.md`) answered a computability question that never crossed the artifact boundary: given typed sidecars, do Tier-A metrics collapse into LLM-free, network-free joins? Yes — but every one of those metrics reads only `gro/*.yaml`. Its `reference_resolvability_rate` there meant only whether an `external_id` string was *printed and typed as resolvable*; no DOI was ever fetched.

This experiment tests the two tiers that experiment explicitly deferred. Per the spec (§1), **Tier B · Anchored** resolves ids to the outside world through pinned resolvers, and **Tier C · Judged** produces novelty/entailment verdicts by reading the graph and comparing it against external precedent. Both are defined by *leaving* the file. So the single methodological difference is the one that matters: here the passes made **real MCP calls to PubMed (`search_articles`, `get_article_metadata`) and ClinicalTrials.gov (`search_trials`, `get_trial_details`)**, resolving real records rather than reading a self-declared boolean. This is the s7.1 "validate against external ground truth" step — run partially, on a six-ARA slice.

## 2. Method

**Corpus (n=6).** All Alzheimer's-domain: two donanemab trial papers (`zim25`, `jes26`, both TRAILBLAZER-ALZ 2 / NCT04437511), three plasma-biomarker studies (`che26` p-tau217 network meta-analysis, `val25` SNAC-K blood-biomarker cohort, `tit26` automated p-tau217 assay), and one first-in-literature functional tau-seeding assay preprint (`han26`, VeraBIND Tau).

**Anchored operations.** For each ARA we sampled 7–12 DOI-anchored references from its `gro/refs.yaml` and resolved each live against PubMed, recording whether the returned title/authors matched the cited work (observed resolvability), against the sidecar's self-declared `resolvable` rate. For the two trial papers we resolved NCT04437511 on ClinicalTrials.gov and joined each typed claim to a registered outcome, classifying it `matches_registered`, `added_post_hoc`, or `dropped`. For every paper we searched for retractions/corrections on the paper itself and its most-cited references.

**Judged operation.** For each ARA we took its headline claims (`gro/claims_typed.yaml`) and searched PubMed for prior art, assigning `novel` / `incremental` / `previously_reported` / `cannot_determine`.

Per-ARA evidence JSON is under `external/`; the synthesis is `external_validation.json`. Every id and outcome cited below came from a live MCP response — none were invented.

## 3. Results

### 3.1 Reference resolvability: observed vs declared

All 67 sampled references were resolved live; **64 matched PubMed records (pooled observed rate 0.955; unweighted per-ARA mean 0.958)**. The three misses were all in `val25`, where PubMed returned no confident match for three citations.

The load-bearing finding is the **gap between observed and declared** resolvability. The unweighted mean self-declared rate across the six ARAs was **0.520** — far below the 0.958 observed:

| ARA | Sampled resolved | Observed | Declared |
|---|---|---|---|
| zim25 | 12/12 | 1.00 | 0.957 |
| jes26 | 12/12 | 1.00 | 0.895 |
| che26 | 12/12 | 1.00 | 0.944 |
| val25 | 9/12 | 0.75 | 0.00 |
| han26 | 12/12 | 1.00 | 0.19 |
| tit26 | 7/7 | 1.00 | 0.132 |

The gap is **not** a quality failure. `val25` (declared 0), `han26` (0.19), and `tit26` (0.13) marked most references `external_id: not_specified` because the compilation *input* was a main-text-only PDF without a captured bibliography carrying DOIs — yet PubMed resolved those same references from the raw citation strings. `val25` is the clearest case: its `refs.yaml` marks all 55 references unresolvable (0%), but searching PubMed on the bare citation text resolved 9 of 12 sampled, including exact author/journal/year/volume/page matches for well-known papers (Jack 2024 *Alzheimers Dement*, Palmqvist 2020 *JAMA*, Dubois 2024 *JAMA Neurol*).

This exposes a real semantic gap in the anchored-tier metric: **the sidecar's `resolvable` field measures compilation-time DOI capture, not true external verifiability.** The two quantities are being conflated under one name. Until the metric is redefined to separate "was a DOI captured at compile time" from "does this reference resolve against a live index," anchored-tier resolvability scores are not comparable across papers with different compilation inputs.

### 3.2 Novelty distribution

Across **31 headline claims** checked against PubMed, verdicts spanned the full spectrum: **10 novel (32%), 10 incremental (32%), 7 cannot_determine (23%), 4 previously_reported (13%)**. This is genuine differentiating signal, and it separates the corpus:

- **High-novelty end:** `han26` — 4 of 5 claims `novel`. VeraBIND Tau is a proprietary, patent-pending functional tau-seeding assay first described in this preprint; PubMed searches for the assay name and for generic plasma-tau-seeding-vs-tau-PET diagnostics returned no prior art beyond the paper itself.
- **Confirmatory end:** `tit26` — 3 of 5 `previously_reported` (an automation reimplementation of established p-tau217 assays); and `val25`, whose headline claims restate a same-cohort companion *Nature Medicine* paper (PMID 40140622) published ~7 months earlier by the same author group on the same SNAC-K cohort (n=2148) with the same biomarker panel. `val25`'s genuine novel contribution is the multistate Markov transition machinery, not the biomarker-dementia associations its headline claims foreground.

The judged tier thus locates papers on a novelty axis using real precedent, not self-report. The caveat is that `cannot_determine` is 7/31 (~23%): absence of a PubMed hit is weak evidence for narrow subgroup or derived claims, so the novel/incremental split carries real uncertainty.

### 3.3 Trial-registry concordance (donanemab papers)

Both trial papers resolved to **NCT04437511** on ClinicalTrials.gov, and their claims joined to the registered outcomes. **No concealed outcome switching was found in either.** What surfaced instead were two transparent *concordance gaps*:

- **zim25:** registered primaries reproduced and matched (CDR-SB change, amyloid PET Centiloid reduction); several reported analyses were **added post-hoc** (CDR-Global hazard ratio, pooled amyloid-reaccumulation model, AUC/time-saved), and registered endpoints (tau PET, vMRI, PK, anti-drug antibodies) were **dropped**. The paper itself discloses the post-hoc endpoints as uncontrolled for multiplicity.
- **jes26:** registered iADRS (overall + intermediate-tau) and CDR-SB and amyloid PET matched; CDR-Global Cox HR, plasma P-tau217, derived time-saved/no-progression metrics, and an LTE-vs-ADNI external-control comparison were **added post-hoc**; ADAS-Cog13, MMSE, ADCS-iADL, tau PET, vMRI, PK, and immunogenicity were **dropped**.

The metric behaves correctly: it flags the registered-vs-reported gap **without** mislabeling transparent post-hoc exploratory analysis as fraud. This is exactly the discrimination the L7 layer is designed for. The limit is statistical: both papers are the *same* trial, so registry-concordance evidence here is effectively one data point.

### 3.4 Retractions

**Zero.** Retraction/correction searches on all six papers and their most-cited references returned nothing. (One unconstrained broad query returned 1007 spurious hits from PubMed boolean OR-scoping and was discarded as a query-construction artifact, not evidence.)

## 4. The honest conclusion on discrimination

Two things are true, and they must be stated separately.

**External computability works.** The anchored and judged tiers are not vaporware: they make live MCP calls that resolve real records. 64/67 sampled references matched PubMed; NCT04437511 resolved with its registered outcome list; the ARAs' own papers were found indexed with matching figures (zim25 headline numbers, jes26 as PMID 42202469, che26/han26/tit26 confirmed by exact title match). The s7.1 "validate the anchored/judged tiers against external ground truth" step **executes** on real infrastructure, and it produces differentiating signal across this corpus on three axes: judged novelty (`han26` high-novel vs `tit26`/`val25` confirmatory), the declared-vs-observed reference gap (well-compiled `zim25`/`jes26`/`che26` vs under-declared `val25`/`han26`/`tit26`), and registry concordance (both trial papers showing transparent post-hoc endpoint elevation).

**But this is not a good-versus-bad discrimination test — and cannot be, on this corpus.** Every paper here is essentially legitimate: zero retractions, near-total reference resolvability, no concealed outcome switching. The "differentiation" observed is *variance on quality and novelty axes among papers that are all real science*. That is a genuinely different thing from separating trustworthy work from untrustworthy work. This is the same wall the parent program hit: the v3 tournament concluded, across all winning metric sets, that "a well-compiled record of bad science and a well-compiled record of good science are, by construction, indistinguishable to every metric in this tournament." Leaving the artifact loosens that constraint — external resolution *can* catch a fabricated reference or a retracted citation, which a self-contained metric provably cannot — but this experiment never presented the tiers with a fabricated reference or a retracted citation to catch. It confirmed the tiers *can reach* external truth; it did not test whether they *separate* good from bad, because there was no bad in the sample.

It is also worth naming that the whole apparatus is LLM-mediated. The sidecars being validated were LLM-authored (the fidelity ceiling the prior experiment described), and the anchored/judged passes here — deciding whether a returned PubMed title "matches" a citation, whether a claim has prior art, whether a reported endpoint "matches" a registered one — are LLM judgements over the tool outputs. The MCP calls are real and deterministic; the *adjudication* of their results is not. Per the spec (§7), independence is pipeline-independence, "necessary not sufficient," everywhere except L3's non-LLM matcher, which was not exercised here.

## 5. Limitations

- **No known-bad papers.** The corpus has zero retracted, fabricated-reference, or expert-flagged-defective papers, so it shows across-corpus variance among legitimate work, not good-vs-bad separation.
- **n=6, one narrow domain** (Alzheimer's biomarkers / anti-amyloid therapy). No cross-domain generalization.
- **Reference resolvability is sampled** (7–12 refs/paper), so the observed rate is an estimate, not exhaustive.
- **The declared-vs-observed gap conflates two quantities** (compile-time DOI capture vs true verifiability); the anchored-tier metric must be redefined before scores are comparable across differently-compiled papers.
- **Registry evidence is effectively one data point** — only two papers had a registry, and both are NCT04437511.
- **Novelty `cannot_determine` is ~23%**; absence of a PubMed hit is weak evidence for narrow subgroup/derived claims.
- **Retraction check was not exhaustive** — it covered each paper plus its most-cited references, not the full citation tail.

## 6. Next step

The single thing this experiment could not do is the one that matters most for funders: prove the tiers separate trustworthy work from untrustworthy work. That requires a **labelled contrast set** the all-legitimate AD corpus lacks. Concretely: assemble a set of **retracted and corrected Alzheimer's papers** (PubMed's Retraction-of-Publication type, plus known fabricated-reference and expert-flagged cases) and a **matched good set** of comparable-topic, comparable-vintage papers with clean records, then re-run these same anchored/judged passes blind and test whether the observed-vs-declared reference gap, the retraction check, the registry-concordance join, and the novelty verdicts actually discriminate the known-bad from the matched-good. Only that closes the gap between "the tiers compute against external truth" (shown here) and "the tiers measure trustworthiness" (still open).

---

*Grounding: per-ARA evidence in `research/metrics/v4-gro/external/*.json`; synthesis in `research/metrics/v4-gro/external_validation.json`. Tier framing and limitation language from `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md` §1, §7. Parent deterministic-tier result and its negative finding from `research/metrics/v4-gro/EXPERIMENT_PAPER.md`. All PubMed and ClinicalTrials.gov lookups were live MCP calls; all result adjudication was LLM-mediated. This is a partial s7.1 run over six legitimate Alzheimer's ARAs; it validates external computability, not good-vs-bad discrimination.*
