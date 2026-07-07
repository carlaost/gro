# Problem Specification

> Grounding: full-text, self-authored paper (`research/metrics/v4-gro/COMPARISON_PAPER.md`). Observations and gaps below are drawn from the paper's Setup (§1), Synthesis (§6), and Limitations (§7) sections.

## Observations

### O01: Three ARA-evaluation approaches exist at three different rigor tiers
- **Statement**: GRO ideal metrics (deterministic + reliable-anchored + reproducible-judged), the v3 ARA-inferred metric design (extractive_fidelity, paper_rankers, artifact_trust), and the Seal Level 2 semantic verifier (D1-D6) occupy three distinct "rigor tiers" — Tier A deterministic, Tier B reliable-anchored, Tier C reproducible-judged/semantic.
- **Evidence**: §1.2-1.3, tier table.
- **Implication**: No prior work had run all three side by side on the same corpus to see whether they agree, disagree, or measure different things.

### O02: The corpus splits into a fully-anchored half and a deterministic-only half
- **Statement**: Of the 12-ARA corpus, only 6 (the biomarker + trial cluster: che26, val25, han26, zim25, jes26, tit26) carry any externally anchored or judged-tier evidence; the other 6 (biology/epidemiology/pipeline cluster: gau25, zho25, aki26, cum26, xu25, ard25) are assessed on deterministic-tier metrics only.
- **Evidence**: §1.1.
- **Implication**: Any claim about Tier B/C metric reliability is only demonstrated on half the corpus, in one clinical/biomarker sub-domain.

### O03: The GRO extension's four newly-computable metrics have no prose analog
- **Statement**: claim-typing, entity-anchoring, over-claim, and genre-completeness metrics require a typed field that raw ARA prose does not have.
- **Evidence**: §2.1.
- **Implication**: The typed-graph substrate is not merely a faster restatement of the prose — it expands what is measurable at all.

### O04: Typing the four shared metrics changes their values, sometimes away from ground truth
- **Statement**: Reference resolvability computed on typed fields is farther from PubMed-observed truth (MAE 0.44) than the same metric computed on raw prose (MAE 0.31).
- **Evidence**: §2.1.
- **Implication**: An LLM-driven typing/extraction pass is itself a source of measurement drift, not a strictly more faithful representation of the source.

### O05: GRO and v3 (both structural instruments) rank ARAs similarly; Seal (semantic) does not track either
- **Statement**: Spearman rho(GRO, v3) = 0.678 (p = 0.015) vs rho(Seal, GRO) = −0.011 (p = 0.974) and rho(Seal, v3) = 0.035 (p = 0.913).
- **Evidence**: §4.4.
- **Implication**: Structural completeness and semantic quality are empirically distinct constructs on this corpus — not two measurements of the same underlying "goodness."

### O06: The corpus contains zero known-bad papers
- **Statement**: 0 retractions, no concealed outcome-switching, and all references are ultimately real across all 12 ARAs.
- **Evidence**: §7, Limitation 1.
- **Implication**: High reliability scores on `retractions` and reference resolution reflect a floor/ceiling effect on a uniformly legitimate corpus, not proof any instrument would correctly flag a fabricated or retracted paper.

### O07: Each instrument catches real defects invisible to the other two
- **Statement**: v3 alone catches che26's fabricated forest-plot statistic; GRO alone catches val25's 0%-resolvable bibliography; Seal alone catches che26's cross-ethnic overgeneralization and zim25's sponsor-only-authorship conflict of interest.
- **Evidence**: §4.5 (divergence table), §6.
- **Implication**: A credible ARA-evaluation pipeline needs all three tiers; none is a valid proxy for the others.

### O08: Known formula/construct defects remain unfixed in the reported numbers
- **Statement**: `genre_silent_omissions` can go negative (zho25 = −1); `broken_ref_integrity` conflates a missing ledger file with a genuinely broken citation (ard25); `reference_resolvability_rate` measures DOI-capture, not verifiability.
- **Evidence**: §7, Limitation 5; §3.3.
- **Implication**: The paper reports these defects as-is for honesty rather than silently correcting them, which matters for anyone reusing the raw metric numbers.

