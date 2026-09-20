# Stage 1 critique — `10_implementation`

## One-line verdicts + rank

- **Agent 4 — RANK 1.** The only proposal with a genuine structural anti-gaming device (the sensitivity-label *variance discount* in `config_calibration`) plus a three-tier environment-honesty encoding and a unique `claim_traceability` metric; best coverage of the shape's own distinctions with the least reliance on raw length.
- **Agent 2 — RANK 2.** `capture_to_claim_gap` is the single best idea in the pool — a *quantitative* ratio of enumerated pipeline stages claimed vs. files captured — and it interlocks tightly with grounding-consistency to punish both directions of capture-cheating.
- **Agent 3 — RANK 3.** `honest_absence_score` (metric 2) is the cleanest treatment of the central FAIL condition, but the set spends two of five slots on overlapping grounding/reconstruction checks and one whole slot on surface version-regex.
- **Agent 1 — RANK 4.** Solid and well-reasoned, but softest on the hard constraint (too many 0.4/0.5/0.6 neutral "nothing to check" bands) and its environment metric is essentially version-regex surface.

## WINNERS: agent2, agent4

---

## Per-winner critique + stage-2 directions

### Agent 4 (Rank 1)

**What genuinely measures science.** `capture_proportionality` scores the silent-drop FAIL by *regime* (0.05 undisclosed-absence vs 0.9 disclosed scope decision vs 0.7 genre-justified che26-style absence) — this maps the shape doc's failure taxonomy almost one-to-one. `environment_concreteness` is the best environment treatment in the pool because it encodes the shape's own key distinction as three tiers: silent blank (0.0, worst) < honest "not specified in paper" (0.4) < concrete detail (0.6–1.0). That ordering — punishing the missing field *harder* than the honestly-declared gap — is exactly the epistemic signal the artifact cares about. `config_calibration`'s variance discount (if ≥3 params all share one sensitivity label, multiply by 0.6) is the only real Goodhart trap any proposer built, catching "decorative sensitivity fields." `claim_traceability` is a distinctive fifth dimension no other proposal covers.

**Where it's weak / stage-2 directions.**
1. **`NAMED_TOOL_RE = [A-Z][A-Za-z0-9_]{2,}` is pure surface** — any capitalized word (even "The", "Not") scores the +0.2 "named tool" bonus. This is the exact verbosity-proxy the brief says loses. Replace with a check that the token co-occurs with a version, a known-tool lexicon, or cross-references a dependency actually cited in `execution/` imports.
2. **Free-pass fallbacks.** `grounding_integrity` returns 0.6 for *any* `code_availability` longer than 20 chars when `execution` is empty — a 21-character boilerplate sentence earns 0.6. Tie this fallback to the *specificity* of the absence justification (named registries searched, "duplicates prose method" reasoning), not its length. Same fix for `config_calibration`'s `len(deps) > 20` band.
3. **`claim_traceability` fabrication gap.** You concede invented `C04, C07` ids can't be checked. Strengthen by cross-referencing claim ids against the actual claim inventory the ARA emits elsewhere, or at minimum flag `claims_supported` ids that appear in *no* other layer as unverifiable.
4. **Generalize the variance discount.** It's your best device — apply the same uniformity penalty to `claim_traceability` (all blocks lazily marked "all") as you already hint, and consider it for grounding tags.

### Agent 2 (Rank 2)

**What genuinely measures science.** `capture_to_claim_gap` turns the "pointer instead of copy" FAIL from a qualitative judgment into a number: count enumerated stages (`\d{2}_\w+` like `01_spaceranger`), inline code-file refs, and declared paths in `artifacts.md`, then divide captured `execution/` files by that claim. A 15-stage pipeline described but zero files captured scores near zero. This is the most direct operationalization of silent under-capture in the whole tournament, and it interlocks correctly with `grounding_consistency_score` (metric 1): you can't cheat by claiming rich code that isn't there (metric 5 catches it) *or* by hiding real code behind vague prose (metric 1's shape check catches it). `grounding_consistency_score` also correctly returns 0.0 on empty `execution` rather than N/A — the strictest, most hard-constraint-compliant grounding metric of the four.

**Where it's weak / stage-2 directions.**
1. **`capture_to_claim_gap` has two free-pass exits.** When `claimed_units == 0` it returns 0.7 (no capture) or 1.0 (any capture), and the no-blocks-no-exec case returns 0.4. A compiler that writes *vague* `artifacts.md` prose (no enumerable `\d{2}_` tokens) lowers its own denominator to zero and escapes into the 0.7/1.0 band — the opposite of what you want. Fix: when a repo is *mentioned* but yields zero enumerable units, treat that as a vagueness penalty, not a free pass; borrow agent 4's regime logic.
2. **Brittle enumeration.** The `\d{2}_\w+` heuristic is entirely dependent on the compiler's prose formatting; a pipeline described as "fourteen stages from project-prep through MOFA" scores zero claimed units. Add textual number-word and count-noun detection, and count `file_paths` more robustly.
3. **Length-based disclosure.** `disclosed_scope_honesty` leans on `len(code_avail) > 60`. Same critique as agent 4: require specific tokens ("not cloned", named registry, size justification), not character count — you already have the keyword check, so drop the length OR gate that lets pure length win.
4. **Minor compute smell.** `b.get("file_paths", []).__str__()` works but is fragile; join the list explicitly. Verify the metric-1 `looks_full_bodied` line-count threshold (15) against the shape doc's ~30-line "substance" bar.

---

## Why each loser lost

**Agent 3 (Rank 3).** `honest_absence_score` is genuinely excellent — arguably the single cleanest silent-coverage-failure check in the pool, cross-referencing `artifacts.md` repo signals against `execution/` capture with a disclosure regex, and it even penalizes suspiciously-thin capture (`total_lines < 20`). But the set is redundant: `grounding_citation_fidelity` (metric 1) and `reconstructed_stub_discipline` (metric 4) are both about grounding/reconstruction honesty and largely re-measure the same terrain, wasting a slot. Worse, `version_pinning_specificity` (metric 3) devotes an entire metric to regex-matching version numbers — the brief explicitly warns that surface features lose, and its own fabrication defense punts ("checkable by a human auditor"). Two soft spots (metric 4 returns a flat 0.5 when no reconstructed files exist) plus that redundancy edge it below agent 2, whose fifth metric adds a *distinct* quantitative dimension rather than a second grounding check.

**Agent 1 (Rank 4).** The most thorough combination essay and a nuanced `reconstruction_fidelity` metric (NotImplementedError-to-def ratio for reconstructed, imports + lines-per-def for transcribed — genuinely good). But it is the softest on the hard constraint: `parameter_rigor_density` returns 0.4 for "plausibly non-parametric" work, `repo_capture_honesty` returns 0.5/0.6 neutral bands for "nothing to check," and the empty-config path hands out a moderate default — each a partial skip the brief tells us to dock. And `environment_specificity_score` (metric 5) is fundamentally the same version-regex-plus-length surface signal that sinks agent 3's metric 3, just field-weighted. Strong reasoning, but more free-pass leakage and more surface reliance than the two winners.
