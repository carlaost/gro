# Proposer 4 (revised) — Metrics for `PAPER.md` (root manifest)

## Changes from stage 1

The judge ranked this set #2 overall, crediting Metric 2 (pre-registration provenance) as the
single strongest "measures real science" metric in the tournament and the adversarial-combination
writeup as the field's most rigorous, but flagged four concrete defects. All four are fixed below:

1. **Metric 5 was a compute-soundness bug, not just a design weakness (top priority).** It scored
   `1.0 - overlap_ratio`, which *rewards* `claims_summary` lines whose vocabulary is disjoint from
   the abstract — i.e. it paid out highest on hallucination/drift, the opposite of what it claimed
   to measure. Rewritten from scratch below: reward now peaks at *moderate* abstract-overlap
   (grounded, not copied, not disconnected) and requires a quantitative anchor not already present
   in the abstract as a second, independent gate. Both near-total copy and near-total disjunction
   now score near zero, and pure paraphrase-with-no-new-number no longer clears the bar.
2. **Metric 2's registration reward was genre-biased.** A flat 0.4-of-1.0 weight on
   PROSPERO/OSF/ClinicalTrials.gov mentions caps a great theory/ML/dataset paper at 0.6 even though
   formal pre-registration isn't a norm for those genres. Renamed to *Identifier & Verifiability
   Provenance Rigor* and reworked: a lightweight genre detector (trial-like vs. general, from
   `domain`/`keywords`/`overview` text) now gates what counts. Trial-like genres are still held to
   the strict formal-registry bar; general genres get equal credit for any independently-checkable
   verifiability artifact (code/data repository, protocol, accession, dataset DOI) instead of being
   penalized for lacking a registry ID that was never applicable in the first place. The hard
   constraint is preserved — absence of *any* verifiability artifact, regardless of genre, still
   scores the sub-component 0.0, never N/A.
3. **Metric 4's `copy_penalty` punished honest keyword extraction.** Penalizing any keyword that
   is a verbatim substring of the title double-counts good behavior — technical terms (e.g.
   "p-tau217") legitimately recur in both title and keywords, and that overlap is a sign of
   accurate indexing, not laziness. The per-keyword title-substring penalty is dropped entirely.
   In its place is a much narrower, whole-list check that only fires on the actual degenerate case
   the penalty was meant to catch: a keyword *list* that, taken as a whole, contributes zero
   vocabulary beyond the title (i.e., the compiler literally split the title into keyword-shaped
   pieces and stopped). Legitimate overlap on individual terms no longer costs anything.
4. **Metric 1 used brittle exact-equality booleans.** A 7-vs-8 claim-count mismatch scored an
   identical hard 0 to a 7-vs-70 mismatch, throwing away the information in *how wrong* the
   manifest's self-reported arithmetic is. Checks A and B now return proportional partial credit
   (`1 - |a-b|/max(a,b,1)`) instead of a boolean equality test, so near-misses are distinguished
   from wildly-inconsistent manifests while still landing at 0.0 for total mismatch or missing data
   (Check C, a simple well-formedness sanity check, is left as a boolean per the judge's narrower
   critique, which targeted only A and B).

All five functions below still (a) assume a fully populated dict shape (paper/frontmatter/body
exactly as originally specified), (b) treat every missing/absent field as a penalty applied to the
score, never as a skipped/N/A check, and (c) never divide by a shrinking denominator to dodge a
missing-data case.

---

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

