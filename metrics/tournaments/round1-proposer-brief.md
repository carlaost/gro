# Proposer brief — blind metric-design tournament

You are one of FOUR independent proposers on a blind panel. Design metrics that measure "GOOD SCIENCE"
from ONE artifact the ARA compiler emits. Bring original ideas — you want to surface signal the other
three miss.

## CLEAN-ROOM RULES (strict)
Read ONLY (a) this brief and (b) the single artifact shape file you are told to use. Do NOT read any
other file — NOT `metrics-directions.md`, NOT anything under `research/metrics/` except your one shape
file, NOT any `critiques/`, NOT `FINDINGS.md`, NOT any existing `*.py` metric, NOT other artifacts'
shapes, NOT other proposers' output. Your proposals must be uncontaminated by any pre-existing scheme.

## THE ONE HARD CONSTRAINT
A metric ASSUMES its inputs are available and computes anyway. If an input is missing / absent / thin, the
metric must PENALIZE that (score it down) — never skip, never return N/A, never "not applicable." Missing
data is a low score, not an absent score. Unavailability MAY itself be a deliberate input to a metric
(the absence of X can be evidence of low quality). Otherwise you have free range.

## OUTPUT: a markdown list of 3–5 metrics. For EACH metric, exactly these five parts:
1. **name**
2. **how it signals good science** — the epistemic argument (why more-of-this = better science)
3. **compute function** — real Python against the documented shape (assume a parsed representation of the
   artifact matching the shape doc; state your input assumptions explicitly at the top of the function)
4. **what the function does & why** — plain-language walk-through of the computation
5. **why it's hard to Goodhart** — the gaming analysis for this metric
End the list with a short **"Combination"** paragraph: why your set is JOINTLY hard to game — i.e. gaming
one metric should hurt another, so a paper can't cheaply win all of them at once.

Write clean markdown to the output path you are given, then reply with ONLY one line:
"agentN <artifact>: M metrics written". Do not paste the proposals into your reply.