## Gaps

### G01: No external good-vs-bad ground-truth set exists for this corpus
- **Statement**: With zero known-bad papers in the 12-ARA corpus, no instrument's reliability on `retractions` or external ref-resolution has been tested against an actual fabricated or retracted paper.
- **Caused by**: O06.
- **Existing attempts**: GRO's own external validation explicitly states this "validates external computability and surfaces concordance/compilation gaps, but it is NOT a full good-vs-bad discrimination test."
- **Why they fail**: The corpus was compiled from published, non-retracted papers by design; discrimination power cannot be demonstrated without deliberately including known-bad exemplars.

### G02: Anchored/judged-tier evidence covers only half the corpus, in one sub-domain
- **Statement**: All Tier-B/Tier-C metric evidence (retractions, external ref-resolution, novelty verdict, trial-registry concordance) comes from the 6-ARA p-tau217/donanemab cluster only.
- **Caused by**: O02.
- **Existing attempts**: The trial-registry concordance check was run on the 2 available trial papers.
- **Why they fail**: Only 2 trial papers exist in the corpus, and both analyze the exact same trial (NCT04437511) — "registry-concordance evidence is effectively a single data point," per the paper's own source file.

### G03: LLM-authored extensions (Seal L2, GRO's judged-tier metrics, v3) carry unvalidated uncertainty
- **Statement**: Seal L2 is an LLM semantic reviewer; GRO's novelty verdicts are LLM judgments over PubMed searches that are phrasing-dependent (22.6% land in `cannot_determine`); `overclaim_flags` is scored over LLM-typed fields. None has an independent human adjudicator in this study.
- **Caused by**: O01, O07.
- **Existing attempts**: None reported — the paper flags this as an open limitation rather than something it has already resolved.
- **Why they fail**: There is no human-expert-consensus baseline in the study design to validate any Tier-C signal against.

### G04: Small, single-domain sample size limits the correlation findings' generality
- **Statement**: n = 12 (n = 11 excluding ard25) is a small sample for Spearman correlation estimates; confidence intervals are wide.
- **Caused by**: The fixed 12-ARA corpus, all Alzheimer's/neurodegeneration, split 6/6 across two clusters.
- **Existing attempts**: The paper reports the correlation both with and without ard25 to check robustness of the near-zero Seal-vs-structural result.
- **Why they fail**: The near-zero result should be read as "no detectable positive relationship in this sample," not "proven independence" — a stronger claim would require a larger, multi-domain corpus.

### G05: No single instrument, alone, has been shown to discriminate good science from bad science
- **Statement**: Each of the three approaches catches real defects the other two are structurally blind to, but none has demonstrated it can separate good from bad science unaided, on this corpus.
- **Caused by**: O06, O07.
- **Existing attempts**: The paper's synthesis (§6) argues for running Tier A/B before Tier C as a pipeline rather than substituting one tier for another.
- **Why they fail**: Without known-bad exemplars (G01), no instrument's discrimination claim can be empirically tested end-to-end.

## Key Insight
- **Insight**: A credible ARA-evaluation pipeline needs a deterministic structural floor (Tier A), an externally anchored middle (Tier B), and a judged semantic ceiling (Tier C) run together — because the three tiers are empirically near-orthogonal (measure different constructs) and each catches real defects invisible to the other two.
- **Derived from**: O01, O05, O07.
- **Enables**: A layered ARA-review protocol: reject the structurally broken cheaply via Tier A/B gates, then spend the expensive Tier C semantic review only on artifacts that clear the floor.

## Assumptions
- A1: The 12-ARA corpus (all Alzheimer's/neurodegeneration) is representative enough of GRO-typed ARAs generally to support the paper's tier-orthogonality conclusion, though the paper itself flags this as unproven beyond this domain (G04).
- A2: GRO's own reliability ranking of its metrics (§3) is trustworthy self-assessment, not independently audited by a fourth party.
- A3: The 6/6 cluster split (biomarker+trial vs biology/epidemiology/pipeline) is the natural and only relevant stratification for reading the anchored/judged-tier results.
