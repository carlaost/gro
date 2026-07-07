# Methods & experiments

How the GRO specification was produced. The short version: it was derived *backwards* from a metrics failure, not designed forwards from taste — and every design step was run as a blind, adversarial tournament so no proposal could be graded by its own author.

## Reading order

1. **[`findings.md`](findings.md)** — the negative result. Metrics computed over a record's own structure measure the *fidelity* of the record, not the *quality* of the science; signal appears only at the claim level with external anchors. This is the input to everything else.
2. **[`metrics-candidates.md`](metrics-candidates.md)** — the indicator ledger: 64 candidate contribution metrics (M01–M64) across every artifact surface, pruned/merged to 23 survivors and a TOP-10 chosen for signal beyond citations and the ARA rigor seal.
3. **[`metrics-merged.md`](metrics-merged.md)** & **[`data-shapes.md`](data-shapes.md)** — the full merged metric suite and the artifact surfaces the metrics are computed over.
4. **[`novelty-comparison.md`](novelty-comparison.md)** — positioning against external benchmarks (the Metascience Novelty Indicators Challenge / LENS): three orthogonal, uncalibrated axes (integrity / novelty / fidelity), none covering the reward-what-citations-punish set.
5. **[`affordance-gap.md`](affordance-gap.md)** — the pivot. Auditing every blocked ideal metric against the data shape that blocks it yields the three-class taxonomy (format-recoverable / anchor-dependent / irreducibly semantic) and the line: *the record doesn't lack the knowledge, it lacks the shape.*
6. **[`tournament-designs.md`](tournament-designs.md)** — the raw winning finalist designs for each of the twelve affordance gaps.
7. **[`tail-synthesis-log.md`](tail-synthesis-log.md)** — the review-gate verdicts and the adversarial critique the final synthesis had to resolve.

The resulting specification is [`../SPEC.md`](../SPEC.md).

## The design method

```
  metrics testbed  ──►  negative result  ──►  affordance-gap audit  ──►  three affordance classes
   (64 indicators,       (fidelity, not         (why was each             (format-recoverable /
    blind tournaments)    quality)               metric blocked?)          anchor-dependent /
                                                                           irreducibly semantic)
                                                                                    │
                                                                                    ▼
  FINAL spec (GRO)  ◄──  adversarial red-team  ◄──  merge 12 designs  ◄──  12 gap tournaments
   (3 rigor tiers +       (force every over-claim                          (4 proposers → judge
    funder dossier)        down to a stated limit)                          picks 2 → refine)
```

Proposer pool per gap: four independent agents (two on one model family, two on another). A deliberately harsh, meta-science-literate judge picked the best two and wrote improvement-forcing critiques; finalists refined and merged; a final reviewer accepted or sent back (bounded). The twelve winners were merged into one draft, then an adversarial critique pass enumerated over-claims, internal inconsistencies, and cross-layer conflicts — each resolved in the final either by a design change or an explicit demotion to the honest-limitations section. Run IDs: `wf_f0bc615b-a88` (+ tail `wf_c4cbff37-887`).

## Honest status

The spec is adversarially hardened but empirically unvalidated. The open experiment — the one that would tell us whether any of this is real — is a **discrimination test**: run the affordance-derived metrics over existing literature (starting from the testbed corpus, adding a contrasting second domain) and validate against external ground truth (trial-registry concordance, retraction/correction records, prior-literature novelty). That experiment has not yet been run.
