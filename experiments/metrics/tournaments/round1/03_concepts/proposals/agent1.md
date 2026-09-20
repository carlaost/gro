# Proposer 1 — metrics for `logic/concepts.md`

Input assumption for all functions below: the artifact is parsed into a list of concept records,
each a dict:
```python
concept = {
    "name": str,                 # the "## {Term Name}" heading text
    "notation": str,              # "—" if none
    "definition": str,            # markdown prose
    "boundary_conditions": str,   # markdown prose, or "Not specified in paper"
    "related_concepts": list[str] # parsed from comma-separated text; [] if field is empty/missing
}
concepts: list[dict]  # the full artifact, one entry per "## {Term Name}" section
```
All functions take `concepts` (possibly `[]`) and return a float in `[0, 1]` (1 = strong evidence
of good science, 0 = strong evidence of bad/absent science). Per the hard constraint, an empty or
near-empty `concepts` list is scored low, not skipped.

---

## 1. Boundary-Condition Depth

**How it signals good science.** A paper's technical vocabulary is only rigorously specified if the
scope of applicability is stated concretely — under what conditions the concept holds, breaks, or was
measured. "Not specified in paper" is sometimes an honest report of the source, but *generic
boilerplate* boundary text (present but contentless, e.g. "applies in most cases") is evidence of a
shallow compile, and a high rate of true absence across many concepts is itself evidence the source
paper under-specifies scope — either way, low depth means low rigor.

**Compute function:**
```python
import re

def boundary_condition_depth(concepts: list[dict]) -> float:
    # Assumes each concept dict has 'boundary_conditions' (str).
    if not concepts:
        return 0.0

    NOT_SPECIFIED = "not specified in paper"
    # signals of genuine, concrete scope language vs filler
    concrete_markers = re.compile(
        r"\b(requires?|assumes?|only when|only if|does not apply|breaks? down|"
        r"threshold|unless|excludes?|restricted to|valid for|holds? (for|when)|"
        r"\d+(\.\d+)?%?|n\s*=\s*\d+)\b",
        re.IGNORECASE,
    )
    scores = []
    for c in concepts:
        text = (c.get("boundary_conditions") or "").strip()
        if not text or text.lower() == NOT_SPECIFIED:
            scores.append(0.0)
            continue
        n_words = len(text.split())
        has_concrete = bool(concrete_markers.search(text))
        if n_words < 6:
            # too short to be a real scope statement even if it has a marker word
            scores.append(0.15)
        elif has_concrete:
            scores.append(1.0)
        else:
            # present, wordy, but generic/vague — "applies broadly", "in many cases"
            scores.append(0.35)
    return sum(scores) / len(scores)
```

**What the function does & why.** For every concept, it classifies the `Boundary conditions` field
into one of four buckets: truly absent/"Not specified" (0.0), present but trivially short (0.15),
present and wordy but generic filler (0.35), or present with concrete scope markers — quantifiers,
conditionals, numeric thresholds, explicit exclusions (1.0). It averages across all concepts, so a
`concepts.md` dominated by real, concrete scope statements scores near 1, and one dominated by
"Not specified" or vague boilerplate scores near 0.

**Why it's hard to Goodhart.** You cannot fix this by pasting a single generic boundary sentence into
every entry ("applies in most cases") — the concrete-marker regex and the length floor specifically
reward numeric/conditional specificity, which a lazy compiler is unlikely to fabricate consistently
across many concepts without contradicting the actual `Definition` text (checked by metric 3) or the
paper's real content. Fabricating plausible-looking numeric thresholds to game this metric risks
manufacturing claims that don't match the source, which is a different, more expensive failure mode.

---

## 2. Concept-Graph Closure

