## Changes from stage 1

- **M2 (Assumption → Consequence Traceability)**: closed the copy-paste hole. The old
  "≥2 of first-6 keywords overlap" test rewarded verbatim duplication of assumption text
  into a limitation/boundary bullet just as much as genuine tracing. Now overlap is
  measured as full-text Jaccard similarity against the best-matching downstream sentence,
  and near-duplicate sentences (similarity ≥ 0.55 — i.e. re-listing) are explicitly
  *disqualified* from counting unless they also carry consequence language; only moderate
  paraphrase similarity (0.2–0.55) or explicit consequence/id-citation still counts as
  real tracing.
- **M4 (Genre-Fit Discipline)**: replaced the lenient per-file keyword ratio (full marks
  for 2 hits; flat 0.5 free pass for unrecognized filenames) with a check aimed directly
  at the shape doc's named defect. A file now scores 0.0 outright if it shows zero
  signature hits itself, *and* 0.0 if the genre it claims is barely present anywhere in
  the paper's combined method corpus (the actual "architecture.md forced onto a
  stat-synthesis review" case) — so an off-list filename no longer escapes the check by
  being unrecognized; it's scored on the same content-evidence basis as named files.
- **M3 (Method Groundedness)**: tightened `SOFTWARE_CALL` so it only matches real call
  syntax — a camelCase or snake_case identifier immediately followed by a non-empty
  argument list — instead of any capitalized English word before a parenthesis, which
  previously false-positived on ordinary prose like "Cohort (described above)".
