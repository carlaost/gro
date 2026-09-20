# GRO Compiler

*Part of the [GRO repository](../../README.md). GRO is a schema for publishing scientific work;
this is the live compiler that writes it. Lives at `compilers/gro-compiler/`.*

A **Claude Code plugin** that keeps a research project's **GRO artifact** compiled **live** —
at the end of *every* agent turn. It bundles the ARA `research-manager` skill (vendored, pinned)
and adds the GRO half: each turn, research-manager records the research *process* into the
project's ARA, then GRO Compiler takes the current state and compiles the **GRO material
layer** on top of it, incrementally. **One install, one thing.**

> **Live capture.** A `Stop` hook fires when the agent finishes a turn and asks it to run the
> two bundled skills in order: `research-manager` (records the turn into the ARA, seeding it on
> the first research-significant turn), then `gro-compiler` (compiles `gro/`). Nothing is
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
self-contained: the material engine (`scripts/gro_extend.py`) and the ARA `research-manager`
skill (`vendor/research-manager/`) are both vendored, so there is no dependency on any other
repo or installer.

### Via the plugin marketplace (recommended)

In Claude Code:

```
/plugin marketplace add carlaost/gro
/plugin install gro-compiler@gro
```

That registers the `Stop` hook and both skills (`gro-compiler:research-manager` and
`gro-compiler:gro-compiler`). Restart the session (or reload plugins) so the hook is active.

If you previously installed the ARA skills with `npx @ara-commons/ara-skills`, the copy in
`~/.claude/skills/research-manager` is now redundant for projects using this plugin; the hook
names the bundled, namespaced copy explicitly so the two do not conflict.

### Manual / project-local

Clone anywhere and point Claude Code at it, or wire the hook directly in your project's
`.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "/absolute/path/to/gro/compilers/gro-compiler/hooks/gro-compiler-stop.sh" }
      ] }
    ]
  }
}
```

## Configure

- **`GRO_ARA_ROOT`** — the ARA root both skills target. Default `ara`. Set to `research/ara`
  (or wherever your ARA lives) if different:
  ```bash
  export GRO_ARA_ROOT=research/ara
  ```
- **Disable without uninstalling** — drop an empty file at `hooks/.disabled`.

## Background by default (0.4.0)

The Stop hook does not block the user's turn. It detaches a headless `claude -p` recorder
(`hooks/record-turn.sh`) that extracts the turn that just ended from the session transcript,
runs research-manager and then gro-compiler against `<ARA>/`, and appends one line per run to
`<ARA>/.recorder.log`. The user sees nothing in the terminal; the record catches up within a
minute or two. Recorders on the same ARA are serialized with a lock. The nested session sets
`GRO_RECORDER_CHILD=1`, which makes its own Stop hook a no-op, so recording never recurses.

- **Fallback.** If the headless recorder cannot authenticate (`claude -p` needs a login the
  child process can reach), it keeps the turn excerpt in `<ARA>/.recorder/pending/` and the next
  Stop falls back to inline recording, which also drains `pending/`, and shows a one-line notice.
  Once `claude auth status` reports a login again, the hook returns to background mode by itself.
- `GRO_RECORDER_MODE=inline` restores the old behaviour: the hook asks the main agent to run
  both skills itself, in the foreground.
- `GRO_RECORDER_MODEL=<model>` picks the model for the background recorder (default: your
  default model).
- Add `<ARA>/.recorder/` and `<ARA>/.recorder.log` to your `.gitignore`.

## How it works

1. **`hooks/gro-compiler-stop.sh`** — the `Stop` hook. Loop-guarded via `stop_hook_active`;
   emits a `block` decision asking the agent to run research-manager, then gro-compiler, then
   allows the stop.
