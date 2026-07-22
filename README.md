# gro-compiler — paper → GRO artifact, from full-text facts

A reusable tool that compiles a **GRO-extended artifact** (an ARA `PAPER.md` plus the
GRO **L8 sidecars**) directly from a paper's **full text**, using facts an LLM extracts
in one pass (e.g. via Undermind `read_pdfs`). It is the paper-based sibling of
`research/paper2gro.py`.

- `paper2gro.py` scaffolds sidecars from an **already-compiled ARA dir** and marks the
  semantic parts `NEEDS_LLM` (novelty typing, delta pairings, baselines, SOTA).
- `gro_compile.py` (**this tool**) builds everything from a **facts JSON** the LLM already
  produced from full text, so claim typing and contribution novelty typing are **filled**.
  Honest `NEEDS_*` markers remain only where even the full text can't supply the value.

This mirrors the published live in-agent `compiler` skill (LLM front, deterministic build):
here Stage 1 is an Undermind `read_pdfs` pass, Stage 2 is `gro_compile.py`.

## The loop

```
1. EXTRACT (LLM/agent):  read_pdfs(<paper>, extraction_prompt.md)  ->  facts JSON  (schema.json)
2. COMPILE (deterministic): python3 gro_compile.py facts/<paper>.json --lib <library>
                            -> <library>/<slug>/PAPER.md + <slug>/gro/*.yaml
```

- `extraction_prompt.md` — the Stage-1 prompt template (substitute the cite key).
- `schema.json` — the exact shape of the facts JSON the extractor must return.
- `gro_compile.py` — the Stage-2 deterministic builder + `--validate`.
- `facts/*.json` — the five worked extractions used to build `../inner-experience-library`.

## Data shape produced (per paper)

`PAPER.md` YAML front-matter: `title, authors, year, venue, doi, ara_version, domain,
keywords, grounding, claims_summary[], abstract`. Then `gro/`:

| file | shape (key fields) | who fills it |
|---|---|---|
| `genre.yaml` | `paper_type`, `expected_slots`, `present_slots`, `absent_declared` | extractor |
| `claims_typed.yaml` | `C##`: `claim_type`, `polarity`, `logical_form`, `population_scope`, `quantity_refs`, `concept_refs`, `proof_refs`(=[]), `depends_on` | extractor + wired |
| `quantities.yaml` | `Q##`: `value`, `unit`, `comparator`, `ci_low/high`, `role`(result/input), `source_ref`, `quote`, `claim_refs` | extractor |
| `entities.yaml` | `EN-<kind>-<slug>`: `term`, `kind`, `xref` | extractor |
| `contributions.yaml` | `CT##`: `author_framed_type`, `compiler_assessed_type{primary,confidence}`, `typing_rationale`, `realized_in`(≥1 claim → anti-puffery lock) | extractor (LLM typing) |
| `external_quantities.yaml` | `XQ##`: `value`, `unit`, `description`, `source_anchor{external_id,fetch_timestamp}`, `baseline_verification` — else **NEEDS_FETCH** | extractor if reported |
| `delta_ledger.yaml` | `D##`: `claimed_value`(Q), `baseline_value`(XQ), `absolute_delta`, `relative_delta`, `delta_status`, `note` — arithmetic auto-computed when paired | compiler (arithmetic) |
| `sota_anchor.yaml` | `precedence_date`, `provenance`, `neighborhood[]`, `used_openalex`, `resolver_notes` — **NEEDS_RESOLVER** until a citation-graph pass runs | resolver (Tier C) |
| `temporal.yaml` | `pub_date`, `doi`, `fetch_timestamp` | compiler (deterministic) |
| `refs.yaml` | `R##`: `raw`, `external_id`, `resolvable` | extractor |

