# M09 — FOL-ability (Oshima principles) — Expansion 1

**Artifact**: `logic/claims.md` (shape: `research/metrics/v3/tournament/shapes/02_claims.md`)
**One-line indicator** (from ledger): Can a clean first-order-logic graph be built over the claims
(Oshima principles)? `[ext] FOL` / `[sem]`. Net-new formal-checkability signal; nothing comparable
exists in round-1 or the ARA verifier.

---

## 1. Expansion of the reasoning

### What "FOL-ability" actually measures

`claims.md` is prose-shaped but logic-*intentioned*: every claim already carries a Statement, a
Status, a Falsification criteria, a Proof (experiment refs), an Evidence basis, and a Dependencies
list pointing at other claims. That is, by construction, an attempt at a directed argument graph —
nodes are propositions, edges are "this claim's truth rests on that claim," and each node ships its
own negation condition (Falsification criteria). FOL-ability asks: **is that graph actually a graph**,
in the formal sense — can each Statement be compiled into a first-order proposition over a
consistent, shared vocabulary of predicates/constants, does each Falsification criterion function as
a genuine logical negation of its Statement rather than a vague restatement, and does the
Dependencies structure form a well-founded (acyclic) entailment order rather than decorative
cross-references?

This is a different axis than "is each number sourced" (grounding/citation metrics) or "is the prose
internally consistent" (a coherence verifier). A claims block can be perfectly well-cited and
narratively coherent while being **formally mush**: hedged quantifiers ("may suggest," "is broadly
consistent with"), predicates that shift meaning between claims that cite each other, falsification
criteria that just repeat the statement in the negative mood without giving a checkable observation,
or a Dependencies graph that is actually cyclic or vacuous (every claim lists `none`, so there is no
graph at all, only isolated leaves). None of that is caught by "did you cite Table 2." FOL-ability is
the metric that asks whether the paper's claim layer could, in principle, be fed to a theorem prover
or a consistency checker and produce a meaningful answer — i.e., whether the compiler did the harder
job of translation, not just transcription. This is the "Oshima principle" this metric is named for:
formal-checkability is a first-class compilation target, not an incidental byproduct of tidy
markdown.

### What it must reward

- Statements whose load-bearing terms resolve to **fixed predicates/constants** shared across the
  claim set (e.g., `AUC(p217_MS, Abeta) = 0.859` reused consistently rather than re-described with
  different vocabulary each time it recurs).
- Falsification criteria that are genuine **negations-in-context** of the Statement — an observation
  that, if it occurred, would make the Statement false under the same predicates (not a different,
  softer claim).
- Dependencies edges that are **semantically load-bearing**: the child claim's formula actually
  requires the parent's formula as a premise, not just topical adjacency.
- A dependency structure that is **acyclic** — a well-founded partial order, the minimum precondition
  for any of this being usable by a downstream reasoner.
- Consistent quantification — `∀`/`∃` scope stated or inferable without ambiguity (e.g., "achieved the
  highest rank" implies a bounded, enumerable comparison set — the compiler should have made that set
  determinable from Evidence basis, not left it open-ended).

### What it must NOT reward

- Superficial formatting compliance (claim has all the required *field labels* filled in) mistaken
  for formalizability. A claim can have every field present and still be logically mush ("broadly
  supports the hypothesis that X may be linked to Y").
- Padding the Dependencies graph with plausible-looking but vocabulary-mismatched edges just to look
  "graph-like" — this must be actively penalized (see §2, vocabulary-consistency check), not rewarded
  for density.
- Rewarding a large claim count as a proxy for a rich graph. Ten isolated, dependency-free claims are
  not a "clean FOL graph"; they're ten disconnected facts. The metric must distinguish *coverage*
  (how many claims exist) from *graph-ness* (how connected/consistent the entailment structure is).
- Crediting a claim whose Falsification criteria is unfalsifiable in practice (e.g., "refuted if future
  work disagrees") — this looks compliant (field is filled) but contributes zero formal content.

### Failure modes / gaming routes, and the countermeasures baked into the workflow below

1. **Vague-but-fluent statements.** An LLM compiler under time pressure writes fluent, hedge-heavy
   prose that *reads* precise but resists formalization ("substantially outperforms," "is likely
   driven by"). Countermeasure: the FOL-formalizer call must emit an explicit `ambiguous_terms` list
   with severity, and any claim whose statement cannot be pinned to bound predicates scores near zero
   on that claim, not a comfortable middle score — muddiness is a defect, not a neutral outcome.
2. **Cosmetic Dependencies.** Compilers pad `Dependencies: [C01]` on nearly every claim to *look*
   connected (rewarding "graph density" naively would encourage this). Countermeasure: every declared
   edge is checked for actual vocabulary/predicate reuse between parent and child; edges that don't
   reuse any symbol from the parent's formalization are flagged as spurious and subtracted from the
   graph-richness credit rather than added to it.
3. **Restated-not-negated falsification.** "Falsification criteria: refuted if the ranking were
   different" — technically present, formally empty (doesn't specify what "different" cashes out to
   in the shared predicate vocabulary). Countermeasure: a dedicated negation-check call scores whether
   the falsification text is a genuine contradiction of the statement's formula in the same
   vocabulary, not merely a same-topic sentence.
4. **Cyclic or self-referential "support."** Two claims each listing the other as a dependency to look
   mutually reinforcing. This breaks well-foundedness outright. Countermeasure: hard cycle detection
   on the dependency graph with a score cap (not a soft deduction) — a cyclic graph cannot be handed
   to any downstream FOL engine, so it cannps the overall metric regardless of how clean the
   individual claims read.
5. **Sourcing-vocabulary mismatch.** A formula uses a constant (e.g., a numeric threshold) that traces
   back to a `Sources` entry that is a bare path or `[pending]` (no verbatim quote). The formalized
   term is then floating — syntactically fine, semantically ungrounded. Countermeasure: grounding
   closure check reuses the claims.md Sources-quote discipline (Rule 16) as a precondition for
   counting a formalized term as "real."
6. **Thin/abstract-only artifacts gaming the mean.** A 2-claim, abstract-only compilation could still
   score well on a naive per-claim average if both of its claims happen to be simple and clean.
   Countermeasure: a graph-richness dampener applies whenever `n_claims` is small or edges are absent,
   per the HARD CONSTRAINT below — thinness is itself scored down, not treated as N/A or as "nothing
   to penalize here."

### How this changes vs. a naive "check each claim's logic" design

Given this ranked in the top 10 specifically for being *net-new* and *tightly scoped* relative to the
ARA verifier (which already checks field-presence and Sources-quote validity at Seal Level 1), this
workflow deliberately does **not** re-litigate field completeness or citation format as its main
signal — it takes Seal-Level-1-style completeness as a gating precondition (feeds into the
completeness term) and spends its actual discriminating power on the graph/logic layer: formula
extraction, negation-validity, vocabulary consistency across edges, and acyclicity. That is the part
no other metric in the suite touches.

---

## 2. Generation / compute workflow

### Inputs (artifact fields, from `02_claims.md`)

Per claim block `C{NN}`: `Statement`, `Status`, `Falsification criteria`, `Proof` (list of `E{NN}`),
`Evidence basis`, `Interpretation` (optional), `Dependencies` (list of `C{NN}` or `none`), `Sources`
(list of `` `value` ← ref (locator) «quote» [input|result] ``), `Tags`.

### Step 0 — Availability gate (penalize, never skip)

```python
def load_claims(artifact_path: str) -> list[dict] | None:
    """Returns None only if the file is truly absent (path doesn't resolve)."""
    ...

claims = load_claims(path)
if claims is None:
    return 0.0  # claims.md is mandatory core; total absence is the worst case, not N/A
if len(claims) == 0:
    return 0.0  # a "graph" over zero nodes is not a graph
```

### Step 1 — Parse claim blocks into structured records

```python
import re

CLAIM_HEADER = re.compile(r"^##\s+(C\d+):\s*(.+)$", re.M)
FIELD = re.compile(
    r"\*\*(Statement|Status|Falsification criteria|Proof|Evidence basis|"
    r"Interpretation|Dependencies|Sources|Tags)\*\*:\s*(.+?)(?=\n- \*\*|\Z)",
    re.S,
)
SOURCE_LINE = re.compile(
    r"`([^`]+)`\s*←\s*([^\(]+)\(([^)]+)\)\s*(«([^»]*)»)?\s*\[(input|result)\]"
)

def parse_claims_md(text: str) -> list[dict]:
    records = []
    headers = list(CLAIM_HEADER.finditer(text))
    for i, h in enumerate(headers):
        cid, title = h.group(1), h.group(2).strip()
        body = text[h.end(): headers[i + 1].start() if i + 1 < len(headers) else len(text)]
        fields = {m.group(1): m.group(2).strip() for m in FIELD.finditer(body)}
        deps_raw = fields.get("Dependencies", "none")
        deps = [] if deps_raw.strip().lower() == "none" else re.findall(r"C\d+", deps_raw)
        sources = []
        for m in SOURCE_LINE.finditer(fields.get("Sources", "")):
            value, ref, locator, _, quote, tag = m.groups()
            sources.append({
                "value": value.strip(), "ref": ref.strip(), "locator": locator.strip(),
                "quote": quote, "tag": tag,
                "pending": "pending" in (quote or "") or "[pending" in fields.get("Sources", ""),
            })
        records.append({
            "id": cid, "title": title,
            "statement": fields.get("Statement", ""),
            "status": fields.get("Status", ""),
            "falsification": fields.get("Falsification criteria", ""),
            "proof": re.findall(r"E\d+", fields.get("Proof", "")),
            "evidence_basis": fields.get("Evidence basis", ""),
            "dependencies": deps,
            "sources": sources,
            "tags": [t.strip() for t in fields.get("Tags", "").split(",") if t.strip()],
            "_raw_fields_present": set(fields.keys()),
        })
    return records
```

### Step 2 — Completeness precondition (deterministic; no LLM)

Required fields per the shape spec: `Statement, Status, Falsification criteria, Proof, Evidence
basis, Dependencies, Sources, Tags` (Interpretation is optional). A block missing any required field,
or whose `Sources` contain a bare path with no `«quote»` (not even a `[pending: ...]` note), fails
this precondition outright.

```python
REQUIRED = {"Statement", "Status", "Falsification criteria", "Proof",
            "Evidence basis", "Dependencies", "Sources", "Tags"}

def completeness_score(claim: dict) -> float:
    missing = REQUIRED - claim["_raw_fields_present"]
    if missing:
        return 0.0  # incomplete claim cannot be honestly formalized; score it, don't drop it
    if not claim["sources"]:
        return 0.0  # a claim with no traceable sources has nothing for terms to ground to
    bad_sources = [s for s in claim["sources"] if s["quote"] is None and not s["pending"]]
    if bad_sources:
        return 0.2  # bare path, no quote, not even flagged pending: worst form of "present but hollow"
    pending_frac = sum(s["pending"] for s in claim["sources"]) / len(claim["sources"])
    return 1.0 - 0.5 * pending_frac  # pending is honest but still thinner than verified
```

### Step 3 — `[ext] FOL` formalization call (LLM, one call per claim)

This is the external-tool step named in the ledger entry (`[ext] FOL`). Exact prompt:

```
SYSTEM: You are a formal-logic compiler. You convert a single scientific claim into a first-order
logic (FOL) proposition using explicit predicates, constants, functions, and quantifiers. You do not
evaluate whether the claim is TRUE — only whether it CAN be stated as a determinate FOL formula.

USER:
Claim statement:
"""{statement}"""

Evidence basis (for resolving comparison sets / bounds only, not for truth-checking):
"""{evidence_basis}"""

Return strict JSON:
{
  "predicates": [{"name": str, "arity": int, "meaning": str}, ...],
  "constants": [str, ...],
  "formula": str,               # e.g. "∀x∈{p217_MS,p217_Ratio,...}: AUC(x,Abeta) <= AUC(p217_MS,Abeta)"
  "quantifier_scope_resolved": bool,   # false if a comparison set/bound is implicit and undetermined
  "ambiguous_terms": [{"term": str, "reason": str, "severity": "low"|"med"|"high"}],
  "formalizable": bool          # your overall judgment: could a theorem prover consume `formula` as-is?
}
```

Deterministic reduction of the LLM's JSON to a sub-score:

```python
SEVERITY_WEIGHT = {"low": 0.1, "med": 0.3, "high": 0.6}

def formalizability_score(fol_result: dict) -> float:
    if not fol_result.get("formalizable") or not fol_result.get("formula"):
        return 0.0
    penalty = sum(SEVERITY_WEIGHT[t["severity"]] for t in fol_result.get("ambiguous_terms", []))
    scope_penalty = 0.0 if fol_result.get("quantifier_scope_resolved") else 0.3
    return max(0.0, 1.0 - penalty - scope_penalty)
```

### Step 4 — Falsification-as-negation check (LLM, one call per claim)

```
SYSTEM: You check whether a stated falsification condition is a genuine logical negation of a
formalized claim, in the SAME predicate vocabulary — not merely a topically related but distinct or
softer statement.

USER:
Formalized claim: {formula}
Predicates: {predicates}
Falsification criteria (natural language): """{falsification}"""

Return strict JSON:
{"is_genuine_negation": true|false,
 "shares_vocabulary": true|false,
 "rationale": str}
```

```python
def negation_score(neg_result: dict) -> float:
    if neg_result["is_genuine_negation"] and neg_result["shares_vocabulary"]:
        return 1.0
    if neg_result["is_genuine_negation"] and not neg_result["shares_vocabulary"]:
        return 0.5  # negates something, but drifted vocabulary — half credit, not full
    return 0.0
```

### Step 5 — Grounding closure of formalized terms (deterministic)

Every `constant` the LLM extracted in Step 3 should trace to a non-pending, quoted `Sources` entry
on that claim (reuses the claims.md grounding discipline as a precondition for a term counting as
"real" in the formal graph, per Rule 16 — this is intentional reuse of the sourcing signal, not
duplication of a separate metric's *purpose*, since here it gates whether a *symbol* is admissible in
the graph, not whether the *prose* is cited).

```python
def grounding_closure_score(fol_result: dict, claim: dict) -> float:
    constants = fol_result.get("constants", [])
    if not constants:
        return 0.5  # no numeric/named constants to ground is unusual and mildly suspect, not free
    quoted_values = {s["value"] for s in claim["sources"] if s["quote"] and not s["pending"]}
    grounded = sum(1 for c in constants if any(c in v or v in c for v in quoted_values))
    return grounded / len(constants)
```

### Step 6 — Per-claim score (multiplicative — cleanliness is conjunctive, not additive)

```python
def claim_score(claim: dict, fol_result: dict, neg_result: dict) -> float:
    c = completeness_score(claim)
    f = formalizability_score(fol_result)
    n = negation_score(neg_result)
    g = grounding_closure_score(fol_result, claim)
    return c * f * n * g
```

A claim that is complete and formalizable but has an unfalsifiable falsification clause, or an
ungrounded constant, scores near zero on the multiplicative product — reflecting that "clean FOL"
requires all of these simultaneously, not on average.

### Step 7 — Graph assembly and structural checks (deterministic; the "graph" part of FOL-ability)

```python
import networkx as nx

def build_dependency_graph(claims: list[dict]) -> "nx.DiGraph":
    g = nx.DiGraph()
    for c in claims:
        g.add_node(c["id"])
    for c in claims:
        for dep in c["dependencies"]:
            g.add_edge(dep, c["id"])  # dep is a premise for c
    return g

def has_cycle(g) -> bool:
    return not nx.is_directed_acyclic_graph(g)

def edge_vocabulary_consistency(g, fol_by_id: dict) -> float:
    """For each dependency edge parent->child, require the child's formula to reuse at least one
    predicate/constant from the parent's formula. Zero-overlap edges are spurious-looking and
    penalized rather than credited toward graph richness."""
    edges = list(g.edges())
    if not edges:
        return 1.0  # vacuously consistent; graph_structure_factor (below) separately penalizes "no edges"
    good = 0
    for parent, child in edges:
        p_syms = set(fol_by_id[parent].get("predicates", [])) | set(fol_by_id[parent].get("constants", []))
        c_syms = set(fol_by_id[child].get("predicates", [])) | set(fol_by_id[child].get("constants", []))
        p_names = {p["name"] if isinstance(p, dict) else p for p in p_syms}
        c_names = {p["name"] if isinstance(p, dict) else p for p in c_syms}
        if p_names & c_names:
            good += 1
    return good / len(edges)

def graph_structure_factor(g, n_claims: int) -> float:
    if n_claims <= 1:
        return 0.4          # a single node cannot be a "graph" — dampened, not zero, not skipped
    n_edges = g.number_of_edges()
    connectivity = min(1.0, n_edges / (n_claims - 1))
    return 0.5 + 0.5 * connectivity   # even a fully dependency-free-but-large claim set caps at 0.5
```

### Step 8 — Final aggregate scoring function

```python
def score_fol_ability(artifact_path: str, formalize_fn, negate_fn) -> float:
    """
    formalize_fn: callable(claim) -> dict   (wraps the Step-3 LLM call)
    negate_fn:    callable(formula, predicates, falsification_text) -> dict  (Step-4 LLM call)
    """
    text = load_claims_md_text(artifact_path)   # returns None if file absent
    if text is None:
        return 0.0

    claims = parse_claims_md(text)
    if not claims:
        return 0.0

    fol_by_id, neg_by_id = {}, {}
    per_claim_scores = []
    for c in claims:
        fol_result = formalize_fn(c)
        neg_result = negate_fn(fol_result.get("formula", ""),
                                fol_result.get("predicates", []),
                                c["falsification"])
        fol_by_id[c["id"]] = fol_result
        neg_by_id[c["id"]] = neg_result
        per_claim_scores.append(claim_score(c, fol_result, neg_result))

    mean_claim_score = sum(per_claim_scores) / len(per_claim_scores)

    g = build_dependency_graph(claims)
    cyclic = has_cycle(g)
    vocab_consistency = edge_vocabulary_consistency(g, fol_by_id)
    structure_factor = graph_structure_factor(g, len(claims))

    overall = mean_claim_score * structure_factor * vocab_consistency

    if cyclic:
        overall = min(overall, 0.2)  # hard cap: a cyclic "entailment" graph is not well-founded FOL

    return max(0.0, min(1.0, overall))
```

### Handling of `[sem]` (semantic-scholar / undermind)

For M09 specifically, the semantic-search leg noted in the ledger (`[sem]`) is used only as a
**fallback disambiguator**, not a primary step: when Step 3's formalizer flags a `medium`/`high`
severity ambiguous term that looks like a domain-standard construct (e.g., an accepted biomarker
name, a standard statistical quantity), an optional `[sem]` lookup (semantic-scholar/undermind query
for the term's standard definition) may resolve it to a bound predicate instead of leaving it
ambiguous. If the `[sem]` call is unavailable or returns nothing, the term stays ambiguous and is
scored as such in Step 3 — the external lookup can only improve a score from a penalized ambiguous
state, never substitute for the LLM formalization step, and its absence is not grounds to skip or
neutralize the penalty.

---

## 3. Why this is hard to Goodhart

- **Two independent LLM judgments per claim** (formalization in Step 3, negation-validity in Step 4)
  that must agree in the same predicate vocabulary — an artifact author optimizing prose for one call
  (e.g., writing something that *sounds* like clean FOL) still has to survive the second call actually
  checking that the falsification clause negates that exact formalization, not a paraphrase.
- **Multiplicative, not additive, per-claim scoring**: padding one field (e.g., writing an
  impressively precise Statement) cannot compensate for a hollow Falsification criterion or an
  ungrounded constant — every dimension must be simultaneously clean.
- **Cosmetic-density is actively detected and punished**, not just under-rewarded: adding
  `Dependencies` edges to look more "graph-like" is checked against actual predicate/constant reuse
  (`edge_vocabulary_consistency`); spurious edges lower this factor rather than raising
  `graph_structure_factor`, so padding backfires.
- **Cycle detection is a hard, deterministic structural cap** — no amount of LLM-judgment gaming on
  individual claims can route around a cyclic dependency graph, because the cap is applied after and
  independent of the per-claim LLM scores.
- **Grounding closure ties formal terms back to the claims.md Sources-quote discipline**, so a
  compiler cannot "clean up" a claim's logic by inventing crisp-sounding constants that have no
  traceable, quoted source — that path is closed by Step 5 regardless of how well-formed the FOL
  syntax looks.
- **Thinness is structurally dampened, not ignored**: a 1-claim or edge-free claim set is capped by
  `graph_structure_factor` at 0.4–0.5 regardless of how clean that lone claim is, which removes the
  incentive to keep the claim set minimal/simple purely to make formalization easy.

## How it composes with the rest of the suite

FOL-ability is deliberately orthogonal to (a) grounding/citation metrics, which check that a
Statement's *numbers* trace to quoted evidence, and (b) prose-coherence/verifier checks, which check
narrative consistency across sections. This metric instead asks whether the claim layer, taken as a
whole, is *structurally* a valid logic object: formalizable propositions, genuine negations, a
well-founded (acyclic) entailment order, and vocabulary reuse across dependency edges. It reuses the
Sources-quote signal only as a *precondition gate* for admitting a term into the formal graph (Step 5)
— it does not re-score citation completeness as its main signal, preserving the non-redundancy with
the ARA verifier's own Seal Level 1 checks and other citation-focused metrics in this suite. Because
no other metric in round-1 or the verifier asks "can this be handed to a theorem prover," this metric
contributes a genuinely new axis of "good science" — formal-checkability as a compilation target —
rather than a re-weighting of grounding or coherence signals already captured elsewhere.
