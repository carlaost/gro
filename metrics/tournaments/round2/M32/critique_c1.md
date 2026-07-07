# M32 — Method validity & verification status — Round 2, Cycle 1 critique

Metric: *Is the method sound — a widely-accepted validated method vs one over-generalized beyond
its warrant (and is that justified/explained)?* A tighter, specific facet of verifier D6. Primary
artifact: §7 `logic/solution/` (`constraints.md` + method files).

Judged on: reasoning quality; concrete/runnable workflow; Goodhart-resistance; penalize-don't-skip
compliance; and preservation of the tighter-than-D6 edge.

---

## Per-expander verdicts

### exp1 — RANK 1

**Reasoning.** The single clearest articulation of *why M32 ≠ D6*: D6 = "was the method executed
correctly"; M32 = the logically prior "is this the right tool, validated for the context it is
actually applied in." The worked example (pass-D6-fail-M32 and vice versa) makes the orthogonality
concrete, and §5 shows the two never touch the same fields — M32 "never reads sample size,
p-values, or study-design quality." That is the top-10 edge, preserved deliberately.

**Workflow.** External `[sem]` validity-tier lookup (STANDARD / ADJACENT / NOVEL_OR_CONTESTED /
UNKNOWN) queried on **method + domain jointly**, then a disclosure branch (JUSTIFIED /
ACKNOWLEDGED_UNJUSTIFIED / SILENT) run *only* for non-STANDARD tiers. This is the design that most
directly grounds "widely-accepted validated" against outside evidence rather than trusting the
paper's or the LLM's self-report — exactly right for a metric whose crux is external validity.

