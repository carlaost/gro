# Proposer 4 — Metrics for `PAPER.md` (root manifest)

All functions assume a parsed representation of `PAPER.md` shaped like:

```python
paper = {
    "frontmatter": {
        "title": str, "authors": list[str], "year": int, "venue": str,
        "doi": str, "ara_version": str, "domain": str,
        "keywords": list[str], "claims_summary": list[str], "abstract": str,
    },
    "body": {
        "overview": str,   # the "## Overview" prose block
        "layer_index": {
            "cognitive": list[{"file": str, "desc": str}] | None,
            "physical":  list[{"file": str, "desc": str}] | None,
            "data":      list[{"file": str, "desc": str}] | None,
            "trace":     list[{"file": str, "desc": str}] | None,
            "evidence":  list[{"file": str, "desc": str}] | None,
        },
    },
}
```

Missing/absent keys are represented as `None` or empty containers, never dropped. Every function
below is defensive against that and treats absence as a scored penalty, never as `N/A`.

---

## 1. Manifest Arithmetic Consistency

**How it signals good science.** A compiler (and, upstream, a paper) that keeps its own numbers
straight — the count of claims it advertises equals the count it lists, the count of evidence
items it says it indexed equals the count of rows in that index — is exhibiting the same discipline
that underlies good science: internal consistency of reported quantities. A manifest that
contradicts itself in its own arithmetic is a weak proxy for a paper (or compilation pipeline) that
doesn't check its own reported numbers elsewhere either (sample sizes, N in tables vs. N in text,
etc.). This is a "canary" signal: cheap to check, and a failure here correlates with the kind of
sloppiness that shows up in more expensive-to-audit places.

**Compute function.**

```python
import re

def manifest_arithmetic_consistency(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is a list[str] (possibly empty/missing).
    Assumes: paper["body"]["layer_index"]["cognitive"] / ["evidence"] are lists of
    {"file","desc"} dicts (possibly None/missing), and that desc text contains the compiler's
    own stated counts in prose, e.g. "8 falsifiable claims (C01-C08)" or
    "Index of 2 tables + 3 figures".
    Returns a score in [0, 1].
    """
    fm = paper.get("frontmatter") or {}
    body = paper.get("body") or {}
    layer_index = body.get("layer_index") or {}

    checks = []  # each entry: True (consistent) / False (mismatch or missing)

    # --- Check A: claims_summary length vs. claims.md's self-reported count ---
    claims_summary = fm.get("claims_summary") or []
    cognitive = layer_index.get("cognitive") or []
    claims_desc = next((row.get("desc", "") for row in cognitive
                         if "claims.md" in row.get("file", "")), "")
    m = re.search(r"(\d+)\s+falsifiable claims", claims_desc)
    if not claims_summary or not claims_desc or not m:
        checks.append(False)  # missing data on either side is a penalty, not a skip
    else:
        checks.append(int(m.group(1)) == len(claims_summary))

    # --- Check B: evidence README's stated "N tables + M figures" vs. actual row counts ---
    evidence = layer_index.get("evidence") or []
    readme_desc = next((row.get("desc", "") for row in evidence
                         if "README" in row.get("file", "")), "")
    m2 = re.search(r"(\d+)\s+tables?\s*\+\s*(\d+)\s+figures?", readme_desc)
    n_table_rows = sum(1 for row in evidence if "/tables/" in row.get("file", ""))
    n_figure_rows = sum(1 for row in evidence if "/figures/" in row.get("file", ""))
    if not evidence or not m2:
        checks.append(False)
    else:
        checks.append(int(m2.group(1)) == n_table_rows and int(m2.group(2)) == n_figure_rows)

    # --- Check C: trace layer states a node count at all (sanity: nonzero, well-formed) ---
    trace = layer_index.get("trace") or []
    trace_desc = trace[0].get("desc", "") if trace else ""
    m3 = re.search(r"(\d+)-node", trace_desc)
    checks.append(bool(m3) and int(m3.group(1)) > 0)

    return sum(checks) / len(checks)
```

**What the function does & why.** It re-derives, from prose the compiler wrote about itself,
numbers that should agree with structural counts elsewhere in the same document, and scores the
fraction of agreements. It deliberately does *not* trust either side blindly — a missing
`claims_summary`, a missing description, or an un-parseable description all count as a failed
check rather than being excluded from the denominator, per the hard constraint.

