# Proposer #2 — metrics for `data/dataset.md` (+ `data/preprocessing.md`)

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
    """Assumes parsed['accession_blocks'][i]['source_access'] and/or
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
            has_qualifier = any(q in clause for q in QUALIFIER_KEYWORDS)
            if has_qualifier:
                qualified_claims += 1

    if total_claims == 0:
        return 0.0  # mentions access section but no scoreable claim found -> treat as thin
    return qualified_claims / total_claims
```

**What the function does & why.** It pulls every sentence-ish clause that mentions an access-tier word
(open, controlled, embargoed, by-request, dbGaP, etc.) and checks whether that same clause also names
*what* the tier applies to (raw vs. processed vs. metadata vs. individual-level). A doc that says only
"data are available" scores 0 on that clause; one that says "processed data are open; raw reads are
controlled access via dbGaP" scores 1.0 on both clauses. The ratio rewards consistently qualified
access language across every accession/cohort, not just one.

**Why it's hard to Goodhart.** You cannot cheaply pad the score by sprinkling the word "open" everywhere
— the qualifier requirement forces you to also name a concrete data layer, which only makes sense if you
actually know the access structure of your own dataset. Fabricating fake qualifiers ("open raw reads")
is directly falsifiable against the accession's real access policy by an auditor who checks the linked
GEO/dbGaP record, so gaming this metric in isolation creates a check-able, high-stakes lie rather than a
free win.

---

## 2. Provenance Specificity Density

**How it signals good science.** Verifiable science is made of falsifiable, checkable numbers —
instrument names, software versions, exact dimensions, read depths, accession IDs — not adjectives.
A dataset section stuffed with concrete, checkable identifiers lets a skeptical reader go verify each
claim independently; one that says "we sequenced samples and processed them appropriately" gives the
reader nothing to check. Specificity density is a cheap, generalizable proxy for how much the writer
actually engaged with their own data pipeline versus wrote boilerplate.

**Compute function.**

```python
import re

ACCESSION_RE = re.compile(r"\b(GSE|GSM|SRA|SRP|SRR|PRJNA|PRJEB|EGA[SDN]|dbGaP|phs\d+)[A-Z0-9]*\b", re.I)
DIM_RE = re.compile(r"\b[\d,]+\s*(genes|spots|samples|donors|reads|cells|participants|patients|studies|datasets)\b", re.I)
INSTRUMENT_VERSION_RE = re.compile(r"\b(v\d+(\.\d+)*|NovaSeq|HiSeq|NextSeq|MiSeq|GRCh\d+|SpaceRanger|CellRanger)\b", re.I)

def provenance_specificity_density(parsed: dict) -> float:
    """Assumes provenance/size_content free text is available per accession block
    (or provenance_and_access / included_cohorts_table for secondary-reuse genre).
    Returns a 0.0-1.0 density score, word-count normalized."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0

    blocks = parsed.get("accession_blocks", [])
    texts = []
    for b in blocks:
        texts.append(" ".join(filter(None, [b.get("provenance"), b.get("size_content")])))
    if parsed.get("provenance_and_access"):
        texts.append(parsed["provenance_and_access"])
    if parsed.get("included_cohorts_table"):
        # a real cohort table itself counts as high-specificity content
        table = parsed["included_cohorts_table"]
        texts.append(" ".join(str(v) for row in table for v in row.values()))

    joined = " ".join(t for t in texts if t).strip()
    if not joined:
        return 0.0  # no provenance prose at all -> floor

    word_count = max(len(joined.split()), 1)
    hits = (
        len(ACCESSION_RE.findall(joined))
        + len(DIM_RE.findall(joined))
        + len(INSTRUMENT_VERSION_RE.findall(joined))
    )
    # normalize: ~1 concrete identifier per 15 words is treated as saturating (score 1.0)
    density = hits / (word_count / 15.0)
    return min(density, 1.0)
