export const meta = {
  name: 'gro-extend-anchors',
  description: 'Sonnet agents genuinely resolve the SOTA precedence anchors + fill missing delta ledgers so the breakthrough significance signal is real, not a uniform 0.20 penalty',
  phases: [
    { title: 'Resolve L8', detail: 'one Sonnet agent per paper: real sota_anchor from its references + OpenAlex, and any missing delta_ledger', model: 'sonnet' },
  ],
}

const ARALIB = '/Users/carlaostmann/code/dasmodel/research/ara-library'
const TODO = typeof args === 'string' ? JSON.parse(args) : args   // [{slug, fix:[...]}]

const RESULT_SCHEMA = {
  type: 'object',
  required: ['slug', 'wrote', 'anchor_provenance', 'anchor_n_neighbors', 'prior_art_density', 'summary'],
  properties: {
    slug: { type: 'string' },
    wrote: { type: 'array', items: { type: 'string' }, description: 'sidecar files written, e.g. sota_anchor.yaml' },
    anchor_provenance: { type: 'string', description: 'the provenance you set (must NOT be compiler_estimated)' },
    anchor_n_neighbors: { type: 'integer' },
    prior_art_density: { type: 'string', enum: ['dense', 'moderate', 'sparse', 'empty'],
      description: 'honest read of how crowded the prior art is: dense=incremental/update, sparse=near-first-in-field' },
    used_openalex: { type: 'boolean' },
    summary: { type: 'string' },
  },
}

function extendPrompt(slug, fixes) {
  const needAnchor = fixes.some(f => f.startsWith('sota_anchor'))
  const needDelta = fixes.some(f => f.startsWith('delta_ledger'))
  return `You are a GRO substrate resolver. Genuinely resolve the LLM/resolver-dependent L8 sidecar fields for ONE Alzheimer's paper so the breakthrough-significance metric can read a real signal instead of a uniform penalty. Do real resolution — do NOT fabricate and do NOT just relabel an estimate.

PAPER DIR: ${ARALIB}/${slug}
Read first, in this order:
  1. ${ARALIB}/${slug}/PAPER.md  — title, doi, year, abstract, claims_summary.
  2. ${ARALIB}/${slug}/gro/refs.yaml  — the paper's RESOLVED references (R### ids + titles/years). THIS is your primary precedence source.
  3. ${ARALIB}/${slug}/gro/temporal.yaml  — precedence_date / cutoff_date to use.
  4. ${ARALIB}/${slug}/gro/quantities.yaml and gro/external_quantities.yaml and gro/claims_typed.yaml — for the delta ledger.
  5. SCHEMA TEMPLATES to mirror EXACTLY (field names matter — a consumer script parses them):
       - anchor:  ${ARALIB}/20225-2025-alzheimer-s-disease-facts-and/gro/sota_anchor.yaml  (a DENSE neighborhood: an annual update)
       - anchor:  ${ARALIB}/che25e-apoe4-reprograms-microglial-lipid-metabolism-in/gro/sota_anchor.yaml  (a genuine discovery — sparser)
       - deltas:  ${ARALIB}/sal25-trailblazer-alz-4-a-phase-3/gro/delta_ledger.yaml

${needAnchor ? `TASK A — write ${ARALIB}/${slug}/gro/sota_anchor.yaml (a REAL resolver-produced precedence neighborhood):
  - Build the neighborhood from the paper's ACTUAL references in refs.yaml: pick the R### entries that are the paper's SOTA/baseline prior art (the works it advances on, competes with, or updates). For each, give an honest overlap in [0,1] = how much this paper's contribution is already covered by that prior work (0.9+ = it is essentially an update/replication of that work; 0.2 = only loosely related).
  - Set contemporaneous_uncited: true on any near-neighbor the paper should have cited but didn't (use OpenAlex to check — see below); false otherwise.
  - Set overlap_jaccard_second_resolver to a REAL number in [0,1] = your second-pass corroboration of the neighborhood's overlap (a genuine estimate, not a copy).
  - Set precedence_date and cutoff_date from temporal.yaml.
  - Set provenance to 'reference_resolved' (or 'openalex_resolved' if you used the API). It MUST NOT be 'compiler_estimated' and the neighborhood MUST be non-empty UNLESS the paper is genuinely first-in-field with no close prior art (then leave neighborhood: [] and say so — that is an honest sparse result, not a failure to try).
  - The DENSITY of the neighborhood is the signal: a burden-of-disease re-estimate or annual review has a DENSE, high-overlap neighborhood (low novelty); a genuine molecular/clinical discovery has a SPARSE, low-overlap one (high novelty). Get this right — it is the whole point.
  - OPTIONAL but preferred: query OpenAlex for real contemporaneous prior art. The DOI is in PAPER.md. Example: curl -s "https://api.openalex.org/works/doi:<DOI>" to get referenced_works and related_works, and "https://api.openalex.org/works?filter=..." to find close works published before the precedence_date that the paper did NOT cite. If OpenAlex is unreachable, degrade gracefully to refs.yaml-only and set used_openalex=false.
` : 'TASK A — skip (anchor already real).'}

${needDelta ? `TASK B — write ${ARALIB}/${slug}/gro/delta_ledger.yaml (comparative deltas vs OFF-PAPER prior work):
  - One D## per comparative claim where the paper positions a number against prior work. claimed_value = a Q## from quantities.yaml; baseline_value = an XQ## from external_quantities.yaml.
  - delta_status ∈ {quantified, qualitative_only, claimed_unresolved, not_claimed}; baseline_verification ∈ {source_verified, self_reported, unverified}. For quantified+source_verified, compute absolute_delta and relative_delta. Do NOT fabricate a quantified delta where the paper only makes a qualitative comparison — mark it qualitative_only. Penalize-don't-skip: if the paper claims an advance it cannot ground, that is claimed_unresolved (a real, low-scoring outcome), not an omission.
` : 'TASK B — skip (delta ledger already present).'}

Write the file(s) with the Write tool, valid YAML, mirroring the template field names precisely. Then re-read what you wrote to confirm it parses. Return the result object.`
}

phase('Resolve L8')
log(`Resolving L8 for ${TODO.length} papers (Sonnet, real reference+OpenAlex resolution)`)
const results = (await parallel(TODO.map(t => () =>
  agent(extendPrompt(t.slug, t.fix), {
    label: `resolve:${t.slug.slice(0, 16)}`,
    phase: 'Resolve L8',
    schema: RESULT_SCHEMA,
    agentType: 'general-purpose',
    model: 'sonnet',
  })
))).filter(Boolean)

const byDensity = {}
for (const r of results) byDensity[r.prior_art_density] = (byDensity[r.prior_art_density] || 0) + 1
log(`Done: ${results.length}/${TODO.length} resolved. density spread: ${JSON.stringify(byDensity)}`)
return { results, n_requested: TODO.length, n_resolved: results.length, density: byDensity }
