# Proposer #2 — Stage 2 revision — metrics for `PAPER.md` (root manifest)

## Changes from stage 1

Judge ranked this set #1 for reaching past compiler surface (Metric 3's conditional disclosure
logic, Metric 5's per-claim evidentiary ratio) but flagged four concrete weaknesses. All four are
fixed below, nothing else was touched:

1. **Metric 2 (falsifiability density)** — the hedging floor only applied when the numeric/CI/compare
   score was already exactly `0.0`, so `"the method may improve accuracy by 5%"` scored `0.4` despite
   being hedged and unfalsifiable. Fixed: hedging now applies a flat penalty *after* the additive
   score is computed, regardless of whether numbers are present.
2. **Metric 3 (epistemic transparency)** — the disclosure regex rewarded the mere presence of generic
   absence language ("not available"), so a compiler that learned the trigger phrase could farm
   `0.75` on any thin paper without actually naming what's missing. Fixed: disclosure is now checked
   *per thin layer* — a thin physical layer requires code/script-specific disclosure language, a thin
   data layer requires dataset-specific language — and partial credit is given only when the specific
   gap(s) actually present are the ones named.
3. **Metric 4 (domain–claim grounding)** — the 10-word stoplist was too small to survive a
   buzzword-padded `domain`/`keywords` list. Fixed: stoplist expanded ~6x to cover generic
   academic/meta-scientific filler, plus a crude IDF-style specificity weight (short/generic tokens
   count less than long/technical tokens) so padding with common words no longer buys free overlap.
4. **Missing bibliographic-identity metric** — this set dropped DOI/author/year integrity entirely,
   which the judge flagged as a real coverage gap given the manifest's primary job is bibliographic
   identity. Added **Metric 6 — Identifier & Bibliographic Integrity**, explicitly borrowing agent1's
   incentive-design insight (honest `"Not specified in paper"` scores *equal* to a valid DOI, removing
   the fabrication incentive) rather than agent3's regression (honest-NA scored lower than a valid
   DOI, which reintroduces the incentive to fabricate).

Metrics 1 and 5 were not criticized and are unchanged. The Combination paragraph is rewritten to
integrate the new metric and the reworked interactions.

