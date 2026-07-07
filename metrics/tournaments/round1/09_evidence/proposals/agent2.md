# Proposer #2 — metrics for `evidence/`

## 1. Evidence Ledger Completeness & Accounting Rigor

**How it signals good science.** The `evidence/` layer's entire epistemic function is to be a
*systematic sweep*: every numbered table/figure in the source is either filed or explicitly
named-and-reasoned in `README.md`. A team that quietly files only the tables that support its
narrative (and drops the inconvenient ones) is doing selective reporting, not grounding. The
presence, specificity, and internal reconciliation of the completeness note is a direct, checkable
proxy for whether the sweep was actually systematic.

**Compute function.**
```python
import re

def evidence_ledger_completeness(parsed):
    """
    Assumes a parsed dict with:
      parsed['readme']['completeness_note']: str — the prose "Completeness note / Supplementary
          objects" section of evidence/README.md.
      parsed['tables']: list of filed table records (evidence/tables/*.md).
      parsed['figures']: list of filed figure records (evidence/figures/*.md).
    """
    note = (parsed.get('readme', {}).get('completeness_note') or '').strip()
    if not note:
        return 0.0  # no accounting at all: worst case, not "N/A"

    filed_tables = len(parsed.get('tables', []))
    filed_figures = len(parsed.get('figures', []))

    total_matches = re.findall(r'(\d+)\s+(tables?|figures?)', note.lower())
    skip_matches = re.findall(r'(table|figure)\s+s?\d+[a-z]?\s*[\(\-:]', note.lower())
    reasoned_skips = re.findall(r'(table|figure)\s+s?\d+[a-z]?\s*[\(\-:][^\.]{10,}', note.lower())

    score = 0.4 if total_matches else 0.1  # explicit counts stated at all?

    stated = {}
    for n, kind in total_matches:
        key = 'table' if kind.startswith('table') else 'figure'
        stated[key] = max(stated.get(key, 0), int(n))

    reconciled = True
    if 'table' in stated and filed_tables + sum(1 for s in skip_matches if s[0] == 'table') < stated['table']:
        reconciled = False
    if 'figure' in stated and filed_figures + sum(1 for s in skip_matches if s[0] == 'figure') < stated['figure']:
        reconciled = False
    score += 0.4 if reconciled else 0.0

    if skip_matches:
        score += 0.2 * (len(reasoned_skips) / len(skip_matches))
    else:
        score += 0.2  # nothing skipped, nothing to reason about

    return round(min(score, 1.0), 3)
```

**What the function does & why.** It reads the mandatory-in-spirit prose note, requires it to state
exact numbered-object counts (not "most tables were filed"), checks that filed-count plus
named-skip-count reconciles against any stated total, and rewards skips only when each carries a
concrete reason rather than a bare mention. An empty or missing note scores zero — silence about
completeness is treated as a completeness failure, per the hard constraint.

**Why it's hard to Goodhart.** You cannot pass this by simply filing more objects (filing garbage
tables would fail metrics 2/3 below on structural and extraction grounds), and you cannot pass it by
writing a vague reassuring note (the regex requires actual numbers and per-item reasons). Inflating
the stated total to make reconciliation trivial is self-defeating: it raises the bar the filed+skip
count must clear.

---

## 2. Structural Fallback & Type Discipline

**How it signals good science.** The schema is strict about failure modes: a `quantitative_plot`
must carry either a real data table or an honest, low-confidence trend summary — never neither.
A `diagram`/`qualitative_sample` must never carry a fabricated numeric table (Critical Rule
violation per the shape doc). Respecting these boundaries is evidence the transcriber represented
what the source actually showed rather than manufacturing convenient structure.

**Compute function.**
```python
import re

def is_substantive_trend(text):
    if not text or len(text.strip()) < 60:
        return False
    numerics = re.findall(r'-?\d+\.?\d*', text)
    entities = set(re.findall(r'\b[A-Z][a-zA-Z0-9_]{2,}\b', text))
    return len(numerics) >= 1 and len(entities) >= 2  # not generic filler

def structural_fallback_discipline(parsed):
    """
    Assumes each figure record has: figure_type, data_table (list[dict] or None),
    trend_summary (str or None), visual_description (dict or None), and — only for
    figure_type == 'mixed' — a 'panels' list of sub-records with the same fields.
    """
    def score_leaf(fig):
        ftype = fig.get('figure_type')
        has_table = bool(fig.get('data_table'))
        has_trend = is_substantive_trend(fig.get('trend_summary'))
        has_visual = bool(fig.get('visual_description'))
        if ftype == 'quantitative_plot':
            return 1.0 if (has_table or has_trend) else 0.0
        if ftype in ('diagram', 'qualitative_sample'):
            if has_table:
                return 0.0  # fabricated numeric table in a non-quantitative type
            return 1.0 if has_visual else 0.2
        return 0.5

    leaves = []
    for fig in parsed.get('figures', []):
        if fig.get('figure_type') == 'mixed':
            panels = fig.get('panels') or []
            leaves.extend([0.0] if not panels else [score_leaf(p) for p in panels])
        else:
            leaves.append(score_leaf(fig))
    return round(sum(leaves) / len(leaves), 3) if leaves else 0.0
```

