# GRO — the Grounded Research Object

*A neutral substrate for scientific output: each record affords a portfolio of verifiable signals, and each funder or institution composes those signals into its own reward function, aligned with its own incentives. This repo holds the working spec plus the research program — experiments, tournaments, and negative findings — that produced it. Everything here is in-progress design exploration: the data shape is still in discovery, and every specific below is hypothesis, not standard.*

This repository is the outcome of a program asking a blunt question: **citations reward citable work and are blind to negative results, replications, refutations, and reuse — can a machine-readable research record afford signals that let funders reward what citations cannot?** Chasing that question far enough produced a draft specification for the record itself. That draft is GRO.

Two design commitments run through everything here:

1. **The substrate is neutral.** GRO does not rank, score, or decide. A record affords signals; what any signal is *worth* is set downstream, by whoever is allocating — a funder, an institution, a program — through a reward function they compose from the portfolio according to their own priorities. Different consumers weighting the same record differently, sometimes contradictorily, is the point: plural reward functions over a shared substrate mean no canonical scalar and no single target to game.
2. **Semantic verdicts are not signals.** Whether work is novel, significant, or promising is not a property of the record and is deliberately **outside the substrate**. It belongs to the judgment layer of a consumer's reward function; the format's only job there is to feed that judgment cleaner, pinned inputs. This boundary is not a stance — it is the lesson of our own negative findings (below).

**Start here:** [`paper/gro-paper.pdf`](paper/gro-paper.pdf) — a 5-page digest of the whole thing (problem → signals → negative result → affordance gap → GRO → limitations → next steps). The rest of the repo is the long-form backing.

---

## The intended data shape

Efforts toward structured scientific output exist, but nearly all of them keep the load-bearing facts in prose an LLM must re-extract — a number hand-retyped in four places instead of one typed value, citations as author-year strings instead of resolvable IDs, honest absence indistinguishable from lazy omission. Structure as a wrapper, not a shape. **The record doesn't lack the knowledge; it lacks the *shape*.** (And the adversary is the paper and the citation economy built on it — not these parallel efforts.)

GRO gives it a shape — and it is primarily a format for **new work**: a shape scientific output is *born into*, capturing at production time what the paper structurally discards — negative results, abandoned trails, typed quantities, the reasoning between them. One canonical typed record per load-bearing fact, addressed by ID; prose binds back to it.

Backfilling existing literature into GRO is a supporting move, not the point. We do it — and will keep doing it for now — because it is the only way to prove anything on the record that exists today. But a backfilled record is permanently lossy and biased: the source material was produced to fit the paper's shape, and no amount of re-extraction recovers what that shape never let authors put down. The signals a record affords come in **two classes**, kept physically separate so no self-certified number is ever dressed as a checked one:

| Signal class | What it holds | How far it can be trusted |
|---|---|---|
| **Deterministic** | typed quantities, claim logical form, typed cross-layer graph, genre manifest | exact, reproducible — a structural join anyone can re-run |
| **Anchored** | references, registrations, accessions, datasets | as reliable as the pinned resolver it joins against; failures quarantined, not faked |

What the record deliberately does **not** carry: verdicts. Novelty, significance, entailment quality, assumption realism — these are irreducibly semantic, and a record that emitted them would be certifying its own importance. They live in the consumer's reward function, fed by the two signal classes above.

> **Status.** Work in progress. The documents in this repo are snapshots of an evolving design; where they disagree, this README is current thinking. Nothing specific — field names, classes, shapes — is final until it survives empirical validation.

These roll up into a **signal portfolio per record** that never collapses to a single number: a consumer can gate on the deterministic floor, read anchored signals as risk, compose the portfolio into whatever reward function matches their incentives — and audit any signal back to its source and its class.

The two classes come from auditing *why* each desirable signal was blocked. The audit necessarily ran on existing, backfilled records — that is what exists today — but what it specifies is the shape for work born in GRO:

- **format-recoverable** — the fact is there as prose; emit it typed → a deterministic join.
- **anchor-dependent** — the fact points outside the record; guarantee resolvable external IDs → a reliable join.
- **irreducibly semantic** — no format change makes it computable → outside the substrate; the consumer's judgment, fed pinned inputs.

The working spec, including the honest-limitations section, is [`SPEC.md`](SPEC.md). For the **field-by-field data shape as actually emitted** — every sidecar with types and example values — see [`DATA_SHAPE.md`](DATA_SHAPE.md) (the concrete reference; `SPEC.md` is the design target, `SPEC.md §7a` records emitted-vs-specified).

## Negative findings so far (scope stated plainly)

One application of the substrate has gone beyond scoping into discovery work: **breakthrough signals** — could signals derived from the record identify work that later proves field-changing? The answer so far is no, and the details matter:

