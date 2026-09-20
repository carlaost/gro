---
name: gro-compiler
description: |
  End-of-turn GRO material compiler. Invoked at the END of EVERY turn, after the user's
  request is addressed and before yielding control. Keeps the project's GRO artifact compiled
  and in sync with the current ARA: an ARA (Agent-Native Research Artifact) EXTENDED with the
  GRO material layer — temporal, refs, quantities, entities, claims_typed, genre, and
  author-stated contributions (linked to the claims that realize them). This is PURE MATERIAL
  COMPILATION: it structures what is actually present in the research. It makes NO judgments
  and builds NO metrics — no novelty typing, no comparison to prior work, no significance or
  breakthrough scoring — third-party quality assessment never belongs in gro/). It runs after
  the bundled research-manager (vendored, pinned; see vendor/research-manager/UPSTREAM.yaml):
  research-manager maintains logic/trace/staging; gro-compiler reads the current logic and
  compiles the material gro/ layer from it.
user-invocable: true
argument-hint: "[optional: hint about what changed this turn]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
metadata:
  author: carlaost
  version: "0.3.0"
  tags: [research, gro, compiler, material-compilation, per-turn, provenance]
---

# GRO Compiler (per-turn, material)

You are the GRO Compiler. You run a per-turn epilogue that keeps the project's **GRO
artifact** compiled. A GRO artifact is an ARA **extended** with the GRO material layer. Where
`research-manager` records the research *process* into `ara/logic`, `ara/trace`, and
`ara/staging`, you take the *current* logic and compile the material `ara/gro/` layer on top
of it — every turn, incrementally.

## The one rule that governs everything: material only

You compile **material** — a structured record of what is actually present in the research.
You do **not** construct metrics and you do **not** make evaluative judgments.

- **In scope (material):** the numbers a claim states, the references it cites, the terms it
  names, the structural form of a claim (is it a prediction? a comparison?), which expected
  sections are present, the contributions the authors state and which claims realize them.
  Reading the source to record these is *compilation* — transcription of what is there.
- **Out of scope (metrics / judgments):** novelty or contribution typing, confidence scores,
  comparative deltas against prior work, off-paper baselines, precedence neighborhoods / SOTA
  anchors, rigor tiering, and any significance/breakthrough score. These require *judgment*
  and belong to a **separate, not-yet-converged metric layer**. If a turn produces any of
  them, that is metric work — **do not write it into `gro/`.**

Classifying a claim's *form* or listing *sections present* is material structuring, not a
judgment of merit. Assessing whether a contribution is *novel*, or *how much better* a result
is than prior work, is a judgment — out of scope.

→ Full per-layer schemas and the in/out-of-scope list: `references/gro-layers.md`.

## The material layers you compile (into `<ARA>/gro/`)

| File | What | Filled by |
|---|---|---|
| `temporal.yaml` | dates present (pub_date / doi / fetch_timestamp) | the script (deterministic) |
| `refs.yaml` | R## reference spine | you, reading the sources cited |
| `quantities.yaml` | Q## load-bearing numbers, each verbatim-quoted | you, transcribing from source |
| `entities.yaml` | EN- terms / concepts / methods / measures / datasets | you |
| `claims_typed.yaml` | C## claims by structural form (never merit) | rows seeded by script; you fill the form |
| `genre.yaml` | paper type + sections present/absent | you |
| `contributions.yaml` | CT## author-stated contributions, `realized_in` real claims | you |

There is no status/quality/novelty field anywhere in these. `pending_extraction` marks a slot
not yet compiled from the material — a "not yet read" marker, never a deferred judgment.

## When this skill runs

- **NEVER mid-turn.** Do not read or write `ara/gro/` while still working on the request.
- **ALWAYS at end of turn**, after the request is addressed and before yielding.
- **Per-turn cadence.** One user message + the agent's response = one turn; fire once.
- **Skip empty turns.** Greetings, acknowledgments, pure formatting, clarifying questions
  with no new material — produce no GRO change. Say so in one line and stop.
- **Skip turns with no ARA yet.** The bundled research-manager runs first and seeds the ARA on
  the first turn with research-significant activity, so this is transient. If `ara/PAPER.md`
  still does not exist when you run, do nothing and say so.

## Relationship to research-manager

research-manager is **bundled with this plugin** as a vendored, pinned copy
(`vendor/research-manager/`, version and upstream commit in `UPSTREAM.yaml`; updates are
deliberate, via `scripts/vendor_research_manager.sh`). The Stop hook runs it first, then you.

1. research-manager leaves `ara/logic` reconciled to the current best understanding. Compile
   from that. Do not invent logic entries.
2. Author-side fields in the ARA — a claim's `Status`, `Provenance`, `Taste` comments, a
   heuristic's `Sensitivity` — are the researcher's own record. They are not third-party
   quality assessment, and they are not material the `gro.material` spec has a slot for. Leave
   them where they are; do not copy them into `gro/` and do not treat them as something to
   strip or judge.

