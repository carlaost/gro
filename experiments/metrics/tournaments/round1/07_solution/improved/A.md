# Proposal — `logic/solution/` (method layer) — agent2

## Changes from stage 1

Stage-1 critique ranked this set #1 but flagged three concrete faults. All three are fixed below;
nothing else was touched.

1. **M4's `ENTITY_PATTERN` was too loose** (`\b[A-Z][a-zA-Z]*\d*\b` matched sentence-initial capitals
   and generic nouns like "Results", "Table", "Cohort" that trivially recur in method files, inflating
   overlap for free). Replaced with `extract_weighted_entities`: acronyms must now be **all-caps**
   (not just initial-cap), a hard-coded `GENERIC_STRUCTURAL_WORDS` blocklist drops boilerplate
   scientific-prose nouns outright, and ubiquitous cross-domain acronyms (AUC, CI, SD, ...) are
   down-weighted to 0.3 rather than counted at full strength — a genuine rarity/IDF-style discount
   without needing an external corpus.
2. **No dedicated assumption-quality metric** — assumptions were only folded into M1's concrete-referent
   count, so a numbered assumption with a number in it scored the same whether or not anyone traced what
   breaks if it's false. Added **Metric 5, Assumption→Consequence Traceability**, borrowing agent1's
   examined-rigor idea but hardening its known flaw: a near-duplicate (Jaccard-similarity) filter blocks
   verbatim re-listing of the assumption text from counting as "tracing a consequence," and a match now
   requires *both* an ID/entity link back to the assumption *and* explicit failure/violation language.
3. **M2's empty-`evidence_flags` case returned 1.0 unconditionally**, which could not distinguish "the
   evidence-layer scan genuinely ran and found nothing" from "the flag list was never populated by the
   pipeline." Added an explicit `evidence_check_ran` input; only a confirmed-ran scan with zero flags now
   earns 1.0. An unconfirmed or unpopulated state is penalized at 0.2, matching the existing
   `evidence_flags is None` treatment, per the hard constraint (never reward an unverifiable state as if
   it were a verified pass).

The input-assumption dict below gains one field (`evidence_check_ran`) to support fix 3; everything else
in the shape is unchanged.

---

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
    "evidence_check_ran": bool,            # True iff the evidence-layer internal-consistency scan actually
                                            # executed for this artifact (independent of what it found).
                                            # Defaults to False if absent — an unconfirmed scan must not be
                                            # treated as equivalent to a confirmed zero-flags result.
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
    # issues the compiler detected while building the evidence/ layer for this same paper, plus
    # `evidence_check_ran`: an explicit attestation that the cross-check scan actually executed.
    evidence_flags = parsed.get("evidence_flags")
    check_ran = bool(parsed.get("evidence_check_ran"))
    c = parsed.get("constraints") or {}
    caveats = c.get("data_quality_caveats") or []

    if not check_ran or evidence_flags is None:
        # Stage-1 fix: an empty evidence_flags list is indistinguishable from "the scan never ran"
        # unless the pipeline explicitly attests the scan executed. Treat "never wired up" and
        # "claims to have run but unconfirmed" identically as an unverifiable state — penalized,
        # not skipped, and never awarded the 1.0 a *confirmed* zero-flags result earns.
        return 0.2
    if not evidence_flags:
        # Scan genuinely ran (check_ran=True, flags list present) and found zero inconsistencies.
        # A caveats subsection is optional here, don't force one.
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
1.0, but only once `evidence_check_ran` confirms the scan actually executed; silently dropped flags drag
the score toward 0. Both a totally unwired pipeline (`evidence_flags is None`) and an unconfirmed scan
(`evidence_check_ran` false, regardless of what the flags list contains) score 0.2 rather than being
skipped or accidentally credited with a perfect "nothing to report" score.

**Why it's hard to Goodhart.** Gaming requires either (a) copying evidence-layer flag text verbatim into
`constraints.md`, which is exactly the desired behavior, not gaming, or (b) inventing caveats that don't
correspond to any real flag — but Metric 1 penalizes any resulting bullets that are generic filler rather
than concretely matched, and Metric 4 penalizes caveats whose named objects don't recur anywhere in the
method files. Falsely asserting `evidence_check_ran=True` to try to claim the 1.0 zero-flags path doesn't
help either: it only pays off if `evidence_flags` is also fabricated as empty, which is a pipeline-level
lie outside what content-authoring can influence, and is exactly the kind of unverifiable claim the metric
is designed to price at 0.2, not 1.0.

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

# Stage-1 fix: the old pattern `\b[A-Z][a-zA-Z]*\d*\b` matched any sentence-initial capital
# ("Results", "Table", "Cohort") with zero digits required, which trivially recurs across
# boilerplate scientific prose and inflated overlap for free. Distinctive entities now require
# either true ALL-CAPS acronym form, an embedded digit, or a numeric quantity — plus a blocklist
# and a down-weighting table stand in for corpus-level IDF without needing an external corpus.

