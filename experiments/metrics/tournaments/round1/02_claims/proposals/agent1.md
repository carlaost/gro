# Proposer 1 — Metrics over `logic/claims.md`

**Assumed parsed shape** (clean-room, derived only from `shapes/02_claims.md`). Every metric below
takes an `artifact` dict of this form:

```python
claim = {
    "id": "C01",                       # str, e.g. "C01"
    "statement": "...",                # str
    "status": "supported",             # str, base enum value ("hypothesis"|"supported"|"refuted"),
                                        # with any parenthetical qualifier stripped out separately
    "status_qualifier": None,          # str or None, e.g. "interpretation-limited by female sample size"
    "falsification_criteria": "...",   # str
    "proof": ["E01"],                  # list[str] experiment ref ids
    "evidence_basis": "...",           # str
    "interpretation": "...",           # str, "" if the field was omitted (it is spec-optional)
    "dependencies": [],                # list[str] claim ids; [] means the doc said "none"
    "dependencies_present": True,      # bool: whether the *field itself* existed in the block at all
    "sources": [                       # list[dict], one per grounding entry
        {"value": "0.859", "ref": "evidence/tables/table2.md",
         "locator": "Table 2, Outcome 1, Rank 1", "quote": "p217_MS (0.859)",
         "tag": "result", "pending": False},
    ],
    "tags": ["p-tau217", "..."],
}
artifact = {"claims": [claim, ...]}
```

Every metric below explicitly states what it does when a field it depends on is missing, empty, or
thin — per the hard constraint, that is always a score reduction, never a skip/N/A.

---

## Metric 1: Grounding Coverage & Quote Fidelity

**How it signals good science.** The shape doc calls `claims.md` the file where "numbers copied
exactly (never rounded)" in the Statement must each trace to a `Sources` entry carrying a *verbatim*
quote (Rule 16, "Grounding discipline"). A paper's claims are only as trustworthy as their traceability
back to a specific number in a specific place. A claim set where every load-bearing number can be
re-derived by a skeptical reader, with no bare paths and no unresolved `[pending: ...]` markers, is
direct, structural evidence of a rigorously compiled — and by extension rigorously reported —
underlying study. This is the most literal operationalization of "show your work."

**Compute function.**

```python
import re
import statistics

NUM_RE = re.compile(r'-?\d+\.?\d*\s*%?')

def grounding_coverage_fidelity(artifact):
    claims = artifact.get("claims", [])
    if not claims:
        return 0.0
    per_claim_scores = []
    for c in claims:
        statement = c.get("statement", "") or ""
        sources = c.get("sources", []) or []

        tokens = [t.strip() for t in NUM_RE.findall(statement) if t.strip()]
        if not tokens:
            # A "falsifiable claim" artifact whose Statement carries no numbers at all
            # is exactly the narrative-hedging the compiler is supposed to strip out.
            per_claim_scores.append(0.0)
            continue
        if not sources:
            # Numbers asserted, nothing behind them at all -> full penalty.
            per_claim_scores.append(0.0)
            continue

        source_values_blob = " ".join(s.get("value", "") or "" for s in sources)
        matched = sum(1 for t in tokens if t in source_values_blob)
        coverage = matched / len(tokens)

        broken = sum(
            1 for s in sources
            if s.get("pending", False) or not (s.get("quote") or "").strip()
        )
        fidelity = 1 - (broken / len(sources))

        per_claim_scores.append(coverage * fidelity)
    return round(statistics.mean(per_claim_scores), 4)
```

**What the function does & why.** For each claim it pulls every numeric token out of the `Statement`
(the load-bearing values the spec says must be copied exactly) and checks how many of them literally
appear among the claim's `Sources[*].value` fields — that's `coverage`. It separately checks what
fraction of `Sources` entries are broken: either flagged `pending` (source not actually opened) or
missing a verbatim `«quote»` (a bare path, which the shape doc says "must fail validation") — that's
`fidelity`. The two multiply, so a claim can't get a good score by having lots of matching-looking
values sourced through broken/pending entries, nor by having pristine entries that don't actually
cover the numbers it asserts. A Statement with zero numbers, or a claim with zero sources, is scored
at the floor (0.0) rather than excluded — per the hard constraint, thinness is a penalty, not a
skip.

