#!/usr/bin/env python3
"""
compile_gro.py — per-turn GRO material compiler (deterministic pass).

The gro-compiler SKILL runs this at the end of every turn. It keeps the MATERIAL layers of
the GRO artifact scaffolded and checks their integrity, then reports what material has not
yet been compiled. It does pure material compilation only — NO metrics, NO judgments (no
novelty typing, no comparison to prior work, no scoring). Metrics are a separate concern.

Engine resolution (first hit wins):
  1. vendored `gro_extend.py` next to this script  ← the normal, self-contained path
  2. $GRO_ENGINE                                    ← explicit path to a gro_extend.py

What it does (never fabricates, never clobbers already-compiled content):
  1. Ensure <ARA>/gro/ exists; scaffold any MISSING material layer (temporal is filled
     deterministically; claims_typed is seeded one row per real claim; the rest are empty
     files carrying their schema, for the compile pass to fill).
  2. Validate material integrity: grounding (every quantity has a verbatim quote + a claim
     link) and referential integrity (claims_typed rows map to real claims; contributions'
     realized_in points at real claims).
  3. Report the not-yet-compiled (pending_extraction) slots and any integrity issues as JSON.

Usage:
    python3 compile_gro.py <ARA_dir>            # scaffold-if-missing + validate + report
    python3 compile_gro.py <ARA_dir> --validate # validate + report only (no scaffold)
    python3 compile_gro.py <ARA_dir> --force     # re-scaffold material layers even if present
"""
import argparse
import importlib.util
import json
import os
import sys


def _import_from_path(path, modname):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_engine():
    """Return (module, source_path). Prefer the vendored gro_extend.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    vendored = os.path.join(here, "gro_extend.py")
    if os.path.isfile(vendored):
        return _import_from_path(vendored, "gro_extend"), vendored
    env = os.environ.get("GRO_ENGINE")
    if env and os.path.isfile(env):
        return _import_from_path(env, "gro_extend"), env
    return None, None


def main():
    ap = argparse.ArgumentParser(description="per-turn GRO material compiler (deterministic pass)")
    ap.add_argument("ara", help="the ARA root dir (contains PAPER.md, logic/, gro/)")
    ap.add_argument("--validate", action="store_true", help="validate + report only; no scaffold")
    ap.add_argument("--force", action="store_true", help="re-scaffold material layers even if present")
    args = ap.parse_args()

    ara_dir = os.path.abspath(args.ara)
    report = {"ara": ara_dir}

    if not os.path.isfile(os.path.join(ara_dir, "PAPER.md")):
        report["ok"] = False
        report["reason"] = ("no PAPER.md at ARA root — the ARA is not seeded yet. "
                            "Nothing to compile this turn.")
        print(json.dumps(report, indent=2))
        return 0

    eng, eng_path = _load_engine()
    if not eng:
        report["ok"] = False
        report["reason"] = ("could not load the GRO material engine — expected vendored "
                            "scripts/gro_extend.py, or set $GRO_ENGINE.")
        print(json.dumps(report, indent=2))
        return 2
    report["engine"] = eng_path

    try:
        gro_dir = os.path.join(ara_dir, "gro")
        if not args.validate:
            sc = eng.scaffold(ara_dir, out_dir=None, force=args.force)
            report["scaffold"] = sc
            gro_dir = sc.get("gro_dir", gro_dir)
        report["validate"] = eng.validate(gro_dir, ara_dir=ara_dir)
    except Exception as e:  # noqa: BLE001
        report["ok"] = False
        report["reason"] = f"engine error ({type(e).__name__}: {e}). Is pyyaml installed?"
        print(json.dumps(report, indent=2))
        return 2

    report["pending"] = report["validate"].get("pending", [])
    report["integrity_issues"] = report["validate"].get("issues", [])
    report["material_complete"] = report["validate"].get("material_complete", False)
    report["ok"] = True

    print(json.dumps(report, indent=2))
    print(
        f"[compile_gro] gro/ at {gro_dir} | material_complete: {report['material_complete']} | "
        f"{len(report['pending'])} slot(s) pending compilation | "
        f"{len(report['integrity_issues'])} integrity issue(s)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
