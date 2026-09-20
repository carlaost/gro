# Proposer #4 — metrics for `logic/solution/` (method layer)

Assumed parsed representation passed to every `compute_*` function:

```python
artifact = {
    "constraints": {
        "boundary_conditions": ["str", ...],
        "assumptions": [{"id": "A1", "text": "str"}, ...],
        "limitations": [
            {"name": "str", "text": "str", "section": "§4.5" | None}
        ],
        "limitations_section_anchor": "§4.5" | None,   # anchor on the "## Known limitations (§X.Y)" header itself
        "data_quality_caveats": ["str", ...],           # [] if the subsection is absent
    },
    "method_files": {
        "study_design.md": "raw markdown text",
        "method.md": "raw markdown text",
        # ... 0+ files, keyed by filename
    },
    "heuristics": [
        {
            "id": "H03",
            "rationale": "str",
            "sensitivity": "low" | "medium" | "high" | "Not specified in paper",
            "bounds": "str" | "Not specified in paper",
            "code_ref": ["src/execution/foo.py", ...] | "Not specified",
            "source": "str",
        },
        ...
    ],  # [] if heuristics.md is absent
}
```

---

## 1. Assumption Testability Score

**How it signals good science.** An assumption is scientifically load-bearing only if it is concrete
enough that a reader could point to evidence that would violate it (a named cohort being
non-independent, a platform drift, a specific sample-size floor). Generic hedges ("results may not
generalize to other populations") cost nothing to write and constrain nothing — they are the
assumption-layer equivalent of a null result reported as "more research is needed." Artifacts whose
assumptions are specific and checkable have done the harder work of pinning down exactly where the
method could break.

**Compute function.**
```python
import re

# Assumes artifact["constraints"]["assumptions"] is a list of {"id","text"} dicts,
# possibly empty.
def assumption_testability_score(artifact: dict) -> float:
    assumptions = artifact["constraints"]["assumptions"]
    if not assumptions:
        return 0.0  # no assumptions stated at all -> penalize, never N/A

    generic_hedges = re.compile(
        r"\b(may not generalize|further (research|validation) (is )?needed|"
        r"results may vary|limited generalizability|standard (assumptions|methods))\b",
        re.I,
    )
    entity_marker = re.compile(
        r"\b([A-Z][a-zA-Z0-9\-]{2,}\s?){1,4}\b|"     # named entity / proper noun phrase
        r"\d+(\.\d+)?\s?(%|mm|ml|n=|patients|samples|donors|cohorts?)"  # quantity+unit
    )
    conditional_marker = re.compile(
        r"\b(assumes?|requires?|implies?|only valid if|holds when|no .* is)\b", re.I
    )

    scores = []
    for a in assumptions:
        text = a["text"]
        markers = 0
        if entity_marker.search(text):
            markers += 1
        if conditional_marker.search(text):
            markers += 1
        if len(text.split()) >= 8:      # enough words to actually specify something
            markers += 1
        is_generic = bool(generic_hedges.search(text))
        scores.append(0.0 if is_generic else min(markers / 3.0, 1.0))

    return sum(scores) / len(scores)
```

**What the function does & why.** Rejects the empty case outright (floor score). For each stated
assumption, it looks for three independent specificity signals: a named entity or quantity, a
conditional/causal construction that states *when* the assumption would fail, and enough length to
plausibly carry real content. Any hit on a known generic-hedge template zeroes that assumption
regardless of markers, since boilerplate can accidentally contain a number ("more than 5% of
studies...") without being a real constraint. The artifact score is the mean across assumptions, so a
single sharp assumption buried among ten vague ones still gets diluted — rewarding consistency, not
one good line.

**Why it's hard to Goodhart.** Padding with more assumptions to average up requires each new one to
independently clear the entity/conditional/length bar without tripping the generic-hedge filter —
that means writing something that *sounds* like a real, checkable constraint, which is most cheaply
achieved by actually transcribing a real constraint from the paper. Templated "high-scoring" filler
(e.g., always writing "assumes cohort X has n>500 patients") would need a different named cohort and
number each time to keep clearing the entity check across many assumptions, and reusing the same
template repeatedly is detectable as low-entropy text (a straightforward extension: flag near-duplicate
assumption texts).

---

## 2. Limitation Section-Anchoring Ratio

**How it signals good science.** A limitation that cites the specific section/table/figure it comes
from is traceable — someone can go verify it against the source. A limitation asserted with no anchor
is unfalsifiable *as a compiled artifact*: there's no way to check whether the compiler read it out of
the paper or manufactured a plausible-sounding caveat. The brief's own gold example anchors the whole
subsection to `§4.5`; papers that report *zero* limitations are flagged as a red flag precisely because
essentially every paper states some caveat — so both "no limitations" and "limitations with no
provenance" are quality failures this metric should catch.

**Compute function.**
```python
import re

# Assumes artifact["constraints"]["limitations"] (list, possibly empty) and
# artifact["constraints"]["limitations_section_anchor"] (str or None).
def limitation_anchoring_ratio(artifact: dict) -> float:
    limitations = artifact["constraints"]["limitations"]
    header_anchor = artifact["constraints"]["limitations_section_anchor"]

    if not limitations:
        return 0.0  # bare "no limitations stated" -> penalize per brief's own red-flag note

    section_pat = re.compile(r"§\s?\d+(\.\d+)?|Table\s?\d+|Figure\s?\d+|Fig\.\s?\d+", re.I)

    header_bonus = 0.15 if header_anchor and section_pat.search(header_anchor) else 0.0

    anchored = 0
    for lim in limitations:
        text = lim.get("text", "")
        name = lim.get("name", "")
        has_own_anchor = bool(section_pat.search(text) or section_pat.search(name))
        has_concrete_object = bool(re.search(r"\b[A-Z][a-zA-Z]{3,}\b", text))  # a real named thing
        if has_own_anchor or (header_anchor and has_concrete_object):
            anchored += 1

    ratio = anchored / len(limitations)
    return min(ratio + header_bonus, 1.0)
```

**What the function does & why.** Empty limitations list is a hard zero — matching the brief's
explicit statement that a limitations-free artifact is a red flag, not a clean bill of health. Given a
non-empty list, it rewards a section-level anchor on the header (small bonus, since one anchor for the
whole block is weaker evidence than per-bullet anchors) and separately checks each bullet for either
its own citation or, failing that, at least a concrete named object (a real method/platform/dataset
term) that makes the claim checkable in principle even without an explicit pointer.

**Why it's hard to Goodhart.** The cheap Goodhart move — writing `(§0.0)` or a fake section number on
every bullet — is defeated by requiring the anchor pattern to be a plausible section/table/figure
reference; a compiler could still fabricate `§4.5` freely, but the regex is a floor check, not a proof
of correctness, and this metric is explicitly one leg of a combination (see below) that also checks
whether the *content* named is a concrete, checkable thing rather than boilerplate — cheap numeric
fabrication doesn't help if the bullet text itself is generic.

---

## 3. Heuristic Field-Completeness & Honesty Score

**How it signals good science.** `heuristics.md` exists to capture *implementation-level* claims —
sensitivity, numeric bounds, and a code reference — that are exactly the kind of detail separating a
paper that reports how fragile its own tricks are from one that hand-waves. A heuristics file where
every field reads "Not specified in paper" is worse than no heuristics file at all: it's the
appearance of rigor (structured fields, an H-number) without any of the substance, i.e. manufactured
precision. Real heuristic entries, per the brief's own example, come with an actual enum sensitivity
rating, a concrete bound (`α∈[0,1]`), and a real `src/execution/...` path.

**Compute function.**
```python
NOT_SPECIFIED = {"not specified", "not specified in paper", "not specified.", ""}

# Assumes artifact["heuristics"] is a list (possibly empty) of heuristic dicts as shaped above.
def heuristic_completeness_score(artifact: dict) -> float:
    heuristics = artifact["heuristics"]
    if not heuristics:
        # Per the tournament's hard constraint: missing input is penalized, not skipped.
        # Fixed low floor rather than 0, since correct absence is common (per shape doc) —
        # but we cannot verify correctness of absence from this artifact alone, so we treat
        # unverifiable absence as a (mild) quality risk rather than a neutral non-event.
        return 0.2

    def field_ok(value) -> bool:
        if isinstance(value, list):
            return len(value) > 0 and value != ["Not specified"]
        return isinstance(value, str) and value.strip().lower() not in NOT_SPECIFIED

    per_heuristic = []
    for h in heuristics:
        fields = [h.get("sensitivity"), h.get("bounds"), h.get("code_ref")]
        filled = sum(1 for f in fields if field_ok(f))
        code_ref_real = isinstance(h.get("code_ref"), list) and any(
            ref.startswith("src/") for ref in h["code_ref"]
        )
        completeness = filled / 3.0
        if not code_ref_real:
            completeness *= 0.7  # a heuristic with no real code anchor is weaker evidence
        per_heuristic.append(completeness)

    return sum(per_heuristic) / len(per_heuristic)
```

**What the function does & why.** No heuristics at all gets a fixed low floor (0.2) rather than zero
or N/A — honoring the hard constraint that missing input is penalized, while not equating it with the
worst possible case, since the shape doc itself notes correct absence is the *common* case. When
heuristics exist, each is scored by how many of its three substantive fields actually carry content
(vs. the templated "Not specified" filler), with an extra discount when the code reference doesn't
point at a real `src/` path — a heuristic that isn't traceable to actual code is closer to a comment
than an engineering claim.

**Why it's hard to Goodhart.** Inventing heuristics to raise the average requires each one to carry a
sensitivity rating, a bound, and a `src/...` path that plausibly exists — fabricating a fake path is
cheap to write but easy to catch downstream (cross-referencing against the actual repository tree,
which this metric's discount term is designed to anticipate). Simply omitting a heuristics file to
dodge the check locks the artifact into the fixed 0.2 floor, which is worse than a modest, honestly
populated file — so the metric doesn't reward silence over disclosure.

---

## 4. Method Grounding Density (quantitative/technical specificity)

**How it signals good science.** The brief's own gold-standard example — *"BayesSpace v1.11.0
spatialCluster(nrep=20000) over k=2..28; optimal k=9"* — is dense with exactly-reproducible detail:
tool name, version, function call, parameter values, a swept range, and the chosen outcome. A method
file that instead says "we clustered the spots using standard software" carries none of that
falsifiable, reproducible content. Density of such tokens is a cheap but meaningful proxy for whether
the compiler (and, transitively, the paper) preserved the actual mechanics of the method rather than a
narrative gloss.

**Compute function.**
```python
import re

# Assumes artifact["method_files"] is a dict[filename -> raw markdown text], possibly empty.
def method_grounding_density(artifact: dict) -> float:
    files = artifact["method_files"]
    if not files:
        return 0.0  # bare constraints-only artifact (e.g. abstract-only source) -> floor case

    version_pat = re.compile(r"\bv?\d+\.\d+(\.\d+)?\b")
    call_pat = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\([^)\n]{0,60}\)")
    param_pat = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[\w.\-]+")
    range_pat = re.compile(r"\b\d+\s?(\.\.|–|-)\s?\d+\b")
    tool_name_pat = re.compile(r"\b[A-Z][a-zA-Z]{2,}(?=[\s,.]|v?\d)")  # capitalized tool-like token

    per_file_scores = []
    for text in files.values():
        words = max(len(text.split()), 1)
        hits = (
            len(version_pat.findall(text))
            + len(call_pat.findall(text))
            + len(param_pat.findall(text))
            + len(range_pat.findall(text))
            + 0.5 * len(tool_name_pat.findall(text))
        )
        density_per_100_words = hits / words * 100
        # logistic-ish squashing: ~4 grounded tokens per 100 words -> ~0.7
        per_file_scores.append(min(density_per_100_words / 6.0, 1.0))

    return sum(per_file_scores) / len(per_file_scores)
```

**What the function does & why.** No method files at all (the "abstract-only source" floor case the
shape doc calls out explicitly) is a hard zero. Otherwise, each method file is scanned for five
families of reproducibility tokens — version numbers, function-call-like syntax, `param=value` pairs,
numeric ranges, and capitalized tool-like names — normalized per 100 words so long, padded files don't
win purely on length, then averaged across files.

**Why it's hard to Goodhart.** Stuffing method text with fake `param=value` pairs and version numbers
to inflate density is detectable in combination: fabricated parameters that don't correspond to any
real tool/heuristic tend to be internally inconsistent with the `Bounds`/`Sensitivity` fields in
`heuristics.md` (Metric 3) and with the boundary conditions in `constraints.md` (Metric 1), whereas
genuine grounding is consistent across all three because it originates from the same source paper.
Fabrication that stays purely inside `method_files` to game this one metric in isolation produces text
that reads as noise (dense jargon with no matching cross-references elsewhere), which a downstream
qualitative check — or a future coherence metric — can flag directly.

---

## 5. Compiler Self-Disclosure Score (data-quality caveats)

**How it signals good science.** The `## Additional caveats surfaced during compilation` subsection is
the artifact's own audit trail — a record of the compiler actively cross-checking the source (does
Table 1's row count match its caption? does the PRISMA diagram's arithmetic reconcile?) rather than
transcribing the paper uncritically. This is a property of the *compilation process's* rigor,
independent of whether the underlying paper itself was rigorous — an artifact that surfaces specific,
named inconsistencies is doing real adversarial verification; an artifact that never does this, across
enough compiled papers, is suspect regardless of how clean any single paper looks.

**Compute function.**
```python
import re

# Assumes artifact["constraints"]["data_quality_caveats"] is a list of markdown-prose
# bullet strings; [] if the subsection is absent entirely.
def self_disclosure_score(artifact: dict) -> float:
    caveats = artifact["constraints"]["data_quality_caveats"]
    if not caveats:
        # Cannot verify from this artifact alone whether absence is warranted (no
        # reconciliation issue existed) or a coverage gap (issue existed, went unflagged).
        # Per the hard constraint, unverifiable absence is scored low, not skipped.
        return 0.15

    named_object_pat = re.compile(
        r"\b(Table|Figure|Fig\.|Section|§|Appendix)\s?\d+", re.I
    )
    numeric_discrepancy_pat = re.compile(r"\b\d+\b.*\b(vs\.?|but|while|vs)\b.*\b\d+\b", re.I)

    scores = []
    for c in caveats:
        has_object = bool(named_object_pat.search(c))
        has_discrepancy = bool(numeric_discrepancy_pat.search(c)) or (
            "**" in c  # bolded named discrepancy per the shape's convention
        )
        scores.append(1.0 if (has_object and has_discrepancy) else (0.5 if has_object or has_discrepancy else 0.15))

    return sum(scores) / len(scores)
```

**What the function does & why.** Absence of the subsection gets a low fixed floor (0.15) rather than
a skip — the metric can't tell, from the artifact alone, whether nothing needed flagging, but per the
tournament rule that ambiguity is scored as a risk, not neutrality. When caveats exist, each is scored
on whether it names a specific object (a table/figure/section number) and whether it states an actual
discrepancy (two numbers or claims put in tension) rather than a vague "some inconsistencies exist."

**Why it's hard to Goodhart.** Fabricating fake self-caveats ("Table 3 has a minor discrepancy") to
farm the high score requires naming specific objects and discrepancies — which, unless they happen to
be true, are trivially checkable against the paper by any downstream reviewer and represent a
reputational risk with no compensating benefit elsewhere. Padding this section costs the compiler
nothing to attempt but is the single easiest of these five things to spot-check against a paper's
actual tables, making it a poor Goodhart target compared to vaguer prose metrics.

---

## Combination

These five metrics are jointly hard to cheaply sweep because they reward specificity in different,
cross-checkable places, and fabricating specificity in one place tends to either fail its own local
check or create detectable incoherence elsewhere. Padding vague assumptions or limitations to raise
their counts fails Metrics 1 and 2 directly (their generic-hedge/anchor filters zero out boilerplate).
Manufacturing heuristics or method-file jargon to win Metrics 3 and 4 produces numeric/technical
content that has no counterpart in the constraints layer's assumptions and boundary conditions —
real grounding is consistent across `constraints.md`, method files, and `heuristics.md` because it all
traces back to the same source paper, while fabricated grounding is generated independently in each
file and tends to diverge. And Metric 5 specifically penalizes the "everything looks clean" artifact
that never admits any internal inconsistency, which is exactly the profile a purely padded, internally
inconsistent artifact would otherwise present if it tried to hide its fabrications by omission. A
paper can't win all five by writing more text in one place; it has to actually preserve traceable,
mutually consistent detail across the whole method layer.
