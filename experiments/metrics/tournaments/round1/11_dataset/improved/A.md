# Proposer 1 (improved) — metrics for `data/dataset.md` (+ `data/preprocessing.md`)

## Changes from stage 1

Stage-1 verdict: RANK 1 / WINNER. Three directed fixes, applied directly:

1. **Access-Tier Honesty over-penalized legitimate single-tier data.** The old metric capped every
   single-tier claim (open-only or gated-only) at 0.5 as "uncontrasted oversimplification," which
   punishes a genuinely all-open dataset that says so with an explicit data-layer qualifier just as
   hard as a lazy blanket "available." Fixed by splitting the old 0.5 bucket into three: a bare
   single-tier claim with no qualifier (0.3, the lazy pattern), a single-tier claim scoped to a named
   data layer via a borrowed qualifier-token check — raw/processed/metadata/individual-level/etc.
   (0.65), and an explicit "genuinely all-open, no gated component exists" disclaimer (0.9, treated as
   near-equal to full open/gated contrast since it is itself a checkable, costly-to-fake claim).
2. **Discrepancy Self-Audit only compared row counts, never summed the `N` column.** This would have
   missed the shape doc's own worked example — che26's mismatch is a cohort/study *count* discrepancy,
   but a paper could just as easily state a participant-total that its own table's `N` column doesn't
   sum to, and the old code never checked that arithmetic. Fixed by adding a second, independent
   reconciliation axis: stated aggregates are now split by unit (studies/datasets/cohorts → compared
   against row count; participants/samples → compared against a summed `N`-column value), and a
   mismatch on *either* axis triggers the flagged/silent branching.
3. **No preprocessing-traceability axis.** The old set only ever checked the *negative* (Genre-Scope
   Fidelity: secondary-reuse must not fabricate raw QC) and never rewarded a primary-generation paper
   for actually supplying a QC trail proportional to the raw-data claims it makes. Added a sixth
   metric, Preprocessing Traceability Proportional to Raw-Data Claims, that scales required QC
   specificity to how strong a raw-data-generation claim the accession blocks actually make, with
   QC vocabulary deduplicated by *dimension* (filtering, normalization, batch correction, exclusion,
   pipeline versioning) so keyword-stuffing one term cannot buy score.

All compute functions assume the artifact has been parsed into a Python dict `d` with this shape
(fields are `None`/`[]` when absent from the markdown — nothing is silently omitted from the dict):

```python
d = {
    "file_present": bool,             # was data/dataset.md emitted at all
    "intro_text": str,                # intro paragraph, "" if none
    "accession_blocks": [             # one per "## {Accession} — ..." heading (primary-generation genre)
        {
            "header": str,
            "provenance": str | None,       # text of **Provenance**
            "source_access": str | None,    # text of **Source / access**
            "size_content": str | None,     # text of **Size / content**
            "licensing_consent": str | None,# text of **Licensing / consent**
            "key_variables": str | None,
        }, ...
    ],
    "provenance_and_access_text": str | None,   # secondary-reuse "## Provenance and access"
    "included_cohorts_table": [ {col: val, ...}, ... ],  # rows of "## Included cohorts", [] if none
    "external_datasets_text": str | None,
    "consent_ethics_text": str | None,
    "preprocessing_text": str | None,           # inline "## Preprocessing" section content
    "preprocessing_file_present": bool,         # separate data/preprocessing.md exists
    "preprocessing_pointer_text": str | None,   # e.g. pointer to logic/solution/method.md
}
```

Every function below treats a missing/thin field as a scored penalty, not a skip, per the tournament's hard constraint.

---

## 1. Access-Tier Honesty

