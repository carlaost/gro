# GRO Compiler

A **Claude Code plugin** that keeps a research project's **GRO artifact** compiled **live** —
at the end of *every* agent turn. It is the GRO analog of the ARA `research-manager`: where
research-manager records the research *process* into an ARA each turn, GRO Compiler takes the
current state and compiles the **GRO material layer** on top of it, incrementally.

> **Live capture.** A `Stop` hook fires when the agent finishes a turn and asks it to run the
> `gro-compiler` skill. The material structure is (re)compiled every turn; nothing is
> fabricated — a slot not yet read from the source is marked `pending_extraction` and picked
> up on a later turn.

## What it is — and what it is not

GRO Compiler does **pure material compilation**: it structures what is *actually present* in
the research into the GRO artifact's material layers. It makes **no judgments** and builds
**no metrics**.

- **In scope (material):** the numbers a claim states, the references it cites, the terms it
  names, the structural form of a claim (is it a prediction? a comparison?), which expected
  sections are present, and the contributions the authors state (linked to the claims that
  realize them). Reading the source to record these is *compilation* — transcription of what
  is there.
- **Out of scope (metrics / judgments):** novelty or contribution typing, confidence scores,
  comparative deltas against prior work, off-paper baselines, precedence neighborhoods / SOTA
  anchors, rigor tiering, and any significance/breakthrough score. These require *judgment*
  and are a **separate, not-yet-converged concern**. They are never written into `gro/`.

## What is a GRO artifact?

An **ARA** (Agent-Native Research Artifact) **extended** with the GRO material layer. The
material layer, written into `<ara>/gro/`:

| File | What |
|---|---|
| `temporal.yaml` | dates present in the material (pub_date / doi / fetch_timestamp) |
| `refs.yaml` | `R##` the reference spine |
| `quantities.yaml` | `Q##` load-bearing numbers, each verbatim-quoted from source |
| `entities.yaml` | `EN-` terms / concepts / methods / measures / datasets named |
| `claims_typed.yaml` | `C##` claims by their structural form (never their merit) |
| `genre.yaml` | paper type + which expected sections are present / absent |
| `contributions.yaml` | `CT##` author-stated contributions, linked to realizing claims |

There is no status/quality/novelty field anywhere in these. `pending_extraction` marks a slot
not yet compiled from the material — a "not yet read" marker, never a deferred judgment. The
compiler never fabricates: it records only what the material states.

## Install

Requires **Python 3** and **PyYAML** (`pip install pyyaml`). The plugin is fully
self-contained — the material engine (`scripts/gro_extend.py`) is vendored, so there is no
dependency on any other repo.

### Via the plugin marketplace (recommended)

In Claude Code:

```
/plugin marketplace add carlaost/gro-compiler
/plugin install gro-compiler@gro-compiler
```

That registers the `Stop` hook and the `gro-compiler` skill. Restart the session (or reload
plugins) so the hook is active.

### Manual / project-local

Clone anywhere and point Claude Code at it, or wire the hook directly in your project's
`.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "/absolute/path/to/gro-compiler/hooks/gro-compiler-stop.sh" }
      ] }
    ]
  }
}
```

## Configure

- **`GRO_ARA_ROOT`** — the ARA root the compiler targets. Default `ara`. Set to `research/ara`
  (or wherever your ARA lives) if different:
  ```bash
  export GRO_ARA_ROOT=research/ara
  ```
- **Disable without uninstalling** — drop an empty file at `hooks/.disabled`.

## How it works

1. **`hooks/gro-compiler-stop.sh`** — the `Stop` hook. Loop-guarded via `stop_hook_active`;
   emits a `block` decision asking the agent to run the skill, then allows the stop.
2. **`skills/gro-compiler/`** — the skill. Runs the deterministic pass, then compiles this
   turn's material into the layers (reading the current logic). Full schemas and the
   in/out-of-scope list are in `references/gro-layers.md`.
3. **`scripts/compile_gro.py`** — the deterministic pass. Scaffolds missing material layers
   non-destructively, fills `temporal`, seeds one `claims_typed` row per real claim, validates
   material integrity (grounding + referential integrity), and prints the pending/issues
   report as JSON.
4. **`scripts/gro_extend.py`** — the vendored material engine (scaffold + validate).

Run the deterministic pass by hand any time:

```bash
python3 scripts/compile_gro.py path/to/ara            # scaffold-if-missing + validate + report
python3 scripts/compile_gro.py path/to/ara --validate # validate + report only
python3 scripts/compile_gro.py path/to/ara --force    # re-scaffold material layers even if present
```

## Spec implemented

This plugin conforms to a single GRO output contract, **`gro.material`** (canonical source of
truth lives in the private `dasmodel` repo; a pinned copy is vendored in `spec/`). It does
**not** implement the separate `gro.metric` spec — no novelty typing, deltas, external
baselines, or SOTA anchor. `spec/IMPLEMENTS` declares `gro.material`; `spec/SPEC_VERSION`
pins the version; `spec/material.gro.openapi.yaml` is the field-by-field contract with example
values.

> Sibling tool: the retrospective/batch **[paper2gro](https://github.com/carlaost/paper2gro)**
> compiler implements both `gro.material` and `gro.metric` (full-text facts → GRO artifact).

## Relationship to research-manager

They **compose**; GRO Compiler does not replace research-manager. research-manager owns
`logic/`, `trace/`, and `staging/` (and its mutability rules apply there). GRO Compiler owns
`gro/` **only** — it reads `logic/` and `PAPER.md` and never writes elsewhere. If both hooks
are active, research-manager reconciles the logic first, then GRO Compiler compiles `gro/`
from it.

## Layout

```
.claude-plugin/
  plugin.json          # plugin manifest (skill + hook)
  marketplace.json     # single-plugin marketplace (enables `/plugin marketplace add`)
hooks/
  gro-compiler-stop.sh # the per-turn Stop hook
  hooks.json
scripts/
  compile_gro.py       # deterministic pass (CLI + skill entrypoint)
  gro_extend.py        # vendored material engine
skills/gro-compiler/
  SKILL.md
  references/gro-layers.md
spec/
  material.gro.openapi.yaml  # vendored, pinned copy of the gro.material output contract
  IMPLEMENTS                 # declares: gro.material
  SPEC_VERSION               # pinned spec version(s)
```

## License

MIT © 2026 Carla Ostmann. See [LICENSE](./LICENSE).