def _closeness(a: int, b: int) -> float:
    """Proportional partial credit: 1.0 on exact match, decaying with relative error.
    A 7-vs-8 mismatch is punished far less than a 7-vs-70 mismatch (stage-1 fix)."""
    if a == b:
        return 1.0
    denom = max(a, b, 1)
    return max(0.0, 1.0 - abs(a - b) / denom)

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

    checks = []  # each entry: a float in [0, 1] (partial credit), never skipped

    # --- Check A: claims_summary length vs. claims.md's self-reported count ---
    claims_summary = fm.get("claims_summary") or []
    cognitive = layer_index.get("cognitive") or []
    claims_desc = next((row.get("desc", "") for row in cognitive
                         if "claims.md" in row.get("file", "")), "")
    m = re.search(r"(\d+)\s+falsifiable claims", claims_desc)
    if not claims_summary or not claims_desc or not m:
        checks.append(0.0)  # missing data on either side is a penalty, not a skip
    else:
        checks.append(_closeness(int(m.group(1)), len(claims_summary)))

    # --- Check B: evidence README's stated "N tables + M figures" vs. actual row counts ---
    evidence = layer_index.get("evidence") or []
    readme_desc = next((row.get("desc", "") for row in evidence
                         if "README" in row.get("file", "")), "")
    m2 = re.search(r"(\d+)\s+tables?\s*\+\s*(\d+)\s+figures?", readme_desc)
    n_table_rows = sum(1 for row in evidence if "/tables/" in row.get("file", ""))
    n_figure_rows = sum(1 for row in evidence if "/figures/" in row.get("file", ""))
    if not evidence or not m2:
        checks.append(0.0)
    else:
        table_agree = _closeness(int(m2.group(1)), n_table_rows)
        figure_agree = _closeness(int(m2.group(2)), n_figure_rows)
        checks.append((table_agree + figure_agree) / 2)

    # --- Check C: trace layer states a node count at all (sanity: nonzero, well-formed) ---
    trace = layer_index.get("trace") or []
    trace_desc = trace[0].get("desc", "") if trace else ""
    m3 = re.search(r"(\d+)-node", trace_desc)
    checks.append(1.0 if (m3 and int(m3.group(1)) > 0) else 0.0)

    return sum(checks) / len(checks)
```

**What the function does & why.** It re-derives, from prose the compiler wrote about itself,
numbers that should agree with structural counts elsewhere in the same document, and scores the
degree of agreement rather than a brittle yes/no. A missing `claims_summary`, a missing
description, or an un-parseable description all count as a hard 0.0 on that check rather than
being excluded from the denominator, per the hard constraint — only *present-but-mismatched* data
gets the softer proportional treatment.

**Why it's hard to Goodhart.** Partial credit doesn't cheapen honesty: to score near 1.0 on
Checks A/B you still need the manifest's self-reported counts to actually match the structural
counts elsewhere — the closeness function only rewards being *close*, not being present. A
compiler/paper that fakes consistency by simply never stating counts in prose (to dodge the regex)
still fails outright (no match → 0.0, the worst possible outcome for that check, same as before).
The only route to a high score is to actually keep the numbers in near-lockstep everywhere; the
only change from stage 1 is that a small, honest discrepancy (e.g. an off-by-one from a
last-minute edit) is no longer scored identically to a wholesale numeric fabrication.

---

## 2. Identifier & Verifiability Provenance Rigor

**How it signals good science.** Verifiable identifiers (a real DOI, a real registration ID)
are the connective tissue that lets independent readers check a claim against its source. Public
pre-registration is one of the strongest known institutional defenses against p-hacking and
HARKing — but it is a genre-specific norm: expected for RCTs, systematic reviews, and clinical
protocols, not for theory papers, ML preprints, or dataset releases, which instead demonstrate
verifiability through released code, accessioned data, or a protocols.io method writeup. A
manifest that surfaces a well-formed DOI *and* the verifiability artifact appropriate to its own
genre is reporting on a paper that made itself checkable and pre-committed in the way its field
actually practices. A manifest with neither offers the reader nothing to verify against,
regardless of genre.

**Compute function.**

```python
import re

_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
_ARXIV_RE = re.compile(r"^(arXiv:)?\d{4}\.\d{4,5}(v\d+)?$", re.IGNORECASE)

