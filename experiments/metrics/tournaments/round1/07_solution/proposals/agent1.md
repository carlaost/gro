# Proposer 1 — metrics for `logic/solution/` (method layer)

Assumed parsed representation of the artifact (`artifact`):

```python
artifact = {
    "constraints": {
        "boundary_conditions": ["...", ...],           # List[str]
        "assumptions": [{"id": "A1", "text": "..."}],   # List[dict]
        "limitations": [{"name": "...", "text": "..."}],# List[dict]
        "data_quality_notes": ["...", ...],             # List[str], optional subsection
    },
    "method_files": {"study_design.md": "<full markdown text>", ...},  # 0..n files
    "heuristics": [{"id": "H01", "rationale": "...", "sensitivity": "...",
                     "bounds": "...", "code_ref": [...], "source": "..."}],  # optional
}
```

Where a metric also needs a cross-layer input (metric 5), that input is named explicitly and
its unavailability is scored low rather than skipped, per the hard constraint.

---

## 1. Limitation & Boundary Specificity Density

**How it signals good science**: Good science states caveats that are falsifiable and
concrete (named cohorts, platforms, effect sizes, section/table refs) — not decorative
boilerplate ("results should be interpreted with caution"). A paper whose `constraints.md`
is all boilerplate hasn't actually examined its own weak points.

**Compute function**:
```python
import re

def limitation_specificity_density(artifact):
    """
    Assumes: artifact['constraints'] with 'boundary_conditions': List[str] and
    'limitations': List[{'text': str}]. Total absence of constraints.md (should never
    happen per shape doc — it's mandatory) or an empty bullet set both floor to 0.0.
    """
    constraints = artifact.get("constraints")
    if not constraints:
        return 0.0
    bullets = list(constraints.get("boundary_conditions", [])) + \
        [l.get("text", "") for l in constraints.get("limitations", [])]
    if not bullets:
        return 0.0

    SPECIFIC = re.compile(
        r"(\d+(\.\d+)?%?)|(§\s?\d)|(\bTable\s?\d)|(\bFigure\s?\d)|"
        r"([A-Z][a-zA-Z]+\d{2,4})|(\bp\s?[<=]\s?0)"
    )
    GENERIC = re.compile(
        r"(may (have|contain) (some )?limitations)|(further (research|study) is needed)|"
        r"(interpreted with caution)|(no (major )?limitations (were )?(identified|stated))",
        re.IGNORECASE,
    )

    specific, generic = 0, 0
    for b in bullets:
        if GENERIC.search(b):
            generic += 1
        if SPECIFIC.search(b) and len(b.split()) >= 8:
            specific += 1

    score = (specific - 0.5 * generic) / len(bullets)
    return max(0.0, min(1.0, score))
```

**What it does & why**: Scans every boundary-condition and limitation bullet for concrete
anchors (numbers, section/table/figure refs, named platforms/cohorts) combined with a
minimum length so a stray digit doesn't count. It separately detects and penalizes
known boilerplate phrasing. The result is the net fraction of bullets that are
genuinely specific.

**Why it's hard to Goodhart**: Sprinkling numbers or fake `§` refs into otherwise vacuous
bullets can nudge the regex, but each bullet is scored independently — padding with many
short, low-content bullets does not raise the ratio, and lengthening bullets with filler
words to hit the 8-word floor makes the generic-phrase detector more likely to fire
somewhere in the same sentence.

---

## 2. Assumption → Consequence Traceability

**How it signals good science**: Stating "we assume X" is cheap; good science shows it
understood *what breaks if X is false* — either by tracing the assumption into a stated
limitation/boundary condition, or by stating the consequence inline. A pile of orphan,
never-revisited assumptions signals decorative rigor rather than examined rigor.

**Compute function**:
```python
import re

def assumption_traceability(artifact):
    """
    Assumes artifact['constraints']['assumptions']: List[{'id': str, 'text': str}] and
    ['limitations'] / ['boundary_conditions'] as above. Zero stated assumptions is
    treated as under-documentation (score 0.0), not as "nothing to trace."
    """
    constraints = artifact.get("constraints", {})
    assumptions = constraints.get("assumptions", [])
    if not assumptions:
        return 0.0

    downstream = (
        " ".join(l.get("text", "") for l in constraints.get("limitations", []))
        + " " + " ".join(constraints.get("boundary_conditions", []))
    ).lower()

    CONSEQUENCE = re.compile(
        r"(if (this|false)|may (bias|inflate|understate|overstate)|otherwise|"
        r"would (invalidate|weaken|undermine))",
        re.IGNORECASE,
    )

    linked = 0
    for a in assumptions:
        text = a.get("text", "")
        aid = a.get("id", "").lower()
        keywords = re.findall(r"[a-zA-Z]{5,}", text.lower())[:6]
        overlap = sum(1 for w in keywords if w in downstream)
        if (aid and aid in downstream) or overlap >= 2 or CONSEQUENCE.search(text):
            linked += 1
    return linked / len(assumptions)
```

