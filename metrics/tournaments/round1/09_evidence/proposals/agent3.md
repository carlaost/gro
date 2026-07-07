# Proposer #3 — metrics for `evidence/`

Assumed parsed representation (`artifact: dict`) used by all compute functions below:

```python
artifact = {
    "readme": {
        "tables_rows":  [{"file": str, "source": str, "claims": list[str], "description": str}, ...],
        "figures_rows": [{"file": str, "source": str, "claims": list[str], "description": str}, ...],
        "completeness_note": str,   # free prose closing section of README.md
    },
    "tables": [
        {
            "file": str, "source": str, "caption": str, "screenshot": str,
            "extraction_type": "raw_table" | "derived_subset",
            "derived_from": str | None,
            "body": [[cell_str, ...], ...],     # header row + data rows, exact cell strings
            "notes": [str, ...],                # bullet strings, may be []
        }, ...
    ],
    "figures": [
        {
            "file": str, "source": str, "caption": str, "screenshot": str,
            "figure_type": "quantitative_plot" | "diagram" | "qualitative_sample" | "mixed",
            "extraction_method": "exact_from_labels" | "digitized_estimate" | "visual_description" | None,
            "reading_confidence": "high" | "medium" | "low" | None,
            "data_table": [[cell_str, ...], ...] | None,
            "trend_summary": str | None,
            "visual_description": dict | None,
            "caveats": [str, ...],
            "panels": [ {..same shape recursively..}, ... ] | None,   # only if figure_type == "mixed"
        }, ...
    ],
}
```

A shared helper, restated inline where used: `flatten_figures(figures)` yields every leaf figure/panel
(expanding `mixed` figures into their `panels`, recursively) so type-specific checks apply uniformly.

---

## 1. Ledger Reconciliation Score

**How it signals good science.** The spec makes `evidence/` a *systematic sweep*: every numbered
table/figure in the source must be filed or explicitly named as skipped-with-reason. A README whose
closing note actually reconciles a stated source-count against what's filed is doing real bookkeeping,
not just decorating a folder with a plausible-looking index. This is the single most checkable honesty
signal in the whole artifact — "did you actually count, or did you just file some things and stop."

**Compute function.**
```python
import re

def ledger_reconciliation_score(artifact: dict) -> float:
    """
    Assumes: artifact["readme"]["completeness_note"] is free prose that, if honest, states
    the total count of numbered tables/figures in the source and either confirms all were
    filed or names exactly which were skipped and why. artifact["readme"]["tables_rows"] /
    ["figures_rows"] are the actually-filed index rows.
    """
    note = artifact["readme"].get("completeness_note", "") or ""
    filed_tables = len(artifact["readme"]["tables_rows"])
    filed_figures = len(artifact["readme"]["figures_rows"])

    if not note.strip():
        return 0.0  # no accounting at all: cannot distinguish "complete" from "silently partial"

    stated_table_totals = [int(n) for n in re.findall(r"(\d+)\s+(?:numbered\s+)?tables?\b", note, re.I)]
    stated_figure_totals = [int(n) for n in re.findall(r"(\d+)\s+(?:numbered\s+)?figures?\b", note, re.I)]
    named_skips = re.findall(r"\b(?:Table|Figure)\s+S?\d+[A-Za-z0-9.\-]*", note)

    score = 0.0
    checks = 0

    for filed_n, stated_list in ((filed_tables, stated_table_totals), (filed_figures, stated_figure_totals)):
        checks += 1
        if not stated_list:
            continue  # no count stated for this kind -> 0 contribution
        stated = max(stated_list)  # take the largest plausibly-the-total number mentioned
        accounted = filed_n + sum(1 for s in named_skips)  # crude: skips shared across both kinds
        if stated == filed_n:
            score += 1.0   # filed == stated total, nothing missing
        elif accounted >= stated:
            score += 0.6   # gap covered by named skips, but imprecisely attributable
        else:
            gap = stated - accounted
            score += max(0.0, 1.0 - gap / max(stated, 1))

    # Bonus signal: does the note affirmatively claim "none silently skipped" / name a reason?
    has_affirmation = bool(re.search(r"none.*skip|no.*silently|accounted for|not filed because|not present in", note, re.I))
    base = score / checks if checks else 0.0
    return round(min(1.0, base * (1.0 if has_affirmation else 0.7)), 3)
```

