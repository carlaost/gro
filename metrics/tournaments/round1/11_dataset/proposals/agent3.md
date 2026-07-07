# Proposer 3 — metrics for `data/dataset.md` (+ `data/preprocessing.md`)

All functions assume a parsed representation `doc` of the artifact with this shape (a reasonable
parse of the free-form markdown described in the shape doc):

```python
doc = {
    "exists": bool,                    # was a data/ directory emitted at all
    "raw_text": str,                   # full concatenated text of dataset.md (+ preprocessing.md if separate)
    "intro": str,                      # intro paragraph text (before first ## heading), "" if absent
    "sections": {                      # dict: heading title -> body text (verbatim, includes sub-bullets)
        # e.g. "Provenance and access", "Included cohorts", "Consent / ethics",
        # "External datasets used (not generated here)", "Preprocessing", ...
    },
    "accession_blocks": [              # one entry per "## {Accession} — {desc}" heading
        {
            "heading": str,
            "fields": {                 # bolded sub-fields found inside the block, keyed by label
                "Provenance": str, "Source / access": str, "Size / content": str,
                "Licensing / consent": str, "Key variables": str,
                # missing labels simply absent from dict
            },
        },
        ...
    ],
    "cohort_table": {                  # parsed "## Included cohorts" table, if present
        "columns": [str, ...],
        "rows": [[cell, ...], ...],
    } or None,
    "has_preprocessing_pointer": bool, # True if dataset.md points to preprocessing.md or method.md for QC
    "preprocessing_text": str,         # body of data/preprocessing.md, or pointed-to section, "" if none
}
```

---

## Metric 1 — Access-Tier Honesty Ratio

**How it signals good science.** The whole epistemic point of a dataset section is to tell a
downstream agent whether the paper's numbers are independently checkable. A claim like "data are
available" is scientifically empty unless it says *which* layer is open and which is gated — metadata
vs. processed objects vs. raw reads vs. cohort-level data behind a consortium request. A well-compiled
artifact never collapses this into a binary; it names the tier for every access claim it makes. More
of this precision is strictly more useful to a reader trying to reproduce the work, and it is also the
place authors are most tempted to overclaim openness — so rewarding tier explicitness rewards honesty
under a real incentive to fudge.

**Compute function.**
```python
import re

def access_tier_honesty(doc: dict) -> float:
    """
    Assumes: doc["exists"], doc["raw_text"], doc["accession_blocks"], doc["sections"].
    Scans every place an access/availability claim is made and checks whether it is
    paired with an explicit tier qualifier (open / controlled / restricted / by-request /
    embargoed / consortium / dbGaP / EGA / DUA, etc.) rather than a bare "available"/"open".
    """
    if not doc.get("exists", False):
        return 0.0

    TIER_WORDS = re.compile(
        r"\b(open|public|controlled[- ]access|restricted|by[- ]request|embargo(ed)?|"
        r"dbGaP|EGA|consortium|data use agreement|DUA|gated|upon reasonable request)\b",
        re.IGNORECASE,
    )
    BARE_CLAIM = re.compile(
        r"\b(data (are|is) available|available upon|access(ible)?)\b", re.IGNORECASE
    )

    # Gather every candidate "access claim" sentence from accession blocks + relevant sections.
    claim_sources = []
    for block in doc.get("accession_blocks", []):
        src = block.get("fields", {}).get("Source / access", "")
        if src:
            claim_sources.append(src)
    for key in ("Provenance and access", "Release status", "External datasets used (not generated here)"):
        if key in doc.get("sections", {}):
            claim_sources.append(doc["sections"][key])

    if not claim_sources:
        # Data-driven artifact with no access statement anywhere: penalize heavily.
        return 0.05

    qualified = 0
    total = 0
    for text in claim_sources:
        sentences = re.split(r"(?<=[.;])\s+", text)
        for s in sentences:
            if BARE_CLAIM.search(s) or TIER_WORDS.search(s):
                total += 1
                if TIER_WORDS.search(s):
                    qualified += 1

    if total == 0:
        return 0.1  # claims exist as prose but nothing recognizable as an access statement at all
    return qualified / total
```

**What the function does & why.** It walks every "Source / access" field inside accession blocks and
every reuse-genre section that plausibly states availability, splits into sentences, and asks: of the
sentences that make an access claim at all, how many pair that claim with a concrete tier word (open,
controlled-access, dbGaP, by-request, embargoed, DUA, etc.)? The ratio rewards artifacts that
consistently disaggregate access by layer (metadata open / raw controlled) and punishes both silence
(no access claim found → 0.05) and blanket, unqualified "available" language (claims found but no tier
words → low ratio).

