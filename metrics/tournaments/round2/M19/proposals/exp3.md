# M19 — Claim↔Experiment↔Evidence entailment (+ publication-bias) — Expansion (exp3)

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
pre-registered endpoint, not a relabeled one).

The **publication-bias cross-check** is the second, structurally distinct half. `logic/experiments.md`
and `logic/solution/study_design.md` are declarative — by design they contain the paper's *own* account
of what it measured and found directionally. They cannot, by construction, tell you what the same
underlying trial *would have reported had all pre-registered endpoints been disclosed*. That requires an
external, adversarial source: the clinical-trial registry. If an experiment's `Setup` (or `problem.md`
Observations, or `study_design.md`'s `Reporting standard and registration` section) names a registered
trial, the registry is ground truth for what was *promised* — primary/secondary endpoints, planned
analyses, status — independent of what the compiled ARA chose to foreground. A mismatch (claim reports a
secondary endpoint as if primary; registry shows the trial was terminated early; registry lists an
endpoint the paper never mentions) is a **publication-bias / selective-reporting signal that no other
in-suite metric can see**, because every other metric only ever looks *inside* the artifact. This is
exactly why the assessment-critique ranked this metric net-new against the ARA verifier (which checks D1
— claim/evidence internal consistency — semantically, i.e. still inside the artifact) and against
round-1 proposals (which stopped at internal entailment).

### 1.2 What it must reward, and what it must not

**Reward:**
- A `Statement` whose asserted relationship (direction, comparator, magnitude class, significance) is
  fully reconstructable from `Setup + Procedure + Metrics + Expected outcome` in the linked `E##`, AND
  is consistent with what the cited `evidence/` table/figure actually shows.
- Type-correct evidentiary standards per genre (CI discipline for meta-analyses, threshold discipline for
  DEG-style claims, proof-closure for theory claims, randomization-appropriate causal language for RCTs).
- A trial registration that is *disclosed and reconciles* — a paper that names its NCT number and whose
  reported endpoints match the registry is doing the transparent thing and should score well, not be
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
   genre. **Fix**: genre is inferred from `Setup` subkeys actually present (`Population`/`Randomization`
   → clinical; `Model`/`Hardware` → ML; `Assay`/`Sequencing` → omics; `Procedure` steps that are proof
   obligations with no numeric `Metrics` → theory), not self-declared, and cross-checked against
   `constraints.md`'s method-file naming (§7's own defect: "method-file naming forced onto the wrong
   genre").
4. **Registry-blindness as an escape hatch.** The single biggest Goodhart risk specific to this metric:
   simply never mentioning a trial registration, so the publication-bias check has nothing to grab onto,
   and hoping the metric treats "no signal" as "no problem." **This is exactly the case the
   penalize-don't-skip constraint exists for.** The workflow below treats "clinical/trial-shaped
   experiment with zero registry linkage" as a first-class negative signal (undisclosed/unregistered
   trial), not a shrug — and treats "non-clinical genre" (where a registry is categorically inapplicable)
   as a capped-ceiling case rather than an exempted one, so a paper can never reach the metric's maximum
   score purely by being a genre the check doesn't reach.
5. **Cherry-picked evidence object.** A multi-panel figure (`mixed` type) could have its unfavorable panel
   quietly left out of the entailment check. **Fix**: the workflow requires enumerating *every*
   evidence object referenced anywhere in the claim's `Sources` list AND every evidence object the
   `README.md` maps to that claim, not just the one panel the prose foregrounds — a discrepancy between
   those two sets is itself scored (see Step 1).

### 1.4 Composition with the rest of the suite

This metric assumes upstream structural checks (Seal Level 1: all fields present, refs resolve,
`Sources` quotes are verbatim) have already run — it does not re-litigate "is `Sources` well-formed," it
asks "having trusted the structure, does the *argument* it encodes actually close, and does an external
source corroborate or contradict it." It is deliberately the most expensive metric in the suite ([sem] +
[ext] on every claim/experiment/evidence triple) and should be weighted accordingly — it is the suite's
main defense against a compiler (or a paper) that produces perfectly-shaped artifacts encoding an
unsound or selectively-reported argument. It composes with a hypothetical "claim comprehensiveness"
metric multiplicatively in spirit, not additively: a comprehensive set of unentailed claims should score
*worse* overall than a smaller comprehensive set of entailed ones, so downstream aggregation should not
let high comprehensiveness offset low entailment.

