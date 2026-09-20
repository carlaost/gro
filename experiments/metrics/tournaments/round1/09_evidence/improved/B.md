## Changes from stage 1

- **Rewrote `self_scrutiny_score` (Metric 3) detector.** The stage-1 version flagged `mismatch_detected`
  whenever *any* pair of numbers in an object failed to sum to a third — true for almost any table with
  3+ numbers, so it branded nearly every honest artifact "inconsistent." It now only fires on a genuine
  **near-miss additive relationship**: an explicit `a+b+c+...` expression the compiler itself wrote out
  in prose (the actual PRISMA-style signal — `179+311+256+195` appearing verbatim, exactly as in the
  spec's worked example), or a table column explicitly labeled `total`/`sum`, whose sum lands in a narrow
  band that neither reconciles cleanly (≤1%/0.5, not a finding) nor is simply unrelated (>15%/5, noise —
  not a finding). Only the band in between — genuinely "should match, doesn't quite" — counts as a
  self-scrutiny target.
- **Replaced Metric 3's flat `0.5` mid-floor** for "nothing detectable to verify against." This isn't the
  hard constraint's literal "missing required input" case (the source data may just contain no arithmetic
  to catch), so it isn't zeroed outright — but it also no longer gets a free neutral score, since silence
  about scrutiny is not evidence that scrutiny happened. It now returns `0.6` only if the artifact shows
  *anchored* self-verification language elsewhere (a discrepancy-word caveat that itself names ≥2 numbers,
  not generic boilerplate), else `0.25` — a real, documented penalty for unprovable scrutiny.
- **Made Metric 2's normalization denominator explicit per object** instead of a blanket `3 * checks`
  constant. Each table/figure now carries its own `max_v` computed from which checks are actually
  reachable and mutually exclusive for that object's type (e.g. a table can trip at most one of the two
  `extraction_type` checks, never both), so the 2x "serious violation" weights are interpretable against
  a real ceiling rather than an arbitrary shared constant.
- **Fixed a cross-kind leak in Metric 1's named-skip accounting.** The stage-1 version summed *all*
  `Table N` / `Figure N` mentions into one shared `named_skips` count and credited it toward both the
  table-total and figure-total reconciliation checks — so a single named skipped table could spuriously
  help "explain" a gap in the figure count too. Skips are now partitioned by kind (`Table` vs `Figure`)
  before being applied to their respective check.

---

# Proposer #3 — metrics for `evidence/` (Stage 2, revised)

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

    # Partition named skips by kind so a skip named for one kind can't spuriously cover a
    # gap in the other kind's count (stage-1 bug: a single shared count did exactly that).
    named_table_skips = re.findall(r"\bTable\s+S?\d+[A-Za-z0-9.\-]*", note)
    named_figure_skips = re.findall(r"\bFigure\s+S?\d+[A-Za-z0-9.\-]*", note)

    score = 0.0
    checks = 0

    for filed_n, stated_list, named_skips in (
        (filed_tables, stated_table_totals, named_table_skips),
        (filed_figures, stated_figure_totals, named_figure_skips),
    ):
        checks += 1
        if not stated_list:
            continue  # no count stated for this kind -> 0 contribution
        stated = max(stated_list)  # take the largest plausibly-the-total number mentioned
        accounted = filed_n + len(set(named_skips))
        if stated == filed_n:
            score += 1.0   # filed == stated total, nothing missing
        elif accounted >= stated:
            score += 0.6   # gap covered by named skips of the SAME kind, but imprecisely attributable
        else:
            gap = stated - accounted
            score += max(0.0, 1.0 - gap / max(stated, 1))

    # Bonus signal: does the note affirmatively claim "none silently skipped" / name a reason?
    has_affirmation = bool(re.search(r"none.*skip|no.*silently|accounted for|not filed because|not present in", note, re.I))
    base = score / checks if checks else 0.0
    return round(min(1.0, base * (1.0 if has_affirmation else 0.7)), 3)
