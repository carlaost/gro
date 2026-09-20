# M32 — Method validity & verification status (expander 4)

## 1. Expanded reasoning

### What this indicator is actually checking
M32 is not "did the authors do good statistics" and not "is the write-up reproducible" — those
belong to D6's broader methodological-rigor sweep and to other tournament metrics on reproducibility/
grounding. M32 asks a narrower, warrant-specific question:

> **Is the method that was actually used validated for the claim it is being asked to support, and —
> if it is being pushed past that validated envelope — does the artifact say so?**

This is a claim about the *fit between method and inference*, not about execution quality. A perfectly
executed method that is the wrong tool for the job (e.g., a diagnostic-accuracy statistic applied to a
screening-population claim, a clustering algorithm validated on bulk RNA-seq applied unmodified to
spatial transcriptomics without acknowledging the domain shift, an architecture component borrowed from
a different modality with no ablation) should score *low* on M32 even if every number in the paper is
internally consistent and perfectly reported. Conversely, a genuinely novel or extended method that
*explicitly* names its own boundary and defends the extension is doing exactly what good science does —
it should score *high*, not be penalized for novelty per se. The metric rewards **honesty about scope**,
not conservatism of method choice.

### What it must reward
- A method with an established validation track record for this problem class, used within that
  envelope (§`study_design.md`/`method.md` describes it and `constraints.md`'s boundary conditions are
  consistent with that envelope).
- A novel/extended/adapted method where the artifact's `constraints.md` (boundary conditions +
  assumptions + known limitations) explicitly names the specific way the method is being pushed beyond
  prior validation, and gives a reason to believe it still holds (a pilot check, a theoretical argument,
  a sensitivity analysis, a citation to prior partial validation).
