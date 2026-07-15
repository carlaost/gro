export const meta = {
  name: 'historical-fulltext-judge-claude',
  description: 'Claude directly judges breakthrough-ness (0-100) from full text on the historical corpus — to correlate LLM JUDGEMENT (not the metric) against field outcome',
  phases: [{ title: 'Judge-FT', detail: 'one Claude agent per paper rates breakthrough-ness from full text' }],
}
const items = typeof args === 'string' ? JSON.parse(args) : args
const SCHEMA = { type:'object', additionalProperties:false, required:['breakthrough_score'],
  properties:{ breakthrough_score:{type:'integer', minimum:0, maximum:100} } }
phase('Judge-FT')
const res = await parallel(items.map(it => () =>
  agent(`Read the full text at ${it.path} (a research paper, published at its time). Rate how much of a scientific BREAKTHROUGH it is — its potential to reshape the field — on 0-100. Judge ONLY from the paper at publication time; use NO hindsight about its later citations or influence. Anchor: 90-100 field-redefining landmark; 65-89 significant new finding/method; 40-64 solid; 15-39 incremental; 0-14 non-contribution (report/review/re-estimate). Output only the JSON.`,
    {label:`fjudge:${it.slug}`, phase:'Judge-FT', schema:SCHEMA, agentType:'general-purpose', effort:'low'})
    .then(o => ({slug:it.slug, score: o && o.breakthrough_score})) ))
const out={}; for(const r of res){ if(r) out[r.slug]=r.score }
return out