**Why it's hard to Goodhart.** To game this you'd have to keep every redundant count in the
manifest in lockstep by construction — which is exactly the behavior we want. A compiler/paper
that fakes consistency by simply never stating counts in prose (to dodge the regex) fails Check A/B
outright (no match → penalized), so evasion is not cheaper than honesty. The only route to a high
score is to actually keep the numbers straight everywhere.

---

## 2. Identifier & Pre-registration Provenance Rigor

**How it signals good science.** Verifiable identifiers (a real DOI, a real registration ID)
are the connective tissue that lets independent readers check a claim against its source, and
public pre-registration is one of the strongest known institutional defenses against p-hacking
and HARKing. A manifest that surfaces a well-formed DOI *and* mentions a registration (PROSPERO,
OSF, ClinicalTrials.gov, protocols.io, etc.) in its overview is reporting on a paper that made
itself checkable and pre-committed. A manifest that has neither is reporting on a paper that
offers the reader nothing to verify against.

**Compute function.**

```python
import re

_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
_ARXIV_RE = re.compile(r"^(arXiv:)?\d{4}\.\d{4,5}(v\d+)?$", re.IGNORECASE)
_REGISTRY_RE = re.compile(
    r"\b(PROSPERO|OSF\.io|clinicaltrials\.gov|protocols\.io|ISRCTN|EudraCT)\b", re.IGNORECASE
)

def identifier_provenance_rigor(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["doi"] is a string (real id, arXiv id, or the literal
    "Not specified in paper"). Assumes: paper["body"]["overview"] is prose text (possibly
    missing/empty).
    Returns a score in [0, 1]: 0.6 weight on identifier validity, 0.4 on registration mention.
    """
    fm = paper.get("frontmatter") or {}
    body = paper.get("body") or {}

    doi = (fm.get("doi") or "").strip()
    if not doi or doi.lower() == "not specified in paper":
        id_score = 0.0
    elif _DOI_RE.match(doi) or _ARXIV_RE.match(doi):
        id_score = 1.0
    else:
        id_score = 0.2  # present but malformed/unverifiable string — better than nothing, barely

    overview = body.get("overview") or ""
    reg_score = 1.0 if _REGISTRY_RE.search(overview) else 0.0

    return 0.6 * id_score + 0.4 * reg_score
```

**What the function does & why.** It regex-validates the DOI/arXiv field against real identifier
grammars (not just "is the string non-empty") so a garbage placeholder can't pass as a valid id,
and it separately rewards an explicit, named pre-registration mention in the overview prose. Both
sub-scores default to zero on absence — an unspecified DOI is scored, not skipped.

**Why it's hard to Goodhart.** Fabricating a DOI that matches the regex risks it being a
plausible-looking but non-resolving identifier — this metric alone can't catch that, but it's
cross-checked against Metric 1's consistency framing and Metric 5's overlap check below: a
paper that fabricates identifiers to inflate this score while thin everywhere else will still
read as unusually generic/copy-heavy on Metric 5 and quantitatively empty on Metric 3, since
inventing a fake DOI does nothing to manufacture real statistical content elsewhere.

---

## 3. Claim Quantitative Grounding Density

**How it signals good science.** Falsifiable, quantitatively-anchored claims (effect sizes,
confidence intervals, p-values, ranking scores) are what let a claim be checked, replicated, or
overturned. Vague claims ("X improves diagnostic performance") are unfalsifiable and unscoreable
by construction. A manifest whose `claims_summary` is dense with numbers, intervals, and named
statistics is reporting on a paper whose central contributions are precise enough to be wrong in a
checkable way — which is a precondition for good science, not a guarantee, but a necessary one.

**Compute function.**

```python
import re

_NUMERIC_ANCHOR_RE = re.compile(
    r"(\d+(\.\d+)?%?)|(\bCI\b)|(\bp\s*[<=]\s*0?\.\d+)|(\bI2\b|\bI\^2\b)|"
    r"(\bAUC\b)|(\bOR\b)|(\bHR\b)|(\bSUCRA\b)|(P-score)", re.IGNORECASE
)

def claim_quantitative_grounding_density(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is list[str] (possibly empty/missing).
    Returns fraction of claims (in [0, 1]) containing at least one quantitative anchor.
    An empty/missing claims_summary scores 0.0 (penalized, not skipped).
    """
    claims = (paper.get("frontmatter") or {}).get("claims_summary") or []
    if not claims:
        return 0.0
    grounded = sum(1 for c in claims if _NUMERIC_ANCHOR_RE.search(c))
    return grounded / len(claims)
```

