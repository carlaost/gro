# Historical validation — STRENGTHENED (full text, dual-model, downstream-citation ground truth)

Corpus: 35/72 historical AD papers (2004-2010) with full text; 27 with >=10 mature citers.
Split: LOW=20 MID=8 HIGH=7 (real impact spread).
Predictor: max(peak,cwmean) contribution-typing from FULL TEXT, by Claude AND GPT-5.5 (dual-model).
Ground truth (LLM-free): downstream citations -> Funk-Owen-Smith disruption mDI (breakthrough),
consolidation (-mDI, convergence), and raw citation count (impact).

BREAKTHROUGH (metric vs mature disruption mDI):
  Claude-FT    rho = -0.27   95% CI [-0.59, +0.14]
  GPT-FT       rho = -0.17
  Consensus    rho = -0.16   95% CI [-0.57, +0.27]
CONVERGENCE (metric vs consolidation -mDI):  consensus rho = +0.16
IMPACT (metric vs total citations):          consensus rho = +0.19
Dual-model agreement (Claude-FT vs GPT-FT metric): rho = +0.22

Verdict: even with full text (variance decompressed), dual-model typing, real low/mid/high
spread, and an LLM-free downstream-citation ground truth, the publication-time contribution
metric shows NO reliable relationship to which papers disrupted the field. All CIs span zero.
If anything the metric leans very weakly toward consolidation/citation-attention and AWAY from
disruption -- consistent with the metascience finding that disruptive != highly-cited. The two
models' contribution-typing agree only rho~0.22, so there isn't even a stable model-independent
"contribution depth". The abstract-only null (rho~0) was not an artifact; the strengthened test confirms it.
Caveat: n=27, single domain, single vintage.
