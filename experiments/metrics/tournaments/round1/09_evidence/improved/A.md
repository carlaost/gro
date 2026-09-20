# Proposer #1 (improved) — metrics for `evidence/`

## Changes from stage 1

Per `critique_stage1.md` (agent1 = joint winner, three fixes requested):

1. **Killed the soft floors that violated the hard constraint.** `sweep_completeness_score` no
   longer returns `0.2` when the completeness note is unparseable/empty — an evidence set that
   gives us nothing checkable at all is now scored `0.0`, a real penalty, not a shrug. Same fix in
   `numeric_reconciliation_transparency`: the "nothing arithmetically checkable" case now returns
   `0.0` instead of `0.4`, with the rationale spelled out (real scientific tables almost always
   carry at least one labeled count — total absence of one across the whole evidence set is itself
   a defect, not a neutral non-finding).
2. **Structural conformance no longer rewards a placeholder trend sentence.** Added
   `is_substantive_trend()` — a low-confidence quantitative-plot fallback must contain an actual
   number *and* at least two named-entity-like tokens (biomarker/group identifiers, stat
   abbreviations like `AUC`/`CI`, capitalized proper nouns), not just a non-empty string. Applied it
   in both Metric 2 (`extraction_honesty_score`'s fallback-validity check — a filler trend summary
   no longer legally substitutes for a data table) and Metric 3 (`structural_conformance_score`'s
   `quantitative_plot` branch, the specific gap the critique named).
3. **Replaced the fragile "last integer in the caption" aggregate heuristic.** `evaluate()` in
   Metric 5 now extracts every *labeled* total (`n = 601`, `total 941`, `screened 601`, `included
   18`, etc.) from the caption and prose, and tries each one as a reconciliation target — instead of
   blindly trusting whatever integer happens to appear last in the caption (which is often a
   footnote marker, a year, or a page reference, not a count at all).

Everything else — the parsed-representation assumptions, the five-metric split, and the combination
narrative — is unchanged from stage 1 except where the fixes above ripple into the prose.

---

Assumed parsed representation (stated once, used by all functions below):

```python
evidence = {
  "readme": {
      "tables":  [{"file": str, "source": str, "claims": list[str] | str | None, "description": str}, ...],
      "figures": [{"file": str, "source": str, "claims": list[str] | str | None, "description": str}, ...],
      "completeness_note": str,       # the closing prose section of evidence/README.md
  },
  "table_files": {
      "<name>.md": {
          "caption": str, "source": str, "screenshot": str,
          "extraction_type": "raw_table" | "derived_subset",
          "derived_from": str | None,
          "table_rows": list[list[str]],   # raw cell strings, unrounded
          "notes": list[str] | None,
      }, ...
  },
  "figure_files": {
      "<name>.md": {
          "caption": str, "source": str, "screenshot": str,
          "figure_type": "quantitative_plot" | "diagram" | "qualitative_sample" | "mixed",
          "extraction_method": "exact_from_labels" | "digitized_estimate" | "visual_description",
          "reading_confidence": "high" | "medium" | "low",
          "plot_kind": str | None, "axes": str | None,
          "data_table": list[list[str]] | None,
          "trend_summary": str | None,
          "visual_description": {"components": str, "connections": str, "annotations": str,
                                   "what_it_conveys": str, "shows": str, "demonstrates": str,
                                   "supports": str} | None,
          "caveats": str | None,
          "panels": list[dict] | None,   # each a mini version of the above, for figure_type="mixed"
      }, ...
  },
}
```

---

## 1. Sweep Completeness

**How it signals good science.** The whole epistemic function of `evidence/` is to be a *systematic
sweep*, not a curated sample — an ARA that quietly files only the tables/figures that flatter its
claims and stays silent about the rest is doing selective evidentiary reporting, the evidence-layer
equivalent of cherry-picking. A trustworthy compile names every numbered object in the source and
accounts for every one it didn't file, with a reason. More honest accounting = more good science.

**Compute function.**