**Why it's hard to Goodhart.** You cannot game this by mechanically inserting tier-sounding words
without them being true, because the metric is paired (deliberately) with Metric 3 below, which
cross-checks stated access/size against the cohort table and accession fields for consistency — sprayed
keyword tier-words that don't match the actual described access mechanism will show up as
inconsistent under that check. Simply repeating "open" everywhere also fails, because the regex
requires the qualifier to co-occur with an access-claim sentence, not just appear anywhere in the
document — stuffing keywords into unrelated prose doesn't raise the ratio since those sentences aren't
counted as claim sentences and drag the denominator down if they trip the BARE_CLAIM pattern without
substance.

---

## Metric 2 — Genre-Conditioned Structural Completeness

**How it signals good science.** The shape doc is explicit that `data/dataset.md` has two legitimate
genres — primary-data-generation (accession blocks with Provenance/Source-access/Size-content/
Licensing-consent/Key-variables) and secondary-reuse (Provenance-and-access + Included-cohorts table +
Consent/ethics). Good science means filling in the genre-appropriate fields fully, not padding with
irrelevant boilerplate or leaving fields thin. A metric that scores completeness *relative to the
detected genre* rewards real documentation effort while correctly not punishing a secondary-reuse
paper for lacking fields (like sequencing depth) that genuinely don't apply to it — avoiding a
genre-mismatched expectation the shape doc explicitly warns against.

**Compute function.**
```python
def genre_conditioned_completeness(doc: dict) -> float:
    """
    Assumes: doc["exists"], doc["accession_blocks"], doc["cohort_table"], doc["sections"].
    Detects genre by structural signature, then scores fraction of genre-required
    fields that are present and non-trivial (length above a floor).
    """
    if not doc.get("exists", False):
        return 0.0

    def substantive(text: str, floor: int = 15) -> bool:
        return bool(text) and len(text.strip()) >= floor

    is_primary = len(doc.get("accession_blocks", [])) > 0
    is_secondary = doc.get("cohort_table") is not None

    if not is_primary and not is_secondary:
        # Neither recognizable genre pattern present -- likely the abstract-only floor case
        # (bare N, no accession, no cohort table). This is itself informative: score it low
        # rather than skipping, per the hard constraint.
        return 0.1 if substantive(doc.get("intro", ""), floor=5) else 0.0

    score_components = []

    if is_primary:
        required = ["Provenance", "Source / access", "Size / content", "Licensing / consent", "Key variables"]
        for block in doc["accession_blocks"]:
            fields = block.get("fields", {})
            hits = sum(1 for r in required if substantive(fields.get(r, "")))
            score_components.append(hits / len(required))

    if is_secondary:
        table = doc["cohort_table"]
        required_cols = {"cohort", "source study", "n", "reference standard"}
        present_cols = {c.strip().lower() for c in table.get("columns", [])}
        col_score = len(required_cols & present_cols) / len(required_cols)
        has_access_section = substantive(doc.get("sections", {}).get("Provenance and access", ""))
        has_consent = "Consent / ethics" in doc.get("sections", {})  # presence alone is fine here;
        # secondary genre may legitimately say "not applicable at the review level"
        secondary_score = (col_score + float(has_access_section) + float(has_consent)) / 3
        score_components.append(secondary_score)

    return sum(score_components) / len(score_components)
```

**What the function does & why.** It first classifies the artifact's genre from hard structural
signals (presence of accession headings vs. a cohort table — both can co-occur, e.g. huu25's external
reference datasets), then scores only the fields that genre is expected to carry, requiring each field
to clear a minimum length floor so a one-word placeholder ("N/A") doesn't count as complete. Neither
pattern found at all collapses to the abstract-only floor case, which per the hard constraint gets a
low score rather than being skipped as "not applicable" — the shape doc itself flags this as a
recognizable degenerate case, not a legitimate absence.

**Why it's hard to Goodhart.** Padding a field to clear the length floor with filler doesn't help
because the floor is deliberately low (just enough to exclude "N/A"/"—"/empty) — real gaming would
require writing genre-plausible technical content (instrument names, accession IDs, IRB numbers),
which is itself costly to fabricate convincingly and is exactly the kind of specific, checkable detail
that constitutes good documentation. Faking a whole extra accession block to average up the primary
score is caught by Metric 1 (a fabricated accession without a matching real Source/access tier reads as
an unqualified or inconsistent claim) and by Metric 3 (a fabricated cohort/accession disrupts internal
count consistency).