```

**What the function does & why.** It concatenates the provenance-bearing prose (per-accession
provenance/size text, the secondary-reuse provenance paragraph, or the cohort table's own cell values)
and counts regex hits for three families of checkable specifics: accession/identifier patterns,
exact-dimension phrases ("30,494 genes × 122,202 spots"), and instrument/software/genome-build
versions. It normalizes by word count so verbose-but-vague sections don't win just by being long, then
caps at a density that a well-written accession block typically hits.

**Why it's hard to Goodhart.** Stuffing in random accession-shaped strings or fake version numbers to
juice the count is directly checkable — an accession number either resolves to a real, matching GEO/SRA
record or it doesn't, and a fabricated instrument/version string is inconsistent with the rest of the
described pipeline (e.g., claiming SpaceRanger output without a spatial platform). This is the same
"invented specificity" pattern the Discrepancy Self-Audit metric (#3) and Access-Tier Honesty (#1) are
built to catch, so fabrication that inflates this metric tends to depress the others.

---

## 3. Discrepancy Self-Audit Score

**How it signals good science.** Real datasets are messy: table counts don't always sum to the number
quoted in the abstract, cohorts get merged or split across the paper's own sections, N's drift between
methods and results. Good science *notices and states* these internal inconsistencies rather than
silently picking whichever number is convenient; a compiler-authored `dataset.md` that surfaces "the 12
tabulated cohorts don't sum to the paper's stated 18 studies" is doing exactly the kind of
adversarial-to-itself bookkeeping that catches sloppy or cherry-picked accounting before a reader has to.

**Compute function.**

```python
import re

RECONCILE_MARKERS = [
    "do not sum", "does not sum", "discrepancy", "mismatch", "does not match",
    "differs from", "inconsistent with", "note:", "however,", "unlike the",
    "the paper states", "vs. stated", "reconcil",
]
NUMBER_RE = re.compile(r"\b\d[\d,]*\b")

def discrepancy_self_audit(parsed: dict) -> float:
    """Assumes raw_text contains any cross-referencing prose the compiler wrote when
    tabulated counts and narrative counts diverge. Returns 0.0 (no numbers to check,
    or numbers present but unreconciled) to 1.0 (mismatch present and explicitly flagged)."""
    if not parsed or not parsed.get("raw_text", "").strip():
        return 0.0

    table = parsed.get("included_cohorts_table")
    intro = parsed.get("intro", "") or ""
    raw = parsed["raw_text"].lower()

    table_n = len(table) if table else None
    stated_numbers = [int(n.replace(",", "")) for n in NUMBER_RE.findall(intro) if len(n) <= 4]

    if table_n is None or not stated_numbers:
        # nothing to cross-check (e.g., primary-generation genre with a single accession,
        # or abstract-only floor case with no table at all) -> can't earn credit for auditing
        # something that structurally doesn't exist here; score low rather than skip
        return 0.2 if parsed.get("accession_blocks") else 0.0

    mismatch_exists = table_n not in stated_numbers
    if not mismatch_exists:
        return 1.0  # counts already reconcile; nothing to flag, full credit

    flagged = any(marker in raw for marker in RECONCILE_MARKERS)
    return 1.0 if flagged else 0.0  # mismatch present but silently unflagged -> worst case
