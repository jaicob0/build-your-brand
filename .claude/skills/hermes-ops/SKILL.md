---
name: hermes-ops
description: Use when the student wants their agents and dashboard tied into one operations layer that runs without them — allowlists enforced, gated agents kept off the schedule, every run recorded, and a stop command they can type from memory.
---

# Hermes

You tie the agents and the dashboard into one layer that runs on a
schedule inside the student's own environment, and you make it
provably refusable.

The hardening is the lesson. An agent with access to a store, an inbox
and a card is only safe because of what it cannot do. Everything here
is built so a wrong instruction produces a dated refusal instead of an
action.

## Prerequisites

- `records/agents/<agent_id>/spec.json` and `AGENT.md` for at least one
  agent, from `agent-forge`, with runs on file.
- `records/mission-control/index.html`, from `mission-control`. The
  layer has to be visible or it is not an operations layer.
- `scripts/hermes_run.py` and `scripts/hermes_schedule.py` in the repo.

## What you do

### Step 1 — Read the posture back

Before anything is scheduled, print what each agent is allowed to do,
from its own spec, not from memory:

```bash
python3 scripts/hermes_run.py <agent_id> --task "<a real task>"
```

That is the check mode. It validates the spec, names the allowlist, says
whether the agent is gated, lists its escalations, and writes the record
to `records/ops/runs/`. Nothing executes.

Show the student each agent's posture and ask one question per agent:
if this ran at three in the morning with nobody watching, what is the
worst thing it could do? If the answer is worse than they are willing
to wake up to, the spec is wrong. Go back to `agent-forge` and tighten
`forbidden` or `allowed_tools` before continuing. That is a normal
outcome, not a failure.

### Step 2 — Prove the refusals

Three refusals, run for real, before a single thing is scheduled:

```bash
# not on the allowlist
python3 scripts/hermes_run.py <agent_id> --task "<task>" --tool curl

# gated agent, asked to run unattended
python3 scripts/hermes_run.py <gated_agent_id> --task "<task>" --go

# an agent that does not exist
python3 scripts/hermes_run.py ghost --task "<task>"
```

Each one refuses and writes a dated record. Open
`records/ops/runs/` and read them. An untested guardrail is a belief.

If any of the three executes instead of refusing, stop. That is a real
bug in the layer and it gets fixed before anything runs on a timer.

### Step 3 — Schedule exactly one thing

One agent, the least dangerous one, on the longest cadence that still
proves it works:

```bash
python3 scripts/hermes_schedule.py <agent_id> --task "<task>" --every 60
```

That prints the launchd job and installs nothing. Read it with the
student: the absolute paths, the interval, where the logs land. Gated
agents are refused here by design, so a spend never reaches a timer.

Install only after they have read it and said so:

```bash
python3 scripts/hermes_schedule.py <agent_id> --task "<task>" --every 60 --install
```

Never pass `--install` in the same breath as the first print. Never
schedule more than one agent in this lesson. Never schedule an agent
whose escalation rules have not fired in testing.

### Step 4 — Watch one cycle, then write the runbook

Wait for one scheduled run. Then:

```bash
ls -t records/ops/runs/ | head -3
cat records/ops/launchd.err.log
```

Check the run landed, the output went where the spec said, and the
dashboard shows it. Reload Mission Control: an agent that ran and does
not appear there is a visibility bug, and you fix it now, while the
student is watching, not later.

Write `records/ops/RUNBOOK.md`:

```
# Hermes runbook

Running now:   [agent, cadence, task, label]
Reads:         [paths]
Writes:        [paths]
Gated:         [which agents are gated and on what]
Logs:          records/ops/launchd.*.log
Records:       records/ops/runs/

## Stop everything
python3 scripts/hermes_schedule.py <agent_id> --uninstall

## When a run is wrong
1. Uninstall first, then read the record. Never debug a live timer.
2. The record names the task and the output path. Open both.
3. Tighten the spec, re-validate, prove the refusal again, reschedule.
```

The stop command goes at the top, and the student types it once, now,
to confirm it works. Then they reinstall if they want it running.
Someone who cannot stop the system does not own it.

## Hard rules

- Never schedule a gated agent. `hermes_schedule.py` refuses it; do not
  work around it.
- Never install a launchd job without the student reading the printed
  plist first.
- Never give a scheduled agent a credential in the plist, in the repo,
  or in a record. Credentials live in the student's own environment.
- Never let an escalation go only to a log file. Escalations surface in
  Mission Control, where a human will actually see them.
- Never claim the layer is running until a scheduled cycle has
  completed and left a record.

## On record

- `records/ops/runs/` with at least three refusals and one real run
- `records/ops/schedule.json`, what is installed and on what cadence
- `records/ops/RUNBOOK.md`, with the stop command at the top, typed
  once to prove it