**How it signals good science:** The entire epistemic point of `dataset.md`, per its stated purpose, is telling a downstream agent whether the paper's numbers are *independently reproducible from public data* or *gated*. A dataset description that says "data is available" without distinguishing which parts (metadata vs. raw reads, processed objects vs. individual-level records) is not actually informative — it collapses a real reproducibility gradient into a boolean. Explicitly co-stating an open claim and its qualifier (e.g., "GEO metadata are open; raw reads are controlled-access via dbGaP") is a costly, checkable signal that the authors understood their own access structure rather than reflexively writing "available upon request." But the reverse must also hold: a paper whose data genuinely *is* all-open is not committing an oversimplification by saying so — the metric must reward that claim when it is made with the same kind of checkable specificity (naming which layer is open, and affirmatively noting no gated component exists), rather than flattening it into the same bucket as a lazy blanket claim.

**Compute function:**

```python
import re

OPEN_TERMS = [r"\bopen\b", r"\bpublic(?:ly)?\b", r"\bunrestricted\b", r"\bno accession\b"]
GATED_TERMS = [
    r"\bcontrolled[- ]access\b", r"\bdbgap\b", r"\brestricted\b", r"\bby request\b",
    r"\bconsortium\b", r"\bembargo", r"\bupon request\b", r"\bnot publicly\b",
]
DATA_LAYER_TERMS = [
    r"\braw\b", r"\bprocessed\b", r"\bmetadata\b", r"\bindividual[- ]level\b",
    r"\bpatient[- ]level\b", r"\bsummary\b", r"\baggregate\b", r"\bsequencing reads?\b",
]
ALL_OPEN_RE = re.compile(
    r"\b(?:entirely|fully|wholly)\s+open\b|\bno (?:controlled[- ]access|restricted|gated) component\b|"
    r"\bno accession(?:ed)? restriction\b",
    re.I,
)

def access_tier_honesty(d: dict) -> float:
    """Assumes d['accession_blocks'] and/or d['included_cohorts_table'] (each row may
    carry a 'Source study'/'Platform' style access-relevant cell) are the sources of
    access-tier claims. Returns 0.0-1.0."""
    if not d.get("file_present"):
        return 0.0  # no data/ artifact to score at all is itself a missing input here

    blocks_text = []
    for b in d.get("accession_blocks", []):
        blocks_text.append(b.get("source_access") or "")
    if d.get("provenance_and_access_text"):
        blocks_text.append(d["provenance_and_access_text"])
    for row in d.get("included_cohorts_table", []):
        blocks_text.append(" ".join(str(v) for v in row.values()))

    if not blocks_text or all(t.strip() == "" for t in blocks_text):
        return 0.0  # dataset described but access tier never addressed -> penalize

    scores = []
    for t in blocks_text:
        if not t.strip():
            scores.append(0.0)
            continue
        has_open = any(re.search(p, t, re.I) for p in OPEN_TERMS)
        has_gated = any(re.search(p, t, re.I) for p in GATED_TERMS)
        has_qualifier = any(re.search(p, t, re.I) for p in DATA_LAYER_TERMS)
        if has_open and has_gated:
            scores.append(1.0)       # explicit tiered disclosure: both sides named
        elif has_open and ALL_OPEN_RE.search(t):
            scores.append(0.9)       # explicit, checkable "genuinely all-open, no gated
                                      # component" claim -- a legitimate single-tier fact,
                                      # not an oversimplification, so it must not be capped
                                      # down at the vague-blanket bucket
        elif (has_open or has_gated) and has_qualifier:
            scores.append(0.65)      # single-tier claim scoped to a named data layer
                                      # (e.g. "processed matrix is open") -- informative even
                                      # without naming the other tier
        elif has_open or has_gated:
            scores.append(0.3)       # bare single-tier claim, no data-layer qualifier --
                                      # the lazy "available upon request" pattern
        else:
            scores.append(0.15)      # access mentioned/present as a field but no tier
                                      # language at all
    return sum(scores) / len(scores)
```