```python
import re

def sweep_completeness_score(evidence):
    """
    Assumes: evidence['readme']['completeness_note'] is the closing prose section of README.md.
    evidence['readme']['tables'/'figures'] rows carry a 'source' string like 'Table 2, §3.2'.
    We regex-extract every 'Table <n>' / 'Figure <n>' mention that appears ANYWHERE (in filed rows
    or in the note), take the highest number per kind as a floor on how many numbered objects the
    source is claimed to contain, and check that every number 1..max is either filed or explicitly
    named in the note together with a reason keyword nearby (not just a bare mention).
    """
    note = evidence.get('readme', {}).get('completeness_note', '') or ''
    filed_tables = evidence.get('readme', {}).get('tables', [])
    filed_figures = evidence.get('readme', {}).get('figures', [])
    REASON_KW = ('duplicate', 'supplement', 'not present', 'not filed', 'skip', 'paywall',
                 'appendix', 'not part of', 'unavailable', 'not included')

    def numbered(rows, kind):
        nums = set()
        for r in rows:
            m = re.search(rf'{kind}\s+(\d+)', r.get('source', ''))
            if m:
                nums.add(int(m.group(1)))
        return nums

    def reasoned_mentions(kind):
        nums = set()
        for m in re.finditer(rf'{kind}\s+(\d+)', note):
            window = note[max(0, m.start()-60): m.end()+60].lower()
            if any(k in window for k in REASON_KW):
                nums.add(int(m.group(1)))
        return nums

    def score_kind(kind, filed_rows):
        filed = numbered(filed_rows, kind)
        claimed_nums = [int(n) for n in re.findall(rf'{kind}\s+(\d+)', note)] + list(filed)
        top = max(claimed_nums, default=0)
        if top == 0:
            return None  # this kind has no numbered objects in the source at all -- nothing to check
        reasoned = reasoned_mentions(kind)
        unaccounted = [n for n in range(1, top + 1) if n not in filed and n not in reasoned]
        return 1.0 - len(unaccounted) / top

    scores = [s for s in (score_kind('Table', filed_tables), score_kind('Figure', filed_figures))
              if s is not None]
    if not scores:
        # Neither filed rows nor the note contain a single numbered-object reference: we cannot
        # verify a sweep happened at all, and an ARA claiming completeness with zero verifiable
        # evidence of *what* it swept is exactly the uncheckable-input case the brief requires us
        # to penalize -- not a case to wave through with a comfortable mid-floor.
        return 0.0
    return max(0.0, min(1.0, sum(scores) / len(scores)))
```

**What the function does & why.** It never trusts a global "we filed everything" claim at face
value. Instead it reconstructs, purely from evidence numbers actually referenced in the artifact, the
implied size of the source's numbered-object set, then walks every integer up to that ceiling and
demands each one be either (a) present as a filed file or (b) named in the completeness note next to
an actual reason word (duplicate, supplementary, paywalled, etc.) — a bare mention of "Figure 9" with
no explanatory context doesn't count. The score is the fraction of numbered objects properly
accounted for. When the artifact gives us no numbered references anywhere to reconstruct a ceiling
from, that is treated as a failure to demonstrate a sweep occurred, not a pass.

**Why it's hard to Goodhart.** You cannot inflate the score by simply filing junk copies (that
doesn't reduce `unaccounted`, since the count is about *numbers*, not file volume), and you cannot
game it by listing skipped numbers with no explanation (the reason-keyword window check catches bare
mentions). You also cannot dodge the check by omitting the completeness note and filing nothing
verifiable — that now falls straight to the `0.0` floor instead of a soft default that rewarded
silence over disclosure. The only ways to raise this score are to actually file more of the swept
objects or write a real, specific justification for each gap — both of which are the behavior the
metric is meant to reward.

---

## 2. Extraction-Method Honesty

**How it signals good science.** The schema draws a hard epistemic line between *read* numbers
(`exact_from_labels`) and *estimated* numbers (`digitized_estimate`, marked with `≈`), and between
quantitative content and non-quantitative content (`diagram`/`qualitative_sample` must never carry a
fabricated numeric table). A compiler that respects these distinctions is one whose confidence labels
can be trusted downstream; one that blurs them (claims "exact" while hedging, or invents numbers in a
diagram) is manufacturing false precision — a classic good-science failure mode.

**Compute function.**

