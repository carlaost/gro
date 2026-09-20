# M14 (Reference-landscape completeness) — critique, round 2 cycle 2

Middle cycle. No winner selected; both A and B advance to cycle 3. For each: did it
address the cycle-1 directions, what is still weak, and specific cycle-3 directions.

Mapping: **A** = the former exp2 lineage (Rank 1). **B** = the former exp1 lineage (Rank 2).

---

## A (former exp2, Rank 1)

### Did it address the cycle-1 directions?

All five directions were addressed, and mostly in the exact form requested:

1. **Conceptual-coverage hardening — addressed, but the guard is leaky.** `has_specific_anchor` +
   the 40%-of-covered-weight cap were both added and are wired into `coverage_score` correctly. This
   is the right shape. But the anchor *extractor* is too permissive and partially defeats the guard
   (see below). Direction addressed in structure, weak in execution.
2. **Define `importance` deterministically — fully addressed.** `compute_importance` implements the
   `0.5*relevance + 0.3*citation_percentile + 0.2*relation_boost_norm` formula I proposed, each term
   deterministically sourced, computed at landscape-construction time. This is clean and closes the
   cycle-1 hole exactly.
3. **Replace keyword-counted cross-layer with role-alignment + external resolution — addressed, but
   one sub-term is likely dead.** `role_alignment_score` now requires `Type`/`Delta`/`Claims affected`
   completeness, validates `Claims affected` against real `problem_ids`, and adds external resolution.
   Good. But `title_similarity` is Jaccard token overlap with a `>= 0.85` threshold — see below; that
   threshold is almost unreachable for real titles, so `external_grounding` (0.30 of the sub-score)
   may float near zero for legitimate ARAs.
4. **Gate contradiction default on `search_available` — fully addressed.** `0.65` only when search
   ran and returned candidates; `0.10` otherwise. Correct.
5. **Asymmetric high-importance miss penalty — fully addressed.** `high_importance_miss_penalty` is a
   first-class component at weight 0.12, borrowed from exp1's mechanism and scoped to
   canonical/contradictory/competing. Correct.

Net: A did the assigned work faithfully. The remaining problems are second-order — the new guards
introduce their own soft spots.

### What is still weak

- **`has_specific_anchor`'s extractor re-opens the very hole it closes.** The named-entity regex
  `\b[A-Z][a-zA-Z0-9]{2,}(?:-[A-Za-z0-9]+)?\b` matches *any* capitalized word ≥3 chars — "The",
  "Alzheimer", "Introduction", "Plasma", "Network". The numeric regex `\b\d{2,5}\b` matches every
  year and every incidental 2–5 digit number. So the anchor set an external abstract yields is
  polluted with dozens of common tokens, and the substring check `a.lower() in excerpt_lower` will
  trivially hit on "alzheimer" or "2023". A compiler that writes topically on-subject prose (exactly
  the vague-prose attack this guard exists to stop) will pass `has_specific_anchor` most of the time.
  The 40% cap still limits the *blast radius*, but the per-paper gate is much weaker than the prose
  describes. This is A's single most important cycle-3 fix.
- **`title_similarity` threshold is miscalibrated and the function is a placeholder.** Jaccard over
  raw whitespace tokens rarely exceeds ~0.5 even for a correct title match, because the union is
  inflated by stopwords and subtitle words. Requiring `>= 0.85` means `external_grounding` (0.30 of
  `role_alignment_score`) rewards almost nothing, penalizing honest `related_work.md` layers. The
  same `0.85` also gates `title_similarity` inside `role_alignment_score` while the docstring elsewhere
  says `>= 0.85 counts as a match` — the placeholder and the threshold were never reconciled.