**Why it's hard to Goodhart.** You cannot inflate this by padding `Sources` with irrelevant entries —
only entries whose `value` textually matches a number that actually appears in the Statement count
toward coverage, and each additional low-quality entry (bare/pending) drags fidelity down for the
whole claim. Faking coverage by copying the Statement's numbers verbatim into invented `Sources.value`
fields without a real matching `«quote»` is caught by the fidelity term, since a fabricated quote is
either detectably generic or, if scrutinized against the underlying evidence file (outside this
metric's scope, but within the compiler's Seal Level 1 check), fails independently. The metric rewards
only the joint condition of "asserted a specific number" AND "quoted its exact origin," which is
expensive to fake at scale across 5–8 claims.

---

## Metric 2: Falsifiability Operationality

**How it signals good science.** Popperian falsifiability is the field's own stated design intent for
this artifact — the whole point of `Falsification criteria` is to say what observation would disprove
the claim. But a criteria field can exist and still be vacuous ("if future research disagrees"). Good
science produces falsification criteria that are *operational*: they name a concrete comparator,
threshold, or statistical condition tied to the specific claim, not a generic disclaimer that could be
pasted onto any claim in any paper.

**Compute function.**

```python
import re
import statistics

NUM_RE = re.compile(r'-?\d+\.?\d*\s*%?')
CONDITIONAL_RE = re.compile(
    r'\b(if|unless|were|would|refuted if|non-significant|outranked|crossing|failed to)\b', re.I
)
VAGUE_PHRASES = [
    "future research", "future studies", "new evidence emerges", "experts disagree",
    "further work", "researchers find", "may not hold", "could be wrong", "if replicated",
]

def falsifiability_operationality(artifact):
    claims = artifact.get("claims", [])
    if not claims:
        return 0.0
    scores = []
    for c in claims:
        crit = (c.get("falsification_criteria") or "").strip()
        statement = c.get("statement", "") or ""
        if not crit:
            scores.append(0.0)
            continue

        has_number = bool(NUM_RE.search(crit))
        has_conditional = bool(CONDITIONAL_RE.search(crit))
        length_ok = len(crit.split()) >= 8

        stmt_tokens = set(re.findall(r'[A-Za-z][A-Za-z0-9_\-]{3,}', statement.lower()))
        crit_tokens = set(re.findall(r'[A-Za-z][A-Za-z0-9_\-]{3,}', crit.lower()))
        shares_entity = len(stmt_tokens & crit_tokens) > 0

        score = sum([has_number, has_conditional, length_ok, shares_entity]) / 4
        if any(p in crit.lower() for p in VAGUE_PHRASES):
            score *= 0.3  # generic boilerplate, heavily discounted even if it hit other checks
        scores.append(score)
    return round(statistics.mean(scores), 4)
```

**What the function does & why.** For each claim it scores the `Falsification criteria` text on four
independent operationality signals: does it contain a concrete number/threshold; does it use a real
conditional/comparative structure ("refuted if," "non-significant," "outranked"); is it long enough to
carry actual content (not a one-liner stub); and does it share a specific named entity/token with the
Statement it's supposed to falsify (proving it was written *for this claim*, not copy-pasted). It then
applies a hard discount if the text matches known generic-disclaimer phrasing, since such phrasing can
independently satisfy length/conditional checks while carrying zero operational content. A missing
`Falsification criteria` field scores 0, not N/A.

**Why it's hard to Goodhart.** A compiler could try to satisfy the surface checks with a formulaic
template ("Refuted if [X] is not observed at [N]"), but the entity-overlap check forces the template
to be re-populated per claim with real specifics from that claim's Statement, and the vague-phrase
discount specifically targets the class of maximally-reusable disclaimer text that would otherwise let
a template win cheaply. Because it composes four largely independent signals multiplicatively-in-effect
(via averaging then a further discount), gaming all four per claim, per template, across every claim in
the set is materially harder than writing one real falsification condition each time.

---

## Metric 3: Editorial Leakage (Evidence/Interpretation Separation)