- Specificity: limitations that name the exact mechanism of possible failure ("BayesSpace was validated
  on 10x Visium at 55µm spot resolution; this study applies it to Visium HD at 2µm — spatial
  autocorrelation assumptions may not transfer") over generic hedging ("further validation is needed").

### What it must NOT reward
- Boilerplate limitations sections that pad `constraints.md` without engaging the actual method
  ("results may not generalize to other populations" attached to *every* paper regardless of method).
- A method described by a prestigious-sounding name whose actual implementation (as described in the
  method file's prose) departs from the standard procedure — the name must match the described steps.
- Simply having *many* assumptions/limitations bullets — volume is not warrant; relevance and
  specificity to the actual method's known failure modes is.
- Silence. An artifact with a thin or absent method layer must not default to a neutral/unscored
  state — see hard constraint below.

### Failure modes / gaming routes and how the design resists them
| Gaming route | Resistance |
|---|---|
| Pad `constraints.md` with generic, method-agnostic hedges to look diligent | [sem] step explicitly classifies each limitation/assumption as *specific-to-method* vs *generic-boilerplate*; only specific ones count toward warrant closure |
| Rename an ad hoc procedure with standard-sounding vocabulary | [sem] classification is grounded in the method file's *described steps*, not its label — prompt requires quoting the specific procedural sentence(s) that justify the classification |
| Thin out or omit the method file so there's less to be judged unsound | HARD CONSTRAINT: absence of method files below `constraints.md` is itself scored as a specific unsound-until-shown-otherwise state (see §2 Step 1), not skipped/N-A — thinning the artifact can only lower the score |
| Mislabel method-file genre (e.g. ship an `architecture.md` for a paper that trained no model) to imply more rigor-scaffolding than the work has | [sem] step explicitly checks file-genre-vs-content match (flagged in shape doc as a Seal-L1 red flag) and penalizes mismatch |
| Get an LLM verifier to rubber-stamp "VALIDATED" by only showing it the method name | Compute workflow feeds the *full* method-file text (not a summary) and requires the sub-score to cite the exact sentence(s) it is judging, so a rubber-stamp with no textual grounding is itself detectable and discounted |
| Claim an extension is "justified" using a citation that doesn't actually support the specific extension | [sem] step requires the justification span to state *what* about the extension it defends (not just "prior work supports this approach" generically) — ungrounded citations are classified as generic, not specific |

### Why the assessment-critique notes change the design
The ledger note says this ranked top-10 specifically as a **tighter, specific facet of D6** —
meaning the design must resist collapsing back into a general "is the methodology rigorous" catch-all
(that's D6's job and would be redundant/verifier-overlapping). Two design consequences:
1. **Scope discipline**: M32's compute workflow only ever asks the validity/warrant question — it does
   not re-score statistical execution, sample size, reproducibility of code, or internal numeric
   consistency (those live in D6 broadly and in the data-quality-caveats cross-check noted in the shape
   doc). Anything the workflow surfaces that isn't a fit-of-method-to-claim issue is out of scope and
   must not move the M32 score.
2. **Net-new edge preserved via the warrant-explicitness axis**: D6 verifiers likely already ask "is
   there a validated method." What's net-new here is scoring *whether the artifact is honest about
   pushing past validation* — a binary "validated: yes/no" collapses that edge; the two-axis design in
   §2 (method-class × warrant-explicitness) keeps it.

### Hard constraint — penalize, don't skip
Availability of the method layer, and of the specific sub-fields (`boundary conditions`, `assumptions`,
`known limitations`, method files beyond `constraints.md`), is *itself* part of the score. An
abstract-only source that has no method file beyond a bare `constraints.md` (the shape doc's "stark,
easily-detected floor case") must resolve to a low, deterministic numeric score — never to a null/NA
that a downstream composite could silently drop or treat as "no information, no penalty."

### Why it's hard to Goodhart
The score is anchored to *quoted, specific textual grounding* at every semantic sub-step (method
classification must cite the describing sentence; warrant-explicitness must cite the specific limitation
sentence and say what mechanism it addresses). This makes low-effort gaming (padding, renaming,
generic hedging) either ineffective (generic text is classified as generic and scores low) or
self-defeating (thinning the artifact to avoid scrutiny hits the hard-constraint floor harder than
leaving a mediocre method description in place — there's no way to game it toward a *higher* score by
removing information). Because the grounding requirement forces the LLM's judgment to be checkable
against the source text, a human or a second verifier can audit any M32 score in seconds by reading the
cited spans — this also gives cheap adversarial verification (re-run with a different [sem] backend and
diff the classifications and their cited spans; large disagreement is itself a signal).

### Composition with the rest of the suite
M32 should compose **multiplicatively/gating**, not additively, with claim-strength metrics that
depend on the method's output: if the core method is EXTENDED-UNJUSTIFIED, every downstream claim that
rests on that method's output should have its own credibility metric capped/discounted, not just have
M32 itself report low in isolation — a single unsound method can invalidate an otherwise pristine
write-up. Against D6 broadly, M32 should be treated as a *specific override signal*: D6 can still score
overall rigor-of-execution highly (stats done correctly, code reproducible) while M32 independently
flags that the wrong tool was rigorously misapplied — the two must remain visible as separate numbers in
the composite, not merged, so a paper can't launder a scope violation behind good execution hygiene
elsewhere.

---

## 2. Generation / compute workflow

### Inputs (artifact fields, from `logic/solution/`)
```text
constraints.md (always present, possibly thin):
  - boundary_conditions: list[str]
  - assumptions: list[{id: str, text: str}]
  - known_limitations: list[{name: str, text: str, section_ref: str|None}]
  - data_quality_caveats: list[str]        # optional subsection, may be absent

method_files (0..N, present iff genuinely produced by the compiler):
  - {filename: str -> raw_markdown_text: str}
    e.g. "study_design.md", "method.md", "architecture.md", "algorithm.md",
         "formalization.md", "proofs.md", "design.md"

heuristics.md (optional):
  - list[{id: str, rationale: str, sensitivity: enum|str, bounds: str, code_ref: list[str]|str, source: str}]
```

### Step 0 — Deterministic parse (no LLM)
Parse `constraints.md` into the three canonical sections + optional caveats subsection; parse each
method file's raw text (kept whole — no summarization before the [sem] step, to preserve groundability).
Record structural facts used by the availability sub-score:
- `has_constraints`: bool (should always be True; if False, this is itself a critical defect)
- `constraints_bullet_count`: int (sum across all sections)
- `method_file_names`: set[str] (excluding `constraints.md`)
- `method_file_char_count`: int (total non-whitespace chars across method files)
- `has_heuristics`: bool

### Step 1 — Availability sub-score (deterministic, penalize-don't-skip)
```python
def availability_subscore(has_constraints: bool, constraints_bullet_count: int,
                           method_file_names: set, method_file_char_count: int) -> float:
    """Returns 0.0-1.0. Never returns None — absence is itself a low score, not N/A."""
    if not has_constraints:
        return 0.0  # constraints.md is mandatory-core; its absence is a hard floor
    score = 0.0
    # thin constraints.md (the shape doc's flagged red flag: "no limitations stated")
    if constraints_bullet_count == 0:
        score += 0.0
    elif constraints_bullet_count < 2:
        score += 0.1
    else:
        score += 0.3
    # method file(s) beyond the mandatory constraints.md
    if not method_file_names:
        score += 0.0   # abstract-only floor case — still scored, not skipped
    elif method_file_char_count < 400:
        score += 0.1   # present but too thin to ground a validity judgment
    else:
        score += 0.4
    return min(score, 0.7)  # availability alone cannot reach a high score;
                             # it only gates how much the semantic axis (Step 2) can contribute
```

### Step 2 — [sem] call: method-validity + warrant-explicitness classification
This step is **mandatory even when method files are absent** — in that case the call still runs against
whatever text exists (`constraints.md` alone, or the bare abstract-derived boundary conditions), and the
model is instructed to select `NOT-DETERMINABLE` rather than guess, which itself maps to a low (not
neutral) numeric value in Step 3.

**Exact prompt (fill `{constraints_text}` and `{method_text}`; if `method_text` is empty, pass the
literal string `"[no method file beyond constraints.md was produced]"`):**

```
You are assessing ONE research artifact's method layer for whether the method used is validated for
the claim it supports, and whether the artifact is honest about any extension beyond that validation.

--- CONSTRAINTS.MD ---
{constraints_text}

--- METHOD FILE(S) ---
{method_text}

Answer as strict JSON with exactly these fields:

{
  "core_method_summary": "<one sentence naming the core method(s) actually described>",
  "method_class": "VALIDATED | EXTENDED_JUSTIFIED | EXTENDED_UNJUSTIFIED | UNVALIDATED_ADHOC | NOT_DETERMINABLE",
  "method_class_grounding_quote": "<verbatim sentence(s) from METHOD FILE(S) that the classification is based on, or empty string if NOT_DETERMINABLE>",
  "method_class_rationale": "<why this class — must name what makes the method validated / how it is
      being extended / why it is ad hoc, referencing the actual described procedure, not its label>",
  "warrant_explicitness": "SPECIFIC | GENERIC | ABSENT",
  "warrant_grounding_quote": "<verbatim limitation/assumption/boundary-condition sentence that names the
      SPECIFIC mechanism by which this method could fail or not generalize, or empty string if ABSENT>",
  "genre_mismatch": true/false,
  "genre_mismatch_explanation": "<if true: which method file's existence/name implies scaffolding
      (e.g. a trained model, a formal proof) that the described content does not actually contain>"
}

Rules:
- method_class_grounding_quote and warrant_grounding_quote MUST be verbatim substrings of the text
  above, or empty strings. Do not paraphrase into the quote field.
- If METHOD FILE(S) is the placeholder "[no method file...]", method_class MUST be NOT_DETERMINABLE
  unless CONSTRAINTS.MD alone unambiguously identifies a named, checkable method — do not infer a
  method that isn't stated.
- warrant_explicitness = SPECIFIC requires the quoted sentence to name a mechanism tied to THIS
  method (not a generic "may not generalize to other populations" applicable to any paper).
- Output JSON only, no prose outside the object.
```

**Turning the [sem] output into a deterministic sub-score:**
```python
METHOD_CLASS_SCORE = {
    "VALIDATED": 1.0,
    "EXTENDED_JUSTIFIED": 0.85,
    "EXTENDED_UNJUSTIFIED": 0.25,
    "UNVALIDATED_ADHOC": 0.15,
    "NOT_DETERMINABLE": 0.10,   # penalized, not neutral — HARD CONSTRAINT
}

WARRANT_SCORE = {
    "SPECIFIC": 1.0,
    "GENERIC": 0.3,
    "ABSENT": 0.0,
}

def verify_grounding(quote: str, source_text: str) -> bool:
    """Deterministic check: a non-empty grounding quote must actually appear in the source text
    (allowing minor whitespace normalization). If it doesn't, treat the [sem] call as having
    hallucinated grounding and force the corresponding axis to its lowest value."""
    if quote.strip() == "":
        return True  # empty quote is valid for NOT_DETERMINABLE / ABSENT
    normalize = lambda s: " ".join(s.split())
    return normalize(quote) in normalize(source_text)

def semantic_subscore(sem: dict, constraints_text: str, method_text: str) -> float:
    method_class = sem["method_class"]
    warrant = sem["warrant_explicitness"]

    # grounding-fraud check — ungroundable quotes zero out that axis regardless of claimed class
    if not verify_grounding(sem["method_class_grounding_quote"], method_text or constraints_text):
        method_class = "NOT_DETERMINABLE"
    if not verify_grounding(sem["warrant_grounding_quote"], constraints_text):
        warrant = "ABSENT"

    m = METHOD_CLASS_SCORE.get(method_class, 0.10)
    w = WARRANT_SCORE.get(warrant, 0.0)

    # Warrant only matters (and only rescues a score) when an extension is actually being made.
    # A VALIDATED method with no stated warrant is not penalized for warrant (nothing to warrant);
    # an EXTENDED/UNVALIDATED method with no warrant IS penalized hard — that's the core signal.
    if method_class == "VALIDATED":
        combined = 0.85 * m + 0.15 * w
    else:
        combined = 0.55 * m + 0.45 * w

    # genre mismatch is an independent penalty (structural honesty of the artifact itself)
    if sem.get("genre_mismatch"):
        combined *= 0.7

    return max(0.0, min(combined, 1.0))
```

### Step 3 — Final score
```python
def score_m32(artifact: dict, sem: dict) -> dict:
    """
    artifact: {
      "has_constraints": bool,
      "constraints_bullet_count": int,
      "method_file_names": set,
      "method_file_char_count": int,
      "constraints_text": str,
      "method_text": str,   # concatenation of all method files' raw text, "" if none
    }
    sem: parsed JSON dict returned by the [sem] call in Step 2, already schema-validated
         (missing/malformed keys should be coerced to the most-penalized enum value, never
         cause the pipeline to abstain).
    """
    avail = availability_subscore(
        artifact["has_constraints"],
        artifact["constraints_bullet_count"],
        artifact["method_file_names"],
        artifact["method_file_char_count"],
    )
    sem_score = semantic_subscore(sem, artifact["constraints_text"], artifact["method_text"])

    # Availability gates the ceiling reachable by the semantic axis: an artifact that is too
    # thin to ground a real judgment cannot be rescued to a high score by a generous [sem] call
    # (this is the concrete enforcement of "availability is itself part of the score").
    ceiling = 0.3 + 0.7 * (avail / 0.7)   # avail in [0,0.7] -> ceiling in [0.3,1.0]
    final = min(sem_score, ceiling)

    # Absolute floor cases per HARD CONSTRAINT — never emit a null/NA
    if not artifact["has_constraints"]:
        final = 0.0

    return {
        "m32_score": round(final, 3),
        "availability_subscore": round(avail, 3),
        "semantic_subscore": round(sem_score, 3),
        "method_class": sem.get("method_class", "NOT_DETERMINABLE"),
        "warrant_explicitness": sem.get("warrant_explicitness", "ABSENT"),
        "genre_mismatch": bool(sem.get("genre_mismatch", False)),
        "grounding_quotes": {
            "method_class": sem.get("method_class_grounding_quote", ""),
            "warrant": sem.get("warrant_grounding_quote", ""),
        },
    }
```

### External/[sem] calls summary
- Exactly one LLM call per artifact (Step 2), against the full un-summarized text of `constraints.md`
  plus all method files concatenated (bounded by context window; if method text is very large, chunk
  per-file and take the lowest-scoring file's classification rather than an average — a single
  unvalidated core method is disqualifying regardless of how much validated scaffolding surrounds it).
- No external database/citation-verification call is required for the base metric. An optional
  strengthening (out of scope for the base score but noted for future work) would route
  `method_class_rationale` through a semantic-scholar/undermind lookup to check whether the named
  method genuinely has the validation track record the [sem] call asserts — this is deliberately not
  included in v1 to keep M32 scoped to what's inspectable from the artifact alone, per the "tighter,
  specific facet" mandate above.
