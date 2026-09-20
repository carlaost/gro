#!/usr/bin/env bash
# record-turn.sh — the background recorder spawned by gro-compiler-stop.sh.
#
#   record-turn.sh <project-cwd> <transcript.jsonl>
#
# 1. Waits for any previous recorder on the same ARA to finish (mkdir lock, 10 min max).
# 2. Extracts THIS turn (the last user message and everything after it) from the transcript
#    into <ARA>/.recorder/turn-<ts>.md — text, tool names, short tool results; no huge blobs.
# 3. Runs a headless `claude -p` in the project dir that invokes the two bundled skills
#    (research-manager, then gro-compiler) against <ARA>/ with that excerpt as its context.
# 4. Appends one line per run to <ARA>/.recorder.log (stdout/stderr of this script go there).
#
# Env: GRO_ARA_ROOT (default ara), GRO_RECORDER_MODEL (optional), GRO_RECORDER_CHILD=1 (set by
# the hook; makes the nested session's own Stop hook a no-op so recording never recurses).
set -u
cwd="$1"; transcript="$2"
ARA_ROOT="${GRO_ARA_ROOT:-ara}"
ARA="$cwd/$ARA_ROOT"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$ARA/.recorder"
lock="$ARA/.recorder/lock"

log() { printf '%s [recorder %s] %s\n' "$(date -u +%FT%TZ)" "$ts" "$*"; }

# --- 1. serialize recorders on this ARA
waited=0
until mkdir "$lock" 2>/dev/null; do
  sleep 5; waited=$((waited+5))
  if [ "$waited" -ge 600 ]; then log "gave up waiting for lock ($lock)"; exit 0; fi
done
trap 'rmdir "$lock" 2>/dev/null' EXIT

# --- 2. extract the turn
excerpt="$ARA/.recorder/turn-$ts.md"
python3 - "$transcript" "$excerpt" <<'PY' || { log "extract failed"; exit 0; }
import json, sys
src, out = sys.argv[1], sys.argv[2]
rows = []
for line in open(src, encoding="utf-8", errors="replace"):
    line = line.strip()
    if not line: continue
    try: rows.append(json.loads(line))
    except Exception: pass
def text_of(content):
    if isinstance(content, str): return content
    return "\n".join(x.get("text","") for x in content if isinstance(x, dict) and x.get("type")=="text")
def has_user_text(r):
    if r.get("type")!="user": return False
    c = r.get("message",{}).get("content")
    if isinstance(c, str): return bool(c.strip())
    return any(isinstance(x,dict) and x.get("type")=="text" and x.get("text","").strip() for x in (c or []))
start = None
for i in range(len(rows)-1, -1, -1):
    if has_user_text(rows[i]):
        start = i; break
if start is None:
    open(out,"w").write("(no user message found in transcript)\n"); sys.exit(0)
parts = []
budget = 14000
def add(s):
    global budget
    if budget <= 0: return
    s = s[:budget]; budget -= len(s); parts.append(s)
for r in rows[start:]:
    t = r.get("type"); m = r.get("message",{}); c = m.get("content")
    if t == "user":
        if has_user_text(r):
            add("## USER\n" + text_of(c).strip() + "\n\n")
        elif isinstance(c, list):
            for x in c:
                if isinstance(x,dict) and x.get("type")=="tool_result":
                    body = x.get("content")
                    if isinstance(body, list): body = "\n".join(y.get("text","") for y in body if isinstance(y,dict))
                    body = (body or "")
                    if len(body) <= 600: add("### tool_result\n" + body.strip() + "\n\n")
                    else: add("### tool_result (" + str(len(body)) + " chars, omitted)\n\n")
    elif t == "assistant" and isinstance(c, list):
        for x in c:
            if not isinstance(x, dict): continue
            if x.get("type")=="text" and x.get("text","").strip():
                add("## ASSISTANT\n" + x["text"].strip() + "\n\n")
            elif x.get("type")=="tool_use":
                inp = x.get("input",{}) or {}
                brief = inp.get("command") or inp.get("file_path") or inp.get("description") or inp.get("skill") or ""
                add("### tool_use " + str(x.get("name")) + ": " + str(brief)[:300] + "\n\n")
open(out,"w").write("# This turn (extracted from the session transcript)\n\n" + "".join(parts))
PY

# --- 3. headless recorder
cd "$cwd" || { log "cd failed"; exit 0; }
model_flag=()
[ -n "${GRO_RECORDER_MODEL:-}" ] && model_flag=(--model "$GRO_RECORDER_MODEL")
prompt="You are the end-of-turn recorder for this repository, running headless in the background. The file ${ARA_ROOT}/.recorder/turn-${ts}.md holds the user turn that just ended (the user's message, the assistant's replies, and the tools it used). Read it first. Then, treating ${ARA_ROOT}/ as the ARA root: (1) invoke the gro-compiler:research-manager skill to record that turn's research-significant events into the ARA; it seeds the ARA if none exists and skips empty or conversational turns. (2) Then invoke the gro-compiler:gro-compiler skill to compile the GRO material layer (${ARA_ROOT}/gro/) from the reconciled logic. Pure material compilation: what is present in the research; no judgments, no metrics. If ${ARA_ROOT}/.recorder/pending/ contains earlier turn files, record those too (read each, then delete it). Both skills skip empty turns. Do only this. Finish with one line per skill."
log "start (transcript=$(basename "$transcript"), excerpt=$(basename "$excerpt"))"
out="$(claude -p "$prompt" \
  --permission-mode acceptEdits \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Skill" "Bash(python3 *)" "Bash(mkdir *)" "Bash(ls *)" "Bash(cat *)" "Bash(head *)" "Bash(tail *)" "Bash(wc *)" "Bash(grep *)" "Bash(date *)" "Bash(sed -n *)" \
  --no-session-persistence \
  ${model_flag[@]+"${model_flag[@]}"} 2>&1)"
rc=$?
log "done rc=$rc :: $(printf '%s' "$out" | tail -3 | tr '\n' ' | ')"
# status for the hook: on an auth failure the next Stop falls back to inline recording
if printf '%s' "$out" | grep -qiE "Failed to authenticate|not logged in|OAuth session expired|Invalid API key"; then
  echo "auth-failed $(date -u +%FT%TZ)" > "$ARA/.recorder/last_status"
  mkdir -p "$ARA/.recorder/pending" && mv "$excerpt" "$ARA/.recorder/pending/" 2>/dev/null
  log "auth failed; excerpt kept in .recorder/pending/ for the inline fallback"
else
  echo "ok $(date -u +%FT%TZ) rc=$rc" > "$ARA/.recorder/last_status"
  rm -f "$excerpt"
fi
exit 0