# Formal trial/review pre-registration registries — the strict bar for trial-like genres.
_FORMAL_REGISTRY_RE = re.compile(
    r"\b(PROSPERO|clinicaltrials\.gov|ISRCTN|EudraCT)\b", re.IGNORECASE
)
# Broader verifiability artifacts — code/data/protocol accessions acceptable for general genres,
# and also credited (at reduced weight) for trial-like genres in lieu of formal registration.
_VERIFIABILITY_RE = re.compile(
    r"\b(PROSPERO|clinicaltrials\.gov|ISRCTN|EudraCT|OSF\.io|protocols\.io|"
    r"github\.com|gitlab\.com|zenodo|dryad|huggingface\.co|GEO\s?accession|"
    r"dataset DOI|data (?:repository|availability))\b", re.IGNORECASE
)
_TRIAL_GENRE_RE = re.compile(
    r"\b(randomi[sz]ed|RCT|systematic review|meta-analysis|clinical trial|"
    r"cohort study protocol|network meta-analysis)\b", re.IGNORECASE
)

def _detect_trial_like_genre(paper: dict) -> bool:
    fm = paper.get("frontmatter") or {}
    body = paper.get("body") or {}
    text = " ".join([
        fm.get("domain") or "",
        " ".join(fm.get("keywords") or []),
        body.get("overview") or "",
    ])
    return bool(_TRIAL_GENRE_RE.search(text))