**What the function does & why.** For each one-line claim in the frontmatter it checks for the
presence of at least one recognizable quantitative or statistical anchor (a number, a CI, a
p-value, a named effect/ranking statistic), then reports the fraction of claims that clear that
bar. A paper whose "claims" are all qualitative assertions scores near zero; a paper reporting
precise, checkable effect sizes scores near one.

**Why it's hard to Goodhart.** You could stuff arbitrary numbers into a claim sentence to game the
regex ("X improves things by 42%"), but that number then becomes a checkable, falsifiable
assertion sitting in a public manifest — cheap gaming here is expensive elsewhere: it either has
to correspond to something in the evidence layer (checkable by a human/agent drilling in, which
this whole manifest exists to enable) or it's a fabrication that damages the paper's credibility if
caught. It doesn't reward *quantity* of numbers (only presence per claim), so padding a single
claim with many numbers doesn't help — you'd need every claim line to carry a distinct anchor.

---

## 4. Keyword Technical Specificity (Non-Genericity Index)

**How it signals good science.** Precise, technical, domain-specific keywords indicate a
compilation (and a paper) that has actually identified what is *distinctive* about the work —
the specific assay, model class, or method — rather than defaulting to generic disciplinary
labels that would apply to thousands of unrelated papers. Good science tends to be precisely
locatable in concept-space; keyword genericity is a cheap proxy for whether the paper (or its
compiled synthesis) actually did that locating work.

**Compute function.**

```python
_GENERIC_TERMS = {
    "study", "analysis", "research", "method", "methods", "approach", "results",
    "data", "review", "systematic review", "meta-analysis", "performance",
    "model", "evaluation", "framework", "investigation", "assessment",
}

def keyword_technical_specificity(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["keywords"] is list[str] (possibly empty/missing) and
    "title" is a string.
    Returns a score in [0, 1] combining: (a) generic-term penalty, (b) multi-word/technical-
    compound bonus, (c) a count-in-range check (5-10 items expected per the manifest spec).
    """
    fm = paper.get("frontmatter") or {}
    keywords = fm.get("keywords") or []
    title = (fm.get("title") or "").lower()

    if not keywords:
        return 0.0

    n = len(keywords)
    count_score = 1.0 if 5 <= n <= 10 else max(0.0, 1.0 - abs(n - 7) / 7)

    generic_hits = sum(1 for kw in keywords if kw.strip().lower() in _GENERIC_TERMS)
    generic_score = 1.0 - (generic_hits / n)

    # Reward multi-word technical compounds (proxy for named entities/methods, e.g.
    # "p-tau217/Abeta42 ratio") over single generic nouns; also penalize keywords that are
    # pure verbatim substrings of the title (copy-paste with zero added indexing value).
    multiword = sum(1 for kw in keywords if len(kw.split()) >= 2 or "/" in kw or "-" in kw)
    multiword_score = multiword / n

    title_copy = sum(1 for kw in keywords if kw.strip().lower() in title)
    copy_penalty = title_copy / n  # fraction that are pure lifts from the title

    specificity = (generic_score + multiword_score) / 2
    return max(0.0, count_score * 0.3 + specificity * 0.5 - copy_penalty * 0.2)
```

**What the function does & why.** It scores keyword *quality*, not just presence: penalizes
generic filler terms drawn from a fixed stoplist, rewards multi-word/technical-compound terms
(a cheap but decent proxy for named methods/entities), penalizes keywords that are just verbatim
lifts from the title (zero incremental indexing information), and checks the list length sits in
the manifest's own documented 5–10 range.

**Why it's hard to Goodhart.** Padding the keyword list with invented-sounding but meaningless
technical-looking compounds ("XYZ-ratio-framework") would raise the multiword score, but such
terms won't recur in `domain`, `abstract`, or `claims_summary` — a straightforward extension (not
required here, but a natural companion metric) would cross-check keyword/domain/abstract term
overlap. Even without that extension, purely generic keyword lists (the cheapest gaming strategy —
just list broad field names) are directly and heavily penalized by `generic_score`, so the "lazy"
gaming path is closed off, and a "spam many plausible technical terms" strategy interacts badly
with Metric 5 below (an abstract that never mentions the term you invented as a keyword reads as
disconnected synthesis).