```

**What it does & why.** Pulls any numeric "N tables"/"N figures" claims out of the completeness note
via regex, and any explicit `Table N` / `Figure N` mentions, now split by kind into two separate
named-skip lists. Compares the stated total against what's actually filed, per kind. Full credit only
when they reconcile exactly; partial credit when a gap is explicitly covered by named skips *of that
same kind*; a further multiplier docks artifacts whose prose never actually asserts completeness in
words. An empty note is an automatic zero — the hard constraint requires this, since "no note" is worse
than a note that turns out to be slightly off.

**Why it's hard to Goodhart.** You could pad the note with a self-serving "N tables, all filed" — but
that's checked against the *actual filed count*, which the compiler can't fudge for free (making more
table files means doing more transcription work, which is real cost, not free text). Naming a skip of
one kind no longer helps paper over a gap in the other kind's count, closing the cross-kind leak that
made stage 1's version easier to game with a single well-placed "Figure 9" mention. Simply inflating the
stated total to make the ratio look bad-but-honest doesn't help either, since under-stating filed counts
triggers the "gap" penalty. The cheapest remaining attack — asserting a suspiciously round total that
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
    (None) are treated as violations, not as "not applicable." Each object's violations are
    normalized against that SAME object's explicit maximum-possible-violation weight (max_v),
    computed from which checks are actually reachable/mutually-exclusive for its type -- not a
    blanket constant -- so the 2x "serious violation" weights stay interpretable.
    """
    total_violations = 0.0
    total_max = 0.0

    for t in artifact["tables"]:
        v = 0
        max_v = 1  # exactly one of the three checks below can ever fire for a given table
        etype = t.get("extraction_type")
        if etype == "derived_subset" and not t.get("derived_from"):
            v += 1
        elif etype == "raw_table" and t.get("derived_from"):
            v += 1
        elif etype not in ("raw_table", "derived_subset"):
            v += 1
        total_violations += v
        total_max += max_v

    for fig in flatten_figures(artifact["figures"]):
        ftype = fig.get("figure_type")
        method = fig.get("extraction_method")
        conf = fig.get("reading_confidence")
        table = fig.get("data_table")
        trend = fig.get("trend_summary")

        v = 0
        max_v = 1  # method/confidence-missing check applies to every figure type

        if method is None or conf is None:
            v += 1

        if ftype == "quantitative_plot":
            # structural failure (2) and the method/confidence pair (1+1) are mutually exclusive:
            # structural requires table AND trend both absent; the confidence check requires a
            # table present. Ceiling is the larger of the two reachable paths.
            max_v += 3
            if not table and not trend:
                v += 2  # structural failure per spec: never neither
            else:
                flat = " ".join(str(c) for row in (table or []) for c in row)
                if method == "exact_from_labels" and "≈" in flat:
                    v += 1  # approx marker under an "exact" claim
                if method == "digitized_estimate" and table and "≈" not in flat:
                    v += 1  # suspiciously precise for an admitted estimate
                if conf == "low" and table and not trend:
                    v += 1  # unreachable alongside the `else` branch's own table-present premise
                             # only when trend also present; kept for schema robustness

        elif ftype in ("diagram", "qualitative_sample"):
            max_v += 3  # fabricated-table (2) and missing-visual-description (1) are independent
            if table:
                v += 2  # fabricated numeric table masquerading as non-quantitative
            if not fig.get("visual_description"):
                v += 1

        total_violations += v
        total_max += max_v

    return round(max(0.0, 1.0 - total_violations / max(total_max, 1)), 3)
```

**What it does & why.** Walks every table and every leaf figure (mixed figures expanded per-panel) and
checks label/content pairs against the spec's own honesty rules: derived vs raw tables must carry (or
omit) `derived_from` consistently; `quantitative_plot`s must have a table or a trend-summary fallback,
never neither; `exact_from_labels` numbers must not contain `≈`; `digitized_estimate` numbers that
never carry `≈` look over-precise for an admitted estimate; `low`-confidence figures with numeric
tables and no accompanying prose narrative are under-hedged; diagrams/qualitative samples must never
carry a numeric data table. Each object's violations are now divided by that object's own explicit
`max_v` — derived from which checks can actually co-occur for its type — rather than the stage-1
version's flat `3 * checks`, which didn't reflect that a table can trip at most one check while a
quantitative-plot figure can trip up to three.

**Why it's hard to Goodhart.** Any attempt to game one check tends to trip another: labeling everything
`digitized_estimate` to dodge the "no ≈ under exact" check now requires actually inserting `≈` markers
everywhere, which is directly visible and checkable against the screenshot/caption elsewhere, and makes
the artifact look uniformly low-confidence (hurting Metric 5's grounding-quality reading elsewhere, and
looking suspicious next to a `high`-reading-confidence claim). Conversely, labeling everything
`exact_from_labels` to look rigorous requires the numbers to actually be bare (no ≈), which for a truly
digitized/estimated figure means either doing the harder work of precise extraction or getting caught
by cross-referencing against Metric 3's arithmetic checks below when the "exact" numbers don't add up.
The explicit per-object denominator also closes a smaller Goodhart path: an artifact couldn't previously
benefit from diluting its violation count by mixing in many trivially-clean tables (which each only ever
contributed to a shared `3x` denominator regardless of how many checks they could even fail); each
object's ceiling is now tied to what it could actually have gotten wrong.

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