```python
import re

def extraction_honesty_score(evidence):
    """
    Assumes figure_files/table_files expose extraction_type/extraction_method, reading_confidence,
    and raw table_rows/data_table cell strings (so '≈' markers are visible verbatim). Mixed figures
    expose 'panels', each a mini version of the same fields.
    """
    def is_substantive_trend(text):
        """A trend summary satisfies the 'table-or-fallback' requirement only if it actually
        reports findings -- a number plus at least two named-entity-like tokens (identifiers,
        group/biomarker names, stat abbreviations such as CI/AUC/MD, or capitalized proper nouns).
        A generic placeholder sentence ('Values trend upward across groups.') has neither and no
        longer counts as a legal substitute for a real data table."""
        if not text or not str(text).strip():
            return False
        text = str(text)
        if not re.search(r'\d', text):
            return False
        tokens = re.findall(r'\b[A-Za-z][A-Za-z0-9_.-]{1,}\b', text)
        entity_like = {t for t in tokens
                       if re.search(r'\d', t)                 # e.g. p217, CI95
                       or (t.isupper() and len(t) > 1)         # e.g. AUC, CI, MD
                       or re.match(r'^[A-Z][a-z]+', t)}        # capitalized proper noun/group name
        return len(entity_like) >= 2

    violations = 0
    checks = 0

    def check_quant(ftype, method, conf, data, trend):
        nonlocal violations, checks
        checks += 1
        if ftype in ('diagram', 'qualitative_sample'):
            if data:
                violations += 1  # fabricated numeric table inside a non-quantitative figure
            return
        if ftype != 'quantitative_plot':
            return
        if not data and not (conf == 'low' and is_substantive_trend(trend)):
            violations += 1  # neither a real data table nor a substantive low-confidence fallback
            return
        flat = [c for row in (data or []) for c in row]
        approx_n = sum(1 for c in flat if '≈' in str(c))
        if method == 'exact_from_labels' and (approx_n > 0 or conf == 'low'):
            violations += 1  # claims exact reading but hedges values or confidence
        if method == 'digitized_estimate' and approx_n == 0:
            violations += 1  # claims estimation but shows no hedge markers -> likely mislabeled

    for fig in evidence.get('figure_files', {}).values():
        if fig.get('figure_type') == 'mixed':
            for p in fig.get('panels', []) or []:
                check_quant(p.get('figure_type'), p.get('extraction_method'),
                            p.get('reading_confidence'), p.get('data_table'), p.get('trend_summary'))
        else:
            check_quant(fig.get('figure_type'), fig.get('extraction_method'),
                        fig.get('reading_confidence'), fig.get('data_table'), fig.get('trend_summary'))

    for tbl in evidence.get('table_files', {}).values():
        checks += 1
        if tbl.get('extraction_type') == 'derived_subset' and not tbl.get('derived_from'):
            violations += 1  # claims a derivation lineage it doesn't actually cite

    if checks == 0:
        return 0.0  # nothing to check -> no evidence at all, maximal penalty
    return max(0.0, 1.0 - violations / checks)
```

**What the function does & why.** For every figure (recursing into panels of `mixed` figures) it
enforces the schema's own honesty rules: no numeric tables hiding inside diagrams/qualitative
samples, no quantitative plot skipping both the data table and its mandated low-confidence
trend-summary fallback (and that fallback must now actually say something, per
`is_substantive_trend` — see Metric 3 for the matching structural check), no `exact_from_labels`
figure quietly containing `≈`-hedged values or a low confidence rating, and no `digitized_estimate`
figure that suspiciously shows zero hedge markers (a sign it was actually read exactly but
under-labeled to look conservative, or mislabeled the other way). Derived-subset tables must cite
their parent. The score is 1 minus the violation rate.

**Why it's hard to Goodhart.** Every individual dodge is cross-checked against a different field
that would have to be *simultaneously and consistently* faked: to fake "exact" you must scrub every
`≈` from the actual cell values (destroying the honest record of what was estimated), and to fake
"estimate" cheaply you'd have to inject fake hedge markers into numbers you actually read cleanly,
which is directly visible if compared to the source screenshot at review time. Mislabeling in one
direction to dodge one check tends to trip the opposite check. And a compiler that tries to dodge
the "no data table" violation with a one-line placeholder trend summary no longer succeeds — the
`is_substantive_trend` gate demands real numbers and named entities, which is exactly the extraction
work the fallback was meant to require in the first place.

---

## 3. Type-Body Structural Conformance

