# Proposer #4 — metrics for `logic/concepts.md`

Assumed parsed shape for all functions below: `concepts` is a list of dicts, one per
`## {Term}` section, each with keys `term` (str), `notation` (str, `"—"` if none),
`definition` (str), `boundary` (str, `"Not specified in paper"` if absent), and
`related` (list of str, the comma-split Related-concepts text). An empty/missing
`concepts.md` is represented as `concepts == []`.

---

## 1. Boundary-Condition Substantiveness (BCS)

**How it signals good science.** A term's boundary conditions are where a paper
declares the limits of its own claims — when a definition applies, when it breaks,
what it assumes. Papers that do careful science tend to know (and state) where their
constructs stop being valid; papers that don't have usually never interrogated the
question. Real boundary text uses conditional language ("requires," "only when,"
"assumes") and has enough content to be a genuine limiting clause, not a stock phrase.

**Compute function.**
```python
def boundary_condition_substantiveness(concepts):
    """
    Assumes: concepts is a list of dicts with keys
      'term', 'notation', 'definition', 'boundary', 'related' (list[str]).
    Missing artifact (empty list) is scored 0.0, per the hard constraint.
    """
    if not concepts:
        return 0.0

    GENERIC_MARKERS = {"not specified in paper", "n/a", "none", "not applicable", "-", "—", ""}
    CONDITIONAL_CUES = ["when", "if ", "requires", "assumes", "applies", "unless",
                         "only if", "does not apply", "limited to", "restricted to",
                         "under", "provided that"]

    scores = []
    generic_count = 0
    for c in concepts:
        b = (c.get('boundary') or "").strip().lower()
        if b in GENERIC_MARKERS or len(b) < 15:
            scores.append(0.0)
            generic_count += 1
            continue
        cue_hits = sum(1 for cue in CONDITIONAL_CUES if cue in b)
        length_score = min(len(b) / 200.0, 1.0)
        cue_score = min(cue_hits / 2.0, 1.0)
        scores.append(0.5 * length_score + 0.5 * cue_score)

    base = sum(scores) / len(scores)
    frac_generic = generic_count / len(concepts)
    # A near-universal "Not specified" is a shallow-read signal, not honest absence
    # (a genuinely simple paper varies which terms lack boundaries — it doesn't
    # blank out all of them uniformly).
    if frac_generic >= 0.8:
        base *= 0.3
    return base
```

**What the function does & why.** For each concept it checks whether the boundary
field is a stock placeholder or too short to carry information; if so it scores 0 for
that entry. Otherwise it rewards length (up to a cap) and the presence of genuine
conditional/limiting language, and averages across concepts. It then applies an extra
multiplicative penalty if ≥80% of entries are the generic placeholder — because a
document where almost nothing has a stated boundary reads as an extraction that never
looked, not a paper that's simply well-bounded everywhere.

