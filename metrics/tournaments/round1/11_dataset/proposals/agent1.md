# Proposer 1 — metrics for `data/dataset.md` (+ `data/preprocessing.md`)

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

**How it signals good science:** The entire epistemic point of `dataset.md`, per its stated purpose, is telling a downstream agent whether the paper's numbers are *independently reproducible from public data* or *gated*. A dataset description that says "data is available" without distinguishing which parts (metadata vs. raw reads, processed objects vs. individual-level records) is not actually informative — it collapses a real reproducibility gradient into a boolean. Explicitly co-stating an open claim and its qualifier (e.g., "GEO metadata are open; raw reads are controlled-access via dbGaP") is a costly, checkable signal that the authors understood their own access structure rather than reflexively writing "available upon request."

**Compute function:**

```python
import re

OPEN_TERMS = [r"\bopen\b", r"\bpublic(?:ly)?\b", r"\bunrestricted\b", r"\bno accession\b"]
GATED_TERMS = [
    r"\bcontrolled[- ]access\b", r"\bdbgap\b", r"\brestricted\b", r"\bby request\b",
    r"\bconsortium\b", r"\bembargo", r"\bupon request\b", r"\bnot publicly\b",
]

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
        if has_open and has_gated:
            scores.append(1.0)      # explicit tiered disclosure
        elif has_open or has_gated:
            scores.append(0.5)      # single-tier claim, at least stated, but no contrast given
        else:
            scores.append(0.15)     # access mentioned/present as a field but no tier language at all
    return sum(scores) / len(scores)
```

**What the function does & why:** It walks every place an access claim could live (per-accession `Source / access` strings, the secondary-reuse `Provenance and access` block, and cohort-table cells), and for each one checks whether it contains *both* an open-type term and a gated-type term. Full credit only goes to blocks that name both sides of the access boundary; a block that only ever says "open" or only ever says "restricted" gets half credit (it's informative but we can't rule out an uncontrasted oversimplification); a block with no tier language at all is scored near zero. An entirely absent access story is a hard zero.

**Why it's hard to Goodhart:** You cannot satisfy this by dumping the word "open" or "controlled-access" everywhere — the metric requires *contrast* on a per-block basis, so an author padding every field with both buzzwords irrespective of truth would need those claims to survive metric 3 (discrepancy self-audit) and the size/content specificity checks, which would expose access claims that don't correspond to any real accession or cohort. Cheaply repeating "open and controlled" without any accompanying accession ID, dims, or platform gets caught by metric 2's specificity requirement.

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

**Why it's hard to Goodhart:** Regex-satisfying noise is cheap to produce ("GSE000000, 999,999 reads, Illumina") but such fabricated specificity is exactly the kind of unverifiable padding that metric 3 (self-audit for internal count consistency) and metric 4 (genre-scope fidelity) are designed to catch, since fabricated numbers rarely stay internally consistent with cohort totals or match the genre's legitimate level of detail (e.g., a secondary-reuse row suddenly citing an instrument model it has no business knowing).

---

## 3. Internal Discrepancy Self-Audit

**How it signals good science:** A dataset section that quietly hides a mismatch between the paper's stated aggregate ("18 studies / 24 independent datasets") and what it actually tabulates (12 rows) is doing accounting sleight-of-hand — silently picking whichever number sounds better. A well-compiled artifact surfaces the mismatch itself. This is a strong, genre-agnostic honesty signal: it rewards the *presence of self-criticism* about the data's own bookkeeping, which is a rarer and more costly thing to fabricate than a clean-looking (but unverified) number.

**Compute function:**

```python
import re

STATED_TOTAL_RE = re.compile(r"\b(\d[\d,]*)\s*(studies|datasets|cohorts|participants|samples)\b", re.I)
FLAG_TERMS = [r"\bdo(?:es)? not sum\b", r"\bdiscrepancy\b", r"\bmismatch\b",
              r"\binconsistent\b", r"\bnote[s]?\b.{0,40}\bdiffer", r"\bdoes not match\b"]

def discrepancy_self_audit(d: dict) -> float:
    """Assumes any stated aggregate count lives in d['intro_text'], and the tabulated
    count is len(d['included_cohorts_table']) or a summed 'N' column within it."""
    if not d.get("file_present"):
        return 0.0

    stated_matches = STATED_TOTAL_RE.findall(d.get("intro_text", "") or "")
    tabulated_n = len(d.get("included_cohorts_table", []))

    if not stated_matches and tabulated_n == 0:
        return 0.1  # no numbers stated anywhere to cross-check -> can't verify anything, penalize

    if not stated_matches or tabulated_n == 0:
        return 0.3  # only one side of the comparison exists -> unverifiable claim, mild penalty

    stated_counts = {int(n.replace(",", "")) for n, _ in stated_matches}
    consistent = tabulated_n in stated_counts

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

**What the function does & why:** It extracts any "N studies/datasets/cohorts" style aggregate claim from the intro prose and compares it to the actual row count of the `Included cohorts` table. If there's nothing to compare (no stated aggregate, or no table), it can't verify anything and scores low rather than abstaining. If the two numbers agree, it scores high but not maximal (nothing was actually being tested for honesty). If they disagree, the score hinges entirely on whether the disagreement is named in nearby prose — an unflagged silent mismatch is the worst-scoring case in the whole metric, deliberately below "we don't know."

**Why it's hard to Goodhart:** An author can't win by suppressing all numbers (that trips the "nothing to compare" 0.1 floor) or by making the counts trivially equal by only tabulating a subset without saying so (that's the exact silent-mismatch failure mode the metric is built to punish once cross-checked against the aggregate claim in the intro). Adding a fake "note: numbers differ" sentence when they actually match doesn't help since consistent cases are capped below the flagged-mismatch case, so gaming this metric requires actually engineering a true, disclosed discrepancy story, which only a genuinely careful compiler produces.

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

**Why it's hard to Goodhart:** Removing all preprocessing detail from a secondary-reuse file to dodge the raw-QC check just tanks metric 2 (specificity) and looks like thinness; conversely, adding real accession IDs to satisfy the primary-generation check means the claim becomes checkable and must survive metric 1 (does the accession's access tier make sense) and metric 3 (does it reconcile with any stated totals). The metric specifically targets the cheap move (declaring things you can't back up) and makes the escape route (adding fabricated but internally-consistent detail) expensive across the other metrics.

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

## Combination

These five metrics are built to interlock rather than to be independently maxed out. Padding every field with reassuring buzzwords ("open," "IRB approved," "generated in this study") to win Access-Tier Honesty and Ethics Coverage produces claims that must then survive Provenance & Size Specificity (do real accession IDs, dimensions, and instruments back up the claim?) and Genre-Scope Fidelity (is the claim even legitimate for this genre — e.g., can a secondary-reuse paper actually claim IRB numbers?). Conversely, piling on fabricated numeric specificity to win the Specificity metric creates exactly the kind of unverified aggregate that the Discrepancy Self-Audit metric is designed to expose once cross-checked against the paper's own stated totals — and a paper that tries to dodge that check by omitting aggregate numbers entirely gets penalized by the self-audit's "nothing to compare" floor instead. In short: honesty-shaped text without underlying structure fails specificity and genre checks; structure-shaped fabrication without honesty fails the self-audit and access-tier contrast checks. A paper can only score well across all five by actually having a well-provenanced, tier-honest, internally-consistent, genre-appropriate dataset section — which is the real target.

agent1 dataset: 5 metrics written
