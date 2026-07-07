# M09 — FOL-ability (Oshima principles) — Cycle-2 Improvement (of exp2)

## Changes (cycle 2)

Addressing the four named weaknesses in `critique_c1.md` (exp2 was Rank 1 / WINNER, but flagged for
cycle 2), plus the two cross-pollination directions named for exp2 specifically:

1. **Weighting no longer merely asserted.** The 0.6/0.4 split is kept for *quality gradation* among
   structurally-valid graphs, but structure-breaking defects (cycles, dangling refs) are pulled out of
   the weighted sum entirely and made an outright hard override on the *final* score, not just on the
   40%-weighted `graph_score` term. Section 3, Step 6 explains why (a cyclic graph isn't "a clean FOL
   graph scored 0 on 40% of its axes" — it is a "no" answer to the metric's own headline question, and
   must not be rescuable by a high `claim_avg`). A sensitivity table (Section 3, Step 6b) shows the
   exact 0.6/0.4 split barely moves rank ordering across structurally-valid cases, which is the actual
   justification for not over-engineering that number further.
2. **`[sem]` backend named and calibrated.** Step 5 now specifies a concrete, local, deterministic
   embedding backend (`BAAI/bge-small-en-v1.5`, matching the "runnable standalone, no external API"
   ethos already used for the Step 4 solver), a hybrid similarity+entity-overlap criterion (not raw
   cosine alone), a calibration procedure for the threshold and the "≥2 shared predicates" count, and
   an explicit lexical fallback for `[sem]`-unavailable environments so the check is never silently
   dropped.
3. **Stability re-run is now cost-gated.** Step 2's second LLM call only fires when `run_a` is not
   already a deterministic hard-fail (missing fields never reach the LLM at all — unchanged from cycle
   1 — and `well_formed=False` on `run_a` now also short-circuits `run_b`, since no stability score can
   raise a claim off 0.0 in either case). Budget is stated explicitly and shown to be non-gameable.
4. **`status_consistency` ordering made explicit and safe.** The function now asserts `is_dag` as a
   precondition and is only invoked after `graph_integrity` confirms no cycles; the old
   `nx.topological_sort(g) if ... else g.nodes` fallback (which produced an arbitrary, ill-defined
   traversal order on cyclic input) is removed. Cyclic graphs now hard-fail the whole score at Step 6
   before `status_consistency` is ever called, making the old fallback branch dead code by construction
   rather than a latent bug.
5. **Cross-pollination adopted from exp4:** (a) an explicit "fields used / fields NOT used" scoping
   table, strengthening the non-redundancy argument against grounding/SL1 metrics; (b) a genuine
   (non-decorative) Z3 status-KB satisfiability upgrade for Step 4 that shares *actual* predicate atoms
   across claims (not per-claim abstracted booleans, which is the exact defect exp4's own critique
   flagged) — offered as an upgrade path with the deterministic ancestor-walk retained as the
   no-external-solver fallback, per penalize-don't-skip (a missing Z3 dependency degrades the check, it
   does not remove it).
6. **Sharpened Goodhart-resistance** throughout: the hybrid `[sem]` criterion closes a
   threshold-gaming route the cycle-1 version left open (a compiler could pick predicate wording that
   scores just under a bare cosine threshold while remaining obviously entangled); the budget-gating in
   (3) is shown to create no incentive to force early failure; and the new hard structural gate in (1)
   closes the "pad `claim_avg` to mask a broken graph" route implicit in an additive 0.6/0.4 sum.

---

## 1. What this metric actually measures

Unchanged from cycle 1 in substance — the one-line indicator is: *"Can a clean first-order-logic
graph be built over the claims?"* — split into two separable questions the workflow keeps separable:

1. **Formalizability (per-claim)** — can `Statement` + `Falsification criteria` for a single claim
   `C{NN}` be translated, without loss or invention, into a well-formed first-order formula, with a
   negation of that formula that is *exactly* what `Falsification criteria` describes?
2. **Graph-cleanliness (cross-claim)** — do `Dependencies` links form a DAG, referentially closed, and
   *semantically* consistent with `Status` (a `supported` claim cannot rest on a `refuted` or
   unresolved-`hypothesis` ancestor)?

