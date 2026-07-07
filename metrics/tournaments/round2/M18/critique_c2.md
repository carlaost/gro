# M18 Cycle-2 Critique: Claim Drift / Reference Truthfulness

Middle cycle. Both A (was exp2) and B (was exp4) advance to cycle 3; no final winner is picked
here. Metric = do cited sources actually say what they're cited for, checked against the REAL
external source ([ext]+[sem]) — net-new vs the verifier's L1 §10, which only confirms the quote
appears at a cited line inside the ARA. Judged on: reasoning correctness; a
concrete/sound/runnable source-fetch + entailment workflow that yields deterministic sub-scores;
Goodhart-resistance; penalize-don't-skip; preservation of the edge over L1 §10.

Both revisions closed all four of their assigned cycle-1 directions. The gap between them has
narrowed. Below: what each addressed, what is still weak, and specific cycle-3 directions.

---

## A (exp2) — revision assessment

### Did it address the cycle-1 directions?

1. **Calibrate the penalty constants — YES, well.** New Step 8 runs three concrete units
   end-to-end to final numbers, and the "Why these constants" note in Step 5 gives a real
   rationale (retrieval ladder ordered by remaining verification work; step sizes ~double so
   "wrong paper confidently asserted" 0.70 > "could not find it" 0.55; specificity/vague penalties
   sized to nudge within a tier, not across one; multi-source decrement capped so padding is
   strictly non-beneficial but sub-tier). This is the strongest calibration story in the field and
   makes the constants defensible rather than asserted.
2. **Gate the RW role/coverage weight — YES, and better than asked.** `rw_dependent` is computed
   from `logic/problem.md`'s own `external_dependency_signal`, not from `related_work.md`'s
   presence. That correctly defeats the "delete related_work.md to dodge the audit" route while
   redistributing the freed 0.25 weight proportionally when the problem is genuinely
   self-contained. Good.
3. **Adopt the explicit "quote exists ≠ source supports" instruction — YES.** Now stated in the
   Metric Intent prose AND opened prominently inside the Step 4 judging prompt. The L1 §10 edge is
   now explicit, not implied.
4. **Make source-identity resolution deterministic — YES.** The `match_score` formula
   (0.5·title_jaccard + 0.3·year + 0.2·author) with fixed thresholds routing to clean /
   identity_uncertain / unresolved / contradictory_identity removes the ungrounded
   "highest-confidence match" judgment call.

### What is still weak