---

## 5. Compilation Synthesis Value-Add

**How it signals good science.** A `claims_summary` that merely restates sentences already sitting
in the `abstract` verbatim indicates a paper (or a compilation pass over it) that hasn't done the
work of synthesis — extracting distinct, falsifiable claims with numbers is different work from
copying prose. Good science communication distills; it doesn't just quote itself. High verbatim
overlap between claims and abstract, especially combined with a short/generic abstract, is a
strong signal of a thin, paywalled-abstract-only source (explicitly flagged in the shape doc as a
case that must be penalized) being compiled without added value.

**Compute function.**

```python
import re

def _normalize(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def compilation_synthesis_value_add(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["abstract"] and ["claims_summary"] are strings/list[str]
    (possibly empty/missing/thin).
    Returns a score in [0, 1]: rewards claims that add information (numbers, named results)
    beyond a token-level match with the abstract; penalizes near-verbatim copies and thin
    abstracts equally (per the hard constraint, absence/thinness is penalized, not skipped).
    """
    fm = paper.get("frontmatter") or {}
    abstract = fm.get("abstract") or ""
    claims = fm.get("claims_summary") or []

    if not abstract or len(abstract.split()) < 50:
        return 0.0  # thin/paywalled-abstract-only source: penalized directly
    if not claims:
        return 0.0

    abstract_tokens = _normalize(abstract)
    novelty_scores = []
    for c in claims:
        claim_tokens = _normalize(c)
        if not claim_tokens:
            novelty_scores.append(0.0)
            continue
        overlap_ratio = len(claim_tokens & abstract_tokens) / len(claim_tokens)
        # A claim that is *entirely* a subset of abstract vocabulary (overlap_ratio ~1.0)
        # adds nothing; some overlap is expected and fine, total overlap is not.
        novelty_scores.append(1.0 - overlap_ratio)

    return sum(novelty_scores) / len(novelty_scores)
```

**What the function does & why.** It first gates on abstract richness (a thin/short abstract, the
signature of a paywalled or abstract-only source per the shape doc's availability notes, directly
zeroes the score rather than being excused). Then, for each claim line, it measures token-level
overlap with the abstract's vocabulary and scores the *complement* — claims that introduce
vocabulary (numbers, named metrics, comparators) not already in the abstract are treated as
evidence of real synthesis work; claims that are near-total subsets of abstract vocabulary are
treated as copy-paste and scored near zero.

**Why it's hard to Goodhart.** The cheap gaming move — paraphrase the abstract sentence with a
thesaurus swap to dodge token overlap while adding no real content — produces claims with novel
*words* but not novel *numbers*, which directly collides with Metric 3 (quantitative grounding):
a paraphrase without added statistics still fails to plant a numeric anchor, so it can raise
Metric 5 only at the cost of not raising Metric 3, unless the paraphrase happens to also add a real
effect size — at which point it's no longer gaming, it's actual synthesis.

---

## Combination

These five metrics are chosen so that the cheapest way to inflate any one of them actively damages
at least one other. Faking manifest arithmetic (Metric 1) requires the numbers to actually agree,
which constrains what you can pad elsewhere. Fabricating a DOI or registration mention (Metric 2)
to look verifiable doesn't manufacture real statistical content, so it leaves Metric 3 and 5 flat.
Padding keywords with generic or invented technical-sounding terms (Metric 4) is directly penalized
by the generic-term stoplist, and invented terms that never surface in the abstract or claims read
as disconnected from Metric 5's synthesis check. Paraphrasing claims to dodge the abstract-overlap
check (Metric 5) without adding real numbers fails to plant a quantitative anchor and so can't lift
Metric 3. In short: three of the five metrics (1, 3, 5) all require the *same* underlying good
behavior — actually-precise, actually-consistent, actually-original claim content — approached from
three different angles (internal arithmetic, statistical anchoring, and lexical novelty vs. the
abstract), so a paper can't cheaply satisfy the surface form of one without the substance that
the other two are independently checking for.