**What it does & why.** Pulls any numeric "N tables"/"N figures" claims out of the completeness note
via regex, and any explicit `Table N` / `Figure N` mentions (the named-skip list). Compares the stated
total against what's actually filed. Full credit only when they reconcile exactly; partial credit when
a gap is explicitly covered by named skips; a further multiplier docks artifacts whose prose never
actually asserts completeness in words (e.g. an index with no closing statement at all, or one that
just lists files without ever claiming "this is everything"). An empty note is an automatic zero — the
hard constraint requires this, since "no note" is worse than a note that turns out to be slightly off.

**Why it's hard to Goodhart.** You could pad the note with a self-serving "N tables, all filed" — but
that's checked against the *actual filed count*, which the compiler can't fudge for free (making more
table files means doing more transcription work, which is real cost, not free text). Simply inflating
the stated total to make the ratio look bad-but-honest doesn't help either, since under-stating filed
counts triggers the "gap" penalty. The cheapest attack — asserting a suspiciously round total that
happens to match filed count — is caught jointly by Metric 5 below (an artifact with near-zero content
that "reconciles" trivially at 0=0 still scores near-zero there, since Metric 5 penalizes an empty
evidence base outright regardless of what the ledger says about it).

---

## 2. Extraction-Method / Type Internal Consistency

**How it signals good science.** The schema encodes an explicit honesty contract: `exact_from_labels`
means bare numbers, `digitized_estimate` means `≈`-prefixed numbers, `low` confidence licenses (and
should trigger) a trend-summary fallback instead of overconfident precision, and `diagram`/
`qualitative_sample` figures must never carry a fabricated numeric table. A compiler that keeps these
labels internally consistent with what it actually produced is being honest about its own uncertainty
— exactly the epistemic virtue "good science" is trying to capture. A compiler that mislabels
(`exact_from_labels` slapped on eyeballed numbers, or a numeric table stuffed into a diagram) is lying
about its own confidence, which is worse than just being imprecise.

**Compute function.**
```python
def flatten_figures(figures):
    for f in figures:
        if f.get("figure_type") == "mixed" and f.get("panels"):
            yield from flatten_figures(f["panels"])
        else:
            yield f

def extraction_consistency_score(artifact: dict) -> float:
    """
    Assumes: each table/figure dict carries the fields in the shared schema above, in particular
    extraction_type/extraction_method/reading_confidence/data_table/trend_summary. Missing fields
    (None) are treated as violations, not as "not applicable."
    """
    violations = 0
    checks = 0

    for t in artifact["tables"]:
        checks += 1
        if t.get("extraction_type") == "derived_subset" and not t.get("derived_from"):
            violations += 1
        if t.get("extraction_type") == "raw_table" and t.get("derived_from"):
            violations += 1
        if t.get("extraction_type") not in ("raw_table", "derived_subset"):
            violations += 1

    for fig in flatten_figures(artifact["figures"]):
        checks += 1
        ftype = fig.get("figure_type")
        method = fig.get("extraction_method")
        conf = fig.get("reading_confidence")
        table = fig.get("data_table")
        trend = fig.get("trend_summary")

        if method is None or conf is None:
            violations += 1

        if ftype == "quantitative_plot":
            if not table and not trend:
                violations += 2  # structural failure per spec: never neither
            flat = " ".join(str(c) for row in (table or []) for c in row)
            if method == "exact_from_labels" and "≈" in flat:
                violations += 1  # approx marker under an "exact" claim
            if method == "digitized_estimate" and table and "≈" not in flat:
                violations += 1  # suspiciously precise for an admitted estimate
            if conf == "low" and table and not trend:
                violations += 1  # low confidence numbers with no narrative fallback

        elif ftype in ("diagram", "qualitative_sample"):
            if table:
                violations += 2  # fabricated numeric table masquerading as non-quantitative
            if not fig.get("visual_description"):
                violations += 1

    return round(max(0.0, 1.0 - violations / max(3 * checks, 1)), 3)
```

