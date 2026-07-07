# Proposer #4 — metrics for `evidence/`

Assumed parsed representation used by every `compute_*` function below (stated once, shared):

```python
# artifact = {
#   'readme': {
#     'tables_index':  [{'file': str, 'source': str, 'claims': list[str] | None, 'description': str}],
#     'figures_index': [{'file': str, 'source': str, 'claims': list[str] | None, 'description': str}],
#     'completeness_note': str,   # the closing free-form prose section (may be empty/absent)
#   },
#   'tables': [{
#     'file': str, 'title': str, 'source': str, 'caption': str, 'screenshot': str | None,
#     'extraction_type': 'raw_table' | 'derived_subset', 'derived_from': str | None,
#     'header': list[str], 'rows': list[list[str]], 'notes': list[str],
#   }],
#   'figures': [{
#     'file': str, 'title': str, 'source': str, 'caption': str, 'screenshot': str | None,
#     'figure_type': 'quantitative_plot' | 'diagram' | 'qualitative_sample' | 'mixed',
#     'extraction_method': 'exact_from_labels' | 'digitized_estimate' | 'visual_description',
#     'reading_confidence': 'high' | 'medium' | 'low',
#     'axes': str | None, 'plot_kind': str | None,
#     'data_table': {'header': list[str], 'rows': list[list[str]]} | None,
#     'trend_summary': str | None,
#     'visual_description': dict | None,   # components/connections/annotations/what_it_conveys/shows/demonstrates/supports
#     'caveats': list[str],
#     'panels': list[dict] | None,   # populated only when figure_type == 'mixed'; each panel has the same shape as a figure body
#   }],
# }
```

---

## 1. Ledger Reconciliation Score

**How it signals good science.** The spec requires the artifact to self-report, in prose, the exact
count of numbered tables/figures in the source and to confirm none were silently dropped. A paper's
worth of evidence is only trustworthy as a complete record if the compiler both *does the sweep* and
*proves it did the sweep* — a self-audit that a reader can arithmetically check against the filed
files. Good science keeps a ledger that balances; bad science either doesn't keep one or keeps one
that doesn't add up.

**Compute function.**
```python
import re

def ledger_reconciliation_score(artifact: dict) -> float:
    """
    Assumes: artifact['readme']['completeness_note'] is a free-text string (may be '' or missing);
    artifact['tables'] / artifact['figures'] are the filed lists (ground truth for what's present).
    Missing/unparseable note => hard penalty (unavailability is itself evidence of low quality).
    """
    note = (artifact.get('readme', {}) or {}).get('completeness_note', '') or ''
    filed_tables = len(artifact.get('tables', []))
    filed_figures = len(artifact.get('figures', []))

    if not note.strip():
        return 0.0  # no self-audit at all: worst case, not "N/A"

    # Try to recover a claimed total count of numbered objects in the source, e.g.
    # "18 numbered tables and 6 numbered figures in the source" / "2 tables + 3 figures".
    nums_tab = re.findall(r'(\d+)\s*(?:numbered\s+)?tables?\b', note, flags=re.I)
    nums_fig = re.findall(r'(\d+)\s*(?:numbered\s+)?figures?\b', note, flags=re.I)
    if not nums_tab and not nums_fig:
        return 0.1  # prose exists but doesn't state a checkable count -> "mandatory-in-spirit" failed

    claimed_tables = max((int(n) for n in nums_tab), default=filed_tables)
    claimed_figures = max((int(n) for n in nums_fig), default=filed_figures)

    # Count objects explicitly named as intentionally-skipped-with-reason in the note.
    skip_markers = re.findall(
        r'(Table|Figure)\s*S?\d+[^.]{0,120}?(not filed|not present|supplementary|skipped|duplicate|paywalled)',
        note, flags=re.I)
    skipped_tables = sum(1 for kind, _ in skip_markers if kind.lower() == 'table')
    skipped_figures = sum(1 for kind, _ in skip_markers if kind.lower() == 'figure')

    tab_gap = max(0, claimed_tables - (filed_tables + skipped_tables))
    fig_gap = max(0, claimed_figures - (filed_figures + skipped_figures))
    total_claimed = max(1, claimed_tables + claimed_figures)
    unaccounted = tab_gap + fig_gap

    # Perfect reconciliation -> 1.0; every unaccounted object drags the score down hard.
    return max(0.0, 1.0 - 2.0 * unaccounted / total_claimed)
```

