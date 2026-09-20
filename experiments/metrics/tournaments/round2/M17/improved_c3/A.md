## Changes (cycle 3)

This is the final repair pass on exp1 → cycle-2's Rank-1 lineage. Cycle 2 fixed the arithmetic bug
and the schema mismatch the judge flagged; the cycle-2 critique (`critique_c2.md`) confirmed all
four cycle-1 directions were done well, then gave four cycle-3 directions, all addressed below. As
in cycle 2, this is surgical: it touches only what was flagged, and leaves every crown jewel —
dual-index search, the self-disclosure asymmetry, the fixed weighted unit set, structural-only
impact, the availability multiplier — untouched.

1. **Hardened the gap→claim edge against tag-stuffing, and retracted the "no new gaming surface"
   claim.** Cycle 2 asserted the controlled-vocab-overlap edge introduced no new gaming surface;
   the critique correctly showed that was false — an author can tag-stuff otherwise-unrelated
   claims with gap vocabulary to inflate `n_dependent_claims`, and the transitive closure amplifies
   a single stuffed tag into an entire downstream subgraph. Cycle 3 applies three independent
   defenses instead of one (§6.3b, §6.3c): (a) the direct-link match now requires the term to
   appear in the claim's `Statement`, not its `Tags` — `Tags` is dropped from the match entirely;
   (b) the transitive closure is now depth-capped; (c) impact is dampened in proportion to what
   fraction of the dependent-claim set is *not* `Status: supported`, so a stuffed but unverified
   subgraph earns much less than a real one even if it survives (a) and (b). The failure-modes
   analysis for this edge is now explicit, not asserted away.