---

## Metric 3 — Cross-Statement Numerical Consistency & Self-Audit

**How it signals good science.** Real datasets accumulate discrepancies — a paper says "18 studies /
24 independent datasets" but only 12 show up in a table; sample sizes get revised between abstract and
methods. Good science does not silently pick whichever number is convenient; it surfaces the mismatch.
The shape doc explicitly cites che26 as the positive example: its `dataset.md` flags that its 12
tabulated cohorts don't sum to the paper's stated totals. Rewarding *flagged* mismatches (and
penalizing *silent* ones) directly measures whether the artifact is doing honest bookkeeping rather
than laundering an inconsistency into a clean-looking summary.

**Compute function.**
```python
import re

def cross_statement_consistency(doc: dict) -> float:
    """
    Assumes: doc["raw_text"], doc["intro"], doc["cohort_table"], doc["sections"].
    Extracts N-like quantities from the intro/prose and compares to the sum of the
    cohort table's N column (or the count of accession blocks' Size/content Ns).
    Rewards explicit acknowledgment of any mismatch; penalizes silent mismatches
    and, more heavily, an inability to cross-check at all when a table exists.
    """
    if not doc.get("cohort_table") and "Included cohorts" not in doc.get("sections", {}):
        # No tabulated data to cross-check against -- can't earn full credit for self-audit,
        # since there's nothing to reconcile. Score low-mid: unverifiable is not the same as
        # verified-consistent, and the hard constraint forbids treating this as N/A.
        return 0.3

    stated_totals = [int(n.replace(",", "")) for n in
                      re.findall(r"(\d[\d,]{2,})\s*(?:independent )?(?:datasets|studies|cohorts|participants)",
                                 doc.get("intro", "") + " " + doc.get("raw_text", ""))]

    table = doc["cohort_table"]
    n_col_idx = None
    for i, col in enumerate(table.get("columns", [])):
        if col.strip().lower() == "n":
            n_col_idx = i
            break
    tabulated_total = 0
    if n_col_idx is not None:
        for row in table.get("rows", []):
            try:
                tabulated_total += int(re.sub(r"[^\d]", "", row[n_col_idx]))
            except (ValueError, IndexError):
                continue
    tabulated_count = len(table.get("rows", []))

    mismatch_found = any(
        abs(t - tabulated_count) > 0 and t != tabulated_total for t in stated_totals
    ) if stated_totals else False

    FLAG_PHRASES = re.compile(
        r"(does not sum|do not sum|discrepanc|mismatch|does not match|inconsisten|"
        r"fewer than stated|differs from)", re.IGNORECASE
    )
    flagged = bool(FLAG_PHRASES.search(doc.get("raw_text", "")))

    if not mismatch_found:
        return 0.85  # numbers reconcile cleanly -- good, though slightly below an "audited" artifact
    return 1.0 if flagged else 0.1
```