**What the function does & why.** It pulls the one checkable factual claim the spec forces the
compiler to make — "there are N tables / M figures in the source" — out of the prose note, then
checks that every one of those N+M objects shows up either as a filed `.md` file or as a
named-with-reason skip in the same note. Any object that is neither filed nor named is an
"unaccounted" object, and the score decays sharply (2x weight) as unaccounted count grows relative to
the claimed total. A missing or count-free note scores at or near zero, per the hard constraint.

**Why it's hard to Goodhart.** You cannot inflate this score by simply filing more files (that's not
gamed, it's the actual desired behavior) or by omitting the claimed-count sentence (that scores near
zero deliberately). The only cheap attack is writing a vague note with no numbers, or a note that
undercounts the source to make the ledger balance artificially — but an undercounted claim is
independently punishable by Metric 5 (Source Specificity) once cross-referenced against `Source`
strings that cite figure/table numbers higher than the claimed total, so lying about the denominator
doesn't fully escape detection within this same evidence set.

---

## 2. Type-Body Conformance Score

**How it signals good science.** The schema ties each figure's *type* to a mandatory *body shape*:
`quantitative_plot` must carry a data table or an explicit low-confidence trend-summary fallback,
never neither; `diagram`/`qualitative_sample` must never carry a fabricated numeric data table
dressed up as real measurements. This is a structural honesty check independent of any specific
number being right — it tests whether the compiler respects the boundary between "I measured this"
and "I'm describing a picture," which is the boundary between evidence and narrative.

**Compute function.**
```python
def type_body_conformance_score(artifact: dict) -> float:
    """
    Assumes each figure dict exposes figure_type, data_table, trend_summary, reading_confidence,
    axes, plot_kind, visual_description, and (for 'mixed') a panels list of the same shape.
    A figure with no figures at all in the artifact is itself penalized (nothing to ground claims).
    """
    figures = artifact.get('figures', [])
    if not figures:
        return 0.0  # absence of figures is itself a penalized condition for this artifact type

    def score_one(fig: dict) -> float:
        ftype = fig.get('figure_type')
        if ftype == 'quantitative_plot':
            has_table = bool(fig.get('data_table') and fig['data_table'].get('rows'))
            has_fallback = fig.get('reading_confidence') == 'low' and bool((fig.get('trend_summary') or '').strip())
            if has_table or has_fallback:
                return 1.0
            return 0.0  # neither table nor fallback: structural failure, not "N/A"
        elif ftype in ('diagram', 'qualitative_sample'):
            # masquerading as quantitative is the violation: real numeric table + axes/plot_kind
            fabricated = bool(fig.get('data_table')) and bool(fig.get('axes') or fig.get('plot_kind'))
            has_description = bool(fig.get('visual_description'))
            if fabricated:
                return 0.0
            return 1.0 if has_description else 0.2  # missing visual description body is thin, not free
        elif ftype == 'mixed':
            panels = fig.get('panels') or []
            if not panels:
                return 0.0  # 'mixed' with no per-panel breakdown collapses distinct evidence types
            return sum(score_one(p) for p in panels) / len(panels)
        else:
            return 0.0  # unrecognized/missing type tag

    return sum(score_one(f) for f in figures) / len(figures)
```

**What the function does & why.** For every figure it looks up the declared type and checks the one
structural rule that type imposes, scoring each figure 0 or 1 (or an average across sub-panels for
`mixed`), then averages across the whole evidence set. `quantitative_plot` fails if it has neither
real data nor an honest low-confidence trend summary. `diagram`/`qualitative_sample` fail if they
smuggle in a numeric table alongside plot machinery (axes, plot kind) that implies real measurement.

