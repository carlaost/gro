# M48 — End-to-end reproducibility bundle — Judge critique, cycle 1

Metric: does figure + data + code co-exist **across layers** for actual end-to-end
replication? Primary artifact §9 evidence, crossing §10/§11. Judged on: genuine cross-layer
span (not single-file); concrete/runnable workflow; penalize-don't-skip with honest-disclosure
vs silent-gap vs fabrication distinguished (never N/A); Goodhart-resistance; edge over verifier
D6's looser "reproducibility is mentioned" check.

---

## Per-expander verdict + rank

### Rank 1 — exp1 (WINNER)
Anchors the metric at §9 and gives the single best justification in the field for *why* §9 is
the right primary artifact: the evidence layer is the only **object-indexed, enumerable** layer
("every Table N / Figure N" is a closed, checkable set), so "penalize missing any leg" becomes a
countable per-object operation rather than a whole-ARA impression. This maps the brief's scoping
(§9 primary, §10/§11 as dependencies) more faithfully than any other proposal.

- **Cross-layer, not single-file**: per-evidence-object triangulation — each table/figure must
  point at a *specific, named* dataset item and a *specific* code/config/toolchain item, matched
  semantically against the object's caption/claims, not just "some code exists somewhere." The
  §1.4 gaming table explicitly blocks "one dataset+pipeline credited to every object" via
  per-object semantic matching. This is genuine span.
- **Penalize-don't-skip**: strict `min()` weakest-link per object; unfiled/undisclosed source
  objects enter as zero-bundle entries (evidence-completeness itself becomes part of M48). No
  branch returns None/N/A — the paywalled/abstract-only floor is scored 0.0, not skipped.
- **Honest/silent/fabrication**: disclosure-quality tiers (specific-reasoned 0.3 > vague
  boilerplate 0.15 > silent 0.0); mislabeled `exact_from_labels` with `≈` markers zeroed toward
  0.3; genre-exemption gated on an *explicit quoted statement* + independent corroboration, never
  inferred from directory absence — closing the "we just didn't write a data section" loophole.
- **Goodhart / D6 edge**: claims-weighting stops diluting a headline result with padded minor
  figures; explicitly frames itself as "D6, but it has to actually be true, object by object, and
  graded not boolean." Strong.
- **Weaknesses**: the "evidence leg" is largely transcription-fidelity, which drifts toward
  single-layer quality that other metrics may own; pure `min()` is brittle (two very different
  ARAs with one near-zero leg score identically — the exact flaw exp3 fixes with a soft-min).

### Rank 2 — exp3 (WINNER)
The most complete and cleanest treatment of the brief's named honest/silent/fabrication axis, and
the most Goodhart-disciplined arithmetic.