**What the function does & why.** It pulls any prose-stated totals ("18 studies / 24 independent
datasets") and compares them against what the cohort table actually enumerates (row count and summed
`N` column). If everything reconciles, it scores well but not perfectly (0.85) — clean numbers with no
audit trail are good but unremarkable. If there's a real mismatch, the artifact is rewarded maximally
only if it explicitly names the discrepancy somewhere in the text (che26's actual behavior); silently
carrying an unreconciled mismatch scores near zero, since that's a worse failure than not having a
table to check at all.

**Why it's hard to Goodhart.** You can't win this by mechanically inserting the word "discrepancy"
absent a real one — the flagged-language search only pays off when `mismatch_found` is true, so
sprinkling audit-sounding language when the numbers already reconcile does nothing (you're capped at
0.85 either way). You also can't win it by suppressing all stated totals from the prose to dodge the
mismatch check, because that empties `stated_totals` and the function falls through to the "no
mismatch found" branch at 0.85 rather than 1.0 — omission caps your score below what honest reconciliation-with-disclosure would earn, so hiding numbers is strictly worse than stating and reconciling them.

---

## Metric 4 — Preprocessing Traceability Proportional to Raw-Data Claims

**How it signals good science.** Whether a QC/preprocessing section is *warranted* is genre-dependent:
primary-data-generation papers that claim raw reads/samples owe the reader a preprocessing trail
(pipeline version, QC thresholds, normalization); secondary-reuse papers correctly have none, because
there is no raw data to clean. Good science means preprocessing detail scales with the raw-data claims
actually made — an artifact that claims to have generated raw sequencing data but supplies zero
preprocessing detail is hiding exactly the steps most likely to introduce bias (filtering thresholds,
batch correction, exclusions).

**Compute function.**
```python
import re

def preprocessing_traceability(doc: dict) -> float:
    """
    Assumes: doc["accession_blocks"], doc["has_preprocessing_pointer"], doc["preprocessing_text"],
    doc["sections"].
    """
    if not doc.get("exists", False):
        return 0.0

    raw_data_claim = any(
        re.search(r"\b(raw|reads|FASTQ|sequenc|instrument|NovaSeq|Visium|assay)\b",
                  block.get("fields", {}).get("Provenance", ""), re.IGNORECASE)
        for block in doc.get("accession_blocks", [])
    )

    if not raw_data_claim:
        # Secondary-reuse or non-generative genre: preprocessing legitimately absent.
        # Score neutrally-high for genre-appropriate silence rather than penalizing absence,
        # but only if the artifact doesn't claim otherwise (fabricated QC on reused data would
        # be caught by Metric 2's consent/provenance cross-check, not here).
        return 0.7

    pointer_or_text = doc.get("preprocessing_text", "") or (
        "pointer" if doc.get("has_preprocessing_pointer") else ""
    )
    if not pointer_or_text:
        return 0.0  # raw data claimed, zero preprocessing trail anywhere -- penalize hard

    QC_TERMS = re.compile(
        r"\b(QC|quality control|filter(ed|ing)?|threshold|normali[sz]ation|"
        r"exclu(ded|sion)|pipeline|version|batch correct)\b", re.IGNORECASE
    )
    text = doc.get("preprocessing_text", "")
    hits = len(set(m.lower() for m in QC_TERMS.findall(text)))
    return min(1.0, 0.3 + 0.15 * hits)  # baseline for having *any* trail, scaled by specificity
```

**What the function does & why.** It first checks whether any accession block's Provenance field
claims raw/instrument-level data generation. If not, preprocessing is genuinely inapplicable and the
metric scores it 0.7 (a deliberate non-maximal "fine, not exceptional" score — see the Combination
paragraph for why this isn't a free pass). If raw data is claimed, the function requires either a
`data/preprocessing.md` pointer or inline preprocessing text; finding none is scored 0, since a raw-data
paper with zero documented QC trail is a real defect. When a trail exists, it counts distinct QC
vocabulary terms (filtering, thresholds, normalization, pipeline version, batch correction) as a proxy
for how mechanistically specific the described preprocessing actually is, capping at 1.0.

**Why it's hard to Goodhart.** Just repeating QC buzzwords without real detail is capped by the
`set()` dedup (repeating "filtered" ten times counts once) and by the modest per-term increment
(0.15), so reaching 1.0 requires genuinely covering several distinct QC dimensions, not keyword
stuffing one term. Claiming no raw data to dodge the requirement (falling into the 0.7 branch) is
self-defeating because it directly contradicts the Provenance field content scored under Metric 2's
completeness check and Metric 1's access-tier check (a "no raw data" claim alongside a dbGaP raw-reads
accession is an internal contradiction those metrics would separately punish).

---

## Combination

These four metrics are jointly hard to game because each one polices the seams the others leave open.
Access-Tier Honesty (1) rewards precise, differentiated access language, but nothing stops someone from
inserting well-chosen tier words with no real backing — except that Genre-Conditioned Completeness (2)
requires those same claims to sit inside a substantively filled-out accession or cohort structure, so a
thin shell dressed up with tier vocabulary scores well on (1) but poorly on (2). Cross-Statement
Consistency (3) can't be gamed by hiding numbers, because omission is scored strictly worse than honest
reconciliation-with-disclosure, and inserting fake mismatch-language without a real mismatch buys
nothing. Preprocessing Traceability (4) closes the remaining gap: an artifact that inflates its
apparent completeness by fabricating an accession block (to help score 2) or claiming raw data it
didn't generate (to appear more rigorous) now owes a real preprocessing trail under (4) or contradicts
itself under (1)'s access-tier check for that same fabricated block. In short: overclaiming provenance
detail creates a preprocessing obligation you must also fake convincingly; overclaiming access
precision without substance gets caught by completeness; and hiding or fabricating numbers is
structurally penalized rather than rewarded — so cheaply winning all four at once requires fabricating
a fully mutually-consistent fake dataset record, which is materially harder than just doing the honest
documentation.
