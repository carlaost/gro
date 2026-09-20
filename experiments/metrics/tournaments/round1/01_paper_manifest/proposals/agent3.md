# Proposer #3 — metrics for `PAPER.md` (root manifest)

Assumed parsed representation for all functions below:

```python
parsed = {
    "frontmatter": {
        "title": str, "authors": list[str], "year": int, "venue": str,
        "doi": str, "ara_version": str, "domain": str,
        "keywords": list[str], "claims_summary": list[str], "abstract": str,
    },
    "body": {
        "overview": str,
        # layer name -> list of (file_path, description) row tuples, as rendered in the Layer Index
        "layer_index": dict[str, list[tuple[str, str]]],
    },
}
```

---

## 1. Claim-Count Self-Consistency

**How it signals good science.** The compiler is supposed to derive `claims_summary` directly
from `logic/claims.md`. If the frontmatter count of claims and the count the Layer Index *itself*
advertises for `claims.md` (e.g. "8 falsifiable claims (C01-C08)") disagree, either the compiler
truncated/hallucinated claims or the manifest is stale — in both cases the manifest is no longer a
trustworthy Level-1 view of the paper's actual claim structure. Agreement is a cheap but real
signal that the entry point hasn't drifted from the underlying cognitive layer.

**Compute function.**

```python
import re

def claim_count_consistency(parsed: dict) -> float:
    # Assumes: frontmatter.claims_summary is a list; body.layer_index["Cognitive Layer"]
    # contains a row for a file named "claims.md" whose description states a count,
    # e.g. "8 falsifiable claims (C01-C08)" or "7 claims".
    claims_summary = parsed.get("frontmatter", {}).get("claims_summary") or []
    n_summary = len(claims_summary)
    if n_summary == 0:
        return 0.0  # thin/absent claims_summary is itself penalized

    cog_rows = parsed.get("body", {}).get("layer_index", {}).get("Cognitive Layer", [])
    claims_desc = None
    for path, desc in cog_rows:
        if path.strip().lower().endswith("claims.md"):
            claims_desc = desc
            break
    if claims_desc is None:
        return 0.0  # no claims.md entry at all -> cannot corroborate -> penalize

    m = re.search(r"(\d+)\s*(?:falsifiable\s*)?claims?", claims_desc, re.IGNORECASE)
    if not m:
        return 0.2  # row exists but doesn't state a count -> weakly penalize, can't verify
    n_claimed = int(m.group(1))

    diff = abs(n_claimed - n_summary)
    if diff == 0:
        return 1.0
    denom = max(n_claimed, n_summary, 1)
    return max(0.0, 1.0 - diff / denom)
```

**What the function does & why.** It pulls the integer count out of the Layer Index's own prose
description of `claims.md` and diffs it against `len(claims_summary)`. Exact match scores 1.0;
any mismatch is penalized proportionally to how far off it is relative to the larger of the two
counts, so a 1-claim discrepancy on an 8-claim paper barely dents the score while a 7-vs-1
discrepancy craters it. Missing `claims_summary` or a missing/uncountable `claims.md` row scores
at or near zero rather than being skipped.

**Why it's hard to Goodhart.** You cannot inflate this by padding `claims_summary` with junk
lines, because the count has to match a *second, independently-worded* piece of text (the Layer
Index description) that the compiler generated separately. To game both, you'd need to
consistently corrupt two different generation passes in the same direction — that's strictly
harder than gaming either field alone, and it also collides with Metric 2 below (junk claim lines
tend to be non-quantitative, dragging that score down too).

---

## 2. Quantitative Evidentiary Density of Claims

**How it signals good science.** Good empirical claims are falsifiable and specific — they carry
effect sizes, confidence intervals, p-values, ratios, or sample sizes, not just qualitative
assertions ("X is important for Y"). A `claims_summary` dense with concrete quantitative content
reflects a source paper (and a faithful compilation of it) that actually reports measurable
results rather than narrative hand-waving.

**Compute function.**

