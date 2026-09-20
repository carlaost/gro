# M48 — End-to-end reproducibility bundle (expander 1)

## 1. Expanded reasoning

### 1.1 What it actually asks

Not "does this ARA mention reproducibility" (that's verifier D6 — a coarse, whole-ARA,
presence-of-mention gate). M48 asks, **per reported result**: *for the specific numbers/figures the
source paper puts forward as evidence, can a competent outsider, using only what this ARA captured,
identify (a) the data that fed the result, (b) the code/tool/config that transformed that data into the
result, and (c) a faithful transcription of the result itself* — and do (a),(b),(c) actually point at
*each other*, not just coexist as three unrelated sections of the ARA?

That "point at each other" clause is the whole point of scoping this at §9 (evidence) with §10/§11 as
cross-layer dependencies rather than scoping it at §10 or §11 alone. A dataset section and a code
section can each independently look excellent while having no traceable connection to the figure they
supposedly produced (wrong dataset described, or code that computes something else in the paper). M48
is a **triangulation** metric, not a checklist of "these three folders exist."

### 1.2 What it must reward

- Per-evidence-object chains where a table/figure's caption or `Claims` ref-ids can be matched to (i)
  a named, access-tier-qualified dataset entry in `data/dataset.md`, and (ii) either transcribed/
  reconstructed code in `src/execution/`, a `src/artifacts.md` block, or a specifically-versioned
  off-the-shelf tool + parameter set in `src/environment.md`/`src/configs/`.
- **Honest, specific disclosure of a broken or absent leg** — e.g. che26's explicit "no code
  released... a `.py` stub reconstructed from prose would only duplicate `logic/solution/
  study_design.md`" — over silence. The metric must never treat "nothing is said" and "absence is
  named and justified" as the same failure; the latter is a materially more reproducible ARA even
  though the underlying paper is equally unreproducible.
- **Access-tier honesty on the data leg**: naming that raw reads are dbGaP-controlled while processed
  objects are open (huu25) is worth more than a blanket "data available," even though neither is a
  full unlock for the automated case.