**How it signals good science.** The shape doc itself names this exact failure mode as a known quality
defect: "`Interpretation` collapsing into `Evidence basis`... a quality defect the validation checklist
explicitly watches for," and gives a concrete example (che26 C08) of an authors' value-laden gloss
("effectively obsolete") getting smuggled into a claim as if it were an equally-grounded fact. Good
science keeps "what the data directly shows" strictly separate from "what we think it means" — good
compilation of good science should preserve that separation rather than erase it.

**Compute function.**

```python
import statistics

EVALUATIVE_LEXICON = [
    "obsolete", "groundbreaking", "revolutionary", "definitively", "proves", "proved",
    "clearly", "undoubtedly", "best", "worst", "superior", "inferior", "remarkable",
    "must", "should", "flawed", "unprecedented", "gold standard", "game-chang",
]

def editorial_leakage(artifact):
    claims = artifact.get("claims", [])
    if not claims:
        return 0.0
    scores = []
    for c in claims:
        statement = (c.get("statement") or "").lower()
        evidence = (c.get("evidence_basis") or "").lower()
        interpretation = (c.get("interpretation") or "").strip()
        sources = c.get("sources", []) or []
        quotes_blob = " ".join((s.get("quote") or "").lower() for s in sources)
        factual_text = statement + " " + evidence

        hits = [t for t in EVALUATIVE_LEXICON if t in factual_text]
        unsupported = [t for t in hits if t not in quotes_blob]
        leakage_ratio = (len(unsupported) / len(hits)) if hits else 0.0

        interpretation_present = 1.0 if interpretation else 0.0
        # 0.7 weight: unsupported evaluative language stated as fact is the core defect.
        # 0.3 weight: no cordoned-off Interpretation channel at all is a milder but real
        # penalty — an input the metric relies on that is simply absent.
        claim_score = 0.7 * (1 - leakage_ratio) + 0.3 * interpretation_present
        scores.append(claim_score)
    return round(statistics.mean(scores), 4)
```

