#!/usr/bin/env bash
# Stop hook: at the end of each turn, ask Claude to run the two bundled skills in order —
# research-manager (records the turn into the ARA, seeding it if absent), then gro-compiler
# (compiles the GRO material layer on top). One hook, one continuation, both skills.
#
# Loop guard: when the hook itself caused the continuation (stop_hook_active=true), allow the
# stop so we don't loop forever.
#
# Config (optional):
#   GRO_ARA_ROOT   the ARA root both skills target (default: ara; dasmodel uses research/ara)
#   a sibling ".disabled" file turns the hook off without editing settings.

input="$(cat)"
active="$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)"

if [ "$active" = "true" ]; then
  exit 0
fi

if [ -f "$(dirname "$0")/.disabled" ]; then
  exit 0
fi

ARA_ROOT="${GRO_ARA_ROOT:-ara}"

reason="Turn ending. Before you stop, run the two bundled skills IN ORDER, treating ${ARA_ROOT}/ as the ARA root (substitute ${ARA_ROOT}/ wherever a skill says ara/ or <ARA>). (1) Invoke the gro-compiler:research-manager skill (the copy bundled with this plugin, not any other research-manager) to record the research-significant events of this turn into the ARA; it seeds the ARA if none exists yet and skips empty/conversational turns. (2) Then invoke the gro-compiler skill to compile the GRO material layer (${ARA_ROOT}/gro/) from the reconciled logic. This is PURE MATERIAL COMPILATION: it structures what is actually present in the research (temporal, refs, quantities, entities, claims_typed, genre, author-stated contributions) and writes no third-party quality assessment - no novelty typing, no comparison to prior work, no significance scoring; that never goes in gro/. Both skills skip empty turns; if there is nothing to record or compile, say so in one line each and stop. Do not start any new unrelated work."

jq -nc --arg r "$reason" '{decision:"block", reason:$r}'
exit 0
