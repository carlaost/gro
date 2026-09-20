# M32 — Method validity & verification status — Expansion (expander 2)

## 1. What this metric is actually for

The one-line indicator: *"Is the method sound — a widely-accepted validated method vs one
over-generalized beyond its warrant (and is that justified/explained)?"*

This is **not** "did the authors execute their method correctly" (that's execution-correctness /
statistical-rigor territory, already covered by the generic ARA verifier's D6 methodological-rigor
check and by other metrics in this suite that look at evidence/stats). M32's job is narrower and
sits one level up the stack: **is the chosen method itself the right tool for the claim being
made, in the domain it's being applied to — and if the authors reached beyond that tool's
established warrant, did they say so and defend it?**

Concretely, M32 answers three linked questions from `logic/solution/`:
1. **What method was actually used?** (named, identifiable, from `method.md` / `study_design.md`
   / `architecture.md` / `algorithm.md` / `heuristics.md`, whichever the genre produced.)
2. **Is that method validated/established for the domain and claim type it's being applied to?**
   (external check — this is not something the artifact alone can verify; it requires literature
   grounding, hence the `[sem]` tag.)
3. **If the application generalizes beyond the method's established warrant** (new domain, new
   scale, new population, a heuristic borrowed from an adjacent field, an assay used off-label),
   **does `constraints.md` (Boundary conditions / Assumptions / Known limitations) explicitly
   name and justify that stretch?**

### What it must reward
- A method that is standard-of-field for the claim type, used within its known domain of
  validity (e.g., Cox proportional-hazards for time-to-event with PH assumption checked; a
  MS/Simoa immunoassay platform already FDA-cleared for the analyte in question).
- A method that **is** a generalization/novel application, but where `constraints.md` names the
  stretch precisely (which assumption is being extended, to what degree) and either cites
  supporting precedent or explicitly flags it as exploratory/unvalidated. Honesty about reach is
  itself a signal of good science and should not score the same as silence.
- Internal consistency between the stated method and the stated assumptions/limitations — e.g., if
  `heuristics.md` documents a heuristic's `Sensitivity: high` with unresolved bounds, that is a
  method-validity signal (an admittedly fragile method component), not a defect to hide.

### What it must NOT reward
- A method being *named* with field-standard vocabulary is not the same as it being *validated for
  this use*. "We used deep learning" or "we applied a validated biomarker assay" is a citation-flag
  phrase, not evidence — the metric must verify against actual literature, not trust the paper's
  own framing.
- Boilerplate limitations language that doesn't actually engage with the method's domain of
  validity (e.g., a generic "further studies are needed" sentence) must not be credited as
  "justified generalization." The bar is specific engagement with *why this method still applies
  here*, not a hedge.
- A method file that exists but is genre-mismatched (e.g., an `architecture.md` invented for a
  paper that trained no model — flagged elsewhere as a Seal-Level-1 defect) should not get partial
  credit for "having a method file"; it should be treated as an availability/validity failure in
  its own right, since a fabricated-genre method file cannot be checked against real literature.

### Failure modes / gaming routes
- **Name-dropping**: compiler or paper cites a prestigious-sounding method name without the paper
  actually satisfying its preconditions. Mitigated by requiring the `[sem]` check to confirm the
  method's established domain, not just its existence.
- **Selective limitation-listing**: `constraints.md` lists many minor caveats but omits the one
  that actually matters (the domain stretch). Mitigated by cross-checking the *specific* method
  named in step 1 against the *specific* language in Known limitations / Boundary conditions,
  rather than crediting "a limitations section exists."
- **Retroactive justification laundering**: a compiler could paraphrase a stretch as if it were
  intentional/justified when the source paper never actually defended it. Mitigated by requiring
  the extracted justification text to be traceable to a `§X.Y` source reference (constraints.md's
  own convention), and by treating unreferenced/vague justification as no justification.
- **Sem-search gaming**: querying only the method's own name (which will always return the
  foundational paper for that method as a general concept) instead of the method **in the domain
  claimed**, which would launder an out-of-domain application as "well-established" just because
  the base method is famous in a *different* domain. Mitigated by always querying method + domain
  jointly, never the method name alone (see workflow §3).
- **Skip-on-absence gaming**: if a method file is absent, an implementation might be tempted to
  score N/A. Explicitly forbidden — see penalize-don't-skip below.

### How the assessment-critique notes reshape this metric's scope (preserving its top-10 edge)
The ledger explains M32 ranked top-10 specifically because it is either net-new versus the generic
ARA verifier or scoped tighter than it. To preserve that edge this workflow explicitly **excludes**
everything that already belongs to D6/other metrics, and confines itself to the validity-of-choice
axis only:
- **Excluded** (belongs elsewhere): whether the method was executed without bugs, whether sample
  size/power was adequate, whether statistical tests were run correctly, whether results replicate,
  whether the code matches the paper (execution-correctness / evidence-layer concerns).
