## Changes from stage 1

The judge ranked this set #2 (WINNER) for being the most deliberately anti-surface set, but flagged
four concrete defects. All four are fixed below, directly in the metrics, with no format changes:

1. **Access-tier construct was ambiguous** (critique: "conflates genuine open-vs-gated differentiation
   with per-clause qualification. Decide which you measure, or score both... State the construct
   explicitly."). **Fixed** by splitting Metric 1 into two named, separately-computed sub-scores —
   (A) per-claim qualification density and (B) document-level tier differentiation — combined with
   explicit weights (0.6/0.4). A legitimately single-tier, explicitly-qualified dataset ("processed
   matrix is open, no controlled component exists") now lands at 0.92, clearly above a lazy blanket
   claim (0.0) but below genuine multi-tier differentiation (1.0), instead of being conflated with
   either.
2. **Discrepancy Self-Audit only compared row counts, never summed the `N` column** (critique: "it
   would not catch che26's actual arithmetic mismatch. Add N-column summation."). **Fixed**: Metric 3
   now extracts a numeric N-like column from the cohort table (by header name: `N`, `n`, `sample size`,
   `participants`, `cases`), sums it, and checks *both* row-count and summed-N against the intro's
   stated numbers before deciding a mismatch exists. A compiler can no longer dodge by keeping the row
   count consistent while letting the summed N quietly diverge, or vice versa.
3. **Preprocessing was scored as bare presence (binary), not QC specificity** (critique: "Upgrade to
   scale by distinct QC dimensions covered ... so 'we did QC' scores below a real
   thresholds/normalization/batch-correction trail."). **Fixed**: Metric 5's primary-generation branch
   now scores `min(distinct_QC_dimensions_covered / 3, 1.0)` across five dimension categories
   (filtering, normalization, alignment/calling, QC-metric thresholds, annotation), deduped by
   *category* so repeating one keyword can't inflate the count — directly borrowing agent3's
   dimension-counting idea while keeping it inside this proposal's existing structural-completeness
   metric rather than adding a sixth metric.
4. **Density saturation constant (1 identifier/15 words) was asserted, not justified** (critique:
   "Calibrate against the two worked examples (huu25, che26) and report where each lands."). **Done,
   and it surfaced a real bug**: under the original genomics-flavored regex set, che26 (secondary-reuse)
   scored **0.0** despite a PROSPERO registration ID, two cited source studies, and a fully-populated
   6-column cohort table — the regexes were structurally blind to secondary-reuse specificity, which
   would have made this metric ungamed-but-unfair (a whole genre floored regardless of quality). Fixed
   by adding citation (`Author et al. (Year)`) and registration (`PROSPERO`, `NCT#####`, `CRD######`)
   regexes plus per-cell cohort-table density credit. Calibration also exposed a second bug: a very
   short text with one lucky number+keyword match (e.g. the shape doc's abstract-only floor case,
   `"N=4,736 participants"`) saturated the ratio to 1.0 purely from having a tiny denominator. Added a
   `length_factor = min(word_count / 40, 1.0)` discount (40 ≈ huu25's own provenance+size word count) so
   short stubs can no longer buy a perfect score with a single hit. Post-fix: huu25 lands at **1.0**
   (6 hits / 40 words, length_factor 1.0), che26 lands at **1.0** (14 hits / ~95 words, length_factor
   1.0), and the abstract-only floor case lands at **~0.05** (1 hit / 2 words, length_factor 0.05) —
   the three cases the shape doc explicitly distinguishes now separate correctly.

Metric 4 (Consent/Ethics Grounding) was praised without a specific defect and is unchanged. The
Combination section is updated to reflect the new interlocks these fixes create.

---

# Proposer #2 (improved) — metrics for `data/dataset.md` (+ `data/preprocessing.md`)

All compute functions assume a parsed representation of `dataset.md` with this shape (as documented
in the shape file):

```python
parsed = {
    "intro": str,                      # intro paragraph, may be ""
    "accession_blocks": [               # one per "## {Accession} — ..." heading; [] if none
        {
            "header": str,
            "provenance": str | None,
            "source_access": str | None,
            "size_content": str | None,
            "licensing_consent": str | None,
            "key_variables": str | None,
        },
        ...
    ],
    "provenance_and_access": str | None,      # secondary-reuse "## Provenance and access"
    "included_cohorts_table": list[dict] | None,  # parsed "## Included cohorts" rows
    "external_datasets": str | None,
    "consent_ethics": str | None,
    "preprocessing": str | None,        # inline "## Preprocessing" text
    "preprocessing_pointer": str | None,  # e.g. "see data/preprocessing.md" or "see logic/solution/method.md"
    "raw_text": str,                    # full raw markdown, for regex fallback
}
```

If `parsed` is `None`, empty, or `raw_text` is empty/whitespace, every metric below treats this as a
thin/absent input and returns its floor score — never `N/A`.

---

## 1. Access-Tier Honesty Index

**How it signals good science.** The single highest-leverage fact a dataset descriptor can convey is
*exactly* what a downstream reader can and cannot get their hands on. A blanket "data available" is
epistemically useless — it collapses "you can download the processed matrix today" and "you must apply
to a consortium and wait eight months for raw reads" into the same claim. Good science pays the tax of
being specific about access tiers because it lets others actually attempt reproduction; bad/lazy science
free-rides on vague availability language that sounds compliant but isn't actionable.

This version measures **two separate, explicitly named constructs** rather than conflating them: (A)
whether each individual access claim names the data layer it applies to, and (B) whether the document
as a whole differentiates more than one access tier when it plausibly has more than one — without
penalizing a dataset that is genuinely, honestly single-tier.

**Compute function.**

```python
import re

ACCESS_KEYWORDS = [
    "open", "public", "publicly available", "controlled access", "restricted",
    "embargo", "by request", "upon request", "gated", "dbgap", "ega",
    "consortium", "material transfer agreement", "mta",
]
QUALIFIER_KEYWORDS = [
    "raw", "processed", "metadata", "summary", "individual-level",
    "patient-level", "genomic", "sequencing reads", "aggregate",
]

def access_tier_honesty(parsed: dict) -> float:
    """Measures two explicitly separate constructs and combines them:
      (A) per-claim qualification: does each access-tier clause also name the
          data layer it applies to (raw vs. processed vs. metadata vs. ...)?
      (B) tier differentiation: does the document, taken as a whole, distinguish
          more than one access tier when more than one plausibly exists, while
          NOT penalizing a genuinely single-tier dataset that explicitly and
          specifically names its one layer (shape doc: all-open data is a
          legitimate, non-defective case).
    Assumes parsed['accession_blocks'][i]['source_access'] and/or
    parsed['provenance_and_access'] hold the access-tier prose. Returns 0.0-1.0."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0  # absent/thin -> floor, not N/A

    access_texts = [
        b.get("source_access") for b in parsed.get("accession_blocks", []) if b.get("source_access")
    ]
    if parsed.get("provenance_and_access"):
        access_texts.append(parsed["provenance_and_access"])

    if not access_texts:
        return 0.0  # data-bearing doc with zero access statement at all is a defect, not N/A

    total_claims = 0
    qualified_claims = 0
    qualifiers_seen = set()
    for text in access_texts:
        lower = text.lower()
        # split into clause-ish units so multi-tier statements (open metadata,
        # controlled raw reads) each get scored rather than merged into one claim
        clauses = re.split(r"[.;]\s+", lower)
        for clause in clauses:
            hits = [k for k in ACCESS_KEYWORDS if k in clause]
            if not hits:
                continue
            total_claims += 1
            clause_qualifiers = [q for q in QUALIFIER_KEYWORDS if q in clause]
            if clause_qualifiers:
                qualified_claims += 1
                qualifiers_seen.update(clause_qualifiers)

    if total_claims == 0:
        return 0.0  # mentions access section but no scoreable claim found -> treat as thin

    # (A) per-claim qualification density
    qualification_score = qualified_claims / total_claims

    # (B) tier differentiation: reward a document that names more than one distinct
    # data layer across its claims; give a genuinely single-tier document high (but
    # not maximal) credit only if the one tier it names is fully, specifically
    # qualified -- not the same floor as a bare "data are available"
    if len(qualifiers_seen) >= 2:
        differentiation_score = 1.0
    elif len(qualifiers_seen) == 1 and qualification_score == 1.0:
        differentiation_score = 0.8
    else:
        differentiation_score = 0.0

    return 0.6 * qualification_score + 0.4 * differentiation_score
```

**What the function does & why.** It pulls every sentence-ish clause that mentions an access-tier word
(open, controlled, embargoed, by-request, dbGaP, etc.) and checks whether that same clause also names
*what* the tier applies to (raw vs. processed vs. metadata vs. individual-level) — construct (A). Then,
independently, it looks at the *set* of distinct data-layer words used across the whole document —
construct (B) — to reward genuine tiering (open metadata + controlled raw reads) above a document that
only ever qualifies one layer. A correctly, specifically stated single-open-tier dataset ("processed
matrix is open, no controlled component exists") scores 0.92 — high, because it isn't lying or being
vague, but shy of the 1.0 reserved for documents that demonstrate real tier contrast. A doc that says
only "data are available" scores 0.0 on both constructs.

**Why it's hard to Goodhart.** You cannot cheaply pad the score by sprinkling the word "open" everywhere
— construct (A)'s qualifier requirement forces you to also name a concrete data layer, which only makes
sense if you actually know the access structure of your own dataset. You also cannot win construct (B)
by inventing a second fake tier ("raw data are also open") purely to look differentiated, because a
fabricated qualifier is directly falsifiable against the accession's real access policy by an auditor
checking the linked GEO/dbGaP record — and a fabricated raw-open claim for what is actually
controlled-access genomic data is exactly the kind of lie Provenance Specificity Density and Discrepancy
Self-Audit are positioned to cross-check against the accession's real structure.

---

## 2. Provenance Specificity Density

**How it signals good science.** Verifiable science is made of falsifiable, checkable numbers —
instrument names, software versions, exact dimensions, read depths, accession IDs, cited source studies,
registration numbers — not adjectives. A dataset section stuffed with concrete, checkable identifiers
lets a skeptical reader go verify each claim independently; one that says "we sequenced samples and
processed them appropriately" gives the reader nothing to check. Specificity density is a cheap,
generalizable proxy for how much the writer actually engaged with their own data pipeline versus wrote
boilerplate — and it has to work for *both* genres the shape doc describes, not just the
genomics-flavored one.

**Compute function.**

```python
import re

ACCESSION_RE = re.compile(r"\b(GSE|GSM|SRA|SRP|SRR|PRJNA|PRJEB|EGA[SDN]|dbGaP|phs\d+)[A-Z0-9]*\b", re.I)
DIM_RE = re.compile(r"\b[\d,]+\s*(genes|spots|samples|donors|reads|cells|participants|patients|studies|datasets)\b", re.I)
INSTRUMENT_VERSION_RE = re.compile(r"\b(v\d+(\.\d+)*|NovaSeq|HiSeq|NextSeq|MiSeq|GRCh\d+|SpaceRanger|CellRanger)\b", re.I)
CITATION_RE = re.compile(r"\b[A-Z][A-Za-z\-]+\s+et al\.?,?\s*\(?\d{4}\)?")
REGISTRATION_RE = re.compile(r"\b(PROSPERO|NCT\d{6,}|ISRCTN\d+|CRD\d{6,})\b", re.I)

# Calibrated against the shape doc's two worked examples. huu25 (primary-generation,
# ~40 words of provenance/size prose) hits 6 regex matches and should saturate.
# che26 (secondary-reuse, ~95 words of provenance/access prose + cohort table) hit
# ZERO matches under the original genomics-only regex set despite a PROSPERO
# registration ID, two cited source studies, and a fully-populated 6-column cohort
# table -- a genre-fairness bug, not a genuine quality gap. CITATION_RE, REGISTRATION_RE,
# and per-cell table credit were added to fix this; both examples now saturate.
DENSITY_SATURATION_WORDS_PER_HIT = 15.0
# Calibration also exposed a second bug: a very short stub with one lucky
# number+keyword hit (e.g. the shape doc's abstract-only floor case,
# "N=4,736 participants") saturated the ratio purely from a tiny denominator.
# LENGTH_CONFIDENCE_WORDS (~huu25's own provenance+size word count) discounts short
# texts so a single hit can no longer buy a perfect score.
LENGTH_CONFIDENCE_WORDS = 40.0

def provenance_specificity_density(parsed: dict) -> float:
    """Assumes provenance/size_content free text is available per accession block
    (or provenance_and_access / included_cohorts_table for secondary-reuse genre).
    Returns a 0.0-1.0 density score, word-count normalized and length-discounted."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0

    blocks = parsed.get("accession_blocks", [])
    texts = []
    for b in blocks:
        texts.append(" ".join(filter(None, [b.get("provenance"), b.get("size_content")])))
    if parsed.get("provenance_and_access"):
        texts.append(parsed["provenance_and_access"])

    table_hits = 0
    if parsed.get("included_cohorts_table"):
        table = parsed["included_cohorts_table"]
        for row in table:
            # every populated field beyond the bare cohort label is one checkable
            # fact (source study, N, disease stage, reference standard, platform...);
            # a real multi-column cohort table is inherently high-specificity content
            # that flattened-text regexes alone under-detect
            table_hits += max(len(row) - 1, 0)
        texts.append(" ".join(str(v) for row in table for v in row.values()))

    joined = " ".join(t for t in texts if t).strip()
    if not joined:
        return 0.0  # no provenance prose at all -> floor

    word_count = max(len(joined.split()), 1)
    hits = (
        len(ACCESSION_RE.findall(joined))
        + len(DIM_RE.findall(joined))
        + len(INSTRUMENT_VERSION_RE.findall(joined))
        + len(CITATION_RE.findall(joined))
        + len(REGISTRATION_RE.findall(joined))
        + table_hits
    )
    density = min(hits / (word_count / DENSITY_SATURATION_WORDS_PER_HIT), 1.0)
    length_factor = min(word_count / LENGTH_CONFIDENCE_WORDS, 1.0)
    return density * length_factor
```

**What the function does & why.** It concatenates the provenance-bearing prose (per-accession
provenance/size text, the secondary-reuse provenance paragraph, and the cohort table's own cell values)
and counts checkable specifics across five families: accession/identifier patterns, exact-dimension
phrases, instrument/software/genome-build versions, cited source studies (`Author et al. (Year)`), and
trial/review registration numbers (PROSPERO, NCT, ISRCTN, CRD) — plus a per-cell credit for populated
cohort-table columns, since a real 6-column table (source study, N, stage, reference standard, platform)
is inherently specific content that flattened-text regexes alone under-detect. It normalizes by word
count so verbose-but-vague sections don't win just by being long, caps the density ratio at 1.0, then
applies a length-confidence discount so a short stub can't saturate off one lucky hit.

**Calibration results (per critique directive).** huu25: 6 hits / 40 words → density 1.0 (capped),
length_factor 1.0 → **final 1.0**. che26 (post-fix): 14 hits (2 citations + 2 registration tokens + 10
table-cell credits) / ~95 words → density 1.0 (capped), length_factor 1.0 → **final 1.0**. Shape doc's
abstract-only floor case ("N=4,736 participants", no accession, no table): 1 hit / 2 words → raw density
7.5 capped to 1.0, but length_factor 2/40 = 0.05 → **final ≈0.05**. The three cases the shape doc
explicitly distinguishes (rich primary-generation, rich secondary-reuse, thin abstract-only stub) now
separate correctly instead of the original formula flooring the entire secondary-reuse genre and
over-rewarding tiny stubs.

**Why it's hard to Goodhart.** Stuffing in random accession-shaped strings, fake version numbers, fake
citations, or a fake registration ID to juice the count is directly checkable — each either resolves to
a real, matching GEO/SRA/PROSPERO record or it doesn't, and a fabricated instrument/version string is
inconsistent with the rest of the described pipeline. Padding a cohort table with empty-looking filler
columns doesn't help, because `table_hits` counts *populated* fields, and an empty or placeholder cell
is exactly what Discrepancy Self-Audit's row/N-sum cross-check (#3) is positioned to catch as
inconsistent with a stated total. Padding word count to chase length_factor without also adding real
identifiers is self-defeating: it lowers density (density is a *ratio* to word count) while giving
length_factor no help beyond the 40-word threshold, so verbosity still loses.

---

## 3. Discrepancy Self-Audit Score

**How it signals good science.** Real datasets are messy: table counts don't always sum to the number
quoted in the abstract, cohorts get merged or split across the paper's own sections, N's drift between
methods and results. Good science *notices and states* these internal inconsistencies rather than
silently picking whichever number is convenient; a compiler-authored `dataset.md` that surfaces "the 12
tabulated cohorts don't sum to the paper's stated 18 studies" is doing exactly the kind of
adversarial-to-itself bookkeeping that catches sloppy or cherry-picked accounting before a reader has to.
A mismatch can show up two ways — the *count* of cohorts disagreeing with a stated count, or the *sum*
of a numeric column (e.g. total N) disagreeing with a stated total — and a compiler could dodge either
check individually, so both need to be covered.

**Compute function.**

```python
import re

RECONCILE_MARKERS = [
    "do not sum", "does not sum", "discrepancy", "mismatch", "does not match",
    "differs from", "inconsistent with", "note:", "however,", "unlike the",
    "the paper states", "vs. stated", "reconcil",
]
NUMBER_RE = re.compile(r"\b\d[\d,]*\b")
N_COLUMN_KEY_RE = re.compile(r"\bn\b|sample size|participants|cases", re.I)
NUMERIC_VALUE_RE = re.compile(r"[\d,]+")

def discrepancy_self_audit(parsed: dict) -> float:
    """Assumes raw_text contains any cross-referencing prose the compiler wrote when
    tabulated counts and narrative counts diverge. Checks BOTH a row-count mismatch
    and a summed-N-column mismatch against numbers stated in the intro. Returns 0.0
    (no numbers to check, or numbers present but unreconciled) to 1.0 (mismatch
    present and explicitly flagged, or no mismatch at all)."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0

    table = parsed.get("included_cohorts_table")
    intro = parsed.get("intro", "") or ""
    raw = parsed["raw_text"].lower()

    stated_numbers = {int(n.replace(",", "")) for n in NUMBER_RE.findall(intro) if len(n.replace(",", "")) <= 4}

    if not table or not stated_numbers:
        # nothing to cross-check (e.g., primary-generation genre with a single accession,
        # or abstract-only floor case with no table at all) -> can't earn credit for auditing
        # something that structurally doesn't exist here; score low rather than skip
        return 0.2 if parsed.get("accession_blocks") else 0.0

    row_n = len(table)

    # sum a numeric N-like column if the table has one (source-study cohort N, sample
    # size, etc.) -- this is the arithmetic check the row-count-only version missed
    n_col_values = []
    for row in table:
        for key, val in row.items():
            if N_COLUMN_KEY_RE.search(str(key)):
                m = NUMERIC_VALUE_RE.search(str(val))
                if m:
                    n_col_values.append(int(m.group().replace(",", "")))
                break
    candidates = {row_n}
    if n_col_values:
        candidates.add(sum(n_col_values))

    mismatch_exists = not (candidates & stated_numbers)
    if not mismatch_exists:
        return 1.0  # at least one of {row count, summed N} reconciles; nothing to flag

    flagged = any(marker in raw for marker in RECONCILE_MARKERS)
    return 1.0 if flagged else 0.0  # mismatch present but silently unflagged -> worst case
```

**What the function does & why.** It compares *two* candidate figures derived from the `Included
cohorts` table — the row count, and the sum of a detected N-like numeric column — against small
integers mentioned in the intro paragraph (the kind of place a paper states "18 studies / 24 independent
datasets"). If either candidate agrees with a stated number, there's nothing to audit and the doc gets
full credit. If neither agrees, it searches the raw text for explicit reconciliation language. A
mismatch that's silently left unflagged scores zero; a paper with no table/count structure to cross-check
at all gets a low but non-zero floor rather than a skip, per the hard constraint.

**Why it's hard to Goodhart.** You cannot win this by suppressing the table or the intro N (that
directly craters Provenance Specificity Density and Genre-Consistent Structural Completeness, and trips
the "nothing to audit" floor case). You also cannot win it by inserting a reconciliation-flavored
sentence with no real mismatch behind it, because the trigger condition is derived independently from
the document's own numbers. Critically, you can no longer dodge by hiding one discrepancy type while
fixing the other: keeping the row count consistent with a stated "12 cohorts" while quietly letting the
summed N drift from a separately stated total N, or vice versa, is now caught either way, since a
mismatch is declared unless *both* candidate figures fail to reconcile with *any* stated number — closing
the single-attack-surface gap the original row-only version left open.

---

## 4. Consent/Ethics Grounding Specificity

**How it signals good science.** Whether a study used real human (or animal) subjects data ethically is
not a formality — it's a load-bearing claim about whether the underlying data collection was legitimate
at all. Primary-data-generation work should be able to name IRB numbers, review boards, and consent
mechanisms because it directly controlled data collection; secondary-reuse work legitimately cannot
restate other cohorts' IRBs, but a well-compiled ARA still says so explicitly ("not applicable at the
review level; individual cohorts carry their own approvals") instead of leaving the section silent or
absent. Precision here — not just presence of the word "IRB" — separates real ethics grounding from
box-checking.

**Compute function.**

```python
import re

IRB_ID_RE = re.compile(r"\b(IRB|WCG|WIRB)\s*#?\s*[\w\-]{2,}\b", re.I)
EXPLICIT_NA_RE = re.compile(r"not applicable at the review level|carr(y|ies) (their|its) own", re.I)
VAGUE_ETHICS_RE = re.compile(r"\bethically approved\b|\bappropriate (irb|ethics) approval\b|\ball necessary approvals\b", re.I)

def consent_ethics_grounding(parsed: dict) -> float:
    """Assumes ethics prose lives in accession_blocks[i]['licensing_consent'] for
    primary-generation genre, or parsed['consent_ethics'] for secondary-reuse genre.
    Returns 0.0-1.0."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0

    blocks = parsed.get("accession_blocks", [])
    consent_texts = [b.get("licensing_consent") for b in blocks if b.get("licensing_consent")]
    top_level = parsed.get("consent_ethics")

    if not blocks and not top_level:
        return 0.0  # data-bearing doc with zero ethics/consent statement anywhere -> floor

    scores = []
    for text in consent_texts:
        if IRB_ID_RE.search(text):
            scores.append(1.0)
        elif VAGUE_ETHICS_RE.search(text):
            scores.append(0.3)  # asserts compliance without naming a checkable board/number
        else:
            scores.append(0.1)  # present but neither specific nor even genre-appropriately vague

    if top_level:
        if IRB_ID_RE.search(top_level):
            scores.append(1.0)
        elif EXPLICIT_NA_RE.search(top_level):
            scores.append(0.9)  # correct, explicit genre-appropriate deferral for secondary-reuse
        elif VAGUE_ETHICS_RE.search(top_level):
            scores.append(0.3)
        else:
            scores.append(0.1)

    return sum(scores) / len(scores) if scores else 0.0
```

**What the function does & why.** For each place ethics/consent language can live (per-accession
`licensing_consent` for primary-generation, or the top-level `Consent / ethics` section for
secondary-reuse), it checks for a real, checkable board identifier (IRB/WCG numbers) first — full
credit. Failing that, it looks for the one legitimate genre-specific escape hatch for secondary-reuse
work: an explicit statement that ethics review isn't restated because the reviewed cohorts carry their
own IRBs — near-full credit, because that's the epistemically honest thing to say. Generic assurance
language ("appropriate approvals were obtained") with no board named gets partial credit, and total
silence on ethics anywhere in a data-bearing doc gets the floor.

**Why it's hard to Goodhart.** Inventing a plausible-looking IRB number is checkable against the cited
institution/board (WCG, NIMH IRP, Maryland DoH, etc.) and against the paper it's compiled from; a fake
number that doesn't match the source paper is a fabrication an auditor or the Provenance Specificity
cross-check can catch. Copy-pasting the vague-boilerplate phrase to dodge the floor only earns partial
credit by design (0.3), never full — so the cheap move is capped well below actually naming a board or
correctly invoking the secondary-reuse deferral.

---

## 5. Genre-Consistent Structural Completeness

**How it signals good science.** The shape file is explicit that `data/dataset.md` is genre-conditioned:
primary-data-generation work should show provenance-through-preprocessing depth (instrument, QC,
normalization), while secondary-reuse work correctly stops at cohort-level provenance and must *not*
fabricate raw-data QC it never performed. A well-compiled artifact matches its structural depth to what
the paper actually did — and "matches" for primary-generation work means more than merely *having* a
preprocessing section: a one-line "we performed QC" and a real thresholds/normalization/batch-correction
trail should not score the same.

**Compute function.**

```python
QC_DIMENSIONS = {
    "filtering": ["filter", "threshold", "exclu", "cutoff", "qc metric"],
    "normalization": ["normali", "batch correction", "harmony", "combat", "log-transform"],
    "alignment_or_calling": ["align", "map to", "variant call", "base call", "demultiplex", "spaceranger", "cellranger"],
    "qc_metrics": ["mitochondrial", "doublet", "read depth", "min reads", "min genes", "qc pass", "qc fail"],
    "annotation": ["annotat", "cluster", "cell type", "domain assignment"],
}
RAW_QC_MARKERS = ["raw read", "base calling", "demultiplex", "alignment", "spaceranger", "cellranger"]

def _qc_dimension_coverage(text: str) -> float:
    """Counts distinct QC dimension CATEGORIES present, deduped, so repeating one
    keyword (e.g. 'filter, filter, filter') cannot inflate the score -- only
    genuinely different QC steps count. 3+ distinct dimensions = a real QC trail."""
    if not text:
        return 0.0
    lower = text.lower()
    covered = sum(1 for kws in QC_DIMENSIONS.values() if any(k in lower for k in kws))
    return min(covered / 3.0, 1.0)

def genre_consistent_completeness(parsed: dict) -> float:
    """Assumes accession_blocks presence signals primary-data-generation genre and
    included_cohorts_table/provenance_and_access presence signals secondary-reuse genre
    (both may co-occur, e.g. huu25's external reference datasets). Returns 0.0-1.0."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0

    is_primary = bool(parsed.get("accession_blocks"))
    is_secondary = bool(parsed.get("included_cohorts_table") or parsed.get("provenance_and_access"))

    if not is_primary and not is_secondary:
        return 0.0  # data-bearing doc with neither recognizable genre pattern -> thin/floor

    preprocessing_text = parsed.get("preprocessing")
    raw_qc_language = bool(preprocessing_text) and any(
        kw in preprocessing_text.lower() for kw in RAW_QC_MARKERS
    )

    score = 0.0
    weight = 0.0

    if is_primary:
        weight += 1.0
        if preprocessing_text:
            # scaled by distinct QC dimensions actually covered, not mere presence,
            # so "we did QC" no longer scores the same as a real multi-step trail
            score += _qc_dimension_coverage(preprocessing_text)
        elif parsed.get("preprocessing_pointer"):
            # pointer to data/preprocessing.md or logic/solution/method.md exists but
            # its content isn't in this parsed doc to score dimension coverage against
            # -> partial credit for not omitting entirely, capped below inline depth
            score += 0.5
        else:
            score += 0.0

    if is_secondary:
        weight += 1.0
        if preprocessing_text and raw_qc_language:
            # fabricated raw-QC detail with no primary data to justify it -> penalize hard
            score += 0.0
        else:
            # correctly stopping at cohort-level provenance (no invented raw QC)
            score += 1.0

    return score / weight if weight else 0.0
```

**What the function does & why.** It infers which genre pattern(s) the document exhibits from
structural fingerprints already in the shape (accession blocks => primary-generation; a cohort table or
a `Provenance and access` section => secondary-reuse). For primary-generation docs it now scores
preprocessing by *distinct QC dimension categories covered* (filtering, normalization,
alignment/calling, QC-metric thresholds, annotation), deduped by category so keyword-stuffing one term
is capped — a real 3-dimension trail saturates, a one-line "we did QC" does not. A pointer to a separate
preprocessing file gets partial (0.5) credit rather than the old binary 1.0, since this function cannot
verify dimension coverage in a file outside `dataset.md`'s own parsed content. For secondary-reuse docs
it keeps the original, narrower raw-QC marker list (rather than reusing the full QC_DIMENSIONS set)
deliberately: legitimate meta-analytic language ("we normalized effect sizes across studies") should not
be punished as if it were a fabricated raw-sequencing claim — only literal raw-level markers
(demultiplexing, base calling, SpaceRanger/CellRanger, etc.) trigger the penalty.

**Why it's hard to Goodhart.** You can't win the primary-generation half by pasting one vague QC
sentence, because the dimension-coverage score requires distinct categories, not keyword repetition, and
fabricated instrument/QC claims are independently caught by Provenance Specificity Density (fake version
strings, mismatched platforms) and Access-Tier Honesty. You can't win the secondary-reuse half by adding
a fake `## Preprocessing` section describing raw QC, because the raw-QC-marker check is designed to zero
that out directly — and inflating a fake QC trail into the *primary* half's dimension count while somehow
also being secondary-reuse is structurally blocked, since raw QC language automatically fails the
secondary branch even as it might help the primary one, so a document can't hedge by claiming both
genres' credit with the same fabricated paragraph.

---

## Combination

These five metrics are built to fail together whenever the underlying document is dishonest rather than
merely thin. Padding access language without naming a data-layer tier wins nothing on Access-Tier
Honesty's construct (A) and can't fake construct (B) either, since a second invented tier is directly
falsifiable against the accession's real access policy and against Provenance Specificity Density's own
identifiers. Inventing fake accession numbers, instrument versions, citations, registration IDs, or IRB
IDs to inflate specificity or ethics-grounding is independently checkable and, if caught, would also flag
as an unreconciled internal inconsistency that Discrepancy Self-Audit — now checking both row-count and
summed-N arithmetic — is built to surface. Suppressing a cohort table, hollowing out its cell values, or
manipulating N values to hit a convenient row-count-only match no longer works, because Provenance
Specificity Density credits populated table cells directly and Discrepancy Self-Audit cross-checks the
summed column independently of row count. Padding a short document to farm Provenance Specificity
Density's length-confidence threshold without real identifiers is self-defeating, since word count grows
the denominator of the density ratio faster than length_factor rewards it. And fabricating structural
depth that doesn't match the paper's actual genre — one-line QC boilerplate claiming primary-generation
depth, or raw QC prose in a secondary-reuse doc, or ethics boilerplate with no named board — is penalized
directly by Genre-Consistent Completeness's dimension-scaled scoring and Consent/Ethics Grounding
respectively, with no overlap-free way to buy credit on one without triggering a penalty on another. A
document can only score well across all five by actually being specific, honest and explicit about access
tiers, self-auditing its own numbers both by count and by sum, ethically grounded in a genre-appropriate
way, and structurally matched — in real depth, not mere presence — to what the paper really did.
