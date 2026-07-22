# GRO extraction prompt (Stage 1 — LLM full-text pass)

Run this over a paper's full text (e.g. Undermind `read_pdfs`, one paper per subagent).
The model must return a **facts JSON** conforming to `schema.json`, which `gro_compile.py`
then turns deterministically into a GRO-extended artifact. Substitute `{CITE_KEY}`.

> Extract structured facts to build a Grounded Research Object (GRO) artifact from
> `{CITE_KEY}`. Use EXACT verbatim quotes with page/section/table locations wherever
> possible. Do NOT invent numbers; if the paper is theoretical with few quantities, say
> so. Return the following, which map 1:1 onto the GRO facts schema:
>
> 1. **meta** — exact title, all authors, year, venue, DOI, a one-line domain, 6–12
>    keywords, a 2–3 sentence overview, and the abstract (verbatim if available).
> 2. **genre** — the paper_type (free slug), and expected/present/absent content slots
>    (e.g. claims, quantities, experiments, dataset, experiential_report).
> 3. **claims** — the 5–10 main falsifiable claims. Each: a one-line statement; a
>    `claim_type` from {existence, association, comparison, causal, generalization,
>    measurement, definition, theory}; polarity {positive, negative, null}; population
>    scope {sample, cohort, multi_cohort, not_applicable}; and which other claims it
>    depends on.
> 4. **quantities** — every important number, split into RESULTS and INPUTS/design
>    parameters. Each: value, unit, role {result, input}, a verbatim quote with location,
>    and which claim(s) it supports.
> 5. **entities** — key named concepts, measures/instruments, methods, and
>    populations/groups, each tagged kind {concept, measure, method, population}.
> 6. **contributions** — the authors' framed contributions. For each, assign
>    `assessed_type` from the CLOSED taxonomy **{new_paradigm, new_method, new_finding,
>    refutation, synthesis, incremental_improvement, replication}** (map first-person
>    reports / new measures / theories / conceptual distinctions onto the nearest term),
>    a confidence 0–1, a one-sentence rationale, and which claims realize it.
> 7. **external_baselines** — ONLY off-paper prior-work numbers the paper explicitly
>    compares against (value, unit, description, the cited DOI, verification). If none,
>    return an empty list (the compiler marks external_quantities NEEDS_FETCH).
> 8. **deltas** — pair a result quantity against an external baseline where the paper
>    makes such a comparison; give a note. If none, empty list.
> 9. **refs** — 4–6 key references it builds on/argues with (raw string + DOI if known).
> 10. **sota** — leave empty unless you actually resolved a precedence neighborhood; the
>    compiler otherwise marks sota_anchor NEEDS_RESOLVER (the Tier-C citation-graph step).

Emit the result as a single JSON object (keys above) — that file is the compiler input.
`read_pdfs` returns prose, so a follow-up structuring pass (or a human) converts the prose
into the JSON; keep the verbatim quotes intact through that step (they are the grounding).
