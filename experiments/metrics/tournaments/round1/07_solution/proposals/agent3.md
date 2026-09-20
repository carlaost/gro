# Proposer 3 — metrics for `logic/solution/` (method layer)

Assumed parsed representation shared by all functions below (a dict-like object built by the ARA
compiler's parser from `constraints.md` + sibling method files):

```python
artifact = {
    "constraints": {
        "boundary_conditions": ["<markdown-prose bullet>", ...],   # [] if section absent
        "assumptions": [{"id": "A1", "text": "<prose>"}, ...],      # [] if section absent
        "known_limitations": {
            "section_ref": "§4.5",           # None if no section anchor given in the heading
            "items": [{"name": "<bold name>", "text": "<prose>"}, ...],
        },
        "additional_caveats": ["<prose>", ...],   # [] if the data-quality-notes subsection is absent
    },
    "method_files": {
        # filename -> raw markdown text (including headings), e.g.
        "study_design.md": "## Cohort\n...",
        "method.md": "## Visium raw processing & QC\n...",
    },  # {} if only constraints.md exists (abstract-only floor case)
    "heuristics": [
        {"id": "H01", "sensitivity": "high", "bounds": "...", "code_ref": ["src/..."], "source": "§3.4"},
        ...
    ],  # [] if heuristics.md absent
}
```

All five functions treat a missing/empty section as computable, low-scoring evidence — never as
"N/A" — per the tournament's hard constraint.

---

## 1. Limitation Traceability & Specificity

**How it signals good science.** A limitation tied to a concrete, checkable locus (a section
number, table, figure, or equation) shows the compiler — and, upstream, the paper — actually
pinned the limitation to a mechanism, not just performed due-diligence theater with a generic
"results may not generalize" sentence. Traceable limitations are falsifiable/auditable by a
downstream reader; untraceable ones are unverifiable rhetoric.

**Compute function.**
```python
import re

def limitation_traceability(artifact: dict) -> float:
    """Assumes artifact['constraints']['known_limitations'] = {'section_ref': str|None,
    'items': [{'name': str, 'text': str}, ...]}. Missing/empty -> 0.0 (penalized, not skipped)."""
    kl = artifact.get("constraints", {}).get("known_limitations", {})
    items = kl.get("items", [])
    if not items:
        return 0.0  # bare "no limitations stated" is itself a red flag per the brief

    locus_pattern = re.compile(
        r"§\s?\d+(\.\d+)?|\bTable\s?\d+|\bFig(ure)?\.?\s?\d+|\bEq(uation)?\.?\s?\d+|\bAppendix\s?[A-Z\d]+",
        re.IGNORECASE,
    )
    header_has_ref = 1.0 if kl.get("section_ref") else 0.0

    traceable = 0
    for it in items:
        text = it.get("text", "") + " " + it.get("name", "")
        if locus_pattern.search(text):
            traceable += 1
    item_ratio = traceable / len(items)

    # Header-level anchor counts for a third of the score; per-item anchors for the rest —
    # a paper can have a good §-anchored heading but still bury vague, unanchored bullets under it.
    return round(0.34 * header_has_ref + 0.66 * item_ratio, 3)
```

**What it does & why.** It regex-scans each `Known limitations` bullet (and the section heading
itself) for a reference to a specific section/table/figure/equation/appendix. It scores the
fraction of bullets that are anchored to something a reader could go check, weighted so that an
anchored heading alone (`## Known limitations (§4.5)`) isn't enough — the individual bullets must
carry their own loci too. An artifact with no limitations at all scores zero rather than being
excluded.

**Why it's hard to Goodhart.** Sprinkling a fake `§2.3` into every bullet is cheap in isolation,
but it does nothing for Metric 3 (assumption falsifiability) or Metric 2 (reproducibility
density), which key off actual concrete/numeric content rather than the mere presence of a
section-symbol token — an artifact that fabricates locus tags without substantive grounding will
look anomalous (high traceability, low density/specificity) when the metrics are read jointly.

---

## 2. Method Reproducibility Grounding Density

**How it signals good science.** Reproducible methods are stated as exact, checkable
parameters — tool name, version, hyperparameter value ("BayesSpace v1.11.0 spatialCluster
(nrep=20000) ... k=9") — not hand-wavy prose. A high density of such quantifiable tokens in the
method files reflects that the compiler could extract, and therefore that the paper actually
reported, concrete operational detail rather than a vague narrative of what was done.

**Compute function.**
```python
import re

def reproducibility_density(artifact: dict) -> float:
    """Assumes artifact['method_files'] = {filename: raw_markdown_text}. Empty dict (abstract-only
    floor case, or a method-file-free artifact) -> 0.0."""
    files = artifact.get("method_files", {})
    if not files:
        return 0.0  # no "how" layer beyond mandatory constraints.md: a stark floor case

    version_pat = re.compile(r"\bv?\d+\.\d+(\.\d+)?\b")
    param_pat = re.compile(r"\b[a-zA-Z_]\w*\s*=\s*[\d.eE+-]+\b")
    named_tool_pat = re.compile(r"\b[A-Z][a-zA-Z]{2,}\s?v?\d")  # e.g. "BayesSpace v1.11"

    total_words, total_hits = 0, 0
    for text in files.values():
        words = re.findall(r"\S+", text)
        total_words += len(words)
        total_hits += (
            len(version_pat.findall(text))
            + len(param_pat.findall(text))
            + len(named_tool_pat.findall(text))
        )
    if total_words == 0:
        return 0.0

    density_per_1000 = 1000 * total_hits / total_words
    # squash to [0,1]; 15 grounded tokens per 1000 words treated as a strong ceiling
    return round(min(density_per_1000 / 15.0, 1.0), 3)
```

**What it does & why.** It counts version strings, `param=value` assignments, and capitalized
tool-names-with-version across every method file, normalizes by total word count so long files
aren't unfairly rewarded, and squashes the resulting density into `[0,1]`. Genuinely quantitative
method sections (omics QC pipelines, statistical model specs) score high; prose-only or
abstract-derived method files score near zero.

**Why it's hard to Goodhart.** Padding a method file with meaningless `x=1` tokens raises this
score cheaply, but the same fabricated numbers won't cohere with Metric 4's genre-keyword check
(numbers dropped into a heading that doesn't structurally belong to that genre look anomalous) and
won't help Metric 1 or 3, which require the numeric/specific content to also be *locus-anchored*
or *assumption-relevant*. Gaming density alone produces a file that's suspicious in isolation
(numeric noise with no corresponding structure), which the other metrics expose.

---

## 3. Assumption Falsifiability

**How it signals good science.** An assumption phrased as a specific, checkable empirical claim
("selecting the single most comprehensive dataset per cohort yields independent nodes — no
patient double-counted") can in principle be verified or refuted. An assumption phrased as an
unfalsifiable platitude ("we assume standard statistical properties hold") cannot be checked by
anyone and signals weak epistemic hygiene — assumptions that can't fail aren't doing honest
epistemic work.

**Compute function.**
```python
import re

def assumption_falsifiability(artifact: dict) -> float:
    """Assumes artifact['constraints']['assumptions'] = [{'id': str, 'text': str}, ...].
    Empty list -> 0.0 (every method makes assumptions; a compiler reporting none is a gap)."""
    assumptions = artifact.get("constraints", {}).get("assumptions", [])
    if not assumptions:
        return 0.0

    hedge_words = re.compile(
        r"\b(generally|typically|usually|roughly|should|may|might|often|reasonably|approximately)\b",
        re.IGNORECASE,
    )
    concrete_pat = re.compile(
        r"\b\d+(\.\d+)?\b|\b(cohort|dataset|patient|sample|estimator|model|variable|node|subject|"
        r"parameter|threshold|classifier|assay)\b",
        re.IGNORECASE,
    )

    scores = []
    for a in assumptions:
        text = a.get("text", "")
        vague = len(hedge_words.findall(text))
        concrete = len(concrete_pat.findall(text))
        # net specificity, floored at 0, saturating so one very dense sentence can't dominate
        scores.append(max(0.0, min(concrete - vague, 4)) / 4.0)

    return round(sum(scores) / len(scores), 3)
```

**What it does & why.** For each assumption bullet it counts hedge/vagueness markers against
concrete-object/numeric markers, floors the net at zero, and averages across all assumptions. A
paper whose assumptions name specific objects and quantities scores near 1; a paper whose
assumptions are generic hand-waving scores near 0; no assumptions at all scores exactly 0.

**Why it's hard to Goodhart.** Loading assumptions with concrete nouns without them being real
falsifiable claims (e.g. "the cohort dataset variable model estimator holds") inflates this score
but produces text with no locus reference (hurting Metric 1 if the assumption is meant to connect
to a limitation) and no coherent structure (hurting Metric 4's genre check, since injected
buzzwords rarely match the surrounding section's real vocabulary distribution). Real falsifiable
assumptions read naturally across all four other metrics; synthetic ones don't.

---

## 4. Genre-Fit Coherence

**How it signals good science.** The compiler is supposed to name and structure method files for
*what the paper actually did* — `architecture.md` for a genuine model, `study_design.md` for a
cohort study — not force a templated file onto the wrong genre (the brief explicitly calls a
`training.md` for a paper that trained no model, or an `architecture.md` for a pure
statistical-synthesis review, a validation-flagged defect). Genuine structural fit is evidence the
transcription is faithful to the source rather than pattern-matched from a template library.

**Compute function.**
```python
import re

GENRE_KEYWORDS = {
    "architecture.md": {"component", "input", "output", "layer", "module", "interaction"},
    "algorithm.md": {"pseudocode", "complexity", "theorem", "algorithm", "step"},
    "training.md": {"epoch", "optimizer", "loss", "learning rate", "batch"},
    "study_design.md": {"cohort", "inclusion", "exclusion", "registration", "search strategy",
                         "reporting standard"},
    "method.md": {"pipeline", "qc", "processing", "clustering", "assay"},
    "heuristics.md": {"rationale", "sensitivity", "bounds"},
    "formalization.md": {"definition", "theorem", "proof", "lemma"},
    "proofs.md": {"proof", "lemma", "theorem", "qed"},
    "design.md": {"design", "rationale", "tradeoff"},
}

def genre_fit_coherence(artifact: dict) -> float:
    """Assumes artifact['method_files'] = {filename: raw_markdown_text}. Files with names not in
    GENRE_KEYWORDS are treated as fully generic (no penalty, no credit -> neutral 0.5 fit).
    Empty method_files (abstract-only case) -> 0.0."""
    files = artifact.get("method_files", {})
    if not files:
        return 0.0

    fits = []
    for fname, text in files.items():
        keywords = GENRE_KEYWORDS.get(fname.lower())
        if keywords is None:
            fits.append(0.5)
            continue
        lower_text = text.lower()
        hit_count = sum(1 for kw in keywords if kw in lower_text)
        fits.append(min(hit_count / max(1, len(keywords) * 0.4), 1.0))  # need ~40% of keyword set

    return round(sum(fits) / len(fits), 3)
```

**What it does & why.** For each conventionally-named method file, it checks how much of that
genre's expected vocabulary actually shows up in the file's content, on the theory that a file
correctly named for its genre will naturally contain that genre's terms, while a
templated-but-wrong file (e.g. `architecture.md` slapped onto a review paper) will conspicuously
lack them. Files with no method content at all score zero, reflecting the "abstract-only" floor
case where the "how" layer is missing entirely.

**Why it's hard to Goodhart.** Keyword-stuffing a file to pass this check (e.g. adding "component,
input, output, layer" to a review's `architecture.md`) will simultaneously wreck Metric 2's
reproducibility density (those keywords aren't tied to real version/parameter numbers, dragging
the density-per-relevant-heading signal down when cross-read) and look structurally incoherent
next to the paper's actual `study_design.md` content, which a joint read easily flags as
inconsistent genre signals within the same artifact.

---

## 5. Heuristic Capture Completeness

**How it signals good science.** `heuristics.md`'s correct absence for most papers is fine and
must not be penalized generically — but its absence *is* a defect when the paper visibly
discusses implementation tricks/gotchas/tuned sensitivities and none were captured. Good science
here means the compiler faithfully surfaces the "gotchas" that materially affect
reproducibility/robustness, rather than silently dropping inconvenient implementation detail.

**Compute function.**
```python
import re

TRICK_SIGNAL_PAT = re.compile(
    r"\bin practice\b|\bto stabilize\b|\bempirically\b|\bwe found\b|\bhyperparameter\b|"
    r"\bwe found it helpful\b|\bablat\w*\b|\bworkaround\b|\btuned\b|\bcritical for convergence\b|"
    r"\bsensitiv\w* to\b|\bgotcha\b",
    re.IGNORECASE,
)
PLACEHOLDER = "not specified"

def heuristic_capture_completeness(artifact: dict) -> float:
    """Assumes artifact['method_files'] = {filename: text} and artifact['heuristics'] = [
    {'id','sensitivity','bounds','code_ref','source'}, ...] (possibly [])."""
    method_text = " ".join(artifact.get("method_files", {}).values())
    implied = len(TRICK_SIGNAL_PAT.findall(method_text))
    heuristics = artifact.get("heuristics", [])

    if implied > 0 and not heuristics:
        return 0.0  # paper visibly signals tricks; none captured -> penalized, not "N/A"

    if not heuristics:
        # correctly absent (no trick-signal language found) -> neutral-high, not perfect,
        # since we can't fully rule out an under-sensitive keyword scan
        return 0.7

    # heuristics present: score completeness of each block's fields
    field_scores = []
    for h in heuristics:
        filled = 0
        total = 4
        for field in ("sensitivity", "bounds", "code_ref", "source"):
            val = h.get(field)
            if val and str(val).strip().lower() != PLACEHOLDER and val != []:
                filled += 1
        field_scores.append(filled / total)
    completeness = sum(field_scores) / len(field_scores)

    # if the paper signals many more tricks than were captured, discount proportionally
    coverage_ratio = min(len(heuristics) / max(1, implied), 1.0) if implied else 1.0
    return round(0.5 * completeness + 0.5 * coverage_ratio, 3)
```

**What it does & why.** It scans the method files for language that typically accompanies stated
implementation tricks ("empirically we found...", "tuned", "critical for convergence", etc.) as a
proxy for "the paper visibly discusses gotchas." If that signal is present but `heuristics.md` is
empty, the artifact is penalized directly (missing input as evidence of a gap, per the hard
constraint) rather than skipped. If heuristics are present, it separately scores how completely
each `H##` block filled its `Sensitivity`/`Bounds`/`Code ref`/`Source` fields (vs. "Not specified"
placeholders) and how many of the implied tricks got captured at all.

**Why it's hard to Goodhart.** Avoiding trick-signal vocabulary in method files to dodge the
"implied tricks" trigger means writing vaguer, less specific method prose — which directly lowers
Metric 2's reproducibility density and Metric 3's concrete-language assumptions score. Conversely,
padding `heuristics.md` with junk `H##` blocks that use "Not specified" for every field to look
"present" gets caught by the completeness sub-score, which explicitly discounts placeholder
fields.

---

## Combination

These five metrics all key off the same underlying scientific virtue — *specific, checkable,
locus-tied content vs. generic templated boilerplate* — but they apply it to five different
surfaces (limitations, method-file numeric detail, assumptions, file/genre structure, and
implementation-trick disclosure) that are cheap to fake individually but expensive to fake
jointly. Injecting fake section anchors (to win #1) produces text with no matching numeric
grounding (hurting #2) or genre-appropriate vocabulary (hurting #4). Keyword- or number-stuffing
to win #2 or #4 creates content that reads as structurally incoherent or unmoored from any real
locus (hurting #1 and #3). Writing deliberately vague, hedge-free-but-still-generic prose to dodge
the trick-signal detector in #5 flattens the specific/numeric language that #2 and #3 reward. A
paper that actually wants to win all five has to do the real thing: report concrete, versioned,
section-anchored methods and honestly disclose the implementation sensitivities that go with them.
