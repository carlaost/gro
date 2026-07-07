# GRO — the Grounded Research Object

*A specification for a scientific publishing substrate whose unit of record computes its own credibility — plus the metrics work, experiments, and adversarial design tournaments that produced it.*

This repository is the research outcome of a program asking a blunt question: **citations reward citable work and are blind to negative results, replications, refutations, and reuse — can signals derived from a machine-readable research record measure, and let funders reward, what citations cannot?** Chasing that question far enough produced a specification for the record itself. That spec is GRO.

It is designed to be imported into the parent [`dasmodel`](https://github.com/carlaost/dasmodel) repo as a git submodule (see below), but stands on its own.

> **Status.** GRO is a design specification, adversarially stress-tested but **empirically unvalidated**. It has not yet been shown to discriminate good science from bad; its judged tier does not scale to a whole corpus; and its anti-gaming guarantees rest on an independence between automated checkers that is asserted, not measured. Those gaps are stated plainly in [`SPEC.md`](SPEC.md) §7 and are the work still to be done, not hidden. This is a substrate *critique and design* artifact — not an implementation, and not a successor to any existing format by inheritance.

---

## The intended data shape

Today's structured research records (e.g. the ARA format this work critiques) store most load-bearing facts as prose an LLM must re-extract — a number hand-retyped in four places instead of one typed value, citations as author-year strings instead of resolvable IDs, honest absence indistinguishable from lazy omission. **The record doesn't lack the knowledge; it lacks the *shape*.**

GRO gives it a shape. One canonical typed record per load-bearing fact, addressed by ID; prose binds back to it. Everything a record must carry is sorted into **three rigor tiers**, kept physically separate so no self-certified number is ever dressed as a checked one:

| Tier | What it holds | How far it can be trusted |
|---|---|---|
| **Deterministic** | typed quantities, claim logical form, typed cross-layer graph, genre manifest | exact, reproducible — a structural join |
| **Reliable-anchored** | references, registrations, accessions, datasets | reliable *given a pinned resolver*; failures quarantined, not faked |
| **Reproducible-judged** | novelty, significance, entailment quality, assumption realism | a calibrated judge, forever — the format only feeds it cleaner, pinned inputs |

These roll up into a **funder-facing credibility dossier** that never collapses to a single number: gate on the deterministic floor, rank on the judged tier, read the rest as risk, and audit any score back to its source *and its rigor class*.

The tiers come from a three-class analysis of *why* each desirable metric was blocked:

- **format-recoverable** — the fact is there as prose; emit it typed → deterministic join.
- **anchor-dependent** — the fact points outside the record; guarantee resolvable external IDs → a reliable join.
- **irreducibly semantic** — no format change makes it computable → a calibrated judge, forever.

The full normative spec, including the honest-limitations section, is [`SPEC.md`](SPEC.md).

## Reasoning summary (how we got here)

1. **Papers and citations are a Goodharted proxy** for scientific quality — they reward citable work and can't see negative results, replications, reuse, or refutations.
2. **A metrics testbed** drafted 64 candidate contribution indicators over a structured corpus (~140 Alzheimer's papers, ~60 compiled) and ran them through blind adversarial tournaments.
3. **The negative result:** *metrics computed over a record's own structure measure the fidelity of the record, not the quality of the science.* A well-compiled record of bad science and of good science were indistinguishable; signal appeared only at the claim level, anchored to external ground truth. (See [`methods/findings.md`](methods/findings.md).)
4. **The affordance gap:** auditing every blocked metric against the shape that blocked it produced the three-class taxonomy above — most blocks were format problems, not feasibility problems. (See [`methods/affordance-gap.md`](methods/affordance-gap.md).)
5. **The design tournament:** each of twelve affordance gaps was run through a four-proposer → judge → refine tournament; the winning designs were merged and put through an adversarial red-team pass that forced every over-claim down to a stated limitation. The output is GRO. (See [`methods/`](methods/).)

## Repository layout

```
gro/
  README.md              # you are here
  SPEC.md                # the normative GRO specification (the intended data shape)
  methods/               # how it was built — the experiments and tournaments
    README.md            #   method overview + reading order
    findings.md          #   the negative result that reframed the program
    affordance-gap.md    #   the three-class blocked-metric taxonomy
    metrics-candidates.md #  the 64->23->10 indicator ledger
    metrics-merged.md    #   merged metric suite (four sources)
    novelty-comparison.md #  positioning vs external benchmarks (LENS / Novelty Challenge)
    data-shapes.md       #   the artifact surfaces the metrics compute over
    tournament-designs.md #  the 12 gaps' winning finalist designs (raw)
    tail-synthesis-log.md #  review verdicts + the adversarial critique the final resolved
  ara/                   # the ARA research-record that came out of this work
    README.md            #   what this is
    PAPER.md  logic/  trace/  staging/
```

## Using as a submodule of `dasmodel`

```bash
git submodule add git@github.com:carlaost/gro.git gro
git submodule update --init --recursive
```

## Provenance & positioning

This is part of an incentive-design research program (the "reward what citations punish" thesis), separate from — and in deliberate critique of — the adopted [ARA](https://arxiv.org/abs/2604.24658) substrate it was stress-tested on. GRO is the substrate-design output of that critique, not an ARA re-implementation. Design tournament run IDs: `wf_f0bc615b-a88` (+ tail `wf_c4cbff37-887`). Full method and honest limitations in [`SPEC.md`](SPEC.md) §7 and [`methods/`](methods/).
