# M48 — End-to-end reproducibility bundle — Expansion 2

## 1. Expanded reasoning

### 1.1 What "good science" signal this indicator captures

An ARA can look fully compiled — grounded claims, a tidy evidence index, a plausible-sounding
method section — and still be **irreproducible** in the one sense that actually matters for
science: could an independent party, given only what's in the artifact, regenerate the reported
number or figure? That requires three physically distinct legs to exist **and connect to the same
claim**:

1. **Evidence** (§9) — the number/figure as reported.
2. **Data** (§11) — what was fed in, and at what access tier.
3. **Code/config** (§10) — what was run to turn data into evidence.

M48 is not "does `src/` exist" (that's closer to what a generic ARA verifier checks) and not "is
each layer internally well-formed" (that's what per-layer metrics like an evidence-completeness or
a config-provenance metric check). It is the **join**: for a given empirical claim, do the
evidence artifact, the data artifact, and the code artifact all name each other, consistently,
such that end-to-end replication is a real (even if labor-intensive) path rather than three
disconnected islands that happen to sit in the same repo. This is exactly the axis the
assessment-critique flagged as net-new versus the ARA verifier's "D6 mentions reproducibility" —
D6 presumably checks *presence* of reproducibility-relevant text; M48 checks *linkage and
sufficiency* across three specific layers for specific claims.

### 1.2 What it must reward

- Explicit **cross-references by claim id** (`C0N`) that tie an `evidence/tables/*.md` or
  `evidence/figures/*.md` entry to a `data/dataset.md` accession block and to a
  `src/execution/*.py` file or `src/artifacts.md` block. The more of these three-way ties exist
  for claims that are empirically load-bearing (i.e., the claims the paper's abstract/title rest
  on), the higher the score.
- **Honest, checkable disclosure of access tier and grounding**: an open-access dataset +
  `transcribed` code scores higher than a controlled-access dataset + `reconstructed` stub, which
  in turn scores higher than either being silently absent. The metric must reward papers that
  *tell the truth about how reproducible they are*, not just papers with more artifacts.
- **Consistency between the three layers' own self-reported completeness statements** —
  `evidence/README.md`'s completeness note, `src/environment.md`'s "Code availability" /ll "Data
  availability" subsections, and `data/dataset.md`'s "Provenance and access" section should agree
  with each other (e.g., if environment.md says "no code released," there should be no
  `src/execution/*.py` masquerading as real code, and no evidence table claiming to be
  independently regenerable).
- **Genre-appropriate completeness**, not maximal artifact count. A pure meta-analysis (che26)
  that has zero `src/execution/` files but *correctly* documents why, and whose evidence traces to
  disclosed controlled/open cohorts, should score higher than a paper that fabricates a code stub
  to look more reproducible.

### 1.3 What it must NOT reward

- Raw volume of files. Ten `src/execution/*.py` files that don't map to any specific claim, or a
  bloated `configs/` directory with no `Claims supported` linkage, add nothing — the metric must
  key off **claim-anchored joins**, not directory size.
- Cosmetic completeness: a `Code availability` paragraph that reads well but doesn't verifiably
  match what's actually in `src/execution/` (e.g., claims "all code available" while
  `src/artifacts.md` shows only a pointer to an uncloned repo) must not pass.
- Claims that are purely analytical/theoretical (a derivation, a definition, a qualitative
  narrative claim) being penalized for lacking a data/code leg — they are out of scope for this
  metric entirely (see §2.2), not scored zero. Conflating "no data needed" with "data leg missing"
  would make the metric fire on the wrong artifacts and duplicate other metrics' territory.

### 1.4 Failure modes / gaming routes and how the design blocks them

