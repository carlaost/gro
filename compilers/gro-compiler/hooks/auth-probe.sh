#!/usr/bin/env bash
# SessionStart hook: check once, at the start of a session, that a headless `claude -p` will be
# able to authenticate — the background recorder depends on it. Informational only: prints a
# systemMessage with the fix when the login is missing or expired; never blocks anything.
[ "${GRO_RECORDER_CHILD:-0}" = "1" ] && exit 0
[ -f "$(dirname "$0")/.disabled" ] && exit 0
[ "${GRO_RECORDER_MODE:-background}" = "inline" ] && exit 0
if claude auth status 2>/dev/null | jq -e '.loggedIn == true' >/dev/null 2>&1; then
  exit 0
fi
jq -nc --arg m "gro-compiler: no login is available to headless claude processes, so the end-of-turn recorder cannot run in the background. Run 'claude auth login' in a terminal (then 'claude -p ok' to confirm). Until then, turns are recorded inline with a notice; nothing is lost." '{systemMessage:$m}'
exit 0
