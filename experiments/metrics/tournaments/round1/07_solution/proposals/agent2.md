# Proposal — `logic/solution/` (method layer) — agent2

Input assumption shared by all functions below: the artifact is parsed into a dict roughly of this shape
(fields may be `None`/absent, which each function must handle per the hard constraint — missing input is
penalized, never skipped):

```python
parsed = {
    "constraints": {
        "boundary_conditions": [str, ...],                 # bullets
        "assumptions": [{"id": "A1", "text": str}, ...],
        "known_limitations": [{"name": str, "text": str}, ...],
        "data_quality_caveats": [str, ...] | None,          # "Additional caveats..." subsection, if present
    } | None,
    "method_files": {"study_design.md": "<raw markdown>", "method.md": "<raw markdown>", ...},  # {} if none
    "heuristics": [{"id": "H01", "rationale": str, "sensitivity": str, "bounds": str,
                     "code_ref": [str, ...], "source": str}, ...] | None,
    "evidence_flags": [str, ...] | None,   # internal-consistency issues the compiler noted in evidence/
                                            # (table/figure reconciliation problems); None = not supplied
}
```

---

## 1. Concrete-Referent Density

**How it signals good science.** A limitation or assumption that names no concrete referent — no
dataset, cohort, statistic, parameter, method, or quantity — is scientifically inert: it cannot be used
by a reader to decide when to distrust the result. "Results may not generalize" is compatible with every
paper ever written and commits the author to nothing checkable. Good science writes boundary conditions
and assumptions that are falsifiable and specific to *this* work, because that specificity is what lets
a downstream reader (or agent) actually apply the caveat.

**Compute function.**
```python
import re

GENERIC_PHRASES = [
    r"may not generalize", r"further (research|work) (is )?needed",
    r"should be interpreted with caution", r"limited sample size",
    r"future studies", r"inherent limitations", r"results may vary",
]
CONCRETE_SIGNALS = [
    r"\d",                                   # any digit: counts, p-values, versions, %s
    r"\b[A-Z][a-zA-Z]*\d+\b",                 # e.g. p-tau217, K562
    r"\b[A-Z]{2,}\b",                         # acronyms: ADNI, PRISMA, AUC
    r"§\s*\d", r"\bTable\s+\d", r"\bFigure\s+\d", r"\bEq\.?\s*\d",
]

def concrete_referent_density(parsed: dict) -> float:
    c = parsed.get("constraints")
    if not c:
        return 0.0  # constraints.md is mandatory-core; total absence is a floor score
    bullets = list(c.get("boundary_conditions") or [])
    bullets += [a["text"] for a in (c.get("assumptions") or [])]
    bullets += [l["text"] for l in (c.get("known_limitations") or [])]
    bullets += list(c.get("data_quality_caveats") or [])
    if not bullets:
        return 0.0  # thin-to-empty constraints.md: penalize, don't skip
    scores = []
    for b in bullets:
        has_concrete = any(re.search(p, b) for p in CONCRETE_SIGNALS)
        is_generic = any(re.search(p, b, re.IGNORECASE) for p in GENERIC_PHRASES)
        if is_generic and not has_concrete:
            scores.append(0.0)
        elif has_concrete:
            scores.append(1.0)
        else:
            scores.append(0.3)  # neither flagged generic nor concrete: mediocre prose
    return sum(scores) / len(scores)
```

**What it does & why.** It walks every bullet across boundary conditions, assumptions, limitations, and
data-quality caveats, and scores each 0/0.3/1 depending on whether it matches a blocklist of generic
hedge-phrases, a concrete-referent pattern (numbers, named acronyms/isoforms, section/table/figure
pointers), both, or neither. The mean over all bullets is the artifact score. An artifact with no
constraints content at all — or a `constraints.md` that is present but empty — scores 0, satisfying the
hard constraint rather than returning N/A.

**Why it's hard to Goodhart.** You cannot win this by sprinkling numbers into the constraints file, because
Metric 4 (grounding overlap, below) separately checks whether those "concrete" referents actually recur in
the method files — fabricated specificity that doesn't connect to the paper's real method is caught there.
Padding with more bullets doesn't help either since the score is a mean, not a count.

---

## 2. Data-Quality-Caveat Coverage (cross-check against evidence-layer flags)

**How it signals good science.** The shape doc itself documents that the compiler independently notices
internal inconsistencies in the source (a table's row count contradicting its caption, PRISMA arithmetic
not reconciling) and is *supposed* to surface them in `constraints.md`'s "Additional caveats surfaced
during compilation" subsection specifically so downstream agents don't over-trust the paper's own process
counts. A method-layer artifact that silently drops known inconsistencies is actively worse than one that
never had a compiler check for them — it launders an inconsistency into apparent reliability.

