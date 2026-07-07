# Problem

## Observations

**O01 — The prior deterministic-tier experiment never left the artifact.**
The parent experiment (`EXPERIMENT_PAPER.md`) converted eight prose-blocked metrics into
structural joins over LLM-authored sidecars and ran them corpus-wide "with no network." Its
`reference_resolvability_rate` "meant only whether an `external_id` string was *printed and typed
as resolvable*; no DOI was ever fetched" (§1, line 9).

**O02 — The GRO spec defines Tier B and Tier C as requiring external resolution by construction.**
"Per the spec (§1), **Tier B · Anchored** resolves ids to the outside world through pinned
resolvers, and **Tier C · Judged** produces novelty/entailment verdicts by reading the graph and
comparing it against external precedent. Both are defined by *leaving* the file." (§1, line 11)

**O03 — The v3 tournament's prior conclusion was a hard limit on self-contained metrics.**
"the v3 tournament concluded, across all winning metric sets, that 'a well-compiled record of bad
science and a well-compiled record of good science are, by construction, indistinguishable to
every metric in this tournament.'" (§4, line 72)

## Gaps

**G01 — Untested: do the anchored/judged tiers actually compute against real external records?**
Before this experiment, no run had made live calls to an external index (PubMed,
ClinicalTrials.gov) to resolve a reference, join a claim to a registered trial outcome, or check
novelty against indexed literature. Whether Tier B/C operations are executable at all outside the
artifact — as opposed to merely specified — was unknown.

**G02 — Untested: can the tiers discriminate good science from bad science?**
Even if the tiers compute externally, no prior run had exposed them to a corpus containing a
known-bad paper (retracted, fabricated reference, or expert-flagged). Leaving the artifact
"loosens" the self-containment limit in principle ("external resolution *can* catch a fabricated
reference or a retracted citation, which a self-contained metric provably cannot" — §4, line 72),
but this had never been tested empirically.

## Key insight

The two gaps are logically separable and must not be conflated: **computability** (does the
metric run against the outside world and return real signal) is a different question from
**discriminative validity** (does that signal separate trustworthy from untrustworthy work). A
corpus made entirely of legitimate papers can answer the first question but cannot, by
construction, answer the second — no matter how well the metric performs on it.

## Assumptions

- The six-ARA corpus (`zim25`, `jes26`, `che26`, `val25`, `han26`, `tit26`) is treated as
  representative of ARAs an anchored/judged pass would encounter in the Alzheimer's domain, not as
  a discrimination benchmark.
- PubMed and ClinicalTrials.gov are treated as adequate "external ground truth" for the reference,
  novelty, and registry checks in scope; no other external index was queried.
- LLM adjudication of tool outputs (title-match, prior-art determination, endpoint-match) is
  accepted as the current implementation of Tier B/C judgement, with the explicit caveat that this
  adjudication is not itself deterministic (§4, line 74).