**What the function does & why.** For each filed figure (each panel, if `mixed`), it checks the
type-specific structural requirement from the shape doc and scores 0 on any violation: a
quantitative plot with neither table nor real trend summary, or a diagram/sample smuggling in a
numeric table. `is_substantive_trend` requires actual numbers and named entities so a one-line
placeholder sentence doesn't count as compliance. No filed figures at all scores 0 — thin evidence
is penalized, not skipped.

**Why it's hard to Goodhart.** Pasting a generic trend sentence fails the substance check
(no numbers/entities). Mislabeling a figure's type to dodge the rule (e.g. calling a real
quantitative plot a "diagram" so no table is required) directly collides with Metric 3's
extraction-method cross-check and with claim linkage expectations, since a plot claimed to be a
mere diagram won't plausibly support the quantitative claims listed for it elsewhere.

---

## 3. Extraction-Method Honesty

**How it signals good science.** The schema draws a bright honesty line: `exact_from_labels` means
literal numbers off the source; `digitized_estimate` means a visually-read approximation and must
carry `≈` markers; `visual_description` means no numeric table exists at all. Mislabeling any of
these — claiming exactness for a guess, or attaching numbers to a pure description — is a specific,
checkable epistemic violation, not a stylistic choice.

**Compute function.**
```python
import re

def extraction_honesty(parsed):
    """
    Assumes figure records carry extraction_method, reading_confidence, and data_table
    (list of row-dicts whose values are literal strings, so a '≈' prefix survives), and
    table records carry extraction_type ('raw_table'/'derived_subset') and body_rows.
    """
    scores = []
    for fig in parsed.get('figures', []):
        method = fig.get('extraction_method')
        conf = fig.get('reading_confidence')
        cells = [str(v) for row in (fig.get('data_table') or []) for v in row.values()]
        numeric_cells = [c for c in cells if re.search(r'\d', c)]
        approx = sum(1 for c in numeric_cells if '≈' in c)
        frac_approx = approx / max(1, len(numeric_cells))

        if method == 'exact_from_labels':
            conf_penalty = 0.3 if conf == 'low' else 0.0
            scores.append(max(0.0, 1.0 - frac_approx - conf_penalty))
        elif method == 'digitized_estimate':
            scores.append(frac_approx if numeric_cells else 0.3)
        elif method == 'visual_description':
            scores.append(0.0 if cells else 1.0)
        else:
            scores.append(0.0)  # missing/invalid enum value

    for tbl in parsed.get('tables', []):
        if tbl.get('extraction_type') == 'raw_table':
            vals = [str(v).strip() for row in tbl.get('body_rows', []) for v in row.values()]
            decimals = [v for v in vals if re.match(r'^-?\d+\.\d+$', v)]
            if decimals:
                clean_share = sum(1 for v in decimals if v.endswith('0')) / len(decimals)
                scores.append(0.4 if clean_share > 0.8 else 1.0)

    return round(sum(scores) / len(scores), 3) if scores else 0.0
```

**What the function does & why.** It checks that `≈` markers appear exactly where the declared
extraction method says they should (present throughout for `digitized_estimate`, absent for
`exact_from_labels`), penalizes a "low confidence" reading dressed up as `exact_from_labels`, and
flags `visual_description` figures that smuggle in numeric tables. For raw tables it flags
suspiciously clean rounding (most decimals ending in 0) as inconsistent with "never rounded" verbatim
transcription of real measurement data.

**Why it's hard to Goodhart.** Faking consistent `≈` marking without genuinely re-deriving digitized
values requires either fabricating numbers (which then tend to look too clean, tripping the
raw-table rounding check and the substantive-trend check in Metric 2) or leaving numbers unmarked
(which directly loses points here). You can't cheaply satisfy both the "looks exact" and "avoids the
clean-number penalty" pulls without doing the real, careful transcription work.

---

## 4. Arithmetic Self-Consistency & Caveat Fidelity

**How it signals good science.** Good transcription doesn't just copy numbers — it notices when
the source's own numbers don't add up (e.g., PRISMA intake counts that don't sum to the reported
screened total) and says so, verbatim-faithfully, rather than silently "fixing" or hiding the
discrepancy. A transcript that surfaces internal inconsistencies it can compute from its own filed
text is demonstrating genuine engagement with the material, not narrative-smoothing.

