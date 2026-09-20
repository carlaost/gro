# V2 → V3 comparison (acceptance criteria)

Each row is a round-2 acceptance criterion (critiques-round2.md) checked against the V2 number and the V3 number. `pending` = a module/LLM/MCP pass that degraded gracefully.

## RC3 — fabricated dead-ends stripped

| ARA | V2 dead_end_density | V3 dead_end_density | V3 synthetic excluded |
|---|---|---|---|
| ahm26b-trends-and-disparities-in-alzheimer-disease | 0.0 | 0.0 | 0 |
| che26-diagnostic-performance-of-plasma-p-tau217 | 0.25 | 0.0 | 2 |
| cum26-alzheimer-s-disease-drug-development-pipeline | 0.0 | 0.0 | 0 |
| huu25-apoe-e4-alzheimer-s-risk-converges | 0.5 | 0.5 | 0 |
| jes26-efficacy-and-safety-of-donanemab-in | 0.0 | 0.2 | 0 |
| kes25-the-alzheimer-s-disease-diagnosis-and | 0.0 | 0.0 | 3 |
| pal25-alzheimer-s-association-clinical-practice-guideline | 0.25 | 0.0 | 2 |
| sal25-trailblazer-alz-4-a-phase-3 | 0.125 | 0.125 | 0 |
| sal26-plasma-emtbr-tau243-and-p-tau217 | 0.25 | 0.0 | 1 |
| the25-blood-phosphorylated-tau-for-the-diagnosis | 0.143 | 0.0 | 1 |
| tit26-automated-high-throughput-quantification-of-plasma | 0.091 | 0.0909 | 0 |
| woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms | 0.0 | 0.125 | 0 |

**Acceptance:** che26 dead_end_density → 0 (all its dead-ends are synthetic).

## RC4 — corrective_science requires an evidence-addressing edge

| ARA | V2 corrective | V3 corrective | V3 corrective edges |
|---|---|---|---|
| ahm26b-trends-and-disparities-in-alzheimer-disease | 0 | 0.0 | 0 |
| che26-diagnostic-performance-of-plasma-p-tau217 | 3 | 0.0 | 0 |
| cum26-alzheimer-s-disease-drug-development-pipeline | 4 | 0.0 | 0 |
| huu25-apoe-e4-alzheimer-s-risk-converges | 4 | 0.0 | 0 |
| jes26-efficacy-and-safety-of-donanemab-in | 12 | 0.0 | 0 |
| kes25-the-alzheimer-s-disease-diagnosis-and | 6 | 0.0 | 0 |
| pal25-alzheimer-s-association-clinical-practice-guideline | 6 | 0.0 | 0 |
| sal25-trailblazer-alz-4-a-phase-3 | 2 | 0.0 | 0 |
| sal26-plasma-emtbr-tau243-and-p-tau217 | 0 | 0.0 | 0 |
| the25-blood-phosphorylated-tau-for-the-diagnosis | 2 | 0.0 | 0 |
| tit26-automated-high-throughput-quantification-of-plasma | 9 | 0.0 | 0 |
| woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms | 2 | 0.0 | 0 |

**Acceptance:** corrective collapses toward ~0 corpus-wide (refutes=0; bounds=baseline).

## RC5 — negative results detected by semantics, not status

| ARA | V2 negative_share | V3 negative_share | V3 n_negative |
|---|---|---|---|
| ahm26b-trends-and-disparities-in-alzheimer-disease | 0.0 | 0.0 | 0 |
| che26-diagnostic-performance-of-plasma-p-tau217 | 0.2 | 0.125 | 1 |
| cum26-alzheimer-s-disease-drug-development-pipeline | 0.0 | 0.0 | 0 |
| huu25-apoe-e4-alzheimer-s-risk-converges | 0.333 | 0.5 | 4 |
| jes26-efficacy-and-safety-of-donanemab-in | 0.0 | 0.2 | 2 |
| kes25-the-alzheimer-s-disease-diagnosis-and | 0.0 | 0.0 | 0 |
| pal25-alzheimer-s-association-clinical-practice-guideline | 0.2 | 0.0 | 0 |
| sal25-trailblazer-alz-4-a-phase-3 | 0.111 | 0.25 | 2 |
| sal26-plasma-emtbr-tau243-and-p-tau217 | 0.2 | 0.0 | 0 |
| the25-blood-phosphorylated-tau-for-the-diagnosis | 0.125 | 0.0 | 0 |
| tit26-automated-high-throughput-quantification-of-plasma | 0.083 | 0.2727 | 3 |
| woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms | 0.0 | 0.375 | 3 |

**Acceptance:** woj25 counts its real null (C04) as negative knowledge.

## RC8 — genre classifier matches gold

| ARA | V2 genre | V3 genre (gold/tierC) |
|---|---|---|
| ahm26b-trends-and-disparities-in-alzheimer-disease | other | observational_epidemiology (gold) |
| che26-diagnostic-performance-of-plasma-p-tau217 | meta_analysis | systematic_review_meta_analysis (gold) |
| cum26-alzheimer-s-disease-drug-development-pipeline | clinical_trial | narrative_review_survey (gold) |
| huu25-apoe-e4-alzheimer-s-risk-converges | single_cell_spatial | primary_experimental (gold) |
| jes26-efficacy-and-safety-of-donanemab-in | clinical_trial | randomized_controlled_trial (gold) |
| kes25-the-alzheimer-s-disease-diagnosis-and | clinical_trial | diagnostic_accuracy_study (gold) |
| pal25-alzheimer-s-association-clinical-practice-guideline | guideline | clinical_practice_guideline (gold) |
| sal25-trailblazer-alz-4-a-phase-3 | clinical_trial | randomized_controlled_trial (gold) |
| sal26-plasma-emtbr-tau243-and-p-tau217 | cohort_study | diagnostic_accuracy_study (gold) |
| the25-blood-phosphorylated-tau-for-the-diagnosis | meta_analysis | systematic_review_meta_analysis (gold) |
| tit26-automated-high-throughput-quantification-of-plasma | assay_method | diagnostic_accuracy_study (gold) |
| woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms | assay_method | primary_experimental (gold) |

**Acceptance:** cum26 → narrative_review_survey (was clinical_trial in V2).

## RC1 — every ranker carries a validity verdict; usable count

- Usable paper-rankers: **0/6** (V2 marked several bare 'discriminating' with no validity check).

## RC10 — homogenization/compiler signals routed off the paper ranking

| ARA | trust w | low-trust? |
|---|---|---|
| ahm26b-trends-and-disparities-in-alzheimer-disease | 1.0 | no |
| che26-diagnostic-performance-of-plasma-p-tau217 | 0.944 | no |
| cum26-alzheimer-s-disease-drug-development-pipeline | 0.97 | no |
| huu25-apoe-e4-alzheimer-s-risk-converges | 0.911 | no |
| jes26-efficacy-and-safety-of-donanemab-in | 0.974 | no |
| kes25-the-alzheimer-s-disease-diagnosis-and | 0.883 | no |
| pal25-alzheimer-s-association-clinical-practice-guideline | 0.797 | no |
| sal25-trailblazer-alz-4-a-phase-3 | 0.992 | no |
| sal26-plasma-emtbr-tau243-and-p-tau217 | 0.944 | no |
| the25-blood-phosphorylated-tau-for-the-diagnosis | 0.859 | no |
| tit26-automated-high-throughput-quantification-of-plasma | 0.917 | no |
| woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms | 0.673 | no |

**Acceptance:** grounding/falsifiability/env now feed w, never a paper rank; two ARAs differing only in environment.md get the same paper rank, different w.
