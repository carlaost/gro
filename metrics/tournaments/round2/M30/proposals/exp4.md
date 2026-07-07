# M30 — Assumption realism & limitation validity (expander 4)

**Artifact**: `logic/solution/constraints.md` (§7, always present) + optional sibling method files for
domain context. **Tag**: [sem] (requires an LLM judgment call; not resolvable by string-matching alone).

## 1. What this indicator is actually catching

`constraints.md` has three (sometimes four) sections: **Boundary conditions**, **Assumptions**,
**Known limitations**, and an optional compiler-added **Additional caveats** subsection. Two other
checks already look at this file from different angles:

- Round-1 shape-07's own concreteness check asks: *is each bullet specific enough to be useful* (dense
  prose vs. vague filler)?
- The ARA verifier's D3 explicitness check asks: *is the section present and does it say something at
  all* (structural completeness)?

Neither of those asks the question that actually determines whether the constraints section is doing
real epistemic work: **is the content true-to-the-work and non-redundant?** A bullet can be perfectly
concrete and perfectly explicit while still being a lie of omission. Two specific ways this happens,
which is why this metric has two sub-targets bundled under one name:

**(a) Dreamcase vs. real assumptions.** An assumption is "dreamcase" when it is chosen because it makes
the analysis tractable or the result look clean, not because it's a plausible property of the real
setting the paper claims to speak to. E.g. che26's own A2 ("selecting the single most comprehensive
dataset per cohort yields statistically independent nodes — no patient double-counted") is a load-bearing
assumption about the very cohorts being pooled; whether it is realistic (COULD overlapping patients
across "independent" cohorts realistically occur, given how AD cohorts are recruited/shared) is exactly
the kind of thing that requires field knowledge to judge, not pattern matching. A dreamcase version of
the same claim would assume away the one condition that would most threaten the pooling — and a
compiler/paper duo that states the assumption without ever flagging its shakiness is doing something
different (and worse) than one that states it and immediately runs a sensitivity check.

