# Proposer 2 — metrics for `logic/concepts.md`

Assumed parsed shape (Python): a list of dicts, one per `## {Term}` heading:

```python
concept = {
    "name": str,
    "notation": str,       # "—" if none stated
    "definition": str,     # markdown prose
    "boundary": str,       # markdown prose, or "Not specified in paper"
    "related": list[str],  # parsed from the comma-separated "Related concepts" field
}
concepts: list[dict]  # the whole artifact; may be empty in a degenerate parse failure
```

---

## 1. Boundary-Condition Depth

**How it signals good science.** A term's scientific content is defined as much by where it stops
applying as by what it says. A compiler (and, behind it, a paper) that can state *when this measure
breaks down / what it assumes / what regime it's valid in* is demonstrating it actually understood the
method rather than paraphrasing a definition. Papers that only ever state "what X is" and never "where X
holds" are shipping vocabulary lists, not science.

**Compute function.**

```python
import re

def boundary_condition_depth(concepts: list[dict]) -> float:
    """
    Assumes: each concept dict has 'boundary' (str). Missing key treated as "" (empty = worst case,
    same as an explicit placeholder — the constraint requires penalizing absence, not skipping it).
    """
    PLACEHOLDER = "not specified in paper"
    CONDITIONAL_MARKERS = [
        "when", "requires", "assumes", "unless", "only if", "provided that",
        "applies to", "does not apply", "excludes", "limited to", "valid for",
        "breaks down", "fails when", "outside of", "restricted to",
    ]

    if not concepts:
        return 0.0

    scores = []
    for c in concepts:
        text = (c.get("boundary") or "").strip()
        if not text or text.lower() == PLACEHOLDER:
            scores.append(0.0)
            continue
        # reward genuine conditional/scoping language, not just prose length
        hits = sum(1 for m in CONDITIONAL_MARKERS if m in text.lower())
        # length is a weak secondary signal (a one-clause boundary is thinner than a paragraph)
        length_bonus = min(len(text) / 220.0, 1.0)
        marker_score = min(hits / 2.0, 1.0)
        scores.append(0.6 * marker_score + 0.4 * length_bonus)

    return sum(scores) / len(scores)
```

**What the function does & why.** For every concept it checks whether `Boundary conditions` is empty or
the known placeholder string (score 0), and otherwise scores it by (a) how many genuinely scoping
words/phrases appear ("when", "requires", "excludes", "breaks down", ...) and (b) prose length as a
weak tie-breaker, capped so a long-winded but empty-content boundary can't dominate. The per-concept
scores are averaged into one artifact-level number in [0, 1].

**Why it's hard to Goodhart.** A compiler could stuff a fake boundary sentence with conditional-sounding
words ("this applies when X, unless Y") without it being true or specific — that raises this score
cheaply. But the marker list rewards *generic* scoping language regardless of content, so gaming it means
writing many short, keyword-stuffed, low-information boundary sentences across every concept — which
directly tanks Metric 3 (Definitional Specificity), because that sentence pattern is exactly the kind of
generic template with low specific-token density.

---

## 2. Notation–Prose Binding

**How it signals good science.** When a paper introduces formal notation, good exposition ties the
symbol back into the prose that explains it — the definition should actually *use* the notation it
declares, not just decorate the entry with a symbol nobody references again. A field that states
`p217 (nodes: p217_MS, ...)` and then never mentions `p217` again in the definition is a sign the
notation was lifted from the source without being woven into the explanation.

**Compute function.**

