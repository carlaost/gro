## Changes (cycle 2)

Base: exp4 (cycle-1 rank 2, co-winner). This revision applies all five named cycle-2 directions from
`critique_c1.md`, plus one absorbed idea from the other lane (exp3's worst-offender guard), while
preserving exp4's core edge (single-[sem]-call cost profile, deterministically-capped LLM verdicts,
worked example).

1. **Grounded `missing_known_threats` (direction 1).** The judge must now name, for each proposed
   missing threat, the *specific design choice in the method excerpt* that makes the threat applicable,
   quoted verbatim. A deterministic post-check (§3.6.1) discards any threat whose quote doesn't
   substring/fuzzy-match the excerpt — closing the "judge invents a threat from genre stereotype alone"
   failure mode named in the critique. This moves the mechanism partway toward exp2's method-scan rigor
   without adding a second LLM call.
2. **Softened fuzzy thresholds (direction 2).** The old hard cutoffs (boilerplate ≥0.75, redundancy
   ≥0.8) are replaced by a three-band scheme: **high-confidence match** (≥0.85) still hard-caps
   deterministically (string evidence the LLM can't argue away); **ambiguous band** (0.55–0.85) is no
   longer an automatic cap — it is instead surfaced *to the same judge call* as a labeled candidate for
   confirmation, so a real, specific limitation that happens to reuse stock nouns isn't wrongly
   flattened; **below 0.55** is untouched. This removes an asserted-not-derived threshold while adding
   no new LLM round-trip.
3. **Cross-bucket dedup (direction 3).** `novelty_backstop` is generalized from "limitations vs.
   (boundary ∪ assumptions)" to a full canonical-priority pairwise check across all three buckets
   (boundary → assumptions → limitations), so restating a boundary condition as an assumption, or
   splitting one caveat into three limitation bullets, is caught — not just the limitation-vs-prior
   direction exp4 originally had.
4. **Data-quality-caveat cross-check now scored, not just logged (direction 4).** `caveat_coverage`
   becomes a real weighted term in the final formula (previously reported only in `detail`). Weights
   are rebalanced (0.50 / 0.35 / 0.15) to make room for it without diluting the two primary sub-targets
   below their cycle-1 dominance.
5. **Expanded worked example (direction 5).** §3.9 now includes three branches: the original che26
   content trace, an availability-floor branch (empty `constraints.md`), and a missing-known-threats
   branch showing a genre-standard threat (verification/spectrum bias) che26 omits, with its
   design-choice grounding quote.
6. **Absorbed from exp3: worst-offender guard.** A single flagrant `dreamcase` + `load_bearing: yes`
   assumption, or a limitations section that is *entirely* boilerplate/restatement, now hard-caps the
   raw score at 0.5 regardless of how the rest of the artifact averages out — closing the residual
   "dilute the one bad item with several fine trivial ones" route that load-bearing weighting alone
   only partially blocks (§3.7, step 5a).

Everything else (single-call [sem] cost profile, availability floor, penalize-don't-skip structure,
composition-with-suite argument) is retained from exp4 and re-verified against the brief below.

---

# M30 — Assumption realism & limitation validity (expander 4, cycle 2)

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

Neither asks the question that actually determines whether the constraints section is doing real
epistemic work: **is the content true-to-the-work and non-redundant?** A bullet can be perfectly
concrete and perfectly explicit while still being a lie of omission. Three specific ways this happens
(the third promoted to full scoring status in this cycle):

**(a) Dreamcase vs. real assumptions.** An assumption is "dreamcase" when it is chosen because it makes
the analysis tractable or the result look clean, not because it's a plausible property of the real
setting the paper claims to speak to. E.g. che26's own A2 ("selecting the single most comprehensive
dataset per cohort yields statistically independent nodes — no patient double-counted") is a
load-bearing assumption about the very cohorts being pooled; whether it is realistic (could overlapping
patients across "independent" cohorts realistically occur, given how AD cohorts are recruited/shared)
requires field knowledge to judge, not pattern matching.

**(b) Limitations that add zero new information.** A genuine limitation narrows the space of situations
in which the result is trustworthy — it names a specific new condition (a subgroup, an artifact, a
mechanism, an interaction) not already implied by Boundary conditions / Assumptions. A boilerplate
limitation ("further research with larger sample sizes is warranted") is stock language that commits to
nothing falsifiable. The shape file flags the degenerate case explicitly: *"a bare 'no limitations
stated' is a red flag ... essentially every paper states some caveat"* — absence-of-content here is
itself evidence of a defect, not a neutral N/A.

**(c) Silent dropping of a compiler-noticed data-quality caveat.** When the evidence layer itself
carries an internal-consistency flag (a table/caption mismatch, arithmetic that doesn't reconcile), a
constraints.md that fails to surface it in **Additional caveats** is not merely incomplete — it is
actively less honest than a constraints.md that has no such caveat to report at all, because the
compiler had the information and dropped it. Cycle 1 treated this as an audit note; this cycle scores
it, because the shape file explicitly calls it "a coverage gap a metric can specifically probe."

### What it must reward
- Assumptions that are **load-bearing and falsifiable** — if untrue, the conclusion would change — and
  stated plainly enough that a reader could go check them.
- Assumptions the paper itself stress-tests (sensitivity analysis, robustness check, alternative
  specification) — direct evidence the assumption was treated as a real risk.
- Limitations that name a **specific mechanism/subgroup/artifact** tied to a location in the paper and
  that constitute a genuinely *new* boundary not already covered elsewhere in the artifact.
- Presence and accuracy of the compiler's **Additional caveats** subsection when the evidence layer
  plausibly contains an internal inconsistency — now a scored coverage term, not just a flag.

### What it must NOT reward
- Bullet **count**. Padding with many vacuous bullets must not outscore one honest, load-bearing one.
- Assumptions phrased so generically they're unfalsifiable.
- Limitations, or assumptions, that **restate** an already-declared bullet from *any* other bucket in
  the file (circular, not incremental) — checked pairwise across all three buckets, not just
  limitation-vs-prior.
- Limitations drawn from a small, genre-generic **boilerplate vocabulary** when nothing paper-specific
  is attached to them — but a limitation that merely *contains* a stock phrase alongside real
  paper-specific content must not be flattened by a blunt threshold (see §3.4).
- Concreteness/explicitness per se — that's already scored elsewhere; rewarding it again here would
  duplicate signal instead of adding it.

## 2. Failure modes / gaming routes this must resist

1. **Volume padding** — stuff Known limitations with many short, generic bullets hoping length reads as
   depth. Countered by per-bullet scoring capped by specificity/novelty, not bullet count, and by the
   worst-offender guard preventing a wash-out average (§3.7 step 5a).
2. **Boilerplate mimicry** — phrase a vacuous limitation using paper-specific nouns so it *looks*
   specific while adding no real new condition. Countered by requiring the judge to state what *new*
   failure condition the bullet introduces, cross-checked against a two-band fuzzy backstop (§3.4) that
   no longer over-fires on genuinely specific bullets that happen to share stock phrasing.
3. **Convenient assumption selection** — state true-but-irrelevant assumptions to inflate the list while
   omitting the one assumption that actually determines validity. Countered by load-bearing weighting
   and the missing-known-threats check.
4. **Compiler under-extraction** — the source paper states a real limitation the compiler dropped.
   Partially caught via genre-mismatched-thinness flagging and, now with real scoring weight, via the
   **caveat-coverage check** (§3.6.2): if the evidence layer flags an internal inconsistency and
   constraints.md is silent about it, that silence now directly costs score rather than only appearing
   in an audit trail.
5. **Gaming by inflating "Additional caveats"** with cosmetic nitpicks while Known limitations stays
   boilerplate. Countered by scoring sections independently (no cross-section compensation) plus the
   worst-offender guard, which looks at the worst *bucket*, not just the worst item.
6. **Threat-list invention** — the judge fabricates a plausible-sounding "missing known threat" that
   isn't actually grounded in what the method describes, inflating the appearance of rigor or unfairly
   penalizing an honest artifact. Countered by requiring a verbatim excerpt quote per threat, discarded
   deterministically if it doesn't match the supplied method text (§3.6.1) — new in this cycle.
7. **Split-bullet padding** — take one real caveat and split it into three bullets across buckets (e.g.
   state part of it as a boundary condition, part as an assumption, part as a limitation) to harvest
   credit three times. Countered by the generalized cross-bucket dedup (§3.5), which was previously
   blind to this because it only checked limitations against prior buckets, never assumption-vs-boundary
   or limitation-vs-limitation.

## 3. Generation / compute workflow

### 3.1 Inputs
- `logic/solution/constraints.md` — required, parsed into: `boundary_conditions: list[str]`,
  `assumptions: list[{id, text}]`, `known_limitations: list[{name, prose, section_ref|None}]`,
  `additional_caveats: list[str]` (optional section).
- Optional context (read-only, for the [sem] step's domain grounding; absence does not block scoring):
  first ~500 words of any sibling method file (`study_design.md`/`method.md`/etc.) to tell the judge what
  genre/methodology this is, and to ground `missing_known_threats` quotes.
- Optional cross-check input: whether `evidence/` tables carry any internal-consistency/data-quality
  flags (per shape-file guidance) — now feeds a scored `caveat_coverage` term (§3.6.2), not just an
  audit note.

### 3.2 Step 0 — Parse

Unchanged from cycle 1:

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

Unchanged in mechanism from cycle 1 — every branch resolves to a numeric score, never `None`/`N-A`.

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
        floor *= 0.25
        flags.append("no limitations stated — treated as a defect per shape-file guidance, not N/A")
    else:
        avg_len = sum(len(l["prose"].split()) for l in c.known_limitations) / len(c.known_limitations)
        if avg_len < 8:
            floor *= 0.6
            flags.append(f"limitations are extremely thin (avg {avg_len:.1f} words) — penalized")
    return floor, flags
```

### 3.4 Step 2 — Deterministic boilerplate pre-filter (cycle-2: two-band, not one hard cutoff)

**Change from cycle 1 (direction 2):** a single `>=0.75` cutoff either fully capped a limitation or left
it untouched — a real, specific limitation that happens to reuse a stock noun ("larger cohort") could be
wrongly flattened, and the threshold itself was asserted rather than derived. We now split into a
**high-confidence band** (still a deterministic hard cap, since at this similarity the text essentially
*is* the stock phrase) and an **ambiguous band** that is deferred to the judge as a labeled candidate
instead of auto-capped.

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

HARD_CAP_THRESHOLD = 0.85     # was 0.75 in cycle 1 — raised so only near-verbatim matches auto-cap
AMBIGUOUS_LOW = 0.55          # below this, no boilerplate signal at all

def boilerplate_ratio(prose: str) -> float:
    """Max fuzzy similarity to any stock phrase, 0-1."""
    return max(fuzz.token_set_ratio(prose.lower(), phrase) / 100 for phrase in BOILERPLATE_LIBRARY)

def flag_boilerplate(limitations: list[dict]) -> list[dict]:
    has_paper_specific_marker = lambda p: bool(re.search(r'\d|%|assay|platform|cohort|subgroup', p, re.I))
    for lim in limitations:
        ratio = boilerplate_ratio(lim["prose"])
        lim["boilerplate_score"] = ratio
        if ratio >= HARD_CAP_THRESHOLD and not has_paper_specific_marker(lim["prose"]):
            lim["boilerplate_verdict"] = "hard_cap"       # deterministic, judge cannot override upward
        elif ratio >= AMBIGUOUS_LOW:
            lim["boilerplate_verdict"] = "ambiguous"       # surfaced to judge for confirmation, §3.6
        else:
            lim["boilerplate_verdict"] = "clear"
    return limitations
```

### 3.5 Step 3 — Cross-bucket redundancy backstop (cycle-2: generalized from limitation-only)

**Change from cycle 1 (directions 3 & 7):** cycle 1 only checked `known_limitations` against
`boundary_conditions ∪ assumptions`. This missed restating a boundary condition as an assumption, or
splitting one caveat across multiple limitation bullets. We now run a canonical-priority pairwise check:
each bucket is checked against every bucket that precedes it in the fixed order
`boundary_conditions → assumptions → known_limitations`, plus within-bucket duplicate detection for the
split-bullet route.

```python
def novelty_backstop(c: "Constraints") -> "Constraints":
    def texts_of(bucket_name):
        if bucket_name == "boundary_conditions":
            return [(i, t) for i, t in enumerate(c.boundary_conditions)]
        if bucket_name == "assumptions":
            return [(i, a["text"]) for i, a in enumerate(c.assumptions)]
        return [(i, l["prose"]) for i, l in enumerate(c.known_limitations)]

    order = ["boundary_conditions", "assumptions", "known_limitations"]
    prior_texts: list[str] = []
    for bucket_name in order:
        items = texts_of(bucket_name)
        # within-bucket duplicate/split check
        own_texts = [t for _, t in items]
        for i, (idx, text) in enumerate(items):
            sims_prior = [fuzz.token_set_ratio(text.lower(), p.lower()) / 100 for p in prior_texts] or [0.0]
            sims_within = [fuzz.token_set_ratio(text.lower(), other.lower()) / 100
                           for j, other in enumerate(own_texts) if j != i] or [0.0]
            max_sim = max(sims_prior + sims_within)
            record = {"bucket": bucket_name, "index": idx, "max_prior_similarity": max_sim,
                      "likely_restatement": max_sim >= 0.8}
            if bucket_name == "known_limitations":
                c.known_limitations[idx].update({
                    "max_prior_similarity": max_sim,
                    "likely_restatement": max_sim >= 0.8,
                })
            elif bucket_name == "assumptions":
                c.assumptions[idx]["likely_restatement"] = max_sim >= 0.8
            # boundary_conditions has nothing before it — record is informational only
        prior_texts.extend(own_texts)
    return c
```

### 3.6 Step 4 — [sem] LLM judgment call (single call, cycle-2 prompt)

One call per artifact — cost profile unchanged from cycle 1, which was the differentiator cited in
`critique_c1.md` ("far cheaper than exp2"). The prompt is extended in three places: (1) ambiguous-band
boilerplate candidates are now shown to the judge for confirmation instead of auto-capped; (2) each
`missing_known_threats` entry must carry a verbatim excerpt quote; (3) a `caveat_coverage` block is
added when evidence-layer flags exist.

**Exact prompt template:**

```
SYSTEM: You are a skeptical peer reviewer with deep domain knowledge of the paper's field. You are
given ONLY the "Constraints, Assumptions, and Limitations" section of a compiled research artifact,
plus (if provided) a short excerpt describing the paper's method/study design, and (if provided) a note
about internal-consistency flags found in the paper's evidence tables. Judge honestly; do not give
benefit of the doubt. Never invent claims about the method that are not supported by the excerpt.

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

## Evidence-layer internal-consistency flags (if any were detected upstream)
{evidence_flags_bulleted_or_"None detected"}

## Limitations flagged as ambiguous boilerplate-candidates (fuzzy match 0.55-0.85 to a stock phrase —
## confirm or reject; do not default to boilerplate just because the phrase overlaps)
{ambiguous_boilerplate_candidates_or_"None"}

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

For EACH item in "ambiguous boilerplate-candidates", answer:
`boilerplate_confirmed`: yes/no — does this bullet, despite the phrase overlap, actually commit to a
paper-specific, falsifiable condition (answer "no", i.e. reject the boilerplate flag), or is the
specific-looking language decorative with no real new content (answer "yes")?

If evidence-layer internal-consistency flags were provided, answer:
`caveat_coverage`: "full" | "partial" | "missing" — does "Additional caveats" (or elsewhere in the
file) faithfully surface the flagged inconsistency? "partial" if mentioned but materially understated;
"missing" if the flagged inconsistency is not surfaced at all. Omit this field if no flags were provided.

Finally, answer:
`missing_known_threats`: list up to 3 well-known threats to validity for THIS genre/method that are
conspicuously absent from both Assumptions and Known limitations (e.g., for a diagnostic-accuracy
meta-analysis: verification bias, spectrum bias, incorporation bias). For EACH threat, you MUST include
`design_choice_quote`: a verbatim substring copied from the Method context excerpt that is the specific
design choice making this threat applicable (e.g. "cohorts were selected retrospectively"). If you
cannot quote such a substring verbatim from the excerpt, do not include the threat. Empty list if you
cannot identify any with confidence — do not invent generic ones just to fill the list.

Return strict JSON:
{
  "assumptions": [{"id": "...", "load_bearing": "...", "realism": "...", "realism_reason": "...", "stress_tested": "..."}],
  "limitations": [{"name": "...", "adds_new_condition": "...", "new_condition_named": "...", "specific": "..."}],
  "boilerplate_confirmations": [{"name": "...", "boilerplate_confirmed": "..."}],
  "caveat_coverage": "full" | "partial" | "missing" | null,
  "missing_known_threats": [{"threat": "...", "design_choice_quote": "..."}]
}
```

#### 3.6.1 Deterministic post-check on `missing_known_threats` (new, direction 1)

Discards any threat whose quote isn't actually in the supplied excerpt — the judge cannot get credit
for a threat it can't ground, closing the invention route named in the critique.

```python
def filter_grounded_threats(verdict: dict, method_excerpt: str | None) -> list[dict]:
    if not method_excerpt:
        return []  # no excerpt was ever supplied — nothing can be grounded, so nothing is credited
    kept = []
    for t in verdict.get("missing_known_threats", []):
        quote = t.get("design_choice_quote", "")
        if quote and fuzz.partial_ratio(quote.lower(), method_excerpt.lower()) >= 90:
            kept.append(t)
        # else: silently dropped — an ungrounded "threat" is treated as if never raised,
        # not as a free penalty point and not as a bonus
    return kept
```

#### 3.6.2 Applying the two-band boilerplate resolution (new, direction 2)

```python
def resolve_boilerplate(limitations: list[dict], boilerplate_confirmations: list[dict]) -> list[dict]:
    conf_by_name = {c["name"]: c["boilerplate_confirmed"] for c in boilerplate_confirmations}
    for lim in limitations:
        if lim["boilerplate_verdict"] == "hard_cap":
            lim["is_boilerplate"] = True
        elif lim["boilerplate_verdict"] == "ambiguous":
            lim["is_boilerplate"] = conf_by_name.get(lim.get("name"), "no") == "yes"
        else:
            lim["is_boilerplate"] = False
    return limitations
```

### 3.7 Turning verdicts into a deterministic sub-score

```python
def score_llm_verdicts(verdict: dict, limitations: list[dict], assumptions_meta: list[dict],
                        caveat_flags_present: bool) -> dict:
    # --- Assumption realism sub-score ---
    REALISM_POINTS = {"real": 1.0, "unclear": 0.4, "dreamcase": 0.0}
    a_scores = []
    worst_offender = False
    for a in verdict["assumptions"]:
        base = REALISM_POINTS[a["realism"]]
        weight = 1.5 if a["load_bearing"] == "yes" else 0.5
        if a["stress_tested"] == "yes":
            base = min(1.0, base + 0.2)
        if a["realism"] == "dreamcase" and a["load_bearing"] == "yes":
            worst_offender = True   # step 5a guard, absorbed from exp3
        a_scores.append(base * weight)
    total_weight = sum(1.5 if a["load_bearing"] == "yes" else 0.5 for a in verdict["assumptions"])
    assumption_score = (sum(a_scores) / total_weight) if verdict["assumptions"] else 0.0

    # --- Limitation novelty sub-score, cross-checked against deterministic backstops ---
    NOVELTY_POINTS = {"yes": 1.0, "partial": 0.5, "no": 0.0}
    l_scores = []
    by_name = {l.get("name"): l for l in limitations}
    all_boilerplate_or_restated = True
    for lv in verdict["limitations"]:
        base = NOVELTY_POINTS[lv["adds_new_condition"]]
        det = by_name.get(lv["name"], {})
        if det.get("is_boilerplate") or det.get("likely_restatement"):
            base = min(base, 0.2)
        else:
            all_boilerplate_or_restated = False
        if lv["specific"] == "yes":
            base = min(1.0, base + 0.1)
        l_scores.append(base)
    limitation_score = sum(l_scores) / len(l_scores) if l_scores else 0.0
    if verdict["limitations"] and all_boilerplate_or_restated:
        worst_offender = True  # entire limitations bucket is dead weight — step 5a guard

    # --- Caveat coverage sub-score (new, direction 4 — was audit-only in cycle 1) ---
    COVERAGE_POINTS = {"full": 1.0, "partial": 0.5, "missing": 0.0}
    if caveat_flags_present and verdict.get("caveat_coverage"):
        caveat_coverage_score = COVERAGE_POINTS[verdict["caveat_coverage"]]
    else:
        # no evidence-layer flags existed to surface — nothing to catch, scored neutral-full,
        # per penalize-don't-skip: absence of the *triggering condition* is not itself a defect
        # (unlike absence of Known limitations, which the shape file says IS a defect)
        caveat_coverage_score = 1.0

    # --- Missing-known-threats penalty (now grounded per §3.6.1) ---
    threat_penalty = min(0.3, 0.1 * len(verdict.get("_grounded_missing_threats", [])))

    return {
        "assumption_realism": assumption_score,
        "limitation_novelty": limitation_score,
        "caveat_coverage": caveat_coverage_score,
        "missing_threat_penalty": threat_penalty,
        "worst_offender": worst_offender,
    }
```

### 3.8 Step 5 — Final score

```python
def compute_m30(raw_constraints_md: str | None,
                 method_excerpt: str | None,
                 evidence_flags: list[str] | None,
                 llm_judge_fn) -> dict:
    c = parse_constraints(raw_constraints_md)
    floor, floor_flags = availability_floor(c)

    if floor == 0.0:
        return {"score": 0.0, "flags": floor_flags, "detail": None}

    c.known_limitations = flag_boilerplate(c.known_limitations)
    c = novelty_backstop(c)

    ambiguous_candidates = [l for l in c.known_limitations if l["boilerplate_verdict"] == "ambiguous"]

    verdict = llm_judge_fn(
        method_excerpt=method_excerpt or "Not provided",
        boundary_conditions=c.boundary_conditions,
        assumptions=c.assumptions,
        limitations=c.known_limitations,
        additional_caveats=c.additional_caveats,
        evidence_flags=evidence_flags or [],
        ambiguous_boilerplate_candidates=ambiguous_candidates,
    )  # -> parsed JSON per §3.6 schema

    verdict["_grounded_missing_threats"] = filter_grounded_threats(verdict, method_excerpt)
    c.known_limitations = resolve_boilerplate(c.known_limitations, verdict.get("boilerplate_confirmations", []))

    sub = score_llm_verdicts(
        verdict, c.known_limitations, c.assumptions,
        caveat_flags_present=bool(evidence_flags),
    )

    # step 5a: worst-offender guard (absorbed from exp3, cycle 2 addition)
    raw_score = 0.50 * sub["assumption_realism"] + 0.35 * sub["limitation_novelty"] + 0.15 * sub["caveat_coverage"]
    raw_score = max(0.0, raw_score - sub["missing_threat_penalty"])
    if sub["worst_offender"]:
        raw_score = min(raw_score, 0.5)

    final = round(100 * floor * raw_score, 1)  # floor multiplies everything — never bypassed
    return {
        "score": final,
        "flags": floor_flags,
        "detail": {**sub, "missing_known_threats": verdict.get("_grounded_missing_threats", [])},
    }
```

The `floor` multiplier still encodes penalize-don't-skip structurally: a missing/empty Assumptions or
Known-limitations section drags the ceiling down (0.35 / 0.25) regardless of how the [sem] step scores
the little content that *is* present. The **worst-offender guard** (step 5a) adds a second, independent
penalize-don't-skip lever that the floor doesn't cover: it protects against a *populated but rotten*
section (many trivial-true assumptions diluting one flagrant dreamcase load-bearing one, or a
limitations bucket that's entirely boilerplate/restatement) — a case the availability floor, which only
looks at presence/thinness, cannot see.

### 3.9 Worked examples (che26, from the shape file — expanded per direction 5)

**Branch 1 — normal content trace (unchanged from cycle 1, re-verified against new weights).**
- Boundary conditions: 2 bullets (scope = blood p-tau isoforms; relative rankings not absolute AUC).
- Assumptions: A2 ("most comprehensive dataset per cohort ⇒ independence, no double-counting").
  Judge verdict: `load_bearing: yes`, `realism: unclear` (cohort overlap in AD biomarker studies is a
  known real risk — ADNI/AIBL-type cohorts are frequently re-used/merged across "different" datasets),
  `stress_tested: no` → assumption_score pulled down meaningfully; not a worst-offender case since
  `realism` is `unclear`, not `dreamcase`.
- Known limitations: "Batch effects" — judge verdict: `adds_new_condition: partial` (names a real,
  specific mechanism but doesn't say which platforms/cohorts are most exposed), `specific: yes` → decent
  but not maximal score. `boilerplate_verdict` for this bullet is `clear` (no stock-phrase overlap), so
  the two-band mechanism doesn't even engage here.
- Additional caveats: Table 1/caption mismatch is present as an evidence-layer flag. In cycle 1 this was
  reported only in `detail`; in cycle 2 it is scored. If constraints.md's "Additional caveats" section
  faithfully states the mismatch (as the real che26 artifact does), `caveat_coverage: "full"` → 1.0,
  contributing its full 0.15 weight rather than sitting outside the formula.

**Branch 2 — availability-floor case (new).** Hypothetical abstract-only-source artifact: `constraints.md`
present but `assumptions: []`, `known_limitations: []`. `availability_floor` returns
`floor = 1.0 * 0.35 * 0.25 = 0.0875`. Even if the (vacuous) LLM call somehow returned a generous verdict
on the empty lists, `raw_score` computed from empty verdict lists defaults `assumption_score` and
`limitation_score` to `0.0` per the `if verdict["assumptions"] else 0.0` guard, so `raw_score = 0.0`
regardless — the floor and the zero-content default reinforce each other, and the final score is `0.0`,
not a skipped/null result. This demonstrates penalize-don't-skip end-to-end on the degenerate input the
shape file calls "a stark, easily-detected floor case."

**Branch 3 — missing-known-threats case (new).** che26 is a diagnostic-accuracy-style biomarker synthesis
across cohorts. Suppose the method excerpt (from `study_design.md`) contains the sentence: *"studies
were included regardless of whether p-tau assays were interpreted with knowledge of clinical diagnosis
status."* Neither Assumptions nor Known limitations in che26's `constraints.md` mentions blinding of
assay interpretation. The judge would be expected to return:
```json
{"threat": "verification/spectrum bias from unblinded assay interpretation",
 "design_choice_quote": "studies were included regardless of whether p-tau assays were interpreted with knowledge of clinical diagnosis status"}
```
`filter_grounded_threats` checks this quote against the excerpt with `fuzz.partial_ratio >= 90` — it
matches verbatim, so the threat is kept and contributes `0.1` to `missing_threat_penalty`. If the judge
had instead returned a generic, unquotable "publication bias may be present" with no matching excerpt
text, `filter_grounded_threats` would silently drop it — neither penalizing nor crediting the artifact
for a threat the judge couldn't actually ground, which is the intended failure-closed behavior.

## 4. Why this is hard to Goodhart

- **The core judgment (realism, novelty) is not lexical.** Padding bullets with plausible-sounding nouns
  doesn't help once the deterministic boilerplate/redundancy backstops cap the LLM's generosity for
  clear-band matches, and the ambiguous band is resolved by the same judge that already has full context
  — not by a second, gameable string threshold.
- **Load-bearing weighting means gaming the wrong assumptions is a losing move.** Inflating the
  assumption list with trivially-true, non-load-bearing statements gets `weight = 0.5` instead of `1.5`
  and can't rescue a low score on the one assumption that actually matters — and cycle 2 additionally
  ensures it can't be diluted into an acceptable average at all, via the worst-offender guard.
- **The missing-known-threats check is adversarial by construction, and now non-fabricable.** It asks the
  judge to name field-standard failure modes the artifact *doesn't* mention — something a compiler/author
  cannot pre-empt by wordsmithing bullets that ARE present — and cycle 2's grounding requirement means
  the judge itself cannot inflate this signal with genre-stereotype invention; every credited threat must
  trace to an actual sentence in the artifact's own method excerpt.
- **Two independent deterministic backstops (boilerplate-library fuzzy match, cross-bucket prior-text
  similarity) bound the LLM's ceiling for high-confidence matches**, while the ambiguous band is resolved
  with context rather than a brittle single threshold — removing the cycle-1 failure mode where a real,
  specific limitation sharing stock nouns got wrongly capped, without reopening the boilerplate-mimicry
  route (a truly vacuous bullet still gets confirmed as boilerplate by the same judge that would have
  scored `adds_new_condition: no` anyway).
- **The floor multiplier is structural, not a suggestion to the judge** — no LLM verdict can push a
  thin/absent constraints.md back above its availability ceiling, closing the "just say something vague
  but confident" loophole.
- **The worst-offender guard closes the residual dilution route** that the floor (presence-only) and
  load-bearing weighting (averaging-only) each leave partially open: a populated, plausible-looking
  artifact with exactly one flagrant load-bearing dreamcase assumption, or an entirely-boilerplate
  limitations bucket, cannot average its way past a 0.5 cap.
- **The caveat-coverage term makes silent compiler under-extraction directly costly**, not just visible
  in an audit log — closing the gap the cycle-1 critique named explicitly ("doesn't feed the numeric
  formula directly").

## 5. Composition with the rest of the suite

This metric remains **orthogonal by subtraction**, not addition: round-1 07's concreteness check and
verifier D3's explicitness check both look at the *form* of the constraints section (is it there, is it
specific-sounding); M30 is explicitly told to skip re-scoring those axes and instead scores *truth-value
plausibility* and *incremental information content* — properties invisible to a presence/specificity
checker. Cycle 2 sharpens this further: the cross-bucket dedup and caveat-coverage term mean M30 now also
implicitly checks a form of *cross-section consistency* (does the file say the same thing three times
dressed differently; does it surface what the evidence layer already flagged) that neither 07 nor D3
attempts, without duplicating either's core signal. A paper cannot satisfy all checks by optimizing on
any single axis — writing longer, more specific-sounding, boilerplate-avoiding bullets improves 07/D3 but
only improves M30 if the added specificity also constitutes a genuinely new, realistic, load-bearing,
non-restated claim, and now additionally only helps caveat coverage if it's *accurate* relative to what
the evidence layer independently shows.
