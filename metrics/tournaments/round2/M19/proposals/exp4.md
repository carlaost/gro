# M19 — Claim↔Experiment↔Evidence entailment (+ publication-bias cross-check)

Expander 4. Primary artifact: `logic/experiments.md`. Cross-layer reads: `logic/claims.md` (§2),
`logic/concepts.md` (§3, tags/vocab only), `logic/problem.md` (§4), `logic/solution/constraints.md`
(§7), `evidence/` (§9).

## 1. Why this indicator signals good science

A paper's rhetorical claims and its actual test design are two different objects. `claims.md` is
prose the compiler extracted; `experiments.md` is the declarative plan that is supposed to have
produced the grounds for that prose; `evidence/` is the verbatim numeric record the plan actually
yielded. Good science requires all three to *chain*: the claim must be the kind of thing the
experiment's design is capable of establishing, and the evidence must be the kind of thing that
establishes it. Bad science routinely breaks this chain without breaking any single link visibly:

- an experiment measures direction-of-effect but the claim asserts a specific ranking order;
- an experiment's `Expected outcome` is vague ("improves performance") but `claims.md` reports a
  crisp comparative superiority nobody actually tested for;
- a `theoretical_proof`-shaped result (derivation, proof obligation) gets claimed with the rhetorical
  confidence of an empirical finding, or vice versa;
- a clinical trial's registered primary endpoint quietly becomes a secondary curiosity in the paper
  while a post-hoc subgroup finding becomes the claim (endpoint switching) — classic publication bias;
- a claim is true of *this* dataset but a directly comparable, already-registered/published study with
  a different or null result exists and is never reconciled anywhere in the ARA.

None of this is caught by checking that `Proof`/`Verifies` resolve (a graph-integrity check) or by a
flat "does the evidence generally support the claim" pass (a semantic-similarity check). It requires
**type-aware entailment**: the logical bar for "this evidence entails this claim" is different for a
ranking claim, a directional claim, a mechanistic claim, and a proof claim, and a verifier that treats
them uniformly will pass claims that are technically ungrounded but read as plausible.

### What it must reward
- Claims whose type-appropriate entailment criterion is met *by the specific cited evidence*, not by
  the general vibe of the paper.
- Experiments whose `Metrics`/`Expected outcome` are precise enough that entailment/non-entailment is
  even decidable (vague plans should fail to entail crisp claims, and this metric should make that
  failure visible rather than giving benefit of the doubt).
- ARAs that surface and reconcile a contradicting external result (registered trial, or an equivalent
  published study) rather than omitting it — reconciliation is rewarded even when perfect agreement
  isn't there, because the epistemic behavior being rewarded is disclosure, not universal victory.

### What it must NOT reward
- Structural resolution alone (`C## → E##` pointer exists) — that is a pointer, not entailment, and is
  already partially covered elsewhere (see §4 on non-redundancy).
- Narrative plausibility / fluent prose — an LLM judge that is only asked "does this evidence support
  this claim?" in the abstract will rubber-stamp confident, well-written claims. The judge must be
  forced to state the type-specific criterion and check it against the verbatim quoted values, not the
  claim's own restatement of itself.
- "No contradicting trial found" when no real search was attempted — absence of contradiction must be
  the result of an actual query, not a default value.

### Failure modes / gaming routes this metric must resist
1. **Vague-experiment gaming**: write an experiment with maximally hedgy `Expected outcome`
   ("outcomes may vary by subgroup") so that almost any claim can be argued to be "consistent with"
   it. Countered by scoring vagueness itself down (see §3 Step 3 rubric: an experiment whose
   `Expected outcome` is too unspecific to falsify entailment gets a capped `PARTIAL`, never
   `ENTAILED`, regardless of what the claim says).
2. **Type-laundering**: dress a correlational/observational result in causal-claim language, or state
   a point estimate as if it were a tested ranking. Countered by classifying claim type independently
   of the claim's own phrasing confidence, from the *experiment's actual design* (Setup/Procedure), and
   flagging a mismatch between claimed rhetorical strength and design-supportable strength as its own
   contradiction category.