Assumed parsed representation for every function below (a dict I'll call `paper`):

```python
paper = {
  "frontmatter": {
    "title": str, "authors": [str], "year": int, "venue": str, "doi": str,
    "ara_version": str, "domain": str, "keywords": [str],
    "claims_summary": [str],   # one line per claim group
    "abstract": str,
  },
  "body": {
    "overview": str,  # raw prose of the "## Overview" section
    "layer_index": {
      # each present layer -> list of row dicts; ABSENT layer -> [] (empty list, not missing key)
      "cognitive": [{"file": str, "description": str}, ...],
      "physical":  [{"file": str, "description": str, "claims": str|None}, ...],
      "data":      [{"file": str, "description": str}, ...],
      "trace":     [{"file": str, "description": str}, ...],
      "evidence":  [{"file": str, "description": str}, ...],
    },
  },
}
```

No file outside `PAPER.md` itself is read by any metric — where a count is needed (e.g. how many
claims `claims.md` actually contains), it is recovered from the *description text* the compiler
already wrote into the Layer Index row for that file (e.g. `"8 falsifiable claims (C01-C08)..."`),
never from opening `claims.md`.

---

## 1. Frontmatter/Body Self-Consistency

**How it signals good science.** A manifest that accurately mirrors its own body is evidence the
compiler (and, transitively, the underlying paper extraction) is internally coherent rather than
hallucinated or stale. Science that can't correctly summarize its own claim count is unlikely to be
trustworthy on harder facts. This is a cheap, structural proxy for "was this manifest actually
regenerated from the true content, or is it drifted/fabricated boilerplate."

**Compute function.**
```python
import re

def self_consistency_score(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is a list; paper["body"]["layer_index"]["cognitive"]
    contains a row whose file is "claims.md" (or similar) with a description that states a count,
    e.g. "8 falsifiable claims (C01-C08)". Also checks evidence counts the same way against
    evidence/README.md's description, e.g. "Index of 2 tables + 3 figures" vs actual row count in
    the evidence table minus the README row itself.
    """
    def extract_count(desc: str) -> int | None:
        m = re.search(r'(\d+)\s+(?:falsifiable\s+)?claims?', desc, re.I)
        if m:
            return int(m.group(1))
        return None

    def extract_evidence_counts(desc: str) -> tuple[int, int] | None:
        m = re.search(r'(\d+)\s+tables?\s*\+\s*(\d+)\s+figures?', desc, re.I)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None

    checks = []

    # Check 1: claims_summary length vs stated claims.md count
    cog_rows = paper["body"]["layer_index"].get("cognitive", [])
    claims_row = next((r for r in cog_rows if "claims" in r["file"].lower()), None)
    n_summary = len(paper["frontmatter"].get("claims_summary", []))
    if claims_row is None:
        checks.append(0.0)  # no claims.md at all -> can't verify, penalize (hard constraint)
    else:
        stated = extract_count(claims_row["description"])
        if stated is None or n_summary == 0:
            checks.append(0.0)
        else:
            diff = abs(stated - n_summary)
            checks.append(max(0.0, 1.0 - diff / max(stated, 1)))

    # Check 2: evidence README stated counts vs actual row count in evidence table
    ev_rows = paper["body"]["layer_index"].get("evidence", [])
    readme_row = next((r for r in ev_rows if "readme" in r["file"].lower()), None)
    if readme_row is None:
        checks.append(0.0)
    else:
        stated_ev = extract_evidence_counts(readme_row["description"])
        actual_files = [r for r in ev_rows if "readme" not in r["file"].lower()]
        n_tables_actual = sum(1 for r in actual_files if "table" in r["file"].lower())
        n_figs_actual = sum(1 for r in actual_files if "figure" in r["file"].lower())
        if stated_ev is None:
            checks.append(0.0)
        else:
            t_ok = 1.0 - min(1.0, abs(stated_ev[0] - n_tables_actual) / max(stated_ev[0], 1))
            f_ok = 1.0 - min(1.0, abs(stated_ev[1] - n_figs_actual) / max(stated_ev[1], 1))
            checks.append((t_ok + f_ok) / 2)

    return sum(checks) / len(checks)
```

**What the function does & why.** It re-derives two counts that the compiler *asserts in prose*
(claim count, table/figure count) from two independent places in the same document — the
`claims_summary` list length, and the literal file rows under `### Evidence` — and compares them to
what the layer-index description string *says*. Perfect agreement scores 1.0; drift scores down
proportionally; a missing row to check against scores 0 outright (per the hard constraint: you
can't dodge the check by omitting the thing being checked).

**Why it's hard to Goodhart.** To game this you'd have to keep `claims_summary`'s length, the
`claims.md` description's stated number, and (independently) the evidence table's row count all in
lockstep — which is exactly the property we want (internal coherence), not a shortcut around it.
Padding `claims_summary` with junk lines to hit a target count would trip metric 2 below (falsifiability
density), because junk lines are vague.

---

## 2. Claim Falsifiability & Precision Density

**How it signals good science.** Good science makes claims that could in principle be wrong —
quantified, comparative, bounded. `claims_summary` is the compiler's most compressed rendering of
the paper's actual findings; if those one-liners are vague ("the method performs well") rather than
precise ("AUC gain of 0.025, 95% CI 0.005–0.045, I²=0%"), that is a direct signal of either a weak
underlying paper or a lossy/lazy compilation — both are "bad science" outcomes for our purposes.

**Compute function.**
```python
import re

def falsifiability_density(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is a list[str]. Empty/missing -> 0 (hard
    constraint: thin claims_summary is penalized, not skipped).

    Stage-2 fix: the hedging penalty now applies unconditionally to every claim, not just as a
    fallback when the additive score is exactly 0.0. A claim can have a bare number AND be hedged
    ("may improve accuracy by 5%") -- that combination must score low, not 0.4.
    """
    claims = paper["frontmatter"].get("claims_summary", [])
    if not claims:
        return 0.0

    number_pat = re.compile(r'\d')
    ci_pat = re.compile(r'\b(CI|confidence interval|±|p\s*[<=>]\s*0?\.\d+|I2|I²)\b', re.I)
    compare_pat = re.compile(r'\b(vs\.?|versus|compared to|outrank|higher than|lower than|greater|superior|inferior)\b', re.I)
    vague_pat = re.compile(r'\b(may|might|could|suggests?|appears? to|potentially|is important|plays a role|likely)\b', re.I)

    per_claim_scores = []
    for line in claims:
        score = 0.0
        if number_pat.search(line):
            score += 0.4
        if ci_pat.search(line):
            score += 0.3
        if compare_pat.search(line):
            score += 0.3
        score = min(score, 1.0)

        # Hedging penalty is unconditional: a claim that hedges its own quantification
        # ("may improve accuracy by 5%") is still an unfalsifiable claim wearing a number as a
        # costume, so subtract regardless of what the additive score was.
        if vague_pat.search(line):
            score = max(0.05, score - 0.5)

        per_claim_scores.append(score)

    return sum(per_claim_scores) / len(per_claim_scores)
```

**What the function does & why.** Each `claims_summary` line is scanned for hallmarks of a
falsifiable, checkable statement: a bare number, a statistical-uncertainty marker (CI/p-value/I²),
and an explicit comparison. These stack additively up to 1.0 per claim, then a hedging-language
penalty is subtracted unconditionally — a numerically-dressed but hedged claim ("may improve
accuracy by 5%") now lands near the floor (0.05) instead of surviving at 0.4 just because a digit is
present. The manifest-level score is the mean across all claims, so one strong claim can't hide many
weak ones.

**Why it's hard to Goodhart.** You could stuff numbers into every line, but numbers alone only buy
0.4, and now hedging language can't be layered on top for free deniability — it always costs 0.5.
You'd need genuine comparative and uncertainty language without hedges, which is harder to fabricate
plausibly without it showing up as internally contradictory against the abstract or the claim count
(metric 1). Randomly inserting digits to farm points also risks mismatching the real `claims.md`
count check in metric 1 if it inflates line count.

---

## 3. Epistemic Transparency of Absence

**How it signals good science.** The shape doc is explicit that thin layers (no code, no dataset,
abstract-only source) are *real* and should be penalized — but there's a meaningful difference
between a paper that quietly has nothing and a compiler/paper that explicitly flags what's missing
and why (e.g. "No analysis code or accessioned primary dataset was released; the work reuses
extracted summary AUC statistics"). Explicit disclosure of a limitation is itself a marker of
scientific honesty; silent thinness with no acknowledgment is a weaker, more suspicious signal.

**Compute function.**
```python
import re

def epistemic_transparency_score(paper: dict) -> float:
    """
    Assumes: paper["body"]["overview"] is a string (prose); paper["body"]["layer_index"] has keys
    for "physical" and "data" (empty list if the layer is genuinely absent from the ARA).

    Stage-2 fix: disclosure credit is no longer earned by *any* generic absence phrase. It is now
    keyed to which layer is actually thin -- a thin physical layer needs code/script-specific
    disclosure language, a thin data layer needs dataset-specific disclosure language. Naming a gap
    that doesn't exist, or using a generic absence phrase that doesn't specify what's missing, no
    longer buys credit.
    """
    overview = paper["body"].get("overview", "") or ""

    code_disclosure_pat = re.compile(
        r'\bno\s+(analysis\s+)?(code|scripts?)\s+(was|were|is|are)?\s*(released|available|provided)\b|'
        r'\bcode\s+(is\s+)?not\s+(publicly\s+)?(available|released)\b|'
        r'\bwithout\s+released\s+code\b|\bno\s+source\s+code\b',
        re.I
    )
    data_disclosure_pat = re.compile(
        r'\bno\s+(accession(ed)?\s+)?(primary\s+)?dataset\s+(was|is)?\s*(released|available|provided)?\b|'
        r'\bdata\s+(is\s+|are\s+)?not\s+(publicly\s+)?available\b|'
        r'\bno\s+accession(ed)?\s+(dataset|data)\b|'
        r'\breuses?\s+extracted\s+summary',
        re.I
    )

    physical_rows = paper["body"]["layer_index"].get("physical", [])
    data_rows = paper["body"]["layer_index"].get("data", [])
    thin_physical = len(physical_rows) <= 1
    thin_data = len(data_rows) == 0

    if not thin_physical and not thin_data:
        # rich implementation/data layer present: transparency about absence is moot; score high
        return 1.0

    required_patterns = []
    if thin_physical:
        required_patterns.append(code_disclosure_pat)
    if thin_data:
        required_patterns.append(data_disclosure_pat)

    matched = sum(1 for pat in required_patterns if pat.search(overview))
    disclosure_completeness = matched / len(required_patterns)

    if disclosure_completeness == 1.0:
        return 0.75   # every actually-thin layer is specifically, correctly disclosed
    elif disclosure_completeness > 0.0:
        return 0.4    # named one real gap but silent on another real gap -- partial honesty
    else:
        return 0.15   # thin AND undisclosed (or disclosed with unspecific language) -- looks silent
```

**What the function does & why.** It first checks whether the paper actually has substantive
code/data layers; if so, the question of disclosure is moot and it scores at ceiling. If the
physical and/or data layers are thin (which the shape doc says will legitimately happen for many
paper genres), it requires the overview prose to name the *specific* gap that is actually present —
a thin physical layer must be disclosed with code/script language, a thin data layer must be
disclosed with dataset language — rather than crediting any generic "not available" phrase
regardless of what it's attached to. A paper with two real gaps that discloses only one now scores
strictly between "fully honest" and "silent," instead of the old binary that let a single trigger
phrase buy full disclosure credit for an arbitrary combination of gaps.

**Why it's hard to Goodhart.** You can't sprinkle a generic absence phrase to inflate the score,
because the metric only rewards disclosure *conditional on which specific layer is actually thin* —
"no code released" prose does nothing for a thin *data* layer, and vice versa, so a compiler that
learns one trigger phrase can no longer cover both branches. Adding disclosure language to a paper
whose layers are already rich buys nothing (branch never reached). Compilers/authors also can't
cheaply fabricate a rich physical/data layer instead, because that would need to survive metric 1's
cross-checks and metric 5's evidence-density ratio.

---

## 4. Domain–Claim Lexical Grounding

**How it signals good science.** `domain` and `keywords` are supposed to be a faithful compression
of what the paper actually contributes. If those tags are generic filler disconnected from what the
`claims_summary`/`abstract` actually say, that indicates either a low-fidelity/rushed extraction or
a paper whose framing oversells its actual (narrower, vaguer) content — both degrade trust in the
manifest as a Level-1 relevance signal, which is its entire purpose per the shape doc's "Purpose"
section.

**Compute function.**
```python
import re

def domain_claim_grounding(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"] has "domain" (str), "keywords" (list[str]), "claims_summary"
    (list[str]), "abstract" (str). Missing/empty domain, keywords, or claims_summary -> penalized,
    not skipped.

    Stage-2 fix: the stoplist was too small (10 words) to survive a buzzword-padded domain/keyword
    list, so it's expanded to cover common academic/meta-scientific filler, and overlap is now
    weighted by a crude IDF-style specificity proxy (short/generic surviving tokens count less than
    long/technical ones) instead of counting every non-stopword token equally.
    """
    fm = paper["frontmatter"]
    domain = fm.get("domain", "") or ""
    keywords = fm.get("keywords", []) or []
    claims = fm.get("claims_summary", []) or []
    abstract = fm.get("abstract", "") or ""

    if not domain or not keywords or not claims:
        return 0.0

    def tokenize(s: str) -> set:
        return set(w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", s.lower())
                   if w not in _STOPWORDS)

    def weight(word: str) -> float:
        # Crude IDF proxy without a corpus: generic academic/meta-scientific words that survive
        # tokenization (because they're >=4 chars and not in the hard stoplist) still shouldn't
        # count as much as a genuinely technical/domain-specific term.
        if word in _GENERIC_ACADEMIC:
            return 0.25
        return 1.0 if len(word) >= 7 else 0.6

    tag_vocab = tokenize(domain) | set(
        w.lower() for kw in keywords for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", kw)
    )
    content_vocab = tokenize(" ".join(claims) + " " + abstract)

    if not tag_vocab or not content_vocab:
        return 0.0

    overlap = tag_vocab & content_vocab
    union = tag_vocab | content_vocab

    weighted_overlap = sum(weight(w) for w in overlap)
    weighted_union = sum(weight(w) for w in union)
    weighted_tag_vocab = sum(weight(w) for w in tag_vocab)

    jaccard = weighted_overlap / weighted_union if weighted_union else 0.0
    coverage = weighted_overlap / weighted_tag_vocab if weighted_tag_vocab else 0.0

    return 0.5 * jaccard + 0.5 * coverage


_STOPWORDS = {
    "with", "from", "that", "this", "into", "such", "using", "based", "across", "their",
    "which", "these", "those", "were", "have", "will", "than", "also", "each", "some",
    "when", "where", "while", "there", "here", "over", "under", "after", "before", "about",
}

# Generic academic / meta-scientific filler that tokenizes fine (len >= 4) but should not count
# as evidence of genuine domain grounding -- this is the "expanded stoplist" fix.
_GENERIC_ACADEMIC = {
    "study", "studies", "analysis", "analyses", "research", "method", "methods", "approach",
    "approaches", "performance", "results", "result", "findings", "finding", "data", "dataset",
    "datasets", "model", "models", "framework", "system", "systems", "review", "significant",
    "novel", "new", "paper", "work", "evaluation", "evaluate", "evaluated", "assessment",
    "assess", "assessed", "outcome", "outcomes", "measure", "measures", "measurement",
    "level", "levels", "high", "higher", "low", "lower", "large", "small", "important",
    "quality", "process", "processes", "factor", "factors", "role", "impact", "effect",
    "effects", "improve", "improved", "improvement", "compare", "comparison", "comparative",
    "clinical", "population", "sample", "samples", "group", "groups", "test", "tests",
    "testing", "diagnostic", "diagnosis", "value", "values",
}
```

**What the function does & why.** It builds a "tag vocabulary" from `domain` + `keywords` and a
"content vocabulary" from `claims_summary` + `abstract`, then measures overlap two ways: Jaccard
(overall shared-vocabulary fraction) and coverage (what fraction of the domain/keyword terms are
actually attested in the substantive content) — both now weighted so generic academic filler
("study", "performance", "model", "significant"...) that survives the hard stoplist still only
contributes a quarter of a genuine technical term's weight, and short surviving tokens count less
than long/technical ones. Averaging both punishes both a tag list that's mostly disconnected filler
and a tag list that's technically present but drowned in unrelated abstract noise.

**Why it's hard to Goodhart.** Copy-pasting abstract words directly into `keywords` to farm overlap
is the "honest" behavior this metric wants to reward (keywords *should* reflect content) — there's
no free lunch, because keywords that are just repeated abstract fragments with no added specificity
would also need to survive human/downstream-agent scrutiny of the Level-1 view being useful at all
(outside this metric's scope, but the incentive it creates is aligned, not perverse). Padding domain
with generic buzzwords ("novel", "significant", "high-performance") to raise coverage odds is now
directly countered: those words are either in the hard stoplist or discounted 4x by the generic-term
weight, so bloating the tag vocabulary with filler drags weighted Jaccard down rather than helping,
even when a stray overlap technically exists.

---

## 5. Layer-Index Evidentiary Density per Claim

**How it signals good science.** Rigorous work backs each claim with proportionate scaffolding —
declared experiments, an exploration trace, and evidence artifacts (tables/figures). A manifest
claiming many findings while indexing almost no supporting layers is a red flag for
overclaiming/thin evidencing; a manifest with rich, well-populated layers per claim indicates the
underlying paper (and its compilation) did the work to substantiate what it asserts.

**Compute function.**
```python
import re

def evidentiary_density_per_claim(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"]["claims_summary"] is a list[str]; paper["body"]["layer_index"]
    has "trace" and "evidence" lists of row dicts, each possibly absent (empty list).
    """
    n_claims = len(paper["frontmatter"].get("claims_summary", []))
    if n_claims == 0:
        return 0.0  # can't evidence claims that don't exist / weren't extracted -> penalize

    li = paper["body"]["layer_index"]

    # trace node count, parsed from description text like "14-node research DAG..."
    trace_rows = li.get("trace", [])
    trace_nodes = 0
    for r in trace_rows:
        m = re.search(r'(\d+)-node', r["description"])
        if m:
            trace_nodes += int(m.group(1))

    # evidence artifact count = number of table/figure files actually indexed (excluding README)
    evidence_rows = li.get("evidence", [])
    n_evidence_files = sum(
        1 for r in evidence_rows
        if "table" in r["file"].lower() or "figure" in r["file"].lower()
    )

    # ratios, each capped at 1.0 so a single overstuffed layer can't dominate
    trace_ratio = min(1.0, trace_nodes / (2 * n_claims))
    evidence_ratio = min(1.0, n_evidence_files / n_claims)

    return 0.5 * trace_ratio + 0.5 * evidence_ratio
```

**What the function does & why.** It normalizes two independently-countable resources — exploration
DAG nodes (from `/trace`) and evidence artifacts (tables/figures from `/evidence`) — by the number
of claims the manifest asserts, on the theory that a well-substantiated paper should show a roughly
proportional amount of exploration and evidence per claim it makes (thresholds of "2 nodes per
claim" and "1 evidence file per claim" are conservative floors, capped at 1.0 so no single glut
layer can carry the whole score). Zero claims, or claims with no trace/evidence layer at all, score
at or near zero — satisfying the hard constraint that missing inputs are penalized rather than
excluded.

**Why it's hard to Goodhart.** Inflating claim count to game other metrics (e.g. splitting one
finding into many `claims_summary` lines) directly *lowers* this ratio unless matched by real
evidence/trace growth, and also risks failing metric 1's cross-check against the true `claims.md`
count. Conversely, padding `/evidence` or `/trace` with junk rows to inflate this metric would need
matching description text (e.g., a bigger stated node count) that metric 1's consistency logic
doesn't directly check here, but any fabricated bulk evidence not reflected in genuinely
distinguishable claims would look anomalous under metric 2 (claims stay vague/few while "evidence"
balloons) — the set is designed so these two move together rather than trading off.

---

## 6. Identifier & Bibliographic Integrity (new)

**How it signals good science.** The manifest's primary job, per the shape doc's Purpose section, is
bibliographic identity — a downstream agent has to be able to trust `title`/`authors`/`year`/`doi`
enough to cite, dedupe, or route on them before it ever opens the paper. A fabricated-looking DOI, a
blank author list, or an implausible year is a direct integrity failure at the manifest's core job,
independent of anything the body prose says. But the shape doc is explicit that `doi` legitimately
has an honest-absence sentinel (`"Not specified in paper"` for datasets/cohorts/non-indexed
preprints) — a good metric must reward that honesty exactly as much as a real DOI, or it creates an
incentive to fabricate a plausible-looking one whenever the true answer is "there isn't one."

**Compute function.**
```python
import re

def bibliographic_integrity_score(paper: dict) -> float:
    """
    Assumes: paper["frontmatter"] has "doi" (str), "authors" (list[str]), "year" (int), "title"
    (str), "venue" (str) -- all mandatory fields per the shape doc. Missing/empty values are
    penalized, never skipped (hard constraint).

    Design note (Stage-2 addition, explicitly borrowing agent1's insight over agent3's): the honest
    sentinel "Not specified in paper" for `doi` scores EQUAL (1.0) to a structurally valid DOI/arXiv
    ID. This removes any incentive for the compiler to fabricate a plausible-looking identifier when
    the source paper genuinely has none -- agent3's design (0.6 for honest-NA vs 1.0 for a valid DOI)
    reintroduces exactly that fabrication incentive and is deliberately not used here.
    """
    fm = paper["frontmatter"]
    checks = []

    # --- doi / identifier honesty ---
    doi = (fm.get("doi") or "").strip()
    doi_pat = re.compile(r'^10\.\d{4,9}/\S+$')
    arxiv_pat = re.compile(r'^(arXiv:)?\d{4}\.\d{4,5}(v\d+)?$', re.I)
    honest_na = doi.lower() == "not specified in paper"

    if not doi:
        checks.append(0.0)  # blank is NOT the honest sentinel -- likely a dropped/failed extraction
    elif honest_na or doi_pat.match(doi) or arxiv_pat.match(doi):
        checks.append(1.0)  # honest absence == valid identifier: no fabrication incentive either way
    else:
        # non-empty, not the honest sentinel, not structurally valid -> most likely a
        # fabricated/malformed identifier, worse than admitting absence
        checks.append(0.1)

    # --- authors ---
    authors = fm.get("authors") or []
    if not authors:
        checks.append(0.0)
    else:
        bogus = sum(
            1 for a in authors
            if not a.strip() or a.strip().lower() in {"unknown", "anonymous", "n/a", "et al"}
        )
        checks.append(max(0.0, 1.0 - bogus / len(authors)))

    # --- year plausibility ---
    year = fm.get("year")
    if not isinstance(year, int) or not (1900 <= year <= 2027):
        checks.append(0.0)
    else:
        checks.append(1.0)

    # --- title present (mandatory, always expected per shape doc) ---
    title = (fm.get("title") or "").strip()
    checks.append(1.0 if title else 0.0)

    # --- venue: no established honest-NA convention for this field in the shape doc (unlike doi),
    # so an explicit "not specified"/"unknown" venue gets partial, not full, credit -- otherwise we'd
    # be inventing a new honesty loophole the shape doc doesn't sanction.
    venue = (fm.get("venue") or "").strip()
    if not venue:
        checks.append(0.0)
    elif venue.lower() in {"not specified", "not specified in paper", "unknown"}:
        checks.append(0.5)
    else:
        checks.append(1.0)

    return sum(checks) / len(checks)
```

**What the function does & why.** It checks five independent bibliographic-identity fields —
identifier, authors, year, title, venue — each contributing equally to the average, with the DOI
check specifically designed so that the honest `"Not specified in paper"` sentinel and a
well-formed DOI/arXiv ID land on the *same* score (1.0), while a non-empty string that is neither
scores worse (0.1) than either. This makes "admit you don't have one" strictly at least as good as
having one, and strictly better than faking one.

**Why it's hard to Goodhart.** The core anti-Goodhart move is structural, not just penal: because
honest absence already scores at ceiling, there is nothing to gain by fabricating a plausible DOI —
the expected-value-maximizing move for a compiler facing a paper with no real identifier is always
to write the honest sentinel, never to guess. Syntactically valid *but fake* DOIs are the one
residual attack (pattern-matching a regex is cheap), but fabricating a real-looking DOI risks
diverging from the true value the moment any downstream consumer resolves it — a cost this metric
doesn't have to model directly because the incentive to attempt it has already been removed by
making honesty free. The authors/year/venue checks are cheap to satisfy honestly (they're supposed
to just reflect the source paper) and offer no shortcut: leaving authors blank or a year out of
range costs more than reporting them correctly, and there's no thin-layer branch to exploit the way
there is in metric 3.

---

## Combination

These six metrics are built to pull against each other under gaming pressure. Inflating
`claims_summary`'s length or vividness (to win metric 2 or 5) risks breaking metric 1's
self-consistency check against the true claim count baked into `claims.md`'s own description text.
Dressing a hedged claim in a bare number no longer buys anything in metric 2 either, since the
hedging penalty now applies unconditionally — so the two easiest surface tricks for claims
(inflate count, add fake numbers) are each independently blocked by a different metric. Padding
`domain`/`keywords` with buzzwords to look comprehensive now costs weighted-Jaccard points directly
(metric 4's expanded stoplist and specificity weighting discount generic filler to a quarter value),
even as it might still raise naive coverage. Fabricating a rich physical/data layer to dodge metric
3's undisclosed-thinness penalty would need to survive metric 1's cross-checks and metric 5's
per-claim evidence ratio (bulk without matching claim substance stands out as disproportionate); and
metric 3 itself can no longer be gamed with one generic absence phrase, since credit is now keyed to
which specific layer (code vs. data) is actually thin. Bulking up `/evidence` or `/trace` node counts
to win metric 5 does nothing for metric 2's claim-precision score, so a paper that "wins" evidentiary
density while its actual claims stay vague or numerically hollow gets caught by the
falsifiability-density metric instead. Metric 6 closes the remaining lever: a compiler that fabricates
a plausible DOI to look complete gains nothing over honestly disclosing its absence (both score 1.0),
so the one surface feature the other five metrics don't touch — bibliographic identity — is
covered without creating a new fabrication incentive of its own. No single lever (claim count, tag
vocabulary, disclosure language, evidence bulk, or identifier fabrication) can be pulled in isolation
without depressing at least one other metric in the set.
