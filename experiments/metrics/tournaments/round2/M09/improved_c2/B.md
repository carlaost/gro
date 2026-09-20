## Changes (cycle 2)

This is a targeted revision of exp4 (Rank 2, WINNER) addressing all four named weaknesses from
`critique_c1.md`, plus the cross-pollination note, without touching what already won:

1. **Fixed the decorative Z3 negation check (critique weakness 1 — the important one).** The old
   `negation_consistent()` built two *unrelated* opaque booleans (`P_{id}`, `notP_{id}`) and asked
   Z3 to verify they were each other's negation "by construction" — trivially `sat` no matter what
   `predicate_form`/`negation_form` actually said. Cycle 2 replaces this with a real recursive-descent
   parser for a formally specified ASCII-FOL grammar, a finite-domain quantifier grounder (domain =
   the claim's own `constants`, typed via `variables`), and a Z3 encoding where **identical atoms in
   `predicate_form` and `negation_form` are mapped to the identical Z3 `Bool`** via a shared atom
   cache. The solver now checks `UNSAT(P ∧ N)` and `UNSAT(¬P ∧ ¬N)` (i.e. `P ∨ N` valid) against the
   *actual parsed content* of both formulas — not a bookkeeping tautology. Ungroundable quantifiers
   (a bound variable with no matching domain) are a new explicit failure mode, penalized (0.05), not
   silently skipped.
2. **Added the missing `[sem]` leg (critique weakness 2), deterministically.** Rather than bolting on
   an unspecified embedding/cosine-similarity backend (the exact thing cycle-1 critique flagged as
   underspecified in exp2), `missing_edge_penalty()` reuses the atom/constant structures the metric
   *already parsed* in step 3–4 — no new external call, no new nondeterminism. It flags a pair of
   claims with no declared `Dependencies` edge as a "hidden entanglement" candidate only when they
   share a **precise numeric constant** (a load-bearing statistic, not a recurring entity name like a
   compound or gene) at ≥3 significant digits, or ≥2 shared numeric constants at any precision — the
   calibration argument and its rejection of the embedding-backend alternative are in §4. This closes
   exactly the "mark every claim `Dependencies: none`" gaming route the critique named, and it composes
   as a multiplicative fragmentation penalty in the same style as the other graph-level multipliers.
3. **Tightened `constants_grounded` to boundary-safe matching (critique weakness 3).** Replaced the
   `c in s or s in c` substring test (which false-positives, e.g., `"0.1"` matching inside `"0.117"`)
   with `_boundary_match()`, which rejects a match flanked by a digit or `.` on either side, so partial
   numeral collisions no longer count as grounded.
4. **Injected the translator call for testability (critique weakness 4), and used the same seam to add
   a budget-gated stability check** (the cross-pollination note: borrow exp2's stability re-run, but
   respect exp2's own critique that it doubles cost unconditionally). `score_M09` now takes a
   `translate: Callable[[Claim, int], FOLTranslation]` parameter (variant `0` = primary call, `1` =
   re-run at a different temperature/paraphrase), decoupling scoring from the LLM client exactly as
   exp3 did. The re-run only fires for claims that land in the **borderline band** after the first
   pass (attempted-but-imperfect: malformed, negation-inconsistent, or partially grounded — i.e.
   scores in `[0.05, 0.8)`); a clean pass (`>=0.8`) or a hard refusal (`0.0`) never triggers a second
   LLM call. If the re-run's predicate relation-symbols diverge (Jaccard `< 0.5`) or the
   negation-consistency verdict flips, the claim's score is capped at `0.15` — non-reproducible
   structure is itself evidence of formalization theater, penalized rather than trusted on the first
   roll. This bounds the added LLM cost to only the ambiguous middle of the distribution, which per the
   shape doc's own typical 5–8-claim, mostly-`supported` compilations should be a minority of claims.

Everything else — the scoping discipline (fields used/not-used), the per-claim score ladder's overall
shape, the dependency-DAG and status-consistency multipliers, the sparse-graph penalty, and the
penalize-don't-skip posture — is preserved from exp4 and, where the fixes above touch it, sharpened
rather than replaced.

---

# M09 — FOL-ability (Oshima principles) — Improved (cycle 2)

## 1. What this metric actually measures

The one-line indicator is: *"Can a clean first-order-logic graph be built over the claims?"*
Read literally against the `logic/claims.md` shape, this is **not** "does the paper sound
rigorous" — it is a narrower, mechanical question: can each claim's `Statement` be compiled into
a well-formed predicate-logic sentence whose negation is *exactly* the claim's own `Falsification
criteria`, and can the full set of claims (wired together via `Dependencies`) be composed into one
knowledge base without producing a contradiction, a cycle, or a hidden (undeclared) entailment?

That last clause — "hidden entailment" — is new in cycle 2 and closes a real gap: a claims graph
that is locally acyclic and consistent can still fail to be "a clean FOL graph" if two claims are
obviously logically entangled (one's predicate reuses another's concluded statistic as a premise)
but the compiler never declared the edge. A graph with invisible edges is not composable in any
honest sense, even if the visible subgraph checks out.

The "Oshima principle" this metric operationalizes, otherwise unchanged from cycle 1: a claim is
only as scientifically useful as its *formal decomposability* — subject/predicate/relation with
typed variables, bound quantifiers, and literal constants that trace back to `Sources`. A claim
that reads as confident prose but cannot be pinned to a predicate with a real, solver-checked
negation is doing rhetorical work, not evidentiary work, no matter how polished its `Evidence
basis` looks.

This metric stays scoped to that gap: Seal Level 1 checks field presence, the ARA verifier checks
grounding accuracy, neither checks whether the *content* is logically well-formed enough to reason
over mechanically or whether the *graph* is honestly wired. M09 only scores formal composability of
what's already there.

## 2. What it must reward vs. must not reward

**Reward:**
- Statements that decompose into a predicate over typed entities/constants with an explicit
  relation (ranking, comparison, threshold, count, hazard ratio, etc.).
- Falsification criteria that are the *actual, solver-verified logical negation* of the Statement's
  predicate — same relation symbols, same grounded atoms, provably `P ∧ ¬P` unsat and `P ∨ ¬P`
  valid over the claim's own finite constant domain.
- `Dependencies` chains that form a genuine implication graph, and that are declared *honestly* —
  if claim B's predicate reuses claim A's concluded statistic, the dependency should be visible in
  the metadata, not just recoverable after the fact by re-parsing the formulas.
- Numeric/entity constants in the formalized predicate that are traceable to a `Sources` entry via
  a boundary-safe match (not a substring collision).

**Must not reward:**
- Claims that are trivially "FOL-able" because they're boolean and empty of content — the scorer
  zeroes out claims whose translation extracts no constants.
- Verbose or jargon-heavy Statements dressed up in logic notation without the notation being sound.
  Syntax validity, quantifier-groundability, and solver-checked negation-consistency are three
  separate gates, each necessary and none sufficient alone.
- A claims graph that games composability by declaring `Dependencies: none` everywhere while the
  underlying predicates are visibly entangled through shared concluded statistics — this is now an
  explicit, penalized failure mode (§3.4/§4 step 6), not a blind spot.
- Re-rewarding what Seal Level 1 / the verifier already reward (field presence, grounding
  correctness).

## 3. Failure modes / gaming routes and mitigations

1. **LLM self-grading its own translation.** Mitigation unchanged from cycle 1: the translator call
   *only* emits structured FOL text (`predicate_form`, `negation_form`, `constants`, `variables`);
   every scoring decision is made by separate deterministic code, never by asking the LLM to
   self-score.
2. **Padding with easy claims.** Mitigation unchanged: `constants_grounded` zeroes any translation
   with no constants; the sparse-graph penalty (§4 step 7) requires ≥3 genuinely clean claims before
   the mean is trusted at face value.
3. **Fake falsifiability (a topically-adjacent but not logically-negating Falsification
   criterion).** Cycle-1 mitigation was a lexical symbol-overlap check plus a Z3 call that verified
   nothing about the actual formulas. **Cycle-2 fix:** `negation_consistent()` now (a) still requires
   lexical relation-symbol overlap as a cheap pre-filter, then (b) parses both `predicate_form` and
   `negation_form` with the grammar in §4, (c) grounds any quantifiers over the claim's own constant
   domain, (d) maps identical grounded atoms to identical Z3 booleans via a shared cache, and (e)
   calls the solver on the *actual* parsed formulas to verify `UNSAT(P ∧ N)` and `UNSAT(¬P ∧ ¬N)`. A
   criterion that reuses different constants or a different relation for a "sounds-like-a-negation"
   sentence now fails at the solver step on its real content, not just on a name-overlap heuristic.
4. **Hidden circularity or dangling references in `Dependencies`.** Mitigation unchanged:
   `dependency_graph_multiplier()` is a whole-artifact multiplicative penalty for cycles/dangling IDs.
5. **Status/graph inconsistency.** Mitigation unchanged: `status_consistency_multiplier()` runs one
   global Z3 pass over the asserted KB (supported=True, refuted=False, hypothesis=unassigned, chained
   through `Dependencies`).
6. **Undeclared entanglement ("`Dependencies: none` everywhere" gaming route) — new in cycle 2.** A
   compiler can trivially pass checks 4–5 by never declaring a dependency edge at all, even when
   claim B's predicate visibly reuses claim A's concluded statistic as a premise constant. This was
   the one gaming route cycle-1's exp4 left open (and the one exp2 caught, at the cost of an
   unspecified/unbudgeted embedding backend and doubled LLM calls). Mitigation: `missing_edge_penalty()`
   (§4 step 6) is fully deterministic and reuses the atom/constant structures already produced by
   step 3–4 — no new LLM or embedding call. It flags a claim pair with no declared edge as a hidden-
   entanglement candidate when they share a precise numeric constant (see §4 calibration argument for
   why numeric, not entity-name, overlap is the right signal), and applies a multiplicative
   fragmentation penalty scaled by the candidate count.
7. **Non-reproducible ("rubber-stamped") formalization of a genuinely narrativized claim — new in
   cycle 2.** A lenient translator call can occasionally force a plausible-looking predicate onto a
   claim that is really too hedged/vague to formalize soundly, and that forced structure won't
   survive a re-ask. Mitigation: the budget-gated stability re-run (§4 step 4b) catches this for the
   claims where it matters (the borderline band) without doubling cost across the whole claim set.

## 4. Generation / compute workflow

### Inputs (artifact fields used — nothing else)
From `logic/claims.md`, per claim block: `Statement`, `Status`, `Falsification criteria`,
`Dependencies`, `Sources` (only the `<value>` tokens). `Proof`, `Evidence basis`, `Interpretation`,
`Tags` are not used by this metric — unchanged scoping discipline from cycle 1.

### Step-by-step
1. **Parse** `claims.md` into `Claim` objects (unchanged from cycle 1).
2. **Availability gate (penalize, never skip):** absent/unreadable/zero-claim-blocks → `0.0`.
3. **Per-claim FOL translation `[ext-FOL]`:** one primary LLM call per claim (variant 0), against the
   grammar-constrained prompt below. `untranslatable=true` is a hard per-claim `0.0`, not a skip.
4. **Deterministic validation** of each translation (no LLM calls except the gated re-run):
   a. **Syntax + quantifier-groundability check** — parse against the formal grammar; reject
      unparseable text or a bound variable with an empty grounding domain.
   b. **Solver-backed negation-consistency check** — the fixed, non-decorative version (§4.2 code).
   c. **Boundary-safe constant-groundedness** against `Sources`.
   d. **Budget-gated stability re-run** — only for claims whose score after (a)–(c) lands in
      `[0.05, 0.8)`: call `translate(claim, variant=1)`, compare relation-symbol Jaccard and the
      negation-consistency verdict; if either diverges, cap the claim's score at `0.15`.
5. **Graph-level checks** across the whole claim set: dependency DAG validity (cycles/dangling refs),
   cross-claim status consistency, and — new — the `[sem]` missing-edge/fragmentation check.
6. **Missing-edge `[sem]` pass:** using the constants/relation-symbols already extracted in step 3–4,
   flag undeclared-but-entangled claim pairs and compute a fragmentation multiplier.
7. **Aggregate**: mean per-claim score × dependency multiplier × status multiplier × fragmentation
   multiplier × sparse-graph penalty if fewer than 3 claims cleared the "clean" bar.

### External call spec

```
[ext-FOL] LLM translation call — one call per claim (variant 0), plus a gated variant-1 re-run
for borderline claims only. Temperature 0 for variant 0; temperature ~0.7 + light paraphrase
instruction for variant 1, so a genuine re-formalization is exercised, not a cached duplicate.

SYSTEM:
You are a formal-logic translator. You NEVER assert a truth value beyond what the claim states.
Output STRICT JSON only, matching this schema:
{
  "untranslatable": bool,
  "reason": str | null,
  "predicate_form": str | null,
  "negation_form": str | null,
  "variables": {"<var>": "<type>"},
  "constants": ["<literal>", ...]
}

Follow this EXACT grammar for predicate_form / negation_form (ASCII, no other operators):

  formula     := quantifier* implication
  quantifier  := ("forall" | "exists") IDENT "."
  implication := disjunction ("->" disjunction)?
  disjunction := conjunction ("|" conjunction)*
  conjunction := negation ("&" negation)*
  negation    := "~" negation | atom | "(" formula ")"
  atom        := IDENT "(" term ("," term)* ")"
  term        := IDENT | NUMBER

Rules:
- Every numeral/named-entity constant in predicate_form MUST appear verbatim in Statement — no
  paraphrasing, no rounding.
- negation_form MUST reuse the same relation/entity symbols as predicate_form (it is a formal
  negation of the same predicate, not a different claim).
- If you use forall/exists, the bound variable's type MUST correspond to a domain you can actually
  enumerate from the constants you are extracting (e.g. "forall x. Outranks(x, p217_MS)" is only
  usable if the other ranked entities are themselves in `constants`). If the claim requires
  quantifying over an open-ended domain you cannot enumerate, set untranslatable=true instead of
  inventing an unbounded quantifier.
- If you cannot do this without inventing a relation not actually stated, set untranslatable=true.

USER:
Claim ID: {claim.id}
Statement: {claim.statement}
Falsification criteria: {claim.falsification}
[variant=1 only, appended]: Re-derive this translation independently — do not just repeat your
prior answer verbatim; if a different but equally faithful formalization exists, prefer it.
```

The grammar constraint above is new in cycle 2 and is the concrete mechanism for "sharpening the
claims→FOL workflow": cycle 1 told the model to use "ASCII: &, |, ~, ->, forall, exists" with no
formal grammar, which is exactly why the cycle-1 solver step could get away with being decorative —
nothing downstream actually had to parse the output. Cycle 2's deterministic code parses this
grammar for real (§4.2), so the prompt now has to produce something a parser can consume.

### 4.1 Real Python: parsing, grounding, and the fixed solver

```python
import re
from dataclasses import dataclass, field
from typing import Optional, Callable
import networkx as nx
from z3 import Solver, Bool, BoolRef, Not, And, Or, Implies, sat, unsat

# --- unchanged from cycle 1: Claim / parse_claims / FOLTranslation dataclasses ---

@dataclass
class Claim:
    id: str
    statement: str
    status: str
    falsification: str
    dependencies: list[str]
    sources: list[str] = field(default_factory=list)


CLAIM_HEADER_RE = re.compile(r"^## (C\d+): (.+)$", re.MULTILINE)
FIELD_RE = lambda name: re.compile(
    rf"\*\*{name}\*\*:\s*(.+?)(?=\n- \*\*|\n## |\Z)", re.DOTALL
)


def parse_claims(claims_md_text: str) -> list[Claim]:
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
    variables: dict[str, str] = field(default_factory=dict)
    constants: list[str] = field(default_factory=list)
    untranslatable: bool = False


# --- injected I/O boundary (fixes critique weakness 4) ---

def call_fol_translator(claim: Claim, variant: int = 0) -> FOLTranslation:
    """[ext-FOL] Executes the LLM prompt above (variant=0 primary, variant=1 gated re-run)
    and parses the JSON response. Performs NO scoring. This is the default implementation;
    score_M09 takes `translate` as a parameter so tests / alternate clients can inject a
    stub without touching scoring code."""
    raise NotImplementedError("wire to LLM client; see prompt spec above")


# --- NEW: a real parser for the grammar in the prompt spec ---

TOKEN_RE = re.compile(r"forall|exists|->|[()&|~,.]|[A-Za-z_]\w*|-?\d+(?:\.\d+)?")


class ParseError(Exception):
    pass


def tokenize(s: str) -> list[str]:
    pos = 0
    toks = []
    while pos < len(s):
        if s[pos].isspace():
            pos += 1
            continue
        m = TOKEN_RE.match(s, pos)
        if not m:
            raise ParseError(f"unrecognized token at {pos!r} in {s!r}")
        toks.append(m.group(0))
        pos = m.end()
    return toks


class Parser:
    """Recursive-descent parser for the formula grammar in the prompt spec.
    AST nodes: ('forall', var, body) | ('exists', var, body) | ('implies', l, r) |
    ('or', [terms]) | ('and', [terms]) | ('not', x) | ('atom', name, [args])."""

    def __init__(self, tokens: list[str]):
        self.toks = tokens
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, expect: Optional[str] = None):
        t = self.peek()
        if t is None or (expect is not None and t != expect):
            raise ParseError(f"expected {expect!r}, got {t!r}")
        self.i += 1
        return t

    def parse_formula(self):
        if self.peek() in ("forall", "exists"):
            kind = self.eat()
            var = self.eat()
            self.eat(".")
            body = self.parse_formula()
            return (kind, var, body)
        return self.parse_implication()

    def parse_implication(self):
        left = self.parse_disjunction()
        if self.peek() == "->":
            self.eat("->")
            right = self.parse_disjunction()
            return ("implies", left, right)
        return left

    def parse_disjunction(self):
        terms = [self.parse_conjunction()]
        while self.peek() == "|":
            self.eat("|")
            terms.append(self.parse_conjunction())
        return terms[0] if len(terms) == 1 else ("or", terms)

    def parse_conjunction(self):
        terms = [self.parse_negation()]
        while self.peek() == "&":
            self.eat("&")
            terms.append(self.parse_negation())
        return terms[0] if len(terms) == 1 else ("and", terms)

    def parse_negation(self):
        if self.peek() == "~":
            self.eat("~")
            return ("not", self.parse_negation())
        if self.peek() == "(":
            self.eat("(")
            f = self.parse_formula()
            self.eat(")")
            return f
        return self.parse_atom()

    def parse_atom(self):
        name = self.eat()
        self.eat("(")
        args = [self.eat()]
        while self.peek() == ",":
            self.eat(",")
            args.append(self.eat())
        self.eat(")")
        return ("atom", name, args)


def parse_fol(sentence: str):
    p = Parser(tokenize(sentence))
    f = p.parse_formula()
    if p.i != len(p.toks):
        raise ParseError(f"trailing tokens: {p.toks[p.i:]}")
    return f


def relation_symbols(ast) -> set[str]:
    """All predicate names appearing anywhere in a parsed formula."""
    if ast[0] == "atom":
        return {ast[1]}
    if ast[0] in ("forall", "exists"):
        return relation_symbols(ast[2])
    if ast[0] == "not":
        return relation_symbols(ast[1])
    if ast[0] == "implies":
        return relation_symbols(ast[1]) | relation_symbols(ast[2])
    if ast[0] in ("and", "or"):
        out = set()
        for t in ast[1]:
            out |= relation_symbols(t)
        return out
    return set()


def ground(ast, domain: list[str]):
    """Finite-domain quantifier grounding: forall x.P(x) -> AND over domain,
    exists x.P(x) -> OR over domain. Raises ParseError if domain is empty
    (an ungroundable quantifier is a structural failure, not a skip)."""
    if ast[0] in ("forall", "exists"):
        _, var, body = ast
        if not domain:
            raise ParseError(f"no groundable domain for bound variable {var!r}")
        instances = [substitute(body, var, d) for d in domain]
        return ("and", instances) if ast[0] == "forall" else ("or", instances)
    if ast[0] == "atom":
        return ast
    if ast[0] == "not":
        return ("not", ground(ast[1], domain))
    if ast[0] == "implies":
        return ("implies", ground(ast[1], domain), ground(ast[2], domain))
    if ast[0] in ("and", "or"):
        return (ast[0], [ground(t, domain) for t in ast[1]])
    return ast


def substitute(ast, var: str, val: str):
    if ast[0] == "atom":
        return ("atom", ast[1], [val if a == var else a for a in ast[2]])
    if ast[0] in ("forall", "exists"):
        if ast[1] == var:  # shadowed; inner variable wins
            return ast
        return (ast[0], ast[1], substitute(ast[2], var, val))
    if ast[0] == "not":
        return ("not", substitute(ast[1], var, val))
    if ast[0] == "implies":
        return ("implies", substitute(ast[1], var, val), substitute(ast[2], var, val))
    if ast[0] in ("and", "or"):
        return (ast[0], [substitute(t, var, val) for t in ast[1]])
    return ast


def to_z3(ast, atom_cache: dict[str, BoolRef]) -> BoolRef:
    """Converts a GROUND (quantifier-free) AST into a Z3 BoolRef. Atoms are keyed by their
    canonical grounded string, so an atom appearing identically in two different formulas
    (e.g. predicate_form and negation_form sharing a relation symbol + constants) maps to
    the SAME Z3 Bool — this is what makes the solver check genuinely semantic instead of
    the cycle-1 opaque-P/notP placeholder."""
    if ast[0] == "atom":
        key = f"{ast[1]}({','.join(ast[2])})"
        if key not in atom_cache:
            atom_cache[key] = Bool(key)
        return atom_cache[key]
    if ast[0] == "not":
        return Not(to_z3(ast[1], atom_cache))
    if ast[0] == "implies":
        return Implies(to_z3(ast[1], atom_cache), to_z3(ast[2], atom_cache))
    if ast[0] == "and":
        return And(*[to_z3(t, atom_cache) for t in ast[1]])
    if ast[0] == "or":
        return Or(*[to_z3(t, atom_cache) for t in ast[1]])
    raise ParseError(f"unexpected node in ground AST: {ast}")


def syntax_valid_and_groundable(sentence: Optional[str], domain: list[str]) -> Optional[tuple]:
    """Returns the GROUND ast on success, None on any parse/grounding failure
    (malformed syntax OR an ungroundable quantifier — both are the same hard-fail bucket)."""
    if not sentence:
        return None
    try:
        ast = parse_fol(sentence)
        return ground(ast, domain)
    except ParseError:
        return None


def negation_consistent(fol: FOLTranslation) -> bool:
    """Fixed version: parses BOTH forms against the real grammar, grounds quantifiers over
    the claim's own constants, and checks the solver against a shared atom cache so that
    identical relation+argument atoms are literally the same Z3 variable in both formulas.
    predicate_form/negation_form pass iff UNSAT(P & N) and UNSAT(~P & ~N) — i.e. they cannot
    both hold and one of them must — evaluated over their ACTUAL parsed structure."""
    if not fol.predicate_form or not fol.negation_form:
        return False

    # cheap lexical pre-filter (kept from cycle 1: still useful, still free)
    pred_symbols = set(re.findall(r"[A-Za-z_]\w*(?=\()", fol.predicate_form))
    neg_symbols = set(re.findall(r"[A-Za-z_]\w*(?=\()", fol.negation_form))
    if not pred_symbols or pred_symbols.isdisjoint(neg_symbols):
        return False

    domain = list(dict.fromkeys(fol.constants))  # de-duped, order-preserving
    ground_p = syntax_valid_and_groundable(fol.predicate_form, domain)
    ground_n = syntax_valid_and_groundable(fol.negation_form, domain)
    if ground_p is None or ground_n is None:
        return False

    atom_cache: dict[str, BoolRef] = {}
    P = to_z3(ground_p, atom_cache)
    N = to_z3(ground_n, atom_cache)

    s1 = Solver()
    s1.add(And(P, N))
    if s1.check() == sat:
        return False  # they can both hold -> not a real negation

    s2 = Solver()
    s2.add(And(Not(P), Not(N)))
    if s2.check() == sat:
        return False  # neither has to hold -> not exhaustive either

    return True


def is_groundable(sentence: Optional[str], domain: list[str]) -> bool:
    return syntax_valid_and_groundable(sentence, domain) is not None


def _boundary_match(c: str, s: str) -> bool:
    """Boundary-safe replacement for the cycle-1 substring check. Rejects a match that is
    flanked by a digit or '.' on either side, so '0.1' no longer matches inside '0.117',
    while still matching numerals embedded in prose like '(P-score = 0.859)'."""
    m = re.search(re.escape(c), s)
    if not m:
        return False
    start, end = m.span()
    before = s[start - 1] if start > 0 else ""
    after = s[end] if end < len(s) else ""
    if before.isdigit() or before == ".":
        return False
    if after.isdigit() or after == ".":
        return False
    return True


def constants_grounded(fol: FOLTranslation, claim: Claim) -> float:
    if not fol.constants:
        return 0.0
    grounded = sum(
        1 for c in fol.constants if any(_boundary_match(c, s) for s in claim.sources)
    )
    return grounded / len(fol.constants)
```

### 4.2 The `[sem]` missing-edge / fragmentation check (new in cycle 2)

**Calibration argument for using symbolic overlap instead of an embedding backend.** Cycle-1
critique of exp2 flagged that its `[sem]` step named "semantic similarity" but left the concrete
backend and threshold unspecified — a real gap, because an opaque embedding model is (a) another
nondeterministic external call this metric would otherwise avoid entirely, (b) gameable by
paraphrasing away from the embedding space without changing logical content, and (c) budget the
brief never accounted for. Cycle 2 instead reuses the parsed, grounded atoms this metric *already
computed* in step 3–4 for every claim — free, deterministic, and directly tied to the formal content
the metric is scoring. The specific signal — **shared numeric constants**, not shared entity names —
is chosen because entity names (compound IDs, cohort names) recur across independent claims in the
same paper simply because the paper is *about* that entity, which would make an entity-overlap
threshold noisy. A precisely matching numeric constant (a P-score, hazard ratio, AUC, gene count) at
≥3 significant digits essentially only recurs across claims when one claim's conclusion is reused as
another's premise — coincidental agreement at that precision is implausible. This mirrors the shape
doc's own worked example (C01's `0.859`, `0.783`, `0.117` P-scores; a later claim about the p217_MS
vs p181_IA comparison would necessarily reuse one of these exact figures if it depends on C01).

```python
NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?%?$")


def _sig_figs(c: str) -> int:
    digits = re.sub(r"[^\d]", "", c)
    return len(digits.lstrip("0")) or len(digits)


def missing_edge_candidates(
    claims: list[Claim], translations: dict[str, FOLTranslation]
) -> list[tuple[str, str]]:
    """Deterministic [sem] step. Flags claim pairs with NO declared Dependencies edge (in
    either direction) that nonetheless share a precise numeric constant in their FOL
    constants -- the signature of an undeclared entailment (claim B's predicate reuses
    claim A's concluded statistic). Reuses translations already computed in step 3-4;
    makes no new LLM/embedding calls."""
    declared_edges = set()
    for c in claims:
        for dep in c.dependencies:
            declared_edges.add(frozenset({c.id, dep}))

    numeric_constants = {
        cid: {c for c in (translations[cid].constants if cid in translations else []) if NUMERIC_RE.match(c)}
        for cid in [c.id for c in claims]
    }

    candidates = []
    ids = [c.id for c in claims]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            if frozenset({a, b}) in declared_edges:
                continue
            shared = numeric_constants[a] & numeric_constants[b]
            if not shared:
                continue
            strong = any(_sig_figs(c) >= 3 for c in shared)
            if strong or len(shared) >= 2:
                candidates.append((a, b))
    return candidates


def fragmentation_multiplier(claims: list[Claim], translations: dict[str, FOLTranslation]) -> float:
    """Multiplicative whole-artifact penalty, same style as dependency/status multipliers.
    Never zeroes the artifact outright (penalize-don't-skip): floors at 0.6."""
    candidates = missing_edge_candidates(claims, translations)
    if not candidates:
        return 1.0
    return max(0.6, 1 - 0.15 * len(candidates))
```

### 4.3 Aggregate scoring, with the injected translator and gated stability re-run

```python
def score_claim(
    claim: Claim, translate: Callable[[Claim, int], FOLTranslation]
) -> tuple[float, FOLTranslation]:
    fol = translate(claim, 0)
    if fol.untranslatable or fol.predicate_form is None:
        return 0.0, fol

    domain = list(dict.fromkeys(fol.constants))
    if not is_groundable(fol.predicate_form, domain) or not is_groundable(fol.negation_form, domain):
        return 0.05, fol  # malformed OR an ungroundable quantifier -- same hard-fail bucket

    if not negation_consistent(fol):
        base = 0.2
    else:
        g = constants_grounded(fol, claim)
        base = 1.0 if g >= 1.0 else 0.2 + 0.3 * g

    if 0.05 <= base < 0.8:
        # budget-gated stability re-run: only the borderline band pays the second LLM call
        fol2 = translate(claim, 1)
        sym1 = re.findall(r"[A-Za-z_]\w*(?=\()", fol.predicate_form or "")
        sym2 = re.findall(r"[A-Za-z_]\w*(?=\()", fol2.predicate_form or "") if fol2.predicate_form else []
        s1, s2 = set(sym1), set(sym2)
        jaccard = (len(s1 & s2) / len(s1 | s2)) if (s1 | s2) else 0.0
        verdict1 = negation_consistent(fol)
        verdict2 = negation_consistent(fol2) if fol2.predicate_form else False
        if jaccard < 0.5 or verdict1 != verdict2:
            base = min(base, 0.15)  # non-reproducible formalization: cap, don't skip

    return base, fol


def dependency_graph_multiplier(claims: list[Claim]) -> float:
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
    from z3 import Bool as Zbool
    s = Solver()
    lits = {c.id: Zbool(c.id) for c in claims}
    for c in claims:
        base_status = c.status.split(" ")[0].strip("()").lower()
        if base_status == "supported":
            s.add(lits[c.id])
        elif base_status == "refuted":
            s.add(Not(lits[c.id]))
        for dep in c.dependencies:
            if dep in lits:
                s.add(Or(Not(lits[c.id]), lits[dep]))
    return 1.0 if s.check() == sat else 0.4


def score_M09(
    claims_md_text: Optional[str],
    translate: Callable[[Claim, int], FOLTranslation] = call_fol_translator,
) -> dict:
    """Top-level entrypoint. HARD CONSTRAINT: missing/thin inputs score down, never
    skip/N-A; availability is itself part of the score. `translate` is injected so tests
    can stub the LLM boundary without touching any scoring logic (fixes critique
    weakness 4)."""
    if not claims_md_text or not claims_md_text.strip():
        return {"score": 0.0, "availability": "missing", "per_claim": {}}

    claims = parse_claims(claims_md_text)
    if not claims:
        return {"score": 0.0, "availability": "empty", "per_claim": {}}

    per_claim: dict[str, float] = {}
    translations: dict[str, FOLTranslation] = {}
    for c in claims:
        score, fol = score_claim(c, translate)
        per_claim[c.id] = score
        translations[c.id] = fol

    dep_mult = dependency_graph_multiplier(claims)
    status_mult = status_consistency_multiplier(claims)
    frag_mult = fragmentation_multiplier(claims, translations)

    mean_claim_score = sum(per_claim.values()) / len(per_claim)
    final = mean_claim_score * dep_mult * status_mult * frag_mult

    clean_count = sum(1 for v in per_claim.values() if v >= 0.8)
    if clean_count < 3:
        final *= 0.5 + 0.5 * (clean_count / 3)

    return {
        "score": round(final, 4),
        "availability": "present",
        "total_claims": len(claims),
        "clean_claim_count": clean_count,
        "dependency_graph_multiplier": dep_mult,
        "status_consistency_multiplier": status_mult,
        "fragmentation_multiplier": frag_mult,
        "missing_edge_candidates": missing_edge_candidates(claims, translations),
        "per_claim": per_claim,
    }
```

### Handling thin/degraded inputs (penalize-don't-skip, worked through)
- **Absent `claims.md`**: `score_M09` returns `0.0`, `availability: "missing"`.
- **Abstract-only compilation**: same mechanism as cycle 1 (vaguer/less-quantified Statements
  come back `untranslatable` or low-constant more often) — additionally, sparse abstract-only
  claim sets rarely produce enough shared numeric constants to trigger false missing-edge
  candidates, so the new fragmentation check does not spuriously punish genuinely thin-but-honest
  compilations.
- **Claims with bare-path Sources (no verbatim quote)**: not re-failed here (verifier's job), but
  the boundary-safe `constants_grounded` now measures this more precisely than the old substring
  check, so these claims still show up as reduced credit without double-counting.
- **Zero claims clear the "clean" bar**: `final` is multiplied by `0.5`, unchanged from cycle 1.
- **Ungroundable quantifier (new failure mode)**: a claim whose `predicate_form` uses `forall`/
  `exists` over a domain the translator couldn't actually enumerate scores `0.05` — the same bucket
  as syntactic malformation, because both mean "the solver cannot consume this," which is the
  metric's whole point. This is never a skip; it is scored as a near-worst per-claim outcome.
- **Non-reproducible borderline translation**: capped at `0.15`, distinctly worse than a
  reproducible-but-partially-grounded claim (`0.2 + 0.3g`), because instability under a re-ask is
  itself negative evidence about whether the claim was really formalizable in the first place.
- **`Dependencies: none` everywhere with visible entangled statistics**: no longer a free pass —
  `fragmentation_multiplier` penalizes the whole artifact proportional to the number of undeclared-
  but-detectable entanglements, floored at `0.6` so it never fully zeroes an otherwise-clean
  artifact on this signal alone.

## 5. Why this is hard to Goodhart

- The score is never computed from the LLM asserting "this is clean" — every accept/reject
  decision is deterministic code running on the LLM's structured output.
- **The negation-consistency solver now genuinely consumes the formulas.** Cycle 1's version could
  be gamed by any well-formed-looking `negation_form` because the Z3 call was checking a tautology
  unrelated to the actual sentences. Cycle 2's parser + finite-domain grounding + shared-atom-cache
  encoding means a `negation_form` that reuses the right symbols but the wrong constants, or that
  negates a different sub-relation, now fails the solver on its real content.
- Constant-groundedness (now boundary-safe) ties the formal claim back to `Sources`, so an LLM
  cannot claim credit for a well-formed-looking predicate that quietly drops, invents, or partially-
  matches numbers.
- **The `[sem]` fragmentation check closes the last open gaming route from cycle 1**: a compiler can
  no longer dodge the dependency-graph and status-consistency multipliers by simply never declaring
  edges, because undeclared-but-numerically-entangled claims are now caught deterministically and
  penalized as a whole-artifact multiplier — and because the signal is symbolic (reused compute, not
  a new nondeterministic call), the compiler cannot game it by paraphrasing prose the way it could
  game an embedding-based check.
- **The stability re-run defeats rubber-stamped forcing of narrativized claims into fake formal
  structure**, and does so without inviting a cost-based Goodhart route (e.g. "always request the
  cheapest/laziest translation first since a full re-run never happens") — the gate is on the
  *outcome band*, not on anything the compiler controls directly; a compiler cannot reliably steer a
  claim out of the borderline band without actually making the claim more clearly formalizable or
  more clearly not, both of which are the intended incentive.
- The dependency/status/fragmentation checks are all graph-wide multipliers, so gaming any
  individual claim's score cannot rescue an artifact whose claims graph is circular, contradictory,
  or dishonestly wired.
- The sparse-graph penalty still defeats padding-with-easy-claims via the same mechanism as cycle 1.

## 6. Composition with the rest of the suite

Unchanged from cycle 1: M09 does not re-check field completeness (Seal Level 1's job) or grounding
accuracy (the ARA verifier's job); it only fires on the logical form and honest graph-wiring of
content those other checks have already gated for presence. It composes multiplicatively with
claim-quality/impact metrics rather than substituting for them. Its output — per-claim clean/dirty
flags, a validated dependency DAG, and now the missing-edge candidate list — remains a reusable
downstream artifact (e.g. for a cross-ARA contradiction-detection pass), and the missing-edge list
in particular is a direct, ready-made input for any future "undeclared cross-claim entailment"
audit, since it is produced as a byproduct of scoring rather than a separate pass.
