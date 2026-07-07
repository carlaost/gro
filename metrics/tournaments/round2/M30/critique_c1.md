# M30 — Assumption realism & limitation validity — Judge critique, cycle 1

Metric M30 asks a *validity/content-truth* question layered on top of round-1 07 (concreteness) and
verifier D3 (explicitness): are the stated assumptions realistic/fair for the work as performed (real
vs. dreamcase), and do the stated limitations add a genuinely new condition (vs. restatement/boilerplate)?
Judging axes: reasoning correctness; a concrete/runnable [sem] realism-judgement → deterministic
sub-score pipeline; Goodhart-resistance; penalize-don't-skip (a bare "no limitations" scores *down*,
never N/A); and being demonstrably *tighter* than the concreteness/explicitness checks it sits above.

The decisive differentiator this cycle: the metric's stated edge is that it is "the deeper signal"
neither 07 nor D3 covers. The strongest proposals operationalize that by reading the method
*independently* to catch **unsurfaced** risk — a declaration-scoped check (grade only what's written)
can never be tighter than a presence/concreteness check. Proposals that only re-grade declared bullets
score lower on the tighter-than-concreteness axis even when otherwise clean.

---

## Per-expander verdicts

### exp1 — rank 4
Solid reasoning; correctly separates the two failure modes (dreamcase assumptions that assume away the
hard problem; restated-not-new limitations). Two-source design (in-artifact internal cross-check +
external [sem] fallback for `unverifiable`) is a good instinct and the availability *ceiling multiplier*
(min(ceiling, computed)) is a clean penalize-don't-skip encoding.

Weaknesses that drop it to last:
- **Code is buggy/sloppy in the load-bearing final function.** Line ~268-269 is contradictory: a dead
  `targeted_bonus = 0.0 ... else 0.0` line, then a convoluted ternary whose semantics for "new limitation
  without a named target" are hard to follow and probably not what the prose intends. For a metric judged
  partly on *runnable* determinism this matters.
- **The external [sem] step is hand-wavy.** `external_verdict` assumes the tool returns a tidy
  `{"contested": bool, "citation_count": int, "summary": str}` — an optimistic, invented contract with a
  brittle `citation_count >= 2 → dreamcase` rule. The other proposals that stay artifact-internal (exp3)
  or ground in method-text quotes (exp2) are more defensible.
- **No independent omission scan.** It grades declared bullets plus a narrow evidence-consistency
  cross-check; it does not read the method independently for standard-but-unsurfaced risks, so its
  tighter-than-concreteness claim rests mostly on "we judge realism not form" — weaker than exp2/exp4.

Net: correct thesis, adequate anti-padding (mean not sum), but the weakest execution and the least
net-new mechanism.

### exp2 — rank 1 (WINNER)
The strongest proposal. Three sub-targets (realism, validity, **coverage**), and the coverage arm is the
standout: an **omission scan** (§5.4) that independently scans the method file(s) for field-standard
caveat triggers (single-center, retrospective, small-N, self-report, no control arm, post-hoc subgroup,
unvalidated instrument, missing-data-without-sensitivity) and penalizes each *used-but-unsurfaced* risk,
with a required exact-sentence quote. This is exactly the "reads the method independently to check for
unsurfaced risk" mechanism that makes the metric genuinely tighter than a declaration-scoped
concreteness/explicitness check — and it directly closes the hardest gaming route (state the easy
assumptions, silently omit the shaky one).

Other strengths:
- **Cross-bucket dedup** (across boundary/assumption/limitation, not within one) closes "restate a
  boundary condition as a limitation for double credit" and "split one caveat into three bullets."
- Clean per-item, label-gated deterministic reductions (`score_assumption`, `score_limitation`) with
  explicit triviality/load-bearing weighting and a named `generic_boilerplate` category — surface
  wording can't buy score.
- **penalize-don't-skip is the most rigorously argued of the four**: every missing-input path (no
  assumptions, no limitations, no evidence flags, zero method files) maps to a defined penalty term;
  the proposal explicitly states "there is no code path that returns None/skip," with the single hard
  zero reserved for the true structural floor (constraints.md absent). Penalties are subtractive from a
  content base and the omission penalty is capped so one sub-check can't zero an otherwise-good artifact.
