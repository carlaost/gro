# M48 — End-to-end reproducibility bundle (cycle 2, improved exp1)

## Changes (cycle 2)

1. **Soft-min replaces strict `min()`.** Per-object bundle score is now a harmonic mean of
   (evidence, code, data) with an explicit hard-zero rule: if any leg is exactly `0.0`, the bundle is
   `0.0` (silent absence / structural failure / fabrication still hard-caps, matching exp3's
   fabrication-caps-the-bundle behavior and the brief's penalize-don't-skip floor) — but for non-zero
   weak legs, `[0.01, 1, 1]` (≈0.029) and `[0.01, 0.01, 0.01]` (=0.01) no longer collapse to the same
   score, fixing the brittleness the judge flagged.
2. **Anchor-matching gates `linked`.** Steps 1 and 2 now extract verbatim numeric/named anchors
   (sample sizes, key statistic values, accession-like tokens, dependency/tool versions, parameter
   values) from evidence objects and from code/data items respectively. Step 3's `linked` verdict
   requires an anchor to actually overlap between the object and its matched item — topical/semantic
   similarity alone is downgraded to a new `linked_no_anchor` tier (0.85), and a positive *anchor
   contradiction* (object states n=601, matched dataset states n=42) is downgraded further to
   `unlinked_present`, not credited as a match. This imports exp4's most Goodhart-resistant mechanism:
   faking a link now requires two independently-formatted layers to numerically agree, not just read
   as topically similar.
3. **Explicit fabrication tier, hard-capping the object.** `evidence_leg_score` now detects the
   Critical-Rule-#11 violation directly (a `diagram`/`qualitative_sample` object whose own
   `has_data_table` field is `true` — i.e. it carries a numeric table its type forbids) and returns
   `0.0` with a `fabricated: true` flag, rather than folding this into a generic low score. Because of
   the hard-zero rule in fix (1), this now hard-caps the *whole bundle*, not just the evidence leg —
   closing the gap the judge noted relative to exp3's whole-bundle fabrication cap. The same
   `fabricated` tier is added to the code/data leg verdicts for the case where the linking step finds a
   *positive, stated contradiction* between an item's claimed grounding and its content (e.g., a
   `transcribed`-tagged execution file whose skimmed entry point computes a demonstrably different
   quantity than any claim it lists) rather than mere absence of a match.
4. **Scope note on the evidence leg vs. a hypothetical transcription-fidelity metric.** Added §1.7
   below, addressing the judge's weakness that "the evidence leg is largely transcription-fidelity,
   which drifts toward single-layer quality that other metrics may own." The evidence leg's role in
   M48 is now explicitly bounded: it exists only to certify that the object is trustworthy enough to
   serve as the *anchor* the code/data legs get checked against, not to grade transcription quality for
   its own sake. Practically this is enforced by the hard-zero/fabrication rule above (an object either
   clears the bar to be usable as ground truth, or the whole bundle is zeroed) plus keeping the
   graded-but-non-zero tiers (`digitized_estimate`=0.6, mislabel=0.3, low-confidence=0.35) deliberately
   coarse rather than adding further fidelity granularity — any finer transcription-quality scoring
   belongs to a dedicated evidence-completeness/fidelity metric, not to M48.

Everything else — §9-object-indexing as primary anchor, per-object semantic linking, disclosure-quality
tiers, claims-weighting, genre-exemption gating on an explicit quote + independent corroboration — is
carried forward unchanged from exp1 cycle 1, per the judge's explicit instruction to keep that anchoring
because it is the truest reading of the brief.

---

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
is a **triangulation** metric, not a checklist of "these three folders exist." Cycle 2 sharpens
"point at each other" from a semantic-plausibility check into a check that also demands a shared,
independently-formatted **anchor value** — see §1.2 and §2.5.

### 1.2 What it must reward

