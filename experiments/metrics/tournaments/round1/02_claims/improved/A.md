# Proposer 2 — Improved Metrics over `logic/claims.md`

## Changes from stage 1

1. **Added Metric 6 (Evidence/Interpretation Separation & Editorial-Leak Detection)** — closes
   the one named coverage hole ("no evidence/interpretation-separation metric"). It checks
   evaluative language in `Evidence basis`/`Statement` against `Sources` quotes (an evaluative
   word is only legitimate if the cited source actually used it) and flags `Interpretation`
   that just restates `Evidence basis` with no new synthesis.
2. **M4 Anchor Fragility now uses transitive, not direct, dependents** for reliance share —
   fixes "conflates 'few [direct] dependents' with 'low risk'" so a long chain
   (C05→C04→C03→C02→C01) correctly loads risk onto C01.
3. **M3 Triangulation now canonicalizes split experiment IDs** (`E01a`/`E01b` → `E01`) and
   additionally collapses any two distinct IDs that resolve to an identical `Sources[*].ref`
   evidence set — closes "credit multiplicity only when distinct IDs map to distinct evidence
   files," with a small extra penalty when a claim's multiplicity depended on a split that
   collapsed.
4. **M2 drops `tag_ratio` as a rewarded dimension**, per "down-weight or drop... near-free
   surface points." It survives only as a small compliance-floor deduction (max −0.05), and its
   weight is reallocated to coverage/validity/precision.

All functions still assume a parsed representation of the artifact: a list of claim dicts, one
per `## C{NN}` block, with keys `id`, `statement`, `status`, `falsification_criteria`, `proof`
(list of experiment-id strings), `evidence_basis`, `interpretation` (string, possibly
empty/absent — this field is genuinely optional per the shape doc, so its absence alone is
never penalized, only its content when present), `dependencies` (list of claim-id strings,
empty for `none`), `sources` (list of dicts with `value`, `ref`, `locator`, `quote`, `tag`),
`tags` (list of strings). Any field the shape doc marks as "always present" that comes through
empty/missing is treated as a real defect to be penalized, not skipped — per the hard
constraint, no metric below ever returns N/A.

---

## Metric 1: Falsifiability Operationalization Score (FOS)

**How it signals good science**

A claim's `Falsification criteria` field is only doing epistemic work if it names an
observable, operational condition under which the claim would be rejected — a threshold, a
comparator, a named alternative outcome. Criteria that merely restate the Statement's negation
("refuted if the results don't hold up") are Popperian-falsifiable in name only: they give a
downstream agent nothing to check against future data. This metric scores how *operational*,
as opposed to *rhetorical*, each claim's falsification criterion actually is, and separately
flags boilerplate (the same criterion template copy-pasted across every claim, which signals
the compiler filled the field mechanically rather than reasoning about each claim).

**Compute function**

```python
import re
from difflib import SequenceMatcher

def falsifiability_operationalization_score(claims):
    """
    claims: list of dicts with at least:
      'statement': str
      'falsification_criteria': str  (required field; '' if missing/absent)
    """
    OPERATIONAL_MARKERS = re.compile(
        r'(\d+(\.\d+)?%?|p\s*[<>=]|95%\s*CI|AUC|hazard ratio|HR\s*[<>=]|non-significant|'
        r'outrank|exceed|fall below|fail(?:ed)? to replicate|crossing 0|reversed|opposite direction)',
        re.IGNORECASE)
    COMPARATORS = re.compile(r'[<>=]|greater than|less than|lower|higher|outperform|underperform', re.IGNORECASE)
    HEDGE_ONLY = re.compile(
        r'^\s*(if|when)\s+(the\s+)?(results?|findings?|data)\s+(do(es)?n\'?t|fail(s)?)\s+'
        r'(support|hold|replicate)\s*\.?\s*$', re.IGNORECASE)

    def tokenize(s):
        return set(re.findall(r'[a-zA-Z0-9]+', s.lower()))

    per_claim = []
    seen_criteria_texts = []
    for c in claims:
        crit = (c.get('falsification_criteria') or '').strip()
        stmt = (c.get('statement') or '').strip()

        if not crit:
            per_claim.append({'id': c.get('id'), 'score': 0.0, 'reason': 'missing falsification criteria'})
            continue

        length_ok = len(crit.split()) >= 8
        has_operational_marker = bool(OPERATIONAL_MARKERS.search(crit))
        has_comparator = bool(COMPARATORS.search(crit))
        is_pure_hedge = bool(HEDGE_ONLY.match(crit))

        stmt_tokens = tokenize(stmt)
        crit_tokens = tokenize(crit)
        new_tokens = crit_tokens - stmt_tokens
        novelty_ratio = len(new_tokens) / max(1, len(crit_tokens))

        score = 0.0
        if length_ok:
            score += 0.25
        if has_operational_marker:
            score += 0.35
        if has_comparator:
            score += 0.15
        if novelty_ratio > 0.3:
            score += 0.25
        if is_pure_hedge:
            score = min(score, 0.1)  # circular hedge disqualifies regardless of other signals

        per_claim.append({'id': c.get('id'), 'score': round(score, 3)})
        seen_criteria_texts.append(crit)

    # boilerplate detection: identical/near-identical criteria reused across claims
    dup_penalty = 0.0
    n = len(seen_criteria_texts)
    if n >= 2:
        pair_sims = [SequenceMatcher(None, seen_criteria_texts[i], seen_criteria_texts[j]).ratio()
                     for i in range(n) for j in range(i + 1, n)]
        avg_sim = sum(pair_sims) / len(pair_sims)
        if avg_sim > 0.6:
            dup_penalty = (avg_sim - 0.6) / 0.4

    raw_scores = [pc['score'] for pc in per_claim]
    aggregate = (sum(raw_scores) / len(raw_scores)) * (1 - 0.5 * dup_penalty) if raw_scores else 0.0
    return {'per_claim': per_claim, 'boilerplate_penalty': round(dup_penalty, 3),
            'aggregate_score': round(aggregate, 3)}
```

