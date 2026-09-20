# M32 — Method validity & verification status (cycle 2, improved from exp3)

## Changes (cycle 2)

Base: exp3 (Round-2 winner, RANK 2). This revision fixes the three weaknesses the critique named
against exp3 specifically, and folds in the cross-winner merge directions (exp1's external-tier
core + exp1/exp2/exp4 hardenings) without losing exp3's core advantage — the only design that scores
*both* halves of the metric's name (validity **and** verification status) through auditable,
quote-grounded fields.

1. **(a) Single-method blind spot → multi-method min-weighted aggregation.** exp3 scored essentially
   one primary method. §2 Step 1 now extracts up to **3** candidate methods ranked by an explicit
   **prominence** rule (defined below — closing exp1's own undefined-"prominence" gap too), scores
   each independently, and aggregates via exp1's `0.4·mean + 0.6·min` blend (§3 Step 4). A paper can
   no longer bury one silently-overreached method behind two clean ones.
2. **(b) "Established-in-scope" resting on unguarded LLM self-report → split blind/full-text calls.**
   The single semantic call is now **two** calls: **Call A** ("blind tier") sees only a
   deterministically redacted, justification-stripped excerpt of the method description and must
   classify validity tier (`STANDARD`/`ADJACENT`/`NOVEL_OR_CONTESTED`/`UNKNOWN`) from domain knowledge
   *before* it can see how the paper defends itself — closing the specific halo route where a
   generous judge reads the paper's own confident framing and rubber-stamps "established-in-scope."
   **Call B** ("disclosure + verification"), given the full text, then does what exp3's single call
   did. Confirmed-vs-guessed tiers are tracked (`external_tool_used`) and unconfirmed tiers are
   score-capped (§3), rather than trusted at face value — directly answering the critique's point
   that exp3 had "no external confirmation that the method truly has the validation track record
   claimed."
3. **(c) Ad hoc `SequenceMatcher` sliding window → normalized-substring-first grounding.** `_quote_grounded`
   is rewritten: cheap `O(n)` normalized substring containment first, falling back to per-sentence
   (not arbitrary-window) fuzzy comparison only for quotes ≥40 chars, with a stricter 0.90 threshold.
   Deterministic, cheaper, and no longer arbitrary about window size/stride.
4. **Merge-direction items also adopted:**
   - exp1's `UNKNOWN`-is-at-least-as-demanding-as-`ADJACENT` floor discipline (§3).
   - exp2's source-ref requirement: a `JUSTIFIED` disclosure drawn from `## Known limitations (§X.Y)`
     must carry that `§X.Y` anchor or it is downgraded (§2 Call B rules, §3 sanitize step) — closes
     laundered justification that gestures at "we discuss this" without pointing anywhere real.
   - exp4's availability-ceiling instinct, applied to close a gap exp3 itself had: a paper with
     several *non-boilerplate* limitations bullets but **zero method files** previously could still
     reach a high semantic score off constraints.md alone. New rule: `method_file_count == 0` (and
     not already caught by `thin_source_flag`) caps the aggregate at 0.55 (§3).

Everything else — the four-situation taxonomy, quote-grounding-or-downgrade discipline, the
thin-source/missing-constraints hard floors, the §7-only scope, and the exclusion of D6's territory
— is retained unchanged because the critique did not fault it.

---

## 1. What this indicator is actually about (unchanged from exp3, restated)

M32 is not "was the method executed carefully" (D6). It answers: **is the method the paper actually
used warranted for the way it was used, and did the authors make that warrant legible — argued,
cited, or empirically checked — rather than assumed?** For each primary method, in
`logic/solution/{constraints.md, study_design.md, method.md, architecture.md, algorithm.md,
heuristics.md, formalization.md, proofs.md, design.md}`, the metric resolves:

1. **Established, in-scope** — validated method, used the way it's normally validated.
2. **Established, but extended** — validated elsewhere, applied here outside/at the edge of its known
   warrant — *and the paper says so and defends it*.
3. **Established, extended, undefended** — same stretch, never acknowledged — the failure mode the
   metric exists to catch.
4. **Novel/bespoke** — validity rests entirely on the paper's own justification/verification.

What it must reward and must *not* reward is unchanged from exp3 (name-dropping ≠ warrant; generic
limitations boilerplate ≠ justification; verbosity ≠ justification; novelty itself is never
penalized when honestly flagged and defended/verified). See exp3 §1 for the full discussion — not
repeated here since the critique raised no reasoning objection to it.

### Failure modes this design must close (exp3's list, plus two new ones from cycle 2)
- Name-drop laundering; boilerplate limitations; reputation halo; silence-as-loophole;
  mislabeling-to-dodge-scrutiny (all per exp3, mechanisms retained/hardened below).
- **NEW — hide-the-bad-method**: a paper with 3 methods, 2 clean + 1 silently overreached, must not
  average out to a comfortable score. Closed by min-weighted aggregation (§2 Step 1, §3 Step 4).
- **NEW — confident-framing halo**: a paper that *narrates* its method choice with high confidence
  ("Cox regression, the gold standard for survival analysis, was used...") must not thereby earn
  `STANDARD`/`established-in-scope` more easily than a paper that states the same fact plainly.
  Closed by the blind Call A redaction (§2 Step 2).

---

## 2. Generation / compute workflow

### Inputs (artifact fields, §7 only — unchanged scope discipline)
- `logic/solution/constraints.md` — always present.
- `logic/solution/*.md` sibling method files — 0..N.

No cross-layer reads. The metric cannot be gamed by reaching for favorable framing in the abstract or
elsewhere.

### Step 1 — Structural parse + candidate-method extraction (deterministic, rule-based)

Parse `constraints.md` into its sections; enumerate method files and their headings. Compute:

- `has_constraints`, `limitations_bullet_count`, `limitations_specificity_ok` (same boilerplate/length
  check as exp3), `method_file_count`, `thin_source_flag` (same definition: `constraints.md` totals
  fewer than 2 bullets across all sections AND `method_file_count == 0`), `genre_mismatch_candidate`
  (per method file, same cheap keyword/structure pre-check as exp3).

**New: candidate-method list with prominence ranking.** Extract up to **3** candidate method names via
a cheap heuristic pass over method-file headings and topic sentences (no semantics needed for
*extraction* itself — Call A confirms/relabels; this pass only proposes candidates and their rank so
the LLM calls have a bounded, ordered worklist):

- Prominence score = (a) +2 if the method is named as the subject/verb of a section titled like
  `## Statistical analysis`, `## Analysis pipeline`, `## Model`, `## Algorithm`, or the paper's own
  "Statistical Models"-style heading; (b) +1 per additional distinct file/heading that references the
  same method by name or acronym; (c) tie-break by file-genre order
  `study_design.md > method.md > architecture.md > algorithm.md > heuristics.md > formalization.md >
  proofs.md > design.md` (primary-to-supporting granularity), then by order of first mention.
- Keep the top 3 by this score. If fewer than 3 distinct methods are named anywhere, score only what
  exists (1 or 2) — never pad. If more than 3 exist, set `additional_unscored_methods: true` (an
  informational flag, not a penalty — methods beyond the top 3 are by construction supporting/auxiliary
  under this ranking, and their execution quality is D6's territory regardless).

**New: redacted description-only excerpt** (for Call A, deterministic sentence filter): from each
method file, drop any sentence containing hedge/justification cue tokens (`however`, `assumption`,
`limitation`, `we acknowledge`, `may not`, `unlike`, `in contrast to`, `caveat`, `validated`,
`well-established`, `gold standard`, `robust to`, `sensitivity analysis`) — keep the rest as
`description_only_text`. This is a lossy, cheap redaction (it will occasionally over- or under-strip),
but its purpose is narrow: reduce the paper's own persuasive self-framing bleeding into the *blind*
tier call, not achieve perfect blinding. Also pass through the `## Boundary conditions` bullets
unredacted (they describe scope/data-type, which Call A needs, and are not self-justification).

### Step 2 — Two-call semantic assessment

**Call A — Blind validity-tier classification** (one call, sees `description_only_text` +
`## Boundary conditions` + the ranked candidate list; does **not** see `## Assumptions`, `## Known
limitations`, or the un-redacted justification prose):

```
SYSTEM/TASK:
You are given a REDACTED excerpt of a research artifact's method description (self-justifying and
hedging sentences have been removed) plus its stated boundary conditions. You are also given a
ranked list of up to 3 candidate methods extracted from this artifact.

For EACH candidate method, classify its VALIDITY TIER using your own domain knowledge of how this
method is normally validated and used -- NOT based on how confidently or plainly the text describes
it (that framing has deliberately been stripped from method-description sentences; do not reward or
infer confidence from tone). Judge only whether the described USE (data type, population, regime,
assumptions implied by the boundary conditions) matches the method's known validated warrant.

Tiers:
- "STANDARD": this method, used this way, on this kind of data/regime, is squarely within how it is
  normally validated and applied.
- "ADJACENT": the base method is validated elsewhere, but this use relaxes/extends at least one
  condition of that validated regime (different population, modality, relaxed assumption, novel
  recombination of known components).
- "NOVEL_OR_CONTESTED": not an established method for this use at all, or actively debated/bespoke.
- "UNKNOWN": the text does not give you enough information to place it in a known regime, OR you are
  not confident enough in your own domain knowledge to classify it. Prefer UNKNOWN over guessing
  STANDARD -- a false "STANDARD" is worse than an honest "UNKNOWN".

Return strict JSON:
{
  "candidates": [
    {
      "method_name": "<string, from the candidate list or a corrected label if the candidate list
                       mis-extracted it>",
      "validity_tier": "STANDARD" | "ADJACENT" | "NOVEL_OR_CONTESTED" | "UNKNOWN",
      "tier_rationale": "<one sentence, knowledge-based, not text-based>",
      "evidence_quotes": [{"field": "validity_tier", "quote": "<verbatim span from the given excerpt
                            describing what data/regime this method was applied to>"}]
    }
    ... one entry per candidate, same order
  ]
}

Rules:
- Every non-"UNKNOWN" tier MUST carry at least one verbatim quote from the given excerpt describing
  the actual use (not a citation of the method's fame). No quote -> tier must be "UNKNOWN".
- Do not infer tier from how confidently the excerpt states the method choice; infer it from whether
  the described data/regime matches what you know of the method's validated conditions.
```

**Post-processing metadata**: record `external_tool_used = false` for this design (Call A is a
knowledge-only reasoning call). If a future deployment wires Call A to an actual retrieval/search tool
over a method-validation literature index, set `external_tool_used = true` for that run — the scoring
function (§3) treats confirmed and knowledge-only tiers differently, so this flag is load-bearing and
must be threaded through honestly rather than always set to the more generous value.

**Call B — Disclosure, verification, assumptions** (one call, full un-redacted text of `constraints.md`
+ all method files, given Call A's candidate list + tiers):

```
SYSTEM/TASK:
You are assessing METHOD VALIDITY AND VERIFICATION STATUS for a research artifact's method layer.
You are given the full, un-redacted text of constraints.md and all sibling method files, plus a list
of methods and their externally-assessed validity tier (already determined; do not re-derive it).

For EACH method in the list, determine:
- disclosure: does the paper, IN ITS OWN WORDS, acknowledge and defend using this method the way it
  did, if the tier is not STANDARD? ("JUSTIFIED" = real defense: theoretical argument, citation of
  precedent, a sensitivity/ablation result, or an explicit "we could not fully validate X, see
  limitation Y" tied to this method's actual mechanism. "ACKNOWLEDGED_UNJUSTIFIED" = the paper names
  the stretch/limitation but gives no real defense, just states it. "SILENT" = no acknowledgment at
  all.) For STANDARD-tier methods, still populate this field the same way (it is generally
  uninformative for STANDARD but must never be omitted).
- self_verification_present: is there a check ON THIS METHOD's fitness -- internal/external
  validation, calibration check, benchmarking vs. ground truth, ablation isolating whether a
  component is load-bearing, or a stated assumption test (e.g. Schoenfeld residuals for proportional
  hazards)? This is NOT a results/accuracy number.
- assumptions_engaged: does constraints.md's Assumptions/Known limitations section name an assumption
  SPECIFIC to this method's mechanism (not generic "our study has limitations")?
- genre_mismatch: does a method file's name imply machinery (e.g. "architecture.md", "training.md")
  not evidenced anywhere in its own body?
- source_ref: if disclosure evidence is drawn from a "## Known limitations (§X.Y)" bullet, the exact
  "§X.Y" string from that heading/bullet; otherwise "".

Return strict JSON:
{
  "methods": [
    {
      "method_name": "<matching the name from the given list>",
      "disclosure": "JUSTIFIED" | "ACKNOWLEDGED_UNJUSTIFIED" | "SILENT",
      "self_verification_present": true | false,
      "self_verification_description": "<one sentence, or empty string>",
      "assumptions_engaged": true | false,
      "genre_mismatch": true | false,
      "source_ref": "<string, may be empty>",
      "evidence_quotes": [{"field": "<field name above>", "quote": "<verbatim span>"}]
    }
    ...
  ]
}

Rules:
- Boilerplate is not evidence: generic "our study has limitations" or "results may not generalize"
  with no mechanism named does NOT satisfy assumptions_engaged, and does NOT make disclosure
  "JUSTIFIED".
- Every field set to a non-default value (anything other than "SILENT" / false / "") MUST be backed
  by at least one verbatim quote in evidence_quotes. No quote -> downgrade to default before
  returning.
- If disclosure = "JUSTIFIED" and the defense is drawn from a "## Known limitations (§X.Y)" bullet,
  source_ref MUST be populated with that §X.Y anchor. A "JUSTIFIED" claim that both (a) attributes
  itself to Known limitations and (b) has an empty source_ref is invalid.
```

### Step 3 — Post-processing guard (deterministic, both calls)

Every non-default field from Call A and Call B must have a matching, source-grounded quote or is
programmatically downgraded to its default (`UNKNOWN` / `SILENT` / `false` / `""`) before scoring.
This is exp3's core anti-hallucination discipline, applied to both calls, with the grounding check
itself hardened (fixing weakness (c)):

```python
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def _quote_grounded(field_name: str, quotes: list, source_text: str) -> bool:
    """Cheap normalized-substring check first (O(n)); fuzzy per-sentence fallback only
    for longer quotes, avoiding the arbitrary sliding-window scan from cycle 1."""
    norm_source = _normalize(source_text)
    sentences = None  # lazily split only if needed
    for q in quotes:
        if q.get("field") != field_name:
            continue
        quote = q.get("quote", "").strip()
        if not quote:
            continue
        norm_quote = _normalize(quote)
        if norm_quote and norm_quote in norm_source:
            return True
        if len(quote) >= 40:
            if sentences is None:
                sentences = re.split(r"(?<=[.!?])\s+|\n+", source_text)
            for sent in sentences:
                if SequenceMatcher(None, norm_quote, _normalize(sent)).ratio() >= 0.90:
                    return True
    return False


@dataclass
class TierJudgment:
    method_name: str
    validity_tier: str          # STANDARD | ADJACENT | NOVEL_OR_CONTESTED | UNKNOWN
    evidence_quotes: list
    external_tool_used: bool = False


@dataclass
class DisclosureJudgment:
    method_name: str
    disclosure: str             # JUSTIFIED | ACKNOWLEDGED_UNJUSTIFIED | SILENT
    self_verification_present: bool
    assumptions_engaged: bool
    genre_mismatch: bool
    source_ref: str
    evidence_quotes: list


def sanitize_tier(t: TierJudgment, source_text: str) -> TierJudgment:
    if t.validity_tier != "UNKNOWN" and not _quote_grounded("validity_tier", t.evidence_quotes, source_text):
        t.validity_tier = "UNKNOWN"
    return t


def sanitize_disclosure(d: DisclosureJudgment, full_source_text: str, known_limitations_refs: set) -> DisclosureJudgment:
    for f in ("self_verification_present", "assumptions_engaged", "genre_mismatch"):
        if getattr(d, f) and not _quote_grounded(f, d.evidence_quotes, full_source_text):
            setattr(d, f, False)
    if d.disclosure == "JUSTIFIED" and not _quote_grounded("disclosure", d.evidence_quotes, full_source_text):
        d.disclosure = "SILENT"
    # source-ref gate (exp2's idea): a JUSTIFIED claim whose only grounded quote actually lives
    # inside a "## Known limitations (§X.Y)" bullet must carry that §X.Y in source_ref.
    if d.disclosure == "JUSTIFIED":
        quote_in_known_limitations = any(
            _quote_grounded("disclosure", [q], full_source_text) and q.get("quote", "") in known_limitations_refs
            for q in d.evidence_quotes if q.get("field") == "disclosure"
        )
        if quote_in_known_limitations and not d.source_ref.strip():
            d.disclosure = "ACKNOWLEDGED_UNJUSTIFIED"
    return d
```

*(`known_limitations_refs` is populated during Step 1's structural parse: the verbatim text of each
`## Known limitations (§X.Y)` bullet, so Step 3 can tell whether a "JUSTIFIED" quote came from there.)*

### Step 4 — Deterministic scoring

```python
def _method_component(tier: str, disclosure: str, sv: bool, ae: bool, external_tool_used: bool) -> float:
    """Per-candidate-method score in [0, 1]. Every branch resolves to a number --
    penalize-don't-skip: there is no UNKNOWN/undefined-tier branch that returns None."""

    if tier == "STANDARD":
        base = 0.70 if ae else 0.50
        base += 0.15 if sv else 0.0
        ceiling = 1.0 if external_tool_used else 0.90   # unconfirmed tier: residual epistemic cap
        return min(base, ceiling)

    if tier == "ADJACENT":
        if disclosure == "SILENT":
            return 0.12                                  # the exact failure mode M32 targets
        if disclosure == "ACKNOWLEDGED_UNJUSTIFIED":
            return 0.22                                  # named but not defended: still low
        base = 0.55 + (0.20 if sv else 0.0) + (0.10 if ae else 0.0)
        ceiling = 1.0 if external_tool_used else 0.90
        return min(base, ceiling)

    if tier == "NOVEL_OR_CONTESTED":
        if disclosure == "SILENT":
            return 0.05                                  # novel AND undefended: highest-risk pattern
        if disclosure == "ACKNOWLEDGED_UNJUSTIFIED":
            return 0.10
        base = 0.45 + (0.25 if sv else 0.0) + (0.10 if ae else 0.0)
        return min(base, 1.0)                            # no external tier exists for novel methods
                                                          # by definition, so no external-cap applies

    # tier == "UNKNOWN": at least as demanding as ADJACENT at every disclosure level, and its
    # ceiling can never reach ADJACENT/STANDARD-justified territory since the tier itself is
    # unresolved -- silence/unclarity is never the optimal strategy.
    if disclosure == "SILENT":
        return 0.08
    if disclosure == "ACKNOWLEDGED_UNJUSTIFIED":
        return 0.15
    base = 0.45 + (0.15 if sv else 0.0) + (0.10 if ae else 0.0)
    return min(base, 0.75)


def aggregate_methods(component_scores: list[float]) -> float:
    """exp1's min-weighted blend: one silently-mismatched method among several good ones
    cannot be diluted away. Never returns a value above the weakest method's score by more
    than the mean would allow."""
    if not component_scores:
        return 0.0
    mean_score = sum(component_scores) / len(component_scores)
    return 0.4 * mean_score + 0.6 * min(component_scores)


def score_m32(structural, candidates: list[dict], source_text: str, known_limitations_refs: set) -> dict:
    """candidates: list of {tier_judgment, disclosure_judgment} pairs, already sanitized.
    Returns {"score": float in [0,1], "flags": [...]} -- never None/NA."""
    flags = []

    if not structural.has_constraints:
        return {"score": 0.0, "flags": ["constraints_missing"]}

    if structural.thin_source_flag:
        return {"score": 0.08, "flags": ["thin_source"]}

    if not candidates:
        # constraints.md exists and isn't thin, but no method could be extracted at all --
        # still scored, still low, never skipped.
        flags.append("no_method_identifiable")
        return {"score": 0.08, "flags": flags}

    component_scores = []
    for c in candidates:
        t, d = c["tier_judgment"], c["disclosure_judgment"]
        s = _method_component(t.validity_tier, d.disclosure, d.self_verification_present,
                               d.assumptions_engaged, t.external_tool_used)
        component_scores.append(s)
        if t.validity_tier == "UNKNOWN":
            flags.append(f"warrant_unclear:{t.method_name}")
        if t.validity_tier == "ADJACENT" and d.disclosure != "JUSTIFIED":
            flags.append(f"undefended_extension:{t.method_name}")
        if t.validity_tier == "NOVEL_OR_CONTESTED" and d.disclosure != "JUSTIFIED":
            flags.append(f"undefended_novel_method:{t.method_name}")
        if d.genre_mismatch:
            flags.append(f"genre_mismatch:{t.method_name}")

    aggregate = aggregate_methods(component_scores)
    if max(component_scores) - min(component_scores) > 0.30:
        flags.append("method_diluted_by_min")   # informational: surfaces hide-the-bad-method attempts

    # Structural specificity gate (exp3, unchanged): favorable semantics can't survive vague/absent
    # limitations text.
    if not structural.limitations_specificity_ok:
        flags.append("limitations_boilerplate_or_absent")
        aggregate = min(aggregate, 0.35)

    # Genre mismatch penalty (structural pre-check OR confirmed by Call B), applied once at the
    # aggregate level in addition to the per-method flag above.
    if structural.genre_mismatch_candidate or any(c["disclosure_judgment"].genre_mismatch for c in candidates):
        aggregate = max(0.0, aggregate - 0.15)

    # NEW: availability ceiling for "constraints.md has real content but zero method files" --
    # closes the gap where exp3 could score a method purely off constraints.md prose with no
    # method-file evidence at all. Availability of the artifact is itself part of the score.
    if structural.method_file_count == 0:
        flags.append("no_method_file_present")
        aggregate = min(aggregate, 0.55)

    if structural.additional_unscored_methods:
        flags.append("additional_unscored_methods")

    return {"score": round(aggregate, 3), "flags": flags}
```

Every branch resolves to a concrete number: missing `constraints.md` → 0.0; thin/abstract-only source
→ 0.08; no method identifiable at all → 0.08; every per-method combination of tier × disclosure × sv ×
ae → a number strictly ordered so that silence/unclarity is always dominated by engagement, exactly as
in exp3 — this property is preserved, not weakened, by the multi-method extension.

---

## 3. Why hard to Goodhart, and composition with the suite

**Hard to Goodhart because:**
- **Two independent semantic signals, not one.** Call A (blind, redacted, knowledge-only) and Call B
  (full text, disclosure-focused) must independently agree with the source for their respective claims
  to survive `sanitize_tier`/`sanitize_disclosure`. An author can no longer win the tier judgment
  merely by writing confidently — the confidence-carrying sentences are stripped before Call A ever
  sees them.
- **Quote-grounding is universal, not partial.** Every non-default field in both calls needs a
  verbatim, source-matched quote or is programmatically downgraded — carried over from exp3 and now
  also applied to Call A's `validity_tier` and Call B's `source_ref`-anchored `disclosure`.
- **Min-weighted aggregation closes the dilution route.** `0.4·mean + 0.6·min` across up to 3
  prominence-ranked methods means a paper cannot bury one silently-overreached method behind two
  well-warranted ones; `method_diluted_by_min` surfaces exactly this pattern for downstream consumers.
- **`UNKNOWN` is never the cheap way out.** It is scored at least as demanding as `ADJACENT` at every
  disclosure level (0.08/0.15/≤0.75 vs. 0.12/0.22/≤0.90–1.0) — a paper cannot dodge scrutiny by writing
  so vaguely about its method that even Call A can't place it; vagueness is punished, not rewarded, and
  the model is explicitly instructed to prefer honest `UNKNOWN` over a guessed `STANDARD`, which
  prevents `UNKNOWN` from becoming an accidental grading loophole in the other direction (guessed-high
  tiers polluting the pool).
- **External-confidence honesty is load-bearing.** `external_tool_used` gates the ceiling on
  `STANDARD`/`ADJACENT`-justified scores (0.90 vs 1.0) — a knowledge-only tier call can never fully
  match the confidence of a genuinely externally-verified one, which is the direct fix for "reputation
  claimed but never checked."
- **Source-ref requirement closes laundered defense.** A `JUSTIFIED` disclosure that claims to come
  from `## Known limitations (§X.Y)` but carries no matching `§X.Y` anchor is downgraded to
  `ACKNOWLEDGED_UNJUSTIFIED` — closing the specific route where a compiler or author gestures at "this
  is discussed in our limitations" without it actually being locatable.
- **Silence, thinness, and missing method files all score at or near the floor** (0.0 / 0.08 / 0.08,
  and now also the new 0.55 ceiling for zero-method-files-but-nonthin-constraints) — omission is never
  the optimal strategy at any granularity the design can detect.

**Composition with the rest of the suite (unchanged from exp3):**
- Excludes general statistical/reproducibility rigor, execution quality, and numeric fidelity — D6's
  and the evidence-layer metrics' job. M32 answers one question only, now at the level of *each*
  prominent method rather than just the single most obvious one.
- Complements results-fidelity metrics: a paper can execute flawlessly and reproduce its own numbers
  (scoring well elsewhere) while applying a method outside its warrant without saying so — M32 catches
  this, and now catches it even when that method is method #2 or #3 rather than the headline one.
- Its flags (`undefended_extension:<method>`, `undefended_novel_method:<method>`, `warrant_unclear:
  <method>`, `method_diluted_by_min`, `no_method_file_present`) remain cheap, legible signals other
  composite/claim-calibration metrics can consume directly — e.g. a claim-strength metric should
  discount generalization claims more heavily when M32 flags an undefended extension on *any* of the
  methods those claims rest on, not just the first one it happens to check.

M32 improved (cycle 2, from exp3): done