**Compute function.**
```python
import re

def data_quality_caveat_coverage(parsed: dict) -> float:
    # Assumes the parsed bundle also carries `evidence_flags`: the list of internal-consistency
    # issues the compiler detected while building the evidence/ layer for this same paper.
    evidence_flags = parsed.get("evidence_flags")
    if evidence_flags is None:
        # We cannot verify whether known issues were surfaced. Per the hard constraint this is a
        # penalized state, not a skip — treat "can't verify" as evidence of an incomplete pipeline.
        return 0.2
    c = parsed.get("constraints") or {}
    caveats = c.get("data_quality_caveats") or []
    if not evidence_flags:
        # No known inconsistencies exist; a caveats subsection is optional here, don't force one.
        return 1.0 if not caveats else 0.9  # slight ding for caveats without any known flag to explain
    if not caveats:
        return 0.0  # known inconsistencies exist and none were surfaced at all
    caveat_text = " ".join(caveats).lower()

    def flag_tokens(flag: str):
        # crude entity extraction: numbers and capitalized/acronym tokens named in the flag
        return set(re.findall(r"\d+|\b[A-Z][a-zA-Z]{2,}\b", flag))

    matched = 0
    for flag in evidence_flags:
        toks = flag_tokens(flag)
        if toks and any(t.lower() in caveat_text for t in toks):
            matched += 1
    return matched / len(evidence_flags)
```

**What it does & why.** It treats the evidence layer's own internal-consistency flags as ground truth for
"issues that should have been surfaced," then checks whether each flag's key tokens (row counts, named
tables, acronyms) actually appear in `constraints.md`'s data-quality-caveats bullets. Full coverage scores
1.0; silently dropped flags drag the score toward 0. Absence of the `evidence_flags` input itself is scored
low (0.2) rather than skipped, satisfying the hard constraint even when the surrounding pipeline hasn't
wired the cross-check up.

**Why it's hard to Goodhart.** Gaming requires either (a) copying evidence-layer flag text verbatim into
`constraints.md`, which is exactly the desired behavior, not gaming, or (b) inventing caveats that don't
correspond to any real flag — but Metric 1 penalizes any resulting bullets that are generic filler rather
than concretely matched, and Metric 4 penalizes caveats whose named objects don't recur anywhere in the
method files.

---

## 3. Method-Genre Coherence & Heuristics-Omission Audit

**How it signals good science.** The shape doc is explicit that the compiler is supposed to pick file
names that describe *this paper's actual method structure* — an `architecture.md`/`training.md` forced
onto a paper that trained no model is itself flagged as a defect (Seal Level 1, §2), and a paper with a
visible "implementation details" style section whose tricks aren't captured in `heuristics.md` is a
coverage gap. Good science here means the method-layer *shape itself* is honest about what kind of paper
this is — a shape/content mismatch is evidence the compiler (or paper) is not being read carefully.

**Compute function.**
```python
import re

ML_GENRE_FILES = {"architecture.md", "algorithm.md", "training.md", "model.md"}
ML_KEYWORDS = [r"\btrain(ed|ing)?\b", r"\bhyperparameter", r"\bepoch", r"\bneural", r"\blayer\b",
               r"\bloss function", r"\bgradient", r"\bfine[- ]tun"]
IMPL_TRICK_KEYWORDS = [r"\btrick", r"\bworkaround", r"\bempirically (found|observed)",
                        r"\bablat", r"\bwe found that", r"\bin practice", r"\bwarm[- ]?(up|start)"]

def method_genre_coherence(parsed: dict) -> float:
    method_files = parsed.get("method_files") or {}
    heuristics = parsed.get("heuristics")
    penalties = 0
    checks = 0

    for fname, text in method_files.items():
        if fname in ML_GENRE_FILES:
            checks += 1
            if not any(re.search(k, text, re.IGNORECASE) for k in ML_KEYWORDS):
                penalties += 1  # file name promises ML content the prose doesn't deliver

    all_method_text = " ".join(method_files.values())
    trick_hits = sum(len(re.findall(k, all_method_text, re.IGNORECASE)) for k in IMPL_TRICK_KEYWORDS)
    checks += 1
    if trick_hits >= 2 and not heuristics:
        penalties += 1  # paper visibly discusses implementation tricks; none were captured

    if checks == 0:
        return 0.0  # no method files at all to check genre against: floor case (abstract-only source)
    return max(0.0, 1.0 - penalties / checks)
```