**How it signals good science.** `logic/concepts.md` is supposed to capture *this paper's* conceptual
structure, not a bag of independently-defined terms. If a term's `Related concepts` mostly point to
*other headings that actually exist in the same document*, the compiler has captured a coherent,
internally-connected vocabulary — evidence the concepts were extracted from a real network of ideas
in the paper rather than generated one at a time from surface text. Related-concept lists that mostly
dangle (pointing to nothing else in the document) suggest disconnected, possibly padded entries.

**Compute function:**
```python
def concept_graph_closure(concepts: list[dict]) -> float:
    # Assumes 'name' (str) and 'related_concepts' (list[str]) on each concept.
    if not concepts:
        return 0.0

    names_norm = {c["name"].strip().lower() for c in concepts if c.get("name")}

    def normalize(s: str) -> str:
        return s.strip().lower()

    per_concept_scores = []
    for c in concepts:
        related = [normalize(r) for r in (c.get("related_concepts") or []) if r.strip()]
        if not related:
            # a real concept with zero stated relations to anything else is a red flag:
            # either isolated jargon or an incomplete compile
            per_concept_scores.append(0.1)
            continue
        # fuzzy containment: related name matches (or is substring of) a real heading
        hits = 0
        for r in related:
            if r in names_norm or any(r in n or n in r for n in names_norm):
                hits += 1
        internal_ratio = hits / len(related)
        # reward some internal closure but don't require 100% (external field terms like
        # "mass spectrometry" are legitimate and expected) — cap credit at a healthy mix
        per_concept_scores.append(min(1.0, 0.3 + 0.7 * internal_ratio))

    return sum(per_concept_scores) / len(per_concept_scores)
```

**What the function does & why.** For each concept, it checks how many of its listed related concepts
resolve (exactly or approximately) to other section headings actually present in the same
`concepts.md`. A concept with no related-concepts at all is penalized outright (0.1) since the field
existing-but-empty is treated as thin, per the hard constraint. Concepts with some but not full
internal overlap get a graded score (a baseline 0.3 plus a bonus for internal hits), because fully
external relations (referencing standard field terms not defined in this doc) are normal and
shouldn't be punished as harshly as total isolation. Averaging over all concepts yields a document-
level graph-coherence score.

**Why it's hard to Goodhart.** Padding every `Related concepts` field with other concept names verbatim
to maximize `internal_ratio` is visible as suspiciously perfect closure and mechanically inflates the
list-length in every entry, which interacts badly with metric 4 (specificity) since a document where
every concept just cites every other concept starts to look templated and drags down cross-entry
distinctiveness. Randomly relating unconnected concepts to game this also produces logically
nonsensical relations that a semantic reviewer (or a downstream Level-2 check) would flag independently.

---

## 3. Notation-to-Prose Grounding

**How it signals good science.** When a concept declares real symbolic `Notation` (not "—"), rigorous
science *uses* that notation to talk precisely about the object — the symbol should reappear in the
`Definition` and/or `Boundary conditions` prose, showing the notation is operational rather than
decorative window-dressing bolted onto a fundamentally prose-only, hand-wavy concept.

**Compute function:**
```python
import re

def notation_prose_grounding(concepts: list[dict]) -> float:
    # Assumes 'notation' (str, "—" if none), 'definition' (str), 'boundary_conditions' (str).
    if not concepts:
        return 0.0

    def tokenize_notation(notation: str) -> list[str]:
        # pull out symbol-like tokens: short alnum/greek/subscript chunks, ignore stopword-y wrapper text
        raw = re.split(r"[,;()]", notation)
        toks = []
        for r in raw:
            r = r.strip()
            if not r:
                continue
            # keep short, symbol-like tokens (avoid matching entire prose clauses)
            candidate = r.split(":")[0].split(" in ")[0].strip()
            if 0 < len(candidate) <= 20:
                toks.append(candidate)
        return toks

    scored = []
    for c in concepts:
        notation = (c.get("notation") or "").strip()
        if notation == "—" or not notation:
            # no notation claimed at all is neutral-low: not every legitimate concept needs
            # notation, but a doc heavy on undefined "—" concepts loses richness elsewhere
            # (handled by other metrics); here we simply exclude it from the denominator logic
            # by scoring it as a mild pass so it doesn't get free credit or unfair punishment.
            scored.append(0.6)
            continue
        toks = tokenize_notation(notation)
        if not toks:
            scored.append(0.2)
            continue
        body = f"{c.get('definition','')} {c.get('boundary_conditions','')}"
        hits = sum(1 for t in toks if t.lower() in body.lower())
        scored.append(min(1.0, hits / len(toks)))

    return sum(scored) / len(scored)
```