| Gaming route | Design countermeasure |
|---|---|
| Fabricate a `src/execution/*.py` stub with invented function bodies to fake a code leg | Grounding-tag check: file must open with `# Grounding: transcribed` or `reconstructed`; `reconstructed` files are capped at a lower leg-score than `transcribed`, and any stub whose only content is `raise NotImplementedError` for the mechanism the claim depends on scores as **absent**, not present, for that claim. |
| Claim "all code/data available" in prose without a mapped artifact | Score is computed **only** from structural, claim-id-linked evidence (README `Claims` column, `Claims supported` fields, dataset accession blocks) — free-text availability claims are used only as a *consistency check* against the structural facts, never as a scoring input on their own. A mismatch (prose says available, structure shows absent) is scored as the absent case *plus* a distinct honesty-flag penalty. |
| Pad `evidence/README.md`'s `Claims` column with ids to make every table look load-bearing | Cross-check against `logic/claims.md`: the claim must actually cite this table/figure back in its own `Sources` field (or exploration_tree.yaml node) — a one-directional link only asserted from the evidence side and not reciprocated from the claim side scores as weak, not full, evidence. |
| Dodge the metric by omitting a `data/` directory entirely for a paper that is obviously data-driven | Step 2 below classifies claims as in/out of scope from `logic/claims.md` + `logic/experiments.md` content, independent of whether `data/` exists. If classification says the claim is empirical/data-driven and `data/dataset.md` is absent, the data leg scores 0 (undisclosed absence) unless `src/environment.md` explicitly and specifically discloses why (matching the genre-appropriate-absence pattern documented in DATA_SHAPES §10/§11) — silence is punished harder than disclosed absence, but disclosed absence is still never full credit, because end-to-end replication genuinely isn't possible without the data. |
| Point at an external repo URL that doesn't actually exist/resolve, to get code-leg credit cheaply | Optional deterministic external check (§3, step 5): HEAD/metadata lookup on any repo URL cited in `src/artifacts.md`'s "File(s) in repo" field; an unresolvable URL demotes that block from "verified pointer" (leg score 1) to "unverifiable pointer" (leg score 0.3). |
| Game the aggregate by having 100% bundles on trivial/decorative claims while the paper's headline claim has no bundle at all | Aggregation (§3, step 6) weights per-claim bundle scores by claim centrality (title/abstract mention, in-degree in `exploration_tree.yaml`, or being cited by ≥1 other claim) rather than a flat mean — a perfect score on peripheral claims cannot offset a missing bundle on the central one. |

### 1.5 Why this composes cleanly with the rest of the suite

It shares fields with per-layer metrics (evidence completeness, config provenance, dataset
access-tier honesty) but computes a **distinct quantity**: those metrics ask "is this one layer
well-formed," M48 asks "do the three layers, joined at the claim level, actually let someone
replicate." Two ARAs can each score well on every individual per-layer metric and still differ
sharply on M48 if their layers simply don't reference each other by claim id. That non-redundancy
is exactly the scope the assessment-critique wanted preserved.

---

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields)

From the compiled ARA directory `<ara>/`:

- `logic/claims.md` — per-claim id, statement, `Sources` (evidence refs), rationale/derivation
  text.
- `logic/experiments.md` (optional, for classification signal — declares which analyses are
  data/code-driven).
- `evidence/README.md` — table/figure index rows: `File`, `Source`, `Claims`, `Description`; plus
  the completeness-note prose.
- `evidence/tables/*.md`, `evidence/figures/*.md` — `Extraction type` / `Extraction method` /
  `Reading confidence` fields.
- `src/environment.md` — `Code availability` / `Data availability` subsections (prose).
- `src/artifacts.md` — per-block `File(s) in repo`, `Nature`, `Claims supported`.
- `src/execution/*.{py,r,...}` — first-line grounding tag, filename/module.
- `src/configs/*.md` — per-parameter `Source` field (secondary signal only).
- `data/dataset.md` (+ `data/preprocessing.md`) — per-accession/cohort `Source / access`,
  `Provenance`, `Key variables`; secondary-reuse `Provenance and access` + `Included cohorts`
  table.
