# Library metrics — V3

Two-axis (paper_rankers vs artifact_trust), validity+variance gate, K_MIN=3 genre ladder. 12 ARAs.

## Genres (Tier A gold / Tier C deterministic)

- `ahm26b-trends-and-disparities-in-alzheimer-disease` → **observational_epidemiology** [PRIMARY_CLINICAL] (gold); trust w=1.0
- `che26-diagnostic-performance-of-plasma-p-tau217` → **systematic_review_meta_analysis** [SYNTHESIS] (gold); trust w=0.944
- `cum26-alzheimer-s-disease-drug-development-pipeline` → **narrative_review_survey** [SYNTHESIS] (gold); trust w=0.97
- `huu25-apoe-e4-alzheimer-s-risk-converges` → **primary_experimental** [PRIMARY_LAB] (gold); trust w=0.911
- `jes26-efficacy-and-safety-of-donanemab-in` → **randomized_controlled_trial** [PRIMARY_CLINICAL] (gold); trust w=0.974
- `kes25-the-alzheimer-s-disease-diagnosis-and` → **diagnostic_accuracy_study** [PRIMARY_CLINICAL] (gold); trust w=0.883
- `pal25-alzheimer-s-association-clinical-practice-guideline` → **clinical_practice_guideline** [SYNTHESIS] (gold); trust w=0.797
- `sal25-trailblazer-alz-4-a-phase-3` → **randomized_controlled_trial** [PRIMARY_CLINICAL] (gold); trust w=0.992
- `sal26-plasma-emtbr-tau243-and-p-tau217` → **diagnostic_accuracy_study** [PRIMARY_CLINICAL] (gold); trust w=0.944
- `the25-blood-phosphorylated-tau-for-the-diagnosis` → **systematic_review_meta_analysis** [SYNTHESIS] (gold); trust w=0.859
- `tit26-automated-high-throughput-quantification-of-plasma` → **diagnostic_accuracy_study** [PRIMARY_CLINICAL] (gold); trust w=0.917
- `woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms` → **primary_experimental** [PRIMARY_LAB] (gold); trust w=0.673

## RC1 diagnostic — variance AND validity (no bare 'discriminating')

| Paper ranker | n | variance | validity | usable |
|---|---|---|---|---|
| corrective_science_score | 8 | non_discriminating | invalid_fabricated | — |
| negative_result_share | 8 | discriminating | pending_sem | — |
| dead_end_density | 8 | discriminating | invalid_fabricated | — |
| translation_trial_linkage | 8 | discriminating | ref_string_bound | — |
| semantic_grounding | 8 | discriminating | judge_scored | — |
| novel_claim_count | 8 | discriminating | pending_sem | — |

**Usable paper-rankers on this corpus: 0/6.** (Master's predicted honest outcome: 0–1. That is the validity gate working, not a bug.)

## Genre-scoped rankings (K_MIN ladder; no singleton rankings)

### corrective_science_score
- **fine:diagnostic_accuracy_study** (fine): kes25-the-alzheimer-s-disease-diagnosis-and (0.0) > sal26-plasma-emtbr-tau243-and-p-tau217 (0.0) > tit26-automated-high-throughput-quantification-of-plasma (0.0)
- **coarse:SYNTHESIS** (coarse_provisional): che26-diagnostic-performance-of-plasma-p-tau217 (0.0) > cum26-alzheimer-s-disease-drug-development-pipeline (0.0) > pal25-alzheimer-s-association-clinical-practice-guideline (0.0)
- **unranked** (bucket_too_small_to_rank): ['huu25-apoe-e4-alzheimer-s-risk-converges', 'sal25-trailblazer-alz-4-a-phase-3']

### negative_result_share
- **fine:diagnostic_accuracy_study** (fine): tit26-automated-high-throughput-quantification-of-plasma (0.2727) > kes25-the-alzheimer-s-disease-diagnosis-and (0.0) > sal26-plasma-emtbr-tau243-and-p-tau217 (0.0)
- **coarse:SYNTHESIS** (coarse_provisional): che26-diagnostic-performance-of-plasma-p-tau217 (0.125) > cum26-alzheimer-s-disease-drug-development-pipeline (0.0) > pal25-alzheimer-s-association-clinical-practice-guideline (0.0)
- **unranked** (bucket_too_small_to_rank): ['huu25-apoe-e4-alzheimer-s-risk-converges', 'sal25-trailblazer-alz-4-a-phase-3']

### dead_end_density
- **fine:diagnostic_accuracy_study** (fine): tit26-automated-high-throughput-quantification-of-plasma (0.0909) > kes25-the-alzheimer-s-disease-diagnosis-and (0.0) > sal26-plasma-emtbr-tau243-and-p-tau217 (0.0)
- **coarse:SYNTHESIS** (coarse_provisional): che26-diagnostic-performance-of-plasma-p-tau217 (0.0) > cum26-alzheimer-s-disease-drug-development-pipeline (0.0) > pal25-alzheimer-s-association-clinical-practice-guideline (0.0)
- **unranked** (bucket_too_small_to_rank): ['huu25-apoe-e4-alzheimer-s-risk-converges', 'sal25-trailblazer-alz-4-a-phase-3']

### translation_trial_linkage
- **fine:diagnostic_accuracy_study** (fine): sal26-plasma-emtbr-tau243-and-p-tau217 (1.0) > kes25-the-alzheimer-s-disease-diagnosis-and (0.0) > tit26-automated-high-throughput-quantification-of-plasma (0.0)
- **coarse:SYNTHESIS** (coarse_provisional): cum26-alzheimer-s-disease-drug-development-pipeline (8.0) > che26-diagnostic-performance-of-plasma-p-tau217 (0.0) > pal25-alzheimer-s-association-clinical-practice-guideline (0.0)
- **unranked** (bucket_too_small_to_rank): ['huu25-apoe-e4-alzheimer-s-risk-converges', 'sal25-trailblazer-alz-4-a-phase-3']

### semantic_grounding
- **fine:diagnostic_accuracy_study** (fine): tit26-automated-high-throughput-quantification-of-plasma (1.0) > kes25-the-alzheimer-s-disease-diagnosis-and (0.964) > sal26-plasma-emtbr-tau243-and-p-tau217 (0.8)
- **coarse:SYNTHESIS** (coarse_provisional): pal25-alzheimer-s-association-clinical-practice-guideline (1.0) > cum26-alzheimer-s-disease-drug-development-pipeline (0.941) > che26-diagnostic-performance-of-plasma-p-tau217 (0.926)
- **unranked** (bucket_too_small_to_rank): ['huu25-apoe-e4-alzheimer-s-risk-converges', 'sal25-trailblazer-alz-4-a-phase-3']

### novel_claim_count
- **fine:diagnostic_accuracy_study** (fine): sal26-plasma-emtbr-tau243-and-p-tau217 (1.0) > tit26-automated-high-throughput-quantification-of-plasma (1.0) > kes25-the-alzheimer-s-disease-diagnosis-and (0.0)
- **coarse:SYNTHESIS** (coarse_provisional): che26-diagnostic-performance-of-plasma-p-tau217 (0.0) > cum26-alzheimer-s-disease-drug-development-pipeline (0.0) > pal25-alzheimer-s-association-clinical-practice-guideline (0.0)
- **unranked** (bucket_too_small_to_rank): ['huu25-apoe-e4-alzheimer-s-risk-converges', 'sal25-trailblazer-alz-4-a-phase-3']

