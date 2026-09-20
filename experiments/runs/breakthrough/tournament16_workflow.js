export const meta = {
  name: 'breakthrough-metric-16-4-2-1',
  description: '16->4->2->1 critique-carrying tournament: each round sees Fable\'s critiques of all prior proposals; agents optimize on TRAIN only, final scored on held-out TEST by the caller',
  phases: [
    { title: 'Round0 propose', detail: '16 clean-room proposers, each hill-climbs a formula on the train split' },
    { title: 'Cut to 4', detail: 'Fable critiques all 16, advances 4' },
    { title: 'Refine to 4', detail: '4 refine using all critiques' },
    { title: 'Cut to 2', detail: 'Fable critiques 4, advances 2' },
    { title: 'Refine to 2', detail: '2 refine' },
    { title: 'Cut to 1', detail: 'Fable critiques 2, advances 1' },
    { title: 'Final', detail: 'winner does a final critique-driven iteration' },
  ],
}

const CORPUS = '/Users/carlaostmann/code/dasmodel/research/metrics/v5-breakthrough/corpus'
const HARNESS = `${CORPUS}/apply_formula.py`
const FEATURES_DOC = `${CORPUS}/FEATURES.md`
const FIELDS = 'contribution, contrib_peak, contrib_wmean, n_contribs, n_puffery, delta, delta_max, frac_quant_verified, n_deltas, anchor, anchor_mean_overlap, anchor_max_overlap, anchor_n, uptake_per_year, cd_index, year'

const INSIGHTS = `WHAT WE ALREADY LEARNED (build on this, do not rediscover):
- Per-feature Spearman vs the expert panel (train): contribution +0.51, contrib_wmean +0.50, contrib_peak +0.38, n_contribs +0.35 (positive but gameable by padding); delta -0.20, delta_max -0.21, n_deltas -0.32 (these are REPORT TELLS — reports announce many big quantified numbers); anchor(resolution-success) -0.20 and anchor_mean_overlap -0.19 (dense prior art = incremental); uptake_per_year +0.00 and cd_index -0.10 (DEAD on recent papers — do not use).
- The current best metric (baseline to beat) is: 0.6*contrib_wmean + 0.6*contrib_peak - 0.15*delta_max - 0.04*n_deltas  -> train Spearman 0.63.
- KNOWN FAILURE MODES to fix: (1) it has NO positive novelty signal — it infers "not a report" from delta structure but never confirms novelty; anchor_mean_overlap is now fully resolved for the corpus, so LOW overlap = sparse prior art = genuinely novel is a real lever you can finally use (try (1 - anchor_mean_overlap) as a novelty term). (2) It over-scores deep-but-derivative papers (a diagnostic-accuracy study, an incremental ML method) because contribution typing credits their depth. (3) The -0.04*n_deltas penalty is a crude raw count that punishes any thorough empirical paper, not just reports.

CAUSAL SIGNAL vs CONFOUND-PROXY (read carefully — this decides whether your metric generalizes):
Not every feature that correlates negatively with the expert score is a legitimate term to subtract. There are two very different cases:
  (a) TRUE INVERSE CONSTRUCT — e.g. anchor_mean_overlap: novelty literally IS distance from prior art, so (1 - overlap) recovers the real latent variable. Flipping the sign is principled and will generalize.
  (b) CONFOUND PROXY — e.g. n_deltas / delta_max: making many quantified comparisons does NOT make a paper less of a breakthrough. These correlate negatively ONLY because, in THIS corpus, the papers piling up deltas happen to be surveillance/burden reports. Subtracting delta is exploiting a spurious corpus confound; it penalizes a genuine discovery that legitimately reports big numbers (it already misfires on aki26, expert 70, delta_max 1.0) and will break on a corpus where breakthroughs also carry deltas.
PREFER causal signals (positive novelty from low prior-art overlap; contribution DEPTH) over sign-flipped proxies. If the real thing you want is "is this a surveillance/report genre," detect GENRE DIRECTLY rather than via a delta-count proxy: GRO emits genre.yaml, but it is inconsistently schematised across papers (some have genre.primary + novelty_prior, most only paper_type) — so it is NOT yet a clean feature. If you want it, propose a normalized genre field in proposed_extensions and explain how you'd condition on it. Do not launder a genre confound through the delta terms.`

