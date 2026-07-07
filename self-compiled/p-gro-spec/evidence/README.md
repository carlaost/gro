# Evidence

This ARA has no `results.json`/`benchmark.json` — the source paper is a format specification, not an
empirical-results paper, so there are no run outputs to point to. All "Sources" quotes in
`logic/claims.md` are verbatim excerpts from the compiled document itself. The underlying artifacts are:

- **Primary source (compiled document)**: `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md`
  (83,941 bytes; the post-adversarial, third-stage revision — despite the filename, it *supersedes* an
  earlier draft of the same name per its own scope note in §0).
- **Stage-1 draft input**: `research/metrics/v3/tournament/TOURNAMENT_DESIGNS.md` (the twelve
  gap-tournament-winning designs — QUANT, CLAIMFOL, ENTITY, EDGES, GENRE, REFGRAPH, REGISTRY,
  NOVELANCHOR, NOVELSCORE, ENTAIL, VALIDITY, HARDSIGNALS — merged into the pre-critique draft).
- **Gap analysis the draft was evaluated against**: `research/metrics/v3/tournament/AFFORDANCE_GAP.md`,
  `research/metrics/v3/tournament/ALL_METRICS_MERGED.md`.
- **Adversarial critique**: `research/metrics/v3/tournament/CRITIQUE_BRIEF.md`,
  `research/metrics/v3/tournament/TAIL_SYNTHESIS_LOG.md` (contains the eleven must-fix items and
  additional over-claim/missing/cross-layer findings this revision resolves).
- **Interim/tournament logs**: `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.interim.md`,
  `research/metrics/v3/tournament/TOURNAMENT_LOG.md`, `research/metrics/v3/tournament/TOURNAMENT_SUMMARY.md`.
- **Provenance / method note**: see the compiled document's own Appendix ("Provenance & method"),
  which names workflow run `wf_f0bc615b-a88` (+ tail) as the generating process.

No `seal/` or `external/` directory applies — this ARA has not yet undergone a Level-1/Level-2 seal
review, and there is no external replication target (the object under study is a specification, not a
reproducible experiment).