**What the function does & why**

Per claim, it rewards: enough length to state a real condition, presence of quantitative/statistical
operators (thresholds, CIs, "non-significant", named comparators), and genuine lexical novelty
relative to the Statement (i.e., the criterion introduces a *new* checkable condition rather than
just negating the Statement's own words). A criterion matching the pure-hedge regex ("refuted if
the results don't support this") is capped near zero no matter what else is true of it. Across the
claim set, it also measures pairwise text similarity between all criteria; if they're all nearly
identical, that's evidence of a mechanically-filled field rather than per-claim reasoning, and the
whole artifact's aggregate is discounted.

**Why it's hard to Goodhart**

Padding the criteria with numbers doesn't help unless the numbers also introduce genuine novelty
relative to the Statement — a criterion that just repeats the Statement's own cited value ("refuted
if 0.859 were wrong") scores low on novelty even though it contains a digit. Making every criterion
long and elaborate to avoid the length/marker penalties raises the boilerplate-similarity risk if
done via a fixed template, and lowers novelty if it's the same clause parametrized without new
comparators. To game this fully, the compiler would have to write genuinely distinct, genuinely
operational rejection conditions for each claim — which is exactly what good falsifiability requires.

---

## Metric 2: Grounding Fidelity & Precision Integrity (GFPI)

**How it signals good science**

The compiler's own grounding discipline (Rule 16) requires every load-bearing number in a
Statement to have a `Sources` entry with a verbatim quote, tagged `[input]`/`[result]`, and copied
at full precision (never rounded). This is the mechanism by which a claim is actually falsifiable
by a third party: a reader can go to the cited locator and verify the number appears exactly as
written. A metric computing directly over this field structure — numeric coverage, quote validity,
and precision fidelity — measures whether the claim's central assertions are checkable at all, as
opposed to narratively plausible. Tag discipline (`[input]`/`[result]`) is retained only as a small
compliance floor, not a rewarded dimension, per stage-1 feedback that it was close to free surface
credit for every well-formed entry.

**Compute function**

```python
import re

def grounding_fidelity_precision(claims):
    """
    claims: list of dicts with:
      'statement': str
      'sources': list of dicts: {'value': str, 'ref': str, 'locator': str,
                                  'quote': str or None, 'tag': 'input'|'result'|None}
    """
    NUM_RE = re.compile(r'\d+\.?\d*%?')

    per_claim = []
    for c in claims:
        stmt = c.get('statement') or ''
        sources = c.get('sources') or []
        stmt_numbers = NUM_RE.findall(stmt)

        if not stmt_numbers:
            # A "falsifiable, quantitative" claim with zero numbers in its own Statement is
            # itself penalized here, not exempted -- it means there is nothing concrete to check.
            per_claim.append({'id': c.get('id'), 'score': 0.2, 'reason': 'no quantitative content to ground'})
            continue

        if not sources:
            per_claim.append({'id': c.get('id'), 'score': 0.0, 'reason': 'no Sources entries at all'})
            continue

        source_values = [s.get('value', '') for s in sources]
        covered = sum(1 for num in stmt_numbers if any(num in sv for sv in source_values))
        coverage = covered / len(stmt_numbers)

        valid_quotes = 0
        precision_matches = 0
        untagged = 0
        for s in sources:
            quote = (s.get('quote') or '').strip()
            has_locator = bool((s.get('ref') or '').strip()) and bool((s.get('locator') or '').strip())
            is_pending = quote.lower().startswith('[pending')
            is_real_quote = bool(quote) and not is_pending
            if has_locator and is_real_quote:
                valid_quotes += 1
                if s.get('value', '') in quote:
                    precision_matches += 1
            if s.get('tag') not in ('input', 'result'):
                untagged += 1

        validity_ratio = valid_quotes / len(sources)
        precision_ratio = precision_matches / len(sources)
        untagged_ratio = untagged / len(sources)

        # Tag discipline is basic field-population, not scientific content (stage-1: "near-free
        # surface points"). It is no longer a rewarded dimension -- it survives only as a small,
        # capped compliance-floor deduction, so fully-untagged sources still cost something
        # without letting tag hygiene alone buy real points the way it could before.
        tag_floor_penalty = 0.05 * untagged_ratio

        score = 0.40 * coverage + 0.35 * validity_ratio + 0.25 * precision_ratio - tag_floor_penalty
        score = max(0.0, score)
        per_claim.append({'id': c.get('id'), 'score': round(score, 3),
                           'coverage': round(coverage, 2), 'validity_ratio': round(validity_ratio, 2),
                           'precision_ratio': round(precision_ratio, 2),
                           'tag_floor_penalty': round(tag_floor_penalty, 3)})

    scores = [pc['score'] for pc in per_claim]
    aggregate = sum(scores) / len(scores) if scores else 0.0
    return {'per_claim': per_claim, 'aggregate_score': round(aggregate, 3)}
```

**What the function does & why**

For each claim it extracts every numeric token in the Statement and checks it has a matching
`Sources` entry (coverage). Independently, it checks that each `Sources` entry actually has a
non-empty locator *and* a real quote — not a bare path, and not a `[pending: ...]` placeholder,
both of which the shape doc calls out as the most common real-world defects (validity). It then
checks that the exact value string appears inside the quoted text (precision — catching silent
rounding or paraphrase). Claims with no numbers at all, or no sources at all, are scored low
rather than skipped, per the hard constraint — an unquantified "falsifiable" claim or an
ungrounded claim is exactly the failure mode this metric exists to catch. Missing `[input]`/
`[result]` tags now only ever *subtract*, in a small capped amount, rather than adding to the
score — this closes the "reward field-population" loophole while keeping the check's diagnostic
value.

**Why it's hard to Goodhart**

Inflating `Sources` with entries that don't correspond to any number in the Statement doesn't raise
coverage (coverage is computed from the Statement's numbers outward, not the source list inward).
Copying the Statement's number into a fabricated "quote" without a real locator/ref still fails
validity. Rounding a source's value relative to the Statement's stated precision (or vice versa)
fails the exact-substring precision check even when the number is "close enough" to a human skim.
Since tags no longer earn points, there is no way to raise the score by populating `[input]`/
`[result]` tags without also doing the coverage/validity/precision work — the only way to score well
is to have already done the actual work: quote the true source text at the same precision as the
claim, for every number the claim leans on.

---

## Metric 3: Evidentiary Independence / Proof Triangulation

**How it signals good science**

`Proof` links a claim to one or more `E##` experiment IDs. A claim resting on a single experiment
is more fragile than one triangulated across independent runs/analyses — and a claim set where
many nominally distinct claims are all secretly `Proof: [E01]` is evidence that the paper's entire
apparent breadth reduces to one dataset or one run, re-described many times. This metric rewards
per-claim multiplicity of independent evidence and separately penalizes artifact-level "evidence
monoculture" — and now additionally refuses to count multiplicity that is manufactured purely by
splitting one experiment's ID string into several labels.

**Compute function**

```python
import re
from collections import Counter, defaultdict

def evidentiary_triangulation(claims):
    """
    claims: list of dicts with:
      'proof': list[str] of experiment ids (e.g. ['E01','E02']), [] if missing/absent.
      'sources': list of dicts (as in Metric 2) -- used to detect and defeat ID-splitting.
    """
    SPLIT_SUFFIX = re.compile(r'^([A-Za-z]+\d+)[a-z]$')

    def canonical(eid):
        eid = (eid or '').strip()
        m = SPLIT_SUFFIX.match(eid)
        return m.group(1) if m else eid

    # Pool, for each canonical experiment id, the set of Sources[*].ref evidence files claimed
    # alongside it anywhere in the artifact -- the closest available proxy for "what evidence
    # actually backs this experiment id."
    canon_to_refs = defaultdict(set)
    for c in claims:
        proof = c.get('proof') or []
        refs = {(s.get('ref') or '').strip() for s in (c.get('sources') or []) if (s.get('ref') or '').strip()}
        for eid in proof:
            canon_to_refs[canonical(eid)].update(refs)

    # If two DIFFERENT canonical ids end up backed by an identical, non-empty ref-set, they are
    # almost certainly the same underlying evidence re-labeled -- collapse them into one cluster
    # so multiplicity can't be farmed by splitting an ID string alone.
    refset_to_canon = {}
    canon_to_cluster = {}
    for canon, refs in canon_to_refs.items():
        key = frozenset(refs)
        if key and key in refset_to_canon:
            canon_to_cluster[canon] = refset_to_canon[key]
        else:
            if key:
                refset_to_canon[key] = canon
            canon_to_cluster[canon] = canon

    def cluster_id(eid):
        c = canonical(eid)
        return canon_to_cluster.get(c, c)

    per_claim = []
    all_cluster_ids = []
    suspicious_splits = set()
    for c in claims:
        proof = c.get('proof') or []
        if not proof:
            per_claim.append({'id': c.get('id'), 'score': 0.0, 'n_experiments': 0})
            continue
        raw_n = len(set(proof))
        clusters = {cluster_id(eid) for eid in proof}
        n = len(clusters)
        if n < raw_n:
            suspicious_splits.add(c.get('id'))
        score = min(1.0, 0.3 + 0.35 * (n - 1))
        per_claim.append({'id': c.get('id'), 'score': round(score, 3),
                           'n_experiments': n, 'n_raw_proof_ids': raw_n})
        all_cluster_ids.extend(clusters)

    counts = Counter(all_cluster_ids)
    total_refs = sum(counts.values())
    if total_refs == 0:
        monoculture_penalty = 1.0
    else:
        top_share = max(counts.values()) / total_refs
        # penalty grows only once one experiment (cluster) accounts for >50% of all proof references
        monoculture_penalty = max(0.0, (top_share - 0.5) / 0.5)

    base_scores = [pc['score'] for pc in per_claim]
    base_avg = sum(base_scores) / len(base_scores) if base_scores else 0.0
    # extra penalty for any claim whose apparent multiplicity depended on IDs that collapsed
    # under canonicalization/ref-overlap -- catches split-farming even in the rare case it
    # doesn't move the monoculture share much.
    split_penalty = 0.15 * (len(suspicious_splits) / max(1, len(claims)))
    aggregate = base_avg * (1 - 0.6 * monoculture_penalty) * (1 - split_penalty)
    return {'per_claim': per_claim, 'monoculture_penalty': round(monoculture_penalty, 3),
            'suspicious_id_splits': sorted(suspicious_splits),
            'aggregate_score': round(aggregate, 3)}
```

**What the function does & why**

Per claim, it counts distinct experiment *clusters* — not raw ID strings — in `Proof`, scoring
multiplicity with diminishing returns (going from 1→2 independent experiments matters much more
than 3→4). IDs are first canonicalized to strip a trailing single-letter split suffix
(`E01a`/`E01b` → `E01`), then further collapsed if two different canonical IDs are backed, across
the whole claim set, by an identical set of `Sources[*].ref` evidence files — the same underlying
evidence cited under two different experiment labels. Claims with an empty `Proof` list score
zero — not skipped — since `Proof` is a mandatory field. At the artifact level, it tallies how
concentrated all `Proof` cluster references are; if one experiment cluster underlies the
overwhelming majority of every claim's evidence, the aggregate is discounted. A separate flat
penalty applies proportional to how many claims' multiplicity scores depended on a split that
later collapsed.

**Why it's hard to Goodhart**

Citing extra experiment IDs in `Proof` to inflate a claim's own multiplicity score directly worsens
the monoculture check if those extra IDs are the *same* handful of experiments (or clusters) reused
everywhere. Splitting one experiment into `E01a`/`E01b` — the loophole flagged in stage 1 — no
longer inflates the count at all: the string-canonicalization catches the common case, and the
ref-overlap collapse catches a split that avoids the naming pattern but still reuses the same
evidence file(s). To score well on both the per-claim and artifact-level halves simultaneously, a
compiler needs claims that are actually backed by genuinely different experiments pointing to
genuinely different evidence, spread across the claim set — precisely the underlying research
practice this metric is a proxy for.

---

## Metric 4: Anchor Fragility Index

**How it signals good science**

`Dependencies` forms a graph of which claims lean on which other claims. Good science distributes
epistemic risk across independently-checkable claims; a paper where most of its claims all cascade
from one "anchor" claim (C01) means the entire finding is only as strong as that single anchor. This
metric builds the dependency graph, computes each claim's *reliance share* — now the full
transitive closure of everything that depends on it, directly or through a chain, not just its
immediate dependents — weights that by the anchor's own local grounding strength, and separately
treats a dependency cycle as a severe structural defect.

**Compute function**

```python
def anchor_fragility_index(claims):
    """
    claims: list of dicts with:
      'id': str (e.g. 'C01')
      'dependencies': list[str] of claim ids, [] for 'none'
      'status': str ('hypothesis'|'supported'|'refuted', possibly with parenthetical qualifier)
      'sources': list of dicts (as in Metric 2) -- used for a lightweight own-strength check
    """
    ids = [c['id'] for c in claims]
    dep_map = {c['id']: (c.get('dependencies') or []) for c in claims}
    dependents = {cid: [] for cid in ids}
    for cid, deps in dep_map.items():
        for d in deps:
            if d in dependents:
                dependents[d].append(cid)
            # a dependency pointing to a nonexistent claim id contributes no resolvable
            # support and is implicitly a defect in the dependency graph itself.

    def has_cycle():
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {cid: WHITE for cid in ids}
        def visit(u):
            color[u] = GRAY
            for v in dep_map.get(u, []):
                if v not in color:
                    continue
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and visit(v):
                    return True
            color[u] = BLACK
            return False
        return any(color[cid] == WHITE and visit(cid) for cid in ids)

    cycle_penalty = 0.5 if has_cycle() else 0.0

    # Transitive reliance: for each claim, find every OTHER claim that depends on it directly
    # or through a chain (C05->C04->C03->C02->C01 means C01's transitive dependents include
    # C02..C05, not just its one direct dependent C02, since all of them fail if C01 does).
    # A `seen` set stops re-traversal so a (separately-penalized) cycle can't loop forever.
    def transitive_dependents(root):
        seen = set()
        frontier = list(dependents.get(root, []))
        while frontier:
            node = frontier.pop()
            if node in seen or node == root:
                continue
            seen.add(node)
            frontier.extend(dependents.get(node, []))
        return seen

    def own_strength(c):
        sources = c.get('sources') or []
        if not sources:
            src_strength = 0.0
        else:
            real_quotes = sum(1 for s in sources
                               if (s.get('quote') or '').strip()
                               and not (s.get('quote') or '').lower().startswith('[pending'))
            src_strength = real_quotes / len(sources)
        status = (c.get('status') or '').lower()
        status_strength = 1.0 if status.startswith('supported') else (0.5 if status.startswith('hypothesis') else 0.3)
        if '(' in status:  # a parenthetical qualifier flags an acknowledged limitation
            status_strength *= 0.7
        return 0.6 * src_strength + 0.4 * status_strength

    strengths = {c['id']: own_strength(c) for c in claims}
    n_claims = max(1, len(claims))
    denom = max(1, n_claims - 1)  # reliance share = fraction of every OTHER claim relying on this one

    per_claim_risk = []
    for cid in ids:
        trans = transitive_dependents(cid)
        reliance_share = len(trans) / denom
        fragility = 1.0 - strengths[cid]
        risk = reliance_share * fragility
        per_claim_risk.append({'id': cid, 'n_direct_dependents': len(dependents[cid]),
                                'n_transitive_dependents': len(trans),
                                'own_strength': round(strengths[cid], 3),
                                'risk_contribution': round(risk, 3)})

    total_risk = sum(r['risk_contribution'] for r in per_claim_risk)
    aggregate_fragility = min(1.0, total_risk)
    aggregate_score = max(0.0, 1.0 - aggregate_fragility - cycle_penalty)
    return {'per_claim_risk': per_claim_risk, 'cycle_penalty': cycle_penalty,
            'aggregate_score': round(aggregate_score, 3)}
```

**What the function does & why**

It inverts the dependency edges and walks the full transitive closure to find, for each claim,
every other claim that ultimately rests on it — not just its immediate dependents — so a claim
buried at the root of a long chain is correctly scored as carrying the whole chain's reliance,
closing the stage-1 gap where a long transitive chain understated an anchor's real load. It
computes a cheap, local strength score per claim from fields already required elsewhere (real,
non-pending source quotes; a `Status` that isn't hedged or merely a `hypothesis`). It then
multiplies reliance share by *weakness* (`1 - strength`) so that a heavily-depended-upon claim with
strong grounding contributes little risk, while a heavily-depended-upon claim that is itself thin
contributes a lot. A dependency cycle is scored as an outright structural defect.

**Why it's hard to Goodhart**

Removing `Dependencies` links to hide an anchor's fragility just relocates claims to look
independent, but independent claims that are each individually thin score badly on their own local
`own_strength`, and the paper loses the (legitimate) credit a real, well-supported dependency chain
would earn. Conversely, propping up the anchor's local strength (real quotes, unhedged status)
without addressing the rest of the paper's actual soundness raises the score for the right reason —
it means the single load-bearing claim really is well grounded. Because reliance is now transitive,
restructuring a long chain to look shallower (e.g., making every claim depend directly on the root
instead of on its immediate predecessor) doesn't change the anchor's transitive-dependent count at
all, so that particular restructuring buys nothing. Gaming this metric in isolation converges on the
two only escape routes that are themselves marks of good practice: distribute claims' independence
for real, or make the anchor genuinely solid.

---

## Metric 5: Epistemic Candor / Status Diversity

**How it signals good science**

The shape doc itself notes `Status` skews heavily toward `supported` because compilers extract what
papers report as findings. But a multi-claim empirical paper that is *100% supported* — zero
`refuted`, zero `hypothesis`, no hedged qualifiers — over many claims is a red flag: genuine
empirical work almost always turns up at least one ablation that didn't help, a secondary endpoint
that missed, or a stated hypothesis not yet resolved. This metric rewards the presence of credible
non-`supported` statuses and penalizes both status monoculture and any attempt to game the metric by
padding in a throwaway, weakly-grounded "refuted" claim just to look diverse.

**Compute function**

```python
from collections import Counter

def epistemic_candor_status_diversity(claims):
    """
    claims: list of dicts with 'status': str (e.g. 'supported', 'refuted', 'hypothesis',
      or 'supported (interpretation-limited by ...)'), and 'sources' as in Metric 2.
    """
    n = len(claims)
    if n == 0:
        return {'aggregate_score': 0.0, 'reason': 'no claims at all'}

    def base_status(s):
        s = (s or '').strip().lower()
        for tag in ('supported', 'refuted', 'hypothesis'):
            if s.startswith(tag):
                return tag
        return 'unknown'

    def has_qualifier(s):
        return '(' in (s or '')

    statuses = [base_status(c.get('status')) for c in claims]
    counts = Counter(statuses)
    n_nonsupported = counts.get('refuted', 0) + counts.get('hypothesis', 0)
    n_unknown = counts.get('unknown', 0)

    diversity_fraction = n_nonsupported / n
    # more claims => a flat 100%-supported set is more suspicious, not equally plausible
    expected_min_diversity = 0.0 if n <= 2 else min(0.35, 0.05 * (n - 2))
    shortfall = max(0.0, expected_min_diversity - diversity_fraction)

    qualifier_fraction = sum(1 for c in claims if has_qualifier(c.get('status'))) / n

    # anti-gaming: a padded-in "refuted"/"hypothesis" claim only counts if it's as
    # well-grounded as any other claim -- a token throwaway claim earns nothing
    credible_nonsupported = 0
    for c in claims:
        if base_status(c.get('status')) in ('refuted', 'hypothesis'):
            sources = c.get('sources') or []
            real = sum(1 for s in sources if (s.get('quote') or '').strip()
                       and not (s.get('quote') or '').lower().startswith('[pending'))
            if sources and real / len(sources) >= 0.5:
                credible_nonsupported += 1
    credible_diversity_fraction = credible_nonsupported / n

    score = (0.55 * min(1.0, credible_diversity_fraction / 0.25)
             + 0.20 * qualifier_fraction
             - 0.5 * shortfall
             - 0.3 * (n_unknown / n))
    score = max(0.0, min(1.0, score))

    return {'n_claims': n, 'status_counts': dict(counts),
            'diversity_fraction': round(diversity_fraction, 3),
            'credible_diversity_fraction': round(credible_diversity_fraction, 3),
            'qualifier_fraction': round(qualifier_fraction, 3),
            'malformed_status_penalty': round(n_unknown / n, 3),
            'aggregate_score': round(score, 3)}
```

**What the function does & why**

It classifies every claim's `Status` into `supported` / `refuted` / `hypothesis` / `unknown`
(malformed field — itself penalized). It computes what fraction of claims are non-`supported`, and
compares that against an *expected minimum* that scales up with claim count — a larger claim set
sitting at 0% non-`supported` is treated as more suspicious than a 2-claim set. It gives partial
credit for hedged `supported (...)` qualifiers, which are themselves a form of candor. Crucially, it
only counts a `refuted`/`hypothesis` claim toward the diversity signal if that claim is *itself*
adequately sourced — a compiler cannot game this by tacking on one cheap, unsupported "refuted"
claim just to break the monoculture.

**Why it's hard to Goodhart**

The obvious cheap attack — add a filler `refuted` or `hypothesis` claim to escape the all-supported
penalty — is blocked by the credibility filter: that filler claim must carry real, quoted sources
just like every other claim, which costs exactly the same compiler effort as grounding a real claim
properly. The qualifier bonus can't be farmed by hedging every single claim, either, since the
`shortfall` penalty is computed independently from actual status diversity, not qualifier count — a
paper that hedges everything but refutes nothing still pays the shortfall penalty.

---

## Metric 6: Evidence/Interpretation Separation & Editorial-Leak Detection

**How it signals good science**

`Evidence basis` is supposed to state exactly what the cited evidence directly shows; `Interpretation`
is an explicitly optional field for the authors' broader synthesis, kept *separate* so a downstream
reader can tell "what was measured" from "what someone concluded from it." The shape doc names two
concrete failure modes: `Interpretation` collapsing into `Evidence basis` (no real separation), and
an evaluative/editorializing clause (e.g. "effectively obsolete") getting smuggled into a claim as if
it were as grounded as the measured ranking next to it — the che26 `C08` case flagged in its own
review with `context_match: false`. This metric checks both directly against the fields that
already exist, closing the one blind spot named against this proposal at stage 1.

**Compute function**

```python
import re

def evidence_interpretation_separation(claims):
    """
    claims: list of dicts with:
      'statement': str
      'evidence_basis': str  (required field; '' if missing/absent)
      'interpretation': str  (optional; '' if absent -- absence alone is never penalized,
                              only unsourced content when present)
      'sources': list of dicts (as in Metric 2) -- quotes are checked for grounding
    """
    # Deliberately broad rather than a small closed list: explicit evaluative/editorializing
    # vocabulary plus comparative/superlative morphology, so a compiler can't dodge the whole
    # check by picking one synonym not on a hand-curated list. Coverage is necessarily partial --
    # no fixed pattern catches every phrasing -- so what matters is that every match caught IS
    # checked against the claim's own Sources quotes before being penalized: the check never
    # falsely dings language the cited source itself actually used.
    EVAL_WORDS = re.compile(
        r'\b(obsolete|superior|inferior|groundbreaking|novel|unprecedented|dramatic(?:ally)?|'
        r'remarkable|compelling|definitive(?:ly)?|robust(?:ly)?|clear(?:ly)?|obvious(?:ly)?|'
        r'arguably|notably|essentially|effectively|substantial(?:ly)?|striking(?:ly)?|'
        r'powerful(?:ly)?|best|worst|breakthrough|revolutionary)\b', re.IGNORECASE)
    COMPARATIVE_MORPH = re.compile(r'\b([a-z]{4,}er|[a-z]{4,}est)\b', re.IGNORECASE)
    MORPH_STOPLIST = {'other', 'number', 'after', 'matter', 'later', 'cluster', 'parameter',
                       'whether', 'together', 'either', 'under', 'consider', 'interest',
                       'water', 'order', 'proper', 'lower', 'upper', 'former', 'latter',
                       'test', 'rest'}

    def find_evaluative(text):
        text = text or ''
        found = set(m.group(0).lower() for m in EVAL_WORDS.finditer(text))
        for m in COMPARATIVE_MORPH.finditer(text):
            w = m.group(0).lower()
            if w not in MORPH_STOPLIST:
                found.add(w)
        return found

    def tokenize(s):
        return set(re.findall(r'[a-zA-Z0-9]+', (s or '').lower()))

    per_claim = []
    for c in claims:
        stmt = c.get('statement') or ''
        eb = c.get('evidence_basis') or ''
        interp = (c.get('interpretation') or '').strip()
        sources = c.get('sources') or []
        quote_text = ' '.join((s.get('quote') or '') for s in sources).lower()

        if not eb.strip():
            # Evidence basis is a mandatory field per the shape doc; empty is a real defect.
            per_claim.append({'id': c.get('id'), 'score': 0.0, 'reason': 'missing evidence basis'})
            continue

        # 1. Editorial-leak check: evaluative language planted in Evidence basis (or the
        # Statement) is only legitimate if the source material itself used that language --
        # otherwise it is the compiler's own gloss smuggled in as if it were a measured fact.
        eb_matches = find_evaluative(eb)
        stmt_matches = find_evaluative(stmt)
        ungrounded_eb = [w for w in eb_matches if w not in quote_text]
        ungrounded_stmt = [w for w in stmt_matches if w not in quote_text]
        leak_count = len(ungrounded_eb) + len(ungrounded_stmt)
        leak_penalty = min(0.6, 0.2 * leak_count)

        # 2. Collapse check: when Interpretation is present, it should do separate synthesis
        # work, not restate Evidence basis in slightly different words. High token overlap
        # between the two fields means the "broader synthesis" field adds no new content.
        if interp:
            eb_tok, interp_tok = tokenize(eb), tokenize(interp)
            union = eb_tok | interp_tok
            jaccard = len(eb_tok & interp_tok) / len(union) if union else 0.0
            collapse_penalty = max(0.0, (jaccard - 0.5) / 0.5) * 0.4
            has_interp = True
        else:
            # Interpretation is documented as optional -- absence alone is not a defect.
            collapse_penalty = 0.0
            has_interp = False

        score = max(0.0, 1.0 - leak_penalty - collapse_penalty)
        per_claim.append({'id': c.get('id'), 'score': round(score, 3),
                           'ungrounded_evidence_basis_terms': sorted(ungrounded_eb),
                           'ungrounded_statement_terms': sorted(ungrounded_stmt),
                           'has_interpretation': has_interp,
                           'collapse_penalty': round(collapse_penalty, 3)})

    scores = [pc['score'] for pc in per_claim]
    aggregate = sum(scores) / len(scores) if scores else 0.0
    return {'per_claim': per_claim, 'aggregate_score': round(aggregate, 3)}
```

**What the function does & why**

For each claim, it scans `Evidence basis` and `Statement` — the fields that are supposed to report
only what was directly measured — for evaluative/editorializing language, using both an explicit
vocabulary and a comparative/superlative morphology pattern so it isn't limited to one hand-picked
word list. Every match found is then checked against the concatenated text of the claim's own
`Sources` quotes: if the source material itself used that word, reporting it is faithful, not
editorializing, and it is not penalized; if it appears nowhere in any quote, it is the compiler's
own unsourced gloss dressed up as an observed fact, and it costs points. Separately, when
`Interpretation` is present, its token overlap with `Evidence basis` is measured — Interpretation is
supposed to add a *different*, broader reading, and heavy overlap means it is adding nothing.
Absence of `Interpretation` is never penalized on its own, since the shape doc marks it explicitly
optional; only unsourced content or non-separation, when the field *is* filled in with something,
counts against the score.

**Why it's hard to Goodhart**

Removing evaluative language entirely from `Evidence basis`/`Statement` to dodge the leak check is
not gaming — it is exactly the compliant behavior the metric wants (objective reporting belongs
there; editorializing, if any, belongs in `Interpretation`, clearly separated). Swapping in a
synonym not on the fixed vocabulary can dodge detection, but only by accident of the pattern's
coverage, not by making the claim more honest — and if that synonym happens to appear in the
source's own quote (because the compiler is being faithful), it was never going to be penalized
anyway, so there is no actual incentive to hunt for undetected synonyms rather than just being
accurate. The collapse check has a real, acknowledged limit: paraphrasing `Interpretation` with
enough synonyms could lower raw token-Jaccard while still adding no real content. This is not fully
closed by this metric alone, but the effort required to paraphrase convincingly is comparable to
writing a genuinely separate synthesis, and any editorializing language introduced in that rewrite
still has to clear the leak check against `Sources` quotes — so the two checks inside this one
metric already pull against a lazy single-move exploit, and it interacts with the field-level
checks in the metrics below.

---

## Joint hardness to Goodhart

Each metric rewards a different, structurally distinct kind of honesty: FOS rewards precise
*rejection conditions*, GFPI rewards *traceable numbers*, Triangulation rewards *independent,
non-duplicated evidence*, Anchor Fragility rewards *distributed structural risk* (now correctly
scored along full dependency chains, not just direct edges), Status Diversity rewards *reported
failure*, and Evidence/Interpretation Separation rewards *keeping measured fact apart from
unsourced gloss*. Gaming any one in isolation tends to actively damage at least one other:

- Padding `Falsification criteria` with template boilerplate to farm FOS's operational-marker
  check triggers FOS's own boilerplate-similarity penalty, and a criterion copied across claims
  without real per-claim content also tends to reuse the same numbers already in the Statement,
  which does nothing for GFPI's coverage (GFPI counts Statement→Source coverage, not
  Statement→criteria overlap).
- Citing more experiments per claim to inflate Triangulation, using the same small pool of
  experiment IDs (or splitting one ID into several labels), directly worsens Triangulation's own
  monoculture and split-detection penalties — and if those over-cited experiments are asserted
  without matching `Sources` entries, GFPI's coverage and validity ratios fall too, and Metric 6's
  leak check has less quote text to justify any evaluative language riding along with them.
- Restructuring `Dependencies` to hide a fragile anchor (breaking edges to look "independent")
  produces claims that are individually thin, which tanks GFPI (their own numeric grounding
  doesn't improve) and Anchor Fragility's own-strength term simultaneously; because reliance is
  now transitive, reshuffling a chain's shape to look shallower doesn't reduce the anchor's
  transitive-dependent count either — there is no edge-rewrite that raises the score without also
  improving real, checkable grounding.
- Adding a throwaway `refuted`/`hypothesis` claim to farm Status Diversity requires that claim to
  carry full `Sources` grounding to count at all, which means it also has to clear GFPI's coverage
  and validity bars — a free-riding filler claim is worthless under both metrics at once.
- Smuggling an unsourced evaluative gloss into `Evidence basis` to make a claim read as more
  impressive costs points under Metric 6's leak check directly, and if the compiler instead tries
  to "launder" that gloss by inventing a matching `Sources` quote to make it look grounded, that
  fabricated quote has to pass GFPI's validity/precision checks — the two metrics jointly close off
  both the honest-and-caught path and the fabricate-to-hide path.

The combination is jointly robust because the six metrics are keyed to different fields
(`Falsification criteria`, `Sources`, `Proof`, `Dependencies`, `Status`, and the
`Evidence basis`/`Interpretation` pair) that a compiler cannot manipulate independently:
coordinated fabrication across all six to fake "good science" converges on actually producing
well-grounded, well-tested, structurally distributed, candidly-reported, and honestly-separated
claims — i.e., the real thing.
