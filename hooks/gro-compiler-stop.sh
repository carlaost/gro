#!/usr/bin/env bash
# Stop hook: at the end of each turn, ask Claude to run the gro-compiler skill to keep the
# project's GRO artifact (ARA + gro/ sidecars + typed layers) compiled and in sync.
#
# Loop guard: when the hook itself caused the continuation (stop_hook_active=true), allow the
# stop so we don't loop forever.
#
# Config (optional):
#   GRO_ARA_ROOT   the ARA root the skill compiles (default: ara; dasmodel uses research/ara)
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

reason="Turn ending. Before you stop, invoke the gro-compiler skill to keep the project's GRO artifact compiled. IMPORTANT: treat ${ARA_ROOT}/ as the ARA root (substitute ${ARA_ROOT}/ wherever the skill says <ARA>). If research-manager also runs this turn, let it finish first so logic/ is reconciled, then compile gro/ from it. This is PURE MATERIAL COMPILATION: the skill structures what is actually present in the research (temporal, refs, quantities, entities, claims_typed, genre, author-stated contributions). It makes NO judgments and builds NO metrics — no novelty typing, no comparison to prior work, no significance/breakthrough scoring; that is a separate concern and never goes in gro/. It skips empty turns and turns with no material change; if there is nothing to compile, say so in one line and stop. Do not start any new unrelated work."

jq -nc --arg r "$reason" '{decision:"block", reason:$r}'
exit 0