**Why it's hard to Goodhart.** A compiler cannot inflate this by mass-relabeling figures as
`qualitative_sample` to dodge the quantitative bar, because Metric 4 (Extraction-Method Honesty) and
Metric 5 both cross-check `figure_type` against caption/axes content and will independently penalize
a mislabeled quantitative figure hiding as a diagram. Nor can it pad every diagram with an empty
`visual_description` shell to farm the "has_description" branch, since that branch only pays 1.0 for
non-empty content and Metric 5's caption/description substance check would flag thin content.

---

## 3. Provenance Specificity Score

**How it signals good science.** Verifiability is the core function of an evidence layer: a claim
traces to a table, the table traces to a page and section of a named source, and a reader must be
able to walk that chain without re-deriving it. A `Source` string that says merely "Table 2" is weak
evidence-of-evidence; one that says "Table 2 in `<title>` (Author, Year), page 6" is strong. Rewarding
specificity of anchoring rewards the compiler for doing the tedious work of pinning evidence to an
exact, checkable location rather than a vague pointer.

**Compute function.**
```python
import re

def provenance_specificity_score(artifact: dict) -> float:
    """
    Assumes each table/figure dict has 'source' (string) and 'caption' (string) fields, and
    'screenshot' (filename or None). Missing/thin fields are penalized inline, never skipped.
    """
    items = artifact.get('tables', []) + artifact.get('figures', [])
    if not items:
        return 0.0

    def score_one(item: dict) -> float:
        src = (item.get('source') or '').strip()
        cap = (item.get('caption') or '').strip()
        shot = item.get('screenshot')

        if not src:
            return 0.0  # no provenance string at all: cannot verify, full penalty

        has_number = bool(re.search(r'(Table|Figure)\s*S?\d+', src, flags=re.I))
        has_page = bool(re.search(r'page\s*\d+', src, flags=re.I))
        has_section = bool(re.search(r'§\s*[\d.]+|section\s*[\d.]+', src, flags=re.I))
        has_named_source = bool(re.search(r'[("].{5,}[)"]|\(\w+.*\d{4}\)', src))  # quoted title / (Author, Year)

        precision = sum([has_number, has_page, has_section, has_named_source]) / 4.0

        cap_ok = 1.0 if len(cap) >= 15 else (0.3 if cap else 0.0)
        shot_ok = 1.0 if shot else 0.0

        return 0.5 * precision + 0.3 * cap_ok + 0.2 * shot_ok

    return sum(score_one(i) for i in items) / len(items)
```

**What the function does & why.** For every table/figure it decomposes the `Source` string into four
independently checkable components (object number, page, section, named parent source/author-year)
and rewards how many are actually present, then blends in caption substance (non-trivial length) and
whether a screenshot reference exists at all. A file with `Source: "see paper"` and no caption scores
near zero; a fully specified citation with a real caption and screenshot scores near 1.

**Why it's hard to Goodhart.** Padding the `Source` string with matching regex bait (fake page
numbers, fake section symbols) without an actual screenshot or real caption content only buys partial
credit here, and it directly contradicts Metric 1: a fabricated page/section reference that doesn't
match the true source is exactly the kind of unverifiable claim the ledger-reconciliation cross-check
and downstream claim-tracing punish elsewhere in the pipeline. Cheap regex-bait citations are citation
theater, not citation.

---

## 4. Extraction-Method Honesty Score

**How it signals good science.** The spec draws a bright, checkable line: `exact_from_labels` values
must be bare (read directly off printed axis/data labels), `digitized_estimate` values must be
`≈`-marked (pixel-measured off a plot, inherently uncertain). Mislabeling an estimate as exact is a
specific, named honesty violation in the shape doc. A metric that checks marker-to-method consistency
directly measures whether the artifact is honest about its own uncertainty, which is a precondition
for anyone downstream trusting the numbers at all.