- **Included** (M32's exclusive territory): is the *chosen method itself*, as a method, warranted
  for this claim in this domain, and is any stretch beyond that warrant disclosed and defended.
This keeps M32 a genuinely different question than "was the study well-run" — it's "was the right
tool picked, and if not exactly right, was that admitted."

## 2. Hard constraint: penalize, don't skip

`constraints.md` is mandatory-core per the shape doc and is never absent — but it can be *thin*
(bare "no limitations stated," which the shape doc itself flags as a red flag, since virtually
every real paper has some caveat). Method files (`method.md`, `study_design.md`, etc.) are
optional and genre-dependent. This workflow treats absence/thinness as itself informative, never
as a reason to abstain:

- No method file at all, for a paper whose problem statement / evidence layer clearly implies a
  concrete method exists (e.g., an ML paper with reported metrics but no `architecture.md`): score
  the **method-identification component at floor (0)** — we cannot verify validity of a method we
  cannot name, and that opacity is itself a good-science defect, not a null result.
- `constraints.md` present but bare/boilerplate (no section actually engages with method domain or
  validity): **justification component at floor (0)**, not skipped.
- `[sem]` lookup returns zero relevant results (method too obscure/novel to have any literature
  footprint, or the external call fails): treat as **established-validity component at floor (0)**
  — unverifiable is scored as unverified, not excluded from the composite.
- Abstract-only source (no method layer beyond bare `constraints.md`, per the shape doc's "stark,
  easily-detected floor case"): the entire metric bottoms out near 0, computed the same way as any
  other input (all three components floor), not set aside as N/A.

The composite formula below is a pure weighted sum of components that are already defined to floor
at 0 under non-availability — no separate N/A branch exists anywhere in the code path.

## 3. Generation / compute workflow

### Inputs (artifact fields)
- `logic/solution/constraints.md` — Boundary conditions, Assumptions, Known limitations,
  Additional caveats (data-quality notes) sections.
- `logic/solution/{study_design.md, method.md, architecture.md, algorithm.md, heuristics.md}` —
  whichever subset exists for this paper's genre.
- (Cross-layer, read-only, for domain context) the paper's stated research question / cohort /
  data domain — taken from whatever problem-statement layer the ARA exposes (§1), used only to
  supply the "domain" term for the `[sem]` query; M32 does not score anything in that layer.

### Step 1 — Extract method identity, domain, and generalization language (LLM call, deterministic parse of output)

Prompt (fill `{constraints_md}`, `{method_files_concat}`, `{domain_context}` from the artifact):

```
You are extracting structured facts from a research artifact's method layer. Do not judge
quality — only extract.

CONSTRAINTS FILE:
{constraints_md}

METHOD FILE(S):
{method_files_concat}

DOMAIN CONTEXT (from problem statement, for reference only):
{domain_context}

Return strict JSON:
{
  "primary_method_name": string or null,   // the single most load-bearing named method/technique
  "method_domain_claimed": string or null, // the domain/population/data-type it's applied to HERE
  "is_generalization": boolean,            // true if the text itself signals a novel/adapted/
                                            // extended/off-label/exploratory use of the method
                                            // relative to its textbook domain
  "generalization_evidence_quote": string or null,  // verbatim quote if is_generalization=true
  "justification_present": boolean,        // true only if constraints.md specifically engages
                                            // with WHY the method still applies despite the stretch
                                            // (not a generic hedge)
  "justification_quote": string or null,
  "justification_source_ref": string or null  // e.g. "§4.5" if constraints.md cites one
}
If no method can be identified at all, set primary_method_name to null and all other fields to
their null/false default — do not guess.
```

Deterministic post-processing:
```python
def parse_extraction(llm_json: dict) -> dict:
    # Reject ungrounded justification claims: justification_present requires both a quote
    # AND a source ref that matches constraints.md's own "(§X.Y)" convention.
    if llm_json.get("justification_present") and not (
        llm_json.get("justification_quote") and llm_json.get("justification_source_ref")
    ):
        llm_json["justification_present"] = False
    return llm_json
```

### Step 2 — `[sem]` external validity check (semantic-scholar)

Only run if `primary_method_name` is non-null (if null, skip straight to scoring with the
method-ID component at floor — this is the one legitimate "nothing to query" case, and it still
produces a score of 0 for that component, not an N/A for the metric).

Query template — **always joint method+domain, never the method name alone** (closes the
sem-search gaming route from §1):

```python
def sem_query(primary_method_name: str, method_domain_claimed: str) -> dict:
    query = f"{primary_method_name} validation {method_domain_claimed}"
    return semantic_scholar.search(
        query=query,
        fields=["title", "abstract", "citationCount", "year", "venue"],
        limit=10,
    )
```

Deterministic turn-into-subscore:
```python
def established_subscore(sem_hits: list[dict], method_domain_claimed: str) -> float:
    if not sem_hits:
        return 0.0  # unverifiable -> scored as unverified, per penalize-don't-skip
    # A hit "counts" as domain-validating evidence if the domain term appears in its
    # title/abstract AND it has a non-trivial citation footprint (established, not a one-off).
    domain_terms = method_domain_claimed.lower().split()
    validating = [
        h for h in sem_hits
        if any(t in (h["title"] + " " + (h.get("abstract") or "")).lower() for t in domain_terms)
        and h.get("citationCount", 0) >= 20
    ]
    if len(validating) >= 2:
        return 1.0   # multiple independent validating sources in-domain
    if len(validating) == 1:
        return 0.6   # some support, thin
    return 0.15       # method exists in literature but not tied to this domain -> likely a stretch
```

### Step 3 — Composite score

```python
from dataclasses import dataclass

@dataclass
class M32Inputs:
    method_identified: bool          # primary_method_name is not None
    is_generalization: bool
    justification_present: bool      # post parse_extraction() grounding check
    established_subscore: float      # from Step 2, already floors at 0.0 on no-data
    constraints_md_thin: bool        # heuristic: fewer than 2 non-empty top-level sections,
                                      # or "no limitations stated"-style bare content
    method_file_genre_mismatch: bool # flagged upstream (e.g. per Seal L1 §2 check) if a method
                                      # file was forced onto a genre it doesn't fit

def score_M32(x: M32Inputs) -> float:
    # Component A: could we even identify a concrete, checkable method? (0/1)
    A = 1.0 if x.method_identified and not x.method_file_genre_mismatch else 0.0

    # Component B: is the method, as applied to this domain, externally established? (0..1)
    B = x.established_subscore if x.method_identified else 0.0

    # Component C: warrant/justification for the choice.
    #   - standard use in an established domain (not a generalization): full credit
    #   - generalization, disclosed and grounded: partial credit (still added risk, but honest)
    #   - generalization, undisclosed/unjustified: floor
    #   - method not identified at all: floor
    if not x.method_identified:
        C = 0.0
    elif not x.is_generalization:
        C = 1.0
    elif x.is_generalization and x.justification_present:
        C = 0.6
    else:
        C = 0.0

    composite = 0.25 * A + 0.45 * B + 0.30 * C

    # Availability/thinness multiplier: a bare constraints.md is itself a defect (per shape doc,
    # "a bare 'no limitations stated' is a red flag") and discounts the whole score rather than
    # being scored separately, since a thin constraints.md degrades our confidence in B and C too.
    if x.constraints_md_thin:
        composite *= 0.7

    return round(composite, 4)
```

### Step 4 — Grounding / audit trail

The scoring function must be called with, and the pipeline must persist alongside the score:
`primary_method_name`, `method_domain_claimed`, `generalization_evidence_quote`,
`justification_quote` + `justification_source_ref`, and the raw top-3 `sem` hits used for
`established_subscore`. This is what makes the score auditable/contestable rather than an opaque
LLM judgment — every component traces to either a verbatim artifact quote or an external API
result, never to free-floating LLM opinion.

## 4. Why it's hard to Goodhart

- The external `[sem]` call is the load-bearing check, and it is queried on **method + domain
  jointly** — an artifact/paper cannot inflate this score just by using a famous method name,
  because the query will fail to find domain-matching validating literature if the application is
  actually a stretch. Gaming would require actually finding real supporting literature, which is
  the thing we want rewarded anyway.
- Justification credit requires a **verbatim quote plus a `§X.Y` source reference** matching
  `constraints.md`'s own citation convention — a fabricated or vague justification (no traceable
  source) is deterministically rejected in `parse_extraction`, closing the laundering route.
- The genre-mismatch check (component A) means a compiler cannot inflate "method identified" by
  forcing a method file onto a paper that doesn't have one — an already-known Seal-Level-1 defect
  is wired directly into this metric's floor rather than left as someone else's problem.
- Thinness of `constraints.md` multiplies the *whole* composite down rather than being a separate
  skippable check, so gaming one component (e.g., getting a good `established_subscore`) cannot
  fully compensate for starving the limitations section.

## 5. Composition with the rest of the suite

M32 is deliberately silent on execution correctness, statistical power, reproducibility, and
evidence-table consistency — those remain D6/other metrics' job. M32 only ever asks "was this the
right method, and if it was a stretch, did the paper own that stretch." Because its three
components (identifiability, external validity, disclosed warrant) are each independently
groundable in either a quote or an API call, it can sit alongside a broader rigor metric without
duplicating it: a paper can score high on generic rigor (well-executed, well-powered) while scoring
low on M32 (rigorously executed but using the wrong tool for the claim), and vice versa
(exploratory/generalized method, honestly flagged, less "rigorous" in a narrow sense but honest
about its own reach — which this metric explicitly rewards over silent overreach).
