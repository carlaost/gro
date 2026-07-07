# Proposer 3 (revised) — metrics for `logic/concepts.md`

## Changes from stage 1

The judge ranked this entry #2 of 4 and named three concrete gaps, all addressed below:

1. **Notation was dropped entirely.** `Notation` is a first-class, mandatory field in the shape
   and `"—"` is an explicitly *legitimate, non-thin* value (per the shared shape's own comment) —
   but a truly *missing* field (no placeholder at all) is a hard-constraint violation and must be
   penalized, not treated the same as an honest `"—"`. Added **Metric 5, Notation–Prose Extraction
   Fidelity (NPEF)**: bidirectional (catches both a symbol stranded in prose while `Notation: —`,
   and notation declared but never grounded anywhere in the prose), and it does *not* punish honest
   absence — it scores a genuine `"—"` with no leaked symbol at 0.8, reserving 1.0 for concepts
   whose declared notation is actually used.
2. **CID didn't distinguish scattered vs. universal `Related concepts` absence.** A document where
   90% of entries have a blank `Related concepts` field is a shallow-read signal (the compiler
   didn't work to place each term in the paper's conceptual network), not just "many small
   per-concept costs." Added a multiplicative shallow-read penalty to CID, mirroring the same
   logic Metric 1 already applies to per-concept boundary placeholders, but now applied at the
   document level for near-universal emptiness (≥80% blank).
3. **CID ignored orphan/fabricated cross-references.** The original design already refuses credit
   for `Related concepts` text that doesn't resolve to a real sibling heading — but it was silent
   about text that *looks like* a fabricated sibling heading (a near-miss reword of a real heading
   name) used to pad the field without doing real cross-referencing work. Added a near-miss-orphan
   penalty using string-similarity against actual headings, calibrated to avoid punishing
   legitimate external/field terminology (e.g., "mass spectrometry"), which the shape doc
   explicitly says belongs in `Related concepts` and must not be penalized.

Metrics 1 (BCIS), 3 (DGS), and 4 (DCP) are unchanged from stage 1 — the judge named no weaknesses
in them, and re-deriving working anti-Goodhart machinery for no reason would be needless churn. The
Combination section is rewritten to fold in the new metric and the sharpened CID.

Assumed parsed representation for all functions below (shared, stated once, unchanged from stage 1):

```python
# concepts: list[dict], one dict per "## {Term Name}" section, in document order.
# {
#   "name": str,                 # the heading text
#   "notation": str,              # "—" if none given (this is a legitimate, non-thin value);
#                                  # "" only if the field itself is missing/dropped (a defect)
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

## 2. Conceptual Interlinkage Density (CID) — revised

**How it signals good science.** A paper that introduces a coherent conceptual apparatus has
terms that reference each other — real theoretical/methodological frameworks are relational, not
a flat list of unconnected glossary entries. If a compiler produces concepts where the `Related
concepts` field is blank, or where no concept is ever named by any other concept's `Related
concepts` field, that's evidence the "concepts" are just independently scraped terms rather than a
mapped-out vocabulary of an interconnected system. Two failure modes beyond the stage-1 version
matter here: (a) *uniform* absence of `Related concepts` across nearly the whole document is a
stronger, document-level shallow-read signal, not just a sum of per-concept costs; and (b) a
compiler can pad the field with text that is *styled* like a real sibling heading (a near-miss
reword) purely to look connected, without doing any genuine cross-referencing — this is distinct
from legitimate mentions of external/field terminology that never were, and were never meant to
be, headings in this document.

**Compute function.**
```python
import difflib

def conceptual_interlinkage_density(concepts):
    """
    Assumes concepts as in the shared shape. `related` is a list of loose-text names (may include
    external/field terms that are not headings in this document -- that is legitimate and must not
    be penalized); [] when the field is blank.
    """
    if not concepts:
        return 0.0
    names = [c["name"].strip().lower() for c in concepts if c.get("name")]
    n = len(concepts)
    if n == 0:
        return 0.0

    in_degree = {nm: 0 for nm in names}
    total_related_mentions = 0
    unresolved_mentions = []  # (mention_text,) that didn't match any sibling heading

    for c in concepts:
        related = c.get("related") or []
        total_related_mentions += len(related)
        for r in related:
            r_norm = r.strip().lower()
            if not r_norm:
                continue
            matched = False
            for nm in names:
                if nm and (nm == r_norm or nm in r_norm or r_norm in nm):
                    in_degree[nm] += 1
                    matched = True
            if not matched:
                unresolved_mentions.append(r_norm)

    if n <= 1:
        return 1.0 if total_related_mentions > 0 else 0.0

    linked = sum(1 for v in in_degree.values() if v > 0)
    coverage = linked / n  # fraction of concepts named by at least one sibling entry

    empties = sum(1 for c in concepts if not (c.get("related") or []))
    empty_fraction = empties / n
    empty_penalty = empty_fraction  # per-concept cost, as in stage 1

    base = max(0.0, coverage - 0.5 * empty_penalty)

    # --- new: document-level shallow-read multiplier for near-universal absence ---
    # Mirrors the same logic Metric 1 applies per-concept to "Not specified in paper": uniform
    # emptiness across (near-)all entries is evidence the compiler didn't attempt cross-referencing
    # at all, not just that many individual concepts happened to lack related terms.
    shallow_read_multiplier = 0.3 if empty_fraction >= 0.8 else 1.0
    base *= shallow_read_multiplier

    # --- new: near-miss orphan penalty ---
    # A mention that closely resembles (but doesn't exactly/substring match) an actual sibling
    # heading is suspicious: it looks like it was meant to read as a cross-reference to a concept
    # in *this* document, but doesn't resolve to one. This is different from a genuine external
    # field term (e.g. "mass spectrometry", "SUCRA") which won't be textually close to any of this
    # document's own headings and is therefore never flagged.
    near_miss_count = 0
    for mention in unresolved_mentions:
        for nm in names:
            if not nm:
                continue
            ratio = difflib.SequenceMatcher(None, mention, nm).ratio()
            if 0.75 <= ratio < 1.0:  # close but not already an exact/substring match
                near_miss_count += 1
                break
    near_miss_rate = (near_miss_count / total_related_mentions) if total_related_mentions else 0.0
    base = max(0.0, base - 0.3 * near_miss_rate)

    return base
```

**What it does & why.** It builds an implicit graph: an edge exists whenever concept A's name
appears inside concept B's `Related concepts` text. It measures what fraction of the document's
own concepts are referenced by at least one sibling (in-degree > 0), subtracts a per-concept
penalty for how many concepts left the field entirely empty, then applies two document-level
corrections: a severe multiplicative penalty when ≥80% of entries are blank (uniform absence reads
as "compiler never attempted this field," a stronger signal than the per-concept cost alone
captures), and a penalty proportional to how many unresolved mentions are near-miss rewordings of
real sibling headings rather than genuine external terminology.

**Why it's hard to Goodhart.** You cannot inflate this score by dumping arbitrary text into
`Related concepts` — only mentions that resolve to another *actual heading in this document* count
toward coverage, so a compiler would have to correctly identify and cross-reference real sibling
concepts, which requires having genuinely parsed the term network rather than free-text padding.
Mentioning unrelated or fabricated concept names doesn't help coverage (they don't match any
`name`), and now actively costs points if they're textually close enough to a real heading to look
like a lazy paraphrase-dodge of an actual cross-reference — while genuine field jargon (which
won't resemble any of *this* document's headings) passes through untouched. The shallow-read
multiplier closes the remaining loophole where a compiler could otherwise "afford" leaving most
entries blank as long as the few populated ones scored well on the per-concept term; now uniform
neglect costs disproportionately more than scattered neglect, matching the real quality gap
between an honestly sparse network and a systematically unattempted one.

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

## 5. Notation–Prose Extraction Fidelity (NPEF) — new

**How it signals good science.** `Notation` is a mandatory field with a legitimate empty value:
the shared shape explicitly marks `"—"` as "a legitimate, non-thin value," and the shape doc notes
that whole classes of ARAs (clinical-trial endpoint vocab) correctly have `Notation: —` throughout.
A metric that penalizes honest absence would punish good science; a metric that ignores the field
entirely (stage-1's gap) misses two real, opposite failure modes: (a) the compiler declared
`Notation: —` but a symbol clearly belonging to this concept (e.g. `p217`, `P-score`) is stranded
loose in the Definition/Boundary prose — a missed-extraction defect, not an honest absence; and
(b) the compiler declared real notation but never actually uses or explains it anywhere in the
prose — decorative notation copied from the source without being grounded in the writeup.

**Compute function.**
```python
import re

SYMBOL_LEAK_PATTERN = re.compile(
    r"`[^`]+`"                              # inline code span
    r"|\$[^$]+\$"                           # inline LaTeX
    r"|\b[a-zA-Z]+\d+(?:_[A-Za-z0-9]+)*\b"   # alnum symbol, e.g. p217, p217_MS
    r"|\b[A-Z]{2,6}\b"                       # short acronym, e.g. SUCRA, NMA
)

def _notation_symbol_tokens(notation):
    raw = re.split(r"[,\s()]+", notation)
    return {t.strip(".,:;()") for t in raw if t.strip(".,:;()")}

def notation_prose_extraction_fidelity(concepts):
    """
    Assumes `notation` is either substantive symbolic text, the literal "—" (a legitimate,
    non-thin value meaning "no notation for this term"), or "" if the field itself is missing
    (a hard-constraint violation, since the field is mandatory even when the honest value is "—").
    `definition`/`boundary` are prose that may or may not mention the declared notation.
    """
    DASH_MARKERS = {"—", "-", "–"}
    if not concepts:
        return 0.0
    scores = []
    for c in concepts:
        notation_raw = (c.get("notation") or "").strip()
        name = (c.get("name") or "").strip()
        prose = f"{c.get('definition') or ''} {c.get('boundary') or ''}"

        if notation_raw == "":
            # Field is mandatory; a truly missing value (not even the honest placeholder) is a
            # defect, not neutral -- the hard constraint requires penalizing missing inputs.
            scores.append(0.0)
            continue

        if notation_raw in DASH_MARKERS:
            leaks = [
                m.group(0) for m in SYMBOL_LEAK_PATTERN.finditer(prose)
                if m.group(0).strip(".,:;()").lower() != name.lower()
            ]
            if leaks:
                scores.append(0.0)  # a real symbol was stranded in prose -> missed extraction
            else:
                scores.append(0.8)  # honest absence, nothing to extract -- good, not maximal
            continue

        # Notation is declared: check whether it's actually grounded anywhere in the prose.
        sym_tokens = _notation_symbol_tokens(notation_raw)
        if not sym_tokens:
            scores.append(0.5)
            continue
        prose_low = prose.lower()
        grounded = sum(1 for t in sym_tokens if t.lower() in prose_low)
        fraction = grounded / len(sym_tokens)
        if fraction == 0.0:
            scores.append(0.5)  # declared but never used anywhere -- decorative notation
        else:
            scores.append(0.6 + 0.4 * fraction)
    return sum(scores) / len(scores)
```

**What it does & why.** It sorts concepts into three buckets: field genuinely missing (defect,
0.0), field honestly `"—"` (checked for a stranded symbol that should have been extracted instead;
0.0 if leaked, 0.8 if clean), and field populated (checked for whether any of its symbol tokens
actually appear in the Definition/Boundary prose; 0.5 if none do — decorative — scaling up to 1.0
as more of the declared tokens are actually grounded in the writeup).

**Why it's hard to Goodhart.** Declaring `Notation: —` to dodge the "explain your notation" work
only pays off if the prose truly never uses a symbol for this concept — the moment a compiler
writes prose containing the concept's actual symbol (which it usually must, to explain a
formula-bearing term at all), the leak check catches the mismatch and the honest-absence credit is
lost. Conversely, copy-pasting ornate notation from the source paper without engaging with it
caps out at 0.5 (worse than honest absence's 0.8) — so decorative notation is actively discouraged
relative to just not claiming any, and the only way to beat honest absence is to genuinely use the
declared symbols in the definition/boundary text, which is the real work being targeted.

---

## Combination

These five metrics pull compilation behavior in different, partially conflicting directions, and
none can be maxed out by a single cheap edit. Metric 1 (BCIS) rewards boundary text that is long
and *dissimilar* to the Definition; Metric 3 (DGS) rewards Definitions that are long and
paper-specific. A compiler that tries to cheaply pass BCIS by copying grounded-sounding phrases
from the Definition into the Boundary field gets caught by BCIS's own paraphrase-overlap check, so
it must instead write genuinely new boundary content — real work. Metric 4 (DCP) closes the
loophole where a compiler inflates Definition length purely to win Metric 3's length floor:
padding with filler either repeats the heading term (caught by DCP) or dilutes the
grounding-marker density (caught by DGS).

Metric 2 (CID) now resists two additional dodges beyond the stage-1 free-text-padding defense:
leaving `Related concepts` blank everywhere is no longer "cheap and uniform" — the shallow-read
multiplier makes near-universal absence cost disproportionately more than the sum of its
per-concept parts, so a compiler cannot simply accept a flat per-concept tax and skip the field
throughout. And padding the field with plausible-looking but fabricated sibling names (a near-miss
reword of a real heading, rather than genuine field jargon) now actively costs points instead of
merely failing to earn them, while legitimate external terminology — which won't be textually
close to any of *this* document's own headings — passes through untouched, exactly preserving the
shape doc's requirement that `Related concepts` may legitimately reference terms outside this
document.

Metric 5 (NPEF) adds an axis the first four don't touch — whether declared notation is actually
used, and whether stranded symbols reveal a missed extraction — while explicitly refusing to
punish the shape doc's named legitimate case (prose-only, `Notation: —` clinical/endpoint
vocabularies). It also interacts with DGS/DCP: a compiler that invents fake notation to look
rigorous, then never mentions it in the definition, pays the NPEF decorative-notation cost (0.5)
even if that definition separately scores well on groundedness — there's no single edit that
raises NPEF and DGS together without the notation and the prose genuinely agreeing with each
other. In short: gaming boundary conditions costs you on Definition-overlap, gaming Definition
length costs you on circularity or groundedness, gaming the relation graph costs you on
definitional support and now also on shallow-read uniformity and orphan fabrication, and gaming
notation costs you on prose-grounding — there is no single cheap edit that raises all five metrics
at once.