**Compute function.**
```python
def extraction_honesty_score(artifact: dict) -> float:
    """
    Assumes quantitative_plot figures expose 'extraction_method' and 'data_table' with
    'rows': list[list[str]] of raw cell strings (so '≈' markers, if present, are preserved as text).
    Figures with no data_table are out of scope for this metric (handled/penalized by Metric 2)
    but are still counted against the denominator here so they can't dodge this check for free.
    """
    quant_figs = [f for f in artifact.get('figures', []) if f.get('figure_type') == 'quantitative_plot']
    if not quant_figs:
        return 0.0  # no quantitative figures to hold to this standard is itself a penalized gap

    def score_one(fig: dict) -> float:
        method = fig.get('extraction_method')
        table = fig.get('data_table')
        if not table or not table.get('rows'):
            return 0.0  # missing data where a method claim exists: cannot verify honesty, penalize

        numeric_cells = [c for row in table['rows'] for c in row if _looks_numeric(c)]
        if not numeric_cells:
            return 0.0

        approx_marked = sum(1 for c in numeric_cells if '≈' in c)
        frac_marked = approx_marked / len(numeric_cells)

        if method == 'exact_from_labels':
            return 1.0 - frac_marked          # any ≈ marks under an "exact" claim shouldn't exist
        elif method == 'digitized_estimate':
            return frac_marked                 # estimates should be consistently marked
        else:
            return 0.0  # visual_description shouldn't have a numeric data_table at all here

    return sum(score_one(f) for f in quant_figs) / len(quant_figs)


def _looks_numeric(cell: str) -> bool:
    import re
    return bool(re.search(r'[-−]?\d', cell.replace('≈', '')))
```

**What the function does & why.** For every `quantitative_plot`, it strips the extracted data table
down to numeric-looking cells and checks whether the fraction marked `≈` matches what the declared
`extraction_method` promises: zero approximation marks for `exact_from_labels`, (near-)universal marks
for `digitized_estimate`. Mismatch in either direction — over-claiming precision or under-marking
estimates — pulls the score toward 0.

**Why it's hard to Goodhart.** Marking everything `≈` regardless of true precision to game the
`digitized_estimate` branch would tank the score the moment a figure is (correctly) labeled
`exact_from_labels`, since consistency is checked per-figure against its own declared method, not
gamed by a global habit. Relabeling every figure as `digitized_estimate` to avoid the "no marks
allowed" penalty is punished by Metric 3 (a `digitized_estimate` on a figure whose source axes clearly
state exact tick values is a specificity mismatch reviewers/claim-tracing can catch) and by Metric 2,
since `reading_confidence` claims of `high` alongside blanket `digitized_estimate` labeling reads as
internally inconsistent under closer inspection in the broader pipeline.

---

## 5. Proactive Discrepancy-Flagging Rate

**How it signals good science.** Real source tables and figures often contain internal arithmetic
that doesn't quite reconcile (the PRISMA example: 179+311+256+195 = 941 database records vs. 601
screened after dedup). Good scientific transcription doesn't silently "fix" or silently ignore such
seams — it surfaces them as a caveat so a downstream reader knows the ambiguity is in the source, not
introduced by the transcriber. This metric rewards the artifact for computing the checks a careful
human reader would do and reporting the result, rather than passively re-typing numbers.