GENERIC_STRUCTURAL_WORDS = {
    "table", "figure", "section", "study", "studies", "results", "result",
    "discussion", "introduction", "method", "methods", "conclusion", "conclusions",
    "cohort", "cohorts", "data", "dataset", "datasets", "analysis", "analyses",
    "model", "models", "group", "groups", "baseline", "sample", "samples",
    "patient", "patients", "outcome", "outcomes", "measure", "measures",
}
COMMON_ACRONYMS_WEIGHT = {  # ubiquitous cross-domain acronyms: weak evidence of real grounding
    "AUC": 0.3, "CI": 0.3, "SD": 0.3, "SE": 0.3, "IQR": 0.3, "AI": 0.3,
    "ML": 0.3, "US": 0.3, "UK": 0.3, "ID": 0.3, "QC": 0.3, "OR": 0.3,
}

ACRONYM_PATTERN = re.compile(r"\b[A-Z]{2,}\b")                    # ADNI, PRISMA, MRI — true acronyms only
ALPHANUM_ID_PATTERN = re.compile(r"\b[a-zA-Z]+-?\d[\w.\-]*\b")     # p-tau217, K562, BayesSpace-v1.11.0
NUMERIC_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")               # counts, p-values, percentages

def extract_weighted_entities(text: str) -> dict:
    """Extract distinctive (non-generic) entities from text, each mapped to a rarity weight.
    Acronyms must be ALL-CAPS (not merely initial-cap), so ordinary capitalized prose nouns
    ("Results", "Table", "Cohort") never qualify by construction. The blocklist is a second line of
    defense against generic scientific-prose nouns that slip through the alphanumeric/numeric
    channels (e.g. a stray "24-hour"). Ubiquitous cross-domain acronyms are down-weighted to 0.3
    rather than treated as full-strength evidence of paper-specific grounding."""
    entities = {}
    for pat in (ACRONYM_PATTERN, ALPHANUM_ID_PATTERN, NUMERIC_PATTERN):
        for m in pat.finditer(text):
            tok = m.group(0)
            key = tok.lower()
            if key in GENERIC_STRUCTURAL_WORDS:
                continue
            weight = COMMON_ACRONYMS_WEIGHT.get(tok.upper(), 1.0)
            entities[key] = max(entities.get(key, 0.0), weight)
    return entities

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
    constraint_entities = extract_weighted_entities(constraint_text)
    if not constraint_entities:
        return 0.0  # no named referents at all in constraints: nothing to ground

    if not method_files:
        # Abstract-only source per the shape doc's stark floor case: no method file exists to
        # ground anything against. This is missing input, not inapplicability — penalize.
        return 0.1

    method_entities = extract_weighted_entities(" ".join(method_files.values()))
    total_weight = sum(constraint_entities.values())
    matched_weight = sum(w for e, w in constraint_entities.items() if e in method_entities)
    return matched_weight / total_weight
```

**What it does & why.** It extracts distinctive, non-generic tokens (true acronyms, alphanumeric IDs,
numeric quantities) from `constraints.md` and separately from all method files, weights ubiquitous
cross-domain acronyms down to 0.3, and measures the weighted fraction of the constraint-layer's named
entities that actually recur in the method-layer prose. High overlap means the constraints are
substantively tied to this paper's real method; low overlap suggests boilerplate. Zero named entities in
`constraints.md`, or a total absence of method files to check against, both score near the floor rather
than being skipped.

**Why it's hard to Goodhart.** Cheaply inflating overlap by copy-pasting method-file jargon into
`constraints.md` verbatim would very likely also satisfy Metric 1's concrete-referent check and Metric 2's
if it happens to touch a genuinely flagged inconsistency — but it does nothing to raise the *quality* of
the limitation itself, and reviewers/other metrics reading the prose (or a human auditor) would see
transplanted phrases with no analytic content, which is exactly the kind of degenerate case Metric 3 would
also flag if it hollows out the method files' own genre-specific vocabulary in the process. Padding with
generic capitalized words no longer helps at all, since they are excluded outright or capped at 0.3 weight
rather than counted as full-strength matches.

---

## 5. Assumption→Consequence Traceability

**How it signals good science.** Naming an assumption with a number in it (rewarded by Metric 1) is not
the same as having *examined* it. Real methodological rigor means the author (or compiler, faithfully
transcribing the author) can say what specifically breaks — which conclusion weakens, which comparison
becomes invalid, which bias is introduced — if the assumption doesn't hold. An assumption that is stated
and never revisited anywhere else in `constraints.md` is decorative: it signals awareness without
examination. This is the deepest science signal in this set because it distinguishes an author who
thought through the assumption's failure mode from one who is pattern-matching "papers have an assumptions
section."

**Compute function.**
```python
import re

