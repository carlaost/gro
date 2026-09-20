# Experiments

## E01: Anchored-tier reference resolution against live PubMed

**Verifies**: C01, C02

**Setup**: Six ARAs (`zim25`, `jes26`, `che26`, `val25`, `han26`, `tit26`). For each, 7–12
DOI-anchored references were sampled from its `gro/refs.yaml`.

**Procedure**: Each sampled reference was resolved live against PubMed (MCP `search_articles`,
`get_article_metadata`), and the returned title/authors were checked against the cited work to
produce an *observed* resolvability verdict. This was compared against the sidecar's own
self-declared `resolvable` field (the *declared* rate) for the same paper.

**Expected outcome (directional)**: If Tier B computes correctly against the outside world,
observed resolvability should be high across a corpus of legitimate, indexed papers. Any gap
between the observed and declared rates would indicate the sidecar field measures something other
than true external verifiability (e.g., an artifact of the compilation input rather than of the
reference itself).

## E02: Judged-tier novelty verdicts against PubMed prior art

**Verifies**: C03, C04

**Setup**: Same six-ARA corpus. Headline claims were drawn from each ARA's
`gro/claims_typed.yaml`.

**Procedure**: For each headline claim, PubMed was searched for prior art (assay names, method
terms, generic equivalents), and a verdict of `novel`, `incremental`, `previously_reported`, or
`cannot_determine` was assigned based on what the search returned.

**Expected outcome (directional)**: If Tier C is genuine differentiating signal rather than
self-report, verdicts should vary meaningfully across papers with different degrees of actual
novelty — e.g., a first-in-literature method should skew toward `novel`, and a reimplementation or
restatement of an existing result should skew toward `previously_reported`/`incremental`.

## E03: Trial-registry concordance join (ClinicalTrials.gov)

**Verifies**: C05

**Setup**: The two donanemab trial papers in the corpus (`zim25`, `jes26`).

**Procedure**: Each paper's trial identifier was resolved on ClinicalTrials.gov (MCP
`search_trials`, `get_trial_details`); each paper's reported claims were then joined to the
registered outcome measures and classified as `matches_registered`, `added_post_hoc`, or
`dropped`.

**Expected outcome (directional)**: A correctly behaving registry-concordance check should
reproduce registered primary endpoints as matches, surface any reported-but-unregistered analyses
as a flagged concordance gap, and distinguish transparently disclosed post-hoc exploration from
concealed outcome switching rather than treating the two the same way.

## E04: Retraction/correction search

**Verifies**: C06

**Setup**: All six ARAs' own papers plus their most-cited references.

**Procedure**: Retraction/correction status was searched for each paper and its most-cited
references via PubMed.

**Expected outcome (directional)**: On a corpus of legitimate, non-retracted papers, this check
should return no retractions; a spuriously broad or malformed query should be recognizable as a
query-construction artifact rather than reported as a finding.
