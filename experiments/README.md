# Experiments

**None of this is part of GRO.** GRO is the schema in [`../spec/`](../spec/). Measuring what is in
a record, whether it is novel, rigorous, significant, is done by funders, curators and validators
on their side, with their own methods. It is not something this project publishes, ships or
maintains as a contract.

What this folder holds is our **method**: we try to measure scientific work over compiled
records in order to test one thing, whether the schema is useful in the sense funders need it
to be, maximally readable for the specific signals they care about. When an experiment shows a
fact is buried in prose, retyped in four places, or indistinguishable from an omission, that is a
finding about the *shape*, and the shape changes. Nothing else flows out of here.

Every experiment states which emitter its input records came from. Everything below ran on the
**July 2026 emitter** (10 sidecars: the 7 material files plus three measuring-side files), which
predates the current schema. Results are kept exactly as they were.

## Layout

```
experiments/
  README.md                 # this page
  METRICS.md                # the indicator program: what one would want to measure, and why
  metrics/                  # indicator design work, code, the two blind indicator tournaments
    findings.md             #   the negative result that reframed the program
  runs/                     # the empirical tests over compiled records
    EXPERIMENT_PAPER.md     #   test 1: does typing make prose-blocked facts computable?
    external-validation/    #   test 2: do anchored facts hold against real registries?
    comparison/             #   test 3: three ways of reading a record, side by side
    breakthrough/           #   test 4: does anything read from a record predict field impact?
    extensions/<slug>/      #   the 12 records' material files used by tests 1-3
  history/                  # how the shape was arrived at; frozen
    SPEC-2026-07.md         #   the July draft that fused shape with measuring (unedited)
    DATA_SHAPE-2026-07.md   #   field reference for the July emitter
    methods/                #   the 12-gap format tournament: gap analysis, designs, critique
    metric.gro.openapi.yaml #   the July measuring-side contract, kept as a starting point
    paper/                  #   the 5-page July digest (old framing)
    self-compiled/          #   the four July documents compiled into records
```

## What the experiments found, in one paragraph each

**Typing makes facts computable.** Over 12 records, converting prose to the typed files turned
every blocked structural check into a plain join, and one join caught a real defect
(broken reference integrity). This is the result the schema rests on.
([`runs/EXPERIMENT_PAPER.md`](runs/EXPERIMENT_PAPER.md))

**A record read alone tells you how well it was compiled, not how good the science is.** Running
64 candidate indicators over records, well-compiled bad science and well-compiled good science
were indistinguishable. Signal appeared only where a record joined something outside itself.
This is the finding that draws the line between the schema and everything done with it.
([`metrics/findings.md`](metrics/findings.md))

**LLM-read "breakthrough-ness" tracks attention, not impact.** Over 66 recent and 72 historical
Alzheimer's papers, the one feature that carried any signal agreed with a same-model panel,
much less with an independent model, and not at all with 15-to-20-year citation disruption.
([`runs/breakthrough/RESULTS_PAPER.md`](runs/breakthrough/RESULTS_PAPER.md))

**Corpus caveat.** The 66-record corpus is mostly abstract-only (17 full text). The records
themselves live in a private repository; this folder holds 12 of them.

## Rules for adding an experiment here

1. State the schema version the input records were produced with.
2. Write outputs beside the record, never into its `gro/` files.
3. End with what, if anything, it says about the shape.
