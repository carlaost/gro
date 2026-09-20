# Proposer #2 — metrics for `PAPER.md` (root manifest)

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
    """
    claims = paper["frontmatter"].get("claims_summary", [])
    if not claims:
        return 0.0

    number_pat = re.compile(r'\d')
    ci_pat = re.compile(r'\b(CI|confidence interval|±|p\s*[<=>]\s*0?\.\d+|I2|I²)\b', re.I)
    compare_pat = re.compile(r'\b(vs\.?|versus|compared to|outrank|higher than|lower than|greater|superior|inferior)\b', re.I)
    vague_pat = re.compile(r'\b(may|might|could|suggests?|appears? to|potentially|is important|plays a role)\b', re.I)

    per_claim_scores = []
    for line in claims:
        score = 0.0
        if number_pat.search(line):
            score += 0.4
        if ci_pat.search(line):
            score += 0.3
        if compare_pat.search(line):
            score += 0.3
        if vague_pat.search(line) and score == 0.0:
            score = 0.05  # vague hedging with no quantification is close to worthless
        per_claim_scores.append(min(score, 1.0))

    return sum(per_claim_scores) / len(per_claim_scores)
```

**What the function does & why.** Each `claims_summary` line is scanned for hallmarks of a
falsifiable, checkable statement: a bare number, a statistical-uncertainty marker (CI/p-value/I²),
and an explicit comparison. These stack additively up to 1.0 per claim. A line with pure hedging
language and nothing quantitative is floored near zero. The manifest-level score is the mean across
all claims, so one strong claim can't hide many weak ones.

**Why it's hard to Goodhart.** You could stuff numbers into every line, but numbers alone only buy
0.4; you'd also need genuine comparative and uncertainty language, which is harder to fabricate
plausibly without it showing up as internally contradictory against the abstract (checked by metric
4) or against the claim count (metric 1). Randomly inserting digits to farm points also risks
mismatching the real `claims.md` count check in metric 1 if it inflates line count.

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
    """
    overview = paper["body"].get("overview", "") or ""
    disclosure_pat = re.compile(
        r'\bno\s+(analysis\s+)?(code|dataset|data|script)s?\b|'
        r'\bnot\s+released\b|\bnot\s+(publicly\s+)?available\b|'
        r'\bno\s+accession(ed)?\b|\bwithout\s+(released|public)\b',
        re.I
    )
    has_disclosure = bool(disclosure_pat.search(overview))

    physical_rows = paper["body"]["layer_index"].get("physical", [])
    data_rows = paper["body"]["layer_index"].get("data", [])
    thin_physical = len(physical_rows) <= 1
    thin_data = len(data_rows) == 0

    if not thin_physical and not thin_data:
        # rich implementation/data layer present: transparency about absence is moot; score high
        return 1.0

    # some layer is thin/absent -> transparency about it matters
    if has_disclosure:
        return 0.75  # honest but still genuinely thin -- capped below "as good as rich"
    else:
        return 0.15  # thin AND undisclosed -- looks like a silent, unflagged gap
```

**What the function does & why.** It first checks whether the paper actually has substantive
code/data layers; if so, the question of disclosure is moot and it scores at ceiling. If the
physical/data layers are thin or empty (which the shape doc says will legitimately happen for many
paper genres), it looks for language in the human-readable `## Overview` that explicitly names the
gap. Disclosed thinness is capped at 0.75 (still worse than a rich artifact, honoring the "thin =
penalized" rule) while undisclosed thinness scores near-floor, treating silent omission as weak
evidence of either sloppy compilation or an attempt to obscure a limitation.

**Why it's hard to Goodhart.** You can't just sprinkle disclosure language to inflate the score,
because the metric only rewards disclosure *conditional on* the layer actually being thin — adding
"no code released" prose to a paper whose physical layer is already rich buys nothing (branch never
reached). Compilers/authors also can't cheaply fabricate a rich physical/data layer instead, because
that would need to survive metric 1's cross-checks and metric 5's evidence-density ratio.

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

    tag_vocab = tokenize(domain) | set(w.lower() for kw in keywords for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", kw))
    content_vocab = tokenize(" ".join(claims) + " " + abstract)

    if not tag_vocab or not content_vocab:
        return 0.0

    overlap = tag_vocab & content_vocab
    jaccard = len(overlap) / len(tag_vocab | content_vocab)
    coverage = len(overlap) / len(tag_vocab)  # how much of the domain/keyword vocab is grounded

    return 0.5 * jaccard + 0.5 * coverage

_STOPWORDS = {"with", "from", "that", "this", "into", "such", "using", "based", "across", "their"}
```

**What the function does & why.** It builds a "tag vocabulary" from `domain` + `keywords` and a
"content vocabulary" from `claims_summary` + `abstract`, then measures overlap two ways: Jaccard
(overall shared-vocabulary fraction) and coverage (what fraction of the domain/keyword terms are
actually attested in the substantive content). Averaging both punishes both a tag list that's mostly
disconnected filler and a tag list that's technically present but drowned in unrelated abstract
noise.

**Why it's hard to Goodhart.** Copy-pasting abstract words directly into `keywords` to farm overlap
is the "honest" behavior this metric wants to reward (keywords *should* reflect content) — there's
no free lunch, because keywords that are just repeated abstract fragments with no added specificity
would also need to survive human/downstream-agent scrutiny of the Level-1 view being useful at all
(outside this metric's scope, but the incentive it creates is aligned, not perverse). Padding domain
with many generic buzzwords to raise coverage odds is countered because Jaccard penalizes vocabulary
bloat that isn't matched in content.

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

## Combination

These five metrics are built to pull against each other under gaming pressure. Inflating
`claims_summary`'s length or vividness (to win metric 2 or 5) risks breaking metric 1's
self-consistency check against the true claim count baked into `claims.md`'s own description text.
Padding `domain`/`keywords` with buzzwords to look comprehensive drags down metric 4's Jaccard term
even as it might raise naive coverage. Fabricating a rich physical/data layer to dodge metric 3's
undisclosed-thinness penalty would need to survive metric 1's cross-checks and metric 5's
per-claim evidence ratio (bulk without matching claim substance stands out as disproportionate).
And bulking up `/evidence` or `/trace` node counts to win metric 5 does nothing for metric 2's
claim-precision score, so a paper that "wins" evidentiary density while its actual claims stay vague
or numerically hollow gets caught by the falsifiability-density metric instead. No single lever
(claim count, tag vocabulary, disclosure language, or evidence bulk) can be pulled in isolation
without depressing at least one other metric in the set.