**(b) Limitations that add zero new information.** A genuine limitation narrows the space of situations
in which the result is trustworthy — it names a specific new condition (a subgroup, an artifact, a
mechanism, an interaction) not already implied by the Boundary conditions / Assumptions bullets. A
boilerplate limitation ("further research with larger sample sizes is warranted", "results may not
generalize to other populations") is stock language that appears near-verbatim across genres regardless
of what the study actually did, and it commits to nothing falsifiable. The shape file itself flags the
degenerate case explicitly: *"a bare 'no limitations stated' is a red flag, since essentially every
paper states some caveat"* — meaning absence-of-content here is not a neutral N/A, it is itself
evidence of a defect (either the paper genuinely didn't reflect, or the compiler dropped real caveats
the source had).

### What it must reward
- Assumptions that are **load-bearing and falsifiable** — if untrue, the conclusion would change — and
  that are stated plainly enough that a reader could go check them.
- Assumptions the paper itself stress-tests (sensitivity analysis, robustness check, alternative
  specification) — this is direct evidence the assumption was treated as a real risk, not swept under
  the rug.
- Limitations that name a **specific mechanism/subgroup/artifact** tied to a location in the paper
  (`§4.5`, a named table, a named assay) and that constitute a genuinely *new* boundary not already
  covered by Boundary conditions.
- Presence of the compiler's **Additional caveats (data-quality notes)** subsection when the
  evidence layer plausibly contains an internal inconsistency (per shape-file guidance, this is a
  coverage signal a metric can specifically probe).

### What it must NOT reward
- Bullet **count**. Padding with many vacuous bullets must not outscore one honest, load-bearing one.
- Assumptions phrased so generically they're unfalsifiable ("we assume the data are representative of
  the population").
- Limitations that are **restatements** of an already-declared boundary condition or assumption
  (circular, not incremental).
- Limitations drawn from a small, genre-generic **boilerplate vocabulary** ("larger sample size",
  "further research needed", "may not generalize") when nothing paper-specific is attached to them.
- Concreteness/explicitness per se — that's already scored elsewhere; rewarding it again here would
  duplicate signal instead of adding it.

## 2. Failure modes / gaming routes this must resist

1. **Volume padding** — stuff Known limitations with many short, generic bullets hoping length reads as
   depth. Countered by per-bullet scoring capped by specificity/novelty, not bullet count.
2. **Boilerplate mimicry** — phrase a vacuous limitation using paper-specific nouns so it *looks*
   specific ("further research is needed with larger cohorts of AD patients") while adding no real new
   condition. Countered by requiring the LLM judge to state what *new* failure condition the bullet
   introduces, not just whether it mentions a specific-sounding noun.
3. **Convenient assumption selection** — state true-but-irrelevant assumptions (arithmetic works, data
   was correctly transcribed) to inflate the assumption list while omitting the one assumption that
   actually determines whether the method is valid. Countered by requiring the judge to flag
   load-bearing-ness, and by an explicit "known threat to validity not addressed" check drawing on the
   judge's domain knowledge of the paper's genre.
4. **Compiler under-extraction** — the source paper states a real limitation but the compiler dropped it
   during compilation, producing a clean-looking but false constraints.md. Only partially catchable
   without the source PDF; caught indirectly via the data-quality-caveats cross-check (§3 below) and via
   flagging genre-mismatched thinness (an omics paper with zero cohort-related limitations is
   suspicious).
5. **Gaming by inflating "Additional caveats"** with cosmetic nitpicks to look rigorous while the real
   Known limitations section stays boilerplate. Countered by scoring sections independently and not
   letting one section's score compensate for another's floor penalty.

## 3. Generation / compute workflow

### 3.1 Inputs
- `logic/solution/constraints.md` — required, parsed into: `boundary_conditions: list[str]`,
  `assumptions: list[{id, text}]`, `known_limitations: list[{name, prose, section_ref|None}]`,
  `additional_caveats: list[str]` (optional section).
- Optional context (read-only, for the [sem] step's domain grounding; absence does not block scoring):
  first ~500 words of any sibling method file (`study_design.md`/`method.md`/etc.) to tell the judge what
  genre/methodology this is, so it can reason about field-standard threats to validity.
- Optional cross-check input: whether `evidence/` tables carry any internal-consistency/data-quality
  flags (per shape-file guidance) — used only for the Additional-caveats coverage check in §3.5.

### 3.2 Step 0 — Parse
```python
import re
from dataclasses import dataclass, field

@dataclass
class Constraints:
    present: bool
    boundary_conditions: list[str] = field(default_factory=list)
    assumptions: list[dict] = field(default_factory=list)      # {"id": "A1", "text": ...}
    known_limitations: list[dict] = field(default_factory=list) # {"name":..., "prose":..., "section": ...}
    additional_caveats: list[str] = field(default_factory=list)

SECTION_RE = re.compile(r'^##\s+(.*)$', re.MULTILINE)

def parse_constraints(raw: str | None) -> Constraints:
    if raw is None or not raw.strip():
        return Constraints(present=False)

    sections = {}
    heads = list(SECTION_RE.finditer(raw))
    for i, m in enumerate(heads):
        title = m.group(1).strip()
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(raw)
        sections[title] = raw[start:end].strip()

    def bullets(text: str) -> list[str]:
        return [b.strip('- ').strip() for b in text.splitlines()
                if b.strip().startswith('-') and b.strip('- ').strip()]

    c = Constraints(present=True)
    for title, body in sections.items():
        low = title.lower()
        if low.startswith('boundary conditions'):
            c.boundary_conditions = bullets(body)
        elif low.startswith('assumptions'):
            for b in bullets(body):
                m = re.match(r'^\*?\*?([A-Z]\d+)\*?\*?:\s*(.*)$', b)
                c.assumptions.append({"id": m.group(1), "text": m.group(2)} if m
                                      else {"id": None, "text": b})
        elif low.startswith('known limitations'):
            sec_ref = re.search(r'\(§([\w.]+)\)', title)
            for b in bullets(body):
                m = re.match(r'^\*\*(.+?)\*\*:\s*(.*)$', b)
                c.known_limitations.append({
                    "name": m.group(1) if m else None,
                    "prose": m.group(2) if m else b,
                    "section": sec_ref.group(1) if sec_ref else None,
                })
        elif low.startswith('additional caveats'):
            c.additional_caveats = bullets(body)
    return c
```

### 3.3 Step 1 — Availability / thinness gate (penalize-don't-skip, hard constraint)

This is where the metric enforces "unavailability is itself an input, never a skip." Every branch below
resolves to a **numeric score**, never `None`/`N-A`.

```python
def availability_floor(c: Constraints) -> tuple[float, list[str]]:
    """Returns (floor_multiplier in [0,1], flags). Multiplies the final score — never short-circuits
    to a null/skip value."""
    flags = []
    if not c.present:
        return 0.0, ["constraints.md missing entirely — treated as worst case, not N/A"]

    floor = 1.0
    if not c.assumptions:
        floor *= 0.35
        flags.append("no assumptions listed — cannot assess load-bearing realism")
    if not c.known_limitations:
        # shape file explicitly calls this a red flag, not a neutral absence
        floor *= 0.25
        flags.append("no limitations stated — treated as a defect per shape-file guidance, not N/A")
    else:
        avg_len = sum(len(l["prose"].split()) for l in c.known_limitations) / len(c.known_limitations)
        if avg_len < 8:
            floor *= 0.6
            flags.append(f"limitations are extremely thin (avg {avg_len:.1f} words) — penalized")
    return floor, flags
```

### 3.4 Step 2 — Deterministic boilerplate pre-filter

A small fixed library of genre-generic hedge phrases, matched with fuzzy string similarity so paraphrases
are caught too. This runs *before* the LLM call so the judge's attention (and the score) is anchored to
a cheap, auditable, non-gameable signal rather than trusting the LLM to notice boilerplate unprompted.

```python
from rapidfuzz import fuzz

BOILERPLATE_LIBRARY = [
    "further research is needed",
    "future studies should validate this in other populations",
    "larger sample size may be needed",
    "results may not generalize to other populations",
    "additional validation is required",
    "this study has several limitations",
    "more work is needed to confirm these findings",
    "the sample size was relatively small",
]

def boilerplate_ratio(prose: str) -> float:
    """Max fuzzy similarity to any stock phrase, 0-1."""
    return max(fuzz.token_set_ratio(prose.lower(), phrase) / 100 for phrase in BOILERPLATE_LIBRARY)

def flag_boilerplate(limitations: list[dict]) -> list[dict]:
    for lim in limitations:
        lim["boilerplate_score"] = boilerplate_ratio(lim["prose"])
        lim["is_boilerplate"] = lim["boilerplate_score"] >= 0.75 and not re.search(r'\d|%|assay|platform|cohort|subgroup', lim["prose"], re.I)
    return limitations
```

### 3.5 Step 3 — Redundancy backstop (limitations vs. boundary/assumptions)

Deterministic similarity check so "adds new info" isn't purely an LLM vibe-check.

```python
def novelty_backstop(limitations: list[dict], boundary_conditions: list[str], assumptions: list[dict]) -> list[dict]:
    prior_text = boundary_conditions + [a["text"] for a in assumptions]
    for lim in limitations:
        sims = [fuzz.token_set_ratio(lim["prose"].lower(), p.lower()) / 100 for p in prior_text] or [0.0]
        lim["max_prior_similarity"] = max(sims)
        lim["likely_restatement"] = lim["max_prior_similarity"] >= 0.8
    return limitations
```

### 3.6 Step 4 — [sem] LLM judgment call

One call per artifact. This is the only step that requires real field/domain judgment (dreamcase vs.
real is not a lexical property). The prompt is deliberately structured to force per-item verdicts with
short justifications, so the output is easy to turn into deterministic sub-scores rather than trusting a
single holistic number from the model.

**Exact prompt template:**

```
SYSTEM: You are a skeptical peer reviewer with deep domain knowledge of the paper's field. You are
given ONLY the "Constraints, Assumptions, and Limitations" section of a compiled research artifact,
plus (if provided) a short excerpt describing the paper's method/study design. Judge honestly; do not
give benefit of the doubt.

USER:
## Method context (may be partial or absent)
{method_excerpt_or_"Not provided"}

## Boundary conditions
{boundary_conditions_bulleted}

## Assumptions
{assumptions_bulleted_with_ids}

## Known limitations
{limitations_bulleted_with_names_and_section_refs}

## Additional caveats (compiler-flagged data-quality notes)
{additional_caveats_bulleted_or_"None"}

For EACH assumption, answer:
1. `load_bearing`: yes/no — would the paper's central conclusion change if this assumption were false?
2. `realism`: "real" | "dreamcase" | "unclear" — is this a plausible property of the actual setting, or
   is it chosen because it conveniently makes the analysis work? Justify in <=25 words using domain
   knowledge of how this kind of study/data usually behaves.
3. `stress_tested`: yes/no — does the paper appear to test what happens if this assumption fails
   (sensitivity analysis, robustness check, alternate specification)?

For EACH known limitation, answer:
1. `adds_new_condition`: yes/partial/no — does this name a genuinely new situation/subgroup/mechanism
   where the result may not hold, beyond what Boundary conditions/Assumptions already say? Name the new
   condition in <=15 words, or say "none — restates X" / "none — generic boilerplate".
2. `specific`: yes/no — is it tied to a concrete detail (a number, named subgroup, named assay/platform,
   section reference)?

Finally, answer:
`missing_known_threats`: list up to 3 well-known threats to validity for THIS genre/method that are
conspicuously absent from both Assumptions and Known limitations (e.g., for a diagnostic-accuracy
meta-analysis: verification bias, spectrum bias, incorporation bias). Empty list if you cannot identify
any with confidence — do not invent generic ones just to fill the list.

Return strict JSON:
{
  "assumptions": [{"id": "...", "load_bearing": "...", "realism": "...", "realism_reason": "...", "stress_tested": "..."}],
  "limitations": [{"name": "...", "adds_new_condition": "...", "new_condition_named": "...", "specific": "..."}],
  "missing_known_threats": ["..."]
}
```

**Turning the LLM's structured output into a deterministic sub-score** (the LLM never outputs a raw
score itself — only categorical verdicts + short text, which this function maps via a fixed rubric):

```python
def score_llm_verdicts(verdict: dict, limitations: list[dict]) -> dict:
    # --- Assumption realism sub-score ---
    REALISM_POINTS = {"real": 1.0, "unclear": 0.4, "dreamcase": 0.0}
    a_scores = []
    for a in verdict["assumptions"]:
        base = REALISM_POINTS[a["realism"]]
        weight = 1.5 if a["load_bearing"] == "yes" else 0.5  # load-bearing assumptions count more
        if a["stress_tested"] == "yes":
            base = min(1.0, base + 0.2)  # bonus for testing a risky assumption
        a_scores.append(base * weight)
    assumption_score = (sum(a_scores) / sum(1.5 if a["load_bearing"] == "yes" else 0.5
                                             for a in verdict["assumptions"])) if verdict["assumptions"] else 0.0

    # --- Limitation novelty sub-score, cross-checked against deterministic backstops ---
    NOVELTY_POINTS = {"yes": 1.0, "partial": 0.5, "no": 0.0}
    l_scores = []
    by_name = {l.get("name"): l for l in limitations}
    for lv in verdict["limitations"]:
        base = NOVELTY_POINTS[lv["adds_new_condition"]]
        det = by_name.get(lv["name"], {})
        if det.get("is_boilerplate") or det.get("likely_restatement"):
            base = min(base, 0.2)  # deterministic backstop caps LLM generosity
        if lv["specific"] == "yes":
            base = min(1.0, base + 0.1)
        l_scores.append(base)
    limitation_score = sum(l_scores) / len(l_scores) if l_scores else 0.0

    # --- Missing-known-threats penalty ---
    threat_penalty = min(0.3, 0.1 * len(verdict.get("missing_known_threats", [])))

    return {
        "assumption_realism": assumption_score,
        "limitation_novelty": limitation_score,
        "missing_threat_penalty": threat_penalty,
    }
```

### 3.7 Step 5 — Final score

```python
def compute_m30(raw_constraints_md: str | None,
                 method_excerpt: str | None,
                 llm_judge_fn) -> dict:
    c = parse_constraints(raw_constraints_md)
    floor, floor_flags = availability_floor(c)

    if floor == 0.0:
        return {"score": 0.0, "flags": floor_flags, "detail": None}

    c.known_limitations = flag_boilerplate(c.known_limitations)
    c.known_limitations = novelty_backstop(c.known_limitations, c.boundary_conditions, c.assumptions)

    verdict = llm_judge_fn(
        method_excerpt=method_excerpt or "Not provided",
        boundary_conditions=c.boundary_conditions,
        assumptions=c.assumptions,
        limitations=c.known_limitations,
        additional_caveats=c.additional_caveats,
    )  # -> parsed JSON per §3.6 schema

    sub = score_llm_verdicts(verdict, c.known_limitations)

    raw_score = 0.55 * sub["assumption_realism"] + 0.45 * sub["limitation_novelty"]
    raw_score = max(0.0, raw_score - sub["missing_threat_penalty"])

    final = round(100 * floor * raw_score, 1)  # floor multiplies everything — never bypassed
    return {
        "score": final,
        "flags": floor_flags,
        "detail": {**sub, "missing_known_threats": verdict.get("missing_known_threats", [])},
    }
```

The `floor` multiplier is what encodes penalize-don't-skip structurally: a missing/empty
Assumptions or Known-limitations section drags the ceiling down (0.35 / 0.25) regardless of how the
[sem] step scores the little content that *is* present — it can never be skipped to N/A, and it can
never fully recover to 100 once thin.

### 3.8 Worked example (che26, from the shape file)

- Boundary conditions: 2 bullets (scope = blood p-tau isoforms; relative rankings not absolute AUC).
- Assumptions: A2 ("most comprehensive dataset per cohort ⇒ independence, no double-counting").
  Judge verdict: `load_bearing: yes` (pooling validity hinges on this), `realism: unclear` (cohort
  overlap in AD biomarker studies is a known real risk — ADNI/AIBL-type cohorts are frequently
  re-used/merged across "different" datasets), `stress_tested: no` → assumption_score pulled down
  meaningfully despite the assumption being clearly and explicitly stated (good D3/07 scores don't
  save it here).
- Known limitations: "Batch effects" bullet — judge verdict: `adds_new_condition: partial` (names a
  real, specific mechanism — manual immunoassay batch drift — but doesn't say which platforms/cohorts
  are most exposed), `specific: yes` → decent but not maximal score.
- Additional caveats: Table 1/caption mismatch is present — this is exactly the kind of
  data-quality-note the shape file singles out as valuable; it doesn't feed the numeric formula above
  directly but is reported in `detail` for downstream aggregation/audit trails.

## 4. Why this is hard to Goodhart

- **The core judgment (realism, novelty) is not lexical.** Padding bullets with plausible-sounding nouns
  doesn't help once the deterministic boilerplate/redundancy backstops cap the LLM's generosity, and the
  LLM is explicitly asked to justify *why* something is dreamcase/boilerplate using field knowledge, not
  asked for a bare score it could be primed toward.
- **Load-bearing weighting means gaming the wrong assumptions is a losing move.** Inflating the
  assumption list with trivially-true, non-load-bearing statements gets `weight = 0.5` instead of `1.5`
  and can't rescue a low score on the one assumption that actually matters.
- **The missing-known-threats check is adversarial by construction** — it asks the judge to name
  field-standard failure modes the artifact *doesn't* mention, which a compiler/author cannot pre-empt
  by wordsmithing the bullets that ARE present; the only way to score well here is for the paper to have
  actually addressed the standard threats.
- **Two independent deterministic backstops (boilerplate-library fuzzy match, prior-text similarity)
  bound the LLM's ceiling**, so an LLM that's been "convinced" by well-written boilerplate still gets
  capped by string-level evidence the model can't argue away.
- **The floor multiplier is structural, not a suggestion to the judge** — no LLM verdict can push a
  thin/absent constraints.md back above its availability ceiling, closing the "just say something vague
  but confident" loophole.

## 5. Composition with the rest of the suite

This metric is designed to be **orthogonal by subtraction**, not addition: round-1 07's concreteness
check and verifier D3's explicitness check both look at the *form* of the constraints section (is it
there, is it specific-sounding); M30 is explicitly told to skip re-scoring those axes and instead scores
*truth-value plausibility* and *incremental information content* — properties that are invisible to a
presence/specificity checker (a perfectly concrete, perfectly explicit assumption can still be dreamcase;
a perfectly concrete limitation can still be a redundant restatement). Because the three checks read the
same artifact but score disjoint properties, a paper cannot satisfy all three by optimizing on any single
axis — e.g., writing longer, more specific-sounding, boilerplate-avoiding bullets improves 07/D3 but only
improves M30 if the added specificity also constitutes a genuinely new, realistic, load-bearing claim.
This also composes usefully with any evidence-layer internal-consistency metric: M30's "Additional
caveats" check is the natural downstream partner of an evidence-table consistency check — one flags the
discrepancy exists, this one flags whether `constraints.md` was honest enough to surface it.