- Per-evidence-object chains where a table/figure's caption or `Claims` ref-ids can be matched to (i)
  a named, access-tier-qualified dataset entry in `data/dataset.md`, and (ii) either transcribed/
  reconstructed code in `src/execution/`, a `src/artifacts.md` block, or a specifically-versioned
  off-the-shelf tool + parameter set in `src/environment.md`/`src/configs/` — **and (cycle 2) where a
  numeric or named anchor from the object (a sample size, a reported statistic, an accession token, a
  version string) is independently reproduced in the matched item**, not merely topically adjacent to
  it. Two independently-formatted layers agreeing on a specific value is much harder to fake than two
  layers both mentioning the same general topic.
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
  "reproducible" (Critical Rule #11 territory) — **cycle 2 makes this an explicit, hard-capping
  fabrication tier (§2.3, §2.6) rather than a soft discount folded into the transcription score**, so
  the evidence leg's own scoring cannot be gamed by fabricating structure that superficially resembles
  rigor.
- A single strong dataset+code pair being credited to *every* figure in the ARA by association rather
  than by evidence of actual applicability — e.g., crediting a table with a pipeline that produced a
  different, unrelated figure just because both live in the same ARA. **Cycle 2 hardens this further**:
  even a semantically-plausible match that lacks any shared anchor is capped at `linked_no_anchor`
  (0.85) rather than full credit, and a match whose anchor actively contradicts the object's own anchor
  is refused outright (§2.5).

### 1.4 Failure modes / gaming routes and how the design blocks them

| Gaming route | Countermeasure in this design |
|---|---|
| Pad `src/artifacts.md`/`configs/` with generic, unlinked entries to inflate "code exists" | Linking step requires the LLM to cite the *specific* matched item and justify the match against the object's caption/claims/notes; unmatched entries don't count for that object |
| Claim genre-exemption ("theory paper") to dodge the data/code legs | Genre classification requires an explicit, quoted textual statement from the ARA itself, not inference from absence; absent both the quote and the artifact, treated as silent-absent (worst tier), not exempt |
| Write "data available upon request" boilerplate to look disclosed | Disclosure-quality tiers separate *vague* disclosure ("available," no tier, no reason) from *specific* disclosure (named reason, or explicit access tier); vague boilerplate scores closer to silent-absent than to a real disclosed-absence |
| Over-claim `exact_from_labels`/`raw_table` fidelity to boost the evidence leg | Evidence leg score is not self-reported by the artifact's own enum value alone — the workflow spot-checks internal consistency (does a `raw_table`/`exact_from_labels` object actually contain unrounded values with no `≈` markers, consistent with the shape doc's own flagged violation) |
| One dataset+pipeline gets credited to every evidence object regardless of fit | Weakest-link (soft-min harmonic mean, cycle 2) aggregation per object plus per-object semantic matching (not global "does *a* dataset exist anywhere") — a mismatch is scored as `present_but_unlinked`, not `present_and_linked` |
| A semantically-plausible but unrelated code/data item is claimed as the match (topical, not actual, overlap) | **(cycle 2)** `linked` requires a shared numeric/named anchor between the object and the matched item; a match with no anchor overlap is capped at `linked_no_anchor` (0.85), and a match whose anchor directly contradicts the object's own anchor is refused (scored `unlinked_present`, not `linked`) |
| Fabricate a numeric table inside a `diagram`/`qualitative_sample` object to look quantitatively rigorous | **(cycle 2)** Detected directly from the object's own `has_data_table` flag against its declared `type`; scored `0.0` with `fabricated: true`, which — under the harmonic-mean hard-zero rule — zeroes the *entire bundle* for that object, not just the evidence leg |
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
- **(cycle 2) Vs. a dedicated transcription-fidelity metric**: see §1.7. M48's evidence-leg scoring is
  intentionally coarse and gate-like, not a fine-grained fidelity grade.
- Should be weighted as a **methodological-rigor / trust-layer signal**, not a novelty or claims-
  quality signal — it says nothing about whether the science is correct or important, only whether an
  outsider could check it.

### 1.7 (cycle 2) The evidence leg is a ground-truth gate, not a fidelity grade

The judge's rank-1 critique noted a real risk: the evidence-leg scoring (§2.3) grades transcription
quality — `exact_from_labels` vs `digitized_estimate` vs mislabeled vs low-confidence — which is a
dimension a dedicated single-layer fidelity metric could plausibly also own, creating redundancy in the
suite. M48 keeps this scoring, because the linking step (§2.5) is only meaningful if the object being
linked *is what it claims to be*: an object whose transcription is unreliable can't function as ground
truth for checking whether the code/data legs actually produced it. But M48's use of this score is
narrower than a fidelity metric's would be:
- The tiers are deliberately coarse (five buckets, not a continuous fidelity scale), because M48 only
  needs to know "is this object trustworthy enough to anchor a cross-layer check," not "how good is
  the transcription on a fine scale."
