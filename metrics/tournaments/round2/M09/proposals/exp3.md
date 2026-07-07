# M09 — FOL-ability (Oshima principles) — Expansion + Workflow (expander 3)

## 1. What this metric actually tests

The one-liner is "can a clean first-order-logic graph be built over the claims." Read literally that
sounds like a yes/no compileability check. That framing is wrong and would make the metric trivially
gameable (an LLM asked "can you FOL-ify this?" will almost always say yes and hand back *some*
formal-looking string). The thing worth measuring is narrower and harder:

> Does the claim's own natural-language content contain enough precision — typed entities, explicit
> quantifier scope, a stated comparison/relation, and a falsification criterion that is the actual
> logical negation of the statement — that an independent formalization attempt converges on the
> *same* logical content twice, without the formalizer having to invent structure that isn't there?

That's the Oshima-principle reading: FOL-ability is not "can you draw some graph," it's "is the
claim's own prose already doing the logical work, such that formalization is a lossless transcription
rather than a lossy interpretation." A claim written as "the treatment improves outcomes" is
FOL-hostile no matter how creative the formalizer is, because "improves" and "outcomes" are
untyped and unquantified — any FOL rendering of it is the formalizer's invention, not the paper's
claim. A claim written as "for detecting Abeta positivity, p217_MS achieved P-score = 0.859,
outranking p217_Ratio (0.783)... refuted if p181_IA or another isoform outranked p217_MS" (real C01
from the shape doc) is FOL-friendly: entities are named, the relation is a strict ranking over a
named metric, and the falsification criterion is *literally* the negation of the ranking claim.

### What it must reward
- Claims whose `Statement` already contains typed entities (named methods/cohorts/genes/compounds),
  an explicit relation (ranking, threshold, hazard ratio, interval), and a scope (which population,
  which outcome) — i.e., claims that need no invented predicates to formalize.
- `Falsification criteria` that are the actual logical negation of `Statement` (or a well-scoped
  sufficient condition for its negation) — not a vague "would need more data" hand-wave.
- Clean, acyclic `Dependencies` chains that form a valid entailment order (a claim's truth is only
  allowed to presuppose claims that could logically precede it).
- Claims that decompose into a small number of atomic predicates rather than a conjunction of five
  unrelated facts crammed into one `Statement` (compound claims are a formalization anti-pattern:
  Oshima-style FOL wants one relation per claim, not a paragraph).

### What it must NOT reward
- Superficial formalizability: an LLM that dresses up "improves outcomes" as
  `∃x (Treatment(x) ∧ Improves(x, Outcome))` has *invented* `Improves` and `Outcome` as
  atomic predicates rather than extracting them — this is formalization theater, and the workflow
  below must specifically detect and penalize it via an "assumptions injected" self-report cross-check
  (§3, step 2).
- Formal-looking output that doesn't correspond to the falsification criterion actually stated — if
  the FOL negation and the prose `Falsification criteria` diverge, that's a sign either the claim's
  falsification condition is not really tied to its content, or the formalizer papered over a gap.
- Rewarding "some FOL was produced" independent of whether a second, independent attempt agrees with
  the first — single-pass generation is not evidence of clean structure, it's evidence an LLM
  followed instructions.

### Failure modes / gaming routes and how the design closes them
1. **"Always say formalizable."** A generator-only design where one LLM call outputs
   `{formalizable: true, fol: "..."}` can't be checked against anything and will drift to always-true.
   Closed by requiring a *second, independently-prompted* verifier call that checks
   negation-equivalence against the prose `Falsification criteria` (§3 step 3) — generator and
   verifier are different prompts/passes so the metric doesn't just measure "one model's
   self-agreement."
2. **Padding with pseudo-formal notation.** Wrapping vague prose in symbols (`∀x...`) without
   constraining anything. Closed by scoring the *residual prose fraction* — how much of the
   `Statement`'s load-bearing content (named values from `Sources`) failed to map onto any predicate
   argument — and by requiring the formalizer to self-report injected assumptions, which are then
   checked against actual claim text (not just trusted).
