#!/usr/bin/env bash
# Vendor the ARA `research-manager` skill into this plugin at a PINNED upstream commit.
#
# This is the only sanctioned way to update vendor/research-manager/. It fetches exactly one
# path of the upstream repo at exactly one commit, replaces the vendored copy wholesale, copies
# the upstream LICENSE alongside, and rewrites the lock file (UPSTREAM.yaml) so the pinned
# version is always readable from the repo. Review the resulting diff, then commit it as one
# deliberate "bump research-manager to <version> (<sha>)" change.
#
# Usage:
#   scripts/vendor_research_manager.sh <git-ref-or-sha>
#   scripts/vendor_research_manager.sh ara-skills-v0.9.0
set -euo pipefail

UPSTREAM_URL="https://github.com/ARA-Labs/Agent-Native-Research-Artifact.git"
UPSTREAM_PATH="skills/research-manager"

REF="${1:-}"
if [ -z "$REF" ]; then
  echo "usage: $0 <git-ref-or-sha>" >&2
  exit 2
fi

HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HERE/vendor/research-manager"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Shallow, blobless, sparse fetch of just the one path at the requested ref.
git -C "$TMP" init -q
git -C "$TMP" remote add origin "$UPSTREAM_URL"
git -C "$TMP" fetch -q --depth 1 --filter=blob:none origin "$REF"
git -C "$TMP" sparse-checkout init --cone
git -C "$TMP" sparse-checkout set "$UPSTREAM_PATH"
git -C "$TMP" checkout -q FETCH_HEAD
SHA="$(git -C "$TMP" rev-parse FETCH_HEAD)"
git -C "$TMP" show FETCH_HEAD:LICENSE > "$TMP/LICENSE.upstream"

SRC="$TMP/$UPSTREAM_PATH"
[ -f "$SRC/SKILL.md" ] || { echo "no SKILL.md at $UPSTREAM_PATH in $REF" >&2; exit 1; }

VERSION="$(grep -m1 -E '^\s*version:' "$SRC/SKILL.md" | sed -E 's/.*version:[[:space:]]*"?([^"]+)"?.*/\1/')"

# Replace wholesale so removed upstream files do not linger.
rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$SRC"/. "$DEST"/
cp "$TMP/LICENSE.upstream" "$DEST/LICENSE"

cat > "$DEST/UPSTREAM.yaml" <<YAML
# Lock file for the vendored ARA research-manager skill. Written by
# scripts/vendor_research_manager.sh — do not edit by hand; re-run the script to bump.
upstream_url: "$UPSTREAM_URL"
upstream_path: "$UPSTREAM_PATH"
ref: "$REF"
sha: "$SHA"
skill_version: "$VERSION"
license: "MIT (see LICENSE in this directory; copyright the upstream authors)"
fetched_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
YAML

echo "vendored research-manager $VERSION @ ${SHA:0:12} ($REF) -> vendor/research-manager/"
find "$DEST" -type f | sed "s|$HERE/||" | sort