**Why it's hard to Goodhart.** Padding every boundary field with a long sentence
containing "when"/"requires" without real content is detectable by the sibling
distinctiveness metric (#3) as templated, near-duplicate text across concepts — so
gaming this one in bulk collides with that one. Writing one genuinely specific,
non-formulaic boundary per concept is exactly the desired behavior, so there's no
cheap uniform trick that survives both metrics.

---

## 2. Concept Graph Coherence (CGC)

**How it signals good science.** Genuine technical vocabulary in a paper is
relational — terms interlock (a method presupposes an object, an object is measured by
an instrument, etc.). A compiler that actually understood the paper's conceptual
structure will produce `Related concepts` links that (a) point to other real headings
in the same document, (b) form a reasonably dense, partly reciprocal web, and (c)
leave few concepts totally isolated. A glossary of disconnected, independently-defined
terms is a weaker signal of genuine understanding than an interconnected vocabulary.

**Compute function.**
```python
def concept_graph_coherence(concepts):
    """
    Assumes: concepts as above. Builds a directed graph from each concept's 'related'
    list via case-insensitive substring matching against the set of declared term
    headings.
    """
    if not concepts or len(concepts) < 2:
        return 0.0  # can't exhibit a coherent web with 0-1 concepts

    terms = [c['term'].strip().lower() for c in concepts]
    n = len(terms)

    def match(name):
        name = name.strip().lower()
        for i, t in enumerate(terms):
            if name == t or name in t or t in name:
                return i
        return None

    edges = set()
    orphan_refs = 0
    total_refs = 0
    for i, c in enumerate(concepts):
        for r in (c.get('related') or []):
            total_refs += 1
            j = match(r)
            if j is None:
                orphan_refs += 1
            elif j != i:
                edges.add((i, j))

    if total_refs == 0:
        return 0.0  # no relational claims at all: treated as an isolated glossary

    possible = n * (n - 1)
    density = len(edges) / possible
    reciprocity = (sum(1 for (i, j) in edges if (j, i) in edges) / len(edges)) if edges else 0.0
    orphan_rate = orphan_refs / total_refs
    isolated = sum(1 for i in range(n) if not any(i in (a, b) for (a, b) in edges))
    isolation_penalty = isolated / n

    score = 0.4 * min(density * 4, 1.0) + 0.3 * reciprocity + 0.3 * (1 - orphan_rate)
    score *= (1 - 0.5 * isolation_penalty)
    return max(0.0, min(score, 1.0))
```

**What the function does & why.** It resolves every `Related concepts` mention to a
real heading in the document (or marks it an orphan reference to nothing), builds a
directed graph, and scores three things: how densely connected the graph is, how often
relations are reciprocated (A cites B and B cites A), and how many references actually
resolve rather than dangling. It then discounts the score if a large share of concepts
have zero connections at all — a document that's just N unrelated definitions in a
trench coat.

**Why it's hard to Goodhart.** Padding every `Related concepts` field with plausible-
looking cross-references is only cheap if the references resolve to real headings and
are at least sometimes reciprocated — fabricating references to non-existent terms
gets caught by the orphan-rate term, and one-directional name-dropping (never
reciprocated) caps the reciprocity term. To win this metric a compiler basically has
to build an actually coherent term set, which is the target behavior.

---

## 3. Definition Distinctiveness (anti-templating / anti-circularity)

**How it signals good science.** A definition that mostly restates the term's own
name, or that is textually near-identical to several other definitions in the same
document, indicates the entries were mechanically filled rather than individually
reasoned through from the source paper. Genuine, paper-grounded definitions of
distinct technical objects should read as distinct prose with low mutual overlap and
low term-definition circularity.

**Compute function.**
```python
import re

def definition_distinctiveness(concepts):
    """
    Assumes: concepts as above. Flags (a) definitions dominated by the term's own
    words (circularity) and (b) high pairwise textual overlap across definitions
    (templating), alongside a raw length floor for thinness.
    """
    if not concepts:
        return 0.0

    def tokenize(s):
        return set(re.findall(r"[a-z]{4,}", (s or "").lower()))

    defs = [tokenize(c.get('definition')) for c in concepts]
    terms_tok = [tokenize(c.get('term')) for c in concepts]
    n = len(concepts)

    circular_scores = []
    for dtok, ttok in zip(defs, terms_tok):
        if not dtok:
            circular_scores.append(1.0)  # empty definition: fully degenerate
            continue
        overlap = len(dtok & ttok) / max(len(dtok), 1)
        circular_scores.append(overlap)
    circularity_penalty = sum(circular_scores) / n

    sims = []
    for i in range(n):
        for j in range(i + 1, n):
            if not defs[i] or not defs[j]:
                continue
            jac = len(defs[i] & defs[j]) / len(defs[i] | defs[j])
            sims.append(jac)
    avg_sim = sum(sims) / len(sims) if sims else 0.0

    avg_len = sum(len(c.get('definition') or "") for c in concepts) / n
    length_score = min(avg_len / 150.0, 1.0)

    score = length_score * (1 - circularity_penalty) * (1 - min(avg_sim * 2, 1.0))
    return max(0.0, min(score, 1.0))
```

**What the function does & why.** It tokenizes each definition and its own term name
to penalize circular definitions (definition text that's mostly just the term's words
repeated), computes pairwise Jaccard similarity across all definitions to catch
templated boilerplate reused across entries, and applies a length floor so terse,
low-information definitions can't hide behind low overlap. The three factors are
multiplied so any one failure mode (circularity, templating, thinness) caps the score.

**Why it's hard to Goodhart.** Making definitions long and mutually distinct while
still circular is caught by the circularity term; making them distinct and non-
circular but generic/copy-pasted from a textbook is caught by metric #5's stoplist;
making them verbose but still template-shaped across entries is caught by the
pairwise-similarity term. There's no single axis to pad along.

---

## 4. Notation–Prose Extraction Fidelity (NPEF)

**How it signals good science / good extraction.** The `Notation` field and the
`Definition`/`Boundary` prose should agree: if a symbol, subscript, or formal token
is used in the prose, it should have been captured in `Notation`; if `Notation` is
declared absent (`"—"`), the prose shouldn't secretly be full of formal symbols the
compiler failed to lift out. Internal consistency between structured fields and free
text is evidence the compiler did a careful, faithful read of the source rather than a
shallow one that leaves information stranded in the wrong field.

**Compute function.**
```python
import re

SYMBOL_PATTERN = re.compile(
    r"(\$[^$]+\$|\\[a-zA-Z]+|[A-Za-z]_\{?[0-9A-Za-z]+\}?|[α-ωΑ-Ω]|\b[A-Z]{2,}[0-9]+\b)"
)

def notation_extraction_fidelity(concepts):
    """
    Assumes: concepts as above. Detects symbolic/formal tokens leaking into prose
    that a declared-absent Notation field should have captured, and rewards
    Notation fields whose symbols are actually grounded/explained in the prose.
    """
    if not concepts:
        return 0.0

    scores = []
    for c in concepts:
        notation = (c.get('notation') or "").strip()
        prose = (c.get('definition') or "") + " " + (c.get('boundary') or "")
        has_symbol_in_prose = bool(SYMBOL_PATTERN.search(prose))
        declared_absent = notation in ("", "-", "—")

        if declared_absent and has_symbol_in_prose:
            scores.append(0.0)   # inconsistent: symbol used but not captured
        elif declared_absent and not has_symbol_in_prose:
            scores.append(0.8)   # plausibly genuine absence of notation
        elif (not declared_absent) and not has_symbol_in_prose:
            scores.append(0.5)   # notation given but never grounded in prose
        else:
            scores.append(1.0)   # notation present and consistently used
    return sum(scores) / len(scores)
```

**What the function does & why.** For every concept it checks whether the `Notation`
field is declared empty and, if so, whether the surrounding prose nonetheless contains
formal symbolic patterns (LaTeX, Greek letters, subscripted tokens, acronym+number
codes) — a mismatch that reveals a missed extraction. It also mildly penalizes the
opposite failure: notation given but never actually used/explained anywhere in the
prose, i.e., decorative or fabricated notation.

**Why it's hard to Goodhart.** Stripping all symbols out of the prose to avoid the
mismatch penalty directly damages Definition specificity (metric #3's length/
information floor) and plausibly the paper's own technical precision; inventing
notation to look thorough is caught by the "notation present but never grounded"
branch. Both failure directions are penalized, so there's no one-sided move.

---

## 5. Genuine-Vocabulary Ratio (Borrowed-Term Exclusion)

**How it signals good science.** The artifact's own stated purpose is to define the
paper's *genuine, specific* technical vocabulary — explicitly not a glossary of
generic/borrowed terms any reader already knows. A concepts.md that spends its
sections defining "p-value" or "control group" rather than the paper's actual
contribution-specific constructs is padding cardinality with filler, which is a
direct failure of the artifact's purpose and should score low even though it looks
"complete."

**Compute function.**
```python
GENERIC_TERMS = {
    "p-value", "confidence interval", "sample size", "mean", "standard deviation",
    "control group", "regression", "correlation", "statistical significance",
    "hypothesis testing", "variance", "median", "odds ratio", "randomization",
    "blinding", "placebo", "cohort", "case study", "survey", "questionnaire",
    "t-test", "chi-square", "anova", "bias", "validity", "reliability",
}

def genuine_vocabulary_ratio(concepts):
    """
    Assumes: concepts as above. Flags concept headings drawn from a fixed stoplist
    of generic/borrowed scientific and statistical vocabulary that the artifact's
    own spec says should not appear as standalone entries.
    """
    if not concepts:
        return 0.0

    n = len(concepts)
    generic_hits = sum(
        1 for c in concepts
        if (c.get('term') or "").strip().lower() in GENERIC_TERMS
    )
    ratio_specific = 1 - (generic_hits / n)

    # Thin documents get less benefit of the doubt: a 2-term concepts.md that is
    # already half generic terms is a worse signal than the same ratio at n=10.
    if n < 3:
        ratio_specific *= 0.7
    return ratio_specific
```

**What the function does & why.** It counts how many concept headings exactly match a
fixed list of generic/borrowed scientific vocabulary and converts that into a
"fraction genuinely specific" score, with an extra discount when the whole document is
very small (so a short concepts.md can't hide a high generic fraction behind a low
absolute count).

**Why it's hard to Goodhart.** Renaming a generic concept to sound paper-specific
without adding real content (e.g., "control group" → "reference cohort") dodges the
literal stoplist but produces a Definition that either restates a well-known idea in
different words (caught by low information/definitions overlapping known textbook
phrasing, partially visible in metric #3's templating check across a corpus of many
ARAs) or is too generic in Boundary/Related fields to look genuinely novel — and
inventing many fake "specific-sounding" terms just to pad past the stoplist tends to
reduce Related-concept connectivity (metric #2), since invented pseudo-specific terms
rarely have real relational links to the paper's actual dense vocabulary.

---

## Combination

These five metrics pull against each other in a way that blocks cheap uniform gaming.
Padding boundary conditions with generic-but-conditional-sounding sentences (to win
#1) produces near-duplicate text across entries that #3 catches as templating.
Fabricating a dense web of cross-references (to win #2) requires resolvable, at least
partly reciprocated links, which is expensive to fake without also building genuinely
distinct, non-circular definitions (#3) and real notation grounding (#4). Stripping
prose of symbols to dodge notation-mismatch penalties (#4) thins out Definition
content and directly lowers #3's length/information floor. And renaming generic
borrowed terms to evade the stoplist (#5) tends to produce either templated/circular
definitions (caught by #3) or isolated nodes with no genuine relational anchoring in
the paper's real vocabulary (caught by #2). No single move improves more than one or
two of the five without actively degrading at least one other.