**What it does & why.** Walks every table and every leaf figure (mixed figures expanded per-panel) and
checks label/content pairs against the spec's own honesty rules: derived vs raw tables must carry (or
omit) `derived_from` consistently; `quantitative_plot`s must have a table or a trend-summary fallback,
never neither; `exact_from_labels` numbers must not contain `≈`; `digitized_estimate` numbers that
never carry `≈` look over-precise for an admitted estimate; `low`-confidence figures with numeric
tables and no accompanying prose narrative are under-hedged; diagrams/qualitative samples must never
carry a numeric data table. Each violation type is weighted by how serious the corresponding spec rule
calls it (structural failures and masquerading get 2x weight). Missing fields count as violations, not
skips.

**Why it's hard to Goodhart.** Any attempt to game one check tends to trip another: labeling everything
`digitized_estimate` to dodge the "no ≈ under exact" check now requires actually inserting `≈` markers
everywhere, which is directly visible and checkable against the screenshot/caption elsewhere, and makes
the artifact look uniformly low-confidence (hurting Metric 5's grounding-quality component if extended,
and looking suspicious next to a `high`-reading-confidence claim). Conversely, labeling everything
`exact_from_labels` to look rigorous requires the numbers to actually be bare (no ≈), which for a truly
digitized/estimated figure means either doing the harder work of precise extraction or getting caught
by cross-referencing against Metric 3's arithmetic checks below when the "exact" numbers don't add up.

---

## 3. Self-Scrutiny Arithmetic-Verification Rate

**How it signals good science.** The one worked example in the spec itself (`figure1.md`, PRISMA flow)
shows the compiler catching that database-record subtotals (179+311+256+195=941) don't reconcile with
"601 screened after removing 219 duplicates," and flagging this in a caveat rather than silently
transcribing numbers that don't add up. That's the actual scientific virtue here: not just recording
numbers, but checking them against each other and reporting when they don't cohere. This is a
positive, checkable behavior — arithmetic verification — that most transcription pipelines skip.

**Compute function.**
```python
import re

def _numbers_in(text: str) -> list[float]:
    return [float(n.replace(",", "")) for n in re.findall(r"-?\d[\d,]*\.?\d*", text or "")]

def self_scrutiny_score(artifact: dict) -> float:
    """
    Assumes: table/figure "notes"/"caveats" are lists of free-text strings, and table/figure
    "body"/"data_table" cells are strings possibly containing arithmetic-checkable quantities
    (e.g. subgroup counts, n's). We independently look for near-miss additive relationships
    among numbers appearing in the same object, then check whether a caveat actually names
    the discrepancy, rather than trusting a self-reported "I checked this" claim at face value.
    """
    objs = []
    for t in artifact["tables"]:
        objs.append({"numbers": [n for row in t.get("body", []) for c in row for n in _numbers_in(c)],
                     "notes": t.get("notes", [])})
    for fig in flatten_figures(artifact["figures"]):
        text_blobs = [fig.get("trend_summary") or ""]
        table = fig.get("data_table") or (fig.get("visual_description") or {}).get("transcribed_numbers")
        nums = [n for row in (table or []) for c in row for n in _numbers_in(c if isinstance(c, str) else str(c))]
        objs.append({"numbers": nums, "notes": fig.get("caveats", [])})

    flagged_correct = 0
    flagged_total = 0
    found_inconsistency = 0

    for o in objs:
        nums = o["numbers"]
        notes_text = " ".join(o["notes"]).lower()
        mentions_discrepancy = bool(re.search(r"reconcil|discrepan|does not match|inconsist|do not match", notes_text))

        # crude independent check: does any subset of numbers sum to another present number, or fail to?
        mismatch_detected = False
        if len(nums) >= 3:
            for i in range(len(nums)):
                target = nums[i]
                rest = nums[:i] + nums[i+1:]
                for j in range(len(rest)):
                    for k in range(j + 1, len(rest)):
                        if abs((rest[j] + rest[k]) - target) > max(0.02 * target, 1):
                            mismatch_detected = True

        if mismatch_detected:
            found_inconsistency += 1
            flagged_total += 1
            if mentions_discrepancy:
                flagged_correct += 1
        elif mentions_discrepancy:
            # claims a discrepancy we couldn't independently verify -> counts as an (unverifiable) flag
            flagged_total += 1
            flagged_correct += 0.5

    if not objs:
        return 0.0
    if found_inconsistency == 0:
        return 0.5  # nothing to verify against; can't reward or penalize scrutiny directly
    return round(flagged_correct / max(flagged_total, 1), 3)
```