- Genuinely genre-correct absence (pure theory/derivation work, or a work with no numbered
  quantitative claims) — but only when the ARA itself states the genre explicitly (a verbatim "no
  primary data were collected / no model was trained" type line in `environment.md` or `PAPER.md`),
  never inferred backward from the mere absence of `data/`/`src/execution/`. Inferring genre from
  absence is exactly the loophole a gamed ARA would exploit ("we just didn't write a data section, so
  score us as theory-exempt").

### 1.3 What it must NOT reward

- A `src/` folder full of real, well-documented code that has no discoverable relationship to any
  filed evidence object (e.g., a repo dump with no claim/figure cross-references) — presence without
  linkage is not end-to-end reproducibility, it's decoration.
- A `data/dataset.md` that states "data available" without an access tier, when the underlying source
  in fact gates raw data — this is the specific honesty defect the shape doc calls out, and rewarding
  the blanket phrasing as if it were the qualified one would train exactly the wrong ARA-writing habit.
- Diagram/qualitative-sample evidence objects fabricating a numeric data table to look more
  "reproducible" (Critical Rule #11 territory) — the evidence leg's own scoring must not create
  incentive pressure toward this.
- A single strong dataset+code pair being credited to *every* figure in the ARA by association rather
  than by evidence of actual applicability — e.g., crediting a table with a pipeline that produced a
  different, unrelated figure just because both live in the same ARA.

### 1.4 Failure modes / gaming routes and how the design blocks them

| Gaming route | Countermeasure in this design |
|---|---|
| Pad `src/artifacts.md`/`configs/` with generic, unlinked entries to inflate "code exists" | Linking step requires the LLM to cite the *specific* matched item and justify the match against the object's caption/claims/notes; unmatched entries don't count for that object |
| Claim genre-exemption ("theory paper") to dodge the data/code legs | Genre classification requires an explicit, quoted textual statement from the ARA itself, not inference from absence; absent both the quote and the artifact, treated as silent-absent (worst tier), not exempt |
| Write "data available upon request" boilerplate to look disclosed | Disclosure-quality tiers separate *vague* disclosure ("available," no tier, no reason) from *specific* disclosure (named reason, or explicit access tier); vague boilerplate scores closer to silent-absent than to a real disclosed-absence |
| Over-claim `exact_from_labels`/`raw_table` fidelity to boost the evidence leg | Evidence leg score is not self-reported by the artifact's own enum value alone — the workflow spot-checks internal consistency (does a `raw_table`/`exact_from_labels` object actually contain unrounded values with no `≈` markers, consistent with the shape doc's own flagged violation) |
| One dataset+pipeline gets credited to every evidence object regardless of fit | Weakest-link (`min`) aggregation per object plus per-object semantic matching (not global "does *a* dataset exist anywhere") — a mismatch is scored as `present_but_unlinked`, not `present_and_linked` |
| Ballast the ARA with many low-stakes figures at full reproducibility to dilute one badly-unreproducible headline result | Aggregation weights each object by how many claims it supports (`Claims` column), so headline objects (referenced by more claims) dominate the score more than an unweighted mean would allow |

### 1.5 Why §9 is the right primary artifact, with §10/§11 as dependencies (not equal partners)

The evidence layer is the anchor because it is the only layer that is **object-indexed and
enumerable** — "every `Table N`/`Figure N` in the source" is a checkable, closed set (per the shape
doc's completeness-ledger requirement). `src/` and `data/` are not indexed against anything by
themselves; they only become checkable once tied to a specific evidence object. Scoping the metric at
§9 with §10/§11 pulled in per-object is what makes "penalize missing any leg" a countable operation
rather than a vague impression, and is exactly the tightening the ledger note asks for relative to
D6's whole-ARA mention-check.

### 1.6 Composition with the rest of the suite

- **Vs. D6 (ARA verifier reproducibility mention)**: D6 is a floor check ("is reproducibility
  addressed anywhere, y/n"); M48 is object-scoped and quantitative, and can fail an ARA that passes D6
  trivially (e.g., a boilerplate "code and data available" line that doesn't survive per-object
  scrutiny). The two are intentionally correlated but not redundant — M48 should be read as "D6, but
  it has to actually be true, object by object, and it's a graded score, not a boolean."
- **Vs. an evidence-completeness metric** (e.g., "did the ARA file every numbered table/figure"):
  that metric only checks the evidence leg in isolation; M48 subsumes it as one of three legs but adds
  the code/data cross-reference, so a perfectly complete evidence ledger with orphaned code/data still
  scores low here.
- **Vs. a FAIR/data-access metric** (§11 indicator list mentions re-use/FAIR directly): that metric
  would score `data/dataset.md` on its own terms (licensing, accession quality); M48 only cares whether
  that data specifically backs a specific reported result. Low overlap: an ARA can have excellent FAIR
  data description generically while failing M48 if no evidence object is traceably tied to it.
- Should be weighted as a **methodological-rigor / trust-layer signal**, not a novelty or claims-
  quality signal — it says nothing about whether the science is correct or important, only whether an
  outsider could check it.

---

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields)

From `evidence/`:
- `evidence/README.md` — full text (Tables table, Figures table, completeness-note prose).
- `evidence/tables/*.md`, `evidence/figures/*.md` — full text of every filed object: `Source`,
  `Caption`, `Extraction type`/`Figure type`, `Extraction method`, `Reading confidence`, `Claims`
  (ref-ids), table body, `Notes`/`Trend summary`/`Visual description`.

From `src/` (cross-layer, §10):
- `src/environment.md` — full text, esp. `Framework`, `Key dependencies`, `Data sources`, and any
  `## Code availability` / `## Data availability` subsections.
- `src/artifacts.md` — every block (`File(s) in repo`, `Nature`, `Claims supported`).
- `src/configs/*.md` — every parameter block (`Value`, `Rationale`, `Source`).
- `src/execution/*` — filenames + first-line grounding tag (`transcribed`/`reconstructed`) + a
  ~20-line skim of each file's imports/entry point (not full-file reasoning — just enough to name what
  it computes).

From `data/` (cross-layer, §11):
- `data/dataset.md` — full text (accession blocks or secondary-reuse blocks, `Source / access`,
  `Included cohorts` table, `## External datasets used`, genre-statement prose).
- `data/preprocessing.md` if present.

From `PAPER.md` (only the top-of-file genre/type declaration, if present) — used solely to corroborate
a genre claim (theory/no-data) found in `environment.md`; not otherwise read.

### 2.2 Step 0 — Presence inventory (deterministic, no LLM)

```python
import re, pathlib

def presence_inventory(ara_root: pathlib.Path) -> dict:
    ev_dir = ara_root / "evidence"
    return {
        "evidence_readme": (ev_dir / "README.md").exists(),
        "table_files": sorted((ev_dir / "tables").glob("*.md")) if (ev_dir / "tables").exists() else [],
        "figure_files": sorted((ev_dir / "figures").glob("*.md")) if (ev_dir / "figures").exists() else [],
        "environment_md": (ara_root / "src" / "environment.md").exists(),
        "artifacts_md": (ara_root / "src" / "artifacts.md").exists(),
        "config_files": sorted((ara_root / "src" / "configs").glob("*.md")) if (ara_root / "src" / "configs").exists() else [],
        "execution_files": sorted((ara_root / "src" / "execution").rglob("*")) if (ara_root / "src" / "execution").exists() else [],
        "dataset_md": (ara_root / "data" / "dataset.md").exists() if (ara_root / "data").exists() else False,
        "preprocessing_md": (ara_root / "data" / "preprocessing.md").exists() if (ara_root / "data").exists() else False,
    }
```

This never "skips" — an entirely-absent `src/` or `data/` directory is a valid, recorded state fed
into Step 3, not a reason to abstain from scoring.

### 2.3 Step 1 — [LLM] Structure the evidence inventory

One call, given `evidence/README.md` + concatenated table/figure files.

**Prompt (exact):**
> You are extracting a structured inventory from an evidence ledger. Input: the full text of
> `evidence/README.md` and every file under `evidence/tables/` and `evidence/figures/`.
>
> Return JSON:
> ```
> {
>   "source_numbered_objects": {"tables_claimed": <int>, "figures_claimed": <int>},
>   "objects": [
>     {
>       "id": "<filename stem>",
>       "kind": "table" | "figure",
>       "filed": true,
>       "claims": ["C01", ...],
>       "caption": "<verbatim caption>",
>       "type": "raw_table" | "derived_subset" | "quantitative_plot" | "diagram" | "qualitative_sample" | "mixed",
>       "extraction_method": "exact_from_labels" | "digitized_estimate" | "visual_description" | null,
>       "reading_confidence": "high" | "medium" | "low" | null,
>       "has_data_table": true|false,
>       "uses_approx_markers": true|false,
>       "mentions_dataset_or_method": "<verbatim snippet from caption/notes naming a dataset, cohort, tool, or method, or empty string>"
>     }, ...
>   ],
>   "unfiled_objects": [
>     {"ref": "Table 4" or "Figure S1", "reason_given": "<verbatim reason from README, or null if not accounted for at all>"}
>   ],
>   "completeness_note_present": true|false
> }
> ```
> Use only what's stated in the text; do not infer values not present. `source_numbered_objects`
> should reflect the total count of `Table N`/`Figure N` objects the README/completeness note states
> existed in the source (filed + unfiled), not just what's filed.

**Deterministic post-processing:**
```python
def evidence_leg_score(obj: dict) -> float:
    """Fidelity of the transcription itself — the object's own reliability as ground truth."""
    if obj["type"] in ("diagram", "qualitative_sample"):
        return 1.0  # no data table required by spec
    if obj["type"] == "mixed":
        return 0.8  # per-panel nuance not modeled at this granularity; conservative default
    # raw_table / derived_subset / quantitative_plot
    if not obj["has_data_table"] and obj.get("reading_confidence") != "low":
        return 0.0  # structural failure per shape doc: neither table nor low-confidence fallback
    if obj["extraction_method"] == "exact_from_labels" and obj["uses_approx_markers"]:
        return 0.3  # mislabeling violation: approx values under an exact-fidelity label
    if obj["extraction_method"] == "exact_from_labels":
        return 1.0
    if obj["extraction_method"] == "digitized_estimate":
        return 0.6
    if obj.get("reading_confidence") == "low":
        return 0.35  # unreadable but honestly flagged, trend-summary substitutes
    return 0.2
```

### 2.4 Step 2 — [LLM] Structure the code and data inventories

One call given `src/environment.md`, `src/artifacts.md`, `src/configs/*.md`, filenames + grounding
tags from `src/execution/`, and `data/dataset.md` (+ `preprocessing.md`).

**Prompt (exact):**
> You are extracting structured inventories of the implementation and data layers of a research
> artifact. Input: the full text of `src/environment.md`, `src/artifacts.md`, all `src/configs/*.md`
> files, the filename and first-line grounding comment of every `src/execution/*` file, and the full
> text of `data/dataset.md` (+ `preprocessing.md` if given).
>
> Return JSON:
> ```
> {
>   "genre_statement": "<verbatim quoted sentence from environment.md or PAPER.md explicitly stating the work is theory-only / no primary data / no code produced, or null if no such explicit statement exists>",
>   "code_availability_statement": {"present": true|false, "verbatim": "<quote or null>", "names_specific_toolchain": true|false, "toolchain_detail": "<e.g. 'netmeta R package v4.5.2' or null>"},
>   "data_availability_statement": {"present": true|false, "verbatim": "<quote or null>"},
>   "code_items": [
>     {"name": "<artifact/config/execution file name>", "kind": "execution_file"|"artifacts_block"|"config_block",
>      "grounding_tag": "transcribed"|"reconstructed"|null, "claims_supported": ["C01",...] | "all" | [],
>      "what_it_does": "<one sentence, grounded in the text only>"}
>   ],
>   "data_items": [
>     {"name": "<accession or cohort-table name>", "access_tier": "open"|"controlled"|"mixed"|"unspecified",
>      "size_content": "<verbatim or empty>", "claims_or_objects_named": "<any Table/Figure/claim ids explicitly tied to this dataset in the text, else empty>"}
>   ]
> }
> ```
> Only extract what is explicitly stated. `access_tier` must be `"unspecified"` (not `"open"`) if the
> text says data is "available" without stating whether it is open or gated.

### 2.5 Step 3 — [LLM] Cross-layer linking, per evidence object

For each `objects[i]` from Step 1, one batched call (all objects in one prompt, structured output
array) against the `code_items` / `data_items` from Step 2.

**Prompt (exact):**
> For each evidence object below (with its caption, claims, and any dataset/method snippet), decide
> whether the code inventory and the data inventory each contain an item that plausibly produced or
> supplied this specific object — not merely "some code/data exists in this ARA," but a specific,
> named item whose stated purpose or content matches this object's caption/claims/method mention.
>
> For each object return:
> ```
> {"id": "<object id>",
>  "code_leg": "linked" | "unlinked_present" | "toolchain_named" | "absent",
>  "code_match": "<name of matched code_item, or toolchain_detail, or null>",
>  "code_justification": "<one sentence citing the specific match or naming why nothing matched>",
>  "data_leg": "linked" | "unlinked_present" | "absent",
>  "data_match": "<name of matched data_item, or null>",
>  "data_justification": "<one sentence>"}
> ```
> `linked` requires the matched item's stated purpose/content to plausibly cover this object's specific
> caption/method, not just be present somewhere in the ARA. `toolchain_named` applies only to the code
> leg when no custom code exists but a specific versioned off-the-shelf tool from
> `code_availability_statement` plausibly covers this object's method. Do not mark `linked` on
> topical similarity alone — require the object's `claims` or `mentions_dataset_or_method` snippet to
> overlap with the matched item's stated `claims_supported`/content.

**Deterministic scoring of the leg verdicts**, using the disclosure-quality distinction from §1.2:

```python
CODE_LEG = {"linked": 1.0, "unlinked_present": 0.6, "toolchain_named": 0.75}
DATA_LEG = {"linked": 1.0, "unlinked_present": 0.5}

def resolved_leg_score(leg: str, match_kind: str, disclosure: dict, genre_exempt: bool) -> float:
    """disclosure = the relevant *_availability_statement dict from Step 2."""
    if genre_exempt:
        return 1.0  # structurally inapplicable, not a gap — excluded from penalty, not "skipped" from the artifact's existence question
    table = CODE_LEG if leg == "code_leg" else DATA_LEG
    if match_kind in table:
        return table[match_kind]
    # match_kind == "absent": grade by disclosure quality, per the hard constraint
    # (unavailability is itself an input; never scored as N/A)
    if disclosure.get("present") and disclosure.get("verbatim"):
        # specific, reasoned disclosure (e.g. che26's "no code released... would duplicate X")
        return 0.3
    if disclosure.get("present"):
        # vague boilerplate ("available upon request", no tier/reason)
        return 0.15
    return 0.0  # silent absence — worst tier
```

`genre_exempt` is set to `True` for the **data leg only** (code can always in principle be produced
for empirical work; a *data* leg is only structurally inapplicable for genuinely non-empirical work)
and only when `genre_statement` from Step 2 is non-null AND independently corroborated by the object
having no `mentions_dataset_or_method` snippet and no numeric content. Never set from directory
absence alone.

### 2.6 Step 4 — Per-object bundle score (weakest-link)

```python
def object_bundle_score(evidence_score: float, code_score: float, data_score: float) -> float:
    # weakest-link: an excellent code leg cannot compensate for an absent/unlinked data leg,
    # per "penalize missing any leg of fig/data/code"
    return min(evidence_score, code_score, data_score)
```

### 2.7 Step 5 — ARA-level aggregation

```python
def compute_m48(evidence_json: dict, links_json: list[dict], claims_weight_floor: int = 1) -> dict:
    objects = {o["id"]: o for o in evidence_json["objects"]}
    per_object = []
    for link in links_json:
        obj = objects[link["id"]]
        e = evidence_leg_score(obj)
        c = resolved_leg_score("code_leg", link["code_leg"], disclosure=code_availability_statement,
                                genre_exempt=False)
        d = resolved_leg_score("data_leg", link["data_leg"], disclosure=data_availability_statement,
                                genre_exempt=is_genre_exempt(obj, genre_statement))
        bundle = object_bundle_score(e, c, d)
        weight = claims_weight_floor + len(obj.get("claims", []))
        per_object.append({"id": obj["id"], "evidence": e, "code": c, "data": d,
                            "bundle": bundle, "weight": weight})

    # Unfiled/undisclosed source objects count as zero-bundle entries at baseline weight —
    # this is what makes evidence-layer completeness itself part of M48, per the hard constraint
    # that availability of the underlying artifact/field is part of the score, not a precondition for it.
    for unfiled in evidence_json["unfiled_objects"]:
        score = 0.3 if unfiled.get("reason_given") else 0.0
        per_object.append({"id": unfiled["ref"], "evidence": score, "code": 0.0, "data": 0.0,
                            "bundle": score, "weight": claims_weight_floor})

    if not per_object:
        # No numbered objects at all, and none claimed to exist: this is the paywalled/
        # abstract-only floor case. Score is not skipped — it is the minimum, because the ARA
        # cannot support end-to-end replication of anything.
        return {"m48_score": 0.0, "per_object": [], "note": "no evidence objects filed or claimed"}

    total_weight = sum(o["weight"] for o in per_object)
    score = sum(o["bundle"] * o["weight"] for o in per_object) / total_weight
    return {"m48_score": round(score, 4), "per_object": per_object}
```

`is_genre_exempt(obj, genre_statement)` implements the corroboration rule from §2.5:

```python
def is_genre_exempt(obj: dict, genre_statement: str | None) -> bool:
    if not genre_statement:
        return False
    non_empirical_kinds = {"diagram", "qualitative_sample"}
    return obj["type"] in non_empirical_kinds and not obj.get("mentions_dataset_or_method")
```

Final metric value is `m48_score` in [0, 1]. No branch of this pipeline returns `None`/`N/A`: an ARA
with no `evidence/` directory at all produces `evidence_json["objects"] == []` and
`unfiled_objects == []` only if `source_numbered_objects` is also `{0,0}` (genuinely no numbered
objects existed in the source, itself a rare and checkable claim); any other empty-evidence case where
the source plainly has tables/figures but none were filed and none accounted for falls into the
`unfiled_objects` path with `reason_given: null`, scoring `0.0` per object, not abstaining.

## 3. Why hard to Goodhart, and composition (summary)

Hardness comes from three compounding requirements that can't be satisfied by padding any single
layer: (1) linking is **per-object and semantic**, requiring the matched code/data item's stated
purpose to actually overlap the evidence object's caption/claims — generic "we have a GitHub repo"
statements don't clear `linked` without a plausible content match; (2) the **weakest-link aggregation**
means an ARA can't average away one badly-unreproducible headline figure by having many fully-linked
minor ones, and claims-weighting further prevents diluting a heavily-cited result with padding; (3)
**disclosure-quality grading is separate from mere absence**, so vague boilerplate ("data available
upon request") is explicitly scored below a specific, reasoned absence statement — closing the cheapest
gaming route (writing something that sounds like disclosure without committing to a checkable claim).
The genre-exemption path is the one deliberate escape valve, and it's gated on an explicit quoted
statement plus independent corroboration from the object's own content, specifically to prevent "we
just didn't write a data section" from masquerading as "this is theory work."

Composition: M48 sits in the trust/rigor tier of the suite alongside D6 (which it strictly refines) and
any FAIR/data-access or evidence-completeness metrics (which it depends on as input signals but is not
redundant with, since it adds the code/data cross-reference those metrics don't check). It says nothing
about claim correctness, novelty, or scientific importance — only about whether an outside agent could,
in principle, verify the specific numbers the paper reports using only what this ARA captured.
