# M09 — FOL-ability (Oshima principles) — Expansion 2

## 1. What this metric actually measures

The one-line indicator is: *"Can a clean first-order-logic graph be built over the claims?"*
Unpacked, that is really two separable questions the workflow below keeps separable, because
conflating them is the single easiest way for this metric to be gamed or to degenerate into a
restyled duplicate of grounding checks that already exist elsewhere in the ARA verifier:

1. **Formalizability (per-claim)** — can `Statement` + `Falsification criteria` for a single claim
   `C{NN}` be translated, without loss or invention, into a well-formed first-order formula: bound
   variables, explicit predicates over entities/quantities named in the claim, quantifiers scoped
   correctly, and a negation of that formula that is *exactly* what `Falsification criteria`
   describes? A claim is only "FOL-able" if its own stated falsification condition is the logical
   negation (or a tight sufficient condition for the negation) of its own statement — not a vague
   restatement, not a different claim.
2. **Graph-cleanliness (cross-claim)** — do the `Dependencies` links declared across claims form a
   structure that a formal system could actually reason over: a DAG (no cycles — circular support is
   not a valid entailment structure), referentially closed (every ID in `Dependencies`/`Proof` exists),
   and *semantically* consistent (a claim marked `supported` cannot have a `refuted` claim as an
   unqualified premise; a `hypothesis` claim cannot be listed as a `Dependencies` premise for a
   `supported` claim, because you cannot ground a supported result in an unresolved hypothesis).