**What it does & why.** For every table and leaf figure, pulls out the raw numbers present and does a
cheap independent check for additive inconsistencies (do any two numbers sum to a third, within
tolerance, and fail to). Where an inconsistency is independently detectable, the function checks
whether the object's own notes/caveats actually name it (`reconcil`, `discrepan`, `does not match`,
etc.). Objects that catch and flag a real inconsistency score full credit; objects with a real,
unflagged inconsistency drag the score down; an artifact with no detectable inconsistencies at all
returns a neutral 0.5 (there's nothing to verify scrutiny against, but we still don't return N/A).

**Why it's hard to Goodhart.** Padding every table with a boilerplate "numbers reconciled" caveat only
helps when there's an actual, independently-detectable mismatch to match it to — bolting fake caveats
onto internally-consistent tables does nothing (no `mismatch_detected`, so the caveat text is never
credited). And suppressing real mismatches (rounding numbers so they superficially add up) is a
transcription-fidelity violation the brief explicitly forbids ("exact cell values, never rounded"),
so gaming this metric by smoothing over real discrepancies actively fights Metric 2/5's honesty checks.

---

## 4. Claim-Grounding Specificity & Breadth

**How it signals good science.** The whole point of `evidence/` is to be the thing every number in
`claims.md` traces back to. A README where claim links are dense, *specific* (varied per row, not one
copy-pasted claim ID stamped on every table/figure regardless of content), and where the rare unlinked
row is actually justified by its description (e.g., a PRISMA diagram that's methodologically relevant
but not itself evidence for a claim) reflects real per-object thinking about what each piece of
evidence supports — not indexing busywork.

**Compute function.**
```python
def claim_grounding_score(artifact: dict) -> float:
    """
    Assumes: artifact["readme"]["tables_rows"] / ["figures_rows"] each have "claims" (list[str],
    possibly empty) and "description" (str). An empty claims list is only excused by a
    sufficiently specific description explaining the object's role.
    """
    rows = artifact["readme"]["tables_rows"] + artifact["readme"]["figures_rows"]
    total = len(rows)
    if total == 0:
        return 0.0  # no evidence index at all

    linked = [r for r in rows if r.get("claims")]
    coverage = len(linked) / total

    claim_sets = [tuple(sorted(r["claims"])) for r in linked]
    distinct_ratio = (len(set(claim_sets)) / len(claim_sets)) if claim_sets else 0.0

    unlinked = [r for r in rows if not r.get("claims")]
    unjustified_unlinked = sum(1 for r in unlinked if len((r.get("description") or "").strip()) < 20)
    unlinked_penalty = (unjustified_unlinked / total)

    score = 0.5 * coverage + 0.3 * distinct_ratio + 0.2 * (1 - unlinked_penalty)
    return round(max(0.0, min(1.0, score)), 3)
```

**What it does & why.** Computes three components over the README index rows: (1) raw coverage — what
fraction of filed objects link to at least one claim; (2) specificity — among linked rows, what
fraction of distinct claim-ID combinations are unique (a low ratio means the same claim ID is being
stamped on many unrelated objects, a sign of lazy blanket-attribution); (3) an unlinked-but-justified
check — rows with no claim link only avoid penalty if their description is substantive enough to
explain why (short/generic descriptions on unlinked rows look like unexplained gaps, which the hard
constraint requires to be penalized, not waved through as N/A).

**Why it's hard to Goodhart.** Linking every object to some claim to maximize coverage tanks the
distinct-ratio term unless the claim IDs are genuinely varied — and inventing many distinct-looking but
spurious claim IDs to fake specificity would create claims with no support in `claims.md` (a
cross-artifact inconsistency outside this file's control, and orthogonal to the honesty checks in
Metric 2/3 which would still catch a table whose actual numbers don't match the claim it's stamped to).
Writing long unlinked descriptions purely to dodge the unjustified-unlinked penalty produces verbose
padding that a distinct completeness metric (Metric 1) doesn't reward and that a human reviewer (Level
2) would flag as filler.