_SUM_EXPR_RE = re.compile(r"\d[\d,]*(?:\.\d+)?(?:\s*\+\s*\d[\d,]*(?:\.\d+)?){1,}")
_DISCREPANCY_RE = re.compile(r"reconcil|discrepan|does not match|do not match|doesn'?t match|inconsist", re.I)

def _exact_tol(target: float) -> float:
    return max(0.01 * abs(target), 0.5)   # essentially reconciles (rounding-level); not a finding

def _near_tol(target: float) -> float:
    return max(0.15 * abs(target), 5.0)   # beyond this, numbers are unrelated, not a near miss

def _object_text_and_numbers(obj: dict, kind: str) -> tuple[str, list[float]]:
    """Collects all free text and all numbers belonging to one table or leaf figure."""
    if kind == "table":
        table = obj.get("body", [])
        text_blobs = list(obj.get("notes", [])) + [obj.get("caption", "") or ""]
    else:
        table = obj.get("data_table") or (obj.get("visual_description") or {}).get("transcribed_numbers") or []
        text_blobs = (
            [obj.get("trend_summary") or "", obj.get("caption") or ""]
            + list(obj.get("caveats", []))
            + [str(v) for v in (obj.get("visual_description") or {}).values()]
        )
    text = " ".join(text_blobs)
    table_numbers = [n for row in table for c in row for n in _numbers_in(c if isinstance(c, str) else str(c))]
    return text, table_numbers + _numbers_in(text)

def _near_miss_from_written_sums(text: str, numbers: list[float]) -> list[tuple[float, float]]:
    """
    Only counts a "finding" when the compiler itself wrote out an explicit addition (e.g.
    "179+311+256+195", verbatim as in the spec's own PRISMA example) AND some other stated
    number in the same object is a genuine near miss for that sum: neither an exact match
    (fine, nothing to flag) nor unrelated (>15%/5 off -- not plausibly the same quantity).
    """
    candidates = []
    for m in _SUM_EXPR_RE.finditer(text):
        addends = _numbers_in(m.group(0))
        if len(addends) < 2:
            continue
        s = sum(addends)
        others = [n for n in numbers if n not in addends]
        if not others:
            continue
        closest = min(others, key=lambda n: abs(n - s))
        diff = abs(closest - s)
        if _exact_tol(s) < diff <= _near_tol(s):
            candidates.append((s, closest))
    return candidates

def _near_miss_from_total_columns(body: list) -> list[tuple[float, float]]:
    """Checks any header column literally labeled total/sum against that row's other numeric cells."""
    if not body or len(body) < 2:
        return []
    header = body[0]
    total_idx = [i for i, h in enumerate(header) if re.search(r"total|sum", str(h), re.I)]
    candidates = []
    for row in body[1:]:
        for ti in total_idx:
            if ti >= len(row):
                continue
            total_vals = _numbers_in(row[ti])
            if not total_vals:
                continue
            total_val = total_vals[0]
            component_vals = [n for i, c in enumerate(row) if i != ti for n in _numbers_in(c)]
            if len(component_vals) < 2:
                continue
            s = sum(component_vals)
            diff = abs(s - total_val)
            if _exact_tol(total_val) < diff <= _near_tol(total_val):
                candidates.append((s, total_val))
    return candidates

def self_scrutiny_score(artifact: dict) -> float:
    """
    Assumes: table/figure "notes"/"caveats" are free-text lists, and body/data_table cells are
    strings possibly containing arithmetic-checkable quantities. Findings are restricted to
    genuine near-miss additive relationships anchored to something the compiler itself wrote
    (an explicit sum expression, or a column explicitly labeled total/sum) -- not brute-force
    pairwise combinatorics over incidental numbers, which flags almost any table with 3+ numbers.
    """
    flagged_correct = 0.0
    flagged_total = 0
    found_inconsistency = 0
    any_object = False
    anchored_verification_seen = False

    for t in artifact["tables"]:
        any_object = True
        text, numbers = _object_text_and_numbers(t, "table")
        candidates = _near_miss_from_written_sums(text, numbers) + _near_miss_from_total_columns(t.get("body", []))
        notes_text = " ".join(t.get("notes", [])).lower()
        mentions_discrepancy = bool(_DISCREPANCY_RE.search(notes_text))
        if mentions_discrepancy and len(_numbers_in(notes_text)) >= 2:
            anchored_verification_seen = True
        if candidates:
            found_inconsistency += 1
            flagged_total += 1
            flagged_correct += 1.0 if mentions_discrepancy else 0.0

    for fig in flatten_figures(artifact["figures"]):
        any_object = True
        text, numbers = _object_text_and_numbers(fig, "figure")
        candidates = _near_miss_from_written_sums(text, numbers)
        caveats_text = " ".join(fig.get("caveats", [])).lower()
        mentions_discrepancy = bool(_DISCREPANCY_RE.search(caveats_text))
        if mentions_discrepancy and len(_numbers_in(caveats_text)) >= 2:
            anchored_verification_seen = True
        if candidates:
            found_inconsistency += 1
            flagged_total += 1
            flagged_correct += 1.0 if mentions_discrepancy else 0.0

    if not any_object:
        return 0.0  # empty evidence base: penalized here too, consistent with Metric 5's read of it

    if found_inconsistency == 0:
        # Not the hard constraint's literal "missing required input" case -- the source data may
        # simply contain no arithmetic to catch. But silence about verification is not proof that
        # verification happened, so this is not a free neutral score either: reward only if the
        # artifact shows ANCHORED self-verification elsewhere (discrepancy language tied to >=2
        # real numbers, not generic boilerplate); otherwise this is a genuine, documented penalty
        # for unprovable scrutiny, not a shrug.
        return 0.6 if anchored_verification_seen else 0.25

    return round(flagged_correct / max(flagged_total, 1), 3)