**Reward**: claims whose logic is *load-bearing* — predicates trace to `Sources`-grounded terms,
quantifiers are non-trivial (not everything smuggled into an implicit `∀` with no restriction),
`Dependencies` edges correspond to genuine premise→conclusion relationships that a solver can chain,
and the falsification criterion is a real, checkable negation rather than boilerplate ("this could be
wrong if the study were flawed").

**Must not reward**: cosmetic formalization. A claims file can be dressed up with FOL-flavored prose
(explicit "for all X such that..." phrasing) without any of it being semantically checkable — that is
worse than plain prose because it fakes the exact signal this metric exists to detect. The workflow
below defends against this by never scoring the *presence* of logic-sounding language; it only scores
whether an independently-run formalizer (Section 3, Step 1) plus a symbolic consistency pass
(Section 3, Step 3) actually succeed on the claim/graph as given, with adversarial checks against a
lenient formalizer (Section 3, Step 4).

## 2. Why this is net-new (preserving the round-1 ranking edge)

Nothing in the ARA verifier or round-1 winners checks whether claims compose into a *provable*
structure — grounding checks (Rule 16, Seal Level 1 `Sources` validation) verify that a claim's
numbers are traceable to evidence, but say nothing about whether the claim's own internal logic is
well-formed, or whether the `Dependencies` DAG the compiler declared is coherent as an entailment
graph rather than just a citation-order convenience. This metric is the only one in the suite that
asks a genuinely different question: not "is this claim supported by data" but "if I treated this
claims file as a formal theory, would it type-check." That is a structural/logical property,
orthogonal to (and not redundant with) both grounding-verification metrics and any metric scoring
prose quality of `Evidence basis`/`Interpretation`.

## 3. Generation / compute workflow

### Inputs (from `logic/claims.md`, per the documented shape)
For each claim block `C{NN}`: `Statement`, `Status`, `Falsification criteria`, `Proof`,
`Dependencies`, `Sources` (used only to check predicate groundedness, not re-verified here — that is
the grounding metric's job). All fields are read; **the metric never treats a missing field as "not
applicable" — a missing `Falsification criteria` or `Dependencies` block scores as a hard-0 on the
sub-checks that depend on it (Section 4), never excluded from the average.**

### Step 0 — Parse
```python
import re

CLAIM_HEADER = re.compile(r"^## (C\d+):\s*(.+)$", re.M)
FIELD = re.compile(
    r"\*\*(Statement|Status|Falsification criteria|Proof|Evidence basis|"
    r"Interpretation|Dependencies|Sources|Tags)\*\*:\s*(.*?)(?=\n- \*\*|\n## |\Z)",
    re.S,
)

def parse_claims(md_text: str) -> list[dict]:
    claims = []
    headers = list(CLAIM_HEADER.finditer(md_text))
    for i, h in enumerate(headers):
        cid, title = h.group(1), h.group(2).strip()
        body = md_text[h.end(): headers[i + 1].start() if i + 1 < len(headers) else len(md_text)]
        fields = {k: v.strip() for k, v in FIELD.findall(body)}
        claims.append({
            "id": cid,
            "title": title,
            "statement": fields.get("Statement", ""),
            "status": fields.get("Status", ""),
            "falsification": fields.get("Falsification criteria", ""),
            "proof": [x.strip() for x in re.findall(r"E\d+", fields.get("Proof", ""))],
            "dependencies": ([] if fields.get("Dependencies", "").lower().startswith("none")
                              else [x.strip() for x in re.findall(r"C\d+", fields.get("Dependencies", ""))]),
            "sources_raw": fields.get("Sources", ""),
            "present_fields": set(fields.keys()),
        })
    return claims
```
Missing fields are visible directly as absent keys in `present_fields` — this feeds the
penalize-don't-skip logic in Section 4 (Step 6) rather than being silently defaulted.

### Step 1 — [LLM] Per-claim formalization ("Oshima pass")
For every claim, call an LLM with a fixed prompt that forces a structured, checkable output rather
than free-form logic prose:

```
SYSTEM: You are a formal-logic transcriber. You do not evaluate scientific merit. You only
translate the exact text given into first-order logic, or report precisely why you cannot.

USER:
Claim ID: {id}
Statement: {statement}
Falsification criteria: {falsification}

Task:
1. Extract every predicate P(args) implied by Statement, using only entities/quantities named
   in Statement (no invented terms).
2. Extract the quantifier structure (∀/∃) and variable bindings, if any; if the statement is a
   ground fact with no quantification, say so explicitly.
3. Write Statement as one first-order formula F using only the predicates from (1) and standard
   connectives (¬,∧,∨,→,↔).
4. Write Falsification criteria as a formula G using the same predicate vocabulary where possible.
5. State whether G is logically the negation of F (¬F), a sufficient condition for ¬F, or NEITHER
   (i.e., falsification criteria don't actually falsify the statement as written).
6. List any terms in Statement you could not formalize (vague quantifiers like "most", unresolved
   pronouns, hedges) as `ambiguous_terms`.

Return strict JSON:
{"predicates": [...], "variables": [...], "quantifiers": [...], "formula_F": "...",
 "formula_G": "...", "g_relation_to_notF": "negation|sufficient_for_negation|neither",
 "ambiguous_terms": [...], "well_formed": true|false}
```
`well_formed` is set false by the model whenever it cannot produce F/G without inventing content —
this is the single most important anti-Goodhart lever in Step 1: the prompt explicitly forbids
inventing predicates, so a claim written as prose-with-logic-flavor but no real structure should
fail here rather than get rubber-stamped.

```python
def formalize_claim(llm_call, claim: dict) -> dict:
    if not claim["statement"] or not claim["falsification"]:
        # penalize, do not skip: no LLM call needed, this is an automatic fail
        return {"well_formed": False, "g_relation_to_notF": "neither",
                "ambiguous_terms": ["<missing field>"], "predicates": []}
    return llm_call(FORMALIZE_PROMPT.format(**claim))  # returns parsed JSON above
```

### Step 2 — [LLM, adversarial re-run] Stability check
Re-run Step 1 at a different sampling temperature (or with a paraphrase-shuffled prompt) and diff the
`predicates` sets and `g_relation_to_notF` verdict. This guards against a lenient/sycophantic
formalizer inflating `well_formed=true` on incoherent input — genuine formal structure should
reproduce; hallucinated structure typically doesn't.

```python
def stability_score(run_a: dict, run_b: dict) -> float:
    if run_a["g_relation_to_notF"] != run_b["g_relation_to_notF"]:
        return 0.0
    pa, pb = set(run_a["predicates"]), set(run_b["predicates"])
    if not pa and not pb:
        return 0.0  # both empty = nothing to formalize = fail, not vacuous pass
    jaccard = len(pa & pb) / len(pa | pb)
    return jaccard
```

### Step 3 — Build and validate the dependency graph
```python
import networkx as nx

def build_graph(claims: list[dict]) -> nx.DiGraph:
    g = nx.DiGraph()
    ids = {c["id"] for c in claims}
    g.add_nodes_from(ids)
    for c in claims:
        for dep in c["dependencies"]:
            g.add_edge(dep, c["id"], dangling=(dep not in ids))
    return g

def graph_integrity(g: nx.DiGraph) -> dict:
    dangling = [(u, v) for u, v, d in g.edges(data=True) if d.get("dangling")]
    try:
        cycles = list(nx.find_cycle(g, orientation="original"))
    except nx.NetworkXNoCycle:
        cycles = []
    return {"dangling_refs": dangling, "cycles": cycles, "is_dag": len(cycles) == 0}
```

### Step 4 — [ext:FOL] Status-consistency pass over the graph
This is the symbolic-solver call the ledger entry flags as `[ext] FOL`: treat each claim's `Status`
as a truth assignment (`supported`→True, `refuted`→False, `hypothesis`→unassigned) and check the
`Dependencies` DAG for assignment conflicts a first-order reasoner would reject — a supported node
cannot have an unqualified `refuted` or unresolved `hypothesis` ancestor.

```python
def status_consistency(claims: list[dict], g: nx.DiGraph) -> list[tuple]:
    status = {c["id"]: c["status"].split(" (")[0].strip() for c in claims}  # strip qualifiers
    violations = []
    for node in nx.topological_sort(g) if nx.is_directed_acyclic_graph(g) else g.nodes:
        if status.get(node) != "supported":
            continue
        for anc in nx.ancestors(g, node):
            if status.get(anc) == "refuted":
                violations.append((node, anc, "supported claim depends on refuted ancestor"))
            elif status.get(anc) == "hypothesis":
                violations.append((node, anc, "supported claim rests on unresolved hypothesis"))
    return violations
```
(In a production build this check can be handed to an actual SAT/SMT backend, e.g. Z3, once
`formula_F`/`formula_G` from Step 1 are used to enrich the assignment beyond `Status` alone — the
above is the deterministic minimum viable version that requires no external solver dependency and is
runnable standalone.)

### Step 5 — [sem] Missing-edge detection (semantic near-duplicate predicates without a declared edge)
Call a semantic-similarity model ([sem]) over pairs of claims' `formula_F`/predicate sets. If two
claims share ≥2 predicates (same entities/quantities) but have **no** `Dependencies` edge between
them in either direction, flag it — this is the gaming route where a compiler declares `Dependencies:
none` everywhere to trivially avoid cycle/consistency failures while the claims are obviously
logically entangled.

```python
def missing_edge_candidates(claims: list[dict], formalizations: dict, g: nx.DiGraph,
                             sem_similarity) -> list[tuple]:
    flags = []
    ids = [c["id"] for c in claims]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            shared = set(formalizations[a]["predicates"]) & set(formalizations[b]["predicates"])
            connected = g.has_edge(a, b) or g.has_edge(b, a)
            if len(shared) >= 2 and not connected:
                flags.append((a, b, sorted(shared)))
    return flags
```

### Step 6 — Aggregate score (penalize-don't-skip throughout)
```python
def score_claim(claim: dict, run_a: dict, run_b: dict) -> float:
    if "Falsification criteria" not in claim["present_fields"] or "Dependencies" not in claim["present_fields"]:
        return 0.0  # hard fail: field absent, never averaged away
    if not run_a["well_formed"] or not run_b["well_formed"]:
        return 0.0
    if run_a["g_relation_to_notF"] == "neither":
        return 0.1  # formalizable statement, but falsification criteria don't actually falsify it
    stab = stability_score(run_a, run_b)
    relation_bonus = 1.0 if run_a["g_relation_to_notF"] == "negation" else 0.6
    ambiguity_penalty = max(0.0, 1.0 - 0.15 * len(run_a["ambiguous_terms"]))
    return max(0.0, min(1.0, stab * relation_bonus * ambiguity_penalty))

def m09_score(claims: list[dict], formalizations: dict, g: nx.DiGraph) -> dict:
    per_claim = {c["id"]: score_claim(c, formalizations[c["id"]]["run_a"], formalizations[c["id"]]["run_b"])
                 for c in claims}
    claim_avg = sum(per_claim.values()) / max(len(per_claim), 1)

    integrity = graph_integrity(g)
    dag_penalty = 1.0 if integrity["is_dag"] else 0.0            # cycles = hard fail on graph-cleanliness
    dangling_penalty = 1.0 if not integrity["dangling_refs"] else 0.0

    violations = status_consistency(claims, g)
    consistency_penalty = max(0.0, 1.0 - 0.25 * len(violations))

    missing_edges = missing_edge_candidates(claims, formalizations, g, sem_similarity=None)
    fragmentation_penalty = max(0.0, 1.0 - 0.1 * len(missing_edges))

    # A claims.md with a single claim and no possible Dependencies structure cannot demonstrate
    # graph-cleanliness at all -- this is scored down, not excluded (thin-input penalty, Sec 4).
    thinness_penalty = min(1.0, len(claims) / 5.0)

    graph_score = dag_penalty * dangling_penalty * consistency_penalty * fragmentation_penalty * thinness_penalty

    final = 0.6 * claim_avg + 0.4 * graph_score
    return {"final": round(final, 3), "claim_avg": claim_avg, "graph_score": graph_score,
            "violations": violations, "missing_edges": missing_edges, "integrity": integrity}
```

Weighting (0.6 formalizability / 0.4 graph-cleanliness) reflects that a paper can still show partial
FOL-ability with a thin dependency structure, but a broken graph (cycles, dangling refs, status
contradictions) caps the score hard via multiplicative penalties rather than being averaged away by
good per-claim formalization — consistent with penalize-don't-skip.

## 4. Handling missing/thin inputs (hard constraint)

`claims.md` is mandatory core and never fully absent (per the shape doc), so this metric never has a
true N/A case — but degraded inputs are common and must degrade the score, not disappear from it:

- **No `Dependencies` anywhere** (compiler wrote `Dependencies: none` for every claim): graph is
  edgeless. `graph_integrity` trivially passes (no cycles, no dangling refs possible), which would
  wrongly look "clean" — this is why Step 5's missing-edge detection exists specifically to catch
  this gaming route and apply `fragmentation_penalty` instead of a false-clean pass.
- **Missing `Falsification criteria` on any claim**: `score_claim` returns a hard `0.0` for that
  claim, dragging `claim_avg` down — never excluded from the denominator.
- **Abstract-only / thin compilation** (per shape doc's availability notes — few claims, weak
  evidence basis): `thinness_penalty` explicitly caps `graph_score` when `len(claims) < 5`, so a
  1–2-claim compilation cannot reach a high M09 score even if those one or two claims formalize
  cleanly — a thin artifact must read as materially worse, not merely "not applicable."
- **LLM formalizer failure/timeout on a claim**: treated as `well_formed=False` → claim scores 0, not
  dropped from the average (see `formalize_claim`'s guard clause and `score_claim`'s hard-fail path).

## 5. Why this is hard to Goodhart

- **Logic-flavored prose doesn't help**: Step 1's prompt explicitly forbids inventing predicates not
  present in `Statement`, so decorative "∀x..." phrasing with no real structure fails `well_formed`
  rather than being rewarded for *looking* formal.
- **Trivial "Dependencies: none" everywhere doesn't help**: Step 5's semantic missing-edge detector
  penalizes exactly this evasion by comparing predicate overlap independent of what the compiler
  declared, so avoiding cycles by avoiding edges altogether is caught as fragmentation, not cleanliness.
- **A lenient/sycophantic formalizer can't single-handedly inflate the score**: Step 2's stability
  re-run requires two independent formalization passes to agree on both predicate structure and the
  F/¬F relation; hallucinated or inconsistent formalizations fail to reproduce and are scored down via
  `stability_score`.
- **Status-gaming (mark everything `hypothesis` to dodge contradiction detection) is visible
  elsewhere**: an all-`hypothesis` claims file trivially "passes" Step 4 (no supported/refuted
  contradictions possible), but it also means no claim can score above the `hypothesis` ceiling
  implied by weak `g_relation_to_notF` outcomes typical of unresolved claims, and it will read as
  anomalous against the artifact shape's own note that `Status` "skews heavily to `supported`" in
  practice — a downstream/paired metric on claim-status distribution (outside this metric's scope) is
  the natural cross-check, discussed next.
- **No single artifact field can be edited in isolation to raise the score**: raising it requires
  jointly consistent `Statement`, `Falsification criteria`, and `Dependencies` across the whole claims
  file — a compiler would have to actually build a coherent logical structure, which is the behavior
  this metric is designed to reward.

## 6. Composition with the rest of the suite

This metric is deliberately narrow and does not re-check what grounding/citation metrics already
check (`Sources` verbatim-quote validity, numeric traceability) — it consumes the *existence* of
`Sources` only insofar as `Proof`/predicate groundedness could feed a future enrichment (noted in
Step 4) but does not re-score grounding itself. It is orthogonal to prose-quality metrics scoring
`Evidence basis`/`Interpretation` separation, and orthogonal to any experiment-level reproducibility
metric (it never inspects `logic/experiments.md`, only claim-to-claim structure). Its only shared
surface with another likely metric is `Status` distribution sanity (flagged above as a natural
external cross-check, not something this metric double-counts). Because it operates purely on
`claims.md`'s declared logical scaffolding (`Statement`, `Falsification criteria`, `Dependencies`) and
produces a graph-theoretic + symbolic-consistency signal, it adds a distinct axis — *is the paper's
claim structure provable* — that nothing else in the suite currently measures.