- Complete, coherent final function returning score + components + human-legible flags.

Minor weaknesses: many [sem] calls (dedup pairs, per-assumption, per-limitation, scan, per-trigger
is_surfaced) → higher compute; the `expected_min = len(method_files)` complexity proxy for thinness is
crude; no worked example. None of these undercut the core edge.

### exp3 — rank 3
Clean, well-scoped, cheapest. Distinctive contribution is the **worst-offender guard** (§5.6): a single
flagrant dreamcase assumption or hollow limitations section caps the metric at 0.5 regardless of a good
average — a genuinely different anti-padding lever from the others (averaging can't wash out one bad
offender). Also has a deterministic boilerplate pre-filter, a structural-floor multiplier, and an
explicit, correct warning that "Step 1-2 must never degrade into a concreteness/presence check." Good
penalize-don't-skip via the floor multiplier + placeholder low scores for empty sections. Deterministic
reductions are the tidiest of the four.

Why not a winner: it *deliberately* scopes out external lookups AND has the weakest omission detection —
its only unsurfaced-risk check is the cross-layer evidence-consistency note (§5.5), which fires only when
the evidence layer already flagged an inconsistency. It cannot catch a shaky-but-undeclared assumption
that is visible in the method but not flagged elsewhere. That makes its tighter-than-concreteness edge
thinner than exp2's (method omission scan) and exp4's (missing-known-threats). A strong, safe design that
under-reaches on the one axis that most defines the metric.

