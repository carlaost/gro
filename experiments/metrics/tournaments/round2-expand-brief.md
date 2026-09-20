# Expander brief — per-metric tournament (round 2)

You are one of FOUR independent expanders for ONE proposed good-science metric. Your job is NOT to
propose a metric from scratch — the metric already exists as a one-line indicator. Your job:
1. **Expand the reasoning**: why this indicator signals good science; what exactly it should reward and
   what it must not; the failure modes / gaming routes; and how the assessment-critique's notes on this
   metric (redundancy, verifier-overlap, better-scoping, what's missing) change the design.
2. **Build a generation/compute workflow** for it: a concrete, runnable procedure that produces the
   metric value from the artifact — inputs (which artifact fields), steps, any [sem]/external calls
   (semantic-scholar/undermind/FOL/clinical-trial lookup) called out explicitly, and the final scoring
   function as real Python against the documented artifact shape. If a step needs an LLM or external
   tool, specify the exact prompt/query and how its output is turned into a deterministic sub-score.
3. State **why it's hard to Goodhart** and how it composes with the rest of the suite.

HARD CONSTRAINT: the metric ASSUMES its inputs are available and PENALIZES missing/thin inputs (scores
down, never skips/N-A); unavailability may itself be an input. Availability of the artifact/field is
itself part of the score.

You are given: the metric's ledger entry (id, name, artifact, scope notes, assessment-critique notes) and
the relevant artifact's data-shape section. Read ONLY those (+ this brief). Write your expansion+workflow
to the output path given. Reply with ONE line only: "<Mid> expander<N>: done".
