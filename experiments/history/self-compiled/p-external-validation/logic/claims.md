# Claims

## C01: Anchored-tier reference resolution computes against live PubMed records
- **Statement**: Of 67 references sampled across six ARAs, 64 resolved to matching PubMed records
  when checked live via MCP calls (pooled observed rate 0.955; unweighted per-ARA mean 0.958),
  demonstrating that the anchored tier's external-resolution operation executes against real
  external infrastructure rather than only against self-declared sidecar fields.
- **Status**: supported
- **Falsification criteria**: Would be refuted if a re-run of the same sampled references against
  PubMed returned materially fewer matches (e.g., pooled rate collapsing toward the corpus's
  self-declared mean of ~0.52), or if the "matches" were found on inspection to be adjudicated
  incorrectly (false positive title/author matches).
- **Proof**: [E01]
- **Evidence basis**: §3.1 of the paper; per-ARA table of sampled/resolved/observed/declared rates.
- **Dependencies**: none
- **Sources**:
  - `67 sampled references, 64 matched, pooled 0.955` ← §3.1 «All 67 sampled references were resolved live; **64 matched PubMed records (pooled observed rate 0.955; unweighted per-ARA mean 0.958)**.» [result]
  - `per-ARA observed rates (1.00/1.00/1.00/0.75/1.00/1.00)` ← §3.1 table «zim25 | 12/12 | 1.00 | 0.957 ... val25 | 9/12 | 0.75 | 0.00 ... tit26 | 7/7 | 1.00 | 0.132» [result]
- **Tags**: anchored-tier, external-computability, reference-resolution, pubmed

## C02: The sidecar's self-declared resolvability field measures compile-time DOI capture, not true external verifiability
- **Statement**: The unweighted mean self-declared `resolvable` rate across the six ARAs (0.520)
  is far below the observed live-resolution rate (0.958); the gap is concentrated in `val25`
  (declared 0.00, observed 0.75), `han26` (declared 0.19, observed 1.00), and `tit26` (declared
  0.132, observed 1.00) — papers whose compiled input lacked a captured bibliography with DOIs,
  even though PubMed resolved the same citations from raw citation text.
- **Status**: supported
- **Falsification criteria**: Would be refuted if the declared field tracked the observed rate
  once compilation-input differences were controlled for, i.e. if papers compiled from the same
  input type showed no declared/observed gap; or if `val25`'s three unresolved references turned
  out to indicate a genuine resolvability problem rather than a PubMed-search miss.
- **Proof**: [E01]
- **Evidence basis**: §3.1, including the worked `val25` example (Jack 2024, Palmqvist 2020,
  Dubois 2024 exact matches from bare citation text despite a 0% declared rate).
- **Dependencies**: [C01]
- **Sources**:
  - `mean declared 0.520 vs observed 0.958` ← §3.1 «The unweighted mean self-declared rate across the six ARAs was **0.520** — far below the 0.958 observed» [result]
  - `val25 declared 0%, resolved 9/12 via bare citation text` ← §3.1 «`val25`'s `refs.yaml` marks all 55 references unresolvable (0%), but searching PubMed on the bare citation text resolved 9 of 12 sampled, including exact author/journal/year/volume/page matches for well-known papers (Jack 2024 *Alzheimers Dement*, Palmqvist 2020 *JAMA*, Dubois 2024 *JAMA Neurol*).» [result]
  - `the metric conflates two quantities` ← §3.1 «the sidecar's `resolvable` field measures compilation-time DOI capture, not true external verifiability. The two quantities are being conflated under one name.» [result]
- **Tags**: anchored-tier, metric-definition-gap, reference-resolution, measurement-validity

## C03: Judged-tier novelty verdicts span the full spectrum and differentiate the corpus
- **Statement**: Across 31 headline claims checked against PubMed prior art, verdicts distributed
  as 10 novel (32%), 10 incremental (32%), 7 cannot_determine (23%), and 4 previously_reported
  (13%) — genuine spread rather than uniform self-report.
- **Status**: supported
- **Falsification criteria**: Would be refuted if re-running the same prior-art searches produced
  a near-uniform verdict (e.g., all `novel` or all `cannot_determine`) regardless of each paper's
  actual contribution, indicating the judged tier is not sensitive to real prior-art presence.
- **Proof**: [E02]
- **Evidence basis**: §3.2, novelty-distribution summary.
- **Dependencies**: none
- **Sources**:
  - `31 claims; 10/10/7/4 across four verdict categories` ← §3.2 «Across **31 headline claims** checked against PubMed, verdicts spanned the full spectrum: **10 novel (32%), 10 incremental (32%), 7 cannot_determine (23%), 4 previously_reported (13%)**.» [result]
