# Quickstart: a live GRO record for a two-person research project

This is the minimal way to dogfood GRO on a real project starting now. No UI, no sophistication.
What you get: a research record that grows as you work, published every couple of days to a
server that timestamps each publish, readable by any agent from a URL, with every earlier state
kept so the claims can be seen evolving.

## One-time setup (each person, 5 minutes)

1. Install the compiler plugin in Claude Code:
   ```
   /plugin marketplace add carlaost/gro
   /plugin install gro-compiler@gro
   ```
   then `/reload-plugins`.
2. Make sure headless Claude can log in (the recorder runs in the background):
   ```
   claude -p "reply with ok"
   ```
   If that errors, run `claude auth login` once and try again.
3. Clone the project repo. If it is new, create it with a README and push it; nothing else is
   needed. The record (`ara/`) is created by the recorder on the first turn that contains real
   research content.

## Working (every session)

- Open Claude Code in the project repo and work as you normally would: discuss, decide, run
  things, read papers. At the end of every turn the plugin records the research-significant
  events into `ara/` in the background and compiles the material layer `ara/gro/`. You will see
  nothing in the terminal; `ara/.recorder.log` shows what it did.
- Meeting notes, transcripts, a colleague's message: paste them into a session and say what they
  are ("notes from today's call with Marco"). The recorder treats them like any other turn.
- Decisions matter more than chatter. Say them in the first person ("we're going with X because
  Y") and they become decision nodes. Hedged talk stays staged until it settles.
- Git flow, two people: `git pull` before a session, `git add ara && git commit && git push` after.
  The record is append-only apart from `ara/logic/`, so conflicts are rare; if two sessions on the
  same day both appended to the same session file, keep both sides.

## Publishing (every couple of days)

Copy the publisher into the project repo once (it is standalone: bash, git, rsync, ssh, python3):

```
cp ~/code/gro/publish/publish.sh ./publish.sh && git add publish.sh && git commit -m "add publisher"
```

Then, with everything committed:

```
./publish.sh
```

Publishing needs ssh access to the server as it stands (the record is rsynced over ssh). Today
that means Carla's key; to let Marco publish, add his public key to the server's
`~/.ssh/authorized_keys`. There is no other way in, which is intended for now.

It tags the commit, ships `ara/` to the server as `current/` and as a dated snapshot, has the
server append a receipt with its own clock, and rewrites `index.md` with what changed since the
last publish. Then `git push origin --tags`.

Result:

```
https://dasmodel.co/records/<project>/index.md            what this is, what changed, receipts
https://dasmodel.co/records/<project>/current/PAPER.md    the record, latest
https://dasmodel.co/records/<project>/snapshots/<tag>/    every earlier publish, verbatim
```

## Consuming it (the intended mode)

Point any agent at the record and ask:

> Read https://dasmodel.co/records/<project>/index.md, then current/PAPER.md and the files it
> lists. What are the current claims, which changed status since the previous publish, and what
> was abandoned and why?

Everything is plain text and YAML, so this works with Claude, a browser, or `curl`.

## What this deliberately does not do yet

- No per-claim versioning inside the record: a claim's row is updated in place, and its history
  lives in the snapshots and in `trace/sessions/*` (`logic_revisions`). Whether claims should
  become versioned objects is an open schema question; this setup lets us watch what we actually
  need before deciding.
- No access control. Anything published is public at that URL.
- No merge tooling for concurrent sessions. Pull before, push after.
- Timestamps inside the record are the author's machine's; the ones to trust are the server
  receipts in `publications.yaml`.