```

**What it does & why.** For every table and leaf figure, looks only for near-miss additive
relationships the compiler itself asserted — an explicit `a+b+c+...` expression in its own prose (the
exact PRISMA pattern from the spec), or a table column explicitly labeled `total`/`sum` — and checks
whether that written sum is a genuine near miss against another stated number: not reconciled (fine),
not unrelated (noise), but caught in the narrow band where a real discrepancy plausibly exists. Where
one is found, the function checks whether the object's own notes/caveats actually name it. Objects that
catch and flag a real near-miss score full credit; a real, unflagged one drags the score down. When
nothing near-miss is detectable anywhere in the artifact, the score is `0.6` if anchored verification
language exists elsewhere (evidence the compiler does perform this kind of check), else a real `0.25`
penalty — never a free-pass neutral value and never N/A.

**Why it's hard to Goodhart.** Restricting findings to sums the compiler itself wrote out (rather than
brute-force number combinatorics) removes the stage-1 loophole where nearly any table full of unrelated
numbers scored as "inconsistent," which made the metric noise rather than signal and gave no lever for
honest improvement. Padding every table with a boilerplate "numbers reconciled" caveat only helps when
there's an actual, independently-detectable near miss to match it to — bolting fake caveats onto
internally-consistent tables does nothing (no candidate is ever generated, so the caveat text is never
credited). And suppressing real mismatches (rounding numbers so they superficially add up) is a
transcription-fidelity violation the brief explicitly forbids ("exact cell values, never rounded"), so
gaming this metric by smoothing over real discrepancies actively fights Metric 2/5's honesty checks.
Writing vague "please trust our scrutiny" prose without ever anchoring it to real numbers no longer buys
the higher no-finding floor either, since `anchored_verification_seen` requires ≥2 real numbers
alongside the discrepancy language, not just the word "reconciled" on its own.

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

These five metrics are still built to pull against each other, and the Stage-2 fixes tighten rather
than loosen that tension. Ledger Reconciliation (1) rewards *coverage* of the source's numbered objects,
which only helps if those objects are real — Source-Locatability (5) penalizes objects that lack a
genuine page/screenshot anchor, so padding the count with thin filler entries wins on (1) but loses on
(5); (1) also no longer lets a named skip of one kind quietly cover a gap in the other kind's count.
Extraction Consistency (2) and Self-Scrutiny (3) both reward *honest hedging* (admitting
`digitized_estimate`/`low confidence`, flagging real arithmetic mismatches) — but over-hedging everything
to look cautious drags down Claim-Grounding specificity (4), since vaguely hedged, undifferentiated
entries tend to produce boilerplate claim links and boilerplate captions that (4) and (5) both catch.
(3) now only rewards flagging near-misses that are anchored to something the compiler itself wrote (an
explicit sum, a labeled total column), so boilerplate "verified" caveats bolted onto clean tables buy
nothing, and the metric can no longer be gamed simply by having lots of unrelated numbers in a table.
Inflating claim-link coverage (4) to look thorough requires distinct, specific claim IDs per object;
faking that specificity produces claims not actually grounded in the tables' own numbers, which (2)'s
per-object consistency checks and (3)'s anchored arithmetic checks are positioned to catch when the
numbers behind a claim don't hold up. In short: an artifact can win completeness only by being real, can
win honesty-labeling only by being consistent with what's actually shown, and can win claim-density only
by being specific — and each of those is separately, mechanically checkable against the other metrics'
inputs, so no single cheap edit improves all five scores at once.
</content>