- **Tags**: judged-tier, novelty, external-computability, differentiation

## C04: The novelty axis separates a first-in-literature preprint from confirmatory/reimplementation papers
- **Statement**: `han26` (VeraBIND Tau, a proprietary first-in-literature functional tau-seeding
  assay) scored 4 of 5 headline claims `novel`, while `tit26` (an automation reimplementation of
  established p-tau217 assays) scored 3 of 5 `previously_reported`, and `val25`'s headline claims
  were found to restate a same-cohort companion paper (PMID 40140622) published roughly 7 months
  earlier by the same author group on the same SNAC-K cohort (n=2148) with the same biomarker
  panel.
- **Status**: supported
- **Falsification criteria**: Would be refuted if closer inspection showed `han26`'s "no prior art"
  result was a search-coverage artifact (i.e., prior art exists but PubMed's index or the search
  terms missed it), or if PMID 40140622 turned out not to share the cohort/panel with `val25`'s
  headline claims.
- **Proof**: [E02]
- **Evidence basis**: §3.2, high-novelty-end and confirmatory-end bullet points.
- **Dependencies**: [C03]
- **Sources**:
  - `han26: 4 of 5 claims novel` ← §3.2 «**High-novelty end:** `han26` — 4 of 5 claims `novel`. VeraBIND Tau is a proprietary, patent-pending functional tau-seeding assay first described in this preprint» [result]
  - `tit26: 3 of 5 previously_reported; val25 restates PMID 40140622` ← §3.2 «**Confirmatory end:** `tit26` — 3 of 5 `previously_reported` (an automation reimplementation of established p-tau217 assays); and `val25`, whose headline claims restate a same-cohort companion *Nature Medicine* paper (PMID 40140622) published ~7 months earlier by the same author group on the same SNAC-K cohort (n=2148) with the same biomarker panel.» [result]
- **Tags**: judged-tier, novelty, case-study, differentiation

## C05: The registry-concordance join correctly flags transparent post-hoc endpoint elevation without mislabeling it as fraud
- **Statement**: Both donanemab papers (`zim25`, `jes26`) resolved to NCT04437511 on
  ClinicalTrials.gov; registered primary endpoints matched in both (`zim25`: CDR-SB change,
  amyloid PET Centiloid reduction; `jes26`: iADRS overall + intermediate-tau, CDR-SB, amyloid PET),
  while several reported analyses in each were classified `added_post_hoc` (e.g. `zim25`'s
  CDR-Global hazard ratio, pooled amyloid-reaccumulation model, AUC/time-saved analysis; `jes26`'s
  CDR-Global Cox HR, plasma P-tau217, derived time-saved/no-progression metrics, LTE-vs-ADNI
  comparison) and other registered endpoints were classified `dropped` (e.g. tau PET, vMRI, PK,
  anti-drug antibodies for `zim25`; ADAS-Cog13, MMSE, ADCS-iADL, tau PET, vMRI, PK, immunogenicity
  for `jes26`). Zero instances of concealed outcome switching were found in either paper.
- **Status**: supported
- **Falsification criteria**: Would be refuted if either paper's post-hoc analyses turned out to
  be undisclosed in the paper text (i.e., actually concealed rather than transparently flagged as
  uncontrolled for multiplicity), or if the registered-endpoint matches were found to be
  misclassified on inspection of the registry record.
- **Proof**: [E03]
- **Evidence basis**: §3.3, per-paper concordance-gap description.
- **Dependencies**: none
- **Sources**:
  - `both resolve to NCT04437511; no concealed outcome switching` ← §3.3 «Both trial papers resolved to **NCT04437511** on ClinicalTrials.gov, and their claims joined to the registered outcomes. **No concealed outcome switching was found in either.**» [result]
  - `zim25 added post-hoc / dropped endpoints` ← §3.3 «several reported analyses were **added post-hoc** (CDR-Global hazard ratio, pooled amyloid-reaccumulation model, AUC/time-saved), and registered endpoints (tau PET, vMRI, PK, anti-drug antibodies) were **dropped**.» [result]
  - `jes26 added post-hoc / dropped endpoints` ← §3.3 «CDR-Global Cox HR, plasma P-tau217, derived time-saved/no-progression metrics, and an LTE-vs-ADNI external-control comparison were **added post-hoc**; ADAS-Cog13, MMSE, ADCS-iADL, tau PET, vMRI, PK, and immunogenicity were **dropped**.» [result]
- **Tags**: judged-tier, registry-concordance, clinicaltrials-gov, differentiation