```python
import re

def _notation_tokens(notation: str) -> list[str]:
    if not notation or notation.strip() == "—":
        return []
    # split on non-alnum/underscore boundaries, keep tokens of length >= 2
    return [t for t in re.split(r"[^A-Za-z0-9_]+", notation) if len(t) >= 2]

def notation_prose_binding(concepts: list[dict]) -> float:
    """
    Assumes: 'notation' and 'definition' string fields. A concept with notation == "—" (or empty) is
    treated as contributing zero to the numerator AND zero to the denominator's "credit" side —
    but per the hard constraint, an artifact that is notation-free across the board must not score
    as if it opted out; it is scored on the coverage term below instead.
    """
    if not concepts:
        return 0.0

    with_notation = 0
    bound = 0
    for c in concepts:
        toks = _notation_tokens(c.get("notation") or "")
        if not toks:
            continue
        with_notation += 1
        defn = (c.get("definition") or "").lower()
        if any(t.lower() in defn for t in toks):
            bound += 1

    coverage = with_notation / len(concepts)          # how much of the field uses real notation at all
    if with_notation == 0:
        binding_rate = 0.0                              # nothing to bind -> can't claim credit
    else:
        binding_rate = bound / with_notation

    # An artifact that is legitimately prose-only (clinical/instrument vocab, per the shape doc) still
    # gets scored, but on binding alone once it has any notation; if it never uses notation at all,
    # this metric contributes its coverage floor rather than an automatic pass.
    return 0.5 * coverage + 0.5 * binding_rate
```

**What the function does & why.** It extracts symbol-like tokens from each `Notation` field, then checks
whether at least one of those tokens actually recurs inside that same concept's `Definition` prose. It
combines two signals: how much of the artifact bothers to introduce real notation at all (`coverage`),
and, among those that do, how often the notation is actually referenced in the explanation rather than
left inert (`binding_rate`). This directly targets copy-pasted-looking notation blocks.

**Why it's hard to Goodhart.** The cheap attack is to literally repeat the notation string inside the
definition sentence to force a token match. But doing that for every entry produces visibly repetitive,
templated definitions — which drags down Metric 3's specific-token-density measure (repeated boilerplate
lowers the ratio of *new* information per sentence) and does nothing for Metric 1's boundary-condition
score, so the gaming effort doesn't transfer.

---

## 3. Definitional Specificity (anti-genericness)

**How it signals good science.** The shape doc is explicit that this artifact should hold the paper's
*genuine, specific* technical vocabulary, not a borrowed glossary of generic field terms. A concept
entry that could have been written by looking up the term on Wikipedia (no paper-specific quantities,
instruments, cohorts, thresholds, or model names) is filler, not evidence the compiler engaged with this
paper's contribution.

**Compute function.**

```python
import re

_NUM_RE = re.compile(r"\d")
_PROPER_RE = re.compile(r"\b[A-Z][a-zA-Z0-9\-]{2,}\b")
GENERIC_STOPWORDS = {"The", "This", "In", "A", "An", "It", "Here", "These", "That"}

def definitional_specificity(concepts: list[dict]) -> float:
    """
    Assumes: 'definition' str field. Empty/missing definition (should be structurally impossible per
    the shape's "mandatory core", but if a parse yields one) scores 0 for that entry.
    """
    if not concepts:
        return 0.0

    scores = []
    for c in concepts:
        defn = (c.get("definition") or "").strip()
        if not defn:
            scores.append(0.0)
            continue
        words = re.findall(r"\w+", defn)
        n_words = max(len(words), 1)

        has_number = bool(_NUM_RE.search(defn))
        proper_nouns = [w for w in _PROPER_RE.findall(defn) if w not in GENERIC_STOPWORDS]
        specific_token_density = min(len(set(proper_nouns)) / (n_words / 15.0 + 1e-6), 1.0)

        # a definition with no numbers, no distinctive proper-noun/acronym tokens, and no cross-links
        # to other concepts in this same file reads as generic/borrowed
        cross_linked = bool(c.get("related"))

        score = 0.4 * has_number + 0.4 * specific_token_density + 0.2 * cross_linked
        scores.append(score)

    return sum(scores) / len(scores)
```

**What the function does & why.** For each definition it looks for concrete markers of paper-specific
content: numeric values/thresholds, distinctive capitalized tokens (method names, acronyms, cohort/
platform names) normalized by definition length, and whether the entry is woven into the rest of the
concept graph via `Related concepts`. Generic textbook-style definitions tend to have none of these;
paper-specific ones do. Averaged into one score in [0, 1].