---

## 2. Generation / compute workflow

### 2.0 Inputs (artifact fields consumed)

| Source file | Fields used |
|---|---|
| `logic/claims.md` | per claim: `id`, `Statement`, `Status`, `Proof` (list[E##]), `Evidence basis`, `Sources` (list of grounding entries) |
| `logic/experiments.md` | per experiment: `id`, `Verifies` (list[C##]), `Setup` (subkeys), `Procedure`, `Metrics`, `Expected outcome`, `Baselines`, `Dependencies` |
| `logic/solution/constraints.md` + `study_design.md`/`method.md` | genre disambiguation; `## Reporting standard and registration` (trial IDs); `## Additional caveats...` (self-disclosed mismatches) |
| `logic/problem.md` | Observations citing a registered trial (fallback trial-ID source) |
| `evidence/README.md` | claim→evidence-object map (cross-check against `claims.md Sources`) |
| `evidence/tables/*.md`, `evidence/figures/*.md` | raw table/figure data, `Reading confidence`, `Extraction method`, `Trend summary` |

### 2.1 Step 0 — Availability gate (deterministic, penalize-don't-skip)

Runs before any [sem]/[ext] call. Produces an `availability_floor` in `[0, 1]` that caps the final score
— a low floor here means the metric cannot be rescued by good-looking downstream sub-scores, because
unentailed-but-unverifiable is not the same as entailed.

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

def infer_genre(setup: dict) -> str:
    keys = {k.lower() for k in setup}
    if {"population", "intervention", "endpoint", "randomization"} & keys:
        return "clinical"
    if {"model", "hardware", "dataset"} & keys:
        return "ml"
    if {"assay", "sequencing", "reference standard"} & keys:
        return "omics"
    if {"design"} <= keys and not ({"model", "assay"} & keys):
        return "statistical_synthesis"
    return "theory_or_other"

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

```python
def build_entailment_bundle(claim: Claim, experiment: Experiment,
                              evidence_objs: dict, readme_claim_map: dict) -> dict:
    cited_locs = {s["locator"] for s in claim.sources}
    readme_locs = set(readme_claim_map.get(claim.id, []))
    citation_set_mismatch = cited_locs.symmetric_difference(readme_locs)
    genre = infer_genre(experiment.setup)
    return {
        "claim_id": claim.id, "experiment_id": experiment.id, "genre": genre,
        "statement": claim.statement,
        "setup": experiment.setup, "procedure": experiment.procedure,
        "metrics": experiment.metrics, "expected_outcome": experiment.expected_outcome,
        "evidence": [evidence_objs[l] for l in (cited_locs | readme_locs) if l in evidence_objs],
        "citation_set_mismatch": bool(citation_set_mismatch),
    }
```

### 2.3 Step 2 — `[sem]` entailment call

One LLM call per bundle. Exact prompt template:

```
SYSTEM: You are a type-aware scientific entailment auditor. You do not trust prose summaries; you
re-derive the relationship directly from the raw evidence data provided.

USER:
GENRE: {genre}   # one of clinical | ml | omics | statistical_synthesis | theory_or_other

CLAIM STATEMENT:
{statement}

EXPERIMENT (declarative plan — contains no exact result numbers by design):
Setup: {setup}
Procedure: {procedure}
Metrics measured: {metrics}
Expected outcome (directional only): {expected_outcome}

RAW EVIDENCE OBJECTS (verbatim transcriptions, the only place exact numbers may appear):
{for each evidence object: its table/figure body + Reading confidence + Extraction method}

TASK:
1. Re-derive, from the raw evidence data ONLY (ignore any narrative gloss), the actual
   direction/magnitude/significance relationship the data shows.
2. State the relationship the CLAIM asserts.
3. Apply the genre-appropriate evidentiary standard:
   - clinical: requires randomization-appropriate language, correct primary vs secondary endpoint framing
   - statistical_synthesis: requires CI discipline (a claim of "significant" backed by a CI crossing 0
     fails)
   - omics: requires the stated significance threshold (e.g. FDR<0.05) to actually gate the claimed count
   - theory_or_other: requires the Procedure's proof obligations to actually close the claimed result,
     not merely gesture at it
4. Classify: entailment ∈ {full, partial, contradicted, unverifiable_vague}.
   - "unverifiable_vague": the claim/expected-outcome is phrased so broadly that no evidence could
     contradict it — this is a DEFECT, not a pass.
5. Return STRICT JSON:
{"entailment": "full|partial|contradicted|unverifiable_vague",
 "type_check": "pass|fail",
 "specificity": "high|medium|low",
 "rationale": "<= 3 sentences, cite exact evidence values used"}
```

Deterministic mapping from the LLM's structured output to a sub-score:

```python
ENTAILMENT_SCORE = {"full": 1.0, "partial": 0.5, "contradicted": 0.0, "unverifiable_vague": 0.2}
SPECIFICITY_MULT = {"high": 1.0, "medium": 0.85, "low": 0.6}

def score_entailment_bundle(sem_result: dict, citation_set_mismatch: bool) -> float:
    base = ENTAILMENT_SCORE[sem_result["entailment"]]
    if sem_result["type_check"] == "fail":
        base *= 0.4                      # genre-inappropriate reasoning caps hard
    base *= SPECIFICITY_MULT[sem_result["specificity"]]
    if citation_set_mismatch:
        base *= 0.75                     # citation laundering signal (§1.3 #2/#5)
    return base
```

### 2.4 Step 3 — `[ext trial lookup]` publication-bias cross-check

**Trial-signal detection** (deterministic, over `Setup`, `study_design.md`'s registration section, and
`problem.md` Observations):

```python
NCT_RE = re.compile(r"NCT\d{8}")

def find_trial_id(experiment: Experiment, study_design_text: str, problem_text: str) -> str | None:
    for blob in (str(experiment.setup), study_design_text, problem_text):
        m = NCT_RE.search(blob)
        if m:
            return m.group(0)
    return None
```

If `genre == "clinical"` (per §2.1's `infer_genre`):

- **Trial ID found** → call `search_trials` / `get_trial_details` (ClinicalTrials.gov) on the NCT id.
  Exact query: `get_trial_details(nct_id=<id>)`, then `analyze_endpoints` on that trial vs. the claim's
  asserted endpoint to check (a) the claim's headline endpoint matches a *primary* (not secondary)
  outcome measure in the registry, (b) the registry's posted results (if `results_posted=True`) agree in
  direction with the claim, (c) trial status is not `Terminated`/`Withdrawn` in a way inconsistent with
  reporting a completed-trial claim.
- **No trial ID found, but genre is clinical** → this is an *undisclosed/unregistered trial* signal, not
  an inapplicable check. Score it directly as a penalty, per penalize-don't-skip.

If `genre != "clinical"` → the registry check is categorically inapplicable, but per the hard constraint
this must never resolve to N/A; it resolves to a fixed sub-ceiling (see composite below) reflecting "no
independent corroboration exists for this genre's claims."

```python
def publication_bias_subscore(genre: str, trial_id: str | None,
                                registry_lookup_fn, claim: Claim) -> tuple[float, str]:
    if genre != "clinical":
        return 0.6, "not_applicable_genre"          # capped ceiling, never full credit, never N/A
    if trial_id is None:
        return 0.1, "clinical_genre_no_registration"  # strong penalty: undisclosed trial
    registry = registry_lookup_fn(trial_id)           # get_trial_details + analyze_endpoints
    if registry is None:
        return 0.2, "nct_cited_but_unresolvable"       # cited ID doesn't resolve: worse than honest absence
    mismatches = 0
    if registry.get("claimed_endpoint_is_primary") is False:
        mismatches += 1
    if registry.get("results_posted") and registry.get("direction_agrees") is False:
        mismatches += 1
    if registry.get("status") in ("Terminated", "Withdrawn") and claim.statement:
        mismatches += 1
    score = max(0.0, 1.0 - 0.4 * mismatches)
    return score, f"reconciled_mismatches={mismatches}"
```

`registry_lookup_fn` is a thin adapter over the Clinical Trials MCP tools: it calls
`get_trial_details(nct_id)` for status/outcomes/results-posted, then `analyze_endpoints(nct_id, ...)` to
diff the registry's declared primary outcome measure against the text of `claim.statement` (a small
[sem] sub-call: "does this claim statement describe outcome X, and is X primary or secondary per the
registry record below?" — same strict-JSON discipline as Step 2).

### 2.5 Step 4 — Composite score

```python
def compute_M19(claim: Claim, experiment: Experiment, evidence_objs: dict,
                 readme_claim_map: dict, sem_entailment_fn, registry_lookup_fn,
                 study_design_text: str, problem_text: str,
                 floor: float) -> dict:
    bundle = build_entailment_bundle(claim, experiment, evidence_objs, readme_claim_map)
    sem_result = sem_entailment_fn(bundle)                     # Step 2 LLM call
    entailment_score = score_entailment_bundle(sem_result, bundle["citation_set_mismatch"])

    trial_id = find_trial_id(experiment, study_design_text, problem_text)
    bias_score, bias_reason = publication_bias_subscore(
        bundle["genre"], trial_id, registry_lookup_fn, claim)

    # entailment carries most of the weight; publication-bias is the differentiator this
    # metric was chosen FOR, so it is not a rounding term.
    raw = 0.65 * entailment_score + 0.35 * bias_score
    final = raw * floor   # availability_floor from Step 0 caps everything

    return {
        "claim_id": claim.id, "experiment_id": experiment.id,
        "genre": bundle["genre"], "entailment": sem_result["entailment"],
        "entailment_score": round(entailment_score, 3),
        "bias_score": round(bias_score, 3), "bias_reason": bias_reason,
        "availability_floor": round(floor, 3),
        "score": round(final, 3),
    }

def compute_M19_artifact(claims, experiments, evidence_objs, readme_claim_map,
                           sem_entailment_fn, registry_lookup_fn,
                           study_design_text, problem_text) -> dict:
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
                                             study_design_text, problem_text, floor))
    artifact_score = sum(p["score"] for p in pair_scores) / max(1, len(pair_scores))
    return {"artifact_score": round(artifact_score, 3), "availability_floor": round(floor, 3),
            "pairs": pair_scores}
```

This is fully runnable given (a) a markdown→dataclass parser for `claims.md`/`experiments.md`/
`evidence/` — trivial regex/section-splitting over the documented field tables — and (b) the two external
adapters (`sem_entailment_fn` wrapping an LLM call with the Step 2 prompt, `registry_lookup_fn` wrapping
the Clinical Trials MCP tools). No step silently returns `None`/`N/A`: every branch above resolves to a
number, and the two places genre or trial-linkage is absent (`not_applicable_genre`,
`clinical_genre_no_registration`) are explicit, documented sub-ceilings rather than skips.

---

## 3. Why hard to Goodhart, and composition

**Hard to Goodhart** because it requires jointly gaming three independent surfaces that don't share an
attacker-controlled lever:
1. The **raw evidence data** (Step 2 re-derives the relationship from transcribed table/figure values,
   not from the claim's own prose) — a compiler can't fix a bad claim by writing better prose around it,
   since the entailment call is instructed to ignore narrative gloss.
2. The **citation-set cross-check** (Step 2's `citation_set_mismatch`) compares two independently-produced
   artifacts (`claims.md Sources` vs. `evidence/README.md`) — gaming one without the other is caught.
3. The **external registry** (Step 3) is outside the artifact entirely; nothing in the compilation process
   can edit ClinicalTrials.gov. The only lever left to an attacker is *never mentioning* a trial ID, which
   is exactly the case explicitly penalized (`clinical_genre_no_registration`, score 0.1) rather than
   exempted — closing the one escape hatch that would otherwise make this metric gameable by omission.
Additionally, the `unverifiable_vague` entailment class and the `specificity` multiplier directly counter
the classic vagueness-as-safety Goodhart route: softening language to avoid contradiction is scored as a
defect, not a pass.

**Composition**: this metric should be read as a *ceiling* on other claim-quality metrics rather than an
independent additive term — a comprehensiveness/sourcing metric measures whether the pieces exist and are
well-formed, this metric measures whether, once they exist, they say something true and undisclosed-bias-
free. A downstream aggregator should not allow a high comprehensiveness score to compensate for a low M19
score (multiplicative gating, not weighted-sum blending), since a comprehensive set of unentailed or
selectively-reported claims is a worse artifact than a sparse set of entailed, reconciled ones. It shares
no computation with the ARA verifier's D1 check (which only confirms sources resolve and quote-match) and
is the only metric in the suite with an external-registry leg, preserving the exact edge the
assessment-critique ranked it for.

M19 expander3: done