2. **`vendor/research-manager/`** — the ARA research-manager skill, vendored verbatim from
   [ARA-Labs](https://github.com/ARA-Labs/Agent-Native-Research-Artifact) at a pinned commit
   (see below). Owns `logic/`, `trace/`, `staging/`; seeds the ARA if absent.
3. **`skills/gro-compiler/`** — the GRO skill. Runs the deterministic pass, then compiles this
   turn's material into the layers (reading the current logic). Full schemas and the
   in/out-of-scope list are in `references/gro-layers.md`.
4. **`scripts/compile_gro.py`** — the deterministic pass. Scaffolds missing material layers
   non-destructively, fills `temporal`, seeds one `claims_typed` row per real claim, validates
   material integrity (grounding + referential integrity), and prints the pending/issues
   report as JSON.
5. **`scripts/gro_extend.py`** — the vendored material engine (scaffold + validate).

Run the deterministic pass by hand any time:

```bash
python3 scripts/compile_gro.py path/to/ara            # scaffold-if-missing + validate + report
python3 scripts/compile_gro.py path/to/ara --validate # validate + report only
python3 scripts/compile_gro.py path/to/ara --force    # re-scaffold material layers even if present
```

## Spec implemented

This plugin conforms to the GRO contract, **`gro.material`**. The canonical source of truth is
`spec/material.gro.openapi.yaml` at the root of this repository (two levels up); a copy is kept
in `spec/` here because a plugin is copied out of the repo when installed (`../../spec/sync.sh`
refreshes it). That is the only GRO contract: measuring (novelty typing, deltas,
external baselines, SOTA anchors) is not part of GRO and this plugin never emits it.
`spec/IMPLEMENTS` declares `gro.material`; `spec/SPEC_VERSION` pins the version;
`spec/material.gro.openapi.yaml` is the field-by-field contract with example values.

> Sibling tool: the retrospective/batch **[paper2gro](https://github.com/carlaost/paper2gro)**
> compiler implements both `gro.material` and `gro.metric` (full-text facts → GRO artifact).

## Bundled research-manager: which version, and how it updates

`vendor/research-manager/UPSTREAM.yaml` is the lock file. It records the upstream repo, path,
git ref, full commit sha, skill version and fetch time of the vendored copy — so the exact
research-manager this plugin runs is always readable from the repo. The skill files are
byte-identical to upstream; nothing is patched locally.

Updates are deliberate, never automatic:

```bash
scripts/vendor_research_manager.sh ara-skills-v0.9.0   # a tag, branch, or full sha
git diff vendor/                                        # review what changed upstream
```

The script replaces `vendor/research-manager/` wholesale at that ref, copies the upstream
LICENSE alongside, and rewrites the lock file. Commit the result as one "bump research-manager
to X" change, and adjust `skills/gro-compiler/SKILL.md` if the ARA claim schema moved.

**Division of labour.** research-manager owns `logic/`, `trace/`, and `staging/` (its
mutability rules apply there). GRO Compiler owns `gro/` **only** — it reads `logic/` and
`PAPER.md` and never writes elsewhere. The author's own fields in the ARA (claim `Status`,
`Provenance`, `Taste` comments) stay in the ARA; they are the researcher's record, not
third-party assessment, and the material spec has no slot for them.

## Layout

```
.claude-plugin/
  plugin.json          # plugin manifest (two skills + hook)
  marketplace.json     # single-plugin marketplace (enables `/plugin marketplace add`)
hooks/
  gro-compiler-stop.sh # the per-turn Stop hook (research-manager → gro-compiler)
  hooks.json
scripts/
  compile_gro.py             # deterministic pass (CLI + skill entrypoint)
  gro_extend.py              # vendored material engine
  vendor_research_manager.sh # re-vendor research-manager at a pinned ref (the only way to update)
skills/gro-compiler/
  SKILL.md
  references/gro-layers.md
vendor/research-manager/     # ARA research-manager, vendored verbatim from ARA-Labs (MIT)
  SKILL.md  references/  templates/
  LICENSE                    # upstream license
  UPSTREAM.yaml              # lock: upstream url/path/ref/sha/version/fetched_at
spec/
  material.gro.openapi.yaml  # vendored, pinned copy of the gro.material output contract
  IMPLEMENTS                 # declares: gro.material
  SPEC_VERSION               # pinned spec version(s)
```

## License

MIT © 2026 Carla Ostmann. See [LICENSE](./LICENSE).

`vendor/research-manager/` is the ARA `research-manager` skill by
[ARA-Labs](https://github.com/ARA-Labs/Agent-Native-Research-Artifact), © 2026 Orchestra
Research, MIT — see [vendor/research-manager/LICENSE](./vendor/research-manager/LICENSE). It is
redistributed unmodified; its version and upstream commit are in
[vendor/research-manager/UPSTREAM.yaml](./vendor/research-manager/UPSTREAM.yaml).
