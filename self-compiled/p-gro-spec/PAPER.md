# PAPER: The Grounded Research Object (GRO) — Unified Format Specification

**Source**: `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md` (post-adversarial revision; supersedes an earlier `IDEAL_FORMAT_SPEC.md` draft)
**Type**: format/architecture specification (design paper, not an empirical results paper)
**Compiled**: 2026-07-07

## Summary

GRO is a scientific-publishing unit-of-record format whose central move is to split every metric a research artifact could report into three explicit rigor tiers — **Tier A** (deterministic, pure functions over a frozen input set: quantity ledger, claim logical form, entity spine, cross-layer graph, genre contract), **Tier B** (anchored/reliable given a pinned external resolver: reference spine, registry join, delta-anchor ledger), and **Tier C** (judged, reproducible-not-deterministic: novelty, entailment, validity, frontier triangulation) — and then requires every dossier row to carry its tier on its face rather than collapsing to one number. The document is itself the third stage of a three-stage process: a draft merged from twelve gap-tournament-winning designs, an adversarial critique that produced eleven "must-fix" findings plus additional over-claims/gaps, and this revision, which resolves each finding either by a concrete design change (a new `XQ##` external-quantity ledger, a scoped `registry_authority`, a two-profile `VerificationRecordCore`, a pinned severity-lattice floor for `contested`, three new Class-C blind-reconstruction passes) or by an explicit, labelled demotion to §7 "Honest limitations." The claims below are the load-bearing design assertions and quantified boundaries this revision commits to — architecture, judge-cost order of magnitude, provenance-regime plurality, and the specific boundedness limits of its five sharpest anti-gaming defenses.

## Layer index

| Layer | File | Content |
|---|---|---|
| Manifest | `PAPER.md` | this file |
| Claims | `logic/claims.md` | C01–C12, the paper's load-bearing design assertions |
| Problem | `logic/problem.md` | O##/G## — the affordance gaps GRO is built to close |
| Experiments | `logic/experiments.md` | E01–E08, the design/critique analyses that ground each claim |
| Evidence | `evidence/README.md` | pointer to the underlying spec text and tournament artifacts |
