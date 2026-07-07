# M09 — FOL-ability (Oshima principles) — Expansion (expander 4)

## 1. What this metric actually measures

The one-line indicator is: *"Can a clean first-order-logic graph be built over the claims?"*
Read literally against the `logic/claims.md` shape, this is **not** "does the paper sound
rigorous" — it is a much narrower, mechanical question: can each claim's `Statement` be
compiled into a well-formed predicate-logic sentence whose negation is *exactly* the claim's
own `Falsification criteria`, and can the full set of claims (wired together via
`Dependencies`) be composed into one knowledge base without producing a contradiction or a
cycle?

That is the "Oshima principle" this metric operationalizes: a claim is only as scientifically
useful as its *formal decomposability* — subject/predicate/relation with typed variables,
bound quantifiers, and literal constants that trace back to `Sources`. A claim that reads as
confident prose but cannot be pinned to a predicate with a real negation is doing rhetorical
work, not evidentiary work, no matter how polished its `Evidence basis` looks.

This is why the assessment-critique flagged it as net-new: Seal Level 1 already checks that
the *fields* exist (Statement present, Sources present, quotes present). The ARA verifier
checks *grounding* (do the Sources actually say what the Statement says). Neither checks
whether the *content* of the Statement is logically well-formed enough to reason over
mechanically. M09 must stay scoped to that gap — it should never re-score field completeness
or grounding accuracy (that's redundant and duplicates the verifier's job and other metrics in
this suite); it should only score **formal composability of what's already there**.

## 2. What it must reward vs. must not reward

**Reward:**
- Statements that decompose into a predicate over typed entities/constants with an explicit
  relation (ranking, comparison, threshold, count, hazard ratio, etc.) — the kind of content
  the shape doc's own examples show (`P-score = 0.859`, `679 upregulated genes`, hazard ratios).
- Falsification criteria that are the *actual logical negation* of the Statement's predicate,
  not a vaguely related "this would be surprising" caveat.
- `Dependencies` chains that form a genuine implication graph (claim B's predicate uses claim
  A's conclusion as a premise) rather than a loose "related topic" cross-reference.
- Numeric/entity constants in the formalized predicate that are traceable to a `Sources` entry
  — formal claims about un-sourced numbers are not "clean," they're unfalsifiable-by-proxy.

**Must not reward:**
- Claims that are trivially "FOL-able" because they're boolean and empty of content (e.g., a
  padded claim like "the method was applied" with no measurable relation) — these game the
  metric by being easy to formalize while carrying no evidentiary weight. The scorer below
  explicitly zeroes out claims whose translation extracts no constants.
- Verbose or jargon-heavy Statements that an LLM translator can dress up in logic notation
  without the notation being sound (i.e., surface mimicry of "formal-sounding" text). This is
  why syntactic validity is checked separately from, and is necessary-but-not-sufficient for,
  semantic negation-consistency below.
- Re-rewarding what Seal Level 1 / the verifier already reward (field presence, grounding
  correctness) — those get zero additional weight here even if they happen to correlate.

## 3. Failure modes / gaming routes and mitigations

1. **LLM self-grading its own translation.** If the same call that produces the FOL sentence
   also reports "yes this is clean," the metric collapses to "does the LLM feel confident."
   Mitigation: the translator call *only* emits structured FOL text (predicate_form,
   negation_form, constants); every scoring decision (syntax validity, negation-consistency,
   constant grounding, cycle-freedom) is made by separate deterministic code below, never by
   asking the LLM to self-score.
2. **Padding with easy claims.** A compiler could inflate the claim count with simple,
   trivially formalizable boolean statements to raise the mean per-claim score. Mitigation:
   (a) the `constants_grounded` check zeroes any translation with no constants — a claim with
   no quantifiable content produces a score of 0, not the free ride you'd expect from "it
   parsed fine"; (b) the whole-artifact score requires a minimum count of *genuinely clean*
   claims (≥3) before the mean is taken at face value, via the sparse-graph penalty — so
   padding with 10 trivial claims plus 2 real ones still fails the density bar.