- **`relation_type` is load-bearing but under-sourced for S2-only mode.** `importance` (via
  `relation_boost_norm`), `high_importance_miss_penalty` (pool = canonical/contradictory/competing),
  and `contradiction_score` all key off `relation_type`. Undermind supplies it explicitly, but when
  Undermind is unavailable (an explicitly supported mode), the doc never says how S2 candidates get a
  `relation_type`. If they default to `None`/`review`, the miss-penalty pool empties and the penalty
  silently returns `1.0` — the strong new component evaporates in exactly the degraded mode where it
  matters. Needs a deterministic S2-side relation classifier (citation-count → canonical, contradiction
  query provenance → contradictory, etc.).
- **`near_direct` (0.85) has no anchor requirement.** The conceptual guard is now strong-in-intent,
  but `near_direct` (same author/year + title-sim ≥ 0.90) earns near-full credit with no check that
  the ARA actually *uses* the paper — a stuffed `related_work.md` bibliography of correct
  author-year strings scores 0.85 each. Worth a lightweight use-check.

### Cycle-3 directions for A

1. **Fix the anchor extractor.** Exclude bare years (`19xx`/`20xx`) and require numeric anchors to
   carry a unit or decimal (`\d+(\.\d+)?%`, `n=\d+`, `\d+\.\d+`). For named-entity anchors, drop
   common-English and domain-stopword tokens, and prefer *distinctive* tokens: mixed
   alphanumerics (`p-tau217`, `GPT4`), multi-word proper strings, or capitalized tokens absent from a
   common-word list. The anchor should be something a vague paraphrase would *not* naturally contain.
2. **Replace `title_similarity` with a real normalized string similarity (token-set ratio or
   trigram) and recalibrate the threshold** to something reachable (~0.55–0.65 token-set), or switch
   to DOI/S2-ID resolution for `external_grounding` and reserve title-sim as a fallback. State the
   chosen function; do not ship the placeholder.
3. **Specify S2-only `relation_type` assignment** so `high_importance_miss_penalty` and
   `contradiction_score` do not silently collapse when Undermind is off. Guard against the
   empty-pool → `1.0` free pass: if the pool is empty *because relations were never classified* (vs.
   genuinely no high-stakes papers), that is a degraded run, not a clean one.
4. **Add a minimal use-requirement to `near_direct`** (the matched paper must appear in a
   role-bearing field, not just a bibliography line), mirroring the coverage/role-alignment
   philosophy already applied elsewhere.

---

## B (former exp1, Rank 2)

### Did it address the cycle-1 directions?

All four directions addressed:

1. **`trace_landscape` now touches the external landscape — addressed.** `trace_external_grounding`
   computes node↔candidate Jaccard, gates on `relation ∈ {baseline,bounds,refutes}`, and adds an
   `ungrounded_explicit` penalty class. This directly implements the direction and is B's strongest
   new piece conceptually.
2. **Genre-sensitive `contra_recall` default — addressed.** `0.75` when `api_ok` and `K` empty,
   `0.0` when search failed. Correct asymmetry.
3. **Capped, importance-ranked top-25 recall gold set + strengthened miss penalty — addressed.**
   `close_top` = top 25 by `importance`, and the `miss_penalty` still draws from the full pool and is
   now importance-weighted (`refutes`/`baseline` cost more). This is exactly the fix and preserves the
   proposal's best feature.
4. **Conceptual-coverage tier with specific-artifact guard + 35% cap — addressed in form, but nearly
   toothless in weight (see below).**

Net: B also did the assigned work faithfully and kept its dominant single external term intact
(external_coverage 0.35), which is the property the brief most wants preserved.

### What is still weak

- **The conceptual tier is almost cosmetic.** `conceptual_bonus` enters `external_coverage` at weight
  `0.05`, and `external_coverage` is `0.35` of the final score — so the entire conceptual tier can
  move the score by at most ~1.75%, and `soft_count(...)*0.5` caps it below that. All the machinery
  (artifact extraction, 35% cap, `direct_covered_weight` bookkeeping) exists to modulate a term that
  barely registers. Either the tier should carry enough weight to matter (and then the guard earns its
  keep) or the complexity should be trimmed. As written it satisfies the direction on paper without
  giving genuine uncited landscape awareness real credit — which was the *point* of the direction.