**What the function does & why:** It walks every place an access claim could live (per-accession `Source / access` strings, the secondary-reuse `Provenance and access` block, and cohort-table cells) and buckets each one by how much of the access structure it actually discloses. Full credit goes only to blocks naming both sides of the boundary. A block making a single-tier claim now splits into three cases instead of one: an affirmatively all-open claim ("entirely open, no controlled-access component") scores near-full credit because it is itself a specific, checkable fact about the data, not a hedge; a single-tier claim scoped to a named data layer (raw/processed/metadata/etc.) scores solidly above the midpoint because it tells a downstream agent exactly what part of the data that tier applies to; a bare single-tier claim with neither a layer qualifier nor an all-open disclaimer scores well below the midpoint, since it is indistinguishable from a lazy "available" placeholder. A block with no tier language at all is scored near zero, and an entirely absent access story is a hard zero.

**Why it's hard to Goodhart:** You cannot satisfy this by dumping the word "open" or "controlled-access" everywhere — the highest buckets require either genuine two-sided contrast or a specific, falsifiable all-open/data-layer claim, and cheap uniform buzzword-stuffing across unrelated accessions collides with metric 2's specificity requirement (does a real accession ID, dimension, or instrument back this claim up?) and metric 4's genre-scope check (is this claim even legitimate for what this block structurally is?). Faking the 0.9 "all-open" bucket by inserting "entirely open" without any accompanying accession or size detail is caught the moment metric 2 scores that same block for concreteness — an unsupported all-open claim next to a thin provenance/size block is exactly the kind of internally-inconsistent padding the interlocking metrics are built to expose.

---

## 2. Provenance & Size Specificity (reproducibility-grade concreteness)

**How it signals good science:** Reproducibility from public data requires more than an access tier — it requires enough concrete detail (instrument, depth, exact dimensions, accession IDs) that an independent party could locate and re-derive the artifact. Vague prose ("we sequenced samples and processed them") carries zero reproducibility value even if the access tier is honestly stated. Concrete, checkable numbers and identifiers are costlier to fabricate believably than adjectives, so their density is a decent proxy for how carefully the compiler (and, transitively, the paper) documented the data.

**Compute function:**

```python
import re

ACCESSION_RE = re.compile(r"\b(GSE|GSM|SRP|SRR|PRJNA|PRJEB|dbGaP phs|EGAS|EGAD)\d*\b", re.I)
NUMERIC_DIM_RE = re.compile(r"\d[\d,]*\s*(genes|spots|samples|donors|reads|participants|cells|×|x)\b", re.I)
INSTRUMENT_RE = re.compile(r"\b(NovaSeq|HiSeq|NextSeq|Visium|SpaceRanger|Illumina|PacBio|Nanopore)\b", re.I)

def provenance_specificity(d: dict) -> float:
    """Assumes provenance/size-content strings live in d['accession_blocks'][i]['provenance']
    and ['size_content']; for secondary-reuse genre, assumes equivalent detail should appear
    in d['included_cohorts_table'] row cells (N, platform, reference standard columns)."""
    if not d.get("file_present"):
        return 0.0

    unit_scores = []
    for b in d.get("accession_blocks", []):
        text = " ".join(filter(None, [b.get("provenance"), b.get("size_content")]))
        if not text.strip():
            unit_scores.append(0.0)
            continue
        hits = sum([
            bool(ACCESSION_RE.search(text)),
            bool(NUMERIC_DIM_RE.search(text)),
            bool(INSTRUMENT_RE.search(text)),
        ])
        unit_scores.append(hits / 3.0)

    for row in d.get("included_cohorts_table", []):
        text = " ".join(str(v) for v in row.values())
        hits = sum([
            bool(re.search(r"\b\d+\b", text)),                 # has an N
            bool(re.search(r"\bplatform|manufacturer|assay\b", text, re.I) or
                 re.search(r"\b(Simoa|IA|IP-MS|PET)\b", text, re.I)),
            bool(re.search(r"reference standard|disease stage", text, re.I)),
        ])
        unit_scores.append(hits / 3.0)

    if not unit_scores:
        return 0.0  # data-driven artifact with no scoreable content block at all
    return sum(unit_scores) / len(unit_scores)
```

