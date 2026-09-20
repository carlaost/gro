#!/usr/bin/env bash
# Stop hook: at the end of each turn, record the turn into the project's ARA and compile the
# GRO material layer on top of it.
#
# Default mode (0.4.0+): BACKGROUND. The hook detaches a headless `claude -p` recorder
# (hooks/record-turn.sh) that reads this turn from the session transcript, runs the two bundled
# skills (research-manager, then gro-compiler) against <ARA>/, and logs to <ARA>/.recorder.log.
# The hook itself exits 0 at once, so the user's turn ends with nothing extra in the terminal.
#
# Inline mode (the pre-0.4.0 behaviour): set GRO_RECORDER_MODE=inline and the hook emits a
# `block` decision asking the main agent to run the two skills itself, in the foreground.
#
# Guards:
#   stop_hook_active=true    the hook caused this continuation -> allow the stop
#   GRO_RECORDER_CHILD=1     we ARE the background recorder -> never recurse
#   hooks/.disabled          turn the hook off without editing settings
#
# Config (optional):
#   GRO_ARA_ROOT        the ARA root both skills target (default: ara)
#   GRO_RECORDER_MODE   background (default) | inline
#   GRO_RECORDER_MODEL  model for the background recorder (default: the user's default model)

input="$(cat)"
active="$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)"
[ "$active" = "true" ] && exit 0
[ "${GRO_RECORDER_CHILD:-0}" = "1" ] && exit 0
[ -f "$(dirname "$0")/.disabled" ] && exit 0

ARA_ROOT="${GRO_ARA_ROOT:-ara}"
MODE="${GRO_RECORDER_MODE:-background}"

# If the last background recorder could not authenticate (headless `claude -p` has no usable
# login), fall back to inline recording so nothing is lost, and tell the user once per turn.
status_file="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)/${ARA_ROOT}/.recorder/last_status"
if [ "$MODE" = "background" ] && [ -f "$status_file" ] && grep -q '^auth-failed' "$status_file"; then
  if claude auth status 2>/dev/null | jq -e '.loggedIn == true' >/dev/null 2>&1; then
    rm -f "$status_file"   # login is back: return to background mode
  else
    MODE=inline
    AUTH_NOTE="gro-compiler: the background recorder could not authenticate (headless claude -p). Recording inline this turn; earlier missed turns are in ${ARA_ROOT}/.recorder/pending/. Fix with 'claude auth login' in a terminal, or set GRO_RECORDER_MODE=inline to keep it inline."
  fi
fi

if [ "$MODE" = "inline" ]; then
  reason="Turn ending. Before you stop, run the two bundled skills IN ORDER, treating ${ARA_ROOT}/ as the ARA root (substitute ${ARA_ROOT}/ wherever a skill says ara/ or <ARA>). (1) Invoke the gro-compiler:research-manager skill (the copy bundled with this plugin, not any other research-manager) to record the research-significant events of this turn into the ARA; it seeds the ARA if none exists yet and skips empty/conversational turns. (2) Then invoke the gro-compiler skill to compile the GRO material layer (${ARA_ROOT}/gro/) from the reconciled logic. This is PURE MATERIAL COMPILATION: it structures what is actually present in the research (temporal, refs, quantities, entities, claims_typed, genre, author-stated contributions) and writes no third-party quality assessment - no novelty typing, no comparison to prior work, no significance scoring; that never goes in gro/. If ${ARA_ROOT}/.recorder/pending/ contains turn files, those are earlier turns a background recorder could not record: read each, record it the same way, then delete the file. Both skills skip empty turns; if there is nothing to record or compile, say so in one line each and stop. Do not start any new unrelated work."
  if [ -n "${AUTH_NOTE:-}" ]; then
    jq -nc --arg r "$reason" --arg m "$AUTH_NOTE" '{decision:"block", reason:$r, systemMessage:$m}'
  else
    jq -nc --arg r "$reason" '{decision:"block", reason:$r}'
  fi
  exit 0
fi

# --- background mode ---
transcript="$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)"
cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"
[ -z "$transcript" ] || [ ! -f "$transcript" ] && exit 0   # nothing to read this turn from

here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$cwd/$ARA_ROOT" 2>/dev/null || exit 0
nohup env GRO_RECORDER_CHILD=1 GRO_ARA_ROOT="$ARA_ROOT" GRO_RECORDER_MODEL="${GRO_RECORDER_MODEL:-}" \
  bash "$here/record-turn.sh" "$cwd" "$transcript" >> "$cwd/$ARA_ROOT/.recorder.log" 2>&1 < /dev/null &
disown 2>/dev/null || true
exit 0