- **The artifact extractor is underspecified — same core risk as A, opposite failure.** B says
  candidate artifacts come from "the same extraction used for the ARA's own blocks," but that
  extractor is never defined, and `r.get("artifacts", [])` is assumed pre-populated on candidates
  without a step that populates it. Exact string/number intersection is *less* pollution-prone than
  A's substring match, but with no exclusion of years/generic numbers it can still false-match on
  "2023" or "AD". Needs the same disciplined extractor A needs.
- **`trace_external_grounding`'s 0.20 Jaccard threshold is loose and topic-overlap-prone.** Titles +
  abstracts of same-field papers share many 4-char tokens; 0.20 Jaccard can be reached by generic
  domain overlap rather than genuine correspondence to a specific abandoned approach. The added
  `relation ∈ {baseline,bounds,refutes}` gate helps, but the numeric threshold is the weak link — a
  confidently-written dead-end node about the right subfield may clear 0.20 without truly matching the
  externally-inferior approach. Risk of both false credit (gaming) and false penalty.
- **Search availability is triple-counted.** `api_ok` appears as its own `0.10` term inside
  `external_coverage`, again in `availability`, and again in `thin_penalty (+0.05)`. A failed search
  is penalized in three places; a clean search is rewarded in three places. This over-weights a single
  binary and distorts the intended component balance.
- **`has_ref_match` in trace grounding checks the ARA's own citation keys, not the external set.**
  `citation_key({"title_or_label": ref}) in ara_keys` confirms the trace ref is cited *in the ARA*,
  not that it resolves to an external landscape paper. That is a weaker, partly circular grounding
  path than the Jaccard route and does not deliver the "corresponds to externally-surfaced approach"
  guarantee the fix advertises.

### Cycle-3 directions for B

1. **Give the conceptual tier enough weight to be a real signal, or cut it.** If kept, lift it out of
   the `0.05` sub-slot so genuine uncited landscape awareness can move the score meaningfully (the
   35% cap already bounds the abuse). Otherwise remove the bookkeeping and state that B scores only
   formally-cited coverage — do not carry a guard-heavy term that cannot affect the outcome.
2. **Define the checkable-artifact extractor explicitly and add a populate step for candidate
   `artifacts`.** Exclude bare years and generic low-information numbers/acronyms; require distinctive
   tokens (units, decimals, mixed alphanumerics, named methods/datasets/cohorts). Share one extractor
   spec across ARA blocks and candidates.
3. **Tighten `trace_external_grounding`.** Raise the Jaccard floor and/or require an *entity/anchor*
   match (a named method/dataset/number shared between node text and the candidate), not just 4-char
   token overlap. Consider requiring the matched candidate to be the node's clear best match by margin,
   not merely above threshold.
4. **Collapse the triple-counted `api_ok`.** Keep search availability in one place (the availability
   term is the natural home), and let `contra_recall`/`trace_landscape` degrade via their own
   already-present `api_ok`-gated defaults rather than adding standalone reward/penalty terms for the
   same bit.
5. **Make `has_ref_match` resolve against the external candidate set** (DOI/title match into `L ∪ K`),
   not just the ARA's own citations, so the second grounding path delivers the external guarantee it
   claims.

---

## Shared cycle-3 theme (both A and B)

Both revisions correctly moved the metric's soft spot from "vague conceptual credit" and "keyword
stuffing" into a **new shared dependency: a deterministic artifact/anchor extractor**. A's is
over-permissive (substring match on polluted anchors); B's is under-defined and under-weighted.
Whichever survives, the cycle-3 win condition is a disciplined, specified extractor that (a) excludes
years and generic tokens, (b) demands distinctive alphanumeric/named anchors a vague paraphrase would
not contain, and (c) is used identically on the external side and the ARA side. Both should also
audit their **load-bearing `relation_type`/relation classifier** — it drives importance, contradiction,
and miss-penalty pools in both, yet neither fully specifies how it behaves (or degrades) when the LLM
or Undermind is unavailable.
