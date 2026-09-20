# Proposer #1 — Metrics for `PAPER.md` root manifest

Assumed parsed representation for all functions below (a `paper` dict):

```python
paper = {
    "frontmatter": {
        "title": str, "authors": [str, ...], "year": int, "venue": str, "doi": str,
        "ara_version": str, "domain": str, "keywords": [str, ...],
        "claims_summary": [str, ...], "abstract": str,
    },
    "body": {
        "h1": str,          # the "# {Paper Title}" heading text
        "overview": str,    # prose under "## Overview"
        "layer_index": {
            "cognitive": [{"file": str, "description": str}, ...] | None,
            "physical":  [{"file": str, "description": str}, ...] | None,
            "data":      [{"file": str, "description": str}, ...] | None,
            "trace":     [{"file": str, "description": str}, ...] | None,
            "evidence":  [{"file": str, "description": str}, ...] | None,
        },
    },
}
```

---

## 1. Frontmatter–Layer-Index Self-Consistency

**How it signals good science.** A manifest that was actually derived faithfully from the deeper
ARA layers will agree with itself: the number of claims promised in `claims_summary` will match the
count of claims the Cognitive Layer says it compiled, the evidence counts stated in the Evidence
Layer's description will match how many table/figure rows are actually indexed, and the H1 will
match the frontmatter title. Internal agreement across independently-generated parts of the same
document is evidence the compiler did real extraction rather than free-associating a summary. This
mirrors exactly the kind of self-consistency check that a real Level-1 validation pass should run.

**Compute function.**

```python
import re

def metric_self_consistency(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is a list (possibly empty/missing);
    paper["body"]["layer_index"] entries are lists of {"file","description"} dicts or None
    when the layer is absent; paper["body"]["h1"] and frontmatter["title"] are strings
    (possibly empty/missing).
    """
    fm = paper.get("frontmatter", {}) or {}
    li = (paper.get("body", {}) or {}).get("layer_index", {}) or {}
    checks = []

    # Check A: claims_summary length vs. count stated in cognitive/claims.md description
    claims_summary = fm.get("claims_summary") or []
    cognitive = li.get("cognitive") or []
    claims_row = next((r for r in cognitive if "claims.md" in (r.get("file") or "")), None)
    if claims_row is None:
        checks.append(0.0)
    else:
        desc = claims_row.get("description", "") or ""
        stated = None
        m = re.search(r'\(C(\d+)-C(\d+)\)', desc)
        if m:
            stated = int(m.group(2)) - int(m.group(1)) + 1
        else:
            m2 = re.search(r'(\d+)\s+falsifiable claims', desc, re.I)
            if m2:
                stated = int(m2.group(1))
        if stated is None or stated == 0:
            checks.append(0.0)
        else:
            diff = abs(stated - len(claims_summary))
            checks.append(max(0.0, 1.0 - diff / stated))

    # Check B: evidence counts stated in evidence/README.md description vs. actual row count
    evidence = li.get("evidence") or []
    if not evidence:
        checks.append(0.0)
    else:
        readme = next((r for r in evidence if "README" in (r.get("file") or "")), None)
        if readme is None:
            checks.append(0.0)
        else:
            desc = readme.get("description", "") or ""
            m = re.search(r'(\d+)\s+tables?\s*\+\s*(\d+)\s+figures?', desc, re.I)
            if not m:
                checks.append(0.0)
            else:
                stated_total = int(m.group(1)) + int(m.group(2))
                actual_total = len(evidence) - 1  # exclude README itself
                diff = abs(stated_total - actual_total)
                checks.append(max(0.0, 1.0 - diff / max(stated_total, 1)))

    # Check C: H1 heading matches frontmatter title verbatim
    h1 = (paper.get("body", {}) or {}).get("h1", "") or ""
    title = fm.get("title", "") or ""
    checks.append(1.0 if h1.strip() and title.strip() and h1.strip() == title.strip() else 0.0)

    return sum(checks) / len(checks) if checks else 0.0
```