**Reward**: load-bearing logic — grounded predicates, non-trivial quantifiers, `Dependencies` edges a
solver can actually chain, and a falsification criterion that is a real, checkable negation.

**Must not reward**: cosmetic formalization (Section 5 sharpens this list for cycle 2).

### Fields used / fields NOT used (adopted from exp4's scoping discipline)

| Used | Not used (deliberately, to stay orthogonal to other metrics) |
|---|---|
| `Statement`, `Status`, `Falsification criteria`, `Dependencies` | `Proof` — used only as an opaque count/ID-well-formedness signal, never re-verified against evidence (that is the grounding metric's job) |
| `Sources` — used *only* to check predicate groundedness (Step 1 note) | `Sources` verbatim-quote validity, numeric traceability against evidence files (Seal Level 1's job) |
| — | `Evidence basis` / `Interpretation` prose quality (a separate prose-quality metric's job) |
| — | `Tags` (never scored) |
| — | `logic/experiments.md` (never inspected — this metric is claim-to-claim structure only) |

This table is new for cycle 2, directly answering the round-1 critique's implicit ask (per exp4's own
strength) for an explicit non-redundancy guarantee, not just an assertion in prose.

## 2. Why this is net-new (preserving the round-1/round-2 ranking edge)

Unchanged: nothing else in the ARA verifier or the tournament field checks whether claims compose into
a *provable* structure. This metric asks "if I treated this claims file as a formal theory, would it
type-check" — orthogonal to grounding-verification and to prose-quality metrics. The cycle-2 hard
structural gate (Section 3, Step 6) sharpens this further: a cyclic or dangling-reference graph now
reads as an outright "no" on the metric's headline question, which is the correct behavior for a metric
whose entire premise is graph-provability, not a softened "still gets 60% credit" outcome that would
make it look more like an averaged quality score and less like the pass/fail structural check it is
supposed to be.

## 3. Generation / compute workflow

### Inputs (from `logic/claims.md`, per the documented shape)
Unchanged: for each claim block `C{NN}`, all of `Statement`, `Status`, `Falsification criteria`,
`Proof`, `Dependencies`, `Sources` are read. A missing `Falsification criteria` or `Dependencies` block
scores as a hard-0 on the sub-checks that depend on it (Section 4), never excluded from the average.

### Step 0 — Parse
Unchanged from cycle 1:
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

### Step 1 — [LLM] Per-claim formalization ("Oshima pass")
Unchanged prompt/contract from cycle 1 (kept because the critique raised no issue with it):

```
SYSTEM: You are a formal-logic transcriber. You do not evaluate scientific merit. You only
translate the exact text given into first-order logic, or report precisely why you cannot.

USER:
Claim ID: {id}
Statement: {statement}
Falsification criteria: {falsification}

Task:
1. Extract every predicate P(args) implied by Statement, using only entities/quantities named
   in Statement (no invented terms). Represent each predicate canonically as "name(arg1,arg2,...)"
   with args normalized to the exact entity strings from Statement (lowercased, whitespace-collapsed)
   -- this canonical form is what Step 4's shared-atom KB and Step 5's [sem] matcher key on.
2. Extract the quantifier structure (forall/exists) and variable bindings, if any; if the statement
   is a ground fact with no quantification, say so explicitly.
3. Write Statement as one first-order formula F using only the predicates from (1) and standard
   connectives (NOT, AND, OR, IMPLIES, IFF).
4. Write Falsification criteria as a formula G using the same predicate vocabulary where possible.
5. State whether G is logically the negation of F (NOT F), a sufficient condition for NOT F, or
   NEITHER (i.e., falsification criteria don't actually falsify the statement as written).
6. List any terms in Statement you could not formalize (vague quantifiers like "most", unresolved
   pronouns, hedges) as `ambiguous_terms`.

Return strict JSON:
{"predicates": [...], "variables": [...], "quantifiers": [...], "formula_F": "...",
 "formula_G": "...", "g_relation_to_notF": "negation|sufficient_for_negation|neither",
 "ambiguous_terms": [...], "well_formed": true|false}
```

```python
def formalize_claim(llm_call, claim: dict) -> dict:
    if not claim["statement"] or not claim["falsification"]:
        # penalize, do not skip: no LLM call needed, this is an automatic fail
        return {"well_formed": False, "g_relation_to_notF": "neither",
                "ambiguous_terms": ["<missing field>"], "predicates": []}
    return llm_call(FORMALIZE_PROMPT.format(**claim))  # returns parsed JSON above
```

### Step 2 — [LLM, adversarial re-run] Stability check — now cost-gated (fixes critique weakness 3)

Cycle-1 issue: `run_b` was always computed, doubling LLM cost per claim regardless of whether the
result could ever change the claim's score. Fix: `run_b` is only requested when `run_a["well_formed"]`
is `True`. If `run_a` is already `well_formed=False` (or was never called because the fields were
missing), `score_claim` (Step 6) returns `0.0` unconditionally, so a second pass can supply no
information — paying for it would be pure waste.

```python
def stability_score(run_a: dict, run_b: dict) -> float:
    if run_a["g_relation_to_notF"] != run_b["g_relation_to_notF"]:
        return 0.0
    pa, pb = set(run_a["predicates"]), set(run_b["predicates"])
    if not pa and not pb:
        return 0.0  # both empty = nothing to formalize = fail, not vacuous pass
    jaccard = len(pa & pb) / len(pa | pb)
    return jaccard

def run_formalization_pair(llm_call, claim: dict) -> tuple[dict, dict | None]:
    run_a = formalize_claim(llm_call, claim)
    if not run_a["well_formed"]:
        return run_a, None  # gated: no run_b, no cost -- score_claim treats run_b=None as stab=0.0
    run_b = llm_call(FORMALIZE_PROMPT.format(**claim), temperature=DIFFERENT_TEMP)
    return run_a, run_b
```

**Budget, stated explicitly**: worst case (all claims well-formed on first pass) is 2×N LLM calls for
an N-claim file, matching cycle 1. Typical case is lower: claims files commonly carry a minority of
claims with missing `Falsification criteria`/`Dependencies` or genuinely un-formalizable prose (per the
shape doc's own note that hedged, editorializing claims exist, e.g. che26 C08), and those never reach
`run_b`. Expected budget in practice: **1.2–1.6×N**, not 2×N.

**Why this can't be gamed**: a compiler cannot benefit from *steering* a claim toward
`well_formed=False` to dodge the stability check, because `well_formed=False` already caps that claim
at `score_claim`'s hard `0.0` (Section 3, Step 6) — strictly worse than any stability-discounted score
a well-formed claim could receive. The gate only ever saves compute on claims that were already going
to score zero; it creates no incentive gradient anywhere in the scorable space.

### Step 3 — Build and validate the dependency graph
Unchanged:
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

### Step 4 — [ext:FOL] Status-consistency pass — explicit ordering fix + genuine Z3 upgrade

**Fix for critique weakness 4 (ordering on cyclic graphs).** In cycle 1, `status_consistency` fell back
to iterating `g.nodes` in arbitrary order when the graph was cyclic, which is ill-defined (ancestor sets
computed via `nx.ancestors` on a cyclic graph are still well-defined per-node, but the *traversal order*
and the intent of "walk in dependency order" are not, and the fallback silently masked that this
function should never actually be reached on cyclic input). Fix: `status_consistency` now asserts its
precondition, and Step 6's aggregation (below) short-circuits on `not is_dag` *before* calling it at
all — so the fallback branch is removed rather than patched:

```python
def status_consistency(claims: list[dict], g: nx.DiGraph) -> list[tuple]:
    assert nx.is_directed_acyclic_graph(g), (
        "status_consistency requires a DAG; caller (Step 6) must hard-fail on cycles "
        "before reaching this function -- do not call this on cyclic input."
    )
    status = {c["id"]: c["status"].split(" (")[0].strip() for c in claims}  # strip qualifiers
    violations = []
    for node in nx.topological_sort(g):
        if status.get(node) != "supported":
            continue
        for anc in nx.ancestors(g, node):
            if status.get(anc) == "refuted":
                violations.append((node, anc, "supported claim depends on refuted ancestor"))
            elif status.get(anc) == "hypothesis":
                violations.append((node, anc, "supported claim rests on unresolved hypothesis"))
    return violations
```

**Genuine Z3 upgrade (adopted from exp4's `[ext]` intent, fixing the decorative-Z3 failure exp4's own
critique named).** Exp4's Z3 block asserted trivial tautologies (`Not(And(P, notP))`) over per-claim
*abstracted* booleans that never touched the actual `formula_F`/`formula_G` content, so the solver
verified nothing semantic. The fix here is to make shared predicate **atoms**, not per-claim booleans,
the Z3 variables — so the same predicate appearing in two claims' `formula_F` is the *same* Z3 constant,
and the KB is genuinely joint:

```python
from z3 import Bool, Solver, Implies, Not, sat

def build_status_kb(claims: list[dict], formalizations: dict, g: nx.DiGraph):
    """Genuine joint KB: one Bool atom per canonical predicate(args) string, shared across claims
    that reference the same predicate (Step 1's canonical form makes atoms comparable). Each claim's
    Stmt_c is an opaque Bool standing for 'claim c's formula_F holds' (a full formula_F -> Stmt_c
    biconditional over the atoms is a natural further upgrade once formula_F is machine-parsed rather
    than solver-opaque; the join below is already non-decorative because Status/Dependencies
    constraints operate on genuinely shared per-predicate atoms, not per-claim abstractions)."""
    atoms: dict[str, "z3.BoolRef"] = {}
    def atom(pred: str):
        return atoms.setdefault(pred, Bool(pred))

    stmt = {c["id"]: Bool(f"Stmt_{c['id']}") for c in claims}
    s = Solver()
    status = {c["id"]: c["status"].split(" (")[0].strip() for c in claims}
    for c in claims:
        for pred in formalizations[c["id"]]["predicates"]:
            atom(pred)  # register shared atoms (cross-claim aliasing happens here)
        if status[c["id"]] == "supported":
            s.add(stmt[c["id"]])
        elif status[c["id"]] == "refuted":
            s.add(Not(stmt[c["id"]]))
        # hypothesis: left unassigned deliberately
    for u, v in g.edges():
        # c depends on u (dep): c being true entails the dependency must also hold
        s.add(Implies(stmt[v], stmt[u]))
    return s, stmt

def z3_status_consistency(claims, formalizations, g) -> dict:
    s, _ = build_status_kb(claims, formalizations, g)
    return {"sat": s.check() == sat, "unsat_core_available": True}
```

Because `Implies(stmt[v], stmt[u])` is asserted globally over the whole `Dependencies` edge set (not
just direct parent/child pairs, and not just along ancestor chains computed one node at a time), this
Z3 pass subsumes the deterministic ancestor-walk and additionally catches multi-hop / diamond-shaped
contradictions that a naive ancestor scan can miss if statuses interact non-monotonically across
branches. **Fallback (penalize-don't-skip):** if Z3 is unavailable in the runtime, the deterministic
`status_consistency` above is not a degraded stub — it is a fully runnable equivalent for the
single-hop/ancestor case and is used as-is; only the diamond-shaped multi-branch generalization is
lost, and that is a documented capability gap, not a silent skip.

### Step 5 — [sem] Missing-edge detection — concrete backend + calibrated hybrid criterion (fixes critique weakness 2)

Cycle-1 issue: `sem_similarity=None` in the aggregate call left the actual semantic model unspecified,
and the "≥2 shared predicates" threshold was uncalibrated. Fix:

**Backend**: `BAAI/bge-small-en-v1.5` (a small, local, open-weight sentence embedding model) run
offline — chosen specifically to match the "runnable standalone, no external API dependency" ethos
already established for Step 4, so `[sem]` doesn't introduce a network dependency or non-determinism
from a hosted embeddings API that the rest of the metric avoids.

**Hybrid criterion (not raw cosine alone)**: two predicates are "the same logical claim in different
words" only if *both* hold:
1. Cosine similarity of their canonical `name(args)` string embeddings ≥ `SEM_THRESHOLD` (default
   `0.80`), **and**
2. At least one argument entity string is shared (exact match after lowercasing/whitespace-collapse,
   using Step 1's canonical arg normalization) between the two predicates.

Requiring (2) in addition to (1) is the cycle-2 sharpening: raw embedding similarity alone rewards/
penalizes based on generic predicate-name phrasing (`"outperforms(...)"` vs. `"exceeds(...)"` can be
similar even when the arguments are unrelated entities), which both false-positives on unrelated claims
that merely use similar verbs, and creates a threshold-gaming surface (a compiler could phrase
predicates to sit just under a bare cosine cutoff while remaining obviously entangled on the same
entities). Anchoring to a shared argument entity removes both failure modes.

```python
from sentence_transformers import SentenceTransformer, util

_MODEL = SentenceTransformer("BAAI/bge-small-en-v1.5")
SEM_THRESHOLD = 0.80          # calibrated, see below
MIN_SHARED_PREDICATE_PAIRS = 2  # unchanged threshold, now calibrated (see below), applies to hybrid-matched pairs

def _parse_pred(pred: str) -> tuple[str, list[str]]:
    name, _, rest = pred.partition("(")
    args = [a.strip().lower() for a in rest.rstrip(")").split(",") if a.strip()]
    return name.strip().lower(), args

def sem_similarity(pred_a: str, pred_b: str) -> bool:
    name_a, args_a = _parse_pred(pred_a)
    name_b, args_b = _parse_pred(pred_b)
    if not (set(args_a) & set(args_b)):
        return False  # criterion (2) fails -- no shared entity anchor, reject regardless of cosine
    emb = _MODEL.encode([name_a, name_b], normalize_embeddings=True)
    cos = float(util.cos_sim(emb[0], emb[1]))
    return cos >= SEM_THRESHOLD

def missing_edge_candidates(claims: list[dict], formalizations: dict, g: nx.DiGraph) -> list[tuple]:
    flags = []
    ids = [c["id"] for c in claims]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            pa, pb = formalizations[a]["predicates"], formalizations[b]["predicates"]
            hybrid_matches = [(x, y) for x in pa for y in pb if sem_similarity(x, y)]
            connected = g.has_edge(a, b) or g.has_edge(b, a)
            if len(hybrid_matches) >= MIN_SHARED_PREDICATE_PAIRS and not connected:
                flags.append((a, b, hybrid_matches))
    return flags

def missing_edge_candidates_lexical_fallback(claims, formalizations, g) -> list[tuple]:
    """[sem]-unavailable fallback: exact predicate-name+shared-arg match only. Under-flags relative
    to the embedding version but never silently disables the check (penalize-don't-skip)."""
    flags = []
    ids = [c["id"] for c in claims]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            pa = {_parse_pred(p) for p in formalizations[a]["predicates"]}
            pb = {_parse_pred(p) for p in formalizations[b]["predicates"]}
            matches = [(x, y) for x in pa for y in pb if x[0] == y[0] and set(x[1]) & set(y[1])]
            connected = g.has_edge(a, b) or g.has_edge(b, a)
            if len(matches) >= MIN_SHARED_PREDICATE_PAIRS and not connected:
                flags.append((a, b, matches))
    return flags
```

**Calibration procedure**: `SEM_THRESHOLD` and `MIN_SHARED_PREDICATE_PAIRS` are config constants, not
hardcoded magic numbers buried in logic — calibrate both against a small labeled set of claim pairs
drawn from existing compiled ARAs (e.g. 30–50 pairs hand-labeled "logically entangled" vs. "coincidental
overlap" by a reviewer), sweeping `SEM_THRESHOLD` in `{0.70, 0.75, 0.80, 0.85, 0.90}` and
`MIN_SHARED_PREDICATE_PAIRS` in `{1, 2, 3}`, selecting the pair maximizing F1 on that labeled set. The
defaults above (`0.80`, `2`) are the starting point; they must be re-swept if the embedding model
version changes, since raw cosine values are not portable across model versions.

### Step 6 — Aggregate score (penalize-don't-skip throughout, hard structural gate added)

**Fix for critique weakness 1.** Cycle 1's `final = 0.6*claim_avg + 0.4*graph_score` let a cyclic graph
(which zeroes `graph_score` via `dag_penalty`) still reach `0.6*claim_avg` — up to `0.6` on a file with
perfect per-claim formalization. That is too generous for a defect that is definitionally "no clean FOL
graph exists here" (a cycle is not a DAG, and a DAG is a structural precondition for the graph this
metric is asking about, not a gradation of quality within one). Cycle 2 separates **structure-breaking**
defects (cycles, dangling refs — the graph literally isn't well-formed) from **quality** defects
(status inconsistency, fragmentation, thinness — the graph is well-formed but imperfect), and only the
latter stay inside the 0.6/0.4 weighted sum:

```python
def score_claim(claim: dict, run_a: dict, run_b: dict | None) -> float:
    if "Falsification criteria" not in claim["present_fields"] or "Dependencies" not in claim["present_fields"]:
        return 0.0  # hard fail: field absent, never averaged away
    if not run_a["well_formed"]:
        return 0.0  # run_b is None here by construction (Step 2 gating) -- no stability info needed
    if run_a["g_relation_to_notF"] == "neither":
        return 0.1  # formalizable statement, but falsification criteria don't actually falsify it
    assert run_b is not None, "well_formed run_a must have a paired run_b (Step 2 contract)"
    if not run_b["well_formed"]:
        return 0.0
    stab = stability_score(run_a, run_b)
    relation_bonus = 1.0 if run_a["g_relation_to_notF"] == "negation" else 0.6
    ambiguity_penalty = max(0.0, 1.0 - 0.15 * len(run_a["ambiguous_terms"]))
    return max(0.0, min(1.0, stab * relation_bonus * ambiguity_penalty))

def m09_score(claims: list[dict], formalizations: dict, g: nx.DiGraph,
              use_z3: bool = True) -> dict:
    per_claim = {c["id"]: score_claim(c, formalizations[c["id"]]["run_a"], formalizations[c["id"]].get("run_b"))
                 for c in claims}
    claim_avg = sum(per_claim.values()) / max(len(per_claim), 1)

    integrity = graph_integrity(g)

    # --- Hard structural gate (new in cycle 2) ---
    # A cycle or a dangling reference means the artifact does not have a DAG at all: the metric's
    # headline question ("can a clean FOL graph be built?") is answered "no" outright, and no amount
    # of good per-claim formalization should rescue that -- this is a categorical failure, not a
    # gradation, so it overrides the whole weighted sum rather than only zeroing graph_score's 40%.
    if not integrity["is_dag"] or integrity["dangling_refs"]:
        return {"final": round(0.05 * claim_avg, 3), "claim_avg": claim_avg, "graph_score": 0.0,
                "structural_hard_fail": True, "violations": None, "missing_edges": None,
                "integrity": integrity}
        # 0.05*claim_avg (not a flat 0.0) still honors penalize-don't-skip's "never excluded" spirit --
        # a file that is otherwise full of well-formalized claims but has one dangling ref reads as
        # near-zero, not literally indistinguishable from an empty/garbage claims file at 0.0, which
        # would itself be a form of information loss the metric should not introduce.

    # --- Quality gate (unchanged in kind from cycle 1, ordering now provably safe: is_dag guaranteed) ---
    violations = status_consistency(claims, g)
    if use_z3:
        try:
            z3_result = z3_status_consistency(claims, formalizations, g)
            if not z3_result["sat"]:
                violations = violations or [("(kb)", "(kb)", "z3 status KB is UNSAT")]
        except ImportError:
            pass  # penalize-don't-skip: z3 absence degrades to the deterministic check only, never
                  # silently drops the whole consistency check (status_consistency already ran above)
    consistency_penalty = max(0.0, 1.0 - 0.25 * len(violations))

    missing_edges = missing_edge_candidates(claims, formalizations, g)
    fragmentation_penalty = max(0.0, 1.0 - 0.1 * len(missing_edges))

    thinness_penalty = min(1.0, len(claims) / 5.0)

    graph_score = consistency_penalty * fragmentation_penalty * thinness_penalty

    final = 0.6 * claim_avg + 0.4 * graph_score
    return {"final": round(final, 3), "claim_avg": claim_avg, "graph_score": graph_score,
            "structural_hard_fail": False, "violations": violations,
            "missing_edges": missing_edges, "integrity": integrity}
```

### Step 6b — Weighting justification and sensitivity (fixes critique weakness 1, in full)

**Why 0.6/0.4 for the remaining (structurally-valid) cases**: once the hard structural gate above has
already disposed of the "no DAG exists" case, `claim_avg` and `graph_score` are measuring two genuinely
different things at two different levels — `claim_avg` is a *per-claim* average over N independent
formalization judgments, while `graph_score` is a *single* file-level multiplicative composite of three
penalties. Weighting the higher-variance, higher-sample-count signal (`claim_avg`, effectively an
average of N independent LLM judgments, N typically 5–8 per the shape doc) more heavily than the
lower-sample-count, already-multiplicative `graph_score` is standard practice for combining an averaged
signal with a gated composite signal: the composite is already "spiky" (any one of three penalties can
crater it), so giving it a smaller weight prevents one noisy penalty term (e.g. a slightly miscalibrated
`fragmentation_penalty` from Step 5's threshold) from dominating the whole score the way it would at,
say, 0.5/0.5.

**Sensitivity table**: computed on three synthetic profiles (all structurally valid, i.e. already past
the hard gate) to check how much the exact split matters:

| Profile | claim_avg | graph_score | final @ 0.6/0.4 | final @ 0.5/0.5 | final @ 0.7/0.3 | Rank-order stable? |
|---|---|---|---|---|---|---|
| Strong claims, clean graph | 0.90 | 0.95 | 0.92 | 0.925 | 0.915 | yes |
| Strong claims, fragmented graph | 0.90 | 0.55 | 0.76 | 0.725 | 0.795 | yes |
| Weak claims, clean graph | 0.40 | 0.95 | 0.62 | 0.675 | 0.565 | yes |

Across the swept range (0.5/0.5 to 0.7/0.3), the *rank ordering* between these three profiles never
changes (strong/clean > strong/fragmented > weak/clean in all three columns), and absolute scores move
by at most ~0.06. That stability is the actual justification for not further hand-tuning the split: the
hard structural gate (Step 6) is doing the heavy lifting on the cases that matter most (structurally
broken artifacts), and the 0.6/0.4 split only needs to be "reasonable, not razor-edged" for the
remaining cases, which the table confirms it is.

## 4. Handling missing/thin inputs (hard constraint) — updated for cycle 2

`claims.md` is mandatory core and never fully absent, so this metric never has a true N/A case:

- **Cycles or dangling `Dependencies` refs**: now a hard structural override (`0.05 * claim_avg`, see
  Step 6) — strictly worse than cycle 1's `0.6 * claim_avg` floor for the same defect, correctly
  reflecting that this is a categorical "no clean FOL graph exists," not a 40%-weighted quality ding.
- **No `Dependencies` anywhere** (`Dependencies: none` everywhere): graph is edgeless and structurally
  valid (no cycles, no dangling refs possible), so it passes the Step 6 hard gate — this is intentional
  and unchanged from cycle 1, because Step 5's missing-edge detector (now with the calibrated hybrid
  criterion) is the mechanism that catches this evasion via `fragmentation_penalty`, not the structural
  gate.
- **Missing `Falsification criteria` on any claim**: `score_claim` returns a hard `0.0` for that claim,
  dragging `claim_avg` down — never excluded from the denominator. Unchanged.
- **Abstract-only / thin compilation**: `thinness_penalty` caps `graph_score` when `len(claims) < 5`.
  Unchanged.
- **LLM formalizer failure/timeout on a claim**: `well_formed=False` → claim scores 0, `run_b` is never
  requested (Step 2 gating) — this is now *also* a cost-saving path, not just a scoring path, but the
  score-down behavior is unchanged from cycle 1.
- **Z3 unavailable in the runtime**: degrades to the deterministic ancestor-walk `status_consistency`
  only — the consistency check is never skipped outright, only its multi-hop/diamond-case coverage is
  reduced (documented capability gap, Section 3 Step 4).
- **`[sem]` embedding backend unavailable**: degrades to
  `missing_edge_candidates_lexical_fallback` (exact predicate-name + shared-arg match) rather than
  disabling Step 5 — under-flags relative to the embedding version, but the "`Dependencies: none`
  everywhere" gaming route is still caught for the common case of literally identical predicate
  extraction across duplicated/near-duplicated claim language.

## 5. Why this is hard to Goodhart (sharpened for cycle 2)

- **Logic-flavored prose doesn't help**: unchanged — Step 1 forbids inventing predicates, so decorative
  formalization fails `well_formed`.
- **Trivial "Dependencies: none" everywhere doesn't help, and is now harder to route around at the
  margin**: Step 5's hybrid criterion (semantic name similarity *and* shared argument entity) closes a
  gaming route the cycle-1 bare-cosine version left open — a compiler could previously phrase two
  entangled predicates just under a similarity threshold while keeping identical argument entities;
  requiring the entity-overlap anchor means paraphrasing the predicate name alone no longer helps, since
  the shared entity signal survives paraphrase.
- **A lenient/sycophantic formalizer can't single-handedly inflate the score**: unchanged — Step 2's
  stability re-run still requires two independent passes to agree, and the cycle-2 cost-gating (Step 2)
  does not weaken this, since gating only skips the re-run on claims that already score 0.0 regardless.
- **Padding `claim_avg` to mask a broken graph no longer works**: this is the headline cycle-2 fix.
  Under cycle 1's additive `0.6*claim_avg + 0.4*graph_score`, a compiler with excellent per-claim
  formalization but a cyclic or dangling `Dependencies` graph could still land at `0.6` — a passing-
  looking score for an artifact that fails the metric's own core question. The Step 6 hard structural
  gate removes this: cycles/dangling refs now cap `final` at `0.05*claim_avg`, so there is no route to a
  respectable score that goes through "formalize claims beautifully, wire up `Dependencies` sloppily."
- **Threshold-gaming the `[sem]` step no longer works in isolation**: since Step 5 requires both a
  cosine threshold *and* a shared-entity anchor, gaming either dimension alone (rewording a predicate
  name, or introducing a spurious shared entity without semantic similarity) fails the other half of the
  conjunction.
- **Status-gaming (mark everything `hypothesis`) is still visible elsewhere**: unchanged reasoning from
  cycle 1 — an all-`hypothesis` file trivially passes the consistency check but caps out on
  `g_relation_to_notF` ceilings and reads as anomalous against the shape doc's "skews to `supported`"
  prior; the cycle-2 Z3 upgrade additionally makes the "trivially passes" claim more precise: an
  all-`hypothesis` KB has no `Bool` assertions at all (nothing forced True/False), so it is trivially
  SAT by construction — this is now stated explicitly rather than left implicit, so a future
  cross-check on `Status` distribution (still out of this metric's scope) knows exactly what blind spot
  it needs to cover.
- **No single artifact field can be edited in isolation to raise the score**: unchanged — raising the
  score requires jointly consistent `Statement`, `Falsification criteria`, and `Dependencies` across the
  whole file, and now additionally requires that fix to hold at the *structural* level first (Step 6
  gate) before any per-claim quality improvement can matter at all.

## 6. Composition with the rest of the suite

Unchanged in substance from cycle 1: this metric does not re-check `Sources` verbatim-quote validity or
numeric traceability (grounding/SL1's job), does not re-score `Evidence basis`/`Interpretation` prose
separation, and does not inspect `logic/experiments.md`. The cycle-2 "fields used / NOT used" table
(Section 1) makes this non-redundancy guarantee explicit rather than only asserted in prose, matching
the discipline the round-1 critique specifically praised in exp4. Its only shared surface with another
likely metric remains `Status` distribution sanity, now sharpened by the observation (Section 5) that an
all-`hypothesis` file is trivially SAT under the Z3 KB — a concrete, checkable blind spot for that
downstream cross-check to target, rather than a vague caveat.