- The one case that must be *exact*, not graded, is fabrication (§2.3, §2.6): an object masquerading as
  a type it isn't (Critical Rule #11) doesn't get a partial fidelity discount — it hard-zeroes the whole
  bundle, because a fabricated object cannot serve as ground truth for anything, and no amount of
  code/data linkage rescues a claim anchored to invented evidence.
- Any richer transcription-quality analysis (e.g., cell-by-cell digitization accuracy, caption
  paraphrase quality) is out of scope for M48 and belongs to whatever metric in the suite owns
  evidence-layer quality in isolation; M48 only imports the minimum signal needed to gate the linking
  legs.

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
into Step 3 (renumbered: linking; see below), not a reason to abstain from scoring.

### 2.3 Step 1 — [LLM] Structure the evidence inventory (+ anchors, cycle 2)

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
>       "mentions_dataset_or_method": "<verbatim snippet from caption/notes naming a dataset, cohort, tool, or method, or empty string>",
>       "anchors": ["<verbatim numeric or named value from caption/notes/table headers that could be independently checked elsewhere, e.g. 'n=601', 'AUC=0.85', 'GSE123456', 'v4.5.2'; empty list if none>"]
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
> existed in the source (filed + unfiled), not just what's filed. `anchors` must be verbatim substrings
> or near-verbatim numeric values actually present in the caption, notes, or table header/footnote text
> — do not read individual data-table cell values here (that would make every object trivially
> "anchored"); extract only distinguishing summary-level values a reader would recognize as identifying
> this specific object (sample sizes, headline statistics, accession-like tokens, version strings).

**Deterministic post-processing:**
```python
def evidence_leg_result(obj: dict) -> dict:
    """Fidelity of the transcription itself — a gate on the object's trustworthiness as ground
    truth for the linking step (§1.7), not a fine-grained fidelity grade."""
    if obj["type"] in ("diagram", "qualitative_sample"):
        if obj["has_data_table"]:
            # Critical Rule #11 violation: a non-quantitative type carrying a numeric data table
            # is fabricated structure, not an honest transcription — hard-fails, does not merely
            # discount (cycle 2).
            return {"score": 0.0, "fabricated": True}
        return {"score": 1.0, "fabricated": False}  # no data table required by spec
    if obj["type"] == "mixed":
        return {"score": 0.8, "fabricated": False}  # per-panel nuance not modeled at this granularity; conservative default
    # raw_table / derived_subset / quantitative_plot
    if not obj["has_data_table"] and obj.get("reading_confidence") != "low":
        return {"score": 0.0, "fabricated": False}  # structural failure: neither table nor low-confidence fallback
    if obj["extraction_method"] == "exact_from_labels" and obj["uses_approx_markers"]:
        return {"score": 0.3, "fabricated": False}  # mislabeling violation: approx values under an exact-fidelity label
    if obj["extraction_method"] == "exact_from_labels":
        return {"score": 1.0, "fabricated": False}
    if obj["extraction_method"] == "digitized_estimate":
        return {"score": 0.6, "fabricated": False}
    if obj.get("reading_confidence") == "low":
        return {"score": 0.35, "fabricated": False}  # unreadable but honestly flagged, trend-summary substitutes
    return {"score": 0.2, "fabricated": False}
```

