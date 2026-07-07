# M32 — Method validity & verification status — Round 2, Cycle 2 critique

Metric: *Is the method sound — a widely-accepted validated method vs one over-generalized beyond
its warrant (and is that justified/explained)?* A tighter facet of verifier D6. Primary artifact:
§7 `logic/solution/` (`constraints.md` + method files).

This is the **middle cycle**: A and B both advance to cycle 3, no final winner is picked here. A is
the cycle-2 revision of exp1 (c1 RANK 1); B is the cycle-2 revision of exp3 (c1 RANK 2). Both
absorbed the c1 convergence directions, so they now aim at the same target (both axes, min-weighted
aggregation, quote-grounding, fallback/availability discipline). The interesting question is no
longer "who covers the brief" — both do — but *which mechanisms are actually correct*, and where
the two still genuinely differ. That difference turns out to be sharp and worth preserving into
cycle 3.

---

## A (revision of exp1) — verdict: fixed all four c1 weaknesses, one philosophy intact, two residual holes

**What it got right.**
- **(a) verification axis** is added the right way: additive, flat, capped, *explicitly never a
  substitute for disclosure* (§5, and the worked NOVEL/SILENT 0.00→0.10 example). This preserves
  the c1-praised centerpiece — disclosure is the load-bearing signal, verification is icing — while
  finally honoring the "& verification status" half of the name. The rationale that verification
  "cannot make a method more standard, only more trustworthy where trust was already incomplete" is
  the correct framing.
- **(b) quote-grounding** (Step 3b) is applied uniformly to `JUSTIFIED`, `verification_quote`, and
  fallback tiers, and the substring-first / difflib-fallback implementation is cheaper and less
  arbitrary than the c1 sliding-window it explicitly retires.
- **(c) prominence** is now a deterministic mention-count function — fully auditable, a strict
  function of the text.
- **(d) fallback** correctly distinguishes *infra failure* (call errors) from *search executed,
  zero hits* (legitimately `UNKNOWN`, unchanged), and the fallback classifier is deliberately
  handicapped (cannot emit `STANDARD`, must name a checkable source). This is a genuinely careful
  fix that closes the "wait for the outage to get a softer path" route.
- Preserved intact: tier-first branching, `0.4·mean + 0.6·min`, `UNKNOWN`-as-demanding-as-`ADJACENT`,
  STANDARD/in-scope → 1.00. That last point matters (see B below) — A keeps c1's failure-mode-3
  reasoning that a standard-method/standard-problem paper should win *by default* with zero
  justification prose.

**Residual holes (→ cycle 3).**

1. **The fallback quote-grounding code is broken and conceptually confused.** In Step 3b the
   commented call is `sanitize_field(tier, tier_evidence, general_knowledge_text=None,
   default="UNKNOWN")` — but `sanitize_field(value, quote, source_text, default)` has no
   `general_knowledge_text` parameter, and passing a `None` source to `is_quote_grounded` would
   throw in `_normalized(None)`. More deeply: a fallback tier's `tier_evidence` is a *named external
   guideline* ("NCCN 2023 §3.1"), which by construction will **not** appear in the paper text, so
   substring-grounding it against any source is the wrong test. What A actually wants there is a
   *non-emptiness / specificity* check ("is a concrete source named?"), not quote-grounding. Cycle 3
   must replace this with an explicit specificity predicate and drop the misapplied `sanitize_field`
   call.

2. **Verification-laundering is only half-closed.** Step 3b confirms the `verification_quote`
   *exists* in the text, but nothing checks that the quoted span is a *fitness check* (calibration,
   assumption test, ablation, benchmark) rather than a *results/accuracy number* — the exact
   distinction §1/§3 say defines the axis. An LLM can quote a real "AUC 0.91 on held-out data"
   sentence, mislabel it as verification, and the grounding pass passes it (the span is real). So
   gaming route 6 is closed against *fabricated* quotes but open against *misclassified real*
   quotes. Cycle 3: add a second grounded check (or a small closed enum of check-types the span must
   match) that adjudicates fitness-check-vs-accuracy-number, not just existence.

