# GRO — the Grounded Research Object

*A specification for a scientific publishing substrate whose unit of record computes its own credibility — plus the metrics work, experiments, and adversarial design tournaments that produced it.*

This repository is the research outcome of a program asking a blunt question: **citations reward citable work and are blind to negative results, replications, refutations, and reuse — can signals derived from a machine-readable research record measure, and let funders reward, what citations cannot?** Chasing that question far enough produced a specification for the record itself. That spec is GRO.

It is designed to be imported into the parent [`dasmodel`](https://github.com/carlaost/dasmodel) repo as a git submodule (see below), but stands on its own.

**Start here:** [`paper/gro-paper.pdf`](paper/gro-paper.pdf) — a 5-page digest of the whole thing (problem → metrics → negative result → affordance gap → GRO → limitations → next steps). The rest of the repo is the long-form backing.

> **Status.** GRO is a design specification, adversarially stress-tested and now **empirically tested on one axis with a largely negative result**. A first discrimination test (breakthrough-ness, 66 recent + 72 historical AD papers — [`experiment/breakthrough/`](experiment/breakthrough/)) found that the one metric carrying signal (L8 contribution-typing) tracks a same-model LLM panel at ρ≈0.58 but an independent model at only ≈0.34 (≈⅓ shared-method bias) and **real-world 15–20-year citation-disruption at ≈0** — i.e. it flags *LLM-perceived contribution depth*, not shown to be field impact. The judged tier also does not scale to a whole corpus, and anti-gaming rests on asserted, not measured, checker independence. These are stated plainly in [`SPEC.md`](SPEC.md) §7/§7a and [`METRICS.md`](METRICS.md); they are the work still to be done, not hidden. This is a substrate *critique and design* artifact — not an implementation, and not a successor to any existing format by inheritance.

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

The full normative spec, including the honest-limitations section, is [`SPEC.md`](SPEC.md). For the **field-by-field data shape as actually emitted** — every sidecar with types and example values — see [`DATA_SHAPE.md`](DATA_SHAPE.md) (the concrete reference; `SPEC.md` is the normative target, `SPEC.md §7a` records emitted-vs-specified).

## Reasoning summary (how we got here)

1. **Papers and citations are a Goodharted proxy** for scientific quality — they reward citable work and can't see negative results, replications, reuse, or refutations.
2. **A metrics testbed** drafted 64 candidate contribution indicators over a structured corpus (~140 Alzheimer's papers, ~60 compiled) and ran them through blind adversarial tournaments.
3. **The negative result:** *metrics computed over a record's own structure measure the fidelity of the record, not the quality of the science.* A well-compiled record of bad science and of good science were indistinguishable; signal appeared only at the claim level, anchored to external ground truth. (See [`metrics/findings.md`](metrics/findings.md); the ideal metrics themselves are in [`METRICS.md`](METRICS.md).)
4. **The affordance gap:** auditing every blocked metric against the shape that blocked it produced the three-class taxonomy above — most blocks were format problems, not feasibility problems. (See [`methods/affordance-gap.md`](methods/affordance-gap.md).)
5. **The design tournament:** each of twelve affordance gaps was run through a four-proposer → judge → refine tournament; the winning designs were merged and put through an adversarial red-team pass that forced every over-claim down to a stated limitation. The output is GRO. (See [`methods/`](methods/).)

## Repository layout

The program runs **metrics → substrate**: the metrics are the entry point, GRO is the substrate they demanded.

```
gro/
  README.md              # you are here
  METRICS.md             # the ideal metrics — thesis, TOP-10, where existing efforts fall short
  SPEC.md                # the normative GRO specification (the intended data shape / full L1-L8 target)
  DATA_SHAPE.md          # CANONICAL data-shape reference — every emitted sidecar, fields + example values (OpenAPI-style), tiers, and what's emitted vs specified
  metrics/               # the incentive-design program (the metrics + code + experiments)
    README.md
    directions.md · candidates.md · merged.md · data-shapes.md
    findings.md          #   the negative result that reframed the program
    novelty-comparison.md · verifier-comparison.md · library-metrics.md
    analysis/            #   comparison-v2-v3, validator-reliability, compiler-model, plan, loop-log
    code/                #   claim_graph.py (flagship), compute_metrics_v3.py, + experiment modules
    tournaments/         #   the two metric tournaments — winners + judgements (round1 per-artifact, round2 per-metric)
  methods/               # how the SUBSTRATE was derived from the metrics
    README.md
    affordance-gap.md    #   the three-class blocked-metric taxonomy (the bridge metrics -> format)
    tournament-designs.md #  the 12 format gaps' winning finalist designs (raw)
    tail-synthesis-log.md #  review verdicts + the adversarial critique the final resolved
  ara/                   # the ARA research-record that came out of this work
    README.md
    PAPER.md  logic/  trace/  staging/
  experiment/            # empirical tests
    README.md
    gro-experiment-paper.pdf   # test 1 write-up: computability (5pp)
    gro_metrics.py · results.json · results.md
    extensions/<slug>/         # GRO typed sidecars generated per ARA (12 ARAs)
    breakthrough/              # test 2: DISCRIMINATION — the breakthrough metric vs LLM panels & real-world disruption
      RESULTS_PAPER.pdf        #   full write-up (the 0.58 -> 0.34 -> ~0 arc, shared-method bias, historical null)
      corpus/ · historical/    #   66 recent + 72 historical (2004-2010) AD papers, scores, reproducible scripts
```

**Empirical status:** two experiments now exist. [`experiment/`](experiment/) confirmed typing the record makes prose-blocked metrics *computable* as structural joins (12 ARAs, deterministic tier). [`experiment/breakthrough/`](experiment/breakthrough/) then ran the harder test — do they *discriminate*? — on the breakthrough axis over 66 recent + 72 historical AD papers, validated against an independent LLM family and, decisively, against real-world citation-disruption. Result: **no reliable discrimination against real outcomes** (ρ≈0; the same metric scored 0.58 against a same-model LLM panel, so ≈⅓ was shared-method bias). The metric flags LLM-perceived contribution depth, not field impact. The sharpening move (full-text, multi-domain historical corpus) is blocked partly by paywall access for older papers. See [`experiment/breakthrough/RESULTS_PAPER.pdf`](experiment/breakthrough/RESULTS_PAPER.pdf) and SPEC §7a.

## Using as a submodule of `dasmodel`

```bash
git submodule add git@github.com:carlaost/gro.git gro
git submodule update --init --recursive
```

## Provenance & positioning

This is part of an incentive-design research program (the "reward what citations punish" thesis), separate from — and in deliberate critique of — the adopted [ARA](https://arxiv.org/abs/2604.24658) substrate it was stress-tested on. GRO is the substrate-design output of that critique, not an ARA re-implementation. Design tournament run IDs: `wf_f0bc615b-a88` (+ tail `wf_c4cbff37-887`). Full method and honest limitations in [`SPEC.md`](SPEC.md) §7 and [`methods/`](methods/).