**What it does & why.** For every method file whose *name* signals an ML/architecture genre, it checks the
file's actual prose for ML-specific vocabulary; a name/content mismatch counts as a penalty. Separately, it
scans all method-file prose for language that typically accompanies implementation tricks/gotchas ("we
found that...", "ablation", "warm-up") and, if that language appears at least twice but no `heuristics.md`
exists, counts a second penalty. The final score is `1 - penalties/checks`, and an artifact with zero
method files (the abstract-only floor case the shape doc calls out) scores 0 rather than being skipped.

**Why it's hard to Goodhart.** You can't fix a genre mismatch by deleting the ML keywords check's target
words from a real architecture description — doing so would make the description less informative and
tank Metric 1 (concrete-referent density) and Metric 4 (grounding overlap) since architecture files are
where the concrete method vocabulary is supposed to live. You also can't dodge the heuristics-omission
check by scrubbing trick-language from the method prose, because that directly removes real methodological
content the paper stated, which is the thing Metric 4 also expects to find echoed from `constraints.md`.

---

## 4. Assumption/Boundary Grounding Overlap

**How it signals good science.** Assumptions and boundary conditions that are genuinely earned from this
paper's actual method should share named entities with the method files — the same cohort, platform,
statistic, or model. A `constraints.md` that reads like a template pasted across papers (generic hedge
language, no shared vocabulary with the paper's own method description) signals the constraints weren't
derived from the actual work.

**Compute function.**
```python
import re

ENTITY_PATTERN = re.compile(r"\b[A-Z][a-zA-Z]{2,}\d*\b|\b\d+(\.\d+)?%?\b")

def extract_entities(text: str) -> set:
    return {m.group(0).lower() for m in ENTITY_PATTERN.finditer(text)}

def assumption_boundary_grounding_overlap(parsed: dict) -> float:
    c = parsed.get("constraints")
    method_files = parsed.get("method_files") or {}
    if not c:
        return 0.0
    constraint_text = " ".join(
        list(c.get("boundary_conditions") or [])
        + [a["text"] for a in (c.get("assumptions") or [])]
        + [l["text"] for l in (c.get("known_limitations") or [])]
    )
    constraint_entities = extract_entities(constraint_text)
    if not constraint_entities:
        return 0.0  # no named referents at all in constraints: nothing to ground

    if not method_files:
        # Abstract-only source per the shape doc's stark floor case: no method file exists to
        # ground anything against. This is missing input, not inapplicability — penalize.
        return 0.1

    method_entities = extract_entities(" ".join(method_files.values()))
    overlap = constraint_entities & method_entities
    return len(overlap) / len(constraint_entities)
```

**What it does & why.** It extracts capitalized/alphanumeric tokens and numeric quantities from
`constraints.md` and separately from all method files, then measures what fraction of the
constraint-layer's named entities actually recur in the method-layer prose. High overlap means the
constraints are substantively tied to this paper's real method; low overlap suggests boilerplate.
Zero named entities in `constraints.md`, or a total absence of method files to check against, both score
near the floor rather than being skipped.

**Why it's hard to Goodhart.** Cheaply inflating overlap by copy-pasting method-file jargon into
`constraints.md` verbatim would very likely also satisfy Metric 1's concrete-referent check and Metric 2's
if it happens to touch a genuinely flagged inconsistency — but it does nothing to raise the *quality* of
the limitation itself, and reviewers/other metrics reading the prose (or a human auditor) would see
transplanted phrases with no analytic content, which is exactly the kind of degenerate case Metric 3 would
also flag if it hollows out the method files' own genre-specific vocabulary in the process.

---

## Combination

These four metrics are jointly hard to game because they pull in different, partially opposed directions.
Padding `constraints.md` with invented specifics inflates Metric 1 but is caught by Metric 4 unless those
specifics genuinely recur in the method files — and making them recur requires real grounding, not
cosmetic edits. Copying evidence-layer flags verbatim to win Metric 2 only helps if the copied text also
carries concrete referents (Metric 1) and shares vocabulary with the method files (Metric 4) — an empty
gesture ("there were data quality issues") fails Metric 1. Renaming or restructuring method files to dodge
Metric 3's genre check risks removing exactly the specific technical vocabulary that Metrics 1 and 4 reward
in `constraints.md`. In short: winning all four requires the constraints file to be specific, faithful to
compiler-detected inconsistencies, and lexically continuous with a genre-honest method-file set — which is
just what a well-compiled method layer looks like.