- **Cross-layer, not single-file**: four legs FIG/DATA/CODE/**SCOPE**, with SCOPE (constraints.md)
  read directly from the one-liner's "(constraints, setup, comprehensive reporting)" — a defensible
  and well-argued expansion, not scope-creep. Cross-leg coherence is a final multiplier
  (0.55–1.00), so four individually-strong legs that don't reference each other are capped, and
  actively contradicting legs are capped at 55%.
- **Penalize-don't-skip / honest vs silent vs fabrication**: the standout. An explicit `LEG_CREDIT`
  table grades the full spectrum — FULL 1.00, genre-correct-disclosed 0.45, silent-gap 0.10,
  fabricated 0.00 — which is the most literal, checkable encoding of the brief's exact requirement.
  FIG gets *no* honest-absence discount (matches §9's "absence = near-total loss of grounding"
  note). Disclosure earns partial credit, never full, because reproduction really is harder.
- **Goodhart / D6 edge**: all arithmetic is fixed code; the sole LLM touchpoint emits closed-enum
  categorical labels with auditable one-line justifications (can't be sweet-talked by prose);
  `config_specificity_ratio` / `fig_completeness_ratio` are regex over value-bearing fields so
  padding prose doesn't move the score; harmonic-mean soft-min punishes a weak leg far more than a
  mean without min()'s brittleness; genre cross-check against method files closes the
  genre-laundering loophole. Excellent.
- **Weaknesses**: DISCLOSED_BUT_DEAD (0.55) scoring *higher* than GENRE_CORRECT_DISCLOSED (0.45) is
  an odd ordering (a dead disclosed link worth more than a legitimately-absent leg?); whole-ARA
  rather than §9-object-indexed, so it inherits less of the brief's enumerable-anchor discipline
  than exp1; the 0-3 coherence scale is less concrete than exp4's anchor-matching.

### Rank 3 — exp4 (loser, strong runner-up)
Best single cross-layer *mechanism* in the field but softer overall scoring. Its
**anchor-matching** idea — extract numeric/named anchors (sample sizes, accession formats,
parameter values, dependency versions) from each leg and check they agree across independently
formatted layers — is the most concrete, most Goodhart-resistant answer to "cross-layer, not
single-file" (faking it requires two independently-formatted layers to numerically agree).
Fabrication caps the *whole* bundle (0.20), not just one leg. But: geometric mean + FLOOR 0.02
is meaningfully less punishing than exp3's harmonic mean / exp1's min; the coherence multiplier
floor of 0.5 undercuts its own claim that coherence is "weighted highest"; and it collapses the
silent-gap (0.20) vs fabrication (0.15) distinction into near-equal caps rather than grading the
disclosure spectrum as finely as the brief asks.

### Rank 4 — exp2 (loser)
Solid claim-id reciprocal-linking idea (evidence→claim link must be reciprocated from claims.md
Sources) and external repo URL verification, but deviates most from the brief. It re-anchors the
metric at `logic/claims.md` rather than §9 evidence (the specified primary artifact); its
`0.5*min + 0.5*mean` blend is the *least* punishing weakest-link of the field (a missing leg
lands ~0.33, softer than exp1/exp3); and the "no in-scope claims → return fixed 0.5 anchor" path
is the weakest on penalize-don't-skip — a neutral-low soft-N/A that the brief's hard constraint
argues against.

---

## WINNERS: exp1, exp3

---

## Winner critiques + cycle-2 directions

**exp1** — Keep the §9-object-indexed anchoring and per-object semantic linking; that is the
truest reading of the brief and should survive into the final metric. Two cycle-2 fixes:
1. Replace strict `min()` with a soft-min (harmonic mean, per exp3) so `[0.01,1,1]` and
   `[0.01,0.01,0.01]` don't collapse to the same score — preserve the weakest-link intent without
   the brittleness.
2. Fold in exp4's **anchor-matching** as the concrete test behind "linked": don't accept a
   semantic match on topical similarity alone; require a shared numeric/named anchor (sample size,
   accession, parameter value) between the evidence object and the matched code/data item. This
   hardens the `linked` verdict against LLM over-crediting and makes the cross-layer claim
   falsifiable.
3. Reconcile with exp3's explicit fabrication tier — exp1 discusses Critical Rule #11 in prose but
   its scoring should add a fabrication path that caps the object (or bundle) hard, not just the
   0.3 mislabel discount.

**exp3** — Keep the LEG_CREDIT honest/silent/fabrication table (best in field) and the
fixed-arithmetic/closed-enum-LLM discipline. Cycle-2 fixes:
1. Fix the credit ordering: GENRE_CORRECT_DISCLOSED should not score below DISCLOSED_BUT_DEAD — a
   legitimately-absent, honestly-disclosed leg is at least as reproducible-honest as a dead link.
2. Add exp1's **claims-weighting** to aggregation so a headline object dominates over padded minor
   ones — exp3 currently weights all four legs/objects flat.
3. Make the SCOPE leg's inclusion explicit about non-redundancy with any constraints/limitations
   metric elsewhere in the suite (it risks re-litigating §7); keep it only as a gating floor, not a
   co-equal differentiator, to preserve the fig/data/code triad the metric name centers on.
4. Import exp4's anchor-extraction to make cross_leg_coherence a checkable computation rather than
   a bare 0-3 LLM scale.

**Convergence note for cycle 2**: exp1 (object-indexed anchor + per-object triangulation) and exp3
(graded disclosure table + fixed soft-min arithmetic) are complementary halves of the ideal metric;
exp4's anchor-matching is the connective tissue both should adopt. The final metric should be
§9-object-indexed (exp1), soft-min weakest-link with a graded honest/silent/fabrication credit
table (exp3), and gate `linked` on shared numeric/named anchors (exp4).

---

## Loser one-liners
- **exp2**: Good reciprocal claim-id linking and repo-URL verification, but re-anchors off §9 to
  logic/claims.md, uses the softest weakest-link blend, and its fixed-0.5 "no in-scope claims"
  path is a soft-N/A that undercuts penalize-don't-skip.
- **exp4**: Best cross-layer mechanism (anchor-matching) and whole-bundle fabrication cap, but
  geometric-mean + FLOOR + coherence-floor-0.5 make the aggregate too soft and it collapses the
  silent-gap vs fabrication distinction the brief asks to be graded — its anchor-matching idea is
  promoted into both winners' cycle-2 directions.