### exp4 — rank 2 (WINNER)
Excellent execution and the most auditable. Distinctive contributions:
- **`missing_known_threats`** (§3.6): the judge is asked to name up to 3 field-standard threats to
  validity for this genre that are conspicuously absent from both Assumptions and Limitations (e.g.
  verification/spectrum/incorporation bias for a diagnostic-accuracy meta-analysis). This is the adversarial,
  reads-beyond-what's-declared mechanism (exp2's peer via domain knowledge rather than method-text
  scanning) that earns the tighter-than-concreteness edge — with the right guardrail ("do not invent
  generic ones just to fill the list").
- **Two independent deterministic backstops** (boilerplate-library fuzzy match; prior-text redundancy
  similarity) that *cap* the LLM's verdict (`base = min(base, 0.2)`), so an LLM charmed by well-written
  boilerplate is still bounded by string-level evidence it can't argue away. This "LLM verdict, but
  deterministically capped" pattern is the cleanest realism-judgement → sub-score reduction of the four.
- **Worked example (che26, §3.8)** — traces A2 (independence/no-double-counting) to `realism: unclear` +
  `load_bearing: yes` + `stress_tested: no`, and the batch-effects limitation to `adds_new_condition:
  partial`. This concretely demonstrates the pipeline and is the only proposal to show its output on a
  real artifact — strong evidence the workflow actually runs.
- Load-bearing weighting (1.5 vs 0.5) so gaming the wrong assumptions is a losing move; floor multiplier
  encodes penalize-don't-skip structurally (0.35 / 0.25 for missing assumptions/limitations, never N/A).
- Single [sem] call per artifact → far cheaper than exp2.

Minor weaknesses: `missing_known_threats` leans on the judge's domain recall (more invention-prone than
exp2's method-quote-grounded scan, though the prompt guards against it); the rapidfuzz dependency and the
`token_set_ratio >= 0.75` boilerplate threshold are somewhat arbitrary; the fuzzy redundancy backstop
(0.8) can miss paraphrase-level restatement that shares few tokens.

---

## WINNERS: exp2, exp4

Both operationalize the metric's defining edge — independently probing for *unsurfaced* risk rather than
only grading declared bullets — which is what makes M30 genuinely tighter than 07/D3. They do it via
complementary mechanisms: exp2 grounds omission detection in the method text (Goodhart-hardest, quote-
required, but compute-heavy); exp4 grounds it in the judge's genre knowledge plus two deterministic
string-level caps and proves the whole pipeline on a real artifact (cheapest, most auditable). exp3's
worst-offender guard and exp1's two-source cross-check are good ideas the winners should absorb.

### Winner critiques + cycle-2 directions

**exp2 — cycle-2 directions:**
1. **Cut [sem] cost.** Five LLM call types (dedup, per-assumption, per-limitation, scan, per-trigger
   is_surfaced) is expensive per artifact. Batch dedup + is_surfaced into single list-in/list-out calls,
   and consider embedding-cosine for dedup with an LLM tie-break only near threshold (the proposal already
   allows this — commit to it and specify the threshold).
2. **Harden the omission scan against invention.** Require, like exp4, that each flagged trigger cite an
   exact method-text sentence (it does) *and* add a guard that the judge must not emit a trigger it can't
   quote — otherwise the scan can hallucinate risks and over-penalize honest papers. State the
   false-positive cost explicitly.
3. **Replace the crude thinness proxy.** `expected_min = len(method_files)` (>=1 assumption per method
   file) is arbitrary; tie thinness to the number of scanned design-risk triggers instead (if the method
   has N standard-caveat-bearing choices, expect roughly that many surfaced items).
4. **Add a worked example.** exp4's che26 trace is a real credibility win; exp2 has none. Run the full
   pipeline on che26 (A2 + batch-effects + the Table-1/caption data-quality caveat) and show the
   component vector and flags.
5. **Steal exp3's worst-offender guard.** A subtractive omission penalty capped at 0.6 still lets a paper
   with one flagrant dreamcase assumption score respectably if everything else is fine; add a min-item
   cap so a single near-flagrant item bounds the ceiling.

**exp4 — cycle-2 directions:**
1. **Ground `missing_known_threats` more.** It currently relies on the judge's genre recall; give it the
   method excerpt (it already passes one) and require each named threat to reference the specific design
   choice in the excerpt that makes the threat applicable — moving it partway toward exp2's method-scan
   rigor and cutting invention.
2. **Justify/soften the fuzzy thresholds.** 0.75 boilerplate and 0.8 redundancy `token_set_ratio` cutoffs
   are asserted, not derived; token-set similarity misses low-overlap paraphrase. Add an embedding-cosine
   or LLM tie-break in the 0.6-0.8 band, and note the failure mode where a real, specific limitation that
   happens to reuse stock nouns gets wrongly capped.
3. **Reconcile the two omission signals.** exp4's `missing_known_threats` and exp2's method-omission scan
   are the same idea from two directions; adopt exp2's cross-bucket dedup (exp4 only checks limitation-vs-
   prior, not across all three buckets) so restating a boundary condition as a limitation is caught.
4. **Feed the data-quality-caveat cross-check into the score.** §3.8 notes the Table-1/caption mismatch is
   reported in `detail` but "doesn't feed the numeric formula directly." Per the shape file this is a
   probe-able coverage signal — make it a small scored term (as exp1/exp2/exp3 do), not just an audit note.
5. **Expand the worked example** to include the availability-floor and missing-threats branches (show a
   genre-standard threat che26 omits, e.g. verification/spectrum bias for diagnostic-accuracy synthesis),
   so the adversarial arm is demonstrated, not just asserted.

### Loser one-liners
- **exp1:** Right thesis and a nice ceiling-multiplier gate, but buggy/contradictory final scoring code, a
  hand-wavy invented external-[sem] return contract, and no independent omission scan — least net-new.
- **exp3:** Cleanest and cheapest with a genuinely useful worst-offender cap, but its only unsurfaced-risk
  check fires solely on pre-existing evidence-layer flags, so it under-reaches on the metric's defining
  "catch what's omitted from the method" axis.