3. **Prominence-by-raw-mention-count is itself a small gaming surface.** `re.escape(name)` exact,
   case-insensitive substring counting means (i) a verbose or boilerplate-repeated method outranks a
   tersely-named but load-bearing one, and (ii) acronym/variant spellings ("Cox proportional-hazards
   model" vs "Cox model" vs "PH model") are counted as different methods and undercounted. Because
   only the top-3 reach the [sem]/disclosure steps, a paper could push a clean method up the ranking
   by repetition and let a briefly-named overreach fall off the evaluated set — quietly re-opening
   the hide-the-bad-method route that the min-aggregation is meant to close. B's heading/structure
   prominence is more robust here (though more complex). Cycle 3: fold in a structural signal
   (named as subject of a `## Statistical analysis`/`## Model`-type heading) and canonicalize
   acronyms before counting.

4. **Fallback tiers score at face value with no residual cap.** A carries `tier_source` into the
   payload as "audit-only, does not gate the score," so a FALLBACK-derived `ADJACENT`/`JUSTIFIED`
   scores *identically* to a `[sem]`-confirmed one. That is a softer path than intended: the whole
   point of external grounding is that a knowledge-only tier is less trustworthy. B's
   `external_tool_used` ceiling (0.90 vs 1.0) is exactly the missing discipline. Cycle 3: apply a
   small residual cap to FALLBACK-sourced components, consistent with penalize-don't-skip.

---

## B (revision of exp3) — verdict: the blind-call halo defense is genuinely new and strong, but B quietly *dropped the external lookup* and mis-calibrated the standard case

**What it got right.**
- **Blind Call A / full-text Call B split** is the strongest single new idea in this cycle. Stripping
  the paper's persuasive framing (`however`, `gold standard`, `robust to`, …) before the tier call
  directly attacks the confident-framing halo that neither winner defended in c1. This is a real
  contribution A does not have.
- Adopted exp1's multi-method min-weighted aggregation (fixes exp3's single-method blind spot,
  c1 weakness (a)).
- Hardened `_quote_grounded` (substring-first, per-sentence fuzzy ≥40 chars @ 0.90) fixes c1
  weakness (c) cleanly.
- Folded in exp2's `source_ref` anchor and exp4's availability ceiling (zero method files → cap
  0.55) — good penalize-don't-skip hygiene.

**Residual holes (→ cycle 3).**