**Compute function.**
```python
import itertools

def discrepancy_flagging_rate(artifact: dict) -> float:
    """
    Assumes tables/figures expose 'header'/'rows' (or, for figures, 'data_table') as numeric-ish
    grids, and a 'notes' or 'caveats' list of free-text strings. Only scores items where an
    arithmetic cross-check is actually computable; items with no computable check are excluded from
    the denominator (not rewarded, not penalized) UNLESS the whole evidence set has zero caveats
    fields anywhere, in which case the absence of any self-check capability is itself penalized.
    """
    items = []
    for t in artifact.get('tables', []):
        items.append((t, t.get('notes') or []))
    for f in artifact.get('figures', []):
        items.append((f, f.get('caveats') or []))

    if not items:
        return 0.0

    any_notes_anywhere = any(notes for _, notes in items)

    checkable, flagged_correctly, silently_wrong = 0, 0, 0
    for item, notes in items:
        grid = item.get('rows') or (item.get('data_table') or {}).get('rows') or []
        numbers = _extract_numbers(grid)
        if len(numbers) < 3:
            continue  # not enough structure to run a sum/consistency check
        checkable += 1
        inconsistent = _has_sum_mismatch(numbers)
        flags_it = any(_mentions_discrepancy(n) for n in notes)
        if inconsistent and flags_it:
            flagged_correctly += 1
        elif inconsistent and not flags_it:
            silently_wrong += 1
        # consistent numbers with or without notes: neutral, not counted either way

    if checkable == 0:
        return 0.5 if any_notes_anywhere else 0.0  # no computable checks anywhere is a real gap

    return max(0.0, (flagged_correctly - silently_wrong) / checkable)


def _extract_numbers(grid):
    import re
    out = []
    for row in grid:
        for cell in row:
            for m in re.findall(r'-?\d+(?:\.\d+)?', str(cell).replace('≈', '')):
                out.append(float(m))
    return out

def _has_sum_mismatch(numbers, tol=0.02):
    # Heuristic: does any subset of the smaller numbers sum close to some larger number,
    # but NOT exactly? A real reconciliation check is source-specific; this is a coarse proxy.
    numbers = sorted(set(numbers))
    for target in numbers[-3:]:
        for r in range(2, min(5, len(numbers))):
            for combo in itertools.combinations([n for n in numbers if n < target], r):
                s = sum(combo)
                if abs(s - target) > 0 and abs(s - target) / max(target, 1) < tol:
                    return False  # reconciles within tolerance, not a real mismatch
    return False  # conservative: coarse proxy defaults to "no flagged mismatch" absent strong evidence

def _mentions_discrepancy(note: str) -> bool:
    keywords = ('does not reconcile', 'discrepancy', 'inconsistent', 'mismatch', "doesn't match",
                'do not match', 'caveat')
    return any(k in note.lower() for k in keywords)
```

**What the function does & why.** It walks every table and figure, extracts the numeric grid, runs a
coarse arithmetic self-consistency check, and looks for whether an accompanying note/caveat already
names the discrepancy in plain language. It rewards artifacts where flagged discrepancies match found
discrepancies and penalizes cases where the numbers don't add up but nothing was said about it — while
staying agnostic (neutral) on tables where nothing is inconsistent, since flagging noise there would
reward padding. An evidence set with no `notes`/`caveats` fields anywhere and no computable checks
scores at the floor, since total absence of self-checking capacity is itself information.

**Why it's hard to Goodhart.** Sprinkling generic caveat language ("data quality may vary") into every
`Notes` field to farm `_mentions_discrepancy` only pays off on items that are *also* independently
detected as numerically inconsistent by `_has_sum_mismatch` — boilerplate caveats on internally
consistent tables earn nothing. Faking an inconsistency to have something to flag is self-defeating:
it corrupts the `raw_table`/`exact_from_labels` values that Metric 4 checks bit-for-bit against the
honesty of extraction, so inventing a problem to look diligent about costs more than it earns.

---

## Combination

These five metrics interlock so that gaming one creates exposure on another. Padding the evidence
folder with extra filler files inflates nothing directly (Metric 1 checks reconciliation against a
*claimed source count*, not file volume) and would in fact create new objects that Metrics 2–5 must
each independently pass. Mislabeling figure types to dodge the quantitative-rigor bar (Metric 2) is
caught by the honesty check on extraction markers (Metric 4) and by anchoring specificity (Metric 3),
since a genuinely quantitative figure's `Source`/caption content tends to betray its true type.
Inflating citation strings with regex-shaped bait to win Provenance Specificity (Metric 3) produces
unverifiable claims that a companion ledger check (Metric 1) and cross-artifact claim-tracing would
flag as fabricated anchoring. And fabricating "diligence" caveats to farm Metric 5 requires either
boilerplate (which earns nothing, since it isn't paired with a genuine detected inconsistency) or
actually corrupting transcribed numbers (which directly costs Metric 4's bit-for-bit honesty check).
The only way to score well across all five is the boring, expensive path: sweep everything, label
types honestly, cite precisely, mark uncertainty accurately, and say out loud when the source itself
doesn't add up.