### 2.4 Step 2 — [LLM] Structure the code and data inventories (+ anchors, cycle 2)

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
>      "what_it_does": "<one sentence, grounded in the text only>",
>      "anchors": ["<verbatim numeric/named value stated for this item: a parameter value, a dependency version, a sample-size or n used in a config, etc.; empty list if none>"]}
>   ],
>   "data_items": [
>     {"name": "<accession or cohort-table name>", "access_tier": "open"|"controlled"|"mixed"|"unspecified",
>      "size_content": "<verbatim or empty>", "claims_or_objects_named": "<any Table/Figure/claim ids explicitly tied to this dataset in the text, else empty>",
>      "anchors": ["<verbatim numeric/named value stated for this item: cohort size, accession id, version; empty list if none>"]}
>   ]
> }
> ```
> Only extract what is explicitly stated. `access_tier` must be `"unspecified"` (not `"open"`) if the
> text says data is "available" without stating whether it is open or gated. `anchors` follows the same
> rule as in the evidence-extraction step: verbatim, summary-level, distinguishing values only.

### 2.5 Step 3 — [LLM] Cross-layer linking, per evidence object (anchor-gated, cycle 2)

For each `objects[i]` from Step 1, one batched call (all objects in one prompt, structured output
array) against the `code_items` / `data_items` from Step 2.

**Prompt (exact):**
> For each evidence object below (with its caption, claims, dataset/method snippet, and anchors),
> decide whether the code inventory and the data inventory each contain an item that plausibly
> produced or supplied this specific object — not merely "some code/data exists in this ARA," but a
> specific, named item whose stated purpose or content matches this object's caption/claims/method
> mention. Then check whether any anchor value on the object side and any anchor value on the matched
> item's side agree (verbatim or the same number, allowing unit/rounding differences of the kind a
> human would still call "the same value") or actively disagree.
>
> For each object return:
> ```
> {"id": "<object id>",
>  "code_leg": "linked" | "linked_no_anchor" | "unlinked_present" | "toolchain_named" | "fabricated" | "absent",
>  "code_match": "<name of matched code_item, or toolchain_detail, or null>",
>  "code_anchor_check": "agree" | "disagree" | "no_anchors_available" ,
>  "code_justification": "<one sentence citing the specific match and anchor outcome, or naming why nothing matched>",
>  "data_leg": "linked" | "linked_no_anchor" | "unlinked_present" | "fabricated" | "absent",
>  "data_match": "<name of matched data_item, or null>",
>  "data_anchor_check": "agree" | "disagree" | "no_anchors_available",
>  "data_justification": "<one sentence>"}
> ```
> Rules:
> - `linked` requires (a) the matched item's stated purpose/content to plausibly cover this object's
>   specific caption/method (not just be present somewhere in the ARA), AND (b) `*_anchor_check ==
>   "agree"` — at least one anchor value present on both sides that matches.
> - `linked_no_anchor` applies when (a) holds but neither side has any extractable anchor at all
>   (`no_anchors_available`) — a plausible semantic match that cannot be independently checked by a
>   shared value, so it is credited but at a discount.
> - If `*_anchor_check == "disagree"` (both sides have anchors but they contradict — e.g. object says
>   n=601, matched item says n=42), do NOT mark `linked` or `linked_no_anchor` even if the semantic
>   match otherwise looks plausible; mark `unlinked_present` instead.
> - `toolchain_named` applies only to the code leg when no custom code exists but a specific versioned
>   off-the-shelf tool from `code_availability_statement` plausibly covers this object's method.
> - `fabricated` applies only when there is positive evidence of invention or contradiction beyond mere
>   absence or anchor mismatch — e.g. a `transcribed`-tagged execution file whose skimmed entry point
>   computes something demonstrably unrelated to any claim it lists, or a data item whose stated
>   access tier is directly contradicted elsewhere in the same input text. Do not use `fabricated` for
>   ordinary absence or an unrelated-but-honest item; use `absent` or `unlinked_present` for those.
> - Do not mark `linked`/`linked_no_anchor` on topical similarity alone — require the object's `claims`
>   or `mentions_dataset_or_method` snippet to overlap with the matched item's stated
>   `claims_supported`/content, in addition to the anchor rule above.

**Deterministic scoring of the leg verdicts**, using the disclosure-quality distinction from §1.2:

```python
CODE_LEG = {"linked": 1.0, "linked_no_anchor": 0.85, "toolchain_named": 0.75, "unlinked_present": 0.6, "fabricated": 0.0}
DATA_LEG = {"linked": 1.0, "linked_no_anchor": 0.85, "unlinked_present": 0.5, "fabricated": 0.0}

