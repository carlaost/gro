export const meta = {
  name: 'breakthrough-expert-panel-sota',
  description: 'SOTA-grounded blind 3-judge panel: each judge sees the paper PLUS a prior-art reading list (titles/years only, no scores) and rates breakthrough-ness = advance beyond that prior art',
  phases: [
    { title: 'SOTA panel', detail: '3 blind judges per paper, grounded in a prior-art brief' },
  ],
}

const ARALIB = '/Users/carlaostmann/code/dasmodel/research/ara-library'
const BRIEFS = '/Users/carlaostmann/code/dasmodel/research/metrics/v5-breakthrough/corpus/briefs'
const SLUGS = typeof args === 'string' ? JSON.parse(args) : args

const JUDGE_SCHEMA = {
  type: 'object',
  required: ['breakthrough_score', 'tier', 'confidence', 'content_available', 'novelty_vs_prior', 'rationale'],
  properties: {
    breakthrough_score: { type: 'integer', minimum: 0, maximum: 100,
      description: 'advance BEYOND the prior-art landscape shown. 0=no advance, 100=redefines the field' },
    tier: { type: 'string', enum: ['landmark', 'significant', 'solid', 'incremental', 'non_contribution'] },
    confidence: { type: 'number', minimum: 0, maximum: 1 },
    content_available: { type: 'boolean' },
    novelty_vs_prior: { type: 'string', enum: ['clearly_beyond', 'incremental_over', 'largely_covered_by', 'cannot_tell'],
      description: 'how this paper stands relative to the prior-art brief specifically' },
    rationale: { type: 'string', description: 'reference the prior art explicitly; <=340 chars' },
  },
}

const PERSONAS = [
  { key: 'trialist', desc: "a senior clinical Alzheimer's-disease researcher and trialist (you have run phase-3 anti-amyloid trials and read the biomarker literature). You judge whether a paper changes clinical practice, diagnosis, or therapeutic direction." },
  { key: 'neuroscientist', desc: 'a molecular / systems neuroscientist studying AD mechanisms (single-cell, spatial transcriptomics, microglia, tau/amyloid biology). You judge mechanistic novelty and whether it opens genuinely new biology.' },
  { key: 'metascientist', desc: 'a metascience / research-impact analyst. You are hard-nosed about distinguishing a genuine discovery from a well-cited non-discovery (an annual statistics report, a burden-of-disease update, a review, an incremental ML benchmark). Field-reshaping potential is what you score.' },
]

function judgePrompt(slug, persona) {
  return `You are ${persona}

Rate how much of a scientific BREAKTHROUGH the following Alzheimer's-disease paper is — its potential to reshape the field — on a 0-100 scale. Breakthrough is RELATIVE TO THE STATE OF THE ART: a paper is only a breakthrough insofar as it advances beyond what was already known.

Read TWO things:
1. The paper's content: ${ARALIB}/${slug}/PAPER.md (title, year, venue, abstract, claims_summary; you may also read logic/claims.md).
2. The prior-art landscape at its publication date: ${BRIEFS}/${slug}.md — the closest PRECEDING works. Judge how far THIS paper advances beyond THAT specific prior art, not just how impressive it sounds in isolation.

STAY BLIND to any computed metric: do NOT open the gro/ sidecars, any *.json in the metrics folder, or any file with "significance"/"score"/"anchor" in the name. The brief deliberately contains NO scores — form your own novelty assessment from the titles.

Anchor your scale:
- 90-100 landmark: redefines diagnosis/therapy/mechanism beyond all shown prior art (a first pivotal disease-modifying trial, a first-in-field molecular discovery).
- 65-89 significant: a real new finding/method clearly beyond the prior art that others will build on.
- 40-64 solid: a competent advance, but close to existing prior work.
- 15-39 incremental: derivative of the prior art shown; a benchmark tweak, a routine update.
- 0-14 non-contribution: an annual statistics/facts report, a burden re-estimate, a generic review — largely covered by the prior art, cited but not a discovery.

If PAPER.md is title-only, set content_available=false, low confidence. Return your rating, including how it stands vs the prior-art brief.`
}

phase('SOTA panel')
log(`SOTA-grounded panel: ${SLUGS.length} papers x ${PERSONAS.length} judges (prior-art brief, no scores)`)
const expert = await parallel(SLUGS.map(slug => () =>
  parallel(PERSONAS.map(p => () =>
    agent(judgePrompt(slug, p.desc), { label: `sotajudge:${p.key}:${slug.slice(0, 10)}`, phase: 'SOTA panel', schema: JUDGE_SCHEMA, effort: 'low' })
      .then(v => (v ? { persona: p.key, ...v } : null))
  )).then(votes => ({ slug, votes: votes.filter(Boolean) }))
))

return { expert, n_papers: SLUGS.length }