3. **Selective citation of confirmatory external work**: `related_work.md` cites supporting priors and
   omits a same-population/same-intervention study with a null or opposite result. Countered by an
   independent [sem] search seeded from the claim's own entities (not from what `related_work.md`
   already chose to cite), so the metric can catch omissions the ARA itself would never surface.
4. **Endpoint switching in registered trials**: report a favorable secondary/post-hoc endpoint as the
   headline claim while downgrading or dropping the pre-registered primary endpoint. Countered by
   pulling the *registered* endpoint list from the registry, independent of what the paper foregrounds.
5. **Padding entailment "wins" with unfalsifiable claims**: a claim so hedged it can't be
   contradicted by anything scores as trivially "entailed." Countered by weighting each claim's
   contribution by its own grounding load (`Sources` entries with `[result]` tags per Statement) — a
   claim with no quoted numbers backing it contributes little regardless of the entailment verdict, and
   also separately fails the claims-layer grounding check (not this metric's job to double-count, but
   its weighting must not be foolable by zero-content claims).

### How the assessment-critique's notes change the design
The ledger says: *"Verifier does D1 semantically; the publication-bias cross-check beats both round-1
and verifier."* Two design consequences:
- **Don't re-litigate D1.** The ARA verifier already performs some semantic claim↔evidence entailment
  check (Seal Level 1/2 §9 cross-layer binding + rigor-review's evidential-grounding dimension). This
  metric's structural-resolution component (§3 Step 1) is kept *minimal and cheap* — a gate, not the
  scored centerpiece — precisely so this metric isn't just re-scoring what the verifier already scores.
  The scored centerpiece is the **type-aware discipline** (verifier's D1 pass is almost certainly
  type-agnostic — "is there support" — and this metric's edge is refusing to grant `ENTAILED` status to
  a ranking claim on the strength of a single-item comparison) and the **publication-bias cross-check**,
  which the verifier does not do at all (it has no external-registry or contradicting-literature search
  step).
- **Scope tighter, weight the net-new part more.** Because the entailment half overlaps partially with
  existing verifier machinery, this metric's score is weighted so the registry/contradiction
  cross-check (§3 Step 4) is not a minor addendum — it is roughly a third of the composite score (see
  §5 weights) and is *itself* structured to never collapse to a free pass (§3 Step 4d), which is what
  would happen if "no registry cited" or "no contradiction found" were treated as neutral rather than
  as an availability signal to be penalized per the hard constraint.

## 2. Inputs (artifact fields)

From `logic/claims.md`, per claim block `C##`: `Statement`, `Status`, `Falsification criteria`,
`Proof` (list of `E##`), `Evidence basis`, `Interpretation`, `Sources` (value/locator/quote/tag
5-tuples), `Tags`.

From `logic/experiments.md`, per experiment block `E##`: `Verifies` (list of `C##`), `Setup` (nested
key:value — including PICO-style subkeys `Population`/`Intervention`/`Endpoint`/`Randomization` when
present), `Procedure`, `Metrics`, `Expected outcome`, `Baselines`, `Dependencies`.

From `evidence/`: `README.md` index (Claims column, cross-check against `claims.md.Sources`), and the
actual table/figure files a claim's `Sources` entries point to (verbatim quoted rows/cells).

From `logic/problem.md` (§4, cross-layer, read-only for context): `Observations`/`Gaps` — used only to
pull cited prior-study identifiers (trial IDs, author-year) that might already name a "connected"
study, so the [sem]/[ext] search in Step 4 isn't duplicating a search the ARA already did.

From `logic/solution/constraints.md` (§7, cross-layer): `Known limitations` and the
compiler-added `Additional caveats surfaced during compilation` — used to check whether a
contradiction the metric's own search surfaces was already disclosed/reconciled by the ARA (if so,
the penalty in Step 4d is reduced — disclosure is rewarded even without full agreement).

