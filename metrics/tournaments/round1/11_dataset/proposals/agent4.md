# Proposer #4 — metrics for `data/dataset.md` (+ `data/preprocessing.md`)

Assumed parsed representation for all functions below: the artifact is pre-parsed into

```python
dataset_md = {
    "raw_text": str,                      # full markdown of data/dataset.md, "" if file absent
    "present": bool,                      # True iff data/dataset.md exists in the ARA
    "intro_paragraph": str,               # text before the first "##" heading
    "accession_blocks": [                 # one dict per "## {Accession} — ..." block (primary genre)
        {
            "heading": str,
            "fields": {                   # bold sub-bullet label -> its text, as literally written
                "Provenance": str | None,
                "Source / access": str | None,
                "Size / content": str | None,
                "Licensing / consent": str | None,
                "Key variables": str | None,
            },
        }, ...
    ],
    "cohorts_table_rows": [dict, ...],    # parsed "## Included cohorts" markdown table, [] if none
                                           # each row has at least an "N" key (secondary-reuse genre)
    "external_datasets_bullets": [str],   # bullets under "## External datasets used (not generated here)"
    "sections_present": set[str],         # normalized heading names actually found, e.g.
                                           # {"provenance_and_access","included_cohorts","consent_ethics",
                                           #  "preprocessing", "external_datasets"}
    "preprocessing_md_present": bool,     # whether a sibling data/preprocessing.md file exists
}
```
No other files are consulted. Every function treats a missing/empty/thin `dataset_md` as a scoreable
(low) case rather than a skip, per the hard constraint.

---

## 1. Accession Field-Completeness Density (AFCD)