```python
import re

_QUANT_PATTERNS = [
    r"\b\d+(\.\d+)?\s*%",                       # percentages
    r"\bp\s*[<=>]\s*0?\.\d+",                    # p-values
    r"95%\s*CI",                                  # confidence intervals
    r"\b(n|N)\s*=\s*\d+",                         # sample sizes
    r"\b\d+(\.\d+)?\b",                           # bare numbers (AUC, OR, HR, I2, etc.)
]
_QUANT_RE = re.compile("|".join(_QUANT_PATTERNS))

def quantitative_claim_density(parsed: dict) -> float:
    # Assumes: frontmatter.claims_summary is a list[str] of one-line claim statements.
    claims = parsed.get("frontmatter", {}).get("claims_summary") or []
    if not claims:
        return 0.0
    hits = sum(1 for c in claims if _QUANT_RE.search(c))
    return hits / len(claims)
```

**What the function does & why.** For each claim line, it checks for at least one quantitative
marker (percentage, p-value, CI, sample size, or a bare number standing in for an effect size /
statistic). The score is simply the fraction of claims that clear this bar — a paper whose claims
are all backed by numbers scores 1.0; a paper reduced to vague prose scores toward 0. Empty
`claims_summary` is explicitly zeroed rather than skipped.

**Why it's hard to Goodhart.** Sprinkling numbers into fabricated claims to farm this score is
cheap in isolation, but it directly increases exposure on Metric 5 (abstract-grounding): fabricated
statistics that don't appear anywhere in the verbatim `abstract` field lower that score. It also
doesn't help Metric 1, since claim *count* consistency is orthogonal to claim *content*. Gaming
this metric alone buys nothing without also fabricating a consistent abstract.

---

## 3. Layer-Index Structural Completeness & Substance

**How it signals good science.** The Layer Index is the manifest's index of everything the
compiler actually produced. A paper whose compilation surfaces a cognitive layer, a physical/
implementation layer, an exploration graph, *and* an evidence index reflects a work substantial
enough to yield real methodology, artifacts, a decision trail, and empirical support — not just an
abstract restated in YAML. Sparse or filler-only sections are a direct proxy for a thin underlying
paper or a lazy compilation.

**Compute function.**

```python
_CORE_LAYERS = ["Cognitive Layer", "Physical Layer", "Exploration Graph", "Evidence"]
_FILLER = {"", "tbd", "n/a", "none", "not available", "no description"}

def layer_index_completeness(parsed: dict) -> float:
    # Assumes: body.layer_index maps layer-name -> list[(file, description)] rows,
    # only for layers actually rendered in PAPER.md (per the shape doc, layers with
    # no files are simply omitted).
    layer_index = parsed.get("body", {}).get("layer_index") or {}

    def substantive_rows(layer_name: str) -> int:
        rows = layer_index.get(layer_name, [])
        return sum(
            1 for _, desc in rows
            if desc and desc.strip().lower() not in _FILLER and len(desc.strip()) >= 10
        )

    scores = []
    for layer in _CORE_LAYERS:
        present_rows = substantive_rows(layer)
        # each core layer contributes up to 1.0: 0 if absent/filler-only,
        # partial credit scaling up to 1 row, full credit at 2+ substantive rows
        scores.append(min(present_rows / 2.0, 1.0))
    return sum(scores) / len(_CORE_LAYERS)
```

**What the function does & why.** It walks the four layers that a genuine research compilation
should almost always be able to populate (cognitive reasoning, implementation/physical artifacts,
an exploration trace, and evidence), counts rows per layer that have real (non-filler, non-trivial)
descriptions, and averages a per-layer completeness score across all four. A manifest with rich,
descriptive rows in every core layer scores near 1.0; one that's missing sections or fills them
with placeholder text collapses toward 0 — exactly per the hard constraint, absence is penalized,
not skipped. (Data Layer is deliberately excluded from the *core* set since the shape doc says it's
legitimately absent for many genres — but see Metric 4, which catches ungrounded compensations.)

