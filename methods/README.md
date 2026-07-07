# methods/ — how the substrate was derived from the metrics

This directory is the **bridge from the metrics program to the format**. The metrics themselves — the seven directions, the indicator ledger, the negative result, the selection tournaments — live in [`../metrics/`](../metrics/) and are headlined in [`../METRICS.md`](../METRICS.md). What's here is how that work turned into a specification for the record itself.

## Reading order

1. **[`affordance-gap.md`](affordance-gap.md)** — the pivot. Given the negative result ([`../metrics/findings.md`](../metrics/findings.md)) — that metrics over a record's own structure measure fidelity, not quality — this audits every *blocked* ideal metric against the data shape that blocked it. The result is the three-class taxonomy (format-recoverable / anchor-dependent / irreducibly semantic) and the line: *the record doesn't lack the knowledge, it lacks the shape.*
2. **[`tournament-designs.md`](tournament-designs.md)** — the raw winning finalist designs for each of the twelve affordance gaps (a design tournament, one per gap: four proposers → judge picks two → refine).
3. **[`tail-synthesis-log.md`](tail-synthesis-log.md)** — the review-gate verdicts and the adversarial critique the final synthesis had to resolve when the twelve designs were merged.

The resulting specification is [`../SPEC.md`](../SPEC.md).

## The design method

```
  metrics program        affordance-gap audit        3 affordance classes
  (../metrics/,      ──►  (why was each         ──►   (format-recoverable /
   negative result)       metric blocked?)            anchor-dependent /
                                                      irreducibly semantic)
                                                              │
                                                              ▼
  FINAL spec (GRO)  ◄──  adversarial red-team  ◄──  merge 12 gap designs
   (../SPEC.md,           (force every over-claim         ◄── 12 gap tournaments
    3 rigor tiers)         down to a stated limit)            (4 proposers → judge → refine)
```

Run IDs: `wf_f0bc615b-a88` (+ tail `wf_c4cbff37-887`).

## Honest status

The spec is adversarially hardened but empirically unvalidated. The open experiment — whether the affordance-derived metrics actually discriminate good science from bad, run over existing literature and validated against external ground truth — has not been run. It is described in [`../metrics/README.md`](../metrics/README.md) and [`../SPEC.md`](../SPEC.md) §7.
