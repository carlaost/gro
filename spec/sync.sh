#!/usr/bin/env bash
# sync.sh — copy the canonical GRO contract into the compiler repos and stamp their version.
#
# Source of truth: this directory (gro/spec/). There is exactly one contract, gro.material.
# Each target repo has spec/IMPLEMENTS listing the x-spec-ids it implements. Only gro.material
# is recognised; anything else listed is reported and skipped.
#
# Usage:
#   ./sync.sh <repo-dir> [<repo-dir> ...]
#   ./sync.sh                       # default targets below
set -euo pipefail
cd "$(dirname "$0")"
CANON="$(pwd)"
FILE="material.gro.openapi.yaml"

DEFAULT_TARGETS=(
  "$HOME/code/gro-compiler"
  "$HOME/code/paper2gro"
)
targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then targets=("${DEFAULT_TARGETS[@]}"); fi

ver="$(grep -E '^[[:space:]]*version:' "$CANON/$FILE" | head -1 | sed -E 's/.*version:[[:space:]]*//')"

for repo in "${targets[@]}"; do
  impl="$repo/spec/IMPLEMENTS"
  if [ ! -f "$impl" ]; then
    echo "skip $repo — no spec/IMPLEMENTS"
    continue
  fi
  mkdir -p "$repo/spec"
  : > "$repo/spec/SPEC_VERSION"
  echo "→ $repo"
  while read -r sid; do
    sid="$(echo "$sid" | tr -d '[:space:]')"
    [ -z "$sid" ] && continue
    case "$sid" in \#*) continue;; esac
    if [ "$sid" = "gro.material" ]; then
      cp "$CANON/$FILE" "$repo/spec/$FILE"
      echo "gro.material $ver" >> "$repo/spec/SPEC_VERSION"
      echo "   vendored $FILE  (gro.material @ $ver)"
    else
      echo "   ⚠️  '$sid' is not a GRO contract (measuring is out of scope for GRO) — skipped"
    fi
  done < "$impl"
done
echo "done. Commit + push each repo to publish."