---

## 5. Source-Locatability & Screenshot-Grounding Completeness

**How it signals good science.** Every table/figure is supposed to carry a precise source locator
(page/section) and a sibling screenshot, so a skeptical reader can go verify the transcription against
the original pixel-for-pixel. An evidence base that is dense in real objects, each with a specific page
citation, a real screenshot reference, and a non-boilerplate caption, is maximally falsifiable/
auditable — the opposite of an artifact that just asserts numbers with nothing to check them against.
Per the spec's own note, a paywalled/abstract-only source correctly produces near-zero grounding
capacity — this metric is built to score that as a real, low number, not a shrug.

**Compute function.**
```python
import re

def source_locatability_score(artifact: dict) -> float:
    """
    Assumes: every table/figure dict has "source" (str), "screenshot" (str filename), and
    "caption" (str). An artifact with zero filed tables/figures is scored 0.0, per the spec's
    own guidance that empty evidence bases represent a near-total loss of grounding capacity,
    not an inapplicable metric.
    """
    objs = list(artifact["tables"]) + list(flatten_figures(artifact["figures"]))
    if not objs:
        return 0.0

    total_pts = 0.0
    for o in objs:
        source = o.get("source") or ""
        screenshot = o.get("screenshot") or ""
        caption = (o.get("caption") or "").strip()

        page_pts = 1.0 if re.search(r"page\s*\d+", source, re.I) else (0.4 if re.search(r"§|section", source, re.I) else 0.0)
        shot_pts = 1.0 if screenshot.lower().endswith(".png") else 0.0
        caption_pts = 1.0 if len(caption) >= 15 else (0.3 if caption else 0.0)

        total_pts += (page_pts + shot_pts + caption_pts) / 3.0

    return round(total_pts / len(objs), 3)
```

**What it does & why.** For every filed table and leaf figure, scores three independently-checkable
grounding attributes: whether the source string pins down a page number (full credit) or only a
section (partial credit) or neither (zero); whether a screenshot filename is actually present; whether
the caption is substantive rather than a one-or-two-word placeholder. Averages across all objects, and
— critically — returns a hard `0.0` when there are no filed objects at all, matching the spec's explicit
statement that this is the artifact hit hardest by paywalled sources and that the correct read of that
situation is "near-total loss," not "not applicable."

**Why it's hard to Goodhart.** Inflating page/screenshot/caption metadata on objects that don't
actually correspond to real source content only helps this metric in isolation; it does nothing for
Metric 1 (which checks the *count* of objects against the source's own stated total, not just metadata
richness) and actively invites a Level-2 human/semantic check of whether the screenshot content matches
the claimed caption. Padding captions with generic boilerplate to clear the 15-character bar is caught
by Metric 4's specificity check when that same padding shows up as a non-distinguishing description on
an unlinked row.

---

## Combination

These five metrics are built to pull against each other. Ledger Reconciliation (1) rewards *coverage*
of the source's numbered objects, which only helps if those objects are real — Source-Locatability (5)
penalizes objects that lack a genuine page/screenshot anchor, so padding the count with thin filler
entries wins on (1) but loses on (5). Extraction Consistency (2) and Self-Scrutiny (3) both reward
*honest hedging* (admitting `digitized_estimate`/`low confidence`, flagging real arithmetic mismatches)
— but over-hedging everything to look cautious drags down Claim-Grounding specificity (4), since vaguely
hedged, undifferentiated entries tend to produce boilerplate claim links and boilerplate captions that
(4) and (5) both catch. Inflating claim-link coverage (4) to look thorough requires distinct, specific
claim IDs per object; faking that specificity produces claims not actually grounded in the tables'
own numbers, which (2)'s per-object consistency checks and (3)'s arithmetic checks are positioned to
catch when the numbers behind a claim don't hold up. In short: an artifact can win completeness only by
being real, can win honesty-labeling only by being consistent with what's actually shown, and can win
claim-density only by being specific — and each of those is separately, mechanically checkable against
the other metrics' inputs, so no single cheap edit improves all five scores at once.