**How it signals good science.** Each figure/table type has a *specific* mandatory body (diagram →
Components/Connections/Annotations/What-it-conveys; qualitative_sample → Shows/Demonstrates/Supports;
quantitative_plot → axes + plot kind + data-or-fallback). A compile that fills in all required
structure for the type it declares is one that actually did the extraction work rather than dashing
off a caption and calling it done — thoroughness of structure is a direct, checkable proxy for
extraction effort.

**Compute function.**

```python
import re

def structural_conformance_score(evidence):
    """
    Assumes missing fields surface as None/''/absent-key. visual_description['supports'] is assumed
    to be a bare ref-id string like 'C03' when present.
    """
    def has(v):
        return v is not None and str(v).strip() != ''

    def is_substantive_trend(text):
        """Same substance gate as Metric 2: a low-confidence fallback must contain a number and at
        least two named-entity-like tokens, not just a non-empty placeholder sentence. Without this,
        a `quantitative_plot` with zero data and one filler sentence was trivially 'conformant'."""
        if not has(text):
            return False
        text = str(text)
        if not re.search(r'\d', text):
            return False
        tokens = re.findall(r'\b[A-Za-z][A-Za-z0-9_.-]{1,}\b', text)
        entity_like = {t for t in tokens
                       if re.search(r'\d', t)
                       or (t.isupper() and len(t) > 1)
                       or re.match(r'^[A-Z][a-z]+', t)}
        return len(entity_like) >= 2

    total, ok = 0, 0

    for tbl in evidence.get('table_files', {}).values():
        total += 1
        req = [tbl.get('caption'), tbl.get('source'), tbl.get('screenshot'), tbl.get('extraction_type')]
        if tbl.get('extraction_type') == 'derived_subset':
            req.append(tbl.get('derived_from'))
        if all(has(v) for v in req) and tbl.get('table_rows'):
            ok += 1

    for fig in evidence.get('figure_files', {}).values():
        total += 1
        base = [fig.get('caption'), fig.get('source'), fig.get('screenshot'), fig.get('figure_type'),
                 fig.get('extraction_method'), fig.get('reading_confidence')]
        if not all(has(v) for v in base):
            continue
        vd = fig.get('visual_description') or {}
        ftype = fig.get('figure_type')
        if ftype == 'diagram':
            ok += all(has(vd.get(k)) for k in
                       ('components', 'connections', 'annotations', 'what_it_conveys'))
        elif ftype == 'qualitative_sample':
            ok += (has(vd.get('shows')) and has(vd.get('demonstrates'))
                    and bool(re.match(r'^[A-Za-z]\d+', str(vd.get('supports', '')))))
        elif ftype == 'quantitative_plot':
            ok += bool(has(fig.get('axes')) and has(fig.get('plot_kind')) and
                        (fig.get('data_table') or
                         (fig.get('reading_confidence') == 'low' and
                          is_substantive_trend(fig.get('trend_summary')))))
        elif ftype == 'mixed':
            panels = fig.get('panels') or []
            ok += bool(panels) and all(has(p.get('figure_type')) for p in panels)

    return ok / total if total else 0.0
```

**What the function does & why.** It looks up the type each file declares for itself, then demands
exactly the body fields the schema requires for that declared type before counting the file as
conformant. Nothing gets partial credit for having *some* fields — a diagram missing "Annotations",
or a qualitative_sample whose "Supports" isn't a real-looking ref-id, fails outright. A
`quantitative_plot` with no data table can no longer pass on a one-sentence filler trend summary — it
must clear `is_substantive_trend`, the same numbers-plus-entities bar Metric 2 applies. The score is
the fraction of all filed objects that are fully conformant.

**Why it's hard to Goodhart.** Filling every field with copy-pasted boilerplate is caught elsewhere:
boilerplate captions/descriptions correlate with low claims-linkage (Metric 4) and shallow reconciliation
(Metric 5), since generic prose won't happen to satisfy those content-sensitive checks. Declaring
a false, easier type to dodge a hard body requirement (e.g. mislabeling a real plot as `diagram` to
avoid needing a data table) is exactly the mislabeling Metric 2 is built to punish. And farming the
low-confidence fallback with a single vague sentence — previously the cheapest way to pass this
metric without doing any real extraction — no longer works: `is_substantive_trend` requires the
sentence to actually name numbers and entities, which is indistinguishable from having done the
reading in the first place.