const RULES = `HARD RULES:
- FIRST read ${FEATURES_DOC} — it defines every feature, what it MEANS, and crucially its PROVENANCE (compiled from the paper by the LLM, vs resolved against prior-art, vs from the follow-on citation graph). Understand what you are combining.
- You do NOT have to use all features. A good metric uses only the few that carry signal. Report exactly which you used in features_used. Padding with weak features hurts generalization.
- Your formula is a single pure Python arithmetic expression over a dict r with ONLY these keys: ${FIELDS}. Guard every field with (r['x'] or 0). You may use +,-,*,/,min(),max(),abs() and parentheses. No other names.
- If you conclude the substrate is MISSING a signal you'd need for the ideal metric (e.g. a downstream replication/refutation edge, a cross-paper credit graph, review sentiment), do NOT force a worse formula around the gap — still give your best formula from what exists, AND record the missing piece in proposed_extensions (a concrete new GRO sidecar/field, what it captures, why it's needed). This is valued output, not a failure.
- SCORE IT YOURSELF on the training split before returning. Run exactly:
    python3 ${HARNESS} "YOUR_FORMULA" --split train
  Read the line "Spearman(new vs expert) = X.XXX". That X is your train_rho. Iterate a few times to improve it.
- NEVER use --split test or --split all. The test set is held out and evaluated once by the organizer. Optimizing on anything but train is disqualifying and self-defeating.
- Prefer FEWER terms. A 3-4 term formula that reaches 0.60 generalizes better than an 8-term one that reaches 0.66 by overfitting 41 points. Interpretability is graded.`

const PROPOSAL_SCHEMA = {
  type: 'object',
  required: ['name', 'formula', 'train_rho', 'rationale', 'n_terms', 'features_used'],
  properties: {
    name: { type: 'string', description: 'short distinctive name' },
    formula: { type: 'string', description: 'pure None-guarded Python arithmetic over dict r' },
    train_rho: { type: 'number', description: 'the Spearman you measured on --split train' },
    n_terms: { type: 'integer' },
    features_used: { type: 'array', items: { type: 'string' },
      description: 'ONLY the features your formula actually uses — you are NOT required to use all of them' },
    rationale: { type: 'string' },
    proposed_extensions: { type: 'array',
      description: 'OPTIONAL. If the ideal metric needs a signal the substrate does not currently emit, propose it here instead of forcing a worse formula. Empty if none.',
      items: { type: 'object', required: ['sidecar_or_field', 'what_it_would_capture', 'why_needed'],
        properties: {
          sidecar_or_field: { type: 'string', description: 'proposed new GRO sidecar or field name' },
          what_it_would_capture: { type: 'string' },
          why_needed: { type: 'string', description: 'what breakthrough signal is currently uncomputable without it' },
        } } },
  },
}
const CRITIQUE_SCHEMA = {
  type: 'object',
  required: ['advance', 'critiques'],
  properties: {
    advance: { type: 'array', items: { type: 'string' }, description: 'names advancing to next round' },
    critiques: { type: 'array', items: { type: 'object', required: ['name', 'verdict'],
      properties: { name: { type: 'string' },
        verdict: { type: 'string', description: 'what is strong, what is weak/overfit-risk, and one concrete improvement' } } } },
    overall: { type: 'string', description: 'cross-cutting guidance for the next round' },
  },
}

// 16 distinct design angles so proposers don't collapse to duplicates
const ANGLES = [
  'novelty-first: make (1 - anchor_mean_overlap) the primary term; sparse prior art = breakthrough',
  'depth-first: importance-weighted contribution depth is the core; minimal penalties',
  'report-suppressor: aggressively subtract report tells (delta_max, n_deltas normalized) from a depth core',
  'multiplicative: multiply a depth term by a novelty term so a paper must be BOTH deep AND novel',
  'peak-driven: one landmark contribution (contrib_peak) dominates; breadth ignored',
  'anti-padding: reward contrib_wmean, explicitly punish n_contribs breadth and n_puffery',
  'novelty x depth interaction with a small verified-delta bonus (frac_quant_verified)',
  'min-gate: score = min(depth, novelty) so a paper cannot win on one axis alone',
  'ratio: depth divided by (1 + report-tell count) to normalize the delta penalty',
  'anchor-neighborhood: use anchor_n and anchor_max_overlap to detect first-in-field (few, low-overlap neighbors)',
  'contribution-quality only: contribution + contrib_wmean, no delta/anchor at all (control arm)',
  'sparse-novelty + peak: (1-anchor_mean_overlap) blended with contrib_peak, light report penalty',
  'capped report-tell: subtract min(n_deltas, cap) so thorough empirical papers are not overpunished',
  'three-signal balanced: depth + novelty-density - report-tell, each ~equal weight',
  'harmonic: harmonic mean of depth and novelty to reward balance and punish imbalance',
  'nonlinear novelty: reward strongly when anchor_mean_overlap is very low, flat otherwise (use max)',
]

phase('Round0 propose')
log('16 clean-room proposers hill-climbing on the train split')
const round0 = (await parallel(ANGLES.map((angle, i) => () =>
  agent(
    `You are breakthrough-metric designer #${i + 1}. Design a formula that ranks recent papers by breakthrough-ness to match a blind expert panel, on the GRO feature data.\n\nGrounding: read ${CORPUS}/corpus_scored.md (the papers + features) and ${CORPUS}/metric_vs_expert.json (current failure).\n\nYOUR ASSIGNED ANGLE (make your design genuinely explore this, so the 16 proposals differ): ${angle}\n\n${INSIGHTS}\n\n${RULES}\n\nReturn your best formula, its measured train_rho, term count, and rationale.`,
    { label: `propose#${i + 1}`, phase: 'Round0 propose', schema: PROPOSAL_SCHEMA, agentType: 'general-purpose', model: 'sonnet' }
  )
))).filter(Boolean)