**What the function does & why.** For each concept that declares real notation, it extracts
symbol-like tokens from the `Notation` field and checks whether they actually appear in the
`Definition`/`Boundary conditions` prose. If the notation is never referenced again, that's a sign the
notation was copied in as decoration without being explained or used. Concepts without notation get a
flat neutral score so the metric isn't rewarding/punishing the mere absence of notation (which is
often correct, per the shape doc — clinical/endpoint concepts skew toward `Notation: —`), only
punishing notation that's declared but ungrounded.

**Why it's hard to Goodhart.** Simply repeating the notation string verbatim inside the definition to
force a token match is easy to do once, but doing it convincingly across many concepts without the
surrounding prose becoming circular or redundant is noticeable, and it directly conflicts with metric
1 and metric 4 (concrete, non-boilerplate content) — stuffing a definition with bare symbol repeats to
pass this metric makes the definition read as templated rather than substantive, which those metrics
penalize.

---

## 4. Definitional Specificity (anti-genericness)

**How it signals good science.** The stated purpose of `concepts.md` is a set of terms "specific to
this paper's contribution or field," explicitly *not* a glossary of borrowed/generic terms. A genuine,
hard-won technical vocabulary entry reads differently from a dictionary definition: it references
concrete instantiations — numbers, named methods/datasets/models, the paper's own terminology — rather
than only generic connector language ("is a method used to...", "refers to the process of...").

**Compute function:**
```python
import re

def definitional_specificity(concepts: list[dict]) -> float:
    # Assumes 'definition' (str) on each concept; treats missing/empty as maximally generic (worst).
    if not concepts:
        return 0.0

    generic_phrases = re.compile(
        r"\b(is a (method|process|way|technique) (used|for)|refers to|"
        r"is defined as|is a type of|generally|commonly|in general|"
        r"is a term (used|for))\b",
        re.IGNORECASE,
    )
    concrete_markers = re.compile(
        r"(\d+(\.\d+)?%?|\b[A-Z]{2,}[a-z]*\d*\b|\bp\s*[<=]\s*0?\.\d+|"
        r"\b(here|in this (paper|study|nma|analysis)|our)\b)",
        re.IGNORECASE,
    )

    scores = []
    for c in concepts:
        text = (c.get("definition") or "").strip()
        if len(text.split()) < 5:
            scores.append(0.0)  # empty or near-empty definition: worst case, not skipped
            continue
        generic_hits = len(generic_phrases.findall(text))
        concrete_hits = len(concrete_markers.findall(text))
        # score rewards concrete grounding, penalizes generic filler density
        raw = concrete_hits - 0.5 * generic_hits
        # squash into [0,1] with a soft cap
        scores.append(max(0.0, min(1.0, 0.2 + 0.2 * raw)))

    return sum(scores) / len(scores)
```

**What the function does & why.** It scans each `Definition` for two competing signal classes: generic
dictionary-style connector phrases (penalized) and concrete, paper-specific markers — numbers,
acronyms/named entities, explicit self-reference like "in this study/NMA" (rewarded). The net signal
is squashed into a bounded per-concept score and averaged. An empty or very short definition scores
zero outright rather than being excluded, satisfying the hard constraint that thin/missing content is
penalized, not skipped.