**Why it's hard to Goodhart.** One could inflate this by sprinkling random capitalized words or fake
numbers into a definition. But those tokens then have to survive Metric 2's notation-binding check (fake
numbers unconnected to any declared notation don't help there) and, more importantly, injecting
noise-words into definitions makes the prose read as padded rather than precise — which is exactly the
failure mode Metric 4 below is built to catch via redundancy across entries.

---

## 4. Cross-Entry Redundancy Penalty

**How it signals good science.** A well-curated concept list defines each distinct idea once and links
to it elsewhere via `Related concepts`, rather than re-explaining the same idea under multiple headings
with near-duplicate prose. High redundancy across `Definition` fields signals the compiler padded the
file to hit a section-count impression rather than doing the harder work of identifying genuinely
distinct, non-overlapping technical terms.

**Compute function.**

```python
def _shingles(text: str, n: int = 5) -> set:
    words = text.lower().split()
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}

def cross_entry_redundancy_penalty(concepts: list[dict]) -> float:
    """
    Assumes: 'definition' str field on each concept. Fewer than 2 concepts -> nothing to compare;
    scored at the floor (0.0) rather than skipped, since an artifact too thin to even assess for
    redundancy is exactly the "thin input" case the hard constraint says must be penalized, not N/A'd.
    """
    n = len(concepts)
    if n < 2:
        return 0.0

    defs = [(c.get("definition") or "") for c in concepts]
    shingle_sets = [_shingles(d) for d in defs]

    pair_scores = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = shingle_sets[i], shingle_sets[j]
            if not a or not b:
                continue
            jaccard = len(a & b) / len(a | b)
            pair_scores.append(jaccard)

    if not pair_scores:
        return 0.0

    avg_overlap = sum(pair_scores) / len(pair_scores)
    max_overlap = max(pair_scores)
    # score is "non-redundancy": high overlap -> low score
    return max(0.0, 1.0 - (0.6 * avg_overlap + 0.4 * max_overlap))
```

**What the function does & why.** It computes 5-word shingles of every definition and measures pairwise
Jaccard overlap across all concept pairs, combining the average overlap (diffuse repetition across the
whole file) with the worst single pair (two near-duplicate entries hiding among otherwise distinct ones).
The final score is `1 - overlap`, so a clean, non-redundant concept list scores near 1 and a padded one
with copy-pasted definitions scores near 0.

**Why it's hard to Goodhart.** The obvious dodge — paraphrase duplicate entries with different words —
requires generating genuinely varied language for what is conceptually the same term, which drives the
`related` field either toward listing the duplicate (a Related-concepts edge is cheaper to add honestly
than to keep faking novel prose) or leaves the concept looking like a distinct entry with real content,
in which case it's no longer redundant, it's just... a legitimately new concept. Either path costs the
gamer real effort or removes the padding, and any paraphrase attempt that keeps meaning-overlap high
while varying surface words still gets caught by shingle overlap unless the rewrite is substantial enough
to also change what Metric 3 measures as its specific-token content.

---

## Combination

These four metrics are built to pull against each other under gaming pressure. Padding
`Boundary conditions` with generic conditional-sounding filler (gaming M1) produces low-specificity,
templated prose that M3 and M4 penalize. Faking notation/definition token overlap to win M2 requires
inserting repeated or noise tokens that either read as boilerplate (hurting M4's redundancy check across
entries) or as unsupported specificity that M3's structure discourages once cross-checked against actual
distinctiveness. And padding the whole file with more sections to look thorough (an obvious tournament
tactic against a soft ≥5 count) directly increases the pairwise-comparison surface for M4, which is
specifically most punishing exactly when entries multiply without adding distinct content. A paper that
wins all four simultaneously has to actually produce concept entries that are numerous, individually
specific, internally bounded with real scope language, notation that's woven into prose, and mutually
non-redundant — which is a reasonable operational definition of "the compiler did the hard, honest work
of extracting this paper's real vocabulary."