phase('Cut to 4')
const cutA = await agent(
  `You are the Fable judge. 16 proposers submitted breakthrough-metric formulas with self-measured train Spearman (JSON below). Advance the 4 strongest. Judge on: measured train_rho, BUT discount likely overfitting (many terms, suspiciously high rho, brittle constructions); reward interpretability, a genuine positive novelty signal (not just report-suppression), and diversity of approach among the 4. Write a concrete critique of each of the 16 (strength, weakness/overfit-risk, one improvement) — these are passed to the next round.\n\n${JSON.stringify(round0, null, 2)}`,
  { label: 'cut:16->4', phase: 'Cut to 4', schema: CRITIQUE_SCHEMA, model: 'fable' }
)
const four = round0.filter(p => (cutA.advance || []).includes(p.name)).slice(0, 4)

phase('Refine to 4')
const refined4 = (await parallel(four.map(p => () =>
  agent(
    `You designed "${p.name}", advancing in the tournament. Refine it into a stronger, still-interpretable formula.\n\nHere are ALL 16 round-0 proposals so you can graft the best ideas:\n${JSON.stringify(round0, null, 2)}\n\nFable's critiques (address yours, and steal what worked elsewhere):\n${JSON.stringify(cutA.critiques, null, 2)}\nFable's overall guidance: ${cutA.overall}\n\n${INSIGHTS}\n\n${RULES}\n\nReturn the improved proposal with its new measured train_rho.`,
    { label: `refine4:${p.name.slice(0, 12)}`, phase: 'Refine to 4', schema: PROPOSAL_SCHEMA, agentType: 'general-purpose', model: 'sonnet' }
  )
))).filter(Boolean)

phase('Cut to 2')
const cutB = await agent(
  `You are the Fable judge. Four refined breakthrough-metric formulas (JSON). Advance the 2 strongest, same criteria (train_rho discounted for overfit-risk; reward interpretability + a real novelty signal). Critique each with one concrete improvement for the next round.\n\n${JSON.stringify(refined4, null, 2)}`,
  { label: 'cut:4->2', phase: 'Cut to 2', schema: CRITIQUE_SCHEMA, model: 'fable' }
)
const two = refined4.filter(p => (cutB.advance || []).includes(p.name)).slice(0, 2)

phase('Refine to 2')
const refined2 = (await parallel(two.map(p => () =>
  agent(
    `You designed "${p.name}", one of the final two. Refine once more.\n\nThe other finalist and Fable's critiques:\n${JSON.stringify(refined4, null, 2)}\nCritiques: ${JSON.stringify(cutB.critiques, null, 2)}\nOverall: ${cutB.overall}\n\n${INSIGHTS}\n\n${RULES}\n\nReturn the improved proposal with measured train_rho.`,
    { label: `refine2:${p.name.slice(0, 12)}`, phase: 'Refine to 2', schema: PROPOSAL_SCHEMA, agentType: 'general-purpose', model: 'sonnet' }
  )
))).filter(Boolean)

phase('Cut to 1')
const cutC = await agent(
  `You are the Fable judge. Two finalist breakthrough-metric formulas (JSON). Pick ONE winner. Prefer the one that will GENERALIZE (interpretable, real novelty signal, not overfit), not merely the higher train_rho. Give the winner one final concrete improvement instruction.\n\n${JSON.stringify(refined2, null, 2)}`,
  { label: 'cut:2->1', phase: 'Cut to 1', schema: CRITIQUE_SCHEMA, model: 'fable' }
)
const winnerName = (cutC.advance || [])[0]
const winner = refined2.find(p => p.name === winnerName) || refined2[0]

phase('Final')
const final = await agent(
  `You are the winning designer of "${winner?.name}". Produce the FINAL breakthrough metric. Apply Fable's last instruction: ${JSON.stringify(cutC.critiques)} / overall: ${cutC.overall}\n\nYour current formula: ${winner?.formula} (train_rho ${winner?.train_rho}).\n\n${INSIGHTS}\n\n${RULES}\n\nReturn the final formula, its measured train_rho, term count, and a rationale covering: which features it uses and why, how it defeats the report-Goodhart hole, whether it has a positive novelty signal, and the honest overfitting risk.`,
  { label: 'final', phase: 'Final', schema: PROPOSAL_SCHEMA, agentType: 'general-purpose', model: 'sonnet' }
)

return {
  baseline: { formula: "0.6*contrib_wmean + 0.6*contrib_peak - 0.15*delta_max - 0.04*n_deltas", train_rho: 0.631, test_rho: 0.600 },
  round0, cutA, refined4, cutB, refined2, cutC, final,
  winner_formula: final?.formula,
}