- `trace/exploration_tree.yaml` — used only for the centrality weight in aggregation (in-degree of
  a claim node).

### 2.2 Step 1 — Enumerate claims and classify scope [LLM call]

Parse `logic/claims.md` into a list of `(claim_id, statement, sources, rationale_text)`.

For each claim, classify with a single deterministic-output LLM call:

```
PROMPT (per claim):
"You are classifying a research claim by whether independently reproducing it requires running
code against data (as opposed to being a pure derivation, definition, qualitative narrative, or
literature-synthesis claim with no computational/empirical pipeline of its own).

Claim: {statement}
Rationale/derivation text: {rationale_text}

Answer with exactly one label:
- EMPIRICAL_COMPUTATIONAL  (requires data + a computational/statistical pipeline to reproduce)
- ANALYTICAL_ONLY          (pure math/logic derivation, no data pipeline)
- NARRATIVE_ONLY           (qualitative/descriptive claim, no reproducible artifact expected)
Output only the label."
```

This is the only place an LLM judgment enters scope; the label is deterministic-in-use afterward
(a lookup key), so it does not itself become a tunable "soft" sub-score. Claims labeled
`ANALYTICAL_ONLY` or `NARRATIVE_ONLY` are **excluded** from M48 scoring entirely (out of scope —
not scored zero; this is what prevents penalizing theory papers for lacking a data leg). If zero
claims are `EMPIRICAL_COMPUTATIONAL`, see the floor rule in step 7.

### 2.3 Step 2 — Build the evidence leg per in-scope claim

```python
def evidence_leg(claim_id, evidence_readme_rows, evidence_files):
    """evidence_readme_rows: list of {file, source, claims: [ids], description}
       evidence_files: dict[file] -> {extraction_type/method, reading_confidence, figure_type}"""
    matches = [r for r in evidence_readme_rows if claim_id in r["claims"]]
    if not matches:
        return 0.0, "no evidence file traces to this claim"
    best = 0.0
    for r in matches:
        f = evidence_files.get(r["file"], {})
        et = f.get("extraction_type") or f.get("extraction_method")
        conf = f.get("reading_confidence")
        if et in ("raw_table", "exact_from_labels"):
            score = 1.0
        elif et == "digitized_estimate" or conf == "medium":
            score = 0.66
        elif et == "visual_description" or conf == "low":
            score = 0.33
        else:
            score = 0.5  # derived_subset / mixed with no explicit confidence marker
        best = max(best, score)
    return best, None
```

### 2.4 Step 3 — Build the data leg per in-scope claim

```python
def data_leg(claim_id, dataset_blocks, environment_md_text):
    """dataset_blocks: list of {claims_linked or key_variables/cohorts, access_tier, accession_or_cohort}
       parsed from data/dataset.md; access_tier in {"open","controlled","descriptive_only","absent"}"""
    linked = [d for d in dataset_blocks if claim_id in d.get("claims_linked", [])]
    if not linked:
        # fall back: no explicit per-claim link, but a data/ dir exists at all for the ARA
        if dataset_blocks:
            return 0.4, "data/ exists but not claim-linked; weak leg"
        # data/ entirely absent — check disclosure
        if "no dataset" in environment_md_text.lower() or "analytical" in environment_md_text.lower():
            return 0.2, "disclosed genre-appropriate absence (still non-reproducible)"
        return 0.0, "undisclosed absence for an empirical claim"
    tier_score = {"open": 1.0, "controlled": 0.7, "descriptive_only": 0.4, "absent": 0.0}
    return max(tier_score[d["access_tier"]] for d in linked), None
```

`access_tier` classification (deterministic string match on `Source / access` field): presence of
"open" / a resolvable accession (GEO/SRA/dbGaP-metadata-open) → `open`; presence of "controlled
access", "dbGaP", "by request", "consortium" → `controlled`; a cohort named only in prose with no
accession/identifier → `descriptive_only`.