def resolved_leg_score(leg: str, match_kind: str, disclosure: dict, genre_exempt: bool) -> dict:
    """disclosure = the relevant *_availability_statement dict from Step 2.
    Returns {"score": float, "fabricated": bool} so the aggregator can distinguish an honest
    zero (silent absence) from a fabrication zero for reporting, even though both hard-cap
    the bundle identically under the harmonic-mean rule in §2.6."""
    if genre_exempt:
        return {"score": 1.0, "fabricated": False}  # structurally inapplicable, not a gap
    table = CODE_LEG if leg == "code_leg" else DATA_LEG
    if match_kind == "fabricated":
        return {"score": 0.0, "fabricated": True}
    if match_kind in table:
        return {"score": table[match_kind], "fabricated": False}
    # match_kind == "absent": grade by disclosure quality, per the hard constraint
    # (unavailability is itself an input; never scored as N/A)
    if disclosure.get("present") and disclosure.get("verbatim"):
        # specific, reasoned disclosure (e.g. che26's "no code released... would duplicate X")
        return {"score": 0.3, "fabricated": False}
    if disclosure.get("present"):
        # vague boilerplate ("available upon request", no tier/reason)
        return {"score": 0.15, "fabricated": False}
    return {"score": 0.0, "fabricated": False}  # silent absence — worst tier
```

`genre_exempt` is set to `True` for the **data leg only** (code can always in principle be produced
for empirical work; a *data* leg is only structurally inapplicable for genuinely non-empirical work)
and only when `genre_statement` from Step 2 is non-null AND independently corroborated by the object
having no `mentions_dataset_or_method` snippet and no numeric content. Never set from directory
absence alone.

### 2.6 Step 4 — Per-object bundle score (soft-min via harmonic mean, cycle 2)

```python
def object_bundle_score(evidence_score: float, code_score: float, data_score: float) -> dict:
    """Soft-min weakest-link: heavily punishes the weakest leg (harmonic mean is dominated by the
    smallest input) without strict min()'s brittleness of collapsing all "has one bad leg" cases to
    an identical score. A leg at exactly 0.0 (silent absence, structural failure, or fabrication)
    still hard-caps the whole bundle at 0.0 — the brief's penalize-don't-skip floor and exp3's
    fabrication-caps-the-bundle behavior are both preserved exactly, not softened."""
    scores = [evidence_score, code_score, data_score]
    if any(s <= 0.0 for s in scores):
        return {"bundle": 0.0, "hard_zero": True}
    n = len(scores)
    harmonic = n / sum(1.0 / s for s in scores)
    return {"bundle": round(harmonic, 4), "hard_zero": False}
```

### 2.7 Step 5 — ARA-level aggregation

```python
def compute_m48(evidence_json: dict, links_json: list[dict], claims_weight_floor: int = 1) -> dict:
    objects = {o["id"]: o for o in evidence_json["objects"]}
    per_object = []
    for link in links_json:
        obj = objects[link["id"]]
        e_result = evidence_leg_result(obj)
        c_result = resolved_leg_score("code_leg", link["code_leg"], disclosure=code_availability_statement,
                                       genre_exempt=False)
        d_result = resolved_leg_score("data_leg", link["data_leg"], disclosure=data_availability_statement,
                                       genre_exempt=is_genre_exempt(obj, genre_statement))
        bundle_result = object_bundle_score(e_result["score"], c_result["score"], d_result["score"])
        weight = claims_weight_floor + len(obj.get("claims", []))
        per_object.append({
            "id": obj["id"], "evidence": e_result["score"], "code": c_result["score"], "data": d_result["score"],
            "bundle": bundle_result["bundle"], "weight": weight,
            "fabricated": e_result["fabricated"] or c_result["fabricated"] or d_result["fabricated"],
        })

    # Unfiled/undisclosed source objects count as zero-bundle entries at baseline weight —
    # this is what makes evidence-layer completeness itself part of M48, per the hard constraint
    # that availability of the underlying artifact/field is part of the score, not a precondition for it.
    for unfiled in evidence_json["unfiled_objects"]:
        score = 0.3 if unfiled.get("reason_given") else 0.0
        per_object.append({"id": unfiled["ref"], "evidence": score, "code": 0.0, "data": 0.0,
                            "bundle": 0.0 if score == 0.0 else score, "weight": claims_weight_floor,
                            "fabricated": False})

    if not per_object:
        # No numbered objects at all, and none claimed to exist: this is the paywalled/
        # abstract-only floor case. Score is not skipped — it is the minimum, because the ARA
        # cannot support end-to-end replication of anything.
        return {"m48_score": 0.0, "per_object": [], "note": "no evidence objects filed or claimed"}

    total_weight = sum(o["weight"] for o in per_object)
    score = sum(o["bundle"] * o["weight"] for o in per_object) / total_weight
    fabrication_flags = [o["id"] for o in per_object if o["fabricated"]]
    return {"m48_score": round(score, 4), "per_object": per_object, "fabrication_flags": fabrication_flags}