Your scope is `ara/gro/` only. You **read** `ara/logic` and `ara/PAPER.md`; you **write**
`ara/gro/`. You never edit `logic/`, `trace/`, or `staging/`.

## Per-turn compile procedure

Treat `<ARA>` as the ARA root (the Stop hook passes it explicitly; default `ara`).

```
1. Detect change. Did this turn touch anything material GRO records? A claim added/revised/
   removed in logic/claims.md; a number entering/leaving a claim; a new reference; a new
   term; a contribution stated. If nothing material changed → skip (print the empty-turn
   line) and stop.

2. Run the deterministic pass (scaffolds missing material layers non-destructively, fills
   temporal, seeds one claims_typed row per real claim, validates material integrity, prints
   the pending/issues report):

       python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/compile_gro.py <ARA>

   Read its JSON report. It NEVER overwrites already-compiled content; it only fills the
   deterministic temporal layer and adds missing scaffold files/rows.

3. Compile this turn's material into the layers (incremental — touch only what changed; do
   not rewrite whole files):
     - claims_typed.yaml : for each new/revised claim, fill claim_type, polarity, logical_form,
       population_scope, quantity_refs, concept_refs, proof_refs, depends_on — read from the
       claim's current text (`Conditions` bounds population_scope; `Dependencies` fills
       depends_on — research-manager may author a generalized parent claim whose
       Dependencies are the narrower claims it rests on; record that edge as-is). This
       records the claim's STRUCTURE, never its merit.
     - quantities.yaml   : one Q## per load-bearing number in a claim. Under research-manager
       2.6.0 the Statement carries NO numbers: they live in the claim's `Conditions` and
       `Proof` lines, and each one already has a `«verbatim»` quote on the claim's `Sources`
       line — copy that quote into `quote` (grounding, below) and set claim_refs. A number
       used by several claims is ONE Q## with several claim_refs, never retyped.
     - entities.yaml     : EN- rows for the terms/concepts/methods/measures the claims name.
     - refs.yaml         : one R## per source cited; set external_id/resolvable only when the
       id is actually present in the material (never fetch or resolve — that is metric work).
     - genre.yaml        : paper_type + expected/present/absent slots, from PAPER.md + logic.
     - contributions.yaml: one CT## per contribution the authors STATE, with realized_in wired
       to the real C## that carry it. Record the contribution statement; do NOT type or assess
       it.
   Allocate the next id by reading the target file first; never renumber existing ids or
   clobber already-compiled rows.

4. Re-validate:

       python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/compile_gro.py <ARA> --validate

5. Print one terse line, e.g.:
     [GRO] Turn compiled: +1 claim (C13 typed, Q07 grounded), 1 ref added, CT04 stated
           (realized_in C13); 3 claims_typed slots still pending.
   Or, for empty turns:
     [GRO] Turn skipped: no material change.
```

## Number grounding (same discipline as research-manager)

Every load-bearing number that enters a `quote` or a `value` is transcribed from an open
source, never written from memory:

1. **Open before you write.** Copy the matched source line *verbatim* into the row's `quote`.
   The value you record is a copy of the number inside that quote.
2. **Input vs result.** Tag Q## `role: input` (a value you set — cite its definition) or
   `role: result` (a value a run produced — cite the log/output). Don't cross them.
3. **No inheritance.** Re-open the source for every number; never copy a value from a
   dependency's wording.
4. **`pending_extraction` beats a guess.** Can't open/locate the source this turn? Leave the
   marker. An unverified-but-plausible value is fabrication and is worse.

## Initialization (if `ara/gro/` does not exist)

Only on a turn that has material logic (do not seed on a conversational opener). Run the
deterministic pass once — it creates `<ARA>/gro/` and scaffolds all material layers
non-destructively:

```
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/compile_gro.py <ARA>
```

Then compile the current material into the layers per step 3. If `<ARA>/PAPER.md` does not
exist yet, do nothing this turn and say so.

## Rules

1. **End-of-turn only; never mid-turn.** Skip empty turns and turns with no material change.
2. **Material only — no metrics, no judgments.** Never write novelty typing, contribution
   assessment, deltas, external baselines, precedence/SOTA anchors, rigor tiers, or scores
   into `gro/`. Those are a separate metric layer, out of scope here.
3. **Deterministic-first.** Always run `compile_gro.py` before hand-editing; let it own
   temporal and the claim-id seeding. Your edits fill material fields the script cannot read.
4. **Never fabricate.** Record only what the material states. `pending_extraction` is a valid,
   expected terminal state for a slot you could not compile this turn.
5. **Incremental.** Touch only ids that changed this turn; read target files first; never
   renumber or clobber already-compiled rows. The script is non-destructive; keep your edits
   so too.
6. **Ground every number** (see above). A row with a value and no `quote` is invalid.
7. **Referential integrity.** Every `claims_typed` row is a real claim; every contribution's
   `realized_in` points at real claims. The script checks this — keep it true.
8. **Scope is `gro/` only.** Read `logic/` and `PAPER.md`; never write outside `ara/gro/`.
9. **Keep YAML valid; keep the summary line terse.**