```

**What the function does & why.** It compares the number of rows in the `Included cohorts` table
against small integers mentioned in the intro paragraph (the kind of place a paper states "18 studies /
24 independent datasets"). If the two already agree, there's nothing to audit and the doc gets full
credit by default. If they disagree, it searches the raw text for explicit reconciliation language
("do not sum", "discrepancy", "however", etc.). A mismatch that's silently left unflagged — the reader
has to notice it themselves — scores zero; a paper with no table/count structure to cross-check at all
(most primary-generation, single-accession cases) gets a low but non-zero floor rather than a skip,
per the hard constraint.

**Why it's hard to Goodhart.** You cannot win this by suppressing the table or the intro N (that
directly craters Provenance Specificity Density and the Structural Completeness metric below, and
trips the "nothing to audit" floor case which is capped well below full credit). You also cannot win it
by inserting a reconciliation-flavored sentence with no real mismatch behind it, because the metric only
rewards flagging when a genuine table-vs-prose count mismatch is independently detected from the
document's own numbers — the trigger condition isn't controlled by prose alone.

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
the paper actually did; a mismatch in either direction — a primary-generation paper skipping QC
entirely, or a secondary-reuse paper inventing raw-level preprocessing detail it has no standing to
claim — is a legitimate defect this metric is built to catch.

**Compute function.**

```python
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

    has_preprocessing = bool(parsed.get("preprocessing") or parsed.get("preprocessing_pointer"))
    raw_qc_language = False
    if parsed.get("preprocessing"):
        raw_qc_language = any(
            kw in parsed["preprocessing"].lower()
            for kw in ["raw read", "base calling", "demultiplex", "alignment", "spaceranger", "cellranger"]
        )

    score = 0.0
    weight = 0.0

    if is_primary:
        weight += 1.0
        # primary-generation genre should have real preprocessing depth (inline or pointed-to)
        score += 1.0 if has_preprocessing else 0.0

    if is_secondary:
        weight += 1.0
        if parsed.get("preprocessing") and raw_qc_language:
            # fabricated raw-QC detail with no primary data to justify it -> penalize hard
            score += 0.0
        else:
            # correctly stopping at cohort-level provenance (no invented raw QC)
            score += 1.0

    return score / weight if weight else 0.0
```

**What the function does & why.** It infers which genre pattern(s) the document exhibits from
structural fingerprints already in the shape (accession blocks => primary-generation; a cohort table or
a `Provenance and access` section => secondary-reuse), then checks the genre-appropriate completeness
condition: primary-generation docs are rewarded for having real preprocessing content or a pointer to
it; secondary-reuse docs are rewarded for *not* inventing raw-data QC language they have no standing to
claim, and penalized if they do. Papers that are neither (thin/malformed data docs) hit the floor.

**Why it's hard to Goodhart.** You can't win the primary-generation half by pasting boilerplate
preprocessing text, because vague or fabricated instrument/QC claims get caught by Provenance
Specificity Density (fake version strings, mismatched platforms) and Access-Tier Honesty (an
unqualified pipeline claim with no matching access-tier statement looks incomplete elsewhere). You can't
win the secondary-reuse half by adding a fake `## Preprocessing` section describing raw QC, because that
specific move is what the raw-QC-language check is designed to zero out directly — the two paths to a
high score are mutually exclusive within a single document, so a paper can't hedge by including both.

---

## Combination

These five metrics are built to fail together whenever the underlying document is dishonest rather than
merely thin. Padding access language without naming a data-layer tier wins nothing on Access-Tier
Honesty and actively looks suspicious under Provenance Specificity Density (real specificity usually
co-occurs with real tiering, since exact dims and accession IDs are the same sentences that carry access
qualifiers in the source examples). Inventing fake accession numbers, instrument versions, or IRB IDs to
inflate specificity or ethics-grounding is independently checkable and, if caught, would also flag as an
unreconciled internal inconsistency that Discrepancy Self-Audit is built to surface. Suppressing a cohort
table or the intro N to dodge an awkward count mismatch craters both Provenance Specificity Density and
Genre-Consistent Structural Completeness at once, since those numbers are exactly the "real content" both
metrics reward. And fabricating structural depth that doesn't match the paper's actual genre (raw QC
prose in a secondary-reuse doc, or ethics boilerplate with no named board in a primary-generation one) is
penalized directly by Genre-Consistent Completeness and Consent/Ethics Grounding respectively, with no
overlap-free way to buy credit on one without triggering a penalty on another. A document can only score
well across all five by actually being specific, honest about access tiers, self-auditing its own
numbers, ethically grounded in a genre-appropriate way, and structurally matched to what the paper really
did — which is to say, by being a good dataset descriptor rather than a well-disguised thin one.