**What the function does & why.** It scans `Statement` and `Evidence basis` — the two fields that are
supposed to be strictly factual — for a lexicon of evaluative/value-laden words. For each hit, it
checks whether that same word actually appears in a verbatim `Sources` quote (i.e., the paper's authors
really did say "obsolete," and it's quoted, not invented by the compiler) — if not, that's an
unsupported editorial claim leaking into a "just the facts" field. Separately, it checks whether an
`Interpretation` section exists at all to properly house any broader synthesis; its absence draws a
fixed penalty rather than being ignored, since a claim block with nowhere to legitimately put
evaluative language is more likely to leak it into Evidence basis, and because the metric treats
`Interpretation` as an input it depends on.

**Why it's hard to Goodhart.** Deleting all evaluative language from Statement/Evidence basis to avoid
the lexicon match is actually the *correct* behavior the metric wants — that is not gaming, that is
compliance. The only way to "cheat" would be to move genuinely-evaluative content into `Interpretation`
purely to dodge the lexicon scan while still keeping `Interpretation` non-empty; but that is exactly
the separation this metric is designed to reward, so the "workaround" and the desired behavior
coincide. Faking a supporting quote to launder an evaluative word past the `unsupported` check requires
fabricating a `«quote»`, which is independently punished by Metric 1's fidelity term if the quote isn't
real.

---

## Metric 4: Dependency Graph Integrity & Coherence

**How it signals good science.** The `Dependencies` field is where the artifact's authors model how
claims build on each other — "commonly reference an earlier 'anchor' claim... from several later
claims." Good science is cumulative and internally consistent: later, more specific claims should
rest coherently on earlier, established ones, dependency references should actually resolve, and a
claim should not casually inherit from a claim the compiler itself marked `refuted` without saying so.
A claim set that is either full of dangling references or a pile of totally disconnected one-off
assertions is weak evidence of a paper (or a compilation) that isn't actually building a coherent
argument.

**Compute function.**

```python
import statistics

def dependency_graph_integrity(artifact):
    claims = artifact.get("claims", [])
    if not claims:
        return 0.0
    ids = {c.get("id") for c in claims if c.get("id")}
    n = len(claims)
    scores = []
    connected_flags = []

    for c in claims:
        deps_present = c.get("dependencies_present", True)
        deps = c.get("dependencies", []) or []
        cid = c.get("id")

        if not deps_present:
            # The field itself is structurally absent from the block. The shape doc
            # requires ALL fields on every claim; this is a hard structural defect,
            # not a benign "none".
            scores.append(0.0)
            connected_flags.append(False)
            continue

        if not deps:
            # Valid explicit "none" -> acceptable, but contributes nothing to connectivity.
            scores.append(0.7)
            connected_flags.append(False)
            continue

        dangling = [d for d in deps if d not in ids or d == cid]
        valid = [d for d in deps if d in ids and d != cid]
        integrity = 1 - (len(dangling) / len(deps))

        status = (c.get("status") or "").split("(")[0].strip().lower()
        qualifier = c.get("status_qualifier") or ""
        incoherent = 0
        for d in valid:
            dep_claim = next((x for x in claims if x.get("id") == d), None)
            if not dep_claim:
                continue
            dep_status = (dep_claim.get("status") or "").split("(")[0].strip().lower()
            if status == "supported" and dep_status == "refuted" and not qualifier:
                incoherent += 1
        coherence = 1 - (incoherent / len(valid)) if valid else 1.0

        scores.append(0.5 * integrity + 0.5 * coherence)
        connected_flags.append(True)

    base = statistics.mean(scores)
    connectivity_rate = sum(connected_flags) / n
    if n >= 2 and connectivity_rate == 0.0:
        # Every claim is a disconnected island in a multi-claim artifact: presented
        # as an unordered pile of facts rather than a cumulative argument.
        base *= 0.6
    return round(base, 4)
```

**What the function does & why.** It builds the set of valid claim ids, then per claim: (a) treats a
structurally missing `Dependencies` field as an automatic floor score; (b) treats an explicit `none` as
acceptable-but-neutral; (c) for real dependency lists, checks referential integrity (do the referenced
ids actually exist, and does a claim not depend on itself), and status coherence (does a `supported`
claim quietly rest on a `refuted` one without any qualifier acknowledging that tension). It then
applies a corpus-level penalty if literally every claim is isolated — a red flag that the claims were
extracted as an unordered list rather than an argument with structure, contradicting the shape doc's
own stated typical pattern.

**Why it's hard to Goodhart.** Referencing more claims to look "well-connected" only helps if the
references are valid and status-coherent — inventing dependency links to boost connectivity
immediately risks either a dangling reference (if the id doesn't exist) or a coherence violation (if
it links to a claim with a conflicting status), both of which are actively penalized. The corpus-level
disconnection penalty can't be dodged by adding one token dependency somewhere, because it only fires
when connectivity is exactly zero — but going the other direction (a fully connected chain) is
constrained by the per-claim coherence check, so there's no free lunch in either direction.

---

## Metric 5: Confidence–Evidence Proportionality (anti–rubber-stamp)

**How it signals good science.** Good science calibrates confidence to evidence: a claim asserted with
maximal rhetorical certainty ("highest," "significantly," "obsolete") should be backed by
proportionally more experiments and sources than a modest, narrow claim. And, per the shape doc's own
observation that "`Status` skews heavily to `supported`... `hypothesis`/`refuted` appear for stated
ablations or explicitly disconfirmed prior expectations," a claim set that is **100% `supported`**
*and* thin on backing everywhere is a signature of either a paper that never tested anything that could
fail, or — more likely for this artifact — an incurious, rubber-stamp compilation that transcribed the
paper's own confidence without independently weighing it. Absence of any hedge/refutation, when
combined with thin evidence, is treated as active evidence of low quality, not a neutral default.

**Compute function.**

```python
import statistics

STRENGTH_WORDS = [
    "highest", "lowest", "all", "none", "significant", "significantly", "never",
    "always", "clearly", "obsolete", "best", "worst", "first", "only", "outperform",
    "superior",
]

def confidence_evidence_proportionality(artifact):
    claims = artifact.get("claims", [])
    if not claims:
        return 0.0
    per_claim, statuses, weights = [], [], []

    for c in claims:
        statement = (c.get("statement") or "").lower()
        status = (c.get("status") or "").split("(")[0].strip().lower()
        qualifier = c.get("status_qualifier") or ""
        statuses.append(status)

        strength_hits = sum(1 for w in STRENGTH_WORDS if w in statement)
        certainty = 1.0 if status == "supported" else (0.5 if status == "hypothesis" else 0.3)
        if status == "supported" and qualifier:
            certainty -= 0.15  # an honest hedge on a "supported" claim is good calibration
        strength_score = min(1.0, strength_hits / 3) * certainty

        proof = c.get("proof", []) or []
        sources = c.get("sources", []) or []
        distinct_files = {s.get("ref") for s in sources if s.get("ref")}
        weight = min(1.0, (len(proof) + len(sources) + len(distinct_files)) / 6)
        weights.append(weight)

        if strength_score == 0:
            per_claim.append(1.0)  # nothing strongly asserted, nothing to over-back
        else:
            per_claim.append(min(1.0, weight / strength_score))

    base = statistics.mean(per_claim)

    all_supported = all(s == "supported" for s in statuses)
    thin_everywhere = statistics.mean(weights) <= (1 / 6)
    if len(claims) >= 3 and all_supported and thin_everywhere:
        base *= 0.5

    return round(base, 4)
```

**What the function does & why.** Per claim, it scores rhetorical "strength" (superlative/absolute
words in the Statement, weighted up if `Status` is `supported` without a hedge, down slightly if a
qualifier is present) and "evidentiary weight" (how many distinct experiments, source entries, and
distinct evidence files back it). It then checks whether weight keeps pace with strength — a claim that
says "highest," "significantly," with total certainty but rests on one experiment and one source is
penalized as an overclaim; a modest claim needs less to be well-calibrated. At the corpus level, it
applies an extra penalty specifically for the pattern of *zero* non-`supported` statuses combined with
uniformly thin backing across ≥3 claims — treating that absence of any hedge as itself diagnostic of
low-quality (rubber-stamp) compilation rather than a neutral or good sign.

**Why it's hard to Goodhart.** Toning down rhetoric to dodge the strength penalty is fine — that's the
correct incentive (claim only as much as the evidence supports). Padding `Proof`/`Sources` to inflate
weight is constrained by Metric 1 (fabricated or irrelevant sources lower grounding fidelity there) and
by Metric 4 (irrelevant claim-level padding doesn't help this metric since weight is capped at 1.0 past
a modest threshold, so stuffing in a 6th, 7th, 8th source buys nothing further). Manufacturing a token
`hypothesis` or `refuted` claim purely to dodge the corpus-level rubber-stamp penalty requires that
claim to itself pass Metrics 1–4 (real numbers, real falsification criteria, real grounding, coherent
dependencies) — a fake hedge claim built just to game this metric is expensive and independently
exposed elsewhere.

---

## Why the combination is jointly hard to game

Each metric leans on a different, largely non-overlapping surface of the same artifact — numeric
traceability (M1), the specificity of stated falsification conditions (M2), the factual/interpretive
boundary (M3), the logical structure across claims (M4), and the calibration between asserted certainty
and evidentiary backing across the whole claim set (M5). Critically, the cheap ways to game any one of
them create real, correlated costs elsewhere: inventing sources to raise M1's coverage or M5's weight
introduces fabricated or mismatched quotes that M1's own fidelity term and M3's leakage term can catch;
writing generic falsification boilerplate to raise M2 fails M2's own vague-phrase and entity-overlap
checks and does nothing for M1 or M5; padding dependency links to look well-integrated for M4 risks
either dangling references or status incoherence that M4 itself penalizes, and manufacturing a token
"refuted" claim to dodge M5's rubber-stamp check only helps if that fabricated claim is itself well
constructed, which routes the cost right back through M1, M2, and M4. There is no single edit — adding
text, adding sources, adding a hedge — that improves the joint score without also having to satisfy the
underlying epistemic property (real numbers, real quotes, real falsification logic, real coherence,
real calibration) that the metric it targets was built to detect.