## C06: Zero retractions or corrections were found across the corpus
- **Statement**: Retraction/correction searches on all six papers and their most-cited references
  returned no matches; one unconstrained broad query that returned 1007 spurious hits was
  identified as a query-construction artifact and discarded, not counted as evidence.
- **Status**: supported
- **Falsification criteria**: Would be refuted if a subsequent, more exhaustive retraction search
  (covering the full reference list rather than only the most-cited references) surfaced a
  retraction or correction on any of the six papers or their citations.
- **Proof**: [E04]
- **Evidence basis**: §3.4.
- **Dependencies**: none
- **Sources**:
  - `zero retractions found; 1007-hit query discarded as artifact` ← §3.4 «**Zero.** Retraction/correction searches on all six papers and their most-cited references returned nothing. (One unconstrained broad query returned 1007 spurious hits from PubMed boolean OR-scoping and was discarded as a query-construction artifact, not evidence.)» [result]
- **Tags**: judged-tier, retraction-check, external-computability

## C07: This corpus validates external computability but cannot demonstrate good-versus-bad discrimination
- **Statement**: Because the six-ARA corpus contains zero retracted, fabricated-reference, or
  expert-flagged-defective papers — a fact established directly by C05 (no concealed outcome
  switching) and C06 (zero retractions) plus the near-total reference resolvability of C01 — the
  observed cross-paper variance on novelty and reference-compilation axes reflects differences
  among papers that are all essentially legitimate science, not a demonstrated separation of
  trustworthy from untrustworthy work; the paper concludes a labelled contrast set of known-bad vs
  matched-good papers is required to test discrimination.
- **Status**: hypothesis
- **Falsification criteria**: This is itself a limitation claim about what the experiment could
  not show; it would be undermined if it could be shown that the corpus in fact contained a
  known-bad paper the checks failed to flag, or supported/resolved only by running the proposed
  labelled-contrast-set experiment (§6) and observing whether the same checks then separate
  known-bad from matched-good papers.
- **Proof**: [E01, E02, E03, E04]
- **Evidence basis**: §4 ("The honest conclusion on discrimination") and §6 ("Next step").
- **Dependencies**: [C01, C05, C06]
- **Sources**:
  - `corpus is all essentially legitimate; zero retractions, near-total resolvability, no concealed switching` ← §4 «Every paper here is essentially legitimate: zero retractions, near-total reference resolvability, no concealed outcome switching. The "differentiation" observed is *variance on quality and novelty axes among papers that are all real science*.» [result]
  - `it did not test whether the tiers separate good from bad` ← §4 «It confirmed the tiers *can reach* external truth; it did not test whether they *separate* good from bad, because there was no bad in the sample.» [result]
  - `next step requires a labelled contrast set` ← §6 «That requires a **labelled contrast set** the all-legitimate AD corpus lacks. Concretely: assemble a set of **retracted and corrected Alzheimer's papers** ... and a **matched good set** ... then re-run these same anchored/judged passes blind and test whether ... [they] actually discriminate the known-bad from the matched-good.» [result]
- **Tags**: discrimination-limit, corpus-composition, honest-limitation, next-step

## C08: External-tier adjudication is LLM-mediated, not fully deterministic, outside the L3 matcher
- **Statement**: While the MCP calls to PubMed and ClinicalTrials.gov are real and deterministic
  retrieval operations, the adjudication of their results — whether a returned PubMed title
  "matches" a citation, whether a claim has prior art, whether a reported endpoint "matches" a
  registered one — is performed by LLM judgement over the tool outputs; per the spec (§7),
  independence in this framework means pipeline-independence ("necessary not sufficient")
  everywhere except the L3 non-LLM matcher, which this experiment did not exercise.
- **Status**: supported
- **Falsification criteria**: Would be refuted if the title-match/prior-art/endpoint-match
  adjudications used in this experiment were shown to have been produced by a deterministic
  rule-based matcher rather than an LLM judgement call, or if the L3 non-LLM matcher had in fact
  been exercised in this experiment's pipeline.
- **Proof**: [E01, E02, E03]
- **Evidence basis**: §4, final paragraph.
- **Dependencies**: none
- **Sources**:
  - `MCP calls real and deterministic; adjudication is not` ← §4 «The MCP calls are real and deterministic; the *adjudication* of their results is not.» [result]
  - `independence means pipeline-independence except L3 matcher, not exercised here` ← §4 «Per the spec (§7), independence is pipeline-independence, "necessary not sufficient," everywhere except L3's non-LLM matcher, which was not exercised here.» [result]
- **Tags**: methodology, llm-mediation, independence-limit