## 3. Generation / compute workflow

### Step 0 — Parse
Deterministic markdown parse of the four files above into the dict shapes used by the Python in §4
(`claims: dict[str, Claim]`, `experiments: dict[str, Experiment]`, `evidence_index`,
`constraints_text`).

### Step 1 — Structural binding gate (deterministic, cheap; NOT the scored centerpiece)
For every claim `c`, resolve every `E##` in `c.proof` against `experiments`; for every resolved `E`,
check `c.id in E.verifies`. Also grep `experiments.md` bodies for stray digit patterns outside
allowed significance-threshold idioms (Critical Rule #3 detector, per the shape file's availability
notes) — a defect here caps the whole claim's entailment score below `ENTAILED` even if Step 3's LLM
judge is fooled, since a plan that leaks numbers is not a plan anymore, it's an evidence file
impersonating a plan.

### Step 2 — Claim-type classification ([sem] call #1)
One call per claim, using the claim's `Statement` + the resolved experiment(s)' `Setup`+`Procedure`
(design determines type; claim phrasing does not — this blocks type-laundering). Output constrained to
one of: `statistical_comparative`, `ranking`, `directional_qualitative`, `existence_detection`,
`mechanistic_causal`, `theoretical_proof`, `descriptive_replication`.

**Prompt (per claim c, experiment(s) Es):**
```
You are classifying the LOGICAL TYPE of a research claim based on the experiment DESIGN that
produced it (not the claim's wording, which may overstate the design).

Claim statement: {c.statement}
Experiment setup: {Es[i].setup for each i}
Experiment procedure: {Es[i].procedure for each i}

Classify into exactly one of:
statistical_comparative | ranking | directional_qualitative | existence_detection |
mechanistic_causal | theoretical_proof | descriptive_replication

Base the classification on what the PROCEDURE is actually capable of establishing, e.g. a pairwise
group-mean comparison is statistical_comparative even if the claim states it as a ranking; a proof
obligation with derivation steps is theoretical_proof even if phrased as an empirical result.

Return strict JSON: {"type": "<one of the above>", "type_confidence": "high|medium|low",
"design_vs_phrasing_mismatch": true|false, "mismatch_note": "<string or empty>"}
```
`design_vs_phrasing_mismatch=true` is itself recorded and feeds a direct penalty in §4 (type-laundering
detector, failure mode #2 above) independent of the entailment verdict.

### Step 3 — Type-aware entailment judgment ([sem] call #2, per claim)
Bundle: `c.statement`, `c.falsification_criteria`, `c.evidence_basis`, `c.sources` (value + verbatim
quote + tag), the resolved experiment(s)' `setup`/`procedure`/`metrics`/`expected_outcome`/`baselines`,
and the claim's `type` from Step 2.

**Prompt:**
```
TYPE = {type}. Apply exactly this type's entailment rubric — do not substitute general plausibility:

- statistical_comparative: the STATEMENT's numeric relationship/direction must be reproduced verbatim
  by the quoted evidence values; if the statement asserts significance, the quoted CI/p-value must
  actually support significance under the stated threshold.
- ranking: EVERY element of the stated order must appear, in that order, in the quoted evidence —
  a claim ranking N items is not entailed by evidence showing only the top item.
- directional_qualitative: evidence must show the same sign/direction described, magnitude not
  required, but the DIRECTION must be explicit in the quote, not inferred by you.
- existence_detection: evidence must show the entity/effect was observed at all (presence/absence),
  not a proxy for it.
- mechanistic_causal: procedure must include a manipulation (not merely an association test) whose
  result is what's quoted; correlational evidence cannot entail a causal statement — cap at PARTIAL.
- theoretical_proof: procedure must contain actual derivation/proof steps (not an empirical run)
  whose conclusion matches the statement; an empirical experiment cannot entail a proof-type claim.
- descriptive_replication: evidence must match the described replicated pattern within the
  experiment's own stated Baselines comparison.

Claim: {c.statement}
Falsification criteria: {c.falsification_criteria}
Cited evidence quotes: {c.sources[*].quote and value}
Experiment metrics/expected outcome/procedure: {...}

If the experiment's Metrics/Expected outcome are too unspecific to apply the rubric (e.g. no
comparator, no measurable direction stated), you MUST NOT return ENTAILED — return PARTIAL at best,
citing the specific missing specification.

Return strict JSON: {"label": "ENTAILED|PARTIAL|CONTRADICTED|UNGROUNDED",
"missing_elements": ["..."], "rationale": "<=40 words"}
```
`CONTRADICTED` = the quoted evidence itself, read under the rubric, is inconsistent with the statement
(e.g. CI crosses zero but claim asserts significance). `UNGROUNDED` = no usable quote/experiment link
to apply the rubric to at all (this must never be silently dropped — it is the worst-information case
and is scored, per the hard constraint, not skipped).

### Step 4 — Publication-bias / contradicting-evidence cross-check ([ext trial lookup] + [sem])
**4a. Genre + identifier detection** (deterministic): regex-scan `problem.md`, `constraints.md`,
`dataset.md`/`related_work.md` text for trial-registry identifiers (`NCT\d{8}`, ISRCTN, EudraCT
patterns) and scan `experiments.md` `Setup` keys for PICO-shaped subkeys
(`Population`/`Intervention`/`Endpoint`/`Randomization`).

**4b. Registrable path** (identifier or PICO-shaped design found): call the clinical-trial-registry
lookup tool.
- `get_trial_details(nct_id)` for any cited ID → extract registered primary/secondary outcome list and
  posted-results status.
- Compare registered outcome list against the experiment's `Metrics`/claim's `Statement` — any
  registered primary outcome absent from what's actually claimed, while a non-primary outcome is
  foregrounded, is flagged `endpoint_switch=true`.
- `search_trials(condition=..., intervention=...)` using terms pulled from `Setup.Population` /
  `Setup.Intervention` to find *other* trials on the same population+intervention not already named in
  `related_work.md`; for hits with posted results, diff their reported direction against the claim's
  `Statement` direction.

**4c. Non-registrable path** (no trial identifier/PICO — omics/ML/theory genres): run a [sem]
literature-contradiction search (semantic-scholar/undermind) seeded from the claim's own `Tags` +
the core entities in `Statement` (not from `related_work.md`'s existing citation list, so the search
can catch what the ARA itself omitted): "closely-matching study, same population/system + same
intervention-or-method + same outcome construct, reporting a different or null result." Any hit not
already named anywhere in `related_work.md` is a candidate omission.
- Additionally check whether `problem.md`/`constraints.md` mention ANY pre-registration/protocol
  (OSF, PROSPERO, trial registry) when `Setup.Design` language implies a confirmatory design (RCT,
  meta-analysis, pre-registered replication). Total absence of any registration mention under such a
  design is itself scored down per 4d below — it is a real availability defect, not a non-applicable
  check.

**4d. Scoring the cross-check per claim/experiment cluster:**
| situation | score |
|---|---|
| registrable + no endpoint-switch + no unreconciled contradicting trial | 1.0 |
| registrable + contradicting/connected trial found, but reconciled (discussed) in `related_work.md`/`constraints.md` | 0.7 |
| registrable + endpoint-switch or unreconciled contradicting trial found | 0.0 |
| registrable-implied design but NO registry identifier present at all | 0.2 (penalized: undisclosed/possibly-unregistered) |
| non-registrable genre, [sem] search performed, no contradicting omission found | 0.6 (capped — absence-of-evidence is weaker than a registry clearance) |
| non-registrable genre, contradicting omission found and unreconciled | 0.1 |
| non-registrable genre but confirmatory-design language present and zero pre-registration/protocol mentioned anywhere | 0.3 (penalized) |

No branch returns "N/A" or is excluded from the average — every claim/experiment cluster lands in one
of these buckets, which is how the hard constraint (penalize, never skip; unavailability is itself a
signal) is enforced at this step specifically.

## 4. Scoring function (Python, against the documented shapes)

```python
from dataclasses import dataclass, field
from enum import Enum

class EntailLabel(Enum):
    ENTAILED = 1.0
    PARTIAL = 0.5
    CONTRADICTED = 0.0
    UNGROUNDED = 0.1  # worst-information case; explicitly scored, never skipped

@dataclass
class Source:
    value: str
    locator: str
    quote: str | None   # None/empty is itself a defect (bare path, no verbatim quote)
    tag: str            # "input" | "result" | "pending"

@dataclass
class Claim:
    id: str
    statement: str
    status: str
    falsification: str
    proof: list[str]           # E## ids
    evidence_basis: str
    sources: list[Source]
    tags: list[str]

@dataclass
class Experiment:
    id: str
    verifies: list[str]        # C## ids
    setup: dict
    procedure: list[str]
    metrics: str
    expected_outcome: list[str]
    baselines: str

def structural_gate(claim: Claim, experiments: dict[str, Experiment]) -> float:
    """Step 1: cheap, minimal weight — do not re-score what the verifier already scores."""
    if not claim.proof:
        return 0.0
    resolved = [experiments[e] for e in claim.proof if e in experiments]
    if len(resolved) != len(claim.proof):
        return 0.2  # dangling reference: penalize, don't drop the claim from scoring
    if not all(claim.id in e.verifies for e in resolved):
        return 0.4  # one-directional binding only
    return 1.0

def grounding_weight(claim: Claim) -> float:
    """Down-weights claims with little/no quoted numeric backing so unfalsifiable claims
    can't buy a free ENTAILED average (failure mode #5)."""
    n_result_sources = sum(1 for s in claim.sources if s.tag == "result" and s.quote)
    return min(1.0, 0.25 + 0.25 * n_result_sources)  # floor 0.25, saturates at 3+ sources

def entailment_score(label: EntailLabel, type_mismatch: bool, vague_design: bool) -> float:
    base = label.value
    if type_mismatch:
        base = min(base, 0.5)   # type-laundering caps credit regardless of LLM label
    if vague_design and label == EntailLabel.ENTAILED:
        base = 0.5              # rubric step 3 forbids ENTAILED on vague designs; defensive clamp
    return base

def pubbias_score(bucket: str) -> float:
    table = {
        "registrable_clean": 1.0,
        "registrable_reconciled": 0.7,
        "registrable_violation": 0.0,
        "registrable_undisclosed": 0.2,
        "nonregistrable_clean": 0.6,
        "nonregistrable_violation": 0.1,
        "nonregistrable_no_protocol_confirmatory": 0.3,
    }
    return table[bucket]  # KeyError on unknown bucket is intentional: never silently default

def score_claim(claim: Claim, experiments: dict[str, Experiment],
                 type_result: dict, entail_result: dict, pubbias_bucket: str) -> dict:
    s_link = structural_gate(claim, experiments)
    w = grounding_weight(claim)
    s_ent = entailment_score(
        EntailLabel[entail_result["label"]],
        type_result["design_vs_phrasing_mismatch"],
        entail_result.get("vague_design", False),
    )
    s_pub = pubbias_score(pubbias_bucket)

    # weights: link is a gate not the centerpiece (0.15); entailment is the type-aware
    # discipline this metric adds over the verifier's flat D1 check (0.50);
    # pub-bias is the net-new, highest-value component per the assessment-critique (0.35)
    composite = 0.15 * s_link + 0.50 * s_ent + 0.35 * s_pub
    return {
        "claim_id": claim.id,
        "structural": s_link,
        "entailment": s_ent,
        "pubbias": s_pub,
        "grounding_weight": w,
        "weighted_composite": composite * w + composite * (1 - w) * 0.0,
        # note: weight discounts the claim's CONTRIBUTION to the artifact average,
        # it does not rescue the composite itself — a zero-source claim still scores
        # its true (usually low) composite, it just counts for less in the artifact roll-up.
    }

def m19_score(claims: dict[str, Claim], experiments: dict[str, Experiment],
              type_results: dict[str, dict], entail_results: dict[str, dict],
              pubbias_buckets: dict[str, str]) -> float:
    if not claims:
        return 0.0  # experiments.md/claims.md are mandatory core; empty is a hard floor, not N/A
    rows = [
        score_claim(c, experiments, type_results[c.id], entail_results[c.id], pubbias_buckets[c.id])
        for c in claims.values()
    ]
    total_w = sum(r["grounding_weight"] for r in rows) or 1e-9
    return sum(r["weighted_composite"] * r["grounding_weight"] for r in rows) / total_w
```

(The `weighted_composite` line intentionally reduces to `composite`; it is written this way to make
explicit that grounding-weight discounts a claim's *voting power* in the artifact-level average, not
its own truth value — a padding attempt that adds thin claims to dilute a bad average doesn't work,
because thin claims both score low AND count for little, they don't count for zero.)

## 5. Composition with the rest of the suite

- **Non-redundant with the ARA verifier's D1 semantic check**: the verifier's D1 asks "is there
  support"; this metric asks "does the *specific claim type's* entailment criterion hold against the
  *verbatim quoted* evidence," and additionally runs an external registry/literature contradiction
  search the verifier has no mechanism for at all. Weighted 0.15/0.50/0.35 specifically so the
  non-overlapping 0.35 (pub-bias) and the sharpened 0.50 (type-aware, not flat) dominate the
  overlapping 0.15 (structural resolution).
- **Composes with the evidence-grounding metric** (§9, `ev <> claim match`) rather than duplicating
  it: that metric checks whether `Sources` quotes exist and are verbatim; this metric consumes those
  quotes as *inputs* and asks a logically stronger question (do they entail the type-specific claim),
  so a claim can pass grounding but fail M19 (well-quoted but insufficient evidence for a ranking) —
  that is the intended, informative split, not overlap.
- **Composes with the constraints/limitations metric** (§7): a disclosed, reconciled contradiction
  scores 0.7 here specifically so that a paper which *admits* a connected contradicting result in
  `constraints.md` is rewarded relative to one that hides it — this creates a genuine incentive
  gradient toward disclosure rather than toward simply having no findable contradictions (which is
  often just a function of narrower search, not better science).

## 6. Why it's hard to Goodhart

1. **The type classification is derived from the experiment's design, not the claim's wording**
   (Step 2), so rephrasing a claim to sound more defensible does nothing — gaming would require
   changing the actual experimental design, which is the behavior the metric wants anyway.
2. **The contradiction search is seeded independently of the ARA's own citations** (Step 4c uses the
   claim's own entities, not `related_work.md`'s existing reference list), so an ARA cannot game the
   check merely by curating what it chooses to cite — the search actively looks past that curation.
3. **No branch of the publication-bias bucket table returns a free pass for absence of a check** —
   "no registry cited," "no protocol mentioned," and "search found nothing" are three different
   buckets with three different (non-maximal, in two of three cases) scores, closing the obvious
   Goodhart route of simply not mentioning trial identifiers to avoid the check triggering at all.
4. **Vague experiment designs are explicitly capped**, not rewarded, so the cheapest gaming route
   (write unfalsifiable `Expected outcome` text so nothing can ever be `CONTRADICTED`) is blocked at
   the rubric level (Step 3's explicit "must not return ENTAILED on unspecific design" instruction) and
   backstopped by the deterministic `vague_design` clamp in `entailment_score`.
5. **Grounding-weight prevents claim-padding**: adding many thin, unfalsifiable claims to dilute a
   damaging average doesn't work because those claims both score low on entailment (no usable quote to
   apply the rubric to → `UNGROUNDED`) and carry low voting weight — there is no configuration where
   adding claims improves the average.