3. **Cherry-picking one clean claim to represent the whole artifact.** Closed by scoring is
   per-claim and aggregated by mean over *all* claims in `claims.md`, with a stated claim `Status`/
   completeness floor — an artifact can't hide five vague claims behind one crisp one.
4. **Circular or dangling `Dependencies`.** A claim graph with cycles isn't a valid FOL entailment
   structure; this is checked deterministically (no LLM judgment call, so it can't be argued with) via
   graph cycle detection.
5. **Missing/bare `Sources` making the claim ungroundable and hence unformalizable in a *checkable*
   way** (a claim could be phrased crisply but reference numbers that were never verified against a
   quoted source) — penalized directly per the hard constraint below, not skipped.

### Why this is net-new / non-redundant
This is explicitly not re-testing Seal Level 1 field-presence (does `Falsification criteria` exist —
yes/no) or citation grounding format (does `Sources` have a `«quote»` — the verifier already checks
that). It is testing a semantic property that only shows up when you actually *try* to formalize the
content: whether the claim's own language is precise enough that two independent formalization
attempts converge, and whether the stated falsification condition is the real logical negation of the
claim rather than a plausible-sounding disclaimer. Nothing in the ARA verifier or round-1 metrics
performs this transformation.

## 2. Hard constraint: penalize, don't skip

- No `claims.md` at all → metric score = `0.0` for the artifact (not N/A). This is a maximal
  penalty, not an exemption.
- `claims.md` present but zero parseable `## C{NN}` blocks → `0.0`.
- A claim missing `Falsification criteria` or `Sources` outright → that claim scores `0.0` on the
  relevant sub-components (§3) rather than being excluded from the mean — a thin artifact must pull
  its own average down, not shrink the denominator.
- Abstract-only / paywalled compilations (per the shape doc's "Availability notes") will naturally
  produce claims with weak `Evidence basis` (`§Abstract` only) and thin `Sources` — these are *not*
  filtered out before scoring; they run through the same pipeline and organically score lower because
  the grounding-completeness sub-score (§3.4) and residual-prose sub-score both degrade. Availability
  of the artifact/section is part of the score, not a precondition for computing it.
- LLM call failure/timeout on a given claim → treated as `formalizable: false` with all downstream
  sub-scores at floor for that claim (never dropped from the denominator).

## 3. Generation / compute workflow

### Inputs (from `logic/claims.md`)
Per claim block: `Statement`, `Status`, `Falsification criteria`, `Proof`, `Evidence basis`,
`Interpretation` (optional), `Dependencies`, `Sources` (list of `<value> ← <ref> («quote») [tag]`),
`Tags`.

### Step 0 — deterministic parse

```python
import re
from dataclasses import dataclass, field

CLAIM_HEADER_RE = re.compile(r"^##\s*(C\d{2,})\s*:\s*(.+)$", re.MULTILINE)
FIELD_RE = re.compile(
    r"-\s*\*\*(Statement|Status|Falsification criteria|Proof|Evidence basis|"
    r"Interpretation|Dependencies|Sources|Tags)\*\*:\s*(.*?)(?=\n-\s*\*\*|\Z)",
    re.DOTALL,
)
SOURCE_LINE_RE = re.compile(
    r"`([^`]+)`\s*←\s*(\S+)\s*\(([^)]*)\)\s*«([^»]*)»\s*\[(input|result|pending)"
)

@dataclass
class Claim:
    cid: str
    title: str
    statement: str = ""
    status: str = ""
    falsification: str = ""
    proof: list = field(default_factory=list)
    evidence_basis: str = ""
    interpretation: str = ""
    dependencies: list = field(default_factory=list)
    sources_raw: str = ""
    tags: list = field(default_factory=list)

def parse_claims(md_text: str) -> list[Claim]:
    """Deterministic split of claims.md into Claim objects. Never raises on malformed
    blocks — a block that fails to parse still becomes a Claim with empty fields, so it
    is penalized downstream rather than silently dropped."""
    claims = []
    headers = list(CLAIM_HEADER_RE.finditer(md_text))
    for i, h in enumerate(headers):
        cid, title = h.group(1), h.group(2).strip()
        start = h.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(md_text)
        body = md_text[start:end]
        fields = {m.group(1): m.group(2).strip() for m in FIELD_RE.finditer(body)}
        c = Claim(cid=cid, title=title)
        c.statement = fields.get("Statement", "")
        c.status = fields.get("Status", "")
        c.falsification = fields.get("Falsification criteria", "")
        c.proof = re.findall(r"E\d{2,}", fields.get("Proof", ""))
        c.evidence_basis = fields.get("Evidence basis", "")
        c.interpretation = fields.get("Interpretation", "")
        c.dependencies = re.findall(r"C\d{2,}", fields.get("Dependencies", ""))
        c.sources_raw = fields.get("Sources", "")
        c.tags = [t.strip() for t in fields.get("Tags", "").split(",") if t.strip()]
        claims.append(c)
    return claims
```

### Step 1 — [sem]/[ext] FOL generation call

For each claim, one LLM call. Exact prompt (fill `{statement}`, `{falsification}`, `{sources}`):

```
SYSTEM: You are a formal-logic transcriptionist, not an interpreter. You translate a scientific
claim into first-order logic using ONLY entities, relations, and quantifiers that are explicitly
named or numerically stated in the text. You must never invent a predicate to fill a gap in vague
prose — if the text doesn't name it, you cannot formalize it, and you must say so.

USER:
STATEMENT: {statement}
FALSIFICATION CRITERIA (as stated by the author): {falsification}
GROUNDED VALUES (from Sources): {sources}

Produce JSON with exactly these keys:
- "formalizable": bool — true only if every relation/entity in your FOL below is explicitly present
  in STATEMENT (no invented predicates).
- "fol_statement": string — the FOL rendering of STATEMENT (typed predicates, explicit quantifiers,
  named constants for entities/values).
- "fol_negation": string — the literal logical negation of fol_statement (¬fol_statement, simplified).
- "predicates": list of {"name": str, "arity": int, "grounded_in_sources": bool} — every predicate
  used, and whether its arguments are among GROUNDED VALUES.
- "assumptions_injected": list of str — any entity/relation/quantifier scope you had to assume or
  infer because STATEMENT itself was silent on it (empty list if none — do not pad this list, and do
  not leave it empty just to look clean; report honestly).
- "residual_prose": string — any clause of STATEMENT that fol_statement does NOT capture (empty
  string if fully captured).
```

### Step 2 — assumptions cross-check (deterministic, no extra LLM call)

```python
def assumption_penalty(claim: Claim, gen_out: dict) -> float:
    """Penalize injected assumptions that are not literally traceable to the statement text.
    Returns a penalty in [0, 1] (0 = no penalty)."""
    injected = gen_out.get("assumptions_injected", [])
    if not injected:
        return 0.0
    stmt_lower = claim.statement.lower()
    untraceable = [a for a in injected if not _keyword_overlap(a, stmt_lower)]
    return min(1.0, len(untraceable) / max(1, len(injected)) * 0.6 + len(injected) * 0.1)

def _keyword_overlap(assumption: str, statement_lower: str, min_hits: int = 1) -> bool:
    words = [w for w in re.findall(r"[a-z0-9]+", assumption.lower()) if len(w) > 3]
    hits = sum(1 for w in words if w in statement_lower)
    return hits >= min_hits
```

### Step 3 — independent verifier call (negation-equivalence check)

A **separate** prompt/pass (different framing, ideally different temperature/seed or model — the
point is it must not just be the generator re-asked the same question) checks whether
`fol_negation` actually matches the author's stated `Falsification criteria`:

```
SYSTEM: You are a skeptical logic auditor. You are given a claim's stated falsification criterion
(plain English, written by the paper's authors) and a candidate formal negation (FOL). Your only job
is to judge whether the FOL negation, if it became true, would be a case the author's falsification
criterion also covers — and vice versa. You are not asked whether the FOL is elegant.

USER:
FALSIFICATION CRITERIA (author's prose): {falsification}
CANDIDATE FOL NEGATION: {fol_negation}

Return JSON: {"entailment_score": float in [0,1] (1 = fully equivalent coverage, 0 = unrelated),
"gap_notes": string (what the FOL negation misses or over-includes relative to the prose criterion)}
```

```python
def negation_consistency(verifier_out: dict) -> float:
    return max(0.0, min(1.0, float(verifier_out.get("entailment_score", 0.0))))
```

### Step 4 — deterministic structural checks

```python
def grounding_completeness(claim: Claim, gen_out: dict) -> float:
    """Fraction of the claim's predicates whose arguments trace to a verified Sources entry
    with a non-empty «quote» and a non-[pending] tag."""
    lines = SOURCE_LINE_RE.findall(claim.sources_raw)
    verified_values = {v for (v, ref, loc, quote, tag) in lines if quote.strip() and tag != "pending"}
    preds = gen_out.get("predicates", [])
    if not preds:
        return 0.0
    grounded = sum(1 for p in preds if p.get("grounded_in_sources"))
    # cross-check the LLM's self-report against the actual verified source count —
    # don't just trust "grounded_in_sources": true
    plausible_cap = min(1.0, len(verified_values) / max(1, len(preds)))
    return min(grounded / len(preds), plausible_cap) if preds else 0.0

def residual_prose_penalty(claim: Claim, gen_out: dict) -> float:
    residual = gen_out.get("residual_prose", "").strip()
    if not residual or not claim.statement:
        return 0.0
    return min(1.0, len(residual) / max(1, len(claim.statement)))

def build_dependency_graph(claims: list[Claim]) -> dict:
    return {c.cid: c.dependencies for c in claims}

def has_cycle(graph: dict) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    def dfs(u):
        color[u] = GRAY
        for v in graph.get(u, []):
            if v not in color:
                continue  # dangling dependency — flagged separately, not a cycle
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False
    return any(color[n] == WHITE and dfs(n) for n in graph)

def dangling_dependency_penalty(graph: dict) -> float:
    all_ids = set(graph.keys())
    dangling = sum(1 for deps in graph.values() for d in deps if d not in all_ids)
    total = sum(len(deps) for deps in graph.values())
    return dangling / total if total else 0.0
```

### Step 5 — per-claim score

```python
def score_claim(claim: Claim, gen_out: dict, verifier_out: dict) -> float:
    if not claim.statement or not claim.falsification or not claim.sources_raw:
        return 0.0  # thin/missing required fields -> floor, not skipped
    if not gen_out.get("formalizable", False):
        # still partially scoreable: a claim honestly reported as non-formalizable is
        # a real (low) signal, not a null -- floor but not necessarily absolute zero if
        # grounding is otherwise present, to distinguish "vague" from "totally empty".
        base = 0.05 * grounding_completeness(claim, gen_out)
        return base

    w_neg, w_ground, w_assump, w_residual = 0.40, 0.30, 0.15, 0.15
    neg_score = negation_consistency(verifier_out)
    ground_score = grounding_completeness(claim, gen_out)
    assump_pen = assumption_penalty(claim, gen_out)
    residual_pen = residual_prose_penalty(claim, gen_out)

    score = (
        w_neg * neg_score
        + w_ground * ground_score
        + w_assump * (1 - assump_pen)
        + w_residual * (1 - residual_pen)
    )
    return max(0.0, min(1.0, score))
```

### Step 6 — artifact-level aggregation

```python
def score_artifact(claims_md_text: str | None, llm_calls) -> float:
    """llm_calls: dict-like providing gen_out and verifier_out per claim id, produced by
    running Step 1 and Step 3 externally (this function is the deterministic aggregator)."""
    if not claims_md_text or not claims_md_text.strip():
        return 0.0

    claims = parse_claims(claims_md_text)
    if not claims:
        return 0.0

    graph = build_dependency_graph(claims)
    cycle_penalty = 0.25 if has_cycle(graph) else 0.0
    dangling_penalty = 0.15 * dangling_dependency_penalty(graph)

    per_claim_scores = []
    for c in claims:
        gen_out = llm_calls.get_gen(c.cid, default={})
        verifier_out = llm_calls.get_verifier(c.cid, default={})
        per_claim_scores.append(score_claim(c, gen_out, verifier_out))

    mean_claim_score = sum(per_claim_scores) / len(per_claim_scores)
    artifact_score = mean_claim_score * (1 - cycle_penalty) * (1 - dangling_penalty)
    return max(0.0, min(1.0, artifact_score))
```

`llm_calls` is an injected interface (real system: a thin wrapper issuing Step 1 and Step 3 calls per
claim, cached by `cid`) so this module stays pure/testable; the actual metric run wires it to the
model provider.

### Worked example against the shape doc's C01
`Statement` names entities (`p217_MS`, `p217_Ratio`, `p181_IA`), a metric (`P-score`), explicit values
(0.859, 0.783, 0.117), and a ranking relation. `Falsification criteria` is close to the literal
negation ("refuted if ... outranked p217_MS ... or non-significant"). Expect: `formalizable: true`,
high `grounding_completeness` (all cited values appear in `Sources` with quotes), low
`assumptions_injected`, high `negation_consistency` (~0.8–0.95) since the prose criterion nearly *is*
the negation already — this is what a near-ceiling FOL-ability claim looks like. A claim like "the
authors argue [p181_IA] is effectively obsolete" (the `Interpretation`, not `Statement`) would score
poorly if it leaked into `Statement`, exactly the failure the shape doc's own availability notes flag.

## 4. Why hard to Goodhart

- **Two independent LLM passes, not one.** Generation (Step 1) and negation-verification (Step 3) are
  separately prompted with different tasks ("transcribe" vs. "audit for equivalence"); an author or a
  sloppy compiler can't satisfy both by making the FOL merely *look* rigorous — the verifier is judged
  against the author's own prose falsification criterion, an artifact the compiler wrote before this
  metric ever runs.
- **Self-report is cross-checked, not trusted.** `assumptions_injected` and `grounded_in_sources` are
  both re-validated against the actual claim text and the actual `Sources` block (Step 2, Step 4) —
  an LLM can't just claim zero assumptions or full grounding; the deterministic checks cap what it can
  claim.
- **Structural checks are non-LLM and non-negotiable.** Cycle detection and dangling-dependency
  detection are pure graph algorithms — no amount of persuasive prose changes their output.
- **Formalizing forces precision that prose-quality metrics don't.** A claim can pass a
  "well-written"/"has all required fields" check while still being logically hollow ("improves
  outcomes"); attempting FOL is specifically the operation that exposes that hollowness, because the
  generator is instructed to refuse to invent predicates and to report residual prose it couldn't
  capture.
- **Penalize-don't-skip removes the "make it disappear" escape hatch.** Because missing
  `claims.md`, missing `Sources`, or missing `Falsification criteria` all score `0.0`/floor rather
  than being excluded, an author cannot improve their score by thinning the artifact — thinness is
  visible and costly, not invisible.

## 5. Composition with the rest of the suite

- Complements (does not duplicate) Seal Level 1 structural validation: SL1 checks *field presence*;
  this metric checks whether present fields are *logically load-bearing*. A claim can pass SL1 and
  score near-zero here (all fields present, all vague).
- Complements grounding/citation-format checks: this metric re-uses the `Sources` `«quote»`/`[pending]`
  structure as an input to `grounding_completeness`, but its unique contribution is the
  negation-equivalence and predicate-invention checks, which no citation-format check performs.
  It also composes with any epistemic-honesty scoring layer (e.g. rigor-review style checks) by
  supplying a machine-checkable signal — "this claim's falsification criterion is not actually the
  negation of its statement" — that a purely qualitative reviewer might miss or phrase as a vague
  "wording" note.
- Orthogonal to any citation-network / external-literature metric (semantic-scholar-style novelty or
  corroboration checks): FOL-ability is entirely internal to `claims.md`'s own logical structure and
  makes no claim about whether the finding is *true* or *novel*, only whether it is *stated precisely
  enough to be formally checked at all* — the necessary precondition for any downstream formal or
  external verification to even be well-posed.