1. **B does not actually implement the external [sem] lookup — this is the biggest gap.** c1's
   critique of exp3 was, verbatim, "no external confirmation that the method truly has the validation
   track record claimed," and convergence direction #4 said to *keep the `[sem]` tier as the primary
   validity signal*. B's answer is a **blind LLM** call, with `external_tool_used = false` for the
   whole design (§2 post-processing: the flag only flips true "if a future deployment wires Call A to
   an actual retrieval tool"). Blind redaction defends against *halo*, but it is still the model's
   own world-knowledge — it does not consult the literature at all, so it does not answer "is this
   genuinely widely-accepted for *this* application." The `external_tool_used` machinery is therefore
   vestigial (always false), and its only live effect is to cap every B score at 0.90. A, by
   contrast, does issue the `[sem]` query. Cycle 3 for B: wire Call A (or a confirmatory Call A′) to
   the real `[sem]`/undermind retrieval and let `external_tool_used` actually toggle — otherwise B is
   strictly weaker than A on the metric's crux ("widely-accepted validated").

2. **The redaction can strip signal, not just persuasion.** The cue-token filter drops any sentence
   containing `validated`, `assumption`, `robust to`, `sensitivity analysis`, etc. A sentence like
   "we applied Cox regression, validated for right-censored survival data, to our cohort" is deleted
   wholesale — taking the *regime* information ("right-censored survival data") that Call A needs to
   classify the tier with it. Aggressive redaction systematically pushes Call A toward `UNKNOWN`,
   which B then scores as demanding-as-`ADJACENT` — i.e. over-stripping silently penalizes honest
   papers. Cycle 3: strip only the persuasive clause (or move to structured domain extraction feeding
   Call A a clean `{data_type, population, regime}` tuple rather than a lossy sentence filter), and
   measure the over-strip rate.

3. **The standard-case calibration contradicts c1's own praised reasoning.** In `_method_component`,
   a `STANDARD`, in-scope method with no `assumptions_engaged` and no self-verification scores
   **0.50**; with assumptions engaged, 0.70; capped at 0.90 (knowledge-only). So the *cleanest
   possible case* — a widely-accepted method used exactly as validated, with the correct "silent
   default" c1 explicitly said should win — tops out well below A's 1.00 and can score as low as
   0.50. B has effectively re-imposed a "you must still talk about assumptions" tax on standard
   methods, which is precisely the failure-mode-3 mistake c1 warned against (rewarding a paper that
   *needed* to justify nothing as if it had underperformed). For a metric that "composes as a veto
   gate," systematically capping the best case at 0.90 and dragging clean-standard to 0.50 will
   depress composite scores across well-behaved papers. Cycle 3: raise the STANDARD/in-scope ceiling
   toward 1.0 and stop penalizing assumption-silence on genuinely standard methods; reserve the
   engagement bonus for non-STANDARD tiers where it does real work.

4. **`source_ref` gate is likely inert.** `q.get("quote","") in known_limitations_refs` tests exact
   set-membership of the whole quote against the set of verbatim bullet texts. Real evidence quotes
   are spans *within* a bullet, not the entire bullet, so this membership test will rarely fire and
   the downgrade rarely triggers. Cycle 3: make it a containment test (quote is a substring of some
   known-limitations bullet) so the anchor requirement actually bites.

5. **Same fitness-check-vs-accuracy-number gap as A** (`self_verification_present` is quote-grounded
   for existence but not adjudicated as a real fitness check). Shared cycle-3 target below.

---

## Comparative read and shared cycle-3 directions

The two designs have converged on structure but split on **where the validity tier comes from**, and
this is the axis cycle 3 should resolve rather than paper over:

- **A has the real external signal** (`[sem]` tier), which is the metric's crux, but trusts the paper
  less in one place (tier classifier sees only search snippets, so it is already partly blind) and
  scores the standard case correctly (1.00).
- **B has the halo defense** (blind redaction) and the honest `external_tool_used` ceiling, but
  *skipped the external call itself* and mis-calibrated the standard case.

These are **complementary, not competing**. The right cycle-3 endpoint for *both* is: an external
`[sem]` tier lookup (A) whose *classification of the returned snippets* is run without the paper's
persuasive framing (B's blindness principle — note A's Step 2 already approximates this since the
classifier sees snippets, not paper prose), with `external_tool_used` genuinely toggling the residual
ceiling (B's honesty mechanism, applied to A's FALLBACK path), and A's STANDARD→1.00 calibration.

Shared directions for cycle 3 (apply to whichever line each expander carries forward):

1. **Close the verification-classification gap in both.** Quote-grounding proves a span *exists*; it
   does not prove the span is a fitness check rather than an accuracy number. Add a second grounded
   adjudication (or a closed enum of check-types: calibration / assumption-test / ablation /
   gold-standard-benchmark / internal-external-validation) that the span must map to, or verification
   credit is voided. This is the last open door on the metric's named second half.
2. **Make prominence robust to both verbosity (A) and idiosyncratic headings (B).** Combine a
   structural signal (named in a `## Statistical analysis`/`## Model`-type heading) with a
   canonicalized (acronym-folded) mention count, so neither repetition-to-rank nor
   nonstandard-headings can drop a load-bearing method out of the evaluated top-3 and re-open
   hide-the-bad-method beneath the min-aggregation.
3. **Reconcile verification magnitude.** A uses a flat +0.10 (barely registers, and does the *least*
   work on the most-contested methods since STANDARD is already capped); B uses tier-scaled
   +0.15/0.20/0.25 gated behind non-SILENT disclosure. Pick one principled schedule — verification
   should arguably do *more* work as tier gets more contested (where trust is most incomplete),
   provided it still cannot buy back a SILENT undisclosed extension.
4. **Reconcile the FALLBACK/knowledge-only residual cap.** A needs B's ceiling on non-external
   tiers; B needs A's actual external call so the ceiling means something. Both should end with:
   external-confirmed tier → full range; knowledge-only/fallback tier → capped, never `STANDARD`,
   scored down, never skipped.
5. **Fix the two concrete code defects** before cycle 3 scoring is trusted: A's broken
   `sanitize_field(..., general_knowledge_text=None)` fallback call, and B's inert exact-membership
   `source_ref` gate.

Both remain fully penalize-don't-skip compliant (every branch resolves to a number; missing
`constraints.md` → 0.0; abstract-only/thin → 0.05–0.08; non-extractable → 0.15/0.08). Neither has
regressed on the tighter-than-D6 edge — both still refuse to read sample size, p-values, or
study-design quality. The cycle-3 work is calibration and grounding-depth, not scope.