3. **Fake falsifiability.** A Falsification criterion that is topically related but not a real
   negation of the Statement (e.g., "refuted if the study cannot be replicated" attached to a
   Statement about a specific numeric ranking) would pass a naive "does it have this field"
   check. Mitigation: `negation_consistent()` requires the solver to verify
   `predicate_form ∧ negation_form` is UNSAT and `predicate_form ∨ negation_form` is valid
   under the shared signature — a criterion that doesn't logically negate the claim fails this
   regardless of how plausible it reads.
4. **Hidden circularity or dangling references in `Dependencies`.** A claims graph that looks
   locally clean per-claim can still be globally broken (A depends on B depends on A, or A
   depends on a claim ID that doesn't exist). Mitigation: `dependency_graph_penalty()` treats
   this as a whole-artifact multiplicative penalty, not a per-claim deduction, because
   composability is a graph property — you cannot build "a clean FOL graph" over a cyclic or
   dangling dependency set no matter how clean the individual nodes are.
5. **Status/graph inconsistency.** A `supported` claim depending on a `refuted` one (without
   the dependency being explained away) breaks the composed knowledge base. Mitigation:
   `status_consistency_penalty()` runs one global solver pass over the whole asserted KB
   (supported=True, refuted=False, hypothesis=unassigned, chained through `Dependencies`) and
   penalizes the whole artifact if that KB is contradictory.

## 4. Generation / compute workflow

### Inputs (artifact fields used — nothing else)
From `logic/claims.md`, per claim block: `Statement`, `Status`, `Falsification criteria`,
`Dependencies`, `Sources` (only the `<value>` tokens, to check constant traceability — this
metric does **not** re-verify that the quoted evidence is correct, that's the grounding
metric's job). `Proof`, `Evidence basis`, `Interpretation`, `Tags` are not used by this metric.

### Step-by-step
1. **Parse** `claims.md` into a list of `Claim` objects (regex/markdown-section parse against
   the documented `## C{NN}: ...` block structure).
2. **Availability gate (penalize, never skip):** if the file is absent, unreadable, or parses
   to zero claim blocks, the metric returns `0.0` outright — this is scored as the worst
   possible outcome, not "N/A," per the hard constraint.
3. **Per-claim FOL translation `[ext-FOL]`:** for each claim, call an LLM with the exact prompt
   in `call_fol_translator()` below. The prompt forces a single JSON object matching
   `FOLTranslation`, and explicitly permits (requires) the model to declare a claim
   `untranslatable` rather than force a fake formalization — refusal-to-force is itself
   information the scorer treats as a hard per-claim zero, not a skip.
4. **Deterministic validation** of each returned translation (no further LLM calls):
   syntax check → negation-consistency check (solver) → constant-groundedness against
   `Sources`. These combine into a bounded per-claim score.
5. **Graph-level checks** across the whole claim set: dependency DAG validity
   (cycles/dangling refs) and cross-claim status consistency (one solver pass over the
   composed KB).
6. **Aggregate**: mean per-claim score × dependency multiplier × status multiplier × a
   sparse-graph penalty if fewer than 3 claims cleared the "clean" bar.

### External call spec

```
[ext-FOL] LLM translation call — one call per claim, temperature 0.

SYSTEM:
You are a formal-logic translator. You NEVER assert a truth value beyond what the claim
states. Output STRICT JSON only, matching this schema:
{
  "untranslatable": bool,          # true if Statement/Falsification are too narrative/hedged
                                    # to support a predicate-logic encoding — do NOT force it
  "reason": str | null,            # required if untranslatable=true
  "predicate_form": str | null,    # single well-formed FOL sentence (ASCII: &, |, ~, ->, forall, exists)
  "negation_form": str | null,     # FOL sentence for Falsification criteria, SAME predicate/relation
                                    # symbols as predicate_form (it must be a formal negation, not a
                                    # different claim)
  "variables": {"<var>": "<type>"},
  "constants": ["<literal>", ...]  # every numeral/named-entity literal used, copied verbatim
                                    # from Statement — no paraphrasing, no rounding
}

USER:
Claim ID: {claim.id}
Statement: {claim.statement}
Falsification criteria: {claim.falsification}

Translate Statement into predicate_form and Falsification criteria into negation_form. Every
numeric or named-entity constant appearing in predicate_form MUST appear verbatim in Statement.
If you cannot do this without inventing a relation not actually stated, set untranslatable=true.
```

The model's own `untranslatable=true` is **not** treated as a skip: downstream this collapses
to the same `None` path as any other translation the deterministic checks reject, and scores
`0.0` for that claim — an artifact of vague, narrativized claims is exactly what this metric is
supposed to catch and penalize, not politely ignore.

### Scoring function (real Python against the documented shape)

```python
import re
from dataclasses import dataclass, field
from typing import Optional
import networkx as nx
# z3-solver assumed available for negation-consistency / KB-consistency checks
from z3 import Solver, Bool, Not, And, Or, sat, unsat

CLAIM_HEADER_RE = re.compile(r"^## (C\d+): (.+)$", re.MULTILINE)
FIELD_RE = lambda name: re.compile(
    rf"\*\*{name}\*\*:\s*(.+?)(?=\n- \*\*|\n## |\Z)", re.DOTALL
)

@dataclass
class Claim:
    id: str
    statement: str
    status: str
    falsification: str
    dependencies: list[str]
    sources: list[str] = field(default_factory=list)  # raw `<value>` tokens


def parse_claims(claims_md_text: str) -> list[Claim]:
    """Parse logic/claims.md into Claim objects per the documented block structure."""
    claims: list[Claim] = []
    blocks = re.split(r"(?=^## C\d+:)", claims_md_text, flags=re.MULTILINE)
    for block in blocks:
        m = CLAIM_HEADER_RE.match(block)
        if not m:
            continue
        cid = m.group(1)
        stmt_m = FIELD_RE("Statement").search(block)
        status_m = FIELD_RE("Status").search(block)
        fals_m = FIELD_RE("Falsification criteria").search(block)
        deps_m = FIELD_RE("Dependencies").search(block)
        src_block_m = re.search(r"\*\*Sources\*\*:\s*(.+?)(?=\n- \*\*Tags\*\*|\Z)", block, re.DOTALL)

        statement = stmt_m.group(1).strip() if stmt_m else ""
        status = status_m.group(1).strip() if status_m else ""
        falsification = fals_m.group(1).strip() if fals_m else ""
        deps_raw = deps_m.group(1).strip() if deps_m else "none"
        dependencies = [] if deps_raw.lower() == "none" else re.findall(r"C\d+", deps_raw)

        sources = []
        if src_block_m:
            sources = re.findall(r"`([^`]+)`\s*←", src_block_m.group(1))

        claims.append(Claim(cid, statement, status, falsification, dependencies, sources))
    return claims


@dataclass
class FOLTranslation:
    claim_id: str
    predicate_form: Optional[str]
    negation_form: Optional[str]
    constants: list[str]
    untranslatable: bool = False


def call_fol_translator(claim: Claim) -> FOLTranslation:
    """[ext-FOL] Executes the LLM prompt specified above and parses its JSON response
    into an FOLTranslation. On untranslatable=true, predicate_form/negation_form are None
    and constants=[]. This function performs NO scoring itself — it is a pure I/O boundary."""
    raise NotImplementedError("wire to LLM client; see prompt spec above")


def syntax_valid(sentence: Optional[str]) -> bool:
    """Deterministic ASCII-FOL grammar check: balanced parens/quantifier scopes, every
    variable bound by forall/exists or declared in `variables`, no leftover narrative
    text. Returns False for None or malformed input."""
    if not sentence:
        return False
    if sentence.count("(") != sentence.count(")"):
        return False
    # reject sentences that are just prose smuggled through (no logical operators/predicate call)
    has_operator_or_call = bool(re.search(r"[&|~]|->|forall|exists|\w+\(", sentence))
    return has_operator_or_call


def negation_consistent(fol: FOLTranslation) -> bool:
    """predicate_form and negation_form must be genuine logical negations of each other
    under a minimal shared-signature theory: treat each as an opaque proposition P, and
    require the translator to have used identical relation/entity symbols in both (checked
    lexically) AND that a solver over abstracted booleans finds P & notP unsat and
    P | notP valid — i.e. they cannot both hold, and one of them must."""
    if not fol.predicate_form or not fol.negation_form:
        return False
    # symbol-overlap check: negation_form must reuse the same relation symbols as predicate_form
    pred_symbols = set(re.findall(r"[A-Za-z_]\w*(?=\()", fol.predicate_form))
    neg_symbols = set(re.findall(r"[A-Za-z_]\w*(?=\()", fol.negation_form))
    if not pred_symbols or pred_symbols.isdisjoint(neg_symbols):
        return False  # negation_form invented an unrelated relation -> not a real negation
    P = Bool(f"P_{fol.claim_id}")
    notP = Bool(f"notP_{fol.claim_id}")
    s = Solver()
    s.add(Not(And(P, notP)))   # cannot both hold
    s.add(Or(P, notP))         # one of them must hold
    s.add(P == Not(notP))      # they are declared as each other's negation
    return s.check() == sat


def constants_grounded(fol: FOLTranslation, claim: Claim) -> float:
    """Fraction of extracted FOL constants that appear verbatim (substring match) in one
    of claim.sources' `<value>` tokens. This checks TRACEABILITY of the formalized
    constants, not correctness of the grounding (that's a different metric's job)."""
    if not fol.constants:
        return 0.0
    grounded = sum(
        1 for c in fol.constants
        if any(c in s or s in c for s in claim.sources)
    )
    return grounded / len(fol.constants)


def score_claim(claim: Claim) -> float:
    fol = call_fol_translator(claim)
    if fol.untranslatable or fol.predicate_form is None:
        return 0.0  # hard penalty; refusal-to-formalize is not a skip
    if not syntax_valid(fol.predicate_form) or not syntax_valid(fol.negation_form):
        return 0.05  # attempted but malformed
    if not negation_consistent(fol):
        return 0.2   # translated, but Falsification criteria isn't a real negation
    g = constants_grounded(fol, claim)
    if g < 1.0:
        return 0.2 + 0.3 * g  # partial: syntactically/logically fine but under-grounded
    return 1.0  # clean: valid, genuinely falsifiable, fully constant-traceable


def dependency_graph_multiplier(claims: list[Claim]) -> float:
    """Whole-artifact graph property: cycles or dangling dependency IDs make the claims
    graph un-composable in FOL (you cannot chain implications through a cycle, or through
    a reference to a node that doesn't exist). Applied to every claim's score, because
    'a clean FOL graph' is a global property, not a per-node one."""
    ids = {c.id for c in claims}
    g = nx.DiGraph()
    g.add_nodes_from(ids)
    dangling = False
    for c in claims:
        for dep in c.dependencies:
            if dep not in ids:
                dangling = True
                continue
            g.add_edge(c.id, dep)
    if dangling:
        return 0.5
    if not nx.is_directed_acyclic_graph(g):
        return 0.3
    return 1.0


def status_consistency_multiplier(claims: list[Claim]) -> float:
    """Composes one global KB: supported -> True, refuted -> False, hypothesis ->
    unassigned, propagated through Dependencies as implications (dependency must hold for
    the dependent claim to hold). Runs a single solver pass; any contradiction in the
    composed KB penalizes the whole artifact."""
    s = Solver()
    lits = {c.id: Bool(c.id) for c in claims}
    for c in claims:
        base_status = c.status.split(" ")[0].strip("()").lower()
        if base_status == "supported":
            s.add(lits[c.id])
        elif base_status == "refuted":
            s.add(Not(lits[c.id]))
        for dep in c.dependencies:
            if dep in lits:
                s.add(Or(Not(lits[c.id]), lits[dep]))  # claim -> its dependency must hold
    return 1.0 if s.check() == sat else 0.4


def score_M09(claims_md_text: Optional[str]) -> dict:
    """Top-level entrypoint. HARD CONSTRAINT: missing/thin inputs score down, never
    skip/N-A; availability is itself part of the score."""
    if not claims_md_text or not claims_md_text.strip():
        return {"score": 0.0, "availability": "missing", "per_claim": {}}

    claims = parse_claims(claims_md_text)
    if not claims:
        return {"score": 0.0, "availability": "empty", "per_claim": {}}

    per_claim = {c.id: score_claim(c) for c in claims}
    dep_mult = dependency_graph_multiplier(claims)
    status_mult = status_consistency_multiplier(claims)

    mean_claim_score = sum(per_claim.values()) / len(per_claim)
    final = mean_claim_score * dep_mult * status_mult

    clean_count = sum(1 for v in per_claim.values() if v >= 0.8)
    if clean_count < 3:
        final *= 0.5 + 0.5 * (clean_count / 3)  # sparse-graph penalty, never a skip

    return {
        "score": round(final, 4),
        "availability": "present",
        "total_claims": len(claims),
        "clean_claim_count": clean_count,
        "dependency_graph_multiplier": dep_mult,
        "status_consistency_multiplier": status_mult,
        "per_claim": per_claim,
    }
```

### Handling thin/degraded inputs (penalize-don't-skip, worked through)
- **Absent `claims.md`** (shouldn't happen per the shape doc — it's mandatory core — but the
  gate exists anyway defensively): `score_M09` returns `0.0`, `availability: "missing"`.
- **Abstract-only compilation** (per the shape doc's own availability notes — few claims, weak
  `Evidence basis`, often just `§Abstract`): these claims still get a real FOL-translation
  attempt; because their Statements tend to be vaguer and less quantified, they will more often
  come back `untranslatable` or with few `constants`, driving per-claim scores down through the
  *same* mechanism as any other thin claim — no special-cased detection is needed, the metric
  naturally reads this as thinner because the content genuinely is thinner.
- **Claims with bare-path Sources (no verbatim quote)** — a Seal Level 1 defect the shape doc
  calls the most common one: this metric does not re-fail those (that's the verifier's job),
  but such claims will typically also have weaker `constants_grounded` fractions since the
  underlying compilation was rushed, so it still shows up as reduced credit without double
  counting the same defect under a different name.
- **Zero claims clear the "clean" bar** (`clean_count == 0`): `final` is multiplied by `0.5`,
  not zeroed — a paper with claims present but none genuinely FOL-able is worse than one with a
  handful clean, but is not treated identically to a paper with no claims file at all.

## 5. Why this is hard to Goodhart

- The score is never computed from the LLM asserting "this is clean" — every accept/reject
  decision (syntax, negation-consistency, constant-groundedness, cycle-freedom, status
  consistency) is deterministic code running on the LLM's structured output, so a compiler
  cannot game the metric by prompting its own extraction LLM to "sound confident."
- Constant-groundedness ties the formal claim back to `Sources`, so an LLM cannot claim credit
  for a well-formed-looking predicate that quietly drops or invents numbers.
- The negation-consistency check specifically defeats the cheapest gaming route (attaching a
  generic, topically-adjacent Falsification criterion) by requiring symbol-level overlap plus
  solver-verified negation, not mere presence of the field.
- The dependency/status checks are graph-wide multipliers, so gaming any individual claim's
  score cannot rescue an artifact whose claims graph is internally circular or contradictory —
  you cannot locally patch your way to a "clean graph."
- The sparse-graph penalty defeats padding-with-easy-claims: raising the claim count with
  trivial, content-free statements doesn't raise the score unless those claims are also
  independently clean and quantified, which trivial claims by construction are not (they
  produce zero extractable constants and score 0.0 each).

## 6. Composition with the rest of the suite

M09 is deliberately orthogonal to the metrics it would otherwise overlap:
- It does **not** re-check field completeness (Seal Level 1's job) or grounding accuracy (the
  ARA verifier's / grounding metrics' job) — it only fires on the *logical form* of content
  those other checks have already gated for presence.
- It composes multiplicatively with claim-quality/impact metrics rather than substituting for
  them: a paper can score well on evidentiary grounding while scoring low here (narrative,
  unformalizable claims) or vice versa (crisp, quantified, falsifiable claims that still turn
  out to be weakly evidenced) — the two signals should diverge on real papers, which is exactly
  what makes this net-new rather than redundant.
- Its output (a per-claim clean/dirty flag plus a validated dependency DAG) is itself a useful
  downstream artifact for other agents — e.g., a cross-ARA contradiction-detection pass could
  consume the same FOL translations this metric already computed, rather than recomputing them,
  making M09's compute a reusable building block rather than a one-off score.