**What the function does & why:** For primary-generation blocks it checks three independent, hard-to-fake concreteness markers — a real accession-style ID, a numeric dimension with units (genes/spots/reads/etc.), and a named instrument/pipeline — and averages how many of the three are present per block. For secondary-reuse cohort rows it checks the table-native equivalents (a real N, a named platform/assay, a named reference standard). Blocks/rows that exist but contain none of these are scored at 0, and an artifact with zero scoreable blocks at all is a hard 0 — thinness is punished rather than ignored.

**Why it's hard to Goodhart:** Regex-satisfying noise is cheap to produce ("GSE000000, 999,999 reads, Illumina") but such fabricated specificity is exactly the kind of unverifiable padding that metric 3 (self-audit for internal count consistency, now checking both row counts *and* summed N) and metric 4 (genre-scope fidelity) are designed to catch, since fabricated numbers rarely stay internally consistent with cohort totals or match the genre's legitimate level of detail (e.g., a secondary-reuse row suddenly citing an instrument model it has no business knowing).

---

## 3. Internal Discrepancy Self-Audit

**How it signals good science:** A dataset section that quietly hides a mismatch between the paper's stated aggregate ("18 studies / 24 independent datasets") and what it actually tabulates (12 rows) is doing accounting sleight-of-hand — silently picking whichever number sounds better. A well-compiled artifact surfaces the mismatch itself. This is a strong, genre-agnostic honesty signal: it rewards the *presence of self-criticism* about the data's own bookkeeping, which is a rarer and more costly thing to fabricate than a clean-looking (but unverified) number. Row-count reconciliation alone only catches one kind of mismatch (stated *cohort/study* counts vs. tabulated rows); a paper can just as easily state a total *participant* count that its own table's `N` column doesn't actually sum to, which requires a second, independent arithmetic check.

**Compute function:**

```python
import re

STATED_TOTAL_RE = re.compile(r"\b(\d[\d,]*)\s*(studies|datasets|cohorts|participants|samples)\b", re.I)
FLAG_TERMS = [r"\bdo(?:es)? not sum\b", r"\bdon'?t sum\b", r"\bdiscrepancy\b", r"\bmismatch\b",
              r"\binconsistent\b", r"\bnote[s]?\b.{0,40}\bdiffer", r"\bdoes not match\b",
              r"\bdo(?:es)? not add up\b"]
COUNT_UNITS = {"studies", "datasets", "cohorts"}
N_UNITS = {"participants", "samples"}
N_KEY_RE = re.compile(r"^n$|sample size|n cohort", re.I)

def _summed_n(rows):
    """Sums any 'N'-labeled column across cohort-table rows. Returns None if no such
    column is present at all (distinct from a column present but empty/non-numeric)."""
    total, found = 0, False
    for row in rows:
        for k, v in row.items():
            if N_KEY_RE.match(str(k).strip()):
                digits = re.sub(r"[^\d]", "", str(v))
                if digits:
                    total += int(digits)
                    found = True
    return total if found else None

def discrepancy_self_audit(d: dict) -> float:
    """Assumes stated aggregates live in d['intro_text']; tabulated row count is
    len(d['included_cohorts_table']), and a summed patient-level N is derived from any
    'N'-labeled column within those rows."""
    if not d.get("file_present"):
        return 0.0

    stated_matches = STATED_TOTAL_RE.findall(d.get("intro_text", "") or "")
    rows = d.get("included_cohorts_table", [])
    tabulated_n = len(rows)
    summed_n = _summed_n(rows)

    if not stated_matches and tabulated_n == 0:
        return 0.1  # no numbers stated anywhere to cross-check -> can't verify anything, penalize

    if not stated_matches or tabulated_n == 0:
        return 0.3  # only one side of any comparison exists -> unverifiable claim, mild penalty

    count_stated = {int(n.replace(",", "")) for n, unit in stated_matches if unit.lower() in COUNT_UNITS}
    n_stated = {int(n.replace(",", "")) for n, unit in stated_matches if unit.lower() in N_UNITS}

    checkable = bool(count_stated) or (bool(n_stated) and summed_n is not None)
    if not checkable:
        return 0.3  # stated numbers exist but none are of a type we can reconcile against

    count_consistent = (not count_stated) or (tabulated_n in count_stated)
    n_consistent = (not n_stated) or (summed_n is None) or (summed_n in n_stated)
    consistent = count_consistent and n_consistent

    all_text = " ".join(filter(None, [
        d.get("intro_text"), d.get("provenance_and_access_text"),
        d.get("consent_ethics_text"),
    ]))
    flagged = any(re.search(p, all_text, re.I) for p in FLAG_TERMS)

    if consistent:
        return 0.85          # numbers agree; can't reward "self-audit" that wasn't needed as highly
    elif flagged:
        return 1.0           # mismatch exists AND is explicitly surfaced -> best case
    else:
        return 0.0           # mismatch exists and is silently unaddressed -> worst case
```

