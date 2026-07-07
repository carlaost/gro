# self-compiled/ — GRO dogfood

The composed **GRO compiler** (ARA-compile + GRO-extend, the same process that produced the sidecars in `../experiment/`) run reflexively over **this project's own papers**. Each paper's findings become a typed ARA + GRO sidecars — the substrate applied to the research that produced it.

| Dir | Source paper | claims | typed quantities |
|---|---|---|---|
| `p-comparison/` | Three Ways to Judge an ARA (comparison + substrate benchmark) | 10 | 49 |
| `p-external-validation/` | External-ground-truth validation of the GRO metrics | 8 | 35 |
| `p-deterministic-experiment/` | Deterministic-tier extension experiment | 11 | 49 |
| `p-gro-spec/` | The Grounded Research Object — specification | 12 | 11 |

Each dir holds an ARA (`PAPER.md`, `logic/{claims,problem,experiments}.md`, `evidence/`) and its GRO sidecars (`gro/{quantities,claims_typed,refs,entities,genre}.yaml`). Every load-bearing number in a claim is copied verbatim from its source paper and tagged in the `Sources` DSL. Note: the "GRO compiler" is not a single packaged tool — it is the ARA compiler composed with the GRO extension step; this directory is what running that composition over our own corpus produces.
