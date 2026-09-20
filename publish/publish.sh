#!/usr/bin/env bash
# publish.sh — minimal GRO publishing: snapshot a project's record (ara/) onto a server that
# stamps it on receipt, so agents can read it by URL and see it evolve publish by publish.
#
#   publish.sh [project-name]        run inside the project repo (the one that has ara/)
#
# What one publish does:
#   1. requires a clean git tree, tags HEAD  pub-<UTC timestamp>
#   2. rsyncs ara/ (minus .recorder*) to  <root>/<project>/current/  and  <root>/<project>/snapshots/<tag>/
#   3. the SERVER appends a receipt (tag, its own clock, git sha, publisher) to  <project>/publications.yaml
#      -- that server timestamp is the one that means something; file mtimes in a repo do not
#   4. writes  <project>/index.md : how to read the record, the snapshot list, and what changed
#      since the previous publish (claims added / status changed, new trace nodes)
#   5. prints the URL
#
# Config (env, all optional):
#   GRO_PUBLISH_HOST   ssh target            default root@159.69.6.146
#   GRO_PUBLISH_ROOT   dir on the server     default /opt/records
#   GRO_PUBLISH_URL    public base URL       default https://dasmodel.co/records
#   GRO_ARA_ROOT       record dir in repo    default ara
set -euo pipefail

HOST="${GRO_PUBLISH_HOST:-root@159.69.6.146}"
ROOT="${GRO_PUBLISH_ROOT:-/opt/records}"
URL="${GRO_PUBLISH_URL:-https://dasmodel.co/records}"
ARA="${GRO_ARA_ROOT:-ara}"

repo="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not inside a git repo"; exit 1; }
cd "$repo"
project="${1:-$(basename "$repo")}"
[ -f "$ARA/PAPER.md" ] || { echo "no $ARA/PAPER.md here — nothing to publish yet"; exit 1; }
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "working tree has uncommitted changes — commit first (the tag must point at what is published)"; exit 1
fi

ts="$(date -u +%Y%m%dT%H%M%SZ)"
tag="pub-$ts"
sha="$(git rev-parse --short HEAD)"
prev="$(git tag -l 'pub-*' | sort | tail -1 || true)"
publisher="$(git config user.name || echo unknown)"

# --- what changed since the previous publish (local, from git) ---
changes="$(python3 - "$prev" "$ARA" <<'PY'
import subprocess, sys, re
prev, ara = sys.argv[1], sys.argv[2]
def show(ref, path):
    try: return subprocess.run(["git","show",f"{ref}:{path}"],capture_output=True,text=True,check=True).stdout
    except subprocess.CalledProcessError: return ""
def claims(text):
    out={}
    for m in re.finditer(r"^## (C\d+): (.*?)\n(.*?)(?=^## C\d+:|\Z)", text, re.S|re.M):
        st=re.search(r"\*\*Status\*\*:\s*(\S+)", m.group(3)); out[m.group(1)]=(m.group(2).strip(), st.group(1) if st else "?")
    return out
def nodes(text): return set(re.findall(r"^\s*- id: (N\d+)", text, re.M))
if not prev:
    print("First publish."); sys.exit(0)
old_c, new_c = claims(show(prev, f"{ara}/logic/claims.md")), claims(show("HEAD", f"{ara}/logic/claims.md"))
old_n, new_n = nodes(show(prev, f"{ara}/trace/exploration_tree.yaml")), nodes(show("HEAD", f"{ara}/trace/exploration_tree.yaml"))
lines=[]
for cid,(title,st) in new_c.items():
    if cid not in old_c: lines.append(f"- new claim {cid} ({st}): {title}")
    elif old_c[cid][1]!=st: lines.append(f"- {cid} status {old_c[cid][1]} -> {st}: {title}")
    elif old_c[cid][0]!=title: lines.append(f"- {cid} retitled: {title}")
for cid in old_c:
    if cid not in new_c: lines.append(f"- claim {cid} removed (see trace)")
added=sorted(new_n-old_n, key=lambda s:int(s[1:]))
if added: lines.append(f"- new trace nodes: {', '.join(added)}")
print("\n".join(lines) if lines else "- no change to claims or trace nodes")
PY
)"

echo "→ tagging $tag ($sha)"; git tag "$tag"

echo "→ shipping $ARA/ to $HOST:$ROOT/$project/"
ssh "$HOST" "mkdir -p '$ROOT/$project/current' '$ROOT/$project/snapshots/$tag'"
rsync -az --delete --exclude '.recorder' --exclude '.recorder.log' "$ARA/" "$HOST:$ROOT/$project/current/"
rsync -az          --exclude '.recorder' --exclude '.recorder.log' "$ARA/" "$HOST:$ROOT/$project/snapshots/$tag/"

echo "→ server receipt"
ssh "$HOST" "cd '$ROOT/$project' && [ -f publications.yaml ] || echo 'publications:' > publications.yaml; \
  printf -- '  - tag: %s\n    received_at: %s\n    git_sha: %s\n    publisher: \"%s\"\n    snapshot: snapshots/%s/\n' \
  '$tag' \"\$(date -u +%FT%TZ)\" '$sha' '$publisher' '$tag' >> publications.yaml"

echo "→ index"
receipts="$(ssh "$HOST" "cat '$ROOT/$project/publications.yaml'")"
{
  cat <<MD
# $project — a GRO research record, published continuously

This is a live research record in the GRO shape: the readable record under \`current/\` (start with
\`current/PAPER.md\`, then \`current/logic/claims.md\`), the typed material layer under \`current/gro/\`
(what is present in the work: quantities, claims by form, entities, references, sections,
stated contributions), and the process trace under \`current/trace/\`.

**For an agent reading this:** fetch \`current/PAPER.md\` for the manifest and layer index, then the
files it points to. Every earlier publish is kept verbatim under \`snapshots/<tag>/\`, so you can
diff any two states of a claim. Dates you can trust are the server receipts in
\`publications.yaml\` (stamped on receipt, not by the author).

## Latest publish: $tag (git $sha)

### Changed since ${prev:-the beginning}
$changes

## Publications (server receipts)
\`\`\`yaml
$receipts
\`\`\`
MD
} > "/tmp/gro-index-$ts.md"
rsync -az "/tmp/gro-index-$ts.md" "$HOST:$ROOT/$project/index.md"; rm -f "/tmp/gro-index-$ts.md"

echo
echo "✅ published $tag"
echo "   $URL/$project/index.md"
echo "   $URL/$project/current/PAPER.md"
echo "   (push the tag too: git push origin $tag)"