---

## 4. Claims-Grounding Coverage

**How it signals good science.** The artifact's stated purpose is to be "the raw material every
number in `claims.md` ultimately traces back to." An evidence set that is large but mostly orphaned
(filed, indexed, yet linked to no claim) isn't doing its job — it's decoration. An evidence set that
barely exists at all (paywalled source, near-zero filings) is a near-total loss of grounding capacity.
Good science here means the evidence layer is small-or-large *in proportion to* how much grounding
work it is actually doing for the claims layer.

**Compute function.**

```python
def claims_grounding_coverage(evidence):
    """
    Assumes README rows expose 'claims' as a list[str] of ref-ids, or None/'—'/'-' when unlinked.
    """
    rows = (evidence.get('readme', {}).get('tables', []) +
            evidence.get('readme', {}).get('figures', []))
    if not rows:
        return 0.0  # nothing filed at all -> total loss of grounding capacity

    def linked(r):
        c = r.get('claims')
        if not c:
            return False
        if isinstance(c, str):
            return c.strip() not in ('', '—', '-')
        return len(c) > 0

    coverage = sum(1 for r in rows if linked(r)) / len(rows)
    # a very thin evidence set is penalized even if what little is there is linked
    thinness_penalty = 1.0 if len(rows) >= 3 else 0.5 + 0.5 * (len(rows) / 3)
    return coverage * thinness_penalty
```

**What the function does & why.** It computes what fraction of filed tables/figures actually carry a
non-empty `Claims` column, then applies a size penalty so that a technically-100%-linked but
one-object evidence set (e.g. from a paywalled source) still scores low, matching the brief's note
that such cases should "read as a near-total loss of grounding capacity, not a small gap." The
`rows == []` case (no evidence filed at all, e.g. a fully paywalled source) already hits the hard
`0.0` floor, consistent with the same missing-input discipline applied elsewhere in this revision.

**Why it's hard to Goodhart.** Rubber-stamping every row with a fake claim ref-id to inflate coverage
only helps if those ref-ids are real and resolve to actual claims elsewhere in the ARA (checked
outside this artifact, but any reviewer cross-referencing `claims.md` catches fabricated links
immediately) — and padding row *count* to dilute the thinness penalty means filing more objects,
which re-exposes the padding files to Metrics 2 and 3's structural/honesty checks.

---

## 5. Numeric Reconciliation Transparency

**How it signals good science.** Real transcription work sometimes surfaces numbers that don't add
up (the PRISMA example: 941 records reported vs. 601 actually screened). Good science reports the
discrepancy verbatim and flags it rather than silently "fixing" it to look clean. Rewarding explicit,
flagged mismatches — not just clean-looking totals — directly targets the honesty behavior the schema
calls out as a specific compliance point.

**Compute function.**

