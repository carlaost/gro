## Changes (cycle 2)

Responding directly to `critique_c1.md`'s cycle-2 directions for exp3 (kept as WINNER rank 2, alongside
exp2's deterministic warrant matrix as the named cross-pollination target):

1. **Type-awareness is no longer concentrated in one freeform `[sem]` judgment.** Step 2's single
   `type_check: pass|fail` field is replaced by a per-genre **deterministic checklist** (`GENRE_CHECKLIST`,
   §2.3) — a fixed, enumerable list of boolean sub-checks per genre (borrowing the spirit of exp2's warrant
   matrix, adapted to this metric's genre-rubric design rather than copying its design-tier×claim-type
   grid). Each checklist item is independently returned with its own one-line rationale, so a reviewer can
   spot-check any single boolean against its evidence citation instead of trusting one holistic verdict.
   The composite score is now a graded function of *fraction of checklist passed*, not a binary 0.4-vs-1.0
   cliff.
2. **Genre inference now has a scored fallback, not silent keyword-only classification.** §2.1's
   `infer_genre` is replaced by `resolve_genre`, which (a) computes a keyword-vote confidence, (b) triggers
   a closed-label `[sem]` fallback whenever confidence is low *or* two genres tie on keyword votes, (c)
   treats disagreement between the keyword vote and the constraints.md method-file naming (already
   cross-checked in cycle 1) as a confidence cap rather than a silent override, and (d) carries the
   resulting `genre_confidence` forward into scoring at two points (entailment multiplier and the
   non-clinical bias ceiling) so an ambiguously-labeled artifact cannot buy full credit on the strength of a
   confident-sounding single label.