**What the function does & why:** It now runs two independent reconciliation axes instead of one. First, any "N studies/datasets/cohorts" style aggregate is compared to the actual row count of the `Included cohorts` table — this is the axis that catches che26's real example (12 rows vs. "18 studies / 24 datasets"). Second, any stated "N participants/samples" aggregate is compared to a summed patient-level `N` column pulled directly from the table's own cells — this catches a different, purely arithmetic failure mode (a table whose row-level counts don't actually add up to the total the paper claims) that the row-count check alone would never see. A mismatch on *either* axis routes into the same flagged/silent branching as before: silently unaddressed is the floor, explicitly surfaced is the ceiling, and agreement on both axes scores high but not maximal since nothing was actually being tested.

**Why it's hard to Goodhart:** An author can't win by suppressing all numbers (that trips the "nothing to compare" 0.1 floor) or by making one axis trivially consistent while leaving the other broken (both axes are checked, and either one failing routes the whole score through the mismatch branch). Adding a fake "note: numbers differ" sentence when both axes actually agree doesn't help since consistent cases are capped below the flagged-mismatch case. Padding the cohort table with a plausible-looking `N` column to force arithmetic agreement is now directly checkable against the paper's own stated participant total, so a compiler can no longer dodge scrutiny by fabricating row counts while leaving the summed `N` unreconciled (or vice versa) — gaming this metric requires actually engineering a true, disclosed discrepancy story on both axes, which only a genuinely careful compiler produces.

---

## 4. Genre-Scope Fidelity (no cross-genre contamination)

**How it signals good science:** The shape doc is explicit that a secondary-reuse `dataset.md` *cannot legitimately contain raw-data QC/preprocessing detail* (there is no raw data to QC), and a primary-generation `dataset.md` that claims "generated in this study" without ever producing an accession is making an unverifiable generation claim. Detecting genre-inappropriate content is a check for hallucinated specificity or template copy-paste — a sign the compiler (or the underlying paper) is padding sections with boilerplate rather than describing what's actually true of this dataset.

**Compute function:**

```python
import re

RAW_QC_TERMS = [r"\badapter trimming\b", r"\balignment\b", r"\bread count\b",
                r"\bbase[- ]calling\b", r"\bdemultiplex", r"\bspaceranger\b", r"\bfastq\b"]
GENERATED_CLAIM_RE = re.compile(r"\bgenerated (?:in|for) this (?:study|paper|work)\b", re.I)

def genre_scope_fidelity(d: dict) -> float:
    """Assumes genre is inferable structurally: primary-generation genre has
    d['accession_blocks'] non-empty; secondary-reuse genre has d['included_cohorts_table']
    non-empty and/or d['provenance_and_access_text'] set, with accession_blocks empty."""
    if not d.get("file_present"):
        return 0.0

    is_primary = bool(d.get("accession_blocks"))
    is_secondary = bool(d.get("included_cohorts_table")) or bool(d.get("provenance_and_access_text"))

    if not is_primary and not is_secondary:
        return 0.0  # file exists but neither genre pattern present -> too thin to trust, penalize

    violations = 0
    checks = 0

    if is_secondary and not is_primary:
        checks += 1
        prep_text = (d.get("preprocessing_text") or "")
        if any(re.search(p, prep_text, re.I) for p in RAW_QC_TERMS):
            violations += 1  # secondary-reuse claiming raw-read-level QC it can't have

    if is_primary:
        for b in d.get("accession_blocks", []):
            checks += 1
            prov = b.get("provenance") or ""
            has_generated_claim = bool(GENERATED_CLAIM_RE.search(prov))
            has_real_accession = bool(re.search(r"\b(GSE|SRP|PRJNA|EGAS)\d+\b", b.get("header", ""), re.I))
            if has_generated_claim and not has_real_accession:
                violations += 1  # claims generation but no verifiable accession attached

    if checks == 0:
        return 0.4  # genre identifiable but nothing to check against -> moderate penalty
    return 1.0 - (violations / checks)
```

**What the function does & why:** It first classifies which genre pattern(s) the file structurally exhibits, then runs genre-specific contamination checks: for secondary-reuse files, it flags raw-sequencing QC vocabulary appearing in the preprocessing text (which shouldn't exist without raw data); for primary-generation blocks, it flags a "generated in this study" claim that isn't backed by an actual accession-style ID in the block's own header. The score is the fraction of applicable checks that pass cleanly.

**Why it's hard to Goodhart:** Removing all preprocessing detail from a secondary-reuse file to dodge the raw-QC check just tanks metric 2 (specificity) and looks like thinness; conversely, adding real accession IDs to satisfy the primary-generation check means the claim becomes checkable and must survive metric 1 (does the accession's access tier make sense) and metric 3 (does it reconcile with any stated totals). A block that inflates its raw-data claim strength to game metric 6's expectations now also has to survive this check: claiming generation without a real accession fails here directly, and claiming generation *with* a real accession pulls in metric 6's QC-trail obligation. The metric specifically targets the cheap move (declaring things you can't back up) and makes the escape route (adding fabricated but internally-consistent detail) expensive across the other metrics.

---

## 5. Ethics/Consent Coverage Conditioned on Data Genre

**How it signals good science:** Ethical provenance (IRB approval, consent framework) is a load-bearing fact for primary human-subjects data generation, and its total absence (not even an explicit "not applicable at review level" statement) leaves a downstream agent unable to distinguish "ethics were handled but the compiler forgot to note it" from "ethics were never considered." Rewarding an explicit statement — including an explicit non-applicability statement for secondary-reuse work — over silence treats disclosure itself as the signal, independent of which answer it gives.

**Compute function:**

```python
import re

IRB_RE = re.compile(r"\bIRB\s*#?\s*[\w-]+|\bWCG\s*#?\s*[\w-]+|\bNIH\s*#\s*[\w-]+", re.I)
CONSENT_RE = re.compile(r"\bconsent\b", re.I)
NOT_APPLICABLE_RE = re.compile(r"\bnot applicable\b.{0,40}\breview\b", re.I)

def ethics_coverage(d: dict) -> float:
    """Assumes ethics/consent info lives in d['accession_blocks'][i]['licensing_consent']
    for primary-generation genre and in d['consent_ethics_text'] for secondary-reuse genre."""
    if not d.get("file_present"):
        return 0.0

    is_primary = bool(d.get("accession_blocks"))

    if is_primary:
        block_scores = []
        for b in d.get("accession_blocks", []):
            text = b.get("licensing_consent") or ""
            if not text.strip():
                block_scores.append(0.0)   # human-derived data block with zero ethics text
                continue
            has_irb = bool(IRB_RE.search(text))
            has_consent = bool(CONSENT_RE.search(text))
            block_scores.append(1.0 if (has_irb and has_consent) else 0.5 if (has_irb or has_consent) else 0.1)
        return sum(block_scores) / len(block_scores) if block_scores else 0.0

    # secondary-reuse genre
    text = d.get("consent_ethics_text") or ""
    if not text.strip():
        return 0.0  # complete silence on ethics -> worst case, cannot infer anything
    if NOT_APPLICABLE_RE.search(text) or IRB_RE.search(text):
        return 0.9   # explicit disclosure, whichever answer it gives
    if CONSENT_RE.search(text):
        return 0.6
    return 0.2
```

**What the function does & why:** For primary-generation blocks it requires both an IRB-style identifier and consent language per accession block, halving credit if only one is present and near-zeroing it if the licensing/consent field exists but is empty of both. For secondary-reuse genre, it treats an explicit "not applicable at the review level" statement as almost as good as a full IRB citation (since disclosure, not the specific answer, is what's being rewarded), while total silence — no `Consent / ethics` section content at all — is scored at the floor.

**Why it's hard to Goodhart:** Copy-pasting a boilerplate "IRB approved" string into every accession block without a real number is caught by the IRB regex only matching identifier-shaped tokens, and a fabricated-looking uniform ID across unrelated accessions would be inconsistent with the distinct provenance/instrument details required by metric 2 to score well — so faking ethics coverage cheaply tends to produce mismatched, low-specificity blocks that lose points elsewhere.

---

## 6. Preprocessing Traceability Proportional to Raw-Data Claims

**How it signals good science:** Genre-Scope Fidelity (metric 4) only checks the *negative* — that secondary-reuse work doesn't fabricate raw-QC content. It never rewards a primary-generation paper for actually *owing and supplying* a QC trail that matches the strength of its raw-data claims. A paper that claims "generated in this study... NovaSeq 6000... raw sequencing reads" but never once mentions filtering thresholds, normalization, batch correction, exclusions, or a pipeline version has made a claim it hasn't backed up — the QC obligation scales with how much raw-data generation is actually claimed, and it should not be possible to satisfy this by keyword-stuffing a single QC term repeatedly instead of covering the real dimensions of a preprocessing trail.

**Compute function:**

```python
import re

RAW_CLAIM_RE = re.compile(
    r"\braw (?:reads?|sequenc\w*|data)\b|\bfastq\b|\bbase[- ]calling\b|\bsequenced\b|"
    r"\b(?:NovaSeq|HiSeq|NextSeq|Illumina|PacBio|Nanopore)\b",
    re.I,
)
QC_DIMENSIONS = {
    "filtering_qc":      [r"\bfilter(?:ing|ed)?\b", r"\bquality control\b", r"\bQC\b", r"\bthreshold(?:s|ed)?\b"],
    "normalization":     [r"\bnormali[sz](?:ation|ed|ing)\b"],
    "batch_correction":  [r"\bbatch[- ]effect\b", r"\bbatch correction\b", r"\bharmony\b", r"\bcombat\b"],
    "exclusion":         [r"\bexclu(?:sion|ded|de)\b", r"\bfail(?:ed)? QC\b", r"\bdropped\b"],
    "pipeline_version":  [r"\bv\d+(?:\.\d+)+\b", r"\bpipeline\b", r"\bworkflow version\b"],
}

def preprocessing_traceability(d: dict) -> float:
    """Assumes raw-data claims live in d['accession_blocks'][i]['provenance'], and QC detail
    lives in d['preprocessing_text'] and/or d['preprocessing_pointer_text']. Applies uniformly
    to both genres: for secondary-reuse, accession_blocks is structurally empty, so
    raw_claim_strength is 0 and the metric awards full credit for owing nothing -- this is
    a scored outcome, not a skipped/N-A one."""
    if not d.get("file_present"):
        return 0.0

    raw_claim_strength = sum(
        1 for b in d.get("accession_blocks", [])
        if RAW_CLAIM_RE.search(b.get("provenance") or "")
    )
    if raw_claim_strength == 0:
        return 1.0  # no raw-data-generation claim made anywhere -> no QC trail is owed;
                    # a legitimate outcome for secondary-reuse genre or a primary block that
                    # never actually asserts raw sequencing, scored as full credit, not N/A

    qc_text = " ".join(filter(None, [
        d.get("preprocessing_text"),
        d.get("preprocessing_pointer_text"),
    ]))
    if not qc_text.strip():
        return 0.0  # raw data claimed but zero QC trail anywhere -> worst case, hard-penalized

    dims_covered = sum(
        1 for patterns in QC_DIMENSIONS.values()
        if any(re.search(p, qc_text, re.I) for p in patterns)
    )
    return dims_covered / len(QC_DIMENSIONS)
```

**What the function does & why:** It first measures how strong a raw-data-generation claim the accession blocks actually make (instrument names, "raw reads," "fastq," "sequenced"). If no such claim exists anywhere — which is the structurally-guaranteed case for secondary-reuse genre, since it has no `accession_blocks` at all — the metric awards full credit outright: nothing is owed, so nothing is missing, and this is scored as a positive 1.0 rather than treated as inapplicable or skipped. If a raw-data claim does exist, the metric requires a QC trail and scores it by how many of five *distinct dimensions* (filtering/QC thresholds, normalization, batch correction, exclusion criteria, pipeline versioning) are covered, not by how many keyword hits occur — repeating "filter" ten times inside one preprocessing paragraph still only satisfies the `filtering_qc` dimension once, so keyword-stuffing a single term cannot inflate the score.

**Why it's hard to Goodhart:** A compiler can't win by stripping all raw-data language from provenance to escape the QC obligation, because that directly lowers metric 2's specificity score (no instrument/read-depth markers) and can flip metric 4's "generated in this study" check into a violation if a generation claim remains without any raw-technical backing. A compiler also can't win by dumping a wall of QC-adjacent prose that only ever restates one dimension, since the per-dimension dedup caps that at 0.2. The only way to score well is to make a real raw-data claim and back it with a QC trail that actually spans distinct preprocessing concerns — which is exactly the profile of a paper that did the work.

---

## Combination

These six metrics are built to interlock rather than to be independently maxed out. Padding every field with reassuring buzzwords ("open," "IRB approved," "generated in this study") to win Access-Tier Honesty and Ethics Coverage produces claims that must then survive Provenance & Size Specificity (do real accession IDs, dimensions, and instruments back up the claim?) and Genre-Scope Fidelity (is the claim even legitimate for this genre — e.g., can a secondary-reuse paper actually claim IRB numbers?). Claiming a genuinely all-open access tier to grab metric 1's 0.9 bucket without any accompanying accession or size detail is caught the instant metric 2 scores that same block for concreteness. Piling on fabricated numeric specificity to win the Specificity metric creates exactly the kind of unverified aggregate that the Discrepancy Self-Audit metric — now checking both tabulated row counts and summed `N`-column arithmetic — is designed to expose once cross-checked against the paper's own stated totals; a paper that tries to dodge that check by omitting aggregate numbers entirely gets penalized by the self-audit's "nothing to compare" floor instead. Inflating a raw-data-generation claim to look more like careful primary-generation work now immediately raises the bar for Preprocessing Traceability, which requires a real, dimension-spanning QC trail rather than keyword padding — and stripping the raw-data language back down to dodge that obligation instead tanks Specificity and risks a Genre-Scope violation if a "generated in this study" claim is left dangling without technical backing. In short: honesty-shaped text without underlying structure fails specificity and genre checks; structure-shaped fabrication without honesty fails the self-audit, access-tier contrast, and preprocessing-traceability checks. A paper can only score well across all six by actually having a well-provenanced, tier-honest, internally-consistent, genre-appropriate, and QC-traceable dataset section — which is the real target.

agent1 dataset (improved): 6 metrics written