**Why it's hard to Goodhart.** Stripping out generic phrases alone doesn't help if nothing concrete
replaces them (raw stays low near the 0.2 floor); stuffing in numbers/acronyms without a genuine
technical claim behind them risks contradicting the `Boundary conditions` or looking incoherent next
to `Related concepts`, and fabricated statistics inflate this metric while creating exposure for a
downstream fact-check / Level-2 semantic review that cross-reads definitions against the paper's real
claims.

---

## 5. Boilerplate-Uniformity Penalty (cross-entry redundancy)

**How it signals good science.** Distinct technical concepts should read as distinct: a `concepts.md`
where multiple entries share near-identical `Definition` or `Boundary conditions` phrasing (differing
mainly by the term name) suggests either padding (invented "concepts" that aren't really distinct) or
a low-effort templated compile rather than genuinely differentiated definitions grounded in the paper.

**Compute function:**
```python
from difflib import SequenceMatcher

def boilerplate_uniformity_penalty(concepts: list[dict]) -> float:
    # Assumes 'definition' (str) and 'boundary_conditions' (str) on each concept.
    # Returns a score where 1.0 = all entries meaningfully distinct, 0.0 = heavily duplicated/thin.
    if len(concepts) < 2:
        # a single concept (or none) can't be checked for cross-entry redundancy; treat
        # under-population itself as a low-information case per the hard constraint
        return 0.3 if concepts else 0.0

    def sim(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

    fields = ["definition", "boundary_conditions"]
    n = len(concepts)
    pair_sims = []
    for field in fields:
        texts = [(c.get(field) or "").strip() for c in concepts]
        for i in range(n):
            for j in range(i + 1, n):
                if not texts[i] or not texts[j]:
                    continue
                pair_sims.append(sim(texts[i], texts[j]))

    if not pair_sims:
        return 0.0  # all fields empty across the board: worst case

    avg_sim = sum(pair_sims) / len(pair_sims)
    high_dupe_fraction = sum(1 for s in pair_sims if s > 0.6) / len(pair_sims)
    # penalize both average similarity and the fraction of near-duplicate pairs
    score = 1.0 - min(1.0, 0.6 * avg_sim + 0.6 * high_dupe_fraction)
    return max(0.0, score)
```

**What the function does & why.** It pairwise-compares every concept's `Definition` and `Boundary
conditions` text against every other concept's, using string similarity. It combines two signals: the
average similarity across all pairs, and the fraction of pairs that are near-duplicates (similarity >
0.6). High values of either drag the score toward 0. Documents with too few concepts to compare, or
with empty fields across the board, are scored low rather than skipped, per the hard constraint.

**Why it's hard to Goodhart.** The obvious dodge — writing superficially different sentences for each
entry — is fine and is exactly what *should* happen for genuinely distinct concepts; you cannot
cheaply defeat this metric without actually diversifying content, and doing so by injecting irrelevant
per-entry filler to lower string similarity will tank metric 4 (specificity) and metric 1 (concrete
boundary markers), since padding text is generic by construction.

---

## Combination

These five metrics are jointly hard to game because they pull in different, sometimes opposing
directions on the same text. Padding `Boundary conditions` with concrete-sounding filler to win metric
1 makes entries converge in phrasing and tanks metric 5's uniformity check. Fabricating numbers/acronyms
to win metric 4's specificity score risks contradicting the `Notation`-to-prose relationship checked in
metric 3, or clashing with genuinely stated boundary conditions from metric 1. Stuffing `Related
concepts` with cross-references to inflate metric 2's graph closure increases apparent redundancy
across entries, which metric 5 penalizes. And none of the metrics reward simply adding more concept
sections — metric 5 punishes near-duplicate padding entries directly, while metrics 1, 3, and 4 punish
each individual thin/generic entry regardless of how many there are. A paper can only score well
across the whole set by having a `concepts.md` that is genuinely distinct per entry, notation that is
actually used, boundary conditions that are actually concrete, and a relation structure that is
actually coherent — which is precisely what "good science" vocabulary documentation looks like.