- **M5 (Cross-Layer Data-Quality Caveat Coverage)**: replaced the inert flat-0.1 floor
  with an explicit, reliably-wired contract. The cross-layer input is now the same
  internal-consistency pass the compiler already must run to populate constraints.md's
  own "Additional caveats surfaced during compilation" subsection (shape doc §7), so per
  the hard constraint we assume it is available; `ran=False` (the check never executed —
  a pipeline defect) floors to 0.0, `ran=True` with zero real inconsistencies scores 1.0
  (correct silence about a problem that doesn't exist is not a gap), and `ran=True` with
  inconsistencies still requires anchor-overlap coverage as before. This stops treating
  "nothing to report" and "input never computed" as the same case.

---

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
Re-listing the same assumption sentence verbatim elsewhere is not tracing it — it's
padding — so verbatim/near-verbatim recurrence must be explicitly told apart from genuine
paraphrase-and-consequence.

**Compute function**:
```python
import re

def assumption_traceability(artifact):
    """
    Assumes artifact['constraints']['assumptions']: List[{'id': str, 'text': str}] and
    ['limitations'] / ['boundary_conditions'] as above. Zero stated assumptions is
    treated as under-documentation (score 0.0), not as "nothing to trace." A downstream
    sentence that is a near-verbatim copy of the assumption text is explicitly
    disqualified from counting as tracing unless it also states a consequence —
    re-listing an assumption is not examining it.
    """
    constraints = artifact.get("constraints", {})
    assumptions = constraints.get("assumptions", [])
    if not assumptions:
        return 0.0

    downstream_text = (
        " ".join(l.get("text", "") for l in constraints.get("limitations", []))
        + " " + " ".join(constraints.get("boundary_conditions", []))
    )
    downstream_lower = downstream_text.lower()
    downstream_sentences = re.split(r"(?<=[.!?])\s+", downstream_text)

    CONSEQUENCE = re.compile(
        r"(if (this|false)|may (bias|inflate|understate|overstate)|otherwise|"
        r"would (invalidate|weaken|undermine))",
        re.IGNORECASE,
    )
    WORD = re.compile(r"[a-zA-Z]{4,}")

    def jaccard(a_words, b_words):
        a, b = set(a_words), set(b_words)
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    linked = 0
    for a in assumptions:
        text = a.get("text", "")
        aid = a.get("id", "").lower()
        a_words = WORD.findall(text.lower())

        if aid and aid in downstream_lower:
            linked += 1
            continue
        if CONSEQUENCE.search(text):
            linked += 1
            continue

        best_sim, best_sentence = 0.0, ""
        for sent in downstream_sentences:
            sim = jaccard(a_words, WORD.findall(sent.lower()))
            if sim > best_sim:
                best_sim, best_sentence = sim, sent

        if best_sim >= 0.55:
            # Near-duplicate sentence: only counts if it *adds* consequence language.
            # Pure re-listing earns nothing.
            if CONSEQUENCE.search(best_sentence):
                linked += 1
        elif best_sim >= 0.2:
            # Genuine paraphrase: downstream text engages the same idea in its own
            # words — real evidence of tracing, not restatement.
            linked += 1

    return linked / len(assumptions)
```

**What it does & why**: For each assumption, checks whether it was "closed" by one of
three routes: its ref-id is cited elsewhere, the assumption text itself states what would
break if it were violated, or a downstream limitation/boundary sentence engages the same
idea. That last route is now similarity-graded rather than a flat keyword count: sentences
that are near-verbatim copies of the assumption are treated as recurrence, not tracing,
and only count if they also carry consequence language; sentences that paraphrase the
assumption's content in different words count as genuine engagement.

**Why it's hard to Goodhart**: Copy-pasting assumption text verbatim into limitations no
longer earns credit by itself — the Jaccard-similarity check specifically routes
near-duplicate sentences into the strict branch that requires independent consequence
language, so duplication alone is worth zero. It also still earns no credit under
Metric 1 (each bullet scored independently, no reward for length or repetition), so
gaming this metric by padding directly taxes Metric 1 *and* fails to move Metric 2 itself.

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
    # Real function/method calls, not any capitalized noun before a paren: the callee
    # must look like an identifier (camelCase or snake_case — "spatialCluster",
    # "run_qc") rather than an ordinary capitalized English word ("Cohort", "Table"),
    # and it must carry a non-empty argument list.
    SOFTWARE_CALL = re.compile(
        r"\b([a-zA-Z]+[A-Z][a-zA-Z0-9]*|[a-zA-Z][a-zA-Z0-9]*_[a-zA-Z0-9_]+)"
        r"\(\s*[^()\s][^()]*\)"
    )
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
if it is long. The call-syntax anchor is restricted to identifiers that actually look like
function/method names (camelCase or snake_case with a non-empty argument list), so ordinary
prose like "Cohort (described above)" or "Table (see below)" no longer false-positives as
a grounded technical line.

**Why it's hard to Goodhart**: Inflating this by inserting irrelevant numbers (page counts,
random digits) is possible in isolation, but the anchors are shaped like real technical
artifacts (version strings, `param=value`, equation refs, real call syntax) rather than
bare digits or capitalized nouns, and any invented software/parameter names that don't
belong to the paper's actual genre get caught by Metric 4 below.

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
    0.0 (no basis to credit discipline positively). Targets the shape doc's named defect
    directly: a file whose name claims a genre must show that genre's vocabulary both in
    its own text and, more importantly, *somewhere real* across the paper's combined
    method corpus — otherwise the name was forced onto a paper that never actually did
    that kind of work. Unrecognized filenames are no longer given a free pass; they are
    scored on the same content-evidence basis as named ones, against whichever genre
    signature their own content best matches.
    """
    method_files = artifact.get("method_files", {})
    if not method_files:
        return 0.0

    corpus = " ".join(method_files.values())
    genre_hit_counts = {
        name: sum(1 for pat in sig if re.search(pat, corpus, re.IGNORECASE))
        for name, sig in GENRE_SIGNATURES.items()
    }

    scores = []
    for fname, text in method_files.items():
        key = fname.lower()
        sig = GENRE_SIGNATURES.get(key)

        if sig is None:
            # Unrecognized filename: score on content evidence against the best-fitting
            # known genre instead of a flat pass. A file with no vocabulary matching any
            # known genre is undifferentiated boilerplate, not automatically neutral.
            best_ratio = max(
                (sum(1 for pat in s if re.search(pat, text, re.IGNORECASE)) / len(s)
                 for s in GENRE_SIGNATURES.values()),
                default=0.0,
            )
            scores.append(min(1.0, best_ratio * 2))
            continue

        own_hits = sum(1 for pat in sig if re.search(pat, text, re.IGNORECASE))
        own_ratio = own_hits / len(sig)
        corpus_ratio = genre_hit_counts[key] / len(sig)

        if own_hits == 0:
            scores.append(0.0)  # filename claims a genre the file itself never shows
        elif corpus_ratio < 0.34:
            # Even generously counting hits anywhere in the whole method layer, this
            # genre is barely present in the paper — the file name is forced onto the
            # wrong genre (the architecture.md-on-a-stat-synthesis-review defect).
            scores.append(0.0)
        else:
            scores.append(min(1.0, own_ratio))

    return sum(scores) / len(scores)
```

**What it does & why**: For each present method filename, checks two things at once:
whether its own content actually contains the vocabulary a paper genuinely needing that
file would use, and whether that genre is substantively present anywhere across the
paper's whole method layer. A `architecture.md` with no layer/module/network language
anywhere in the paper scores zero, directly catching the named defect rather than being
satisfiable by two isolated keyword hits.

**Why it's hard to Goodhart**: Stuffing genre buzzwords into just the flagged file to pass
this check tends to either (a) not correspond to any real version/parameter/equation,
which drags down Metric 3's groundedness, or (b) if made genuinely specific enough to
satisfy Metric 3, it must then be substantively true to the paper's actual method — at
which point it's no longer gaming, it's just accurate reporting. Reaching for an
off-list filename to dodge the check no longer works either, since unrecognized names are
scored against the same content-evidence bar as recognized ones.

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

def data_quality_caveat_coverage(artifact, evidence_check=None):
    """
    Assumes a cross-layer input `evidence_check`: {"ran": bool, "inconsistencies":
    List[str]}. This is not an optional side-channel — it is the same internal-
    consistency pass the compiler already must run to populate constraints.md's own
    "Additional caveats surfaced during compilation" subsection (shape doc §7: tables'
    row counts vs. captions, PRISMA-diagram arithmetic, etc.), so per the hard constraint
    we assume it is available in practice. `ran=False` means the compiler's own
    cross-check step never executed — a pipeline defect distinct from "checked, found
    nothing" — and is scored at the floor rather than skipped or defaulted to a
    mid-range placeholder.
    """
    if evidence_check is None or not evidence_check.get("ran", False):
        return 0.0  # cross-check never ran: cannot be trusted, floor rather than skip

    inconsistencies = evidence_check.get("inconsistencies", [])
    dq_notes = artifact.get("constraints", {}).get("data_quality_notes", []) or []

    if not inconsistencies:
        # Ran, and genuinely found nothing to flag: correct silence is not a gap.
        return 1.0

    if not dq_notes:
        return 0.0  # real inconsistencies exist; none were surfaced

    dq_text = " ".join(dq_notes).lower()
    covered = 0
    for inconsistency in inconsistencies:
        anchors = re.findall(r"[A-Za-z]{4,}|\d+", inconsistency)[:5]
        if sum(1 for a in anchors if a.lower() in dq_text) >= 2:
            covered += 1
    return covered / len(inconsistencies)
```

**What it does & why**: Takes inconsistencies found independently elsewhere (a different
extraction pass over tables/figures) and checks whether the solution layer's own
data-quality notes actually name them (via shared anchor tokens like table numbers or
cohort names). The input contract now distinguishes three states instead of one collapsed
"absent" case: the cross-check never ran (pipeline defect, floored to 0.0), it ran and
found nothing (correctly rewarded at 1.0, since there was nothing to surface), or it ran
and found real inconsistencies (must be covered to score well).

**Why it's hard to Goodhart**: The compiler cannot fabricate coverage without knowing what
the independently-derived evidence-layer inconsistencies actually say — this is a
same-fact-two-sources check, which is exactly the kind of cross-artifact redundancy that
resists single-layer editing. Padding `data_quality_notes` with generic disclaimers
doesn't raise the score because credit requires two-token anchor overlap with the specific
inconsistency, not just presence of any note. And because "ran and found nothing" now
scores differently from "never ran," there is no way to quietly disable the cross-check to
collect a free mid-range score — skipping it is the worst-scoring option, not a shrug.

---

## Combination

These five metrics are jointly hard to game because they pull in different, mutually
constraining directions. Padding `constraints.md` with generic filler to look thorough
fails Metric 1's specificity/generic-phrase test outright. Copy-pasting assumption text to
fake closure under Metric 2 is now caught directly — near-duplicate sentences are
disqualified unless they add consequence language — and, even if it slipped through,
produces duplicate bullets that earn zero net credit under Metric 1, since bullets are
scored independently rather than by aggregate length. Inventing plausible-sounding
technical detail to inflate Metric 3's groundedness either belongs to the wrong genre —
costing Metric 4, whose corpus-wide check now catches wrong-genre files under any
filename, recognized or not — or, if genre-correct, must be accurate enough to actually be
true, at which point it has stopped being gamed detail and become real reporting. Reaching
for prestige-sounding file names (`architecture.md`, `algorithm.md`) without matching
substance is directly penalized by Metric 4 independent of how much prose those files
contain, and an off-list name no longer offers an escape hatch. And Metric 5 cannot be
gamed from within the solution artifact alone at all — it requires matching facts
independently derived in a different layer, any attempt to suppress a real inconsistency
or fake coverage with vague notes is caught by the anchor-overlap check, and disabling the
cross-check itself is now the lowest-scoring option rather than a neutral default. A paper
would need to simultaneously write specific, non-generic caveats; genuinely close the
assumption-to-consequence loop without just re-listing; ground its methods in real
checkable detail expressed as real call syntax; use file names that actually match
corpus-wide evidence of that genre; and honestly reproduce independently-derived
data-quality flags — which is to say, it would need to actually do the rigorous work, not
simulate it.