### ID wiring (deterministic)
Local `key` handles in the facts JSON (`c1`, `q_vviq_aph`, …) become canonical IDs
(`C01`, `Q01`, `EN-measure-vviq`, `CT01`, `XQ01`, `D01`, `R01`). The compiler back-fills
`claim.quantity_refs` from each quantity's `claim_keys`, computes `delta.abs.v1` /
`delta.rel.v1` when a `Q`↔`XQ` pair is declared, and enforces that every `CT##` realizes
≥1 claim.

### Grounding
Every claim wires to quantities; every quantity carries a **verbatim quote + source_ref**.
That quote is the evidence anchor — this facts-based path does not build a separate
`/evidence` layer, so `proof_refs` is intentionally empty.

### Honest gaps (never fabricated)
- **NEEDS_FETCH** — no off-paper prior-work baseline reported → `external_quantities` empty.
- **NEEDS_RESOLVER** — precedence neighborhood needs a live OpenAlex/citation-graph pass;
  `--validate` reports `metric_ready=False` until then (same state as a fresh paper2gro run).

### Contribution taxonomy (closed)
`compiler_assessed_type.primary` must be one of `new_paradigm, new_method, new_finding,
refutation, synthesis, incremental_improvement, replication` — matched to what the
significance metric reads. `--validate` rejects anything else, so map first-person
reports / new measures / theories / conceptual distinctions onto the nearest term.

## Usage

```bash
python3 -m pip install pyyaml
python3 gro_compile.py facts/daw20.json --lib ../inner-experience-library --validate
python3 gro_compile.py --batch facts --lib ../inner-experience-library --validate
# cross-check against the existing pipeline's validator:
python3 ../paper2gro.py ../inner-experience-library/<slug> --validate
```

## SOTA resolution via Undermind

`sota_anchor` no longer has to stay NEEDS_RESOLVER. Populate `facts.sota.neighborhood`
(entries `{ref: <facts ref key or R##>, overlap: 0..1, contemporaneous_uncited: bool}`)
from an Undermind reference/citation search — a `year_max`-bounded `search_papers` on the
paper's core finding, scoring its key priors for finding-level overlap. The compiler maps
ref-keys → `R##`, sets `provenance: undermind_resolved`, and the artifact becomes
`metric_ready`. Leave `facts.sota` empty to keep the honest NEEDS_RESOLVER state.

## Test status (this build)

Compiled **9 papers** → `../inner-experience-library/`, all **[VALID]** under
`gro_compile.py --validate` and **`metric_ready=True`** under the existing
`paper2gro.py --validate`, with `sota_anchor` resolved via Undermind. Notes from the run:
- delta arithmetic verified (e.g. Watkins hippocampal 10% vs ~40% → abs −30, rel −0.75);
- `CONTRIB_NORMALIZE` maps loose extraction labels (`theory`, `new_measure`, …) onto the
  closed taxonomy so JSON-mode extraction stays metric-compatible;
- **extraction is not fully hands-off** — `read_pdfs` JSON-mode returned schema-clean
  output for some papers but loosely-structured output for others, so each paper still
  needs a normalization/QA pass before compiling. Only PDF-✓ papers can be read.

## Specs implemented

This compiler conforms to two separate GRO output contracts (canonical source of truth lives
in the private `dasmodel` repo; a pinned copy is vendored in `spec/`):

- **`gro.material`** — the material layer (temporal, refs, quantities, entities, claims_typed,
  genre, author-stated contributions).
- **`gro.metric`** — the not-yet-converged metric layer (contribution novelty typing,
  external_quantities, delta_ledger, sota_anchor).

`spec/IMPLEMENTS` declares both; `spec/SPEC_VERSION` pins the versions. See
`spec/*.openapi.yaml` for the field-by-field contract with example values.

> Sibling tool: the live, per-turn **[gro-compiler](https://github.com/carlaost/gro-compiler)**
> plugin implements `gro.material` only (pure material compilation, no metrics/judgments).
> This tool is the retrospective/batch path and additionally implements `gro.metric`.
