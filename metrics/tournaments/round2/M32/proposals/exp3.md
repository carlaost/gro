# M32 — Method validity & verification status (expander 3)

## 1. Expanded reasoning

### What this indicator is actually about
M32 is not "was the method executed carefully" (that's D6/reproducibility territory). It is a narrower
question: **is the method the paper actually used warranted for the way it was used, and did the authors
make that warrant legible (argued, cited, or empirically checked) rather than just assumed?** Two papers
can both run a flawless, well-documented pipeline (high D6) while differing sharply on M32: one applies a
textbook method squarely inside its validated regime; the other quietly stretches a method past the
conditions under which it's known to work, and never says so.

Concretely, the metric should resolve one of four situations for the paper's primary method(s), as stated
in `logic/solution/{constraints.md, study_design.md, method.md, architecture.md, algorithm.md, heuristics.md}`:

1. **Established, in-scope** — a widely-validated method used the way it is normally validated (same data
   type/regime, assumptions plausibly holding).
2. **Established, but extended** — the base method is validated elsewhere, but applied here outside (or at
   the edge of) its known warrant (different population/modality, relaxed assumption, novel recombination
   of known components) — *and the paper says so and defends it*.
3. **Established, extended, undefended** — same stretch as (2), but never acknowledged or argued — silent
   over-generalization. This is the failure mode the metric exists to catch.
4. **Novel/bespoke method** — not an established method at all; validity rests entirely on whatever
   justification/verification the paper itself provides.

### What it must reward
- Explicit engagement with *this method's* known failure modes/assumptions in `constraints.md`
  (Boundary conditions / Assumptions / Known limitations) — not boilerplate "our study has limitations,"
  but assumption text specific to the method (e.g. proportional-hazards, exchangeability, i.i.d., cluster
  independence, distribution-shift, calibration drift).
- Honest labeling of extension/novelty *plus* a real defense: a theoretical argument, a citation of
  precedent for the extension, a sensitivity/ablation result, or an explicit "we could not fully validate
  X, see limitation Y."
- A genuine **method-level verification step** — internal or external validation, calibration check,
  benchmarking against a gold standard/ground truth, ablation isolating whether a component is load-bearing,
  or a stated assumption test (e.g. Schoenfeld residuals for proportional hazards). This is a check *on the
  method's fitness*, not a results/accuracy number (that belongs to other metrics).
- Consistency between the method-file *genre* chosen (study_design.md vs architecture.md vs algorithm.md)
  and what the paper actually did — a `training.md`/`architecture.md` forced onto a paper that trained no
  model is itself a validity-frame defect, not a naming quibble.

### What it must NOT reward
- Citing a method's name/fame as validity ("we used Cox regression, a well-established method") with no
  engagement of whether its assumptions hold here — name-dropping is not warrant.
- Generic limitations boilerplate that could be pasted into any paper in the field.
- Confidence or verbosity of the method write-up — a heavily detailed `method.md` with dense pipeline
  parameters (looks rigorous) but zero discussion of *why this method, here* should not score well; detail
  about execution is not justification of choice.
- Penalizing novelty per se — a genuinely novel method that is honestly flagged and defended/verified
  should outscore a "standard" method used silently outside its warrant.

### Failure modes / gaming routes this design must close
- **Name-drop laundering**: cite a validated method, never touch its assumptions → must not pass as
  "established-in-scope"; requires an explicit assumptions-engaged check.
- **Boilerplate limitations**: vague "generalizability may be limited" sentences must not satisfy
  justification — the rubric must demand specificity tied to the method's actual mechanism.
- **Reputation halo**: an LLM judge asked "is this a valid method?" will default to "yes" for famous
  methods (Cox, transformers, PCR) regardless of fit — the prompt must force the judge to check *fit to
  this use*, not fame.
- **Silence as a loophole**: if a paper simply never discusses method fitness, a naive scorer might treat
  "no red flags mentioned" as clean. Per the hard constraint, silence/absence must be actively penalized
  (an "unclear" floor band), not treated as N/A or neutral.
- **Mislabeling to dodge scrutiny**: an author might describe a genuinely novel adaptation using
  established-method language to avoid the "extended/novel" bar. Countered by grounding every semantic
  label in a verbatim quote (auditable) rather than trusting the paper's or compiler's framing wholesale.
- **Padding via detail**: dense method-file prose can look thorough without ever justifying the choice —
  the rubric separates "verification present" and "assumptions engaged" from mere length/detail.

### How the assessment-critique notes reshape the scope
The ledger flags M32 as top-10 specifically *because* it is net-new vs. the ARA verifier and a **tighter**
facet of D6 (general methodological rigor) — that edge must be preserved, so this design deliberately:
- Excludes anything already owned by D6/other verifiers: overall statistical correctness, reproducibility
  of numbers, documentation completeness, writing quality. Those are out of scope even if they show up in
  the same files.
- Reduces the semantic judgment to a small number of **independently falsifiable, quote-grounded fields**
  (warrant class, justified?, self-verified?, assumptions engaged?, genre mismatch?) rather than one
  holistic "rigor score," which is exactly the kind of fuzzy 1–10 judgment that would collapse back into
  D6's territory and be redundant with it.
- Keeps the artifact scope to §7 only (no reaching into results/evidence for outcome quality) — the metric
  is about the *warrant for the method*, not whether the method produced good numbers.

## 2. Generation / compute workflow

### Inputs (artifact fields, §7 only)
- `logic/solution/constraints.md` — always present; sections: `## Boundary conditions`,
  `## Assumptions`, `## Known limitations (§X.Y)`, optional `## Additional caveats surfaced during
  compilation`.
- `logic/solution/*.md` sibling method files — 0..N of `study_design.md`, `method.md`, `architecture.md`,
  `algorithm.md`, `heuristics.md`, `formalization.md`, `proofs.md`, `design.md` (whichever exist for this
  paper).

No cross-layer reads are used — the metric is deliberately confined to what §7 itself states, so it cannot
be gamed by reaching for favorable framing elsewhere (e.g. an optimistic abstract).

### Step 1 — Structural parse (deterministic, rule-based)
Parse `constraints.md` into its sections; enumerate which method files exist and their `##`/`###`
headings. Compute cheap, non-gameable structural signals:
- `has_constraints`: bool (should always be true; false is a severe artifact defect, not this metric's
  fault per se, but it removes all inputs this metric needs → floor score).
- `limitations_bullet_count`, `limitations_specificity`: count of `## Known limitations` bullets and a
  crude length/keyword check (bullet must be >1 sentence and not match a small blocklist of generic
  phrases like "further research is needed", "results may not generalize" with nothing else attached).
- `method_file_count`: number of sibling method files.
- `thin_source_flag`: true if `constraints.md` totals fewer than 2 bullets across all sections AND
  `method_file_count == 0` — this is the legitimate "abstract-only source" floor case described in the
  shape doc, distinguished from a defect by being *uniformly* thin (nothing anywhere to engage with), not
  selectively silent on method validity while detailed elsewhere.
- `genre_mismatch_candidate`: true if a method file name implies machinery not evidenced anywhere in its
  own body (e.g. `architecture.md` with no described components/layers, `training.md` with no described
  training procedure) — a cheap keyword/structure pre-check; confirmed or overridden by the semantic step.

### Step 2 — Semantic warrant classification ([sem] call)
One LLM call per artifact, over the concatenated text of `constraints.md` + all method files (each file
clearly labeled). This is the only semantic step; its output is a small structured JSON, not a holistic
score, to keep it falsifiable and scoped.

**Exact prompt:**
```
SYSTEM/TASK:
You are assessing METHOD VALIDITY AND VERIFICATION STATUS for a single research artifact's method
layer (§7 logic/solution/). You are given the full text of constraints.md and all sibling method files
(study_design.md, method.md, architecture.md, algorithm.md, heuristics.md -- whichever exist).

Your job is narrow: judge whether the method(s) used are a widely-validated method applied within their
known warrant, or an over-generalization/adaptation beyond that warrant -- and whether that warrant (or
its extension) is explicitly justified in the text. Do NOT rate general statistical rigor,
reproducibility, or writing quality -- only the method's fitness-for-use and whether that fitness is
argued or merely assumed.

Return strict JSON with exactly these fields:
{
  "method_name": "<short label for the primary method(s) actually used>",
  "warrant_class": "established-in-scope" | "established-but-extended" | "novel-or-adapted" | "unclear",
  "warrant_justified": true | false,
  "self_verification_present": true | false,
  "self_verification_description": "<one sentence, or empty string>",
  "assumptions_engaged": true | false,
  "genre_mismatch": true | false,
  "evidence_quotes": [{"field": "<field name above>", "quote": "<verbatim span from the input text>"}]
}

Rules:
- If the text gives no basis to decide a field, output "unclear" (for warrant_class) or false (for the
  booleans) -- never omit a field, never guess to fill a gap.
- Every field set to a non-default value (anything other than "unclear" / false) MUST be backed by at
  least one verbatim quote in evidence_quotes. A claim with no quote is invalid and must be downgraded to
  its default (unclear/false) before returning.
- Boilerplate is not evidence: a generic "our study has limitations" or "results may not generalize"
  sentence with no mechanism named does NOT satisfy assumptions_engaged or warrant_justified.
- Fame is not warrant: a method being standard/well-known elsewhere does not by itself justify
  "established-in-scope" -- check whether it is being used the way it is normally validated (same data
  type, same regime, same assumptions plausibly holding), based only on what the text says.
- self_verification_present means a check ON THE METHOD's validity (internal/external validation,
  calibration, benchmarking vs. ground truth, ablation isolating a component, an assumption test) --
  NOT a reported accuracy/results number.

INPUT:
<constraints.md verbatim text>
<method file 1: filename>
<method file 1 verbatim text>
... (repeat per method file)
```

**Post-processing guard**: any field whose value is non-default but has zero matching entries in
`evidence_quotes`, or whose quote does not appear (fuzzy-substring match, case/whitespace tolerant) in the
actual source text, is programmatically downgraded to its default value before scoring. This blocks
hallucinated justification from ever reaching the scorer.

### Step 3 — Deterministic scoring function
```python
from dataclasses import dataclass
from difflib import SequenceMatcher

@dataclass
class StructuralSignals:
    has_constraints: bool
    limitations_bullet_count: int
    limitations_specificity_ok: bool   # >=1 bullet passes the boilerplate/length check
    method_file_count: int
    thin_source_flag: bool
    genre_mismatch_candidate: bool

@dataclass
class SemJudgment:
    warrant_class: str          # "established-in-scope" | "established-but-extended"
                                 # | "novel-or-adapted" | "unclear"
    warrant_justified: bool
    self_verification_present: bool
    assumptions_engaged: bool
    genre_mismatch: bool
    evidence_quotes: list        # [{"field": str, "quote": str}]


def _quote_grounded(field: str, quotes: list, source_text: str, threshold: float = 0.85) -> bool:
    """A field's non-default value only counts if it has >=1 quote that actually
    appears (fuzzy match) in the source. Blocks hallucinated justification."""
    for q in quotes:
        if q.get("field") != field:
            continue
        quote = q.get("quote", "").strip()
        if not quote:
            continue
        # cheap fuzzy containment check over sliding windows of source_text
        window = min(len(quote) * 2, len(source_text))
        for i in range(0, max(1, len(source_text) - window), max(1, window // 2)):
            chunk = source_text[i:i + window]
            if SequenceMatcher(None, quote, chunk).ratio() >= threshold or quote in source_text:
                return True
    return False


def sanitize_judgment(sem: SemJudgment, source_text: str) -> SemJudgment:
    """Downgrade any non-default field lacking a grounded quote to its default."""
    if sem.warrant_class != "unclear" and not _quote_grounded("warrant_class", sem.evidence_quotes, source_text):
        sem.warrant_class = "unclear"
    for field in ("warrant_justified", "self_verification_present", "assumptions_engaged", "genre_mismatch"):
        if getattr(sem, field) and not _quote_grounded(field, sem.evidence_quotes, source_text):
            setattr(sem, field, False)
    return sem


# --- warrant_class base credit table ---------------------------------------
# Score band per (warrant_class, warrant_justified, self_verification_present, assumptions_engaged).
# Bounded to [0.0, 1.0]; "unclear" and undefended extensions are floored low by design
# (penalize-don't-skip: no N/A branch exists in this table -- every combination resolves to a number).

def _semantic_component(sem: SemJudgment) -> float:
    wc, wj, sv, ae = sem.warrant_class, sem.warrant_justified, sem.self_verification_present, sem.assumptions_engaged

    if wc == "established-in-scope":
        base = 0.75 if ae else 0.45          # named-but-not-engaged is only partial credit
        base += 0.15 if sv else 0.0          # verification is a bonus even in-scope
        return min(base, 1.0)

    if wc == "established-but-extended":
        if not wj:
            return 0.15                       # silent over-generalization: the exact failure mode M32 targets
        base = 0.55
        base += 0.20 if sv else 0.0
        base += 0.10 if ae else 0.0
        return min(base, 1.0)

    if wc == "novel-or-adapted":
        if not wj:
            return 0.05                       # novel AND undefended: highest-risk pattern, lowest score
        base = 0.45
        base += 0.25 if sv else 0.0
        base += 0.10 if ae else 0.0
        return min(base, 1.0)

    # wc == "unclear": artifact failed to make method warrant legible at all -> penalized floor, not N/A
    return 0.10


def score_m32(structural: StructuralSignals, sem: SemJudgment, source_text: str) -> dict:
    """Returns {"score": float in [0,1], "flags": [str, ...]} -- never returns None/NA."""
    flags = []

    # Hard floor: constraints.md missing entirely removes all inputs this metric needs.
    if not structural.has_constraints:
        return {"score": 0.0, "flags": ["constraints_missing"]}

    sem = sanitize_judgment(sem, source_text)

    # Legitimate thin-source floor (e.g. abstract-only compile): still scored, still low,
    # never skipped -- distinguished from selective silence by uniform thinness.
    if structural.thin_source_flag:
        flags.append("thin_source")
        return {"score": 0.08, "flags": flags}

    semantic = _semantic_component(sem)

    # Structural specificity gate: even a favorable semantic read is capped if the
    # limitations section itself is boilerplate/empty -- closes the "LLM was generous,
    # text was vague" gap between the two signals.
    if not structural.limitations_specificity_ok:
        flags.append("limitations_boilerplate_or_absent")
        semantic = min(semantic, 0.35)

    # Genre mismatch penalty (confirmed by either the rule-based pre-check or the sem call).
    if structural.genre_mismatch_candidate or sem.genre_mismatch:
        flags.append("genre_mismatch")
        semantic = max(0.0, semantic - 0.15)

    if sem.warrant_class == "unclear":
        flags.append("warrant_unclear")
    if sem.warrant_class == "established-but-extended" and not sem.warrant_justified:
        flags.append("undefended_extension")
    if sem.warrant_class == "novel-or-adapted" and not sem.warrant_justified:
        flags.append("undefended_novel_method")

    return {"score": round(semantic, 3), "flags": flags}
```

Every branch above resolves to a concrete number; there is no code path that returns "N/A" or skips
scoring for missing/thin/unclear inputs — missing `constraints.md` scores 0.0, a thin/abstract-only source
scores 0.08, and an "unclear" semantic read is floored at 0.10, all strictly below any engaged, justified
case. Availability of the field is itself part of the score, exactly per the hard constraint.

## 3. Why hard to Goodhart, and composition with the suite

**Hard to Goodhart because:**
- Every non-default semantic judgment must carry a verbatim, source-matched quote (`sanitize_judgment`
  programmatically strips ungrounded claims before scoring) — an author or compiler can't win by having the
  judge simply assert "warrant_justified: true"; the claim is checked against the actual text.
- The rubric explicitly instructs the judge to discount fame/reputation and boilerplate, and the structural
  gate independently caps the score when `constraints.md`'s limitations section is vague — so a generous
  LLM read cannot rescue a genuinely thin write-up (two independent signals must agree to score well).
- Silence scores lowest (`unclear` floor 0.10, thin-source floor 0.08, missing-constraints floor 0.0), so
  omission is never the optimal strategy — the dominant gaming route for a lot of "rigor" metrics (say
  nothing, hope no one notices) is explicitly the worst-scoring path here.
- Novelty is not penalized on principle — `novel-or-adapted` + `warrant_justified=True` +
  `self_verification_present=True` scores up to 0.80, higher than a merely name-dropped
  `established-in-scope` (0.45–0.75) — removing the incentive to mislabel a genuinely novel method as
  "standard" to dodge scrutiny.
- Gaming requires simultaneously satisfying a deterministic, rule-based structural check (real
  non-boilerplate limitations bullets, coherent file/genre naming) *and* a quote-grounded semantic
  judgment — harder to satisfy both cheaply than either alone.

**Composition with the rest of the suite:**
- Deliberately excludes general statistical/reproducibility rigor, execution quality, and numeric fidelity
  — those remain D6's and the evidence-layer metrics' job. M32 answers one question only: is the method's
  applicability here warranted, and is that warrant argued or verified.
- Complements evidence/results-fidelity metrics: a paper can execute a method flawlessly and reproduce its
  own numbers exactly (scoring well on those axes) while still applying it outside its valid warrant
  without saying so — M32 is the axis that catches that case specifically, which is why the ledger marks it
  net-new rather than redundant.
- Its flags (`undefended_extension`, `undefended_novel_method`, `warrant_unclear`) are cheap, legible
  signals other composite/claim-calibration metrics can consume directly — e.g. a claim-strength metric
  should discount generalization/causal claims more heavily when M32 flags an undefended extension on the
  method those claims rest on, without M32 itself needing to reach into the claims layer.

M32 expander3: done