```python
import re
from itertools import combinations

def numeric_reconciliation_transparency(evidence):
    """
    Assumes raw cell strings in table_rows/data_table, plus a free-text caveats/notes string per
    object. Instead of trusting the last bare integer in a caption as 'the total' (fragile: captions
    often end with a footnote marker, a year, or a page ref that isn't a count at all), we anchor on
    integers explicitly labeled as counts (n=, total, screened, included, identified, excluded,
    studies, records) in the caption or prose, and test each such labeled total as a reconciliation
    target against the object's inner numbers.
    """
    def ints_in(s):
        return [int(x) for x in re.findall(r'-?\d+', str(s))]

    def reconciles(nums, target):
        for r in range(1, min(len(nums), 6) + 1):
            for combo in combinations(nums, r):
                if abs(sum(combo) - target) <= max(1, round(target * 0.01)):
                    return True
        return False

    FLAG_KW = ('reconcile', 'do not match', "doesn't match", 'mismatch', 'discrepanc',
               'not correspond', 'does not add up')
    LABEL_KW = r'(?:n\s*=|total(?:s|ed)?|screened|included|excluded|identified|records?|studies)'

    def labeled_totals(text):
        text = str(text or '')
        totals = []
        for m in re.finditer(r'\bn\s*=\s*(\d+)\b', text, re.IGNORECASE):
            totals.append(int(m.group(1)))
        for m in re.finditer(rf'{LABEL_KW}\D{{0,15}}?(\d+)', text, re.IGNORECASE):
            totals.append(int(m.group(1)))
        return totals

    def evaluate(rows, caption, prose):
        all_nums = [n for row in rows for c in row for n in ints_in(c)]
        targets = set(labeled_totals(caption)) | set(labeled_totals(prose))
        if not targets or len(all_nums) < 2:
            return None
        for target in sorted(targets, reverse=True):
            candidates = [n for n in all_nums if n != target]
            if reconciles(candidates, target):
                return True
        return any(kw in (prose or '').lower() for kw in FLAG_KW)

    checkable, transparent = 0, 0
    for tbl in evidence.get('table_files', {}).values():
        r = evaluate(tbl.get('table_rows', []), tbl.get('caption', ''),
                      ' '.join(tbl.get('notes') or []))
        if r is not None:
            checkable += 1
            transparent += r

    for fig in evidence.get('figure_files', {}).values():
        r = evaluate(fig.get('data_table') or [], fig.get('caption', ''), fig.get('caveats', ''))
        if r is not None:
            checkable += 1
            transparent += r

    if checkable == 0:
        # No explicitly labeled total anywhere in the evidence set is a penalized gap, not a
        # neutral non-finding: real scientific tables/figures almost always carry at least one
        # labeled count (n=, total, screened...), so its total absence across every object is
        # itself informative of thin or careless extraction, and the brief requires we penalize
        # uncheckable input rather than default to a comfortable mid-score.
        return 0.0
    return transparent / checkable
```

**What the function does & why.** For each object with an explicitly *labeled* count in its caption
or prose (not a bare positional guess) and enough inner numbers to plausibly sum to it, it tests
every labeled total as a reconciliation target; if none reconciles, it checks whether the
accompanying notes/caveats prose flags the mismatch explicitly. The score is the fraction of
checkable objects that are either internally consistent or honestly flagged when they aren't.

**Why it's hard to Goodhart.** You can't raise this score by writing vague disclaimer boilerplate
into every Notes field, because the metric only credits a flag when a *real* arithmetic mismatch was
found first — prose with no matching numeric discrepancy just doesn't get evaluated. You also can't
raise it by quietly correcting numbers to make them add up cleanly, since the shape doc requires
verbatim, unrounded transcription — Metric 2's exactness checks and a source-screenshot spot-check
would catch silently "fixed" values. Anchoring the target on an explicit label also closes off a
subtler dodge available in the original heuristic: a compiler could no longer make an inconvenient
mismatch "uncheckable" (and thus invisible to this metric) just by rephrasing the caption so the
inconvenient count isn't the last integer in the sentence — every labeled count is now a candidate
target, not just the positionally last one. And leaving every object's total unlabeled to duck the
check entirely now costs the full `0.0` floor rather than a comfortable default.

---

## Combination

Each metric leans on a different part of the artifact, and gaming one tends to bleed into the others.
Inflating apparent completeness (Metric 1) by filing padding objects exposes those objects to the
structural and honesty checks (Metrics 2–3) and dilutes claims coverage (Metric 4) unless they're
genuinely useful; omitting the completeness note altogether to avoid a checkable claim now costs the
full `0.0` floor instead of a shrug. Mislabeling extraction confidence to look either more rigorous or
more conservative (dodging Metric 2) tends to fail Metric 3's type-specific structural requirements,
since a relabeled figure typically has the wrong shape of body for its new declared type — and neither
metric can be satisfied any more by a filler low-confidence trend sentence, since both now require the
same numbers-plus-entities substance test. Rubber-stamping fake claims-links to win Metric 4 is
exposed the moment those links are cross-checked against `claims.md`, and doesn't help the
size-thinness term unless real objects are filed, which re-exposes them to Metrics 1–3. Papering over
numeric inconsistencies with generic disclaimer language to win Metric 5 does nothing, because the
metric only rewards flags attached to real, detected mismatches against an explicitly labeled total —
and "fixing" numbers instead of flagging them is directly punishable as a verbatim-fidelity violation
under Metric 2. No single cheap edit — padding, relabeling, fake linking, vague caveats, or leaving
inputs uncheckable — improves more than one metric at a time, and most such edits actively cost points
across several metrics at once, now including the floors themselves.