**What it does & why**: For each assumption, checks three independent ways it could be
"closed": its ref-id is cited elsewhere, its own vocabulary echoes into a limitation or
boundary-condition bullet, or the assumption text itself states what would break if it
were violated. The fraction of assumptions satisfying any of these is the score.

**Why it's hard to Goodhart**: Copy-pasting assumption text verbatim into limitations to
force a keyword match produces no new information and is visible as duplicated raw text —
it earns no credit under Metric 1 (each bullet scored independently, no reward for length
or repetition) while consuming bullet slots that could have carried genuine specificity,
so gaming this metric directly taxes Metric 1's density score.

---

## 3. Method Groundedness (checkable-detail density)

**How it signals good science**: Reproducible method sections are full of falsifiable
specifics — exact software versions, parameter values, equation references, quantities
with units — not narrative hand-waving. The huu25-style line ("BayesSpace v1.11.0
spatialCluster(nrep=20000) ... optimal k=9") is the positive exemplar named in the shape
doc; vague prose is the negative one.

**Compute function**:
```python
import re

def method_groundedness(artifact):
    """
    Assumes artifact['method_files']: Dict[str, str] (filename -> full markdown text).
    A paper with zero method files beyond the mandatory constraints.md (the documented
    'abstract-only' floor case) scores 0.0 — there is nothing to ground.
    """
    method_files = artifact.get("method_files", {})
    if not method_files:
        return 0.0

    VERSION = re.compile(r"\bv?\d+\.\d+(\.\d+)?\b")
    PARAM = re.compile(r"\b[a-zA-Z_]+\s*=\s*[\d.\-eE]+\b")
    EQREF = re.compile(r"\b(Eq\.?|Equation)\s?\d+\b")
    SOFTWARE_CALL = re.compile(r"\b[A-Z][a-zA-Z]+\s*\(")
    NUMUNIT = re.compile(r"\b\d+(\.\d+)?\s?(mm|ml|kg|nm|%|reads|cells|donors|patients)\b")

    total, grounded = 0, 0
    for text in method_files.values():
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            total += 1
            if any(p.search(line) for p in
                   (VERSION, PARAM, EQREF, SOFTWARE_CALL, NUMUNIT)):
                grounded += 1
    return grounded / total if total else 0.0
```

**What it does & why**: Walks every non-heading prose line across all method files and
flags lines carrying at least one falsifiable technical anchor. The ratio of grounded to
total lines is the score — a method file that's mostly narrative summary scores low even
if it is long.

**Why it's hard to Goodhart**: Inflating this by inserting irrelevant numbers (page counts,
random digits) is possible in isolation, but the anchors are shaped like real technical
artifacts (version strings, `param=value`, equation refs) rather than bare digits, and any
invented software/parameter names that don't belong to the paper's actual genre get caught
by Metric 4 below.

---

## 4. Genre-Fit Discipline

**How it signals good science**: The shape doc explicitly names wrong-genre method-file
naming as a real defect (e.g., `architecture.md` attached to a pure statistical-synthesis
paper, or `training.md` for a paper that trained no model). A compiler/paper that reaches
for genre-typical file names without the matching substance is performing rigor rather
than doing it.

**Compute function**:
```python
import re

GENRE_SIGNATURES = {
    "architecture.md": [r"\blayer\b", r"\bmodule\b", r"\bcomponent\b", r"\bencoder\b", r"\bnetwork\b"],
    "algorithm.md": [r"\bpseudocode\b", r"\bcomplexity\b", r"O\(", r"\balgorithm\b"],
    "training.md": [r"\bepoch", r"\blearning rate\b", r"\boptimizer\b", r"\bbatch size\b"],
    "model.md": [r"\bparameter", r"\btrain", r"\bmodel\b"],
    "study_design.md": [r"\bcohort\b", r"\binclusion\b", r"\bexclusion\b", r"\bregist", r"\bsearch strategy\b"],
    "method.md": [r"\bassay\b", r"\bpipeline\b", r"\bQC\b", r"\bprotocol\b"],
    "heuristics.md": [r"\btrick\b", r"\bgotcha\b", r"\bempirical", r"\bin practice\b"],
    "formalization.md": [r"\btheorem\b", r"\bproof\b", r"\blemma\b", r"\bformal"],
    "proofs.md": [r"\btheorem\b", r"\bproof\b", r"\blemma\b"],
    "design.md": [r"\bdesign\b", r"\brationale\b"],
}

def genre_fit_discipline(artifact):
    """
    Assumes artifact['method_files']: Dict[str, str]. No method files at all floors to
    0.0 (no basis to credit discipline positively).
    """
    method_files = artifact.get("method_files", {})
    if not method_files:
        return 0.0

    scores = []
    for fname, text in method_files.items():
        sig = GENRE_SIGNATURES.get(fname.lower())
        if sig is None:
            scores.append(0.5)  # unrecognized name: can't verify fit either way
            continue
        hits = sum(1 for pat in sig if re.search(pat, text, re.IGNORECASE))
        scores.append(min(1.0, hits / max(2, len(sig) // 2)))
    return sum(scores) / len(scores)
```