def identifier_provenance_rigor(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["doi"] is a string (real id, arXiv id, or the literal
    "Not specified in paper"). Assumes: paper["body"]["overview"] and the physical-layer
    descriptions are prose text (possibly missing/empty).
    Returns a score in [0, 1]: 0.6 weight on identifier validity, 0.4 on genre-appropriate
    verifiability provenance.
    """
    fm = paper.get("frontmatter") or {}
    body = paper.get("body") or {}
    layer_index = body.get("layer_index") or {}

    doi = (fm.get("doi") or "").strip()
    if not doi or doi.lower() == "not specified in paper":
        id_score = 0.0
    elif _DOI_RE.match(doi) or _ARXIV_RE.match(doi):
        id_score = 1.0
    else:
        id_score = 0.2  # present but malformed/unverifiable string — better than nothing, barely

    overview = body.get("overview") or ""
    physical = layer_index.get("physical") or []
    physical_text = " ".join(row.get("desc", "") for row in physical)
    search_text = overview + " " + physical_text

    is_trial_like = _detect_trial_like_genre(paper)
    if is_trial_like:
        # Trial-like genres are held to the strict bar: formal registration in full, any other
        # verifiability artifact only partially substitutes (it doesn't carry the same
        # pre-commitment guarantee against post-hoc outcome switching).
        if _FORMAL_REGISTRY_RE.search(search_text):
            prov_score = 1.0
        elif _VERIFIABILITY_RE.search(search_text):
            prov_score = 0.5
        else:
            prov_score = 0.0
    else:
        # General genres: no formal-registry norm exists, so any independently-checkable
        # verifiability artifact (code repo, data accession, protocol) earns full credit.
        prov_score = 1.0 if _VERIFIABILITY_RE.search(search_text) else 0.0

    return 0.6 * id_score + 0.4 * prov_score
```

**What the function does & why.** It regex-validates the DOI/arXiv field against real identifier
grammars so a garbage placeholder can't pass as a valid id, exactly as before. The provenance half
now first classifies genre from `domain`/`keywords`/`overview` text, then applies a genre-matched
bar: trial-like papers still need to clear the strict formal-registry check for full credit (with
a discounted partial credit for a code/data artifact alone, since that isn't the same institutional
guarantee), while general-genre papers get full credit from any real verifiability artifact. Total
absence of both an identifier and a provenance artifact still scores 0.0 on both halves — the hard
constraint that missing inputs are penalized, not excused, is unchanged.

**Why it's hard to Goodhart.** Fabricating a DOI that matches the regex risks it being a
plausible-looking but non-resolving identifier — this metric alone can't catch that, but it's
cross-checked against Metric 1's consistency framing and Metric 5's overlap/anchor check below: a
paper that fabricates identifiers to inflate this score while thin everywhere else will still
read as quantitatively empty on Metric 3 and unable to produce a grounded-yet-novel claim on
Metric 5, since inventing a fake DOI does nothing to manufacture real statistical content
elsewhere. The genre gate itself is hard to game in the cheap direction: claiming a trial-like
genre in `domain`/`keywords` when the paper isn't one doesn't help (it just raises the bar you're
held to, since formal registration is now expected), and claiming a general genre to dodge the
strict bar when the overview text is otherwise saturated with RCT/meta-analysis language will
simply trip `_TRIAL_GENRE_RE` regardless of what the compiler intended.

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
precise, checkable effect sizes scores near one. (Unchanged from stage 1 — the judge flagged no
defect in this metric.)

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
compiled synthesis) actually did that locating work. Note that a keyword *legitimately* echoing a
technical term from the title (e.g., a title mentioning "p-tau217" and a keyword listing it too)
is accurate indexing, not laziness — only a keyword *list* that as a whole adds nothing beyond the
title's own vocabulary is a real genericity failure.

**Compute function.**

```python
import re

_GENERIC_TERMS = {
    "study", "analysis", "research", "method", "methods", "approach", "results",
    "data", "review", "systematic review", "meta-analysis", "performance",
    "model", "evaluation", "framework", "investigation", "assessment",
}

def _normalize(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def keyword_technical_specificity(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["keywords"] is list[str] (possibly empty/missing) and
    "title" is a string.
    Returns a score in [0, 1] combining: (a) generic-term penalty, (b) multi-word/technical-
    compound bonus, (c) a count-in-range check (5-10 items expected per the manifest spec),
    (d) a whole-list novelty gate against the title.
    """
    fm = paper.get("frontmatter") or {}
    keywords = fm.get("keywords") or []
    title = fm.get("title") or ""

    if not keywords:
        return 0.0

    n = len(keywords)
    count_score = 1.0 if 5 <= n <= 10 else max(0.0, 1.0 - abs(n - 7) / 7)

    generic_hits = sum(1 for kw in keywords if kw.strip().lower() in _GENERIC_TERMS)
    generic_score = 1.0 - (generic_hits / n)

    # Reward multi-word technical compounds (proxy for named entities/methods, e.g.
    # "p-tau217/Abeta42 ratio") over single generic nouns.
    multiword = sum(1 for kw in keywords if len(kw.split()) >= 2 or "/" in kw or "-" in kw)
    multiword_score = multiword / n

    # Whole-list novelty gate (replaces the old per-keyword title-substring penalty, which
    # punished honest technical-term overlap with the title). This only fires on the actual
    # degenerate case: the keyword list, taken together, contributes zero vocabulary the title
    # didn't already have — i.e. the compiler just chopped the title into keyword-shaped pieces.
    # A keyword list that individually echoes several title terms but also introduces even one
    # new technical word (a method name, a comparator, a statistic) is not penalized at all.
    title_tokens = _normalize(title)
    keyword_tokens = set()
    for kw in keywords:
        keyword_tokens |= _normalize(kw)
    new_vocab = keyword_tokens - title_tokens
    novelty_score = 1.0 if new_vocab else 0.0

    specificity = (generic_score + multiword_score + novelty_score) / 3
    return max(0.0, count_score * 0.3 + specificity * 0.7)
```

**What the function does & why.** It scores keyword *quality*, not just presence: penalizes
generic filler terms drawn from a fixed stoplist, rewards multi-word/technical-compound terms
(a cheap but decent proxy for named methods/entities), checks the list length sits in the
manifest's own documented 5–10 range, and — replacing the old individual-keyword copy penalty —
gates on whether the keyword list *as a whole* introduces any vocabulary beyond the title. This
targets the actual failure mode (a keyword list that is nothing but the title's own words) without
punishing the common, correct case of a keyword restating a technical term that also appears in
the title.

**Why it's hard to Goodhart.** Padding the keyword list with invented-sounding but meaningless
technical-looking compounds ("XYZ-ratio-framework") would raise the multiword score and trivially
clear the novelty gate (any invented word is "new" relative to the title), but such terms won't
recur in `domain`, `abstract`, or `claims_summary` — a paper doing this reads as disconnected
synthesis on Metric 5 (the grounding half of that metric requires overlap with the abstract
somewhere, and invented keyword vocabulary appearing nowhere else in the manifest doesn't buy
anything there). Purely generic keyword lists (the cheapest gaming strategy — just list broad
field names) are still directly and heavily penalized by `generic_score`, and a list that is
literally the title's words rearranged now fails the novelty gate outright rather than being
scored based on brittle substring penalties that could be dodged with synonym swaps.

---

## 5. Compilation Synthesis Value-Add

**How it signals good science.** A `claims_summary` that merely restates sentences already sitting
in the `abstract` verbatim indicates a paper (or a compilation pass over it) that hasn't done the
work of synthesis — extracting distinct, falsifiable claims with numbers is different work from
copying prose. But a claim that shares *no* vocabulary with the paper's own abstract is equally
suspect in the opposite direction: it is either drift (the compiler inventing content not actually
in the source) or scope creep unmoored from what the paper claims to be about. Good synthesis sits
in between — grounded in the paper's own stated contribution, but adding something the abstract
didn't already spell out (an effect size, a named comparator, a specific statistic). High verbatim
overlap between claims and abstract, especially combined with a short/generic abstract, is a
strong signal of a thin, paywalled-abstract-only source (explicitly flagged in the shape doc as a
case that must be penalized) being compiled without added value; near-zero overlap is a signal of
fabrication or unmoored drift, which is no better.

**Compute function.**

```python
import re

_NUMERIC_ANCHOR_RE = re.compile(
    r"\d+(\.\d+)?%?|\bCI\b|\bp\s*[<=]\s*0?\.\d+|\bI2\b|\bI\^2\b|"
    r"\bAUC\b|\bOR\b|\bHR\b|\bSUCRA\b|P-score", re.IGNORECASE
)

def _normalize(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def _numeric_anchors(s: str) -> set:
    return {m.group(0).lower() for m in _NUMERIC_ANCHOR_RE.finditer(s)}

def compilation_synthesis_value_add(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["abstract"] and ["claims_summary"] are strings/list[str]
    (possibly empty/missing/thin).
    Returns a score in [0, 1]. Fixed from stage 1, which scored 1.0 - overlap_ratio and thereby
    rewarded claims that were maximally DISJOINT from the abstract (a compute-soundness bug that
    directly rewarded hallucination/drift). Now: each claim is scored on two independent axes —
    (a) a grounding-shape score that peaks at MODERATE lexical overlap with the abstract and
    drops toward 0 at both extremes (pure copy and pure disjunction), and (b) whether the claim
    carries a quantitative anchor not already present in the abstract (real added precision, not
    just added or swapped words). A thin/missing abstract or claims_summary is penalized (0.0),
    never skipped, per the hard constraint.
    """
    fm = paper.get("frontmatter") or {}
    abstract = fm.get("abstract") or ""
    claims = fm.get("claims_summary") or []

    if not abstract or len(abstract.split()) < 50:
        return 0.0  # thin/paywalled-abstract-only source: penalized directly
    if not claims:
        return 0.0

    abstract_tokens = _normalize(abstract)
    abstract_anchors = _numeric_anchors(abstract)

    per_claim_scores = []
    for c in claims:
        claim_tokens = _normalize(c)
        if not claim_tokens:
            per_claim_scores.append(0.0)
            continue

        overlap_ratio = len(claim_tokens & abstract_tokens) / len(claim_tokens)
        # Triangular shape: 1.0 at overlap_ratio == 0.5 (grounded but not copied), decaying to
        # 0.0 at both overlap_ratio == 0 (disjoint/drift) and overlap_ratio == 1 (verbatim copy).
        grounding_shape = max(0.0, 1.0 - abs(overlap_ratio - 0.5) * 2)

        claim_anchors = _numeric_anchors(c)
        novel_anchors = claim_anchors - abstract_anchors
        anchor_bonus = 1.0 if novel_anchors else 0.0

        per_claim_scores.append(0.5 * grounding_shape + 0.5 * anchor_bonus)

    return sum(per_claim_scores) / len(per_claim_scores)
```

**What the function does & why.** It first gates on abstract richness (a thin/short abstract, the
signature of a paywalled or abstract-only source per the shape doc's availability notes, directly
zeroes the score rather than being excused). Then, for each claim line, it scores two things
independently: whether the claim sits in the "grounded but not copied" middle band of lexical
overlap with the abstract (this is the direct fix for the stage-1 bug — disjoint claims and
verbatim claims now both score the *shape* component near zero, instead of disjoint claims scoring
highest), and whether the claim introduces a quantitative anchor (a number, CI, named statistic)
that isn't already present anywhere in the abstract — real added precision, distinguishable from a
thesaurus-swapped paraphrase of an abstract sentence that happens to dodge the token-overlap check.

**Why it's hard to Goodhart.** The stage-1 gaming path — paraphrase to reduce token overlap while
adding no real content — is now closed on both axes at once: paraphrasing toward *less* overlap
without adding a new number pushes the claim toward the disjoint end of the triangular shape
(lowering, not raising, the grounding component) and still fails the anchor_bonus check, so it
can't score well. Paraphrasing toward *more* overlap (copying more of the abstract's wording)
symmetrically fails the shape score from the other side. The only way to score well on a given
claim is to sit near moderate, genuine grounding *and* supply a number/statistic the abstract
didn't already state — which is exactly claim-extraction synthesis, not gaming. This also now
composes correctly with Metric 3: a claim that clears the anchor_bonus here necessarily contains a
numeric anchor, so a paper can't score well on Metric 5 while scoring zero on Metric 3 (the
converse — numbers present but all also present verbatim in the abstract, i.e. copied statistics —
still fails anchor_bonus here even though it would pass Metric 3, correctly distinguishing "has
numbers" from "added numbers beyond the abstract").

---

## Combination

These five metrics are chosen so that the cheapest way to inflate any one of them actively damages
at least one other, and stage-2's fixes tighten several of those couplings further. Faking manifest
arithmetic (Metric 1) still requires the numbers to actually agree closely (now proportionally, not
just exactly) to score well, which constrains what you can pad elsewhere. Fabricating a DOI or a
verifiability artifact (Metric 2) to look checkable doesn't manufacture real statistical content, so
it leaves Metric 3 and the anchor half of Metric 5 flat; and the genre gate closes off the cheap move
of mislabeling genre to dodge the strict bar, since the trial-genre detector runs on the same
overview/domain text the compiler already wrote. Padding keywords with generic or invented
technical-sounding terms (Metric 4) is still directly penalized by the generic-term stoplist, and
invented terms that never surface in the abstract or claims read as disconnected from Metric 5's
grounding-shape score (which requires overlap with the *paper's own* vocabulary, not just any
technical-looking string). Paraphrasing claims to dodge the abstract-overlap check (Metric 5) no
longer works at all now that both copy *and* disjunction are penalized, and gaming it further
requires an actual novel quantitative anchor, which is precisely what Metric 3 also independently
rewards. In short: three of the five metrics (1, 3, 5) all require the *same* underlying good
behavior — actually-precise, actually-consistent, actually-original claim content — approached from
three different angles (internal arithmetic, statistical anchoring, and grounded-but-novel synthesis
against the abstract), and Metric 2's genre-aware provenance check and Metric 4's whole-list novelty
gate now each close off a specific cheap escape hatch (genre-mislabeling, title-echo penalties) that
stage 1 either left open or over-punished.