### 2.5 Step 4 — Build the code leg per in-scope claim

```python
def code_leg(claim_id, execution_files, artifacts_blocks, environment_md_text):
    """execution_files: list of {module, grounding_tag, claims_supported}
       artifacts_blocks: list of {repo_url_or_path, verified(bool), claims_supported, nature}"""
    exec_matches = [f for f in execution_files if claim_id in f.get("claims_supported", [])]
    if exec_matches:
        tags = [f["grounding_tag"] for f in exec_matches]
        if any(t == "transcribed" for t in tags):
            return 1.0, None
        if any(t == "reconstructed" for t in tags):
            return 0.6, None
        return 0.3, "execution file present but missing/invalid grounding tag"  # spec violation

    art_matches = [a for a in artifacts_blocks if claim_id in a.get("claims_supported", [])]
    if art_matches:
        if any(a["verified"] for a in art_matches):
            return 0.45, "pointer-only, verified to exist"
        return 0.15, "pointer-only, unverified/unverifiable"

    if "no code" in environment_md_text.lower() or "no analysis code was released" in environment_md_text.lower():
        return 0.2, "disclosed absence (still non-reproducible)"
    return 0.0, "undisclosed absence for an empirical claim"
```

### 2.6 Step 5 — Optional external verification [external call]

For any `artifacts.md` block whose `File(s) in repo` cites a GitHub/GitLab/Zenodo/OSF URL, issue a
lightweight metadata lookup (HTTP HEAD / provider API — not a semantic search call; this is a
factual existence check, analogous in spirit to the brief's undermind/semantic-scholar calls but
for repo resolution rather than literature) to set `verified` in step 4:

```python
def verify_repo_pointer(url: str) -> bool:
    # e.g. GitHub: GET api.github.com/repos/{owner}/{repo} -> 200 and non-empty
    # Zenodo/OSF: resolve DOI/landing page -> 200
    # Failure, timeout, or 404 -> False (never raises; treated as unverifiable, not as an error)
    ...
```

This step is optional in the sense that its absence (e.g., no network access at compute time)
must not cause an N/A — if it cannot run, `verified` defaults to `False`, which is the more
conservative (lower) score per the penalize-don't-skip constraint, never a skip of the leg.

### 2.7 Step 6 — Per-claim bundle score (structurally penalizes any missing leg)

```python
def bundle_score(ev, data, code):
    legs = [ev, data, code]
    return 0.5 * min(legs) + 0.5 * (sum(legs) / len(legs))
```

A claim with legs `(1.0, 1.0, 0.0)` scores `0.5*0 + 0.5*0.667 = 0.33`, not the `0.667` a plain
mean would give — a single absent leg caps the bundle well below "two-thirds good," which is the
concrete mechanism for "penalize missing any leg of fig/data/code."

### 2.8 Step 7 — Aggregate to the whole-ARA M48 score

```python
def m48_score(ara):
    claims = classify_claims(ara["logic/claims.md"])          # step 1 (LLM)
    in_scope = [c for c in claims if c.label == "EMPIRICAL_COMPUTATIONAL"]

    if not in_scope:
        # Whole paper is analytical/narrative: M48 is out of scope for the ARA, but per the
        # HARD CONSTRAINT we never silently emit N/A. Report the metric as scored at a fixed
        # neutral-low anchor (not full credit, not a skip) with an explicit "no in-scope claims"
        # flag, so downstream aggregation still sees a number and an availability signal.
        return {"score": 0.5, "flag": "no_empirical_computational_claims", "n_claims": 0}

    per_claim = []
    for c in in_scope:
        ev, ev_note   = evidence_leg(c.id, ara["evidence_readme_rows"], ara["evidence_files"])
        dt, dt_note   = data_leg(c.id, ara["dataset_blocks"], ara["environment_md_text"])
        cd, cd_note   = code_leg(c.id, ara["execution_files"], ara["artifacts_blocks"], ara["environment_md_text"])
        b = bundle_score(ev, dt, cd)
        weight = centrality_weight(c.id, ara["exploration_tree"])   # >=1.0, title/abstract or high in-degree claims weighted up
        per_claim.append((c.id, b, weight, {"evidence": ev, "data": dt, "code": cd,
                                             "notes": [n for n in (ev_note, dt_note, cd_note) if n]}))

    total_w = sum(w for _, _, w, _ in per_claim)
    score = sum(b * w for _, b, w, _ in per_claim) / total_w

    # Consistency cross-check: environment.md / dataset.md / README completeness prose must not
    # contradict the structural facts just computed. Any contradiction found demotes the score
    # further (multiplicative honesty penalty), it never raises it.
    honesty_penalty = consistency_check(ara)   # returns multiplier in (0, 1], 1.0 = fully consistent
    score *= honesty_penalty

    return {"score": round(score, 3), "n_claims": len(in_scope), "per_claim": per_claim,
            "honesty_multiplier": honesty_penalty}
```

