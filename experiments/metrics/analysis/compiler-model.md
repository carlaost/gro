# The compiler model — assumed ground truth for V3

**Status: adopted as a working axiom (turn 20, crystallized as claim C16).** For V3 we stop
re-litigating whether the metrics "really measure the paper" and instead *assume* the model of the
compiler stated here. Every V3 design decision is justified against it. This is a design contract,
not a validated fact — see the "What this does NOT buy us" section: adopting it does **not** close the
external-validity gate (RC1/RC2).

Sources: `metrics-critique.md` (§1–§7), `research/metrics/v2/critiques-round2.md` (RC1–RC11), staged
observations O06/O11/O17/O18. The forensic examples below are transcribed from those docs.

---

## The core split: three layer classes, not one

The ARA compiler takes a paper (PDF + whatever code/data/trials exist) and emits a structured artifact
(claims, evidence, exploration trace, environment, related-work edges, …). The critique "the metrics
measure the compiler, not the paper" is **true for two of three layer classes and false for the
third.** A metric is only as valid as the layer it reads.

### 1. EXTRACTIVE layers — the compiler is a faithful re-view → metrics here are legitimate

Layers that *transcribe and re-organize what the paper actually says*: `claims.md` statements,
load-bearing numbers, `evidence/` tables and figures, the numeric grounding quotes.

- The compiler is acting as a careful reader that restates the paper in a cleaner schema.
- A metric computed on these layers **is** a metric on the paper. It inherits the paper's content, not
  the compiler's invention.
- **Consequence for V3:** metrics on extractive layers are *allowed to rank papers*. This is the
  concession that narrows the round-1 critique — the flagship claims+evidence work is **not**
  contaminated. (O18 concession; C16.)
- **Residual risk (bounded):** the compiler can mis-transcribe (wrong number, dropped qualifier). That
  is a *fidelity* error on a per-value basis, addressed by grounding checks (RC7) — not a reason to
  discard the whole layer.

### 2. HOMOGENIZATION — a faithful compiler still flattens → metrics here are non-discriminating

Layers the compiler fills *for every paper from the same template*, regardless of the paper: the
existence of a "Falsification criteria" field, the presence of cross-layer links, a filled
`environment.md` slot.

- Even a **perfect** compiler fills these uniformly. So a "presence" metric measures
  *field-population by the compiler*, not the paper's rigor.
- Evidence: `falsifiability_presence = 1.0` for every claim across all ARAs (metrics-critique.md §1);
  the "criteria" are mechanical post-hoc inversions the compiler wrote, not author pre-registration.
- **Consequence for V3:** homogenization metrics **cannot rank papers** — they have no paper-level
  variance by construction. They are demoted to the **artifact-trust axis** (hygiene/presence gates
  that feed a trust-weight `w`), never to the paper ranking. (RC6/RC10.)

### 3. FABRICATION — the schema outruns the source → the compiler invents → metric measures the compiler

Layers the ARA schema *demands* but the source paper structurally lacks. A review / meta-analysis /
guideline has no first-person exploration process, yet the schema wants an exploration trace with
dead-ends. The compiler fills the gap by **manufacturing content** — typically by negating the paper's
own conclusions into straw "abandoned hypotheses."

- These nodes are not a view of the paper; they are the compiler's creative writing.
- Evidence (transcribed):
  - che26 (network meta-analysis) `dead_end_density = 0.25`, driven entirely by invented nodes N11/N12
    with the hypothesis *"p-tau181 would remain competitive"* — a flip of the paper's own supported
    conclusion (`critiques-round2.md:39`).
  - `refutes = 0` corpus-wide; `corrective_science_score` runs on `bounds`/`extends` that just relabel
    "we beat the prior standard" (a baseline), not refutation (`critiques-round2.md:51`).
  - woj25 C04 is a *real* null ("plasma p-tau181&231 fails to differentiate, Cohen's d<0.2, AUC 0.514")
    but is filed `status: supported`, so the status-based negative-result metric scores it **zero**
    (`critiques-round2.md:63`).
- **Consequence for V3:** fabrication must be **stripped before counting**. A dead-end counts only on a
  positive binding to an author-documented failure; corrective credit only for an edge that addresses
  the prior claim's evidence; negatives detected by claim *semantics*, not by `status`. (RC3/RC4/RC5.)

---

## The design contract V3 must honor

| Layer class | Compiler behavior | V3 routing | Governing critiques |
|---|---|---|---|
| Extractive (claims, numbers, evidence) | Faithful re-view | **May rank papers** (`paper_rankers`) | RC5, RC7 (fidelity guard) |
| Homogenization (presence fields, links) | Uniform template fill | **Artifact-trust only** (feeds `w`, never ranks) | RC6, RC10 |
| Fabrication (dead-ends/RW on synthesis genres) | Invents to fill schema gap | **Strip via detectors, then rank the residue** | RC3, RC4, RC5 |

Operational rules that fall out of the model:
1. **Never rank a paper on a layer the compiler fabricated.** Detectors (RC3/4/5) must remove
   schema-gap inventions before any counting. A `dead_end` on a synthesis-genre paper is presumed
   synthetic unless it binds to a real author-reported failure.
2. **Never rank a paper on a homogenized presence field.** Route presence proxies to the trust axis;
   trust-weight `w` scales an ARA's contribution to *library-level* metrics but never lowers its own
   paper rank (the woj25 fix).
3. **Extractive metrics are fair game**, subject to a per-value fidelity check (RC7 semantic grounding)
   that catches mis-transcription without discarding the layer.

---

## What this does NOT buy us (the axis that survives a perfect compiler)

Adopting the compiler model as ground truth resolves *which layers are safe to rank on*. It does **not**
tell us whether ranking high on any of those layers correlates with **good science**.

- Compiler-fidelity and metric-validity are **independent axes.** A perfectly faithful re-view adds no
  external ground truth: re-representing a paper more cleanly does not reveal whether "high grounding"
  or "high corrective score" tracks reproducibility, expert quality, or eventual retraction.
- Therefore "these metrics cannot be *validated* on this corpus" (RC1/RC2) holds **regardless** of how
  good the compiler is. Assuming the compiler is perfect is the *most generous* case, and even there the
  validity gate stays open.
- **Honest predicted outcome (carried from the master's standing verdict):** once fabrication is
  stripped and homogenization is routed off the ranking, ~0–1 paper-rankers survive the validity gate on
  this 12-ARA corpus, and RC2 external validation cannot be properly powered at n=12. That is the gate
  working, not a V3 failure.

**In one line:** assume the compiler is a faithful re-view where it extracts, a flattener where it
homogenizes, and a confabulator where the schema outruns the source — build metrics that only rank on
the first, and remember that even a perfect re-view still needs an external yardstick to be called
valid.