- **Structure reads fidelity, not quality.** Signals computed over a record's own structure tell you whether the record is faithful — not whether the science is good. A well-compiled record of bad science and of good science were indistinguishable. Real signal appeared only at the claim level, anchored to ground truth outside the record. (See [`metrics/findings.md`](metrics/findings.md).)
- **LLM-judged "breakthrough-ness" tracks perception, not impact.** In a discrimination test (66 recent + 72 historical Alzheimer's papers — [`experiment/breakthrough/`](experiment/breakthrough/)), the one signal carrying any weight agreed with a same-model LLM panel at ρ≈0.58, an independent model family at ≈0.34 (≈⅓ shared-method bias), and real-world 15–20-year citation-disruption at **≈0**. It flags LLM-perceived contribution depth, not field impact. ([`experiment/breakthrough/RESULTS_PAPER.pdf`](experiment/breakthrough/RESULTS_PAPER.pdf))

These two results are why the substrate/reward-function boundary sits where it does: the record can verifiably carry facts and anchors; it cannot verifiably carry importance. Everything else in the signal space — including the directions below — remains at scoping or design stage, stated as such.

## Signal families being explored

What we are looking at affording with GRO, each a different consumer priority over the same substrate:

- **Information gain** — where is a research neighborhood dense, sparse, or redundant; where does a new record add the most that isn't already there.
- **Translational ripeness** — where work sits in the lab-to-world transition: already translational, at the edge, still upstream, past the window.
- **Field formation potential** — method seeds and convergence clusters: new methods trigger fields, and clusters form years before recognition.

None of these is validated. Each is listed as a design target for the reward-function layer, not a capability claim.

## Reasoning summary (how we got here)

1. **Papers and citations are a Goodharted proxy** for scientific quality — they reward citable work and can't see negative results, replications, reuse, or refutations.
2. **A signals testbed** drafted 64 candidate contribution indicators over a structured corpus (~140 Alzheimer's papers, ~60 compiled) and ran them through blind adversarial tournaments.
3. **The negative result:** signals computed over a record's own structure read the fidelity of the record, not the quality of the science. (See [`metrics/findings.md`](metrics/findings.md); the ideal indicators are in [`METRICS.md`](METRICS.md).)
4. **The affordance gap:** auditing every blocked signal against the shape that blocked it produced the three-class taxonomy above — most blocks were format problems, not feasibility problems. (See [`methods/affordance-gap.md`](methods/affordance-gap.md).)
5. **The design tournament:** each of twelve affordance gaps was run through a four-proposer → judge → refine tournament; the winning designs were merged and put through an adversarial red-team pass that forced every over-claim down to a stated limitation. The output is GRO. (See [`methods/`](methods/).)

## Repository layout

The program runs **signals → substrate**: the indicator work is the entry point, GRO is the substrate it demanded.

```
gro/
  README.md              # you are here
  METRICS.md             # the ideal indicators — thesis, TOP-10, where existing efforts fall short
  SPEC.md                # the working GRO specification (the intended data shape / full L1-L8 target)
  DATA_SHAPE.md          # CANONICAL data-shape reference — every emitted sidecar, fields + example values (OpenAPI-style), classes, and what's emitted vs specified
  metrics/               # the incentive-design program (the indicators + code + experiments)
    README.md
    directions.md · candidates.md · merged.md · data-shapes.md
    findings.md          #   the negative result that reframed the program
    novelty-comparison.md · verifier-comparison.md · library-metrics.md
    analysis/            #   comparison-v2-v3, validator-reliability, compiler-model, plan, loop-log
    code/                #   claim_graph.py (flagship), compute_metrics_v3.py, + experiment modules
    tournaments/         #   the two indicator tournaments — winners + judgements (round1 per-artifact, round2 per-metric)
  methods/               # how the SUBSTRATE was derived from the indicator work
    README.md
    affordance-gap.md    #   the three-class blocked-signal taxonomy (the bridge indicators -> format)
    tournament-designs.md #  the 12 format gaps' winning finalist designs (raw)
    tail-synthesis-log.md #  review verdicts + the adversarial critique the final resolved
  ara/                   # the structured research-record testbed used by the experiments
    README.md
    PAPER.md  logic/  trace/  staging/
  experiment/            # empirical tests
    README.md
    gro-experiment-paper.pdf   # test 1 write-up: computability (5pp)
    gro_metrics.py · results.json · results.md
    extensions/<slug>/         # GRO typed sidecars generated per record (12 records)
    breakthrough/              # test 2: DISCRIMINATION — breakthrough signals vs LLM panels & real-world disruption
      RESULTS_PAPER.pdf        #   full write-up (the 0.58 -> 0.34 -> ~0 arc, shared-method bias, historical null)
      corpus/ · historical/    #   66 recent + 72 historical (2004-2010) AD papers, scores, reproducible scripts
```

**Empirical status:** two experiments exist — both on backfilled corpora (the only kind that exists yet), which bounds what they can show. [`experiment/`](experiment/) confirmed typing the record makes prose-blocked signals *computable* as structural joins (12 records, deterministic class). [`experiment/breakthrough/`](experiment/breakthrough/) then ran the harder test — do they *discriminate*? — with the largely negative result described above. The sharpening move (full-text, multi-domain historical corpus) is blocked partly by paywall access for older papers.

## Using as a submodule of `dasmodel`

```bash
git submodule add git@github.com:carlaost/gro.git gro
git submodule update --init --recursive
```

## Provenance & positioning

This is part of an incentive-design research program (the "reward what citations punish" thesis). The target of the critique is the paper–citation complex, not any parallel structured-output effort; GRO is the substrate-design output of the signals program. Design tournament run IDs: `wf_f0bc615b-a88` (+ tail `wf_c4cbff37-887`). Full method and honest limitations in [`SPEC.md`](SPEC.md) §7 and [`methods/`](methods/).