3. **`not_applicable_genre` tightened from a flat `0.6` to `0.35`, and made confidence-sensitive.** The
   critique flagged `0.6` as too generous for an axis that categorically cannot be audited. It is now
   `0.35 * (0.5 + 0.5 * genre_confidence)`, i.e. it tops out at `0.35` only when genre classification is
   itself confident, and shrinks further when it isn't. This closes a genre-mislabeling Goodhart route that
   cycle 1 did not consider (see §3, new failure mode #6): an attacker who frames a clinical-shaped setup
   ambiguously enough to dodge into `theory_or_other` used to land in a *cushier* bucket (`0.6`) than an
   honestly-labeled but unregistered clinical trial (`0.1`) — a perverse incentive to obscure genre. The new
   ceiling removes that incentive by pricing the escape route as expensive when it is achieved through low
   classification confidence.
4. **Fabricated/mismatched-NCT guard spelled out explicitly**, matching exp2's condition-overlap
   discipline. Cycle 1's registry check only handled "no id" / "id doesn't resolve" / "id resolves but
   posted results/status/endpoint-framing disagree." It had no check for the case where a cited NCT id
   *resolves* but to a trial studying a different population or intervention than the claim describes —
   i.e., a fabricated or careless citation that is *worse* than admitting no registration exists. §2.4 adds
   `condition_overlap_fn`, a closed-label `[sem]` sub-call comparing the claim's `Setup.Population`/
   `Setup.Intervention` against the registry's condition/intervention/arm fields, and scores
   `no_overlap` at `0.0` — strictly below the `0.1` an honestly-unregistered clinical claim receives, and
   below the tightened `0.05` for an unresolvable id (also lowered from `0.2`, since citing an id that
   cannot even be looked up is closer to fabrication than to honest omission and should not out-score a
   genuine "we didn't register" admission by as much as cycle 1 allowed).
5. **Composite weighting is unchanged (0.65/0.35 entailment/bias, floor as multiplicative cap)** — the
   critique did not fault this and the multiplicative floor was explicitly called out as load-bearing; it is
   preserved verbatim rather than re-litigated.

Everything below is the complete, self-contained cycle-2 metric spec (not a diff) so it can be read and run
on its own.

---

# M19 — Claim↔Experiment↔Evidence entailment (+ publication-bias) — cycle 2 (improved, track B)

## 1. Expanded reasoning

### 1.1 What "good science" signal this indicator actually captures

Every other claim-adjacent metric in this suite (comprehensiveness, sourcing/grounding, falsifiability
phrasing) checks whether the *pieces are present and internally well-formed*. None of them checks the
thing a reader ultimately cares about: **does the chain from Statement → Proof → Evidence actually hold
as an argument?** A claim can have a perfectly-formatted `Sources` entry, a `Proof` pointing at a real
`E##`, and an experiment with dense `Setup`/`Procedure` fields — and still not be *entailed*, because:

- the experiment tests something adjacent to, but not identical to, the claim (scope slippage — e.g.
  `E03` measures DEG counts in white-matter SpDs, but `C03`'s Statement asserts a genome-wide effect);
- the `Expected outcome` is directional ("DEGs concentrate in white-matter...") but the evidence table
  it cites shows the *opposite* concentration, or shows no statistically distinguishable concentration
  at all;
- the entailment is type-inappropriate for the field's own evidentiary standard — an RCT claim citing a
  single-arm observational `Setup` as if it were randomized evidence; a mass-spec assay claim citing an
  immunoassay comparator; a "significant" claim whose cited forest-plot CI actually crosses zero (visible
  directly in `05_experiments.md`'s own worked example: Figure 3 Panel A shows `p231_UGOT: MD 0.00 [-0.07;
  0.07]` — a CI crossing zero — which must NOT entail a "significant advantage" claim even if the prose
  elsewhere asserts one).

This is **type-aware** entailment, not generic NLI: the criterion for "does the evidence support the
claim" is different for a statistical-synthesis claim (needs CI/p-value discipline) vs. a DEG-count claim
(needs FDR threshold discipline) vs. a proof-obligation claim (needs the proof sketch to actually close,
not just gesture at a theorem name) vs. a clinical-endpoint claim (needs randomization + the *actual*
pre-registered endpoint, not a relabeled one). Cycle 2 keeps this framing but stops relying on a single
LLM call to hold all four rubrics in its head at once (see §1.3 #6 and §2.3): the rubric is now a fixed
per-genre checklist, and genre itself is a scored classification rather than an assumed label.

The **publication-bias cross-check** is the second, structurally distinct half. `logic/experiments.md`
and `logic/solution/study_design.md` are declarative — by design they contain the paper's *own* account
of what it measured and found directionally. They cannot, by construction, tell you what the same
underlying trial *would have reported had all pre-registered endpoints been disclosed*. That requires an
external, adversarial source: the clinical-trial registry. If an experiment's `Setup` (or `problem.md`
Observations, or `study_design.md`'s `Reporting standard and registration` section) names a registered
trial, the registry is ground truth for what was *promised* — primary/secondary endpoints, planned
analyses, status — independent of what the compiled ARA chose to foreground. A mismatch (claim reports a
secondary endpoint as if primary; registry shows the trial was terminated early; registry lists an
endpoint the paper never mentions; **or the cited id resolves to a trial studying a different population
or intervention entirely**) is a **publication-bias / selective-reporting (or citation-fabrication)
signal that no other in-suite metric can see**, because every other metric only ever looks *inside* the
artifact. This is exactly why the assessment-critique ranked this metric net-new against the ARA verifier
(which checks D1 — claim/evidence internal consistency — semantically, i.e. still inside the artifact)
and against round-1 proposals (which stopped at internal entailment).

### 1.2 What it must reward, and what it must not

**Reward:**
- A `Statement` whose asserted relationship (direction, comparator, magnitude class, significance) is
  fully reconstructable from `Setup + Procedure + Metrics + Expected outcome` in the linked `E##`, AND
  is consistent with what the cited `evidence/` table/figure actually shows.
- Type-correct evidentiary standards per genre, now checked item-by-item against `GENRE_CHECKLIST`
  (CI discipline for meta-analyses, threshold discipline for DEG-style claims, proof-closure for theory
  claims, randomization-appropriate causal language for RCTs) rather than as one bundled verdict.
- Confident, correctly-cross-checked genre classification — a paper whose `Setup` subkeys and
  `constraints.md` method naming agree should not be taxed for ambiguity it doesn't have.
- A trial registration that is *disclosed and reconciles* — a paper that names its NCT number, and whose
  registry condition/intervention actually overlaps the claim's population/intervention, and whose
  reported endpoints match the registry, is doing the transparent thing and should score well, not be
  treated with suspicion merely for being checkable.
- Faithful transcription of a *known* internal inconsistency (e.g., `constraints.md`'s "Additional
  caveats" section already flags a mismatch) — this should score BETTER than a paper with the same
  underlying mismatch but no self-disclosure, because self-disclosure is itself evidence of rigor.

**Must not reward:**
- A `Statement` phrased so vaguely ("the intervention performed favorably") that it trivially can't be
  contradicted by anything — vagueness is not entailment-safety, it's information loss, and must be
  penalized as thinness (see §1.3, Goodharting via vagueness).
- Directional language in `Expected outcome` that happens to match the evidence table by accident of
  being unfalsifiably broad ("some effect was observed").
- A trial cross-check that "passes" only because no NCT id was ever surfaced — silence must not read as a
  clean bill of health (see the availability-gate design below).
- An ambiguously-framed `Setup` that routes a clinical-shaped experiment into a non-clinical genre bucket
  purely to land on the (now-tightened, confidence-scaled) non-clinical ceiling instead of the harsher
  unregistered-trial penalty — see new failure mode §1.3 #6.
- An NCT id that resolves to a real trial but one studying an unrelated population/intervention — this is
  worse than never citing one at all, and must score below the honest-absence case.

### 1.3 Failure modes / gaming routes, and the assessment-critique adjustments they drive

1. **Vagueness-as-safety.** A compiler (or an adversarial one) could soften `Expected outcome` /
   `Statement` language until nothing could ever fail to entail it. **Fix**: score entailment
   *granularity*, not just entailment *truth* — a claim entailed only because it is unfalsifiably vague
   gets capped, tying into the specificity check that's already load-bearing in `05_experiments.md`'s own
   defect list (digit-leak / vagueness detectors).
2. **Citation laundering.** `Evidence basis` cites a real table, but the specific *row/column* actually
   invoked doesn't support the specific magnitude claimed (a `Sources` entry can be locator-correct while
   being semantically wrong — the assessment-critique's core insight that this beats the ARA verifier's
   D1 check, because D1 verifies "does a source exist and quote-match," not "does the source, correctly
   read, support the number's *use* in the argument"). **Fix**: the `[sem]` entailment step is required
   to re-derive the claimed relationship from the raw evidence table/figure data, independent of the
   `Evidence basis` prose, and diff the two.
3. **Genre-mismatched rigor.** Applying RCT-grade entailment standards to a proof-obligation experiment
   (or vice versa) produces false negatives that a gameable metric-avoider could exploit by mislabeling
   genre. **Fix (cycle 2, sharpened)**: genre is inferred from `Setup` subkeys actually present via a
   *scored* keyword vote (`resolve_genre`, §2.1), with a `[sem]` closed-label fallback triggered whenever
   the vote is ambiguous (low margin or a tie), and cross-checked against `constraints.md`'s method-file
   naming (§7's own defect: "method-file naming forced onto the wrong genre"). Disagreement between the
   keyword vote and the constraints.md label no longer silently resolves to whichever fires first — it
   caps `genre_confidence`, which is itself now a scored input to two downstream penalties (see #6).
4. **Registry-blindness as an escape hatch.** The single biggest Goodhart risk specific to this metric:
   simply never mentioning a trial registration, so the publication-bias check has nothing to grab onto,
   and hoping the metric treats "no signal" as "no problem." **This is exactly the case the
   penalize-don't-skip constraint exists for.** The workflow below treats "clinical/trial-shaped
   experiment with zero registry linkage" as a first-class negative signal (undisclosed/unregistered
   trial, `0.1`), not a shrug — and treats "non-clinical genre" (where a registry is categorically
   inapplicable) as a capped-ceiling case (now `0.35`, confidence-scaled) rather than an exempted one, so
   a paper can never reach the metric's maximum score purely by being a genre the check doesn't reach.
5. **Cherry-picked evidence object.** A multi-panel figure (`mixed` type) could have its unfavorable panel
   quietly left out of the entailment check. **Fix**: the workflow requires enumerating *every*
   evidence object referenced anywhere in the claim's `Sources` list AND every evidence object the
   `README.md` maps to that claim, not just the one panel the prose foregrounds — a discrepancy between
   those two sets is itself scored (see Step 1).
6. **Genre-mislabeling to dodge the harsher clinical branch (new in cycle 2).** Cycle 1's non-clinical
   ceiling (`0.6`) was *higher* than the honestly-unregistered-clinical penalty (`0.1`) — meaning an
   attacker who obscures a clinical experiment's `Setup` keys enough to get classified as
   `theory_or_other` (e.g., writing "Cohort" instead of "Population," omitting "Randomization" language)
   would be *rewarded* relative to an honest clinical label with no registration. **Fix**: the
   non-clinical ceiling is lowered to `0.35` and scaled down further by `genre_confidence`
   (`0.35 * (0.5 + 0.5 * genre_confidence)`), so the escape route is only worth taking if the resulting
   genre classification is itself confidently correct — an ambiguous, borderline-clinical `Setup` that
   ties or nearly ties on keyword votes gets *low* confidence and therefore a *low* non-clinical ceiling,
   removing the incentive to obscure rather than clearly state genre-defining fields.
7. **Fabricated or unrelated trial citation.** A compiler (or paper) could cite a real-looking NCT id that
   resolves to an actual registry entry, but for a different population, intervention, or indication than
   the claim describes — laundering the "checkable, transparent" credit of registration without the
   substance. **Fix**: `condition_overlap_fn` (§2.4) runs a closed-label `[sem]` comparison between the
   claim's `Setup.Population`/`Setup.Intervention` and the registry's condition/intervention/arm fields;
   `no_overlap` scores `0.0`, strictly below the `0.1` honest-absence case and below the `0.05`
   unresolvable-id case, so fabrication/misattribution is never a profitable alternative to honest
   omission.

### 1.4 Composition with the rest of the suite

This metric assumes upstream structural checks (Seal Level 1: all fields present, refs resolve,
`Sources` quotes are verbatim) have already run — it does not re-litigate "is `Sources` well-formed," it
asks "having trusted the structure, does the *argument* it encodes actually close, and does an external
source corroborate or contradict it." It is deliberately the most expensive metric in the suite ([sem] +
[ext] on every claim/experiment/evidence triple, now with an additional closed-label `[sem]` genre
fallback and an additional closed-label `[sem]` condition-overlap check on the registry leg) and should be
weighted accordingly — it is the suite's main defense against a compiler (or a paper) that produces
perfectly-shaped artifacts encoding an unsound or selectively-reported argument. It composes with a
hypothetical "claim comprehensiveness" metric multiplicatively in spirit, not additively: a comprehensive
set of unentailed claims should score *worse* overall than a smaller comprehensive set of entailed ones,
so downstream aggregation should not let high comprehensiveness offset low entailment.

---

## 2. Generation / compute workflow

### 2.0 Inputs (artifact fields consumed)

| Source file | Fields used |
|---|---|
| `logic/claims.md` | per claim: `id`, `Statement`, `Status`, `Proof` (list[E##]), `Evidence basis`, `Sources` (list of grounding entries) |
| `logic/experiments.md` | per experiment: `id`, `Verifies` (list[C##]), `Setup` (subkeys), `Procedure`, `Metrics`, `Expected outcome`, `Baselines`, `Dependencies` |
| `logic/solution/constraints.md` + `study_design.md`/`method.md` | genre disambiguation; `## Reporting standard and registration` (trial IDs); `## Additional caveats...` (self-disclosed mismatches); method-file naming (cross-check for genre confidence) |
| `logic/problem.md` | Observations citing a registered trial (fallback trial-ID source) |
| `evidence/README.md` | claim→evidence-object map (cross-check against `claims.md Sources`) |
| `evidence/tables/*.md`, `evidence/figures/*.md` | raw table/figure data, `Reading confidence`, `Extraction method`, `Trend summary` |

### 2.1 Step 0 — Availability gate (deterministic, penalize-don't-skip)

Runs before any [sem]/[ext] call. Produces an `availability_floor` in `[0, 1]` that caps the final score
— a low floor here means the metric cannot be rescued by good-looking downstream sub-scores, because
unentailed-but-unverifiable is not the same as entailed. Unchanged from cycle 1 except that genre
resolution (previously a plain `infer_genre`) is now the scored `resolve_genre` used at pair-scoring time
in §2.2/§2.3 — the floor itself stays a function of ref health / evidence availability / digit-leak, since
genre confidence is a pair-level (not artifact-level) signal and belongs in the per-pair score, not the
global floor.

```python
import re
from dataclasses import dataclass, field

@dataclass
class Claim:
    id: str
    statement: str
    proof: list         # list[str] E## ids
    evidence_basis: str
    sources: list        # list of dicts: {"value":..., "locator":..., "quote":..., "tag":...}

@dataclass
class Experiment:
    id: str
    verifies: list       # list[str] C## ids
    setup: dict          # subkey -> string
    procedure: list       # list[str]
    metrics: str
    expected_outcome: list  # list[str]
    dependencies: list

@dataclass
class EvidenceObject:
    ref: str              # e.g. "tables/table2.md"
    source: str
    claims: list          # C## ids from README.md
    kind: str             # "table" | "figure"
    extraction_method: str | None
    reading_confidence: str | None
    body: str             # raw markdown body (data table / trend summary)

NUMBER_RE = re.compile(r"(?<![%<>≥≤])\b\d+(\.\d+)?%?\b")
DESIGN_THRESHOLD_RE = re.compile(r"(FDR|p)\s*[<>=]\s*0?\.\d+", re.I)

def digit_leak_defects(experiments: list[Experiment]) -> dict[str, int]:
    """Cheap defect detector per experiment: numeric leakage into Metrics/Expected outcome
    that is NOT a stated significance threshold. Returns count of leaked numbers per E##."""
    out = {}
    for e in experiments:
        text = e.metrics + " ".join(e.expected_outcome)
        leaked = [m for m in NUMBER_RE.finditer(text)
                  if not DESIGN_THRESHOLD_RE.search(text[max(0, m.start()-10):m.end()+4])]
        out[e.id] = len(leaked)
    return out

def resolve_refs(claims: list[Claim], experiments: list[Experiment]) -> dict[str, list[str]]:
    """Bidirectional ref check. Returns dict of defect lists."""
    cmap = {c.id: c for c in claims}
    emap = {e.id: e for e in experiments}
    defects = {"dangling_proof": [], "dangling_verifies": [], "orphan_claim": [], "orphan_experiment": []}
    for c in claims:
        for eid in c.proof:
            if eid not in emap:
                defects["dangling_proof"].append((c.id, eid))
        if not c.proof:
            defects["orphan_claim"].append(c.id)
    for e in experiments:
        for cid in e.verifies:
            if cid not in cmap:
                defects["dangling_verifies"].append((e.id, cid))
        if not e.verifies:
            defects["orphan_experiment"].append(e.id)
    return defects

GENRE_KEYWORDS = {
    "clinical": {"population", "intervention", "endpoint", "randomization", "arm", "enrollment"},
    "ml": {"model", "hardware", "dataset", "hyperparameters", "training"},
    "omics": {"assay", "sequencing", "reference standard", "pipeline", "quantification"},
    "statistical_synthesis": {"design", "search strategy", "inclusion criteria", "heterogeneity"},
}

def _keyword_vote(setup: dict) -> dict[str, int]:
    keys = {k.lower() for k in setup}
    return {g: len(keys & kws) for g, kws in GENRE_KEYWORDS.items()}

def infer_genre_scored(setup: dict, constraints_method_naming: str | None) -> tuple[str, float, dict]:
    """Cycle-2 replacement for cycle-1's plain infer_genre. Returns (genre, confidence, raw_votes).
    confidence in [0,1]; low confidence signals 'ambiguous, needs [sem] fallback' to resolve_genre."""
    votes = _keyword_vote(setup)
    total_votes = sum(votes.values())
    if total_votes == 0:
        return "theory_or_other", 0.4, votes   # no keyword signal at all: default genre, but LOW confidence,
                                                 # never a free pass into the (now-tightened) non-clinical ceiling
    ranked = sorted(votes.items(), key=lambda kv: -kv[1])
    top_genre, top_n = ranked[0]
    second_n = ranked[1][1] if len(ranked) > 1 else 0
    confidence = 1.0 if second_n == 0 else max(0.3, (top_n - second_n) / top_n)
    if constraints_method_naming and constraints_method_naming.lower() != top_genre:
        confidence = min(confidence, 0.5)   # disagreement CAPS confidence; does not silently override
    return top_genre, round(confidence, 2), votes

def resolve_genre(setup: dict, constraints_method_naming: str | None,
                   sem_genre_fallback_fn) -> tuple[str, float, str]:
    """Genre resolution with a scored [sem] backstop (critique fix: 'add a genre-inference fallback,
    currently keyword-only, no [sem] backstop; score genre-classification confidence')."""
    genre, confidence, votes = infer_genre_scored(setup, constraints_method_naming)
    max_vote = max(votes.values()) if votes else 0
    tie = sum(1 for v in votes.values() if v == max_vote and v > 0) > 1
    ambiguous = confidence < 0.6 or tie
    if ambiguous:
        sem_genre, sem_conf = sem_genre_fallback_fn(setup)   # closed-label [sem] call, same discipline as
                                                               # the Step 2 entailment call's closed labels
        if sem_genre != genre:
            genre = sem_genre                                 # [sem] backstop wins on disagreement, per
                                                                 # the same precedent as constraints.md naming
            confidence = min(confidence, sem_conf, 0.5)         # but disagreement still caps confidence —
                                                                 # it resolves the label, not the uncertainty
            method = "sem_fallback_override"
        else:
            confidence = max(confidence, sem_conf)
            method = "sem_fallback_confirmed"
    else:
        method = "keyword"
    return genre, confidence, method

def evidence_availability(claim: Claim, readme_map: dict, evidence_objs: dict) -> float:
    """1.0 = every Sources locator resolves to a real evidence object with usable data;
    0.0 = evidence layer effectively absent for this claim. Never returns None."""
    if not claim.sources:
        return 0.0
    resolved = 0
    for s in claim.sources:
        loc = s["locator"] if isinstance(s, dict) else s
        obj = evidence_objs.get(loc)
        if obj is None:
            continue
        if obj.kind == "table" or (obj.kind == "figure" and obj.body.strip()):
            resolved += 1
        elif obj.reading_confidence == "low":
            resolved += 0.5   # trend-summary-only fallback: usable but degraded
    return resolved / len(claim.sources)

def availability_floor(claims, experiments, evidence_objs, readme_map) -> float:
    if not experiments:
        return 0.05   # experiments.md effectively absent: floor near-zero, never N/A
    defects = resolve_refs(claims, experiments)
    n_pairs = sum(len(c.proof) for c in claims) or 1
    n_dangling = len(defects["dangling_proof"]) + len(defects["dangling_verifies"])
    ref_health = max(0.0, 1 - n_dangling / n_pairs)
    ev_avail = sum(evidence_availability(c, readme_map, evidence_objs) for c in claims) / max(1, len(claims))
    leak = digit_leak_defects(experiments)
    leak_penalty = max(0.0, 1 - 0.15 * sum(1 for v in leak.values() if v > 0))
    return max(0.05, ref_health * 0.4 + ev_avail * 0.4 + leak_penalty * 0.2)
```

### 2.2 Step 1 — Deterministic pre-check per (Claim, Experiment) pair

For every `C## -> E##` edge from `Proof`/`Verifies` (both directions must agree — Step 0 already flags
disagreement), assemble the **entailment bundle**: claim statement + experiment Setup/Procedure/Metrics/
Expected outcome + every evidence object the claim's `Sources` cites + every evidence object
`evidence/README.md` maps to that claim (union of both sets — a discrepancy between the two sets, e.g. a
claim citing table2 in `Sources` while `README.md` maps it to table3, is logged as a `citation_set_
mismatch` defect and lowers the entailment confidence cap for that pair, independent of the [sem] call).
Genre is now resolved with `resolve_genre` (§2.1) instead of a plain lookup, and its confidence travels
with the bundle into Step 2/3 scoring.

```python
def build_entailment_bundle(claim: Claim, experiment: Experiment,
                              evidence_objs: dict, readme_claim_map: dict,
                              constraints_method_naming: str | None,
                              sem_genre_fallback_fn) -> dict:
    cited_locs = {s["locator"] for s in claim.sources}
    readme_locs = set(readme_claim_map.get(claim.id, []))
    citation_set_mismatch = cited_locs.symmetric_difference(readme_locs)
    genre, genre_confidence, genre_method = resolve_genre(
        experiment.setup, constraints_method_naming, sem_genre_fallback_fn)
    return {
        "claim_id": claim.id, "experiment_id": experiment.id,
        "genre": genre, "genre_confidence": genre_confidence, "genre_method": genre_method,
        "statement": claim.statement,
        "setup": experiment.setup, "procedure": experiment.procedure,
        "metrics": experiment.metrics, "expected_outcome": experiment.expected_outcome,
        "evidence": [evidence_objs[l] for l in (cited_locs | readme_locs) if l in evidence_objs],
        "citation_set_mismatch": bool(citation_set_mismatch),
    }
```

### 2.3 Step 2 — `[sem]` entailment call with deterministic per-genre checklist

Cycle-1 fix: rather than one holistic `type_check: pass|fail` field trusting the LLM to apply five
different rubrics consistently from memory, the rubric is lifted into an explicit, fixed checklist per
genre. The LLM still makes the semantic call (whether a given checklist item holds), but *what counts as
type-correct* is no longer implicit — it is enumerable, diffable across runs, and spot-checkable item by
item.

```python
GENRE_CHECKLIST = {
    "clinical": [
        "uses_randomization_appropriate_causal_language",
        "headline_endpoint_is_primary_not_secondary_per_setup_or_registry",
        "comparator_arm_is_the_one_the_statement_describes",
    ],
    "ml": [
        "baseline_comparison_is_stated_and_actually_used_in_the_claimed_comparison",
        "metric_definition_in_Metrics_matches_the_relationship_asserted_in_Statement",
        "improvement_claim_not_conflated_with_statistical_significance_absent_a_stated_test",
    ],
    "omics": [
        "significance_threshold_is_stated_in_Setup_or_Metrics",
        "claimed_DEG_or_effect_count_is_gated_by_that_threshold_not_a_looser_one",
        "direction_of_effect_in_Statement_matches_direction_in_raw_evidence",
    ],
    "statistical_synthesis": [
        "CI_or_p_value_is_present_in_the_raw_evidence_object",
        "significance_claim_is_false_if_the_cited_CI_crosses_the_null",
        "heterogeneity_or_subgroup_caveats_present_in_evidence_are_not_silently_dropped_by_Statement",
    ],
    "theory_or_other": [
        "Procedure_lists_proof_obligations_that_map_onto_the_claimed_result",
        "no_step_gestures_at_a_theorem_or_lemma_without_closing_it",
        "claimed_result_scope_matches_the_scope_actually_established_by_the_obligations",
    ],
}

PROMPT_TEMPLATE = """
SYSTEM: You are a type-aware scientific entailment auditor. You do not trust prose summaries; you
re-derive the relationship directly from the raw evidence data provided.

USER:
GENRE: {genre}   # one of clinical | ml | omics | statistical_synthesis | theory_or_other
GENRE_CONFIDENCE: {genre_confidence}   # how confidently genre was resolved (keyword vote / [sem] fallback)
GENRE_CHECKLIST (answer every item, do not skip any):
{checklist_items}

CLAIM STATEMENT:
{statement}

EXPERIMENT (declarative plan — contains no exact result numbers by design):
Setup: {setup}
Procedure: {procedure}
Metrics measured: {metrics}
Expected outcome (directional only): {expected_outcome}

RAW EVIDENCE OBJECTS (verbatim transcriptions, the only place exact numbers may appear):
{evidence_objects}

TASK:
1. Re-derive, from the raw evidence data ONLY (ignore any narrative gloss), the actual
   direction/magnitude/significance relationship the data shows.
2. State the relationship the CLAIM asserts.
3. For EACH item in GENRE_CHECKLIST, answer true/false with a one-sentence rationale citing exact
   evidence values where relevant. Do not collapse this into a single verdict.
4. Classify overall entailment ∈ {{full, partial, contradicted, unverifiable_vague}}.
   - "unverifiable_vague": the claim/expected-outcome is phrased so broadly that no evidence could
     contradict it — this is a DEFECT, not a pass.
5. Return STRICT JSON:
{{"entailment": "full|partial|contradicted|unverifiable_vague",
 "checklist_results": [{{"item": "<checklist_item_name>", "passed": true|false, "rationale": "<=1 sentence"}}, ...],
 "specificity": "high|medium|low",
 "rationale": "<= 3 sentences, cite exact evidence values used"}}
"""
```

Deterministic mapping from the LLM's structured output to a sub-score:

```python
ENTAILMENT_SCORE = {"full": 1.0, "partial": 0.5, "contradicted": 0.0, "unverifiable_vague": 0.2}
SPECIFICITY_MULT = {"high": 1.0, "medium": 0.85, "low": 0.6}

def checklist_pass_fraction(sem_result: dict) -> float:
    results = sem_result["checklist_results"]
    if not results:
        return 0.0   # missing checklist entirely is a defect, not a pass
    return sum(1 for r in results if r["passed"]) / len(results)

def score_entailment_bundle(sem_result: dict, citation_set_mismatch: bool,
                              genre_confidence: float) -> float:
    base = ENTAILMENT_SCORE[sem_result["entailment"]]
    checklist_score = checklist_pass_fraction(sem_result)
    # graded ladder replaces cycle-1's flat "type_check fail -> *0.4": a genre-appropriate claim that
    # fails one checklist item out of three is not treated identically to one that fails all three.
    base *= (0.4 + 0.6 * checklist_score)
    base *= SPECIFICITY_MULT[sem_result["specificity"]]
    if citation_set_mismatch:
        base *= 0.75                     # citation laundering signal (§1.3 #2/#5)
    # low-confidence genre classification caps the score: an ambiguously-labeled bundle should not be
    # able to earn full entailment credit for satisfying a checklist that might be the wrong checklist.
    base *= (0.7 + 0.3 * genre_confidence)
    return base
```

### 2.4 Step 3 — `[ext trial lookup]` publication-bias cross-check

**Trial-signal detection** (deterministic, over `Setup`, `study_design.md`'s registration section, and
`problem.md` Observations) — unchanged from cycle 1:

```python
NCT_RE = re.compile(r"NCT\d{8}")

def find_trial_id(experiment: Experiment, study_design_text: str, problem_text: str) -> str | None:
    for blob in (str(experiment.setup), study_design_text, problem_text):
        m = NCT_RE.search(blob)
        if m:
            return m.group(0)
    return None
```

If `genre == "clinical"` (per §2.1's `resolve_genre`):

- **Trial ID found** → call `search_trials` / `get_trial_details` (ClinicalTrials.gov) on the NCT id.
  Exact query: `get_trial_details(nct_id=<id>)`, then `analyze_endpoints` on that trial vs. the claim's
  asserted endpoint to check (a) the claim's headline endpoint matches a *primary* (not secondary)
  outcome measure in the registry, (b) the registry's posted results (if `results_posted=True`) agree in
  direction with the claim, (c) trial status is not `Terminated`/`Withdrawn` in a way inconsistent with
  reporting a completed-trial claim, and **(d, new in cycle 2) the registry's condition/intervention/arm
  fields actually overlap the claim's `Setup.Population`/`Setup.Intervention`** — a resolvable id is not
  by itself evidence the citation is honest.
- **No trial ID found, but genre is clinical** → this is an *undisclosed/unregistered trial* signal, not
  an inapplicable check. Score it directly as a penalty, per penalize-don't-skip.

If `genre != "clinical"` → the registry check is categorically inapplicable, but per the hard constraint
this must never resolve to N/A; it resolves to a fixed sub-ceiling, now tightened and confidence-scaled
(see composite below) reflecting "no independent corroboration exists for this genre's claims, and that
absence is worth less credit than cycle 1 gave it."

```python
def condition_overlap_fn(claim: Claim, experiment_setup: dict, registry: dict,
                           sem_overlap_fn) -> str:
    """Closed-label [sem] call, same discipline as Step 2's checklist. Returns one of:
    'full_overlap' | 'partial_overlap' | 'no_overlap'.
    New in cycle 2 — spells out the fabricated/mismatched-NCT guard exp2 already had."""
    claim_population = experiment_setup.get("Population") or experiment_setup.get("Cohort")
    claim_intervention = experiment_setup.get("Intervention")
    return sem_overlap_fn(claim.statement, claim_population, claim_intervention,
                           registry.get("condition"), registry.get("interventions"),
                           registry.get("arms"))

def publication_bias_subscore(genre: str, genre_confidence: float, trial_id: str | None,
                                registry_lookup_fn, claim: Claim, experiment_setup: dict,
                                sem_overlap_fn) -> tuple[float, str]:
    if genre != "clinical":
        # tightened from a flat 0.6 (critique: too generous for an unauditable axis) and made
        # confidence-sensitive (closes the genre-mislabeling escape hatch, §1.3 #6): an
        # ambiguously-classified non-clinical experiment cannot reach even this lowered ceiling.
        ceiling = round(0.35 * (0.5 + 0.5 * genre_confidence), 3)
        return ceiling, "not_applicable_genre"
    if trial_id is None:
        return 0.1, "clinical_genre_no_registration"     # strong penalty: undisclosed trial
    registry = registry_lookup_fn(trial_id)               # get_trial_details + analyze_endpoints
    if registry is None:
        return 0.05, "nct_cited_but_unresolvable"          # tightened from 0.2: an unresolvable cited
                                                             # id is closer to fabrication than to honest
                                                             # absence and must not out-score it as much
    overlap = condition_overlap_fn(claim, experiment_setup, registry, sem_overlap_fn)
    if overlap == "no_overlap":
        # new in cycle 2: the id resolves, but to a DIFFERENT trial than the claim describes.
        # Scored strictly below honest absence (0.1) and below the unresolvable case (0.05) —
        # fabrication/misattribution must never be a profitable alternative to disclosure.
        return 0.0, "nct_resolves_to_unrelated_trial"
    mismatches = 0
    if registry.get("claimed_endpoint_is_primary") is False:
        mismatches += 1
    if registry.get("results_posted") and registry.get("direction_agrees") is False:
        mismatches += 1
    if registry.get("status") in ("Terminated", "Withdrawn") and claim.statement:
        mismatches += 1
    if overlap == "partial_overlap":
        mismatches += 1   # e.g., right intervention wrong population, or vice versa
    score = max(0.0, 1.0 - 0.4 * mismatches)
    return score, f"reconciled_mismatches={mismatches}"
```

`registry_lookup_fn` is a thin adapter over the Clinical Trials MCP tools: it calls
`get_trial_details(nct_id)` for status/outcomes/results-posted, then `analyze_endpoints(nct_id, ...)` to
diff the registry's declared primary outcome measure against the text of `claim.statement` (a small
[sem] sub-call: "does this claim statement describe outcome X, and is X primary or secondary per the
registry record below?" — same strict-JSON discipline as Step 2). `sem_overlap_fn` is a second, equally
small closed-label [sem] sub-call dedicated to the condition-overlap check, kept separate from the
endpoint-framing call so a reviewer can audit "does this trial match this population" independently of
"does this trial's endpoint match this claim."

### 2.5 Step 4 — Composite score

```python
def compute_M19(claim: Claim, experiment: Experiment, evidence_objs: dict,
                 readme_claim_map: dict, sem_entailment_fn, registry_lookup_fn,
                 sem_genre_fallback_fn, sem_overlap_fn,
                 constraints_method_naming: str | None,
                 study_design_text: str, problem_text: str,
                 floor: float) -> dict:
    bundle = build_entailment_bundle(claim, experiment, evidence_objs, readme_claim_map,
                                       constraints_method_naming, sem_genre_fallback_fn)
    sem_result = sem_entailment_fn(bundle)                     # Step 2 LLM call (checklist-based)
    entailment_score = score_entailment_bundle(
        sem_result, bundle["citation_set_mismatch"], bundle["genre_confidence"])

    trial_id = find_trial_id(experiment, study_design_text, problem_text)
    bias_score, bias_reason = publication_bias_subscore(
        bundle["genre"], bundle["genre_confidence"], trial_id, registry_lookup_fn,
        claim, experiment.setup, sem_overlap_fn)

    # entailment carries most of the weight; publication-bias is the differentiator this
    # metric was chosen FOR, so it is not a rounding term. Unchanged from cycle 1 — the critique
    # did not fault this weighting, only the sub-scores feeding it.
    raw = 0.65 * entailment_score + 0.35 * bias_score
    final = raw * floor   # availability_floor from Step 0 caps everything

    return {
        "claim_id": claim.id, "experiment_id": experiment.id,
        "genre": bundle["genre"], "genre_confidence": bundle["genre_confidence"],
        "genre_method": bundle["genre_method"],
        "entailment": sem_result["entailment"],
        "checklist_pass_fraction": round(checklist_pass_fraction(sem_result), 3),
        "entailment_score": round(entailment_score, 3),
        "bias_score": round(bias_score, 3), "bias_reason": bias_reason,
        "availability_floor": round(floor, 3),
        "score": round(final, 3),
    }

def compute_M19_artifact(claims, experiments, evidence_objs, readme_claim_map,
                           sem_entailment_fn, registry_lookup_fn,
                           sem_genre_fallback_fn, sem_overlap_fn,
                           constraints_method_naming, study_design_text, problem_text) -> dict:
    floor = availability_floor(claims, experiments, evidence_objs, readme_claim_map)
    emap = {e.id: e for e in experiments}
    pair_scores = []
    for c in claims:
        if not c.proof:
            pair_scores.append({"claim_id": c.id, "score": 0.0, "reason": "no_proof_ref"})
            continue
        for eid in c.proof:
            e = emap.get(eid)
            if e is None:
                pair_scores.append({"claim_id": c.id, "experiment_id": eid,
                                     "score": 0.0, "reason": "dangling_proof_ref"})
                continue
            pair_scores.append(compute_M19(c, e, evidence_objs, readme_claim_map,
                                             sem_entailment_fn, registry_lookup_fn,
                                             sem_genre_fallback_fn, sem_overlap_fn,
                                             constraints_method_naming, study_design_text,
                                             problem_text, floor))
    artifact_score = sum(p["score"] for p in pair_scores) / max(1, len(pair_scores))
    return {"artifact_score": round(artifact_score, 3), "availability_floor": round(floor, 3),
            "pairs": pair_scores}
```

This is fully runnable given (a) a markdown→dataclass parser for `claims.md`/`experiments.md`/
`evidence/` — trivial regex/section-splitting over the documented field tables — and (b) four external
adapters: `sem_entailment_fn` (Step 2 checklist call), `sem_genre_fallback_fn` (closed-label genre
backstop), `sem_overlap_fn` (closed-label condition-overlap check), and `registry_lookup_fn` (wrapping the
Clinical Trials MCP tools). No step silently returns `None`/`N/A`: every branch above resolves to a
number, and the places genre-confidence or trial-linkage is degraded (`not_applicable_genre`,
`clinical_genre_no_registration`, `nct_cited_but_unresolvable`, `nct_resolves_to_unrelated_trial`) are
explicit, documented sub-ceilings rather than skips, each priced relative to the others so that no
dishonest or ambiguous state ever out-scores a more honest, more disclosed one.

---

## 3. Why hard to Goodhart, and composition

**Hard to Goodhart** because it requires jointly gaming four independent surfaces that don't share an
attacker-controlled lever (cycle 2 adds the fourth):

1. The **raw evidence data** (Step 2 re-derives the relationship from transcribed table/figure values,
   not from the claim's own prose) — a compiler can't fix a bad claim by writing better prose around it,
   since the entailment call is instructed to ignore narrative gloss.
2. The **citation-set cross-check** (Step 2's `citation_set_mismatch`) compares two independently-produced
   artifacts (`claims.md Sources` vs. `evidence/README.md`) — gaming one without the other is caught.
3. The **external registry** (Step 3) is outside the artifact entirely; nothing in the compilation process
   can edit ClinicalTrials.gov. The only levers left to an attacker are (a) *never mentioning* a trial ID
   — exactly the case explicitly penalized (`clinical_genre_no_registration`, score `0.1`) rather than
   exempted — or (b) *citing an unrelated trial* to launder the appearance of transparency — now closed by
   `condition_overlap_fn`, priced at `0.0`, strictly worse than either honest omission or an unresolvable
   citation.
4. **Genre classification itself** (new in cycle 2) is no longer a free, attacker-legible lever: a
   `Setup` engineered to be ambiguous between clinical and non-clinical keywords lands in low-confidence
   territory, and low confidence caps *both* the entailment score (via the `0.7 + 0.3*genre_confidence`
   multiplier) and the non-clinical bias ceiling (via `0.35 * (0.5 + 0.5*genre_confidence)`). Clearly
   labeling genre-defining `Setup` fields is now strictly dominant over obscuring them, closing the
   perverse incentive identified in §1.3 #6 where cycle 1's flat `0.6` non-clinical ceiling was worth more
   than an honest, unregistered clinical label.

Additionally, the `unverifiable_vague` entailment class and the `specificity` multiplier directly counter
the classic vagueness-as-safety Goodhart route: softening language to avoid contradiction is scored as a
defect, not a pass. The per-genre `GENRE_CHECKLIST` (replacing a single holistic `type_check`) means an
attacker (or a sloppy compiler) cannot get credit for "mostly seeming type-appropriate" — each checklist
item is independently gradeable and independently auditable, so gaming would require satisfying every
genre-specific rigor requirement individually rather than producing prose that reads as generically
rigorous.

**Composition**: this metric should be read as a *ceiling* on other claim-quality metrics rather than an
independent additive term — a comprehensiveness/sourcing metric measures whether the pieces exist and are
well-formed, this metric measures whether, once they exist, they say something true and undisclosed-bias-
free. A downstream aggregator should not allow a high comprehensiveness score to compensate for a low M19
score (multiplicative gating, not weighted-sum blending), since a comprehensive set of unentailed or
selectively-reported claims is a worse artifact than a sparse set of entailed, reconciled ones. It shares
no computation with the ARA verifier's D1 check (which only confirms sources resolve and quote-match) and
is the only metric in the suite with an external-registry leg, preserving the exact edge the
assessment-critique ranked it for — cycle 2 strengthens that edge by making the registry leg resistant to
fabricated-citation laundering, not just registry-silence.