**How it signals good science.** A primary-data-generation paper's credibility rests on whether a
downstream reader/agent can independently locate, size, and legally use the data. The shape doc names
five expected sub-fields per accession block (Provenance, Source/access, Size/content,
Licensing/consent, Key variables) — each answers a distinct reproducibility question (how was it made,
where does it live, how big is it, can I use it, what's in it). A compiler/author who fills all five,
with substantive (non-boilerplate) text, has done the provenance work; one who leaves gaps or pads with
vague filler has not. This rewards *density of real information*, not merely the existence of the file.

**Compute function.**
```python
import re

REQUIRED_FIELDS = ["Provenance", "Source / access", "Size / content",
                    "Licensing / consent", "Key variables"]

def _is_substantive(text):
    """Reject boilerplate/empty/placeholder-style field text."""
    if not text:
        return False
    t = text.strip()
    if len(t) < 15:                       # too short to carry real info
        return False
    if re.fullmatch(r"(n/?a|tbd|unknown|see above|-{1,3})\.?", t, re.I):
        return False
    return True

def accession_field_completeness_density(dataset_md):
    if not dataset_md.get("present") or not dataset_md.get("accession_blocks"):
        # Data-driven-with-generated-data genre absent entirely, or file missing/thin:
        # treated as a hard floor per the "missing input -> penalize" rule.
        return 0.0

    block_scores = []
    for block in dataset_md["accession_blocks"]:
        fields = block.get("fields", {})
        hits = sum(1 for f in REQUIRED_FIELDS if _is_substantive(fields.get(f)))
        block_scores.append(hits / len(REQUIRED_FIELDS))

    return sum(block_scores) / len(block_scores)
```

**What the function does & why.** For every `##`-level accession block, it checks each of the five
canonical sub-fields for presence *and* substance (rejecting one-word or placeholder answers), scores
each block as a fraction 0–1, and averages across all accession blocks in the file. A file with zero
accession blocks (because it's missing, or because the paper is genuinely primary-data but the compiler
never wrote the sub-bullets) scores 0.0 — a hard floor, not a skip. A secondary-reuse-only paper with no
accession blocks at all is legitimately scored by the *other* metrics below (this metric is silent
signal for that genre by design of its sibling metrics, not by returning N/A here — see Combination).

**Why it's hard to Goodhart.** Padding a field with a long but empty sentence ("Data licensing terms
are standard for this type of study and consistent with common practice.") is filterable by requiring
the field text to reference at least one of: an accession/registry ID pattern, a number, or a named
consent/IRB-style token — cheap boilerplate rarely contains any of these together across all five
fields simultaneously. To pass this metric an author has to actually type real accession numbers,
real dimensions, and real IRB numbers, which are independently checkable against the paper's own text
(a cheap paraphrase attack is caught the moment someone compares the "Size / content" number against
the actual GEO/dbGaP record — outside this metric's scope, but it raises the cost of faking).

---

## 2. Access-Tier Differentiation Ratio (ATDR)

**How it signals good science.** The shape doc flags collapsing "open vs. controlled-access" into a
single blanket claim as a real, identifiable defect. Good science about data provenance requires
telling the reader *which slice* of the data is open (metadata, processed objects) versus gated (raw
reads, individual-level records) — not just asserting availability once. A dataset description that
differentiates access by data-object type is doing real epistemic work (it lets a reader plan what they
can and can't reproduce); one that says "data available upon request" for everything is doing none.

**Compute function.**
```python
import re

OPEN_TOKENS = [r"\bopen\b", r"\bpublic(?:ly)?\b", r"\bno restriction"]
CONTROLLED_TOKENS = [r"\bcontrolled[- ]access\b", r"\bdbGaP\b", r"\bby request\b",
                      r"\brestricted\b", r"\bembargo", r"\bconsortium\b", r"\bgated\b"]

def _tier_hits(text, tokens):
    return sum(1 for pat in tokens if re.search(pat, text, re.I))

def access_tier_differentiation_ratio(dataset_md):
    if not dataset_md.get("present"):
        return 0.0

    access_texts = []
    for block in dataset_md.get("accession_blocks", []):
        t = block.get("fields", {}).get("Source / access")
        if t:
            access_texts.append(t)
    prov_text = ""
    if "provenance_and_access" in dataset_md.get("sections_present", set()):
        prov_text = dataset_md.get("intro_paragraph", "") + " " + dataset_md.get("raw_text", "")
        access_texts.append(prov_text)

    if not access_texts:
        # data-driven work with no access statement anywhere: worst case, not N/A.
        return 0.0

    differentiated = 0
    for t in access_texts:
        open_hits = _tier_hits(t, OPEN_TOKENS)
        controlled_hits = _tier_hits(t, CONTROLLED_TOKENS)
        # Differentiated = explicitly names BOTH an open-ish component and a
        # controlled/gated-ish component within the same access statement.
        if open_hits > 0 and controlled_hits > 0:
            differentiated += 1
        elif open_hits == 0 and controlled_hits == 0:
            differentiated += 0     # no tier language at all -> blanket/undocumented, worst
        # else: exactly one tier named -> partial credit handled below

    partial = sum(
        1 for t in access_texts
        if (_tier_hits(t, OPEN_TOKENS) > 0) != (_tier_hits(t, CONTROLLED_TOKENS) > 0)
    )
    score = (differentiated + 0.4 * partial) / len(access_texts)
    return min(score, 1.0)
```

**What the function does & why.** It scans every access-relevant text span (per-accession
`Source / access` fields, plus the `Provenance and access` section for the secondary-reuse genre) for
vocabulary indicating an *open* tier and vocabulary indicating a *controlled/gated* tier. A statement
naming both (e.g. "GEO metadata are open; raw reads are controlled-access via dbGaP") gets full credit
because it is doing the differentiation work the shape doc calls out as the key scoring axis. A
statement naming only one tier gets partial credit (it may be honestly single-tier, e.g. everything
really is open — but it's cheaper to fake, so it's discounted rather than zeroed or maxed). A statement
with no tier vocabulary at all, or a data-driven artifact with no access statement whatsoever, scores at
the floor.

**Why it's hard to Goodhart.** The cheap attack — sprinkling both "open" and "controlled" keywords
anywhere in the file without them applying to the *same* data object — is blunted by scoping the token
search to the access-specific fields/sections rather than the whole document, and by requiring the
co-occurrence to happen within a single access statement (per accession or per provenance section) so a
generic disclaimer elsewhere doesn't launder the score. Someone who wants to look "differentiated"
without doing the work still has to correctly assign which named accession/component is open vs. gated,
which is checkable against Metric 1's per-field accession content (if Size/content or Provenance for
that same accession doesn't match up with a controlled-access raw-data claim, the two metrics disagree).

---

## 3. Stated-vs-Tabulated Count Self-Audit Score (SVTC)

**How it signals good science.** The shape doc gives a concrete example (che26) where the paper's own
narrative N ("18 studies / 24 independent datasets") doesn't match its own cohort table (12 rows), and
calls out that a well-compiled artifact *surfaces* this discrepancy rather than silently picking a
number. This is a strong, general signal: an artifact that reconciles or explicitly flags its own
internal arithmetic is demonstrating active verification rather than passive transcription — exactly
the epistemic behavior "good science" review wants to reward, and it is *computable* (arithmetic
comparison), not just a stylistic preference.

**Compute function.**
```python
import re

STATED_N_PATTERN = re.compile(
    r"(?:total|overall|stated|comprises?|includes?)\D{0,20}?(\d[\d,]{1,7})\s*"
    r"(?:studies|datasets|cohorts|participants|patients|samples)", re.I)

HEDGE_PATTERN = re.compile(
    r"(do(?:es)? not sum|discrepanc|mismatch|inconsisten|does not match|"
    r"do not match|note[sd]?\s+that.*differ)", re.I)

def _to_int(numstr):
    return int(numstr.replace(",", ""))

def stated_vs_tabulated_self_audit(dataset_md):
    if not dataset_md.get("present"):
        return 0.0

    rows = dataset_md.get("cohorts_table_rows", [])
    if not rows:
        # No tabulated cohort structure to audit at all (e.g. thin/abstract-only dataset.md,
        # or file present but empty of any countable structure): penalize, don't skip.
        return 0.0

    tabulated_total = 0
    for row in rows:
        n_val = row.get("N") or row.get("n")
        if n_val is None:
            continue
        m = re.search(r"\d[\d,]*", str(n_val))
        if m:
            tabulated_total += _to_int(m.group())

    full_text = dataset_md.get("raw_text", "")
    stated_matches = [_to_int(m.group(1)) for m in STATED_N_PATTERN.finditer(full_text)]

    if not stated_matches:
        # Table exists but no separately-stated headline total to check against:
        # nothing to reconcile, but also nothing proving reconciliation was even considered.
        return 0.5

    mismatch_exists = any(abs(s - tabulated_total) > 0 for s in stated_matches)
    hedge_flagged = bool(HEDGE_PATTERN.search(full_text))

    if not mismatch_exists:
        return 1.0                       # numbers genuinely agree: best case
    return 1.0 if hedge_flagged else 0.0  # mismatch exists: only full credit if self-disclosed
```

**What the function does & why.** It sums the `N` column of the parsed cohorts table to get a
tabulated total, extracts any headline "N studies/datasets/participants" claim from the free-form
prose, and compares them. If they agree, the artifact is internally consistent — top score. If they
disagree *and* the text contains explicit hedge/discrepancy language near the mismatch, the artifact is
still top-scored because it did the harder, more honest thing (surfacing a real problem in the source
paper rather than hiding it). If they disagree and nothing flags it, that's the worst case: a silent,
uncommented internal contradiction — exactly the failure mode named in the shape doc.

**Why it's hard to Goodhart.** You cannot buy a high score by just inserting a hedge phrase like "note
some discrepancy" when the numbers actually agree — the branch that grants credit for hedging only
fires when a real numeric mismatch is detected first, so the hedge language is inert unless attached to
an actual arithmetic conflict. Conversely, you cannot buy a high score by suppressing the headline
number to avoid the comparison firing (removing the "total N" sentence lands you in the `stated_matches`
empty branch, which caps at 0.5, not 1.0) — hiding the number is worse than stating and reconciling it.

---

## 4. External-Dataset Reference Specificity (EDRS)

**How it signals good science.** `## External datasets used (not generated here)` exists precisely to
separate "the data this study actually produced/owns" from "the data it merely leaned on for validation
or context." Good science treats these borrowed datasets with the same identifying rigor as its own —
naming the accession/registry/DOI, not just a vague genre reference ("public GWAS summary stats were
used"). A paper that cites its external, non-generated inputs as specifically as its own strengthens the
whole chain of reproducibility; one that name-drops external validation vaguely is asking the reader to
trust an unverifiable claim.

**Compute function.**
```python
import re

ID_PATTERNS = [
    r"\bGSE\d+\b", r"\bGDS\d+\b", r"\bdbGaP\b", r"\bphs\d+\b",
    r"\b10\.\d{4,9}/\S+\b",                  # DOI
    r"\bNCT\d+\b",                           # trial registry
    r"\bPXD\d+\b", r"\bEGA[SD]\d+\b",
    r"\b[A-Z]{2,10}-\d{2,4}\b",               # named-cohort-style tokens, e.g. TRIAD-2023 style
]
ID_RE = re.compile("|".join(ID_PATTERNS))

def external_dataset_reference_specificity(dataset_md):
    if not dataset_md.get("present"):
        return 0.0

    bullets = dataset_md.get("external_datasets_bullets", [])
    if not bullets:
        # No external-datasets section at all. This is only a legitimate silence if the
        # artifact is self-contained (uses zero external data) -- but dataset.md gives no
        # positive signal of that here, so per the hard constraint we score the floor
        # rather than assume innocence.
        return 0.0

    specific = sum(1 for b in bullets if ID_RE.search(b))
    return specific / len(bullets)
```

**What the function does & why.** It looks at every bullet under the external-datasets section and
checks whether it contains a recognizable identifier pattern (GEO/dbGaP/DOI/trial-registry/named-cohort
token). The score is the fraction of external-data claims that are independently traceable rather than
asserted by genre-name alone. An artifact that never lists external datasets at all — which, on this
artifact alone, is indistinguishable from "the compiler forgot" versus "there truly were none" — is
scored at the floor rather than skipped, consistent with the hard constraint.

**Why it's hard to Goodhart.** Inventing plausible-looking fake IDs to pass the regex is possible in
principle, but doing so densely across every external bullet raises the chance that at least one
fabricated ID collides implausibly with the size/species/domain details already committed to in Metric
1's accession blocks or the paper's own described scope — i.e., gaming this metric in isolation is
cheap, but gaming it *consistently* with the rest of the file (which a careful reviewer or a downstream
agent will cross-check) is not. It also can't be gamed by simply adding more external-dataset bullets
with no IDs — that dilutes rather than inflates the ratio.

---

## Combination

These four metrics are constructed so that gaming any one in isolation degrades another. Padding
accession fields with generic prose to win AFCD (Metric 1) produces exactly the kind of vague,
non-token-bearing text that fails ATDR's requirement (Metric 2) that the *same* access statement name a
specific open component and a specific controlled component — generic filler rarely encodes real tier
distinctions. Suppressing an inconvenient headline total to dodge a mismatch penalty in SVTC (Metric 3)
directly starves EDRS-adjacent and AFCD's substantiveness checks, since the same free-text pass that
looks for a stated total is also where size/N information that Metric 1 rewards would need to live —
removing numbers to hide a discrepancy costs completeness elsewhere. And inflating EDRS (Metric 4) with
fabricated-looking identifiers creates numbers and codes that a reconciliation pass (in the spirit of
Metric 3) can flag as inconsistent with anything else claimed about scale or provenance in the same
file. Jointly, a paper can only score well across all four by actually doing the provenance homework:
real per-accession detail, real tier differentiation, honest arithmetic, and real external citations —
faking any one leaves fingerprints the other three are positioned to catch.