- **CRITICAL — the contradiction cap is laundered by `max()`; prose and code disagree.** Step 5
  prose says "Contradiction cap: any `contradicted` judgment caps the unit at 0.10." But the Step 7
  code applies the cap to the *source's* base (`if support == "contradicted": base = min(base,
  0.10)`), appends it to `source_scores`, then sets `score = max(source_scores)`. So a unit citing
  one `contradicted` source (capped 0.10) and one `direct` source (1.0) scores `max(0.10, 1.0) =
  1.00`. Worse, `unresolved_or_bad` counts only `unsupported`/`unverifiable`, NOT `contradicted`,
  so the multi-source decrement never fires either. This is *exactly* the laundering hole B was
  directed to close in cycle 1 and did close — A's code leaves it wide open while its own prose
  claims otherwise. This is the single most important cycle-3 fix for A: it is a correctness bug,
  a Goodhart hole, and a self-inconsistency all at once.
- **`match_score` is under-defined for the dominant citation format in this artifact.** The
  §4 shape shows `Evidence` fields are author-year lists with NO titles (e.g. "§1 Introduction
  (Karikari et al., 2020; Mila-Aloma et al., 2022; ...)"). With no cited title, `title_token_jaccard`
  falls back to undefined "domain terms if available." An author+year-only citation can reach at
  most `0.3·year + 0.2·author = 0.50` even on a perfect author/year match, so it can NEVER reach the
  0.75 clean-resolve threshold — it is systematically routed to `identity_uncertain`, forced to
  `metadata_only`, and support-capped at `partial`. That means the metric will penalize essentially
  every well-formed real ARA (whose Evidence fields look exactly like the shape example) as
  identity-uncertain. The determinism is real but appears mis-calibrated against the actual input
  distribution.
- **`external_dependency_signal` is itself a softenable Goodhart surface.** A compiler that wants
  to dodge the RW-weight can phrase a genuine dependency implicitly ("we use a network
  meta-analysis approach") rather than naming it as reused/compared/bounded/extended/refuted, so
  the signal reads false. Less evadable than B's literal-RW-id trigger (see below), but still a
  language-level escape hatch worth acknowledging and hardening.

### Cycle-3 directions for A

1. **Fix the contradiction cap so it binds at the UNIT level regardless of co-cited support.**
   Make the code match the prose: after computing `score = max(source_scores)`, add
   `if any(j["support"] == "contradicted" for j in unit["judgments"]): score = min(score, 0.10)`.
   Show it in a fourth worked example (contradicted + direct bundle → 0.10), mirroring B's
   Step-6 worked example, so the fix is verifiable rather than asserted.
2. **Define `match_score` for title-less author-year citations — the common case.** Specify the
   title proxy explicitly (e.g. domain/key terms extracted from the unit `text` and `Evidence`
   context), and re-examine whether author+year+venue agreement should be able to reach clean
   resolve. Either lower the clean-resolve threshold for citations that structurally cannot carry a
   title, or add a venue/citationCount corroboration term — otherwise re-run Step 8's Unit
   O2-statement with a realistic author-year-only Evidence field and confirm it doesn't collapse to
   identity_uncertain. Calibrate against the shape file's own example.
3. **Harden `external_dependency_signal` against implicit-phrasing evasion.** Add a note (or a
   second detection pass) that a named methodology/dataset/comparator counts as an external
   dependency even when the reuse relationship is stated implicitly, so softening the verb doesn't
   flip `rw_dependent` to false.
4. Minor: the specificity penalty (−0.10) and vague cap (0.65) are now justified; state once
   whether they stack with the multi-source decrement on the same unit (worked example implies they
   can), so the worst-case floor is bounded and intentional.

---

## B (exp4) — revision assessment

### Did it address the cycle-1 directions?

1. **Add a bounded, gated cross-layer role-drift audit — YES.** New Step 7 borrows exp2's role
   audit (imports/baseline/bounds/extends/refutes vs the real source), gated on `referenced_rw_ids`
   being non-empty, with a penalize-don't-skip floor (`role_support = 0.0`, retained in denominator)
   when RW is needed but absent/unresolved, plus a distinct −0.05 artifact penalty for the
   self-created unresolved dependency. This closes B's only named cycle-1 gap and keeps problem.md
   dominant (RW_ROLE_WEIGHT = 0.15, only applied when triggered).
2. **Bound the external-call budget deterministically — YES.** New Step 0 adds fixed
   `AUDIT_CAPS`, a deterministic `tie_break_key` (numbers/comparators/causal verbs first, artifact
   order only as stable fallback), and a `resolution_only` overflow pass so cost is a fixed function
   of artifact size and overflow units are penalized-not-dropped.
3. **Pin down the multi-dimensional match sub-scores — YES.** Step 5 now ships 0.0/0.5/1.0 rubric
   anchors for scope/polarity/specificity/number, plus JSON-schema validation with one retry and a
   conservative `unverifiable`/0.0 fallback. The multiplicative combination is no longer
   noise-amplifying.
4. **Sanity-check contradiction propagation — YES, this is the standout fix.** B correctly
   *demonstrated* that the cycle-1 formula laundered a contradicted source (`bundle = 0.69` for a
   direct+contradicted pair) and added a hard `bundle ≤ 0.15` cap whenever any bundle source is
   `contradicted`, with the arithmetic shown both ways. This is exactly the discipline the brief
   rewards, and it is the same hole A still has open.

### What is still weak

- **The role-audit trigger is more evadable than A's.** `referenced_rw_ids` is populated by
  literal `RW##` token or entry-title/author string matches in the problem text. A compiler can
  lean heavily on external work while describing it generically (naming the method but never the
  RW id or the entry's author/title), so `referenced_rw_ids` stays empty and Step 7 never fires.
  This is the mirror of A's weakness but strictly easier to exploit — a pure token match is
  defeated by paraphrase, whereas A's semantic `external_dependency_signal` at least tries to catch
  the relationship. B should move toward semantic dependency detection.
- **`resolution_only` unit scoring aggregates an undefined per-citation quantity.** `unit_score`
  returns `min(0.5, unit.get("resolution_score", 0.0))`, but Step 3 defines resolution score
  *per citation*, and a unit can carry several. How the unit-level `resolution_score` is derived
  (max? mean? min?) is unspecified, so the overflow-pass number is not yet deterministic. Also, a
  cleanly-resolvable-but-drift-y overflow citation earns a flat 0.5 with no entailment check; on a
  large artifact the average could sit near 0.5 with zero truthfulness verification. Caps are
  generous enough that overflow is rare for typical 3–5-observation artifacts, so this is lower
  severity than A's contradiction bug, but it should be nailed down.
- **Unit-level dilution of contradiction.** The 0.15 cap is per atomic-claim `bundle`, then
  `unit_score = mean(claim_scores)`. A unit with one contradicted atomic claim (0.15) and one clean
  claim (0.9) averages to ~0.53. Defensible (distinct atomic claims may cite distinct sources), but
  worth stating explicitly whether a contradicted claim anywhere in a load-bearing unit should
  propagate more strongly, so the choice is deliberate rather than incidental.

### Cycle-3 directions for B

1. **Broaden the Step 7 trigger beyond literal RW-id/title token matching.** Add a semantic
   dependency signal (borrow the spirit of A's `external_dependency_signal`): fire the role audit
   when a Gap/Observation leans on a named external method/dataset/comparator that resolves to an
   `related_work.md` entry, even if the problem text doesn't cite the RW id verbatim. Otherwise the
   audit is defeated by paraphrase — the cheapest possible evasion.
2. **Make the `resolution_only` overflow score deterministic.** Specify how per-citation
   resolution scores aggregate to the unit `resolution_score` (recommend `max`, matching the
   best-supporting-source logic elsewhere), and confirm the 0.5 ceiling can't let a large batch of
   unaudited-but-resolvable units float an artifact's mean upward without any entailment check.
3. **State the unit-level contradiction propagation choice.** Decide and document whether a single
   contradicted atomic claim should cap the whole unit (as A's prose intends) or only its own
   bundle (current behavior). A one-line worked example either way would settle it.
4. Minor: Step 0 caps (8/8/6/6/6/5/5) are asserted; add one sentence tying them to expected
   artifact cardinality (§4 says typically 3–5 Observations, 2–4 Gaps) so it's clear the caps
   almost never bind for real artifacts and exist only as a runaway-cost guard.

---

## Cross-cutting note for cycle 3

The two proposals have converged on nearly the same architecture and now differ mainly on two
axes, each being the mirror of the other:

- **Contradiction handling:** B is correct and verified (hard unit/bundle cap, worked example);
  A is broken (prose says unit-cap, code does source-cap-then-`max`, laundering survives). A must
  fix this to stay competitive.
- **Role-audit trigger robustness:** A is more robust (semantic `external_dependency_signal` off
  the problem layer, undodgeable by deleting related_work.md); B is more evadable (literal RW-id/
  title token match, defeated by paraphrase). B should adopt A's semantic approach.

Whichever proposal imports the other's stronger half in cycle 3 will pull ahead. Both remain
strong on penalize-don't-skip and on preserving the L1 §10 edge (both now state
quote-exists ≠ source-supports explicitly in the judging prompt).