`consistency_check` (deterministic, no LLM): flags e.g. `environment.md` prose claiming "all code
and data available" while ≥1 in-scope claim has `code_leg == 0` or `data_leg == 0`; each such
contradiction multiplies the running honesty multiplier by 0.85 (compounding, floor 0.4).

### 2.9 Never-skip / availability-is-signal enforcement

- If `evidence/`, `src/`, and `data/` are **all** entirely absent from the ARA while step 1
  produces ≥1 `EMPIRICAL_COMPUTATIONAL` claim, every leg is forced to 0 by construction (steps
  2–4's fallback branches), giving `bundle_score = 0.0` for every in-scope claim and thus
  `score = 0.0` for the ARA — not N/A, not excluded, the worst score on the scale.
- Every branch in steps 2–4 has an explicit "absent" return value (0.0, 0.2, or 0.4 depending on
  disclosure) — there is no code path that returns `None`/`NaN`/"not applicable." This is the
  concrete mechanism satisfying the brief's hard constraint.

---

## 3. Why this is hard to Goodhart

1. **The join, not the parts, is scored.** Padding any one layer (more files, longer prose) does
   nothing unless the new material is claim-id-linked to the other two layers *and* passes the
   grounding/access-tier checks — gaming it requires actually building the cross-layer linkage,
   which is most of the work of being genuinely reproducible in the first place.
2. **The minimum-plus-average blend structurally forbids "two strong legs hide one missing leg."**
   Any strategy that races to maximize evidence/data while skipping code (or vice versa) is capped
   near 33-40% regardless of how good the other two legs are.
3. **Grounding tags and access tiers are checked against controlled vocabularies pulled straight
   from the compiler spec** (`transcribed`/`reconstructed`, `open`/`controlled`), not free-text
   sentiment — an LLM can't be sweet-talked by well-written but unlinked prose, because the score
   only reads structural fields plus the single narrow scope-classification call.
4. **Disclosure is rewarded but capped below presence.** This removes the incentive to either (a)
   silently drop a hard leg, or (b) over-claim reproducibility in prose to compensate — both are
   detected and both score below the honestly-present case, so the equilibrium strategy is to
   actually build and link the bundle.
5. **Centrality weighting in aggregation** closes the "decorate peripheral claims, ignore the
   headline claim" loophole cheaply gameable metrics fall into.

## 4. Composition with the rest of the suite

M48 consumes structural facts that per-layer metrics also touch (evidence completeness, dataset
access-tier honesty, code-grounding-tag correctness) but converts them into a claim-anchored
cross-product rather than a per-layer average — it will disagree with those metrics precisely when
an ARA is well-formed layer-by-layer but poorly joined, which is the failure mode none of them
individually catch. It should be weighted in the final suite as a distinct "can this actually be
replicated end-to-end" signal, not merged with or substituted for the per-layer completeness
metrics it draws inputs from.