```

Note: an unfiled object with `reason_given` still uses its disclosure score directly as the bundle
(no code/data legs exist to average against for an object that was never filed), which is why it is not
routed through `object_bundle_score` — there is nothing to take a harmonic mean *of* when the evidence
leg itself is the entire available signal for that entry.

`is_genre_exempt(obj, genre_statement)` implements the corroboration rule from §2.5:

```python
def is_genre_exempt(obj: dict, genre_statement: str | None) -> bool:
    if not genre_statement:
        return False
    non_empirical_kinds = {"diagram", "qualitative_sample"}
    return obj["type"] in non_empirical_kinds and not obj.get("mentions_dataset_or_method")
```

Final metric value is `m48_score` in [0, 1], plus a `fabrication_flags` list surfaced alongside the
score so a reviewer can see *why* a bundle hit its hard-zero floor (fabrication vs. ordinary silent
absence), even though both are scored identically. No branch of this pipeline returns `None`/`N/A`: an
ARA with no `evidence/` directory at all produces `evidence_json["objects"] == []` and
`unfiled_objects == []` only if `source_numbered_objects` is also `{0,0}` (genuinely no numbered
objects existed in the source, itself a rare and checkable claim); any other empty-evidence case where
the source plainly has tables/figures but none were filed and none accounted for falls into the
`unfiled_objects` path with `reason_given: null`, scoring `0.0` per object, not abstaining.

## 3. Why hard to Goodhart, and composition (summary)

Hardness comes from four compounding requirements that can't be satisfied by padding any single
layer: (1) linking is **per-object and semantic, and (cycle 2) anchor-gated** — the matched code/data
item's stated purpose must overlap the evidence object's caption/claims *and* share an independently
checkable numeric/named value; generic "we have a GitHub repo" statements, or plausible-sounding but
anchor-free matches, no longer clear full `linked` credit, and an anchor that actively contradicts the
object is refused outright; (2) the **soft-min (harmonic-mean) aggregation with a hard zero floor**
means an ARA can't average away one badly-unreproducible headline figure by having many fully-linked
minor ones — a true zero (silent absence, structural failure, fabrication) still caps the whole bundle
exactly as strict `min()` would, while non-zero-but-weak legs are graded more informatively than
`min()` allowed, and claims-weighting further prevents diluting a heavily-cited result with padding;
(3) **disclosure-quality grading is separate from mere absence**, so vague boilerplate ("data available
upon request") is explicitly scored below a specific, reasoned absence statement — closing the cheapest
gaming route (writing something that sounds like disclosure without committing to a checkable claim);
(4) **fabrication is a distinct, hard-capping tier** (cycle 2) rather than a soft discount, on both the
evidence leg (Critical Rule #11: a diagram/qualitative object smuggling in a numeric table) and the
code/data legs (a positive, stated contradiction between an item's claimed grounding and its content),
so an ARA cannot buy back a fabrication with strength elsewhere in the bundle. The genre-exemption path
remains the one deliberate escape valve, gated on an explicit quoted statement plus independent
corroboration from the object's own content, specifically to prevent "we just didn't write a data
section" from masquerading as "this is theory work."

Composition: M48 sits in the trust/rigor tier of the suite alongside D6 (which it strictly refines) and
any FAIR/data-access or evidence-completeness metrics (which it depends on as input signals but is not
redundant with, since it adds the code/data cross-reference those metrics don't check). Per §1.7, it
also deliberately keeps its evidence-leg scoring coarse and gate-like rather than a fine-grained
fidelity grade, to avoid duplicating a dedicated transcription-fidelity metric elsewhere in the suite.
It says nothing about claim correctness, novelty, or scientific importance — only about whether an
outside agent could, in principle, verify the specific numbers the paper reports using only what this
ARA captured.