**What the function does & why.** It runs three independent cross-checks that all live inside the
single manifest file: (A) does the promised claim count in the frontmatter list match the count the
Cognitive Layer's own description advertises; (B) does the Evidence Layer's stated table/figure
count match how many rows are actually listed under it; (C) does the H1 heading literally match the
`title` field. Each check is scored 0–1 and averaged. Any missing row, missing layer, or unparsable
description contributes a hard zero for that check — there is no "skip."

**Why it's hard to Goodhart.** You cannot inflate `claims_summary` for a padding-driven metric (like
metric 2 below) without also breaking this metric's count-agreement check, because the two are
adversarially coupled by construction — the compiler would have to fabricate a *matching* fake count
in the Cognitive Layer description too, which is a second, independently-checkable lie.

---

## 2. Claim Quantitative Density

**How it signals good science.** Good empirical science states claims that are falsifiable — bound
to a number, an effect size, a confidence interval, a sample size — not hand-wavy assertions. A
manifest whose `claims_summary` lines are dense with quantitative, checkable content (e.g. "AUC gain
of 0.025, 95% CI 0.005–0.045") is doing real epistemic work up front; one whose lines are vague prose
("the treatment appears promising") is deferring all rigor to layers the reader may never open. Since
`claims_summary` is the *only* thing a Level-1, budget-constrained agent reads, its quantitative
density is a direct proxy for whether that agent gets real signal or empty assurance.

**Compute function.**

```python
import re

def metric_claim_quant_density(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is a list of strings (possibly empty/missing).
    """
    claims = (paper.get("frontmatter", {}) or {}).get("claims_summary") or []
    if not claims:
        return 0.0

    quant_pattern = re.compile(
        r'(\d+(\.\d+)?\s*%|\bCI\b|p\s*[<>=]\s*0\.\d+|\bI\^?2\b|\bAUC\b|n\s*=\s*\d+|'
        r'\d+(\.\d+)?\s*(±|\+/-)|95%|\bOR\s*=|\bHR\s*=|P-score|SUCRA|\d+\.\d+)',
        re.I,
    )
    hits = sum(1 for c in claims if quant_pattern.search(c or ""))
    return hits / len(claims)
```

**What the function does & why.** For each line in `claims_summary`, a regex looks for the surface
markers of quantitative, falsifiable science: percentages, confidence intervals, p-values,
heterogeneity statistics, effect-size labels, sample sizes, or bare decimal numbers. The metric is
the fraction of claim lines carrying at least one such marker. A missing or empty `claims_summary`
(e.g. from a paywalled/abstract-only source, as the shape doc flags) scores a hard 0, matching the
documented expectation that thinness here should be penalized, not excused.

**Why it's hard to Goodhart.** Simply sprinkling numbers into vague claims to trip the regex is
detectable in combination with Metric 1: any inflation of the number or specificity of claims that
isn't backed by a matching Cognitive Layer claim count gets caught by the self-consistency check.
Fabricating precise-looking numbers that don't appear anywhere else in the artifact is also a form of
the exact fabrication risk the honesty metric (5) is built to catch if it leaks into other fields.

---

## 3. Layer Substantiveness & Coverage

**How it signals good science.** The Layer Index is the manifest's promise of what depth exists
behind it. A rigorous compilation populates *multiple* layers (cognitive reasoning, implementation,
exploration trace, evidence) with entries whose one-line descriptions carry specific counts and
content ("14-node research DAG," "8 falsifiable claims (C01–C08)") rather than generic filler ("Notes
about the paper"). A manifest that lists a layer but describes it vaguely is signaling a thin or
rushed compilation even before you open the file it points to.

**Compute function.**

```python
import re

def metric_layer_substantiveness(paper: dict) -> float:
    """
    Assumes: paper["body"]["layer_index"] maps layer name -> list of {"file","description"} dicts,
    or None/[] when that layer is genuinely absent from the ARA.
    """
    li = (paper.get("body", {}) or {}).get("layer_index", {}) or {}
    weights = {"cognitive": 0.35, "physical": 0.20, "trace": 0.20, "evidence": 0.25}
    expected_rows = {"cognitive": 5, "physical": 2, "trace": 1, "evidence": 3}

    total = 0.0
    for layer, w in weights.items():
        rows = li.get(layer) or []
        if not rows:
            total += 0.0  # absent layer is penalized, not skipped
            continue
        richness = min(1.0, len(rows) / expected_rows[layer])
        digit_rows = sum(1 for r in rows if re.search(r'\d', r.get("description", "") or ""))
        specificity = digit_rows / len(rows)
        layer_score = 0.5 * richness + 0.5 * specificity
        total += w * layer_score
    return total
```

**What the function does & why.** For each of the four layers that are near-universally expected
(cognitive, physical, trace, evidence — Data is treated as a genre-conditional bonus and deliberately
excluded from the denominator so its absence doesn't unfairly tank non-data papers, while its
presence would still show up favorably via richer physical/evidence rows in practice), the function
scores two things: how many entries are listed relative to a realistic expectation, and what
fraction of those entries' descriptions contain a concrete count or number (a cheap but effective
proxy for "this description says something specific" vs. generic boilerplate). Layers that are
missing entirely score zero for their full weight.

**Why it's hard to Goodhart.** Padding a layer with many low-content rows raises richness but tanks
specificity (rows without digits drag the average down), and padding rows with fake digits to fake
specificity is exactly the kind of unsupported precision Metric 5 and Metric 1 are watching for
elsewhere in the same document — the fabricated counts have to stay consistent across the whole
manifest or they get caught.

---

## 4. Keyword Specificity & Non-Genericness

**How it signals good science.** Keywords exist to let an agent triage relevance without reading
further. Keywords that are generic ("analysis," "study," "method") carry no discriminating
information and are cheap to write regardless of paper quality; keywords that are specific,
domain-grounded, and actually traceable back into the title/abstract/domain text reflect that the
compiler genuinely extracted the paper's technical vocabulary rather than padding a list to hit the
"5–10 items" requirement.

**Compute function.**

```python
def metric_keyword_specificity(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["keywords"] is a list of strings (possibly empty/missing);
    "abstract", "title", "domain" are strings (possibly empty/missing), used only as grounding text.
    """
    fm = paper.get("frontmatter", {}) or {}
    keywords = fm.get("keywords") or []
    if not keywords:
        return 0.0

    grounding_text = " ".join([
        (fm.get("abstract") or "").lower(),
        (fm.get("title") or "").lower(),
        (fm.get("domain") or "").lower(),
    ])
    generic_terms = {
        "analysis", "study", "review", "research", "method", "methods", "approach",
        "model", "performance", "evaluation", "results", "data", "paper", "system",
    }

    scores = []
    for kw in keywords:
        kwl = (kw or "").lower().strip()
        words = kwl.split()
        is_generic = (not words) or all(w in generic_terms for w in words) or len(kwl) < 4
        grounded = kwl in grounding_text or any(len(w) > 4 and w in grounding_text for w in words)
        s = (0.0 if is_generic else 0.5) + (0.5 if grounded else 0.0)
        scores.append(s)

    base = sum(scores) / len(scores)
    uniqueness = len(set(k.lower().strip() for k in keywords)) / len(keywords)
    return base * uniqueness
```

**What the function does & why.** Each keyword earns up to 0.5 points for not being generic
boilerplate and up to 0.5 points for being traceable into the paper's own abstract/title/domain text
(i.e. actually grounded, not invented). The per-keyword average is then multiplied by a uniqueness
ratio so that duplicate or near-duplicate keywords (a cheap way to hit a "10 items" quota) drag the
score down. A missing keyword list scores zero.

**Why it's hard to Goodhart.** Padding with generic terms costs points directly; padding with
ungrounded but seemingly-technical jargon costs points via the grounding check, since it won't appear
anywhere else in the manifest's own text; and padding with duplicates costs points via uniqueness.
An adversary would have to genuinely extract more specific, correct terminology from the actual
abstract — which is the honest way to raise this score.

---

## 5. Bibliographic Identity Honesty Under Uncertainty

**How it signals good science.** Good science reporting is honest about what is and isn't known
rather than fabricating plausible-looking placeholders. The shape doc explicitly distinguishes a
legitimate `doi = "Not specified in paper"` from a fabricated DOI. A trustworthy manifest should be
rewarded for correctly-formed identifiers *and* for honestly flagging absence, while a manifest with
malformed-but-confident-looking values (a DOI-shaped string that isn't a real DOI, a single-token
"author" list, an implausible year) should be penalized as suspect fabrication.

**Compute function.**

```python
import re

def metric_biblio_honesty(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"] contains (possibly missing/empty) title, authors, year, venue,
    doi, ara_version, domain fields, per the documented frontmatter schema.
    """
    fm = paper.get("frontmatter", {}) or {}
    fields = ["title", "authors", "year", "venue", "doi", "ara_version", "domain"]
    total = 0.0

    for f in fields:
        v = fm.get(f)
        if not v:
            total += 0.0  # missing mandatory field: hard penalty, no skip
            continue
        if f == "doi":
            valid_doi = bool(re.match(r'^10\.\d{4,9}/\S+$', v))
            valid_arxiv = bool(re.match(r'^arXiv:\d{4}\.\d{4,5}', v, re.I))
            honest_na = v.strip() == "Not specified in paper"
            if valid_doi or valid_arxiv or honest_na:
                total += 1.0
            else:
                total += 0.2  # doi-shaped but unverifiable / malformed: suspect
        elif f == "authors":
            ok = isinstance(v, list) and len(v) >= 1 and all(
                isinstance(a, str) and len(a.split()) >= 2 for a in v
            )
            total += 1.0 if ok else 0.3
        elif f == "year":
            total += 1.0 if isinstance(v, int) and 1900 < v <= 2027 else 0.0
        else:
            total += 1.0 if isinstance(v, str) and len(v.strip()) > 10 else 0.2

    return total / len(fields)
```

**What the function does & why.** It walks the seven mandatory bibliographic fields and scores each
for presence, plausibility, and — for DOI specifically — honesty: a correctly-formatted DOI/arXiv id
or the explicit honest fallback string both score full marks, while a doi-shaped-but-invalid string
is treated as more suspicious than an honest "unknown" and scores lower. Similarly, a single-name or
missing author list, an implausible year, or a boilerplate one-word venue/domain string are all
penalized rather than given credit for merely being non-empty.

**Why it's hard to Goodhart.** Fabricating a well-formed-looking-but-fake DOI to score well is
directly disincentivized: the honest "Not specified in paper" fallback scores *equally well* as a
valid identifier, so there's no reward for the compiler to guess/fabricate one — removing the
incentive to game this field at all. Fabricating full author names or venue strings to pass the
length/token checks risks contradicting the `abstract` text, which grounding-based Metric 4 partly
cross-references.

---

## Combination

These five metrics are jointly hard to game because they check the same manifest from angles that
pull against each other. Padding `claims_summary` with more (or more numerically dressed-up) entries
to win Metric 2 breaks the count agreement Metric 1 checks against the Cognitive Layer's own stated
claim count. Padding the Layer Index with extra rows to win Metric 3's richness term tanks its
specificity term unless the added rows carry real counts — and any invented counts must stay
consistent with Metric 1's cross-checks. Padding `keywords` to look thorough is directly punished by
Metric 4's genericness, grounding, and uniqueness penalties. And fabricating confident-looking
identifiers (DOI, authors, venue) to appear complete scores no better — and often worse — than
honestly flagging unavailable data under Metric 5, removing the incentive to fabricate at all. A
paper can't cheaply inflate one axis without either contradicting another axis's cross-check or
failing its own specificity/grounding test.
