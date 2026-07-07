# Proposer 3 — metrics for `logic/concepts.md`

Assumed parsed representation for all functions below (shared, stated once):

```python
# concepts: list[dict], one dict per "## {Term Name}" section, in document order.
# {
#   "name": str,                 # the heading text
#   "notation": str,              # "—" if none given (this is a legitimate, non-thin value)
#   "definition": str,            # markdown-prose, may be empty if the field is missing
#   "boundary": str,              # markdown-prose, or the literal "Not specified in paper"
#   "related": list[str],         # split/trimmed from the comma-separated field; [] if blank/missing
# }
```

---

## 1. Boundary-Condition Informativeness Score (BCIS)

**How it signals good science.** Stating genuine boundary/applicability conditions ("when does
this hold, when does it not") requires the compiler to have actually located scope-limiting
detail in the source paper — that detail only exists in papers that were rigorous enough to state
their own limits. A concepts list where boundary conditions are either the generic "Not specified
in paper" placeholder, or a boundary sentence that just re-paraphrases the Definition field, is
evidence of a shallow compilation pass (or a source paper that never specified its own scope) —
either way, a real signal of thin science communication, not neutral missing-ness.

**Compute function.**
```python
def boundary_condition_informativeness(concepts):
    """
    Assumes: concepts as in the shared shape above. `boundary` is either substantive prose or
    the literal placeholder "Not specified in paper" (case-insensitive) when the source doesn't
    state one.
    """
    NOT_SPECIFIED_MARKERS = ["not specified in paper", "not specified", "n/a", "none stated"]
    if not concepts:
        return 0.0
    scores = []
    for c in concepts:
        boundary = (c.get("boundary") or "").strip()
        definition = (c.get("definition") or "").strip()
        if not boundary:
            scores.append(0.0)
            continue
        low = boundary.lower()
        if any(m in low and len(low) < len(m) + 15 for m in NOT_SPECIFIED_MARKERS):
            scores.append(0.0)  # boilerplate placeholder -> no real content
            continue
        b_tokens = set(low.split())
        d_tokens = set(definition.lower().split())
        overlap = (len(b_tokens & d_tokens) / len(b_tokens)) if b_tokens else 1.0
        if overlap > 0.6:
            scores.append(0.2)  # near-paraphrase of the Definition = padding, not new content
            continue
        length_score = min(len(boundary.split()) / 12.0, 1.0)
        scores.append(0.3 + 0.7 * length_score)
    return sum(scores) / len(scores)
```

**What it does & why.** For every concept, it checks (a) is the boundary field non-empty, (b) is
it the generic "not specified" boilerplate, (c) does it substantially just repeat words already in
the Definition (word-overlap ratio > 0.6, a cheap paraphrase detector), and (d) is it long enough
to plausibly carry real content. Concepts that pass all checks get near-full credit scaled by
length; concepts that fail any get 0–0.2. The artifact score is the mean over concepts.

**Why it's hard to Goodhart.** Padding the boundary field with generic filler text ("this concept
applies broadly across contexts") to avoid the placeholder penalty will usually either (i) overlap
heavily with the Definition's vocabulary (caught by the paraphrase check) or (ii) be detectably
generic/short. Writing genuinely new, non-overlapping, sufficiently long boundary text for every
concept is exactly the behavior we want to reward — and it's expensive to fake for many concepts
because each one needs paper-specific scope language, which drags directly against the
Definition-overlap check if lazily copy-adjusted from the Definition itself.

---

## 2. Conceptual Interlinkage Density (CID)

**How it signals good science.** A paper that introduces a coherent conceptual apparatus has
terms that reference each other — real theoretical/methodological frameworks are relational, not
a flat list of unconnected glossary entries. If a compiler produces concepts where the `Related
concepts` field is blank, or where no concept is ever named by any other concept's `Related
concepts` field, that's evidence the "concepts" are just independently scraped terms rather than a
mapped-out vocabulary of an interconnected system — a weaker signal of engaging with the paper's
actual argument structure.

**Compute function.**
```python
def conceptual_interlinkage_density(concepts):
    """
    Assumes concepts as in the shared shape. `related` is a list of loose-text names (may include
    external/field terms that are not headings in this document); [] when the field is blank.
    """
    if not concepts:
        return 0.0
    names = [c["name"].strip().lower() for c in concepts if c.get("name")]
    n = len(concepts)
    if n == 0:
        return 0.0
    in_degree = {nm: 0 for nm in names}
    total_related_mentions = 0
    for c in concepts:
        related = c.get("related") or []
        total_related_mentions += len(related)
        for r in related:
            r_norm = r.strip().lower()
            if not r_norm:
                continue
            for nm in names:
                if nm and (nm == r_norm or nm in r_norm or r_norm in nm):
                    in_degree[nm] += 1
    if n <= 1:
        return 1.0 if total_related_mentions > 0 else 0.0
    linked = sum(1 for v in in_degree.values() if v > 0)
    coverage = linked / n  # fraction of concepts named by at least one sibling entry
    empties = sum(1 for c in concepts if not (c.get("related") or []))
    empty_penalty = empties / n
    return max(0.0, coverage - 0.5 * empty_penalty)
```

**What it does & why.** It builds an implicit graph: an edge exists whenever concept A's name
appears inside concept B's `Related concepts` text. It then measures what fraction of the
document's own concepts are referenced by at least one sibling (in-degree > 0) — a proxy for how
interlinked the vocabulary is — and subtracts a penalty proportional to how many concepts left the
`Related concepts` field entirely empty (thinness must cost something even if global coverage is
otherwise okay).

**Why it's hard to Goodhart.** You cannot inflate this score by dumping arbitrary text into
`Related concepts` — only mentions that resolve to another *actual heading in this document* count
toward coverage, so a compiler would have to correctly identify and cross-reference real
sibling concepts, which requires having genuinely parsed the term network rather than free-text
padding. Mentioning unrelated or fabricated concept names doesn't help (they don't match any
`name`), and mentioning only 1–2 hub concepts repeatedly caps out quickly once those are already
covered — spreading references thinly across many concepts is the only way to keep raising the
score, which is exactly the "real interconnected vocabulary" behavior being targeted.

---

## 3. Definitional Groundedness / Specificity (DGS)

**How it signals good science.** The artifact's stated purpose is to define "the paper's genuine
technical vocabulary... not a glossary of borrowed/generic terms." A Definition that is
paper-specific — tied to this study's actual thresholds, comparisons, named methods/datasets, or
explicit "in this paper/model/trial" framing — indicates the compiler (and transitively, the
underlying paper) engaged with the term's role in *this* contribution, rather than pasting in a
generic textbook definition that could apply to any paper using that word. Borrowed/generic
definitions are a known failure mode the shape doc explicitly warns concepts.md should avoid.

**Compute function.**
```python
import re

def definitional_groundedness(concepts):
    """
    Assumes `definition` is prose text (may be empty if the field is missing/blank).
    Heuristic proxy: does the definition contain paper-specific grounding markers
    (self-referential framing, numeric thresholds/values, explicit comparisons) rather than
    reading as a context-free, generic dictionary definition.
    """
    GROUNDING_PATTERNS = [
        r"\bthis (paper|study|nma|model|trial|analysis|network|cohort|dataset)\b",
        r"\bhere\b",
        r"\bin this\b",
        r"\d",
        r"\b(vs\.?|versus|compared to)\b",
    ]
    if not concepts:
        return 0.0
    scores = []
    for c in concepts:
        d = (c.get("definition") or "").strip().lower()
        if not d:
            scores.append(0.0)
            continue
        hits = sum(1 for p in GROUNDING_PATTERNS if re.search(p, d))
        word_count = len(d.split())
        length_ok = word_count >= 15
        grounding_score = min(hits / 2.0, 1.0)
        length_score = 1.0 if length_ok else word_count / 15.0
        scores.append(0.5 * grounding_score + 0.5 * length_score)
    return sum(scores) / len(scores)
```

**What it does & why.** For each Definition it checks for lightweight textual markers of
paper-specific grounding (self-referential phrases, digits/thresholds, explicit comparisons) and
combines that with a length floor (generic dictionary definitions tend to be short and
context-free; genuinely paper-specific ones need more words to situate the term). The two
sub-scores are averaged and then averaged again across all concepts.

**Why it's hard to Goodhart.** Sprinkling a bare digit or the word "here" into an otherwise
generic definition only buys partial credit (grounding is capped and combined with a genuine
length requirement), so cheap keyword-stuffing plateaus fast. To max this out for every concept,
the definitions must actually be long enough to carry paper-specific content — and inventing fake
numeric thresholds/comparisons for terms that don't have them risks contradicting the same
paper's other artifacts (claims, methods) that a downstream cross-artifact check could catch,
so fabrication has a paper trail elsewhere.

---

## 4. Definitional Circularity Penalty (DCP)

**How it signals good science.** A definition that mostly just restates its own heading term
("P-score: a score derived from P...") explains nothing — it's a placeholder pretending to be a
definition. Genuine engagement with a paper's vocabulary produces definitions that explain a term
*in other words*, grounding it in mechanism, method, or role rather than echoing the name back.
Circularity is a distinct failure mode from brevity or genericness (a definition can be
grounded-sounding yet still circular, or short yet non-circular), so it needs its own check.

**Compute function.**
```python
import re

def definitional_circularity_penalty(concepts):
    """
    Assumes `name` (the heading text) and `definition` (prose, possibly empty).
    Returns a score in [0,1]: 1 = low circularity (good), 0 = high circularity or missing
    definition (bad).
    """
    def tokens(s):
        return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

    if not concepts:
        return 0.0
    scores = []
    for c in concepts:
        name_toks = tokens(c.get("name"))
        definition = (c.get("definition") or "").strip()
        if not definition:
            scores.append(0.0)
            continue
        first_clause = definition.split(".")[0]
        clause_toks = tokens(first_clause)
        if not clause_toks:
            scores.append(0.0)
            continue
        overlap = len(name_toks & clause_toks) / len(clause_toks)
        total_len = len(tokens(definition))
        circularity = overlap * (1.0 if total_len < 20 else 0.5)
        scores.append(max(0.0, 1.0 - circularity))
    return sum(scores) / len(scores)
```

**What it does & why.** It looks at the opening clause of each Definition (up to the first
period) and measures what fraction of its vocabulary is just the heading's own words repeated.
High overlap in a short opening clause, especially when the whole definition is also short,
is scored as circular/tautological; overlap that's diluted by a long, substantive definition is
penalized less (the term name recurring once in a rich paragraph isn't the same failure as a
one-line restatement).

**Why it's hard to Goodhart.** The obvious dodge — avoid repeating the heading's own words — just
pushes the compiler toward writing an actual independent explanation, which is the goal. The other
dodge — bury a circular opening clause inside a long definition — is exactly what the `total_len`
discount already anticipates and only halves the penalty, it doesn't erase it; and inflating length
without new content collides with Metric 3's grounding/length balance (padding with repetitive or
generic filler helps circularity but drags down groundedness, since filler rarely contains numeric
thresholds or comparisons).

---

## Combination

These four metrics are jointly hard to game because they pull compilation behavior in different,
partially conflicting directions. Metric 1 (BCIS) rewards boundary text that is long and
*dissimilar* to the Definition; Metric 3 (DGS) rewards Definitions that are long and
paper-specific. A compiler that tries to cheaply pass BCIS by copying grounded-sounding phrases
from the Definition into the Boundary field gets caught by BCIS's own paraphrase-overlap check, so
it must instead write genuinely new boundary content — real work. Metric 2 (CID) can't be gamed
with free-text padding because only references that resolve to actual sibling headings count, and
inventing fake, over-connected cross-references produces an artificial concept web that a Definition
audit (Metric 3/4) would likely expose as unsupported by the actual definitions. Metric 4 (DCP)
closes the loophole where a compiler inflates Definition length purely to win Metric 3's length
floor: padding with filler either repeats the heading term (caught by DCP) or dilutes the
grounding-marker density (caught by DGS). In short: gaming boundary conditions costs you on
Definition-overlap, gaming Definition length costs you on circularity or groundedness, and gaming
the relation graph costs you on definitional support — there's no single cheap edit that raises all
four at once.