**Compute function.**
```python
import re

def arithmetic_self_consistency(parsed):
    """
    Assumes each table/figure record exposes any free text fields present in the shape
    (caption, notes, trend_summary, visual_description values, data-quality caveats) as
    strings/lists of strings this function can scan for arithmetic the transcriber themself wrote.
    """
    def blobs(rec):
        out = [rec.get('caption', '') or '']
        notes = rec.get('notes', [])
        out += notes if isinstance(notes, list) else [notes or '']
        out.append(rec.get('trend_summary', '') or '')
        vd = rec.get('visual_description') or {}
        out += list(vd.values()) if isinstance(vd, dict) else []
        out.append(rec.get('data_quality_caveats', '') or '')
        return ' '.join(t for t in out if t)

    total_checks = surfaced = unflagged = 0
    for rec in parsed.get('tables', []) + parsed.get('figures', []):
        text = blobs(rec).lower()
        for expr in re.findall(r'\d+(?:\s*\+\s*\d+)+', text):
            total_checks += 1
            computed = sum(int(x) for x in re.split(r'\s*\+\s*', expr))
            others = [int(n) for n in re.findall(r'\b\d{2,6}\b', text)]
            mismatch = computed not in others  # no number in the text matches the recomputed sum
            flagged = bool(re.search(r'(do not reconcile|inconsisten|caveat|discrepanc|not match|does not match)', text))
            if mismatch and flagged:
                surfaced += 1
            elif mismatch and not flagged:
                unflagged += 1

    if total_checks == 0:
        return 0.3  # no arithmetic ever appeared to check against — treat as thin, not exempt
    net = (surfaced - unflagged) / total_checks
    return round(max(0.0, min(1.0, 0.5 + 0.5 * net)), 3)
```

**What the function does & why.** It scans only the filed transcript text itself for arithmetic the
transcriber wrote down (sums like `179+311+256+195`), recomputes it, and checks whether a mismatch
against other stated numbers is honestly flagged with caveat language nearby. If the artifact never
contains any such arithmetic at all, it gets a fixed, mediocre 0.3 — never a free pass — since
absence of any self-checking opportunity is itself weak evidence of rigor per the hard constraint.

**Why it's hard to Goodhart.** You can't inflate this score by inventing fake "look, we found an
inconsistency" caveats disconnected from real numbers — the regex requires the caveat to co-occur
with an actual computable mismatch in the same blob. Suppressing real mismatches (staying silent to
avoid mentioning them) is directly counted as `unflagged` and penalized, so silence is not a safe
strategy either.

---

## 5. Claim-Traceability Density

**How it signals good science.** The shape doc frames `evidence/` as the layer "every number in
`claims.md` ultimately traces back to." An evidence item with no claim linkage is either irrelevant
filler or a claim silently ungrounded elsewhere; a healthy evidence base links most filed items to
specific claims, spread across a genuinely varied set of claim IDs rather than a couple of catch-all
references.

**Compute function.**
```python
from collections import Counter

def claim_traceability_density(parsed):
    """
    Assumes parsed['readme']['tables_index'] and parsed['readme']['figures_index'] are lists of
    index rows, each with a 'claims' field: list[str] of ref-ids (e.g. ['C01','C02']), or an
    empty list / '—' marker meaning no claim was linked.
    """
    rows = parsed.get('readme', {}).get('tables_index', []) + parsed.get('readme', {}).get('figures_index', [])
    if not rows:
        return 0.0

    linked = 0
    all_ids = []
    for r in rows:
        claims = r.get('claims') or []
        if isinstance(claims, str):
            claims = [] if claims.strip() in ('', '—', '-') else [claims]
        if claims:
            linked += 1
            all_ids.extend(claims)

    coverage = linked / len(rows)
    penalty = 0.0
    if all_ids and len(rows) > 3:
        top_share = max(Counter(all_ids).values()) / len(all_ids)
        if top_share > 0.7:
            penalty = 0.2  # a couple of claim IDs rubber-stamped onto everything
    return round(max(0.0, coverage - penalty), 3)
```

**What the function does & why.** It computes the fraction of filed evidence items carrying at
least one real claim reference, then discounts the score if the claim IDs used are suspiciously
concentrated (suggesting the same one or two claim IDs were pasted onto every row rather than each
item being individually linked to what it actually supports).

**Why it's hard to Goodhart.** Linking every row to *some* claim ID is cheap, but doing so with a
narrow, repeated set of IDs trips the concentration penalty. Fabricating a wide spread of plausible-
looking but unearned claim IDs to dodge that penalty requires the underlying tables/figures to
actually look substantive enough to justify per-item distinct claims — which routes straight back
into Metrics 2 and 3's structural and honesty checks, since manufactured "distinct" linkage without
real underlying data tends to produce the same thin, generic content those metrics already catch.

---

## Combination

These five metrics are jointly hard to game because each shortcut for one creates exposure on
another. Padding the completeness note to reconcile counts (Metric 1) without truly reasoning about
skipped objects produces thin filed items that fail structural fallback discipline (Metric 2) and
generic trend text (Metric 2's substance check). Mislabeling extraction method or over-rounding
values to look "exact" (Metric 3) tends to also strip out the very numbers arithmetic
self-consistency (Metric 4) would otherwise cross-check, so the "no arithmetic found" floor (0.3)
catches evasion by omission. Silencing real internal inconsistencies to look clean (Metric 4) is
directly penalized as an unflagged mismatch rather than rewarded for tidiness. And rubber-stamping
claim links to inflate traceability (Metric 5) without doing real per-item transcription work
produces exactly the low-substance figures/tables that Metrics 2 and 3 independently punish. A
paper cannot cheaply manufacture "systematic, honest, self-checking, traceable" evidence — actually
doing the transcription work is the only path that scores well across all five.
