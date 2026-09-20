# Problem

## Observations

### O01: Every Tier-A deterministic metric in the GRO spec is marked `computable_on_prose: false` on raw prose ARAs
The GRO specification defines eight Tier-A ("pure functions of authored data") metrics. On the original prose ARA (`PAPER.md` plus its drill-down layers), each of the eight is marked `computable_on_prose: false` — not because the arithmetic is hard, but because the field the metric reads (e.g. `claim_type`, `logical_form`, a `quantity_ref`/`proof_ref` link, a `resolvable` boolean, an `xref`, an `expected_slots`/`present_slots`/`absent_declared` triple) does not exist in prose. To compute the metric over prose, an LLM would first have to re-extract the exact typed field the sidecar carries — making the "metric" an LLM annotation step, not a lookup.

### O02: The parent v3 metrics tournament's negative result — internal-consistency metrics cannot see the outside world
Across all 11 winning metric sets in the prior tournament, and independently across its judges, the conclusion was that "a well-compiled record of bad science and a well-compiled record of good science are, by construction, indistinguishable to every metric in this tournament," because a metric that reads only the artifact "cannot, in principle, verify anything about the world outside that file." This negative result predates and frames the present experiment.

### O03: A corpus of 12 already-compiled ARAs was available for a real (not toy) test
The corpus spans clinical biomarker studies (che26, val25, han26, tit26), donanemab trials and secondary analyses (zim25, jes26), single-nucleus/spatial transcriptomics (gau25, ard25), a narrative review (zho25), molecular neuropathology (aki26), a drug-pipeline census (cum26), and a GBD epidemiological analysis (xu25) — enough genre and evidentiary diversity to see whether the deterministic-tier mechanism holds up outside a single toy example.

## Gaps

### G01: No demonstrated mechanism to convert prose-blocked deterministic metrics into computable ones
Prior to this experiment it was unproven that authoring typed sidecars once, upstream, would actually collapse the eight metrics into pure structural joins runnable with zero LLM/network calls at metric-compute time — as opposed to just relocating the same LLM-inference burden into the sidecar-authoring step without actually decoupling it from the metric call.

### G02: Unknown whether the mechanism holds at corpus scale with real numbers, not just in principle
Even if the join mechanism is sound in principle, it was unknown whether it would run cleanly (zero failures) across a real 12-ARA corpus, and what the actual per-metric distribution of values would look like — including edge cases (undefined denominators, negative counts, parser bugs on non-ASCII minus signs).

### G03: Unknown whether the deterministic tier, once computable, actually surfaces anything real
It was unknown whether any of the eight metrics, once running as joins, would catch a genuine structural defect (as opposed to running without error but never firing) — this is the difference between "the metric is computable" and "the metric is useful."

### G04: Left explicitly open — whether the deterministic tier discriminates good science from bad
This experiment does not close G04. No external ground truth (a labeled good/bad-science corpus) was used, and per O02 the parent program's negative result predicts, and this experiment's design guarantees, that it cannot be closed by a metric that reads only the `gro/` sidecars. This gap is inherited, restated, and left open rather than resolved (see C11).
