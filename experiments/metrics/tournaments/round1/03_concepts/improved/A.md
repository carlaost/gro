# Proposer #4 (improved) — metrics for `logic/concepts.md`

## Changes from stage 1

The judge ranked this entry #1 but flagged three concrete weaknesses. All three are fixed below,
not just acknowledged:

1. **GVR (old metric #5) is cut, not patched.** A hardcoded 26-term English stoplist was surface-level,
   trivially dodged by renaming ("control group" → "reference cohort"), and doesn't generalize across
   fields. Per the judge's second suggested fix, its *intent* — catch borrowed/generic vocabulary
   padding cardinality — is folded into what was Definition Distinctiveness (#3), now **Definition
   Distinctiveness & Grounding (DDG)**. Instead of matching term strings against a keyword list, DDG
   asks a field-agnostic question: does this entry's definition anchor into the paper's own specifics
   (deictic/paper-referential language, a concrete number, or genuine use elsewhere in the document's
   own relational web) rather than reading as a portable, context-free textbook restatement? This
   survives a rename that GVR couldn't, because renaming a borrowed term doesn't manufacture grounding.
2. **CGC's reciprocity weighting is fixed.** Reciprocity dropped from a load-bearing 0.3 weight to a
   0.1 bonus, and a new 0.4-weighted **weakly-connected-component coverage** term takes over as the
   primary coherence signal — so a legitimately hierarchical/directional vocabulary (a method
   presupposes an object; the object doesn't need to cite the method back) is no longer capped for
   failing to be mutually reciprocal. The previously unexplained `density * 4` magic number is replaced
   with a justified target (`n * 2` expected resolved edges, grounded in the shape doc's own worked
   examples, where `Related concepts` lists run ~3–4 items per entry).
3. **BCS now has a paraphrase gate**, adapted directly from agent3's BCIS (per the judge's explicit
   instruction to borrow it): a `Boundary conditions` field with >0.6 token-overlap with `Definition`
   is scored 0.2, not rewarded for length/cue-words it inherited by being copy-pasted. This closes the
   exact loophole the stage-1 version left open — a boundary field that's just the definition re-pasted
   with a "requires" bolted on used to score well; now it doesn't.

NPEF (notation fidelity) is carried over unchanged — the judge called it the best notation metric in
the field and named no weaknesses in it. The metric count moves from 5 to 4 (GVR is retired rather than
replaced 1-for-1); this is intentional, per the judge's own instruction to "fold the intent in and drop
the standalone stoplist" rather than patch a fundamentally brittle mechanism.

Assumed parsed shape for all functions below (unchanged): `concepts` is a list of dicts, one per
`## {Term}` section, each with keys `term` (str), `notation` (str, `"—"` if none), `definition` (str),
`boundary` (str, `"Not specified in paper"` if absent), and `related` (list of str, the comma-split
Related-concepts text). An empty/missing `concepts.md` is represented as `concepts == []`.

---

## 1. Boundary-Condition Substantiveness (BCS)

**How it signals good science.** A term's boundary conditions are where a paper declares the limits of
its own claims — when a definition applies, when it breaks, what it assumes. Papers that do careful
science tend to know (and state) where their constructs stop being valid; papers that don't have
usually never interrogated the question. Real boundary text uses conditional language ("requires,"
"only when," "assumes") and has enough content to be a genuine limiting clause, not a stock phrase —
and it must be a genuinely distinct clause, not the Definition field re-served with a conditional
word bolted on.

**Compute function.**
```python
import re

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

    def tokenize(s):
        return set(re.findall(r"[a-z]{4,}", (s or "").lower()))

    scores = []
    generic_count = 0
    for c in concepts:
        b_raw = (c.get('boundary') or "").strip()
        b = b_raw.lower()
        if b in GENERIC_MARKERS or len(b) < 15:
            scores.append(0.0)
            generic_count += 1
            continue

        # Paraphrase gate (adapted from agent3's BCIS, per judge direction): a boundary field
        # that mostly restates the Definition's own vocabulary is a copy-paste dodge of the
        # placeholder penalty above, not a genuine limiting clause, regardless of its length
        # or how many conditional cue-words it happens to contain.
        b_tok = tokenize(b_raw)
        d_tok = tokenize(c.get('definition'))
        overlap = len(b_tok & d_tok) / max(len(b_tok), 1) if b_tok else 0.0
        if overlap > 0.6:
            scores.append(0.2)
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

**What the function does & why.** For each concept it checks whether the boundary field is a stock
placeholder or too short to carry information; if so it scores 0 for that entry. It then checks whether
the boundary text is substantially the same tokens as the Definition field — if so, it's a paraphrase
dodge, not a real limiting clause, and scores 0.2 regardless of length or cue-word count. Only text that
clears both gates is scored on length and genuine conditional/limiting language, averaged across
concepts. It then applies an extra multiplicative penalty if ≥80% of entries are the generic
placeholder — because a document where almost nothing has a stated boundary reads as an extraction that
never looked, not a paper that's simply well-bounded everywhere.

**Why it's hard to Goodhart.** Padding every boundary field with a long sentence containing
"when"/"requires" without real content is detectable by the sibling distinctiveness metric (#2) as
templated, near-duplicate text across concepts — so gaming this one in bulk collides with that one.
Copy-pasting the Definition into Boundary to dodge the placeholder penalty is now caught directly by
the paraphrase gate. Writing one genuinely specific, non-formulaic boundary per concept is exactly the
desired behavior, so there's no cheap uniform trick that survives all three checks.

---

## 2. Concept Graph Coherence (CGC)

**How it signals good science.** Genuine technical vocabulary in a paper is relational — terms
interlock (a method presupposes an object, an object is measured by an instrument, etc.). A compiler
that actually understood the paper's conceptual structure will produce `Related concepts` links that
(a) point to other real headings in the same document, and (b) leave few concepts totally isolated,
tying the vocabulary into one connected structure rather than a set of disjoint pockets. Critically,
this connectedness does not require mutual citation: a coherent vocabulary is often hierarchical or
directional (a method presupposes an object; the object need not cite the method back), so reciprocity
is a mild bonus, not a requirement.

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

    # Weakly-connected-component coverage: treat edges as undirected for the purpose of asking
    # "does this vocabulary hang together as one structure," since a directional/hierarchical web
    # (method -> object, object not citing method back) is a legitimate and common shape, not a
    # coherence failure. This replaces reciprocity as the load-bearing connectivity signal.
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for (i, j) in edges:
        union(i, j)

    comp_sizes = {}
    for i in range(n):
        r = find(i)
        comp_sizes[r] = comp_sizes.get(r, 0) + 1
    coverage = max(comp_sizes.values()) / n

    # Density target: the shape doc's own worked examples show concepts typically list ~3-4
    # related terms each, not n-1 (a term is not expected to relate to every other term in the
    # document). An average of 2 *resolved* edges per concept is a defensible "coherent" bar,
    # replacing the previous unjustified flat *4 multiplier on raw density.
    expected_edges = max(n * 2, 1)
    density_score = min(len(edges) / expected_edges, 1.0)

    orphan_rate = orphan_refs / total_refs
    reciprocity = (sum(1 for (i, j) in edges if (j, i) in edges) / len(edges)) if edges else 0.0
    isolated = sum(1 for i in range(n) if not any(i in (a, b) for (a, b) in edges))
    isolation_penalty = isolated / n

    # Reciprocity is now a small bonus (0.1), not a third of the score: it rewards genuinely
    # mutual relations where they exist, without penalizing legitimate directional structure.
    score = 0.4 * coverage + 0.3 * density_score + 0.2 * (1 - orphan_rate) + 0.1 * reciprocity
    score *= (1 - 0.5 * isolation_penalty)
    return max(0.0, min(score, 1.0))
```

**What the function does & why.** It resolves every `Related concepts` mention to a real heading in the
document (or marks it an orphan reference to nothing) and builds a graph. It scores primarily on
whether the vocabulary forms one connected structure (largest weakly-connected component as a fraction
of all concepts) and on resolved-edge density against a justified target, discounts for references that
dangle to nowhere, and gives reciprocated relations a small bonus rather than requiring them. It then
discounts the whole score if a large share of concepts have zero connections at all — a document that's
just N unrelated definitions in a trench coat.

**Why it's hard to Goodhart.** Padding every `Related concepts` field with plausible-looking
cross-references is only cheap if the references resolve to real headings — fabricating references to
non-existent terms is caught by the orphan-rate term. Faking connectivity by pointing everything at one
hub term still earns component coverage, but not density or a specificity payoff elsewhere (Definition
Distinctiveness, #3, penalizes the thin, repetitive definitions such a hub-and-spoke fake tends to
produce). To win this metric a compiler basically has to build an actually coherent term set, which is
the target behavior — and it no longer has to fake mutual citation to do so.

---

## 3. Definition Distinctiveness & Grounding (DDG)

**How it signals good science.** A definition that mostly restates the term's own name, or that is
textually near-identical to several other definitions in the same document, indicates the entries were
mechanically filled rather than individually reasoned through from the source paper. Separately, a
definition that reads as a portable, context-free restatement of a well-known idea — with no anchor
into this paper's own specifics — is evidence of borrowed/generic vocabulary padding cardinality rather
than genuine, contribution-specific terminology (the artifact's own stated purpose is to define the
paper's *genuine* technical vocabulary, not terms any reader already knows). Genuine, paper-grounded
definitions of distinct technical objects should read as distinct prose, with low mutual overlap, low
term-definition circularity, and some anchor tying them to this specific paper.

**Compute function.**
```python
import re

def definition_distinctiveness_and_grounding(concepts):
    """
    Assumes: concepts as above. Flags (a) definitions dominated by the term's own words
    (circularity), (b) high pairwise textual overlap across definitions (templating),
    (c) a raw length floor for thinness, and (d) absence of any paper-specific anchor
    (the borrowed/generic-vocabulary failure mode formerly checked by a hardcoded
    stoplist of English terms).
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

    # Grounding: replaces the old hardcoded stoplist. Instead of matching term *names* against a
    # fixed English word list (trivially dodged by renaming, and useless outside English/stats
    # vocabulary), ask whether each entry's DEFINITION shows any anchor into this specific paper:
    # deictic/paper-referential language, a concrete number, or genuine use elsewhere in the
    # document's own relational web (referenced by another concept's Related list). A borrowed,
    # portable, textbook-style definition typically has none of these; a genuine contribution-
    # specific construct usually has at least one.
    GROUNDING_CUES = [
        "this paper", "this study", "this analysis", "this model", "this network",
        "this dataset", "this trial", "this cohort", "this framework", "this method",
        "in this ", "here,", "here we", "here it", "our ", "we use", "we define",
    ]
    NUMBER_PATTERN = re.compile(r"\d")
    term_names = [c.get('term', '').strip().lower() for c in concepts]

    def referenced_elsewhere(i):
        name = term_names[i]
        for j, c in enumerate(concepts):
            if j == i:
                continue
            for r in (c.get('related') or []):
                r = r.strip().lower()
                if r and (r == name or r in name or name in r):
                    return True
        return False

    grounded_flags = []
    for i, c in enumerate(concepts):
        d = (c.get('definition') or "").lower()
        cue_hit = any(cue in d for cue in GROUNDING_CUES)
        number_hit = bool(NUMBER_PATTERN.search(d))
        grounded_flags.append(cue_hit or number_hit or referenced_elsewhere(i))
    grounding_rate = sum(grounded_flags) / n

    # Grounding is a soft multiplier (0.5-1.0), not a hard gate: absence of an explicit deictic
    # cue or number doesn't prove a term is borrowed (some genuine formal objects are just stated
    # plainly), but a document where NO entries ground into the paper's own specifics or relational
    # web reads as generic padding and should lose real credit, not a token amount.
    grounding_factor = 0.5 + 0.5 * grounding_rate

    score = length_score * (1 - circularity_penalty) * (1 - min(avg_sim * 2, 1.0)) * grounding_factor
    return max(0.0, min(score, 1.0))
```

**What the function does & why.** It tokenizes each definition and its own term name to penalize
circular definitions, computes pairwise Jaccard similarity across all definitions to catch templated
boilerplate reused across entries, applies a length floor so terse definitions can't hide behind low
overlap, and now also checks whether each definition shows any sign of anchoring into this specific
paper — deictic/paper-referential phrasing, a concrete number, or genuine use in another concept's
`Related concepts` list. A document where no entries ground into the paper's own specifics or its own
relational web is exactly the borrowed/generic-vocabulary padding the old stoplist tried to catch, but
detected structurally instead of by matching against a fixed English word list. The four factors are
combined so any one failure mode (circularity, templating, thinness, ungroundedness) meaningfully caps
the score.

**Why it's hard to Goodhart.** Making definitions long and mutually distinct while still circular is
caught by the circularity term; making them distinct, non-circular, and long but generic/copy-pasted
from a textbook with no paper anchor is caught by the grounding term — and critically, renaming a
borrowed term ("control group" → "reference cohort") no longer helps, because grounding is checked
against the definition's content and the document's own relational web, not the term's surface string.
Manufacturing fake grounding by inserting "in this paper" into an otherwise generic definition without
adding real content is still caught by the length floor and, if done identically across entries, by the
pairwise-similarity term. There's no single axis to pad along.

---

## 4. Notation–Prose Extraction Fidelity (NPEF)

**How it signals good science / good extraction.** The `Notation` field and the `Definition`/`Boundary`
prose should agree: if a symbol, subscript, or formal token is used in the prose, it should have been
captured in `Notation`; if `Notation` is declared absent (`"—"`), the prose shouldn't secretly be full
of formal symbols the compiler failed to lift out. Internal consistency between structured fields and
free text is evidence the compiler did a careful, faithful read of the source rather than a shallow one
that leaves information stranded in the wrong field.

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

**What the function does & why.** For every concept it checks whether the `Notation` field is declared
empty and, if so, whether the surrounding prose nonetheless contains formal symbolic patterns (LaTeX,
Greek letters, subscripted tokens, acronym+number codes) — a mismatch that reveals a missed extraction.
It also mildly penalizes the opposite failure: notation given but never actually used/explained anywhere
in the prose, i.e., decorative or fabricated notation. Honest absence (no notation declared, no symbols
found) scores 0.8, not a penalty — a clinical/endpoint-vocabulary concept legitimately has no notation,
and this metric must not punish that class of good science.

**Why it's hard to Goodhart.** Stripping all symbols out of the prose to avoid the mismatch penalty
directly damages Definition specificity (metric #3's length/information floor) and plausibly the
paper's own technical precision; inventing notation to look thorough is caught by the "notation present
but never grounded" branch. Both failure directions are penalized, so there's no one-sided move.

---

## Combination

These four metrics pull against each other in a way that blocks cheap uniform gaming. Padding boundary
conditions with generic-but-conditional-sounding sentences (to win #1) produces near-duplicate text
across entries that #3 catches as templating; copy-pasting the Definition into Boundary to dodge the
placeholder penalty is now caught directly by #1's own paraphrase gate. Fabricating a dense web of
cross-references (to win #2) requires links that actually resolve to real headings, which is expensive
to fake without also building genuinely distinct, non-circular, paper-grounded definitions (#3) and
real notation grounding (#4) — routing every fake reference through one hub term still earns component
coverage but not the density target, and the thin, repetitive definitions such a shortcut produces are
caught by #3. Stripping prose of symbols to dodge notation-mismatch penalties (#4) thins out Definition
content and directly lowers #3's length/information floor. And renaming a borrowed, generic term to
sound paper-specific no longer evades detection the way it could against a stoplist: it still has to
either ground into the paper's own specifics or its own relational web (#3's new grounding term) or be
caught as templated/circular (#3's original terms) or as an isolated node with no genuine relational
anchoring (#2). No single move improves more than one metric without actively degrading at least one
other.