**Goodhart-resistance — strongest in the field.** Two standout moves the others lack: (1) the tier
branch is evaluated *first*, so a standard-method/standard-problem paper wins with zero
justification prose (correct) without also letting a paper that *needed* to justify an extension
coast on the same silence (failure-mode 3, explicitly closed); (2) **min-weighted aggregation
(0.4·mean + 0.6·min)** across up to 3 methods, so one silently-mismatched method cannot be diluted
by several fine ones — no other proposal defends the multi-method hide-the-bad-one route.
UNKNOWN-tier is treated as at-least-as-demanding as ADJACENT ("absence of evidence is not evidence
of validity") — a genuinely thoughtful floor.

**Penalize-don't-skip.** Every branch of `score_m32` terminates in a number; explicit floors 0.0 /
0.05 / 0.15 for missing-constraints / abstract-only / non-extractable. Fully compliant.

**Weaknesses (→ cycle 2).** (a) Omits the *"& verification status"* half of the metric name —
there is no axis for whether the paper performed a method-fitness check (calibration, ablation,
assumption test). exp3 has this; exp1 should absorb it. (b) The disclosure classification is a
bare LLM call with no quote-grounding — vulnerable to the LLM asserting JUSTIFIED without textual
anchor. Borrow exp3's `sanitize_judgment` so JUSTIFIED must carry a verbatim, source-matched span.
(c) "cap at top 3 by prominence" leaves "prominence" undefined — specify it. (d) Add a
self-contained backstop for when the external search is unavailable so niche-method papers don't
all collapse to UNKNOWN.

---

### exp3 — RANK 2

**Reasoning.** The only proposal that fully honors *both* halves of the metric name: it scores
method **validity** (warrant_class) *and* **verification status** (`self_verification_present` — a
check *on the method's fitness*: internal/external validation, calibration, benchmarking, ablation,
assumption test — explicitly distinguished from a results/accuracy number). Given the metric is
literally titled "Method validity & verification status," this is a real on-brief advantage. The
four-situation taxonomy (in-scope / extended-defended / extended-undefended / novel) is crisp, and
it correctly *rewards honest novelty over silent standard-method overreach*, removing the incentive
to mislabel.

**Workflow.** Confined to §7 text, one semantic call emitting a small falsifiable JSON (not a
holistic 1–10), plus deterministic structural signals. The scope discipline is deliberate and well
argued: reducing to independently falsifiable, quote-grounded fields is exactly what keeps it from
collapsing back into D6's fuzzy rigor score.

**Goodhart-resistance — strongest grounding machinery.** `sanitize_judgment` + `_quote_grounded`
programmatically downgrade *any* non-default field lacking a source-matched verbatim quote before
scoring — an LLM cannot win by asserting `warrant_justified: true`. Two independent signals must
agree: a favorable semantic read is *capped at 0.35* when the structural boilerplate check fails.
The thin-source floor is distinguished from selective silence by *uniform* thinness — a subtle,
correct distinction none of the others draw as cleanly.

**Penalize-don't-skip.** Explicit floors: missing constraints 0.0, thin/abstract-only 0.08,
unclear 0.10 — all strictly below any engaged case, "no N/A branch exists in this table."
Compliant.

**Weaknesses (→ cycle 2).** (a) Scores essentially a single primary method and its warrant — no
multi-method min-aggregation, so exp1's hide-the-bad-method route is open here. Adopt exp1's
0.6-weighted-min blend. (b) "established-in-scope" rests on LLM world-knowledge guarded only by a
reputation-halo prompt instruction — no *external* confirmation that the method truly has the
validation track record claimed. exp3 itself notes an external lookup as future work; pulling in
exp1's `[sem]` tier as a confirmatory layer would harden the load-bearing judgment. (c) The
`_quote_grounded` sliding-window `SequenceMatcher` loop is ad hoc and O(n·windows) — replace with
normalized-substring + a rapidfuzz partial-ratio.

---

### exp4 — RANK 3 (loser)

Clean two-axis design (method_class × warrant_explicitness) with a well-built deterministic
availability sub-score that concretely enforces "availability is part of the score" via a ceiling
remap, plus a `verify_grounding` substring check and a smart "chunk per file, take the
lowest-scoring file" anti-dilution rule. Genuinely good work. It loses because it substantially
**overlaps exp3's artifact-only warrant framing while capturing less**: it folds
extended/unvalidated into method_class but has no dedicated *verification-status* axis (the
metric's named second half), its grounding check is a single normalized-substring test weaker than
exp3's full-field sanitize pass, and the `ceiling = 0.3 + 0.7*(avail/0.7)` remap is over-engineered
for what it does. Where exp3 and exp4 converge, exp3 is the stronger expression; where they differ,
exp1's external grounding is the more valuable complement to keep.

### exp2 — RANK 4 (loser)

Shares exp1's external-lookup instinct and contributes one good idea — justification credit
requires a verbatim quote *plus* a `§X.Y` source ref matching constraints.md's own convention,
deterministically rejecting laundered/vague justification. But it scores only the *single* "most
load-bearing" method, leaving the hide-the-bad-method route wide open, and its `established_subscore`
is the weakest technical core in the field: abstract keyword-token matching gated on an arbitrary
`citationCount >= 20` threshold is brittle and gameable in both directions (a famous in-domain
method with sparse abstract keywords scores low; keyword-stuffed abstracts launder a stretch). The
better parts of exp2 (joint method+domain query; source-ref-anchored justification) are already
subsumed by exp1 and exp3.

---

## WINNERS: exp1, exp3

### Cycle-2 directions for winners

The two winners are complementary, not redundant — exp1 is externally-grounded (best answer to
"widely-accepted validated"), exp3 is artifact-grounded + auditable (best answer to "is the warrant
legible and is verification present"). Cycle 2 should converge them:

1. **Merge the axes.** Take exp1's tier×disclosure external-validity core AND exp3's
   `self_verification_present` axis, so the final metric scores *validity* (external) and
   *verification status* (from text) as the name demands. Neither winner alone does both.
2. **Adopt exp1's multi-method min-weighted aggregation** as the aggregation layer for whichever
   design wins — it is the only defense against burying one bad method among good ones, and both
   exp3 and exp2 lack it.
3. **Adopt exp3's `sanitize_judgment` quote-grounding** for every semantic field in the merged
   design (including exp1's disclosure = JUSTIFIED), so no non-default label survives without a
   source-matched verbatim span.
4. **Resolve the external-call dependency.** Keep the `[sem]` tier lookup as the primary validity
   signal but define a self-contained fallback (exp3's reputation-halo-guarded classification) for
   when search is unavailable, and keep UNKNOWN scored as demanding-as-ADJACENT.
5. **Pull in exp2's source-ref requirement** (`§X.Y` matching constraints.md convention) as an
   additional grounding gate on justification, and exp4's availability-ceiling as the
   penalize-don't-skip enforcement mechanism.

### Loser one-liners

- **exp2:** Good source-ref-anchored justification check, but single-method-only and a brittle
  keyword-plus-arbitrary-citation-threshold validity subscore; its best ideas are subsumed by exp1.
- **exp4:** Clean two-axis warrant design and strong availability gating, but overlaps exp3 while
  missing the named "verification status" axis and using a weaker single-substring grounding check.