FAILURE_CUE_PHRASES = [
    r"\bif\b.{0,60}\b(not|fails?|violat\w*|does(?:n't| not) hold|were false)\b",
    r"\bviolat\w*", r"\bwould invalidat\w*",
    r"\bmay (overstate|understate|bias|confound|inflate|deflate)\w*",
    r"\bcompromis\w*", r"\bno longer (hold|applies?)\b", r"\bbreaks? down\b", r"\bundermin\w*",
]

def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def _is_near_duplicate(a_text: str, b_text: str, threshold: float = 0.6) -> bool:
    # Stage-1 fix: agent1's analogous metric credited "2 of first-6 words" overlap, which a
    # verbatim re-listing of the assumption trivially satisfies. Full-text Jaccard similarity
    # over all tokens is much harder to satisfy by copy-paste while genuinely restating, and
    # explicitly disqualifies a candidate from counting as a traced consequence.
    ta, tb = _tokenize(a_text), _tokenize(b_text)
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= threshold

def assumption_consequence_traceability(parsed: dict) -> float:
    c = parsed.get("constraints")
    if not c:
        return 0.0  # constraints.md is mandatory-core; total absence is a floor score
    assumptions = c.get("assumptions") or []
    if not assumptions:
        return 0.0  # constraints.md present but no assumptions traced at all: penalize, don't skip

    candidate_texts = [l["text"] for l in (c.get("known_limitations") or [])]
    candidate_texts += list(c.get("boundary_conditions") or [])

    traced = 0
    for a in assumptions:
        a_id = a.get("id", "")
        a_text = a.get("text", "")
        a_entities = extract_weighted_entities(a_text)
        found = False
        for cand in candidate_texts:
            if _is_near_duplicate(a_text, cand):
                continue  # re-listing the assumption verbatim is not tracing a consequence
            references_id = bool(a_id) and re.search(re.escape(a_id) + r"\b", cand) is not None
            shares_entity = bool(a_entities) and any(
                e in extract_weighted_entities(cand) for e in a_entities
            )
            has_failure_cue = any(re.search(p, cand, re.IGNORECASE) for p in FAILURE_CUE_PHRASES)
            if has_failure_cue and (references_id or shares_entity):
                found = True
                break
        if found:
            traced += 1
    return traced / len(assumptions)
```

**What it does & why.** For every numbered assumption, it searches the limitations and boundary-condition
bullets for a candidate consequence: text that (a) is not a near-duplicate of the assumption itself, (b)
either names the assumption's ID directly or shares a distinctive entity with it (reusing Metric 4's
weighted-entity extractor, so the linkage has to be substantive, not a stray shared common word), and (c)
contains explicit failure/violation language describing what would go wrong. An assumption satisfying all
three counts as traced; the score is the fraction of assumptions traced. An artifact with a populated
`constraints.md` but zero assumptions, or zero traced consequences, scores 0 rather than N/A.

**Why it's hard to Goodhart.** The near-duplicate filter directly blocks the cheapest attack — re-listing
the assumption's own text as a "limitation" — from counting at all. Faking the ID/entity link without
duplicating text requires writing a *new* sentence that shares real vocabulary with the assumption, which
either (i) genuinely engages with the assumption's failure mode, the desired behavior, or (ii) drags in
distinctive entities that don't actually connect to anything in the method files, which Metric 4 catches
independently. Padding limitations with generic failure-cue phrases ("this may bias results") without any
ID/entity linkage doesn't help either, since the metric requires both cue language *and* linkage, and
content-free cue phrases are exactly the kind of bullet Metric 1 already scores near zero.

---

## Combination

These five metrics are jointly hard to game because they pull in different, partially opposed directions.
Padding `constraints.md` with invented specifics inflates Metric 1 but is caught by Metric 4 unless those
specifics genuinely recur in the method files — and making them recur requires real grounding, not
cosmetic edits, and generic filler no longer even registers as a specific entity under Metric 4's hardened
extractor. Copying evidence-layer flags verbatim to win Metric 2 only helps if the copied text also
carries concrete referents (Metric 1) and shares vocabulary with the method files (Metric 4) — an empty
gesture ("there were data quality issues") fails Metric 1, and falsely claiming the scan ran doesn't help
without the flags to back it up. Renaming or restructuring method files to dodge Metric 3's genre check
risks removing exactly the specific technical vocabulary that Metrics 1 and 4 reward in `constraints.md`.
Metric 5 closes the remaining gap the other four shared: an assumption could previously earn full marks by
merely containing a number, with no examination of its failure mode; now a numbered-but-unexamined
assumption is visibly incomplete, and the cheapest way to fake examination — re-listing the assumption as
its own "consequence" — is explicitly disqualified by the duplicate filter, forcing any credit-seeking edit
to also satisfy Metric 4's entity linkage. In short: winning all five requires the constraints file to be
specific, faithful to compiler-detected inconsistencies, examined for what each assumption's failure would
break, and lexically continuous with a genre-honest method-file set — which is just what a well-compiled
method layer looks like.