**Why it's hard to Goodhart.** Padding the Layer Index with extra rows of generic text ("various
findings discussed") is caught by the length/filler filter, which requires >=10 non-filler
characters per row — cheap padding reads as filler. Manufacturing genuinely substantive-looking
fake rows (e.g., inventing an evidence table that doesn't exist) inflates this score but has to
survive Metric 1's cross-check logic in spirit: any layer padding that isn't backed by a real file
elsewhere in the ARA is a structural claim with nothing behind it, and the same generation process
that would fabricate evidence rows tends to also destabilize the claims-count text checked in
Metric 1.

---

## 4. Bibliographic & Identifier Integrity

**How it signals good science.** A manifest's core job is accurate bibliographic identity. Good
science compilation means faithfully recording what's actually citable — a real DOI/arXiv id or an
honest "Not specified in paper" — rather than a plausible-looking placeholder. Fabricated-looking
identifiers, missing authors, or implausible years are a direct signal of either a broken source
paper or a compiler that guessed rather than extracted.

**Compute function.**

```python
import re
import datetime

_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
_ARXIV_RE = re.compile(r"^(arXiv:)?\d{4}\.\d{4,5}(v\d+)?$", re.IGNORECASE)
_PLACEHOLDER_AUTHORS = {"unknown", "author", "n/a", "anonymous", "et al."}

def bibliographic_integrity(parsed: dict) -> float:
    # Assumes: frontmatter has title, authors (list[str]), year (int-like), venue, doi (str).
    fm = parsed.get("frontmatter", {})
    checks = []

    title = (fm.get("title") or "").strip()
    checks.append(1.0 if len(title) >= 10 else 0.0)

    authors = fm.get("authors") or []
    valid_authors = [
        a for a in authors
        if a and a.strip().lower() not in _PLACEHOLDER_AUTHORS and len(a.strip()) >= 2
    ]
    checks.append(1.0 if len(valid_authors) >= 1 and len(valid_authors) == len(authors) else
                  (0.3 if valid_authors else 0.0))

    year = fm.get("year")
    current_year = datetime.datetime.now().year
    try:
        year_int = int(year)
        checks.append(1.0 if 1900 <= year_int <= current_year + 1 else 0.0)
    except (TypeError, ValueError):
        checks.append(0.0)

    venue = (fm.get("venue") or "").strip()
    checks.append(1.0 if len(venue) >= 3 else 0.0)

    doi = (fm.get("doi") or "").strip()
    if doi == "Not specified in paper":
        checks.append(0.6)  # honest absence: acceptable but not as strong as a real id
    elif _DOI_RE.match(doi) or _ARXIV_RE.match(doi):
        checks.append(1.0)
    else:
        checks.append(0.0)  # looks fabricated / malformed / vague placeholder

    return sum(checks) / len(checks)
```

**What the function does & why.** Five independent sanity checks — title length, author-list
sanity (no placeholders, no silently-dropped authors), plausible publication year, a real venue
string, and a properly-formatted (or honestly absent) identifier — are averaged into one score.
Each sub-check is binary-ish and penalizes missing or implausible data rather than ignoring it; the
DOI check specifically rewards the honest "Not specified in paper" convention over a value that
merely *looks* like a DOI but fails the regex (a strong fabrication tell).

**Why it's hard to Goodhart.** The DOI regex plus the explicit carve-out for the honest
"Not specified in paper" string closes the cheapest exploit (writing "N/A" or "unknown" to dodge
work) by scoring it at 0, not partial credit — so gaming this metric requires either a *real*
well-formed identifier (which is verifiable against external registries downstream, out of scope
here but a deterrent) or the honest-absence string, both of which are legitimate outcomes. Faking
a plausible year/venue/author list is possible but does nothing to help any of the other four
metrics, so it's pure, isolated effort with no compounding payoff.

---

## 5. Abstract-Grounding of Domain & Keywords

**How it signals good science.** `domain` and `keywords` are supposed to be *derived from* the
paper's actual content (title + abstract, per the shape doc's own note: "domain/keywords still
populate from title+abstract"). If the keyword list and domain string share essentially no
vocabulary with the verbatim abstract, they were likely generated generically (or hallucinated)
rather than extracted — a Level-1 view that isn't actually anchored to the paper it claims to
summarize is worse than useless, since agents trust it to triage relevance.

**Compute function.**

```python
import re

_STOPWORDS = {"the", "a", "an", "of", "and", "or", "in", "for", "to", "with", "on", "is", "are"}

def _tokenize(text: str) -> set[str]:
    return {
        w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
        if w not in _STOPWORDS
    }

def abstract_grounding(parsed: dict) -> float:
    # Assumes: frontmatter has abstract (str, possibly empty/thin), domain (str),
    # keywords (list[str]), title (str) as fallback context.
    fm = parsed.get("frontmatter", {})
    abstract = fm.get("abstract") or ""
    title = fm.get("title") or ""
    domain = fm.get("domain") or ""
    keywords = fm.get("keywords") or []

    if len(abstract.strip()) < 50:
        return 0.0  # thin/absent abstract: nothing to ground against, and the shape
                     # doc flags this itself as a penalizable degraded case

    grounding_pool = _tokenize(abstract) | _tokenize(title)

    if not keywords:
        return 0.0

    grounded = 0
    for kw in keywords:
        kw_tokens = _tokenize(kw)
        if kw_tokens and (kw_tokens & grounding_pool):
            grounded += 1
    keyword_score = grounded / len(keywords)

    domain_tokens = _tokenize(domain)
    domain_score = (
        len(domain_tokens & grounding_pool) / len(domain_tokens)
        if domain_tokens else 0.0
    )

    return 0.7 * keyword_score + 0.3 * domain_score
```

**What the function does & why.** It tokenizes the abstract and title into a "grounding pool" of
real content words, then checks what fraction of `keywords` share at least one significant word
with that pool, and separately what fraction of the `domain` string's words are grounded the same
way. The two are weighted (keywords matter more since there are more of them to check) into one
score. A thin/missing abstract — the shape doc's own named degraded case — is hard-zeroed rather
than letting keywords/domain float free of any anchor.

**Why it's hard to Goodhart.** The obvious exploit — copy-pasting abstract words verbatim as
keywords — actually *improves* the ARA (keywords that are genuinely descriptive of the abstract
are a legitimate outcome, not degenerate), so there's no free lunch there. The other exploit —
writing a generic-but-abstract-consistent domain/keyword set — is constrained by needing real
overlap with a *specific* paper's abstract vocabulary, which is much harder to fake generically
across many different ARAs than it is to fake once. It also can't be gamed by padding the abstract
field with keyword soup, since Metric 4's title-length and general bibliographic checks are
separate, and an abstract stuffed with keywords rather than prose reads as a different kind of
defect that downstream Seal-Level review would likely flag independently.

---

## Combination

These five metrics are jointly hard to game because they pull on different, partly-opposed levers
of the same manifest. Inflating `claims_summary` with more (or more numeric-sounding) lines to
win Metric 2 breaks the count parity checked by Metric 1 unless the `claims.md` description is
*also* rewritten to match — and any invented statistics that aren't traceable to the real
`abstract` text get punished by Metric 5's grounding check. Padding the Layer Index with fake
substantive-looking rows to win Metric 3 produces structural claims (more evidence, more
implementation) that have no correlate in the bibliographic/abstract fields Metrics 4–5 examine,
and a compiler sloppy enough to fabricate Layer Index rows is also likely to drift on the
claims.md count checked by Metric 1. Faking a clean-looking DOI or author list to win Metric 4
does nothing to help the other four, since none of them read those fields — it's isolated,
non-compounding effort. In short: content-fabrication metrics (2, 5) check each other via the
shared abstract; structural-fabrication metrics (1, 3) check each other via the shared
claims/layer counts; and identity-fabrication (4) is deliberately walled off so it can't be
"bought" cheaply alongside the others. A paper can't win all five by fabricating one consistent
story — the fabrication has to be consistent across independently-sourced parts of the same
document, which is strictly more expensive than faithfully compiling the real paper.
