# V3 good-science metrics — convergent findings after 3 adversarial cycles

*Autonomous critique→improve loop, 2026-07-05/06. Three independent Fable metascientist critiques
(`critiques/cycle{1,2,3}.md`), each acted on. This is the honest bottom line. Full trail in `loop-log.md`.*

## The headline finding

**On this corpus, the metric system measures compiler FIDELITY, not science QUALITY — and that is a
property of the corpus, not a fixable bug in the metrics.** Every metric that claimed to rank *papers*
by *quality* was shown, under adversarial scrutiny, to be either (a) driven by compiler artifacts,
(b) a fidelity/transcription check mislabeled as quality, or (c) non-discriminating. After removing the
mislabeling honestly, **0 of 6 paper-rankers are usable** (survive a variance × validity gate). This is
not a failure of the loop — it is the loop working: it converged on a true negative.

**What DOES carry signal is at the CLAIM level, anchored to something outside the compiler:**
- **3 claims** are endpoint-concordant with registered clinical-trial results (jes26:C01, sal25:C01/C02).
- **4 claims** are hand-verified priority over-claims caught via prior literature (sal25:C01 "first
  head-to-head" predated by a Feb-2025 review; sal26:C01; huu25:C05; woj25:C04) — catches **no
  compiler-based check could make**, because they require the outside literature.
- **1 claim** is a confirmed compiler polarity inversion (jes26:C09 — "clearance maintained" vs the
  paper's "amyloid reaccumulates"), caught by measuring extractive fidelity against full text.
- **1 trial's primary endpoint was amended** (jes26/NCT04437511: registered primary CDR-SB → iADRS at a
  timestamped registry version; the paper headlines iADRS). This is the first validation signal in the
  project with a **live failing branch** (un-fakeable, timestamped pre-registration; measures a research
  *behavior* not transcription) — but its one firing is a **benign, blinded, pre-specified trial-level
  amendment** (the change predates the earliest unblinded readout by ~8 months, and it is the *trial's*
  event, not this post-hoc reanalysis paper's), so on this corpus outcome-switching yields **0 detected
  misconduct**. sal25 = consistent; sal26/cum26 = structurally out of scope. The signal is soundly built
  but corpus-starved: n=3 trial-linked ARAs, all clean/benign, no positive control. (It needs a known
  data-driven-switch case — e.g. from the COMPare/RIAT catalog — to prove it *discriminates*, not just
  *fires*.)

These are real because they anchor to external ground truth (a registry, prior literature, the source
PDF). Everything computed purely from the compiler's own output measures the compiler.

## Why the paper-ranking axis is dead (and should be retired, not tuned)

| What we tried | Why it failed |
|---|---|
| Rank papers on process-transparency (dead-ends, corrective science) | Compiler *fabricates* these on synthesis genres; after stripping fabrication → non-discriminating / invalid |
| Rank on grounding / falsifiability presence | Homogenization — compiler fills the same fields for every paper (pinned at 1.0) |
| Rank on [sem] judge scores (evidence-relevance, scope, falsifiability quality) | Reliable (κ≈0.89) but they detect *compiler* errors, not paper quality; falsifiability-quality is at chance (κ=−0.03) |
| Rank on trial-linkage | Unnormalized name-drop count (a review "wins" by citing 8 trials) |
| "validated" as a gate | Meant "an LLM ran" — variance with extra steps |

After all corrections: 6 rankers → 1 surviving genre bucket → **0 usable**. The apparatus is empirically
retired. (Cycle 4 R1: move it to an appendix; make the claim the unit of the headline.)

## The compiler-model axiom (C16), measured

The founding assumption — "the compiler's extractive layer is a faithful re-view, so metrics on it rank
the paper" — was measured against full text (10/12 ARAs): **overall extractive fidelity 0.918**; 8/10
ARAs perfectly faithful; 2 with ranking-flipping infidelities (jes26 polarity inversion; woj25 number
mismatch + inversion). **Verdict: gate, don't withdraw** — true per-ARA where measured, false as a
blanket axiom. Now enforced as a severity-weighted gate (a flipped conclusion or wrong number excludes an
ARA from ranking; an added interpretive clause does not). *Final wording of claim C16 is flagged for
Carla at ARA node N47.* One earlier "infidelity" (huu25 MAPT) was **retracted** — it was a pdftotext
artifact stripping italic gene symbols, not a compiler error.

## The actual unlock (what this corpus structurally cannot provide)

Three signals that would measure *science* are unreachable here, and no amount of metric engineering
fixes them — they require a different corpus:

1. **Corroboration → replication** needs a **multi-topic, independent-discovery corpus.** At single-topic
   n=12, cross-paper "corroboration" clusters are same-trial-family artifacts (correctly labeled
   exploratory, correctly ~zero).
2. **A real "validated" verdict** needs a **held-out, expert-labeled quality set** to correlate metrics
   against. Without an external science-quality label, every metric is definitionally a
   consistency/fidelity check. This ingredient has been missing every cycle.
3. **The only un-gameable science signal is reproduction**, which needs **code-shipping papers** (runnable
   code + data). AD clinical/biomarker papers ship no code, so this corpus can never yield a reproduction
   outcome — the ceiling.

**Concrete recommendation: to actually measure good science, change the corpus** to a cross-domain set
that includes computational, code-shipping papers across multiple topics, plus a held-out expert-labeled
subset. The metric scaffolding (two-axis routing, validity×variance gate, fabrication detectors, external
anchoring, severity-weighted fidelity gate) is sound and ready; it is starved of a corpus that can
exercise it.

## What is genuinely reusable (the scaffolding is good)

- **The claim-graph external-anchor engine** (`claim_graph.py`): ChEMBL resolvability (as a fabrication
  check), per-claim trial-endpoint concordance, PubMed/bioRxiv novelty-vs-prior-literature. This is the
  Goodhart-resistant core and the direction that worked.
- **Severity-weighted extractive-fidelity gate** (`extractive_fidelity.py`): measures compiler faithfulness
  vs source, per-ARA.
- **The validity×variance honesty gate** (`compute_metrics_v3.py`): refuses to call anything usable that
  is merely varying or merely LLM-scored.
- **The validator-reliability harness** (`validator_reliability.md`): κ on the judges before trusting them.

## Honest status line

**Usable paper-rankers: 0/6 (axis retired). Endpoint-concordant claims: 3. Hand-verified priority
over-claims: 4. Confirmed compiler inversions: 1. Outcome-switching misconduct detected: 0 (signal built,
corpus-starved). Corpus verdict: cannot measure good science at n=12 single-topic no-code — the finding
IS the ceiling, and the unlock is a different corpus, not another metric.**

*Convergence confirmed by Fable critique round 4 (VERDICT: CONVERGED, `critiques/cycle4.md`): R1–R7
verified real in code/data; no science-measuring in-place work remains; next move is Carla's corpus.*