2. **Retightened the `searched_empty` → novelty ceiling.** Cycle 2's `conf=0.6` /
   `UNKNOWN_INDEX_RISK_PRIOR=0.5` gave a clean-but-empty dual-index search 0.80 novelty, only 0.20
   below a confirmed-clean judged search (1.00) — too close, per the critique, to fully close the
   strategic-obscurity route (pick jargon so obscure both indexes return nothing). Cycle 3 lowers
   `conf` to `0.5` **and** raises the uninformative prior to `0.65` (§6.2b): both changes compound
   in the same direction (less confidence in "clean empty" as evidence, and a prior skewed toward
   prior-art risk rather than a true coin flip when there's no real signal either way). The new
   ceiling is `0.675` novelty — a 32.5-point gap instead of 20, and close to parity with B's
   independently-derived `~0.675` ceiling for an equivalent strong target (`0.5·raw + 0.175` at
   `raw=1`), confirming this isn't an arbitrary tightening but converges with the sibling design's
   independently-reasoned number.
3. **Separated harness/API failure from artifact non-novelty, with an explicit stated policy.** The
   critique named a real, unresolved tension: forcing every `retrieval_failed` unit to worst-case
   novelty makes the score hostage to infra flakiness and non-reproducible across runs. Cycle 3
   resolves this with a two-tier policy (§6.2c), stated explicitly rather than left implicit:
   escalate retries first (1→3 attempts, exponential backoff) so an isolated network blip rarely
   reaches "failed" at all; a unit that still fails after escalation is scored worst-case as before
   (penalize-don't-skip — a single stubborn failure among many units must not exempt the run from
   scoring); but if **half or more** of an artifact's searchable units end up `retrieval_failed`
   after escalated retries, the run hard-fails to a distinct `uncomputable_retry_required` status
   instead of emitting a numeric score — at that scale, "the retrieval backend is down" is a far
   better explanation than "half this paper's claims independently hit dead indexes," and a
   confident-looking number would be actively misleading. Any run with partial failure below that
   threshold now also carries a visible `harness_reliability: "degraded"` flag naming the affected
   units, so run-to-run variance from infra is surfaced, not hidden.
4. **Unchanged, by design**: the dual-index requirement (§6.2a), the fixed artifact-driven unit set
   (KI/Gaps/anchor-claim/method) and its weights, the self-disclosure asymmetry (0.05 disclosed vs
   0.30 undisclosed, §6.4 of exp1/cycle-2), the structural-only impact rubric (Prompt B, fed only
   structural facts, never prose), the `Status`-based anchor-claim impact dampening, the
   availability multiplier (§6.5), and the `judge_all_candidates` single-pass caching (§6.3a of
   cycle 2). None of these were flagged in cycle 3 and none are touched below except where a section
   explicitly says its *inputs* changed (e.g. Prompt B now also receives the supported-fraction
   figure from §6.3c).

---

## Repaired sections (supersede the corresponding sections of cycle 2, and by extension exp1)

### §6.2a — External retrieval contract, retries escalated

Unchanged except the retry policy, which is now shared infrastructure for §6.2c's escalate-before-
declaring-failure rule:

```python
def call_semantic_scholar(query_terms: list[str], retries: int = 3, timeout_s: float = 8.0) -> RetrievalResult:
    """[sem] call. Same endpoint/params/mapping as cycle 2 §6.2a. Retry policy widened from 1 to 3
    attempts with exponential backoff (2s, 4s, 8s) before the call is declared a failure — see
    §6.2c for why: a single-retry failure was too cheap a bar for declaring 'we could not
    determine this,' and the cycle-3 escalate-then-flag policy depends on 'failed' meaning
    'persistently failed across a real backoff window,' not 'timed out once.'
    On exhaustion: RetrievalResult(outcome="failure", hits=[]), unchanged from cycle 2.
    """
    ...  # real HTTP call with the widened retry/backoff/failure-tagging behavior described above


def call_undermind(unit_text: str, retries: int = 3, timeout_s: float = 15.0) -> RetrievalResult:
    """[sem] call. Same endpoint/body/mapping as cycle 2 §6.2a. Retry policy widened to match
    call_semantic_scholar (3 attempts, 2s/4s/8s backoff) for the same reason."""
    ...  # real HTTP call
```

Everything else in §6.2a (endpoints, request/response shapes, `dedup_candidates`, the operational
definition of "strong overlap") is unchanged from cycle 2 — none of it was flagged.

### §6.2b — Retrieval confidence regimes, retightened `searched_empty` ceiling

`retrieval_level()` is unchanged from cycle 2. Only the two constants that determine the
`searched_empty` blend move, and only in the direction of more skepticism:

```python
UNKNOWN_INDEX_RISK_PRIOR = 0.65
# Cycle 2 used 0.5 (a true coin-flip prior). Cycle 3 raises this to 0.65: when both indexes come
# back empty, there is genuinely no positive evidence of prior art, but there is also no positive
# evidence the search was thorough enough to rule it out (index coverage gaps, embedding recall
# limits, non-indexed venues). A prior skewed toward prior-art risk — rather than a neutral
# coin-flip — better reflects "absence of a hit is weak, not neutral, evidence" and directly
# narrows the strategic-obscurity route the critique flagged.

EMPTY_SEARCH_CONFIDENCE = 0.5
# Cycle 2 used conf=0.6 (fixed inline). Cycle 3 lowers it to 0.5 and names it as a constant: a
# clean-but-empty dual-index result is even less conclusive than cycle 2 credited it as, so it
# should pull LESS of the blend toward "confirmed clean" (strength=0.0) and MORE toward the
# (now-higher) risk prior. The two changes compound rather than substitute for each other.


def unit_effective_strength(level: RetrievalLevel, judged: list[tuple[dict, float, dict]],
                             disclosure_penalty: float) -> float:
    """judged = output of judge_all_candidates() (§6.3a of cycle 2); only non-empty when
    level == 'searched_with_hits'. disclosure_penalty comes from §6.4 of cycle 2, unchanged."""
    if level in ("unsearchable", "retrieval_failed"):
        # No reliable signal in either direction. Per penalize-don't-skip (§7), absence of a
        # verdict is never scored as favorable; both cases collapse to worst-case prior-art risk.
        # (retrieval_failed's RUN-LEVEL handling — escalate, then hard-fail if systemic — is a
        # separate, additional check layered on top; see §6.2c. This per-unit worst-case default
        # is unchanged and still applies to isolated failures.)
        return 1.0
    if level == "searched_empty":
        conf = EMPTY_SEARCH_CONFIDENCE          # 0.5, was 0.6
        strength = 0.0                          # no candidates exist to judge
        blended = conf * strength + (1 - conf) * UNKNOWN_INDEX_RISK_PRIOR   # 0.5*0 + 0.5*0.65 = 0.325
        return min(1.0, blended + disclosure_penalty)   # disclosure_penalty is always 0.0 here
    # searched_with_hits: full confidence in whatever the judge concluded
    strength = max((s for _, s, _ in judged), default=0.0)
    return min(1.0, strength + disclosure_penalty)
```

**Unit test table, updated (replaces cycle 2's table):**

| Regime | Setup | `level` | Computation | `effective_strength` | `novelty` contribution |
|---|---|---|---|---|---|
| Unsearchable | query has <2 concept/tag terms; search never runs | `unsearchable` | forced worst case | `1.0` | `0.0` |
| Retrieval failed (isolated) | S2 or Undermind still fails after 3 retries w/ backoff | `retrieval_failed` | forced worst case (per-unit) | `1.0` | `0.0` |
| Searched, empty | both indexes queried successfully, 0 hits total | `searched_empty` | `0.5·0 + 0.5·0.65 = 0.325` | `0.325` | `0.675` (capped, provisional — **down from 0.80 in cycle 2**) |
| Searched, hits, all `none` | candidates returned, judge says no technical-core overlap | `searched_with_hits` | `max(strengths)=0.0` | `0.00` | `1.00` (only regime with real positive evidence, so the only one earning full novelty) |
| Searched, hits, one `substantial`, disclosed | as above but one hit judged 0.7, cited in `related_work.md` | `searched_with_hits` | `0.7 + 0.05 = 0.75` | `0.75` | `0.25` |
| Searched, hits, one `substantial`, undisclosed | same hit, absent from `related_work.md` | `searched_with_hits` | `0.7 + 0.30 = 1.00` | `1.00` | `0.00` |

The ordering property cycle 1 and cycle 2 established still holds — `searched_empty` strictly below
`searched_with_hits`+`none`, both strictly above `unsearchable`/`retrieval_failed` — but the gap
between "clean empty search" and "confirmed clean search" is now `0.325` of novelty (32.5 points)
instead of cycle 2's `0.20` (20 points), meaningfully tightening the strategic-obscurity route: an
author who picks ultra-specific jargon so both indexes return nothing now banks `0.675` novelty, not
`0.80`.

### §6.2c — Harness-failure isolation policy (new)

This directly answers cycle-3 direction #3 and states the policy explicitly rather than leaving the
tension implicit, as the critique asked.

**The tension, named precisely:** a single API timeout should not be allowed to (a) silently crush
one unit's novelty to zero the same way as if it were an unsearchable/vague claim, in a way that
makes two runs of the *same, unchanged* artifact score differently depending on network conditions
at scoring time; but it also must not (b) be allowed to become a skip/N/A route, or to blend toward
a lenient default, since that would reopen exactly the "obscure domain evades scoring" gaming route
penalize-don't-skip exists to close.

**The resolution — escalate, then penalize-in-place for isolated failures, hard-fail for systemic
ones:**

1. **Escalate before declaring failure.** §6.2a's retry count moved from 1 to 3 attempts with
   exponential backoff (2s/4s/8s). This alone eliminates most transient blips from ever reaching
   `retrieval_failed` in the first place, which is the cheapest and most direct fix for
   reproducibility — most of the non-reproducibility the critique worried about was a symptom of a
   too-thin retry budget, not an inherent property of treating failure as worst-case.
2. **A unit that still fails after escalation is scored worst-case, unchanged from cycle 2
   (`effective_strength = 1.0`).** This is a deliberate choice to keep penalize-don't-skip's
   strongest form at the *unit* level: if only one or two units out of an artifact's four-to-six
   fail, the honest, correct interpretation is "we still don't have a verdict for this specific
   claim," which is exactly the case §7's rule is built to never reward. Excusing an isolated
   failure would hand back the same skip route the direction warns against, just relocated from
   "vague query" to "unlucky timing."
3. **A NEW run-level circuit breaker separates "this run is unreliable" from "this artifact is not
   novel."** After all units are retrieved, before computing the final composite:

```python
def harness_reliability_check(per_unit_levels: list[RetrievalLevel]) -> dict:
    """Run once, after all units have been retrieved (§6.6), before final scoring.
    per_unit_levels excludes 'unsearchable' units — those are a genuine artifact-quality signal
    (vague query), not a harness signal, and must not count toward or against reliability."""
    searchable_levels = [lvl for lvl in per_unit_levels if lvl != "unsearchable"]
    if not searchable_levels:
        return {"status": "ok", "failed_fraction": 0.0}
    n_failed = sum(1 for lvl in searchable_levels if lvl == "retrieval_failed")
    failed_fraction = n_failed / len(searchable_levels)
    if failed_fraction >= 0.5:
        # Half or more of the units this artifact could in principle be searched for came back
        # with no reliable answer even after escalated retries. At this scale, "the retrieval
        # backend is degraded right now" is a materially better explanation than "half this
        # paper's independent claims all coincidentally hit index blind spots" — reporting a
        # confident numeric score at this point would look rigorous while being misleading.
        return {"status": "uncomputable_retry_required", "failed_fraction": failed_fraction}
    if failed_fraction > 0.0:
        return {"status": "degraded", "failed_fraction": failed_fraction}
    return {"status": "ok", "failed_fraction": 0.0}
```

4. **The chosen threshold (`0.5`) and its consequence are explicit, not buried:**
   - `failed_fraction < 0.5` → run proceeds to a normal numeric score, exactly as in cycle 2 (each
     failed unit still scores worst-case per point 2 above), but the top-level result additionally
     carries `"harness_reliability": "degraded"` and lists the specific failed `unit_ids` (§6.6).
     A downstream aggregator or human reviewer can now discount or re-run scores flagged this way
     instead of treating them as unconditionally trustworthy — the run-to-run variance the critique
     raised is now visible metadata, not a silent property of the number.
   - `failed_fraction >= 0.5` → the run does **not** produce `score`. It returns
     `{"score": None, "status": "uncomputable_retry_required", "failed_fraction": ..., "per_unit": [...]}`
     — a hard signal for automatic retry or human escalation. This is the one place in the whole
     M17 design where a numeric score is deliberately withheld; it is not a skip of the metric (the
     artifact is not scored as N/A or averaged into the suite silently) — it is a distinct,
     loudly-surfaced non-score that a caller must handle explicitly, which is a stronger guarantee
     against silent skipping than emitting *any* number would be.

This is the two-tier policy the critique asked cycle 3 to state explicitly: **escalate to reduce
false failures, penalize-in-place for the failures that remain (because isolated failures are still
informative-enough to score, per §7), and hard-fail-and-flag only when the failure pattern itself
becomes the dominant signal** — at which point pretending to measure novelty would be measuring the
retrieval backend's uptime instead.

### §6.3b — `n_dependent_claims`, hardened against tag-stuffing (supersedes cycle-2 §6.3b)

Cycle 2 claimed the controlled-vocab-overlap edge introduced "no new gaming surface." **That claim
is retracted.** The critique is correct: an author can add gap-vocabulary terms to a claim's `Tags`
without touching its actual argument, and the transitive reverse-closure then drags in everything
downstream of that one stuffed claim — a cheap, structural lever the metric is supposed to resist,
not one it should have asserted away.

Three independent, layered defenses, none of which is individually sufficient but which compound:

**Defense 1 — direct match must hit the claim's `Statement`, not its `Tags`.** `Tags` is dropped
from the direct-link check entirely. `Statement` is the field the ARA's own internal
claims-grounding verifier separately checks for coherence with the claim's evidence base — inflating
`n_dependent_claims` by rewriting a claim's actual asserted content to reference gap vocabulary is a
far more expensive and more independently-detectable move than editing a free-text `Tags` list, and
it now risks tripping an unrelated verifier check in the process.

**Defense 2 — the transitive closure is depth-capped.** One matched claim can no longer drag in an
unbounded downstream subgraph; at most two hops of reverse-dependency are inherited.

**Defense 3 — impact is dampened by the unsupported fraction of the dependent set** (§6.3c) — even a
stuffing attempt that survives Defenses 1 and 2 only pays off if the claims it captured are *also*
independently verified as `Status: supported`, which an author cannot fabricate without separately
passing whatever check assigns that status.

```python
MAX_CLOSURE_DEPTH = 2
# Bounds how many reverse-dependency hops a single directly-linked claim can propagate through.
# Without this cap, one Statement match at the root of a long dependency chain could pull in every
# claim built on top of it, turning one legitimate (or one narrowly-stuffed) match into an
# arbitrarily large count.


def gap_dependent_claim_ids(gap_statement: str, claims: list[dict],
                             concept_vocab: set[str]) -> tuple[set[str], set[str]]:
    """Step 1 — direct link: a claim is directly linked to a Gap if the Gap's own controlled-
    vocabulary query terms (via the same `build_terms` lookup extract_novelty_units already uses)
    appear in that claim's STATEMENT. Tags are no longer matched here (cycle-2 defense removed —
    see rationale above; Tags-only overlap was the tag-stuffing lever).

    Step 2 — transitive closure over the real Dependencies graph, capped at MAX_CLOSURE_DEPTH hops.

    Returns (all_dependent_claim_ids, supported_dependent_claim_ids) — the second set feeds the
    impact dampening in §6.3c.
    """
    gap_terms = set(build_terms(gap_statement))
    if not gap_terms:
        return set(), set()

    direct = {
        c["id"] for c in claims
        if any(t in c.get("statement", "").lower() for t in gap_terms)
    }

    downstream_of: dict[str, set[str]] = {c["id"]: set() for c in claims}
    for c in claims:
        for dep in c.get("dependencies") or []:
            if dep in downstream_of:
                downstream_of[dep].add(c["id"])

    closure = set(direct)
    frontier = [(cid, 0) for cid in direct]
    while frontier:
        cid, depth = frontier.pop()
        if depth >= MAX_CLOSURE_DEPTH:
            continue
        for nxt in downstream_of.get(cid, ()):
            if nxt not in closure:
                closure.add(nxt)
                frontier.append((nxt, depth + 1))

    status_by_id = {c["id"]: c.get("status") for c in claims}
    supported = {cid for cid in closure if status_by_id.get(cid) == "supported"}
    return closure, supported


def compute_n_dependent_claims(units: list["NoveltyUnit"], claims: list[dict],
                                concept_vocab: set[str]) -> tuple[int, int]:
    """Union across all Gap units, unchanged from cycle 2 (a claim depending on two gaps still
    counts once). Now also returns the supported-subset count for §6.3c's dampening."""
    dependent: set[str] = set()
    supported: set[str] = set()
    for u in units:
        if u.unit_type == "gap":
            d, s = gap_dependent_claim_ids(u.text, claims, concept_vocab)
            dependent |= d
            supported |= s
    return len(dependent), len(supported)
```

**Failure-modes note (replaces cycle 2's incorrect "no new gaming surface" claim):** this edge
remains a real, non-zero gaming surface — a determined author can still write a Statement that
superficially reuses gap vocabulary in an otherwise-unrelated claim. Defenses 1–2 raise the cost and
cap the blast radius of doing so; Defense 3 (§6.3c) removes most of the payoff by requiring the
stuffed claims to *also* be independently supported. No single layer is claimed to be sufficient on
its own, which is the honest version of the claim cycle 2 got wrong.

### §6.3c — Impact dampened by dependent-claim support fraction (new)

Prompt B (unchanged wording from exp1 §6.3) now also receives the supported-subset count, and the
resulting impact score is dampened by the fraction of the dependent-claim set that is *not*
`supported`:

```python
def judge_impact_with_support(problem: dict, n_dependent_claims: int, n_dependent_supported: int,
                               n_trials: int, llm_call) -> float:
    """Prompt B's STRUCTURAL FACTS block gains one line versus exp1/cycle-2:
    '- Of those {n_dependent_claims} claims, {n_dependent_supported} carry Status=supported
       (the remainder are hypothesis/refuted).'
    This is still a structural fact, not prose — it costs nothing new to compute (already produced
    by §6.3b) and lets the judge see whether a large dependent-claim count is backed by verified
    argument or not, which the 1-5 rubric itself is free to weight. The multiplicative dampening
    below is a SEPARATE, deterministic floor on top of the judge's own score — belt and suspenders,
    since the judge call has sampling variance and shouldn't be the only thing standing between a
    stuffed-but-unverified claim set and a high impact score."""
    raw_impact = judge_impact(problem, n_dependent_claims, n_trials, llm_call)  # exp1 §6.3, unchanged
    if n_dependent_claims == 0:
        return raw_impact
    unsupported_fraction = 1.0 - (n_dependent_supported / n_dependent_claims)
    # Caps the deterministic dampening at 50%: even an entirely-unsupported dependent set still
    # reflects SOME real structural claim about the artifact's shape (the claims do exist and do
    # cite the gap), so this is a discount, not a zeroing-out — full zeroing is left to the judge's
    # own 1-5 reasoning if it independently finds the set unconvincing.
    return raw_impact * (1.0 - 0.5 * unsupported_fraction)
```

Worked check against the tag-stuffing route: an author who stuffs 5 unrelated claims' `Statement`s
with gap vocabulary but whose actual `Status` remains `hypothesis` (stuffing text alone doesn't
change verification outcomes) gets `n_dependent_claims=5`, `n_dependent_supported=0`,
`unsupported_fraction=1.0`, and a 50% multiplicative impact cut — on top of the higher cost and
detectability risk from Defense 1, and independent of Prompt B's own judgment, which is also fed the
same supported/total figures and free to discount further.

### §6.6 — Final composite, reassembled with all cycle-3 repairs

```python
def score_M17(problem: dict, claims: list[dict], concepts: list[dict],
              related_work: dict, solution: dict, llm_call, is_clinical_domain: bool) -> dict:
    concept_vocab = {c["term"].lower() for c in concepts}
    units = extract_novelty_units(problem, claims, concepts, solution)

    per_unit = []
    for u in units:
        if not u.searchable:
            level, judged, penalty = "unsearchable", [], 0.0
        else:
            ss = call_semantic_scholar(u.query_terms)   # retries=3 default, §6.2a
            um = call_undermind(u.text)                 # retries=3 default, §6.2a
            level = retrieval_level(u.searchable, ss, um)
            if level == "searched_with_hits":
                candidates = dedup_candidates(ss.hits, um.hits)
                judged = judge_all_candidates(u, candidates, llm_call)   # cycle-2 §6.3a, unchanged
                strong = [c for c, s, _ in judged if s >= 0.7]
                penalty = undisclosed_prior_art_penalty(u.unit_id, strong, related_work["full"])
            else:
                judged, penalty = [], 0.0
        effective_strength = unit_effective_strength(level, judged, penalty)   # §6.2b, retightened
        per_unit.append((u, effective_strength, level))

    # NEW (§6.2c) — run-level harness reliability gate, checked BEFORE producing a numeric score.
    reliability = harness_reliability_check([level for _, _, level in per_unit])
    if reliability["status"] == "uncomputable_retry_required":
        return {
            "score": None,
            "status": "uncomputable_retry_required",
            "failed_fraction": round(reliability["failed_fraction"], 4),
            "per_unit": [(u.unit_id, u.unit_type, level, round(s, 4)) for u, s, level in per_unit],
        }

    weighted_prior_art = sum(u.weight * s for u, s, _ in per_unit) / sum(u.weight for u, _, _ in per_unit)
    novelty_score = 1.0 - weighted_prior_art

    # §6.3b (hardened) — now returns (total, supported) dependent-claim counts.
    n_dependent_claims, n_dependent_supported = compute_n_dependent_claims(units, claims, concept_vocab)
    n_trials = clinicaltrials_field_activity(
        [t for u in units for t in u.query_terms]) if is_clinical_domain else 0
    impact_score = judge_impact_with_support(   # §6.3c — status-dampened
        problem, n_dependent_claims, n_dependent_supported, n_trials, llm_call)

    # unchanged from exp1/cycle-2: impact is dampened if the claims meant to close the gap aren't
    # actually supported
    anchor_ids = [u.unit_id for u in units if u.unit_type == "anchor_claim"]
    supporting_statuses = [c["status"] for c in claims if c["id"] in anchor_ids]
    if supporting_statuses and all(s != "supported" for s in supporting_statuses):
        impact_score *= 0.5

    avail_mult = availability_multiplier(problem, related_work["full"], related_work["brief"])   # unchanged

    raw = 0.6 * novelty_score + 0.4 * impact_score
    final = avail_mult * raw

    result = {
        "score": round(final, 4),
        "novelty_score": round(novelty_score, 4),
        "impact_score": round(impact_score, 4),
        "availability_multiplier": round(avail_mult, 4),
        "n_dependent_claims": n_dependent_claims,
        "n_dependent_claims_supported": n_dependent_supported,
        "per_unit": [(u.unit_id, u.unit_type, level, round(s, 4)) for u, s, level in per_unit],
    }
    if reliability["status"] == "degraded":
        result["harness_reliability"] = "degraded"
        result["failed_unit_ids"] = [u.unit_id for u, _, level in per_unit if level == "retrieval_failed"]
    return result
```

`per_unit` still reports each unit's retrieval `level` (cycle-2 addition, unchanged) so a reviewer
can distinguish `searched_with_hits` / `searched_empty` / `unsearchable` / `retrieval_failed`
directly in the audit output; the new `harness_reliability` / `failed_unit_ids` fields (only present
when at least one unit failed but the run stayed below the hard-fail threshold) make partial infra
degradation visible without withholding the score.

## §7 — Penalize-don't-skip summary, updated (cycle 3)

All bullets from exp1 §7 and cycle-2's addendum hold unchanged. Two are added:

- **Tag/Statement-stuffing a claim to inflate `n_dependent_claims`** → capped by three compounding
  defenses (§6.3b/§6.3c): the direct match now requires the Gap's terms to appear in the claim's
  `Statement` (not `Tags`), the transitive closure is depth-capped at 2 hops, and impact is
  multiplicatively dampened (up to 50%) by the fraction of the dependent set that is not
  `Status: supported`. A stuffing attempt that survives all three still cannot buy full impact
  credit without also being independently verified.
- **Systemic retrieval-backend failure (≥50% of an artifact's searchable units failing even after
  escalated retries)** → the run does not silently emit a low numeric score that would be
  indistinguishable from confirmed non-novelty; it returns a distinct `uncomputable_retry_required`
  status with no `score` field, forcing explicit retry/escalation rather than baking harness downtime
  into the artifact's record. Below that threshold, isolated per-unit failures are still scored
  worst-case exactly as before (never excused, never a skip route) but are now surfaced via a
  `harness_reliability: "degraded"` flag naming the affected units, so run-to-run variance from
  infrastructure is visible rather than silent.