**What it does & why**: For each present method filename, checks whether its content
actually contains the vocabulary a paper genuinely needing that file would use. A
`architecture.md` with no layer/module/network language scores near zero, directly
catching the defect the shape doc calls out.

**Why it's hard to Goodhart**: Stuffing genre buzzwords to pass this check tends to
either (a) not correspond to any real version/parameter/equation, which drags down
Metric 3's groundedness, or (b) if made genuinely specific to satisfy Metric 3, it must
then be substantively true to the paper's actual method — at which point it's no longer
gaming, it's just accurate reporting.

---

## 5. Cross-Layer Data-Quality Caveat Coverage

**How it signals good science**: The shape doc names a specific, checkable honesty test:
when the evidence layer independently surfaces a numeric inconsistency (e.g., a table's
row count contradicting its own caption), a rigorous solution layer says so in its
"Additional caveats surfaced during compilation" subsection rather than silently
reproducing the inconsistency. Silence here is a specific, catchable failure to flag a
known problem to downstream readers.

**Compute function**:
```python
import re

def data_quality_caveat_coverage(artifact, evidence_inconsistencies=None):
    """
    Assumes artifact['constraints']['data_quality_notes']: List[str] (the compiler-added
    subsection). Also assumes a cross-layer input, evidence_inconsistencies: List[str],
    each a free-text description of a numeric/table/figure inconsistency independently
    detected while parsing the evidence/ layer. Per the hard constraint: if this
    cross-layer input is not supplied, we cannot verify the caveats layer is honest, so
    we score low rather than skipping the metric.
    """
    if not evidence_inconsistencies:
        return 0.1

    dq_notes = artifact.get("constraints", {}).get("data_quality_notes", []) or []
    if not dq_notes:
        return 0.0  # real inconsistencies exist; none were surfaced

    dq_text = " ".join(dq_notes).lower()
    covered = 0
    for inconsistency in evidence_inconsistencies:
        anchors = re.findall(r"[A-Za-z]{4,}|\d+", inconsistency)[:5]
        if sum(1 for a in anchors if a.lower() in dq_text) >= 2:
            covered += 1
    return covered / len(evidence_inconsistencies)
```

**What it does & why**: Takes inconsistencies found independently elsewhere (a different
extraction pass over tables/figures) and checks whether the solution layer's own
data-quality notes actually name them (via shared anchor tokens like table numbers or
cohort names). Missing corroborating input is itself scored low, per the hard constraint,
rather than treated as "not applicable."

**Why it's hard to Goodhart**: The compiler cannot fabricate coverage without knowing what
the independently-derived evidence-layer inconsistencies actually say — this is a
same-fact-two-sources check, which is exactly the kind of cross-artifact redundancy that
resists single-layer editing. Padding `data_quality_notes` with generic disclaimers
doesn't raise the score because credit requires two-token anchor overlap with the specific
inconsistency, not just presence of any note.

---

## Combination

These five metrics are jointly hard to game because they pull in different, mutually
constraining directions. Padding `constraints.md` with generic filler to look thorough
fails Metric 1's specificity/generic-phrase test outright. Copy-pasting assumption text
to fake closure under Metric 2 produces duplicate bullets that earn zero net credit under
Metric 1, since bullets are scored independently rather than by aggregate length.
Inventing plausible-sounding technical detail to inflate Metric 3's groundedness either
belongs to the wrong genre — costing Metric 4 — or, if genre-correct, must be accurate
enough to actually be true, at which point it has stopped being gamed detail and become
real reporting. Reaching for prestige-sounding file names (`architecture.md`,
`algorithm.md`) without matching substance is directly penalized by Metric 4 independent
of how much prose those files contain. And Metric 5 cannot be gamed from within the
solution artifact alone at all — it requires matching facts independently derived in a
different layer, and any attempt to suppress a real inconsistency, or to fake coverage
with vague notes, is caught by the anchor-overlap check or by the default-low score when
corroboration is unavailable. A paper would need to simultaneously write specific,
non-generic caveats; genuinely close the assumption-to-consequence loop; ground its
methods in real checkable detail; use file names that actually match that detail; and
honestly reproduce independently-derived data-quality flags — which is to say, it would
need to actually do the rigorous work, not simulate it.
