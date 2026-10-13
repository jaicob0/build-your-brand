---
name: hermes-ops
description: Use when the student wants their agents and dashboard tied into one operations layer that runs without them — a central allowlist, an append-only audit log, an escalation channel a human actually reads, one orchestrator on a host, five refusals proved first, and a runbook with the stop command at the top.
---

# Hermes

You tie the agents and the dashboard into one layer that runs on a
host, on a schedule, and you make it provably refusable before a single
thing runs unattended.

The hardening is the lesson. An agent with access to a store, an inbox
and a card is only safe because of what it cannot do. Everything here
is built so a wrong instruction produces a dated refusal instead of an
action, and so the student can watch that happen before they walk away.

## Prerequisites

- `records/agents/<agent_id>/spec.json`, `AGENT.md` and `test-log.md`
  for at least one agent, from `agent-forge`.
- `records/mission-control/index.html`, from `mission-control`. A layer
  nobody can see is not an operations layer.
- `scripts/hermes_run.py`, `hermes_orchestrator.py`,
  `hermes_schedule.py`, `hermes_escalate.py`, `allowlist_build.py`.

## What you do

### Step 1 — One file to audit

```bash
python3 scripts/allowlist_build.py
```

This collects every agent's allowlist into
`records/ops/allowlist.json`: per agent, the tools it may use, what it
is forbidden, whether it is gated, which credential names it needs, and
its trigger mode. One file a human reads when they want to know what
the system can do.

At run time the effective permission is the **intersection** of the
spec and this file, so tightening here can never be undone by editing a
spec. Tighten anything that reads wider than the job needs, then
rebuild: the narrower list survives, and what you withheld is recorded.

A tool a spec asks for later that is in neither list is a tool nobody
reviewed. `allowlist_build.py --check` calls that drift, and the
orchestrator refuses to tick until a human has looked at it.

### Step 2 — Where the exceptions go

An escalation that lands only in a log file is an exception nobody
handles. Decide where a human will actually see it:

```bash
python3 scripts/hermes_escalate.py --configure
```

Then set `channel` in `records/ops/channel.json`:

- `queue` — a dated file in `records/ops/escalations/`. Always written,
  whatever else you pick. Free, and the record.
- `notify` — a macOS notification. Free, no account.
- `webhook` — a JSON POST to a URL in `BYB_WEBHOOK_URL`. Slack,
  Discord, anything.
- `email` — SMTP from the env vars named in the config.

Credentials are read from the environment by name. Never written into
the config, a record, or this repo.

Prove the channel before you trust it:

```bash
python3 scripts/hermes_escalate.py --test
```

The student has to see that arrive. If it did not arrive, the channel
is not configured, whatever the file says.

### Step 3 — Read the posture back

For each agent, with a real task:

```bash
python3 scripts/hermes_run.py <agent_id> --task "<a real task>"
```

Check mode. It validates the spec, prints the effective tool list and
where it came from, the trigger, whether it is gated, whether it is in
dry run, any missing credentials, and what it stops for. It writes the
record and executes nothing.

Then ask one question per agent: **if this ran at three in the morning
with nobody watching, what is the worst thing it could do?** If the
answer is worse than the student is willing to wake up to, the spec is
wrong. Go back to `agent-forge`, tighten, rebuild the allowlist. That
is a normal outcome.

### Step 4 — Prove the refusals

Seven, for real, before anything touches a timer:

```bash
# a tool off the effective list
python3 scripts/hermes_run.py <agent_id> --task "<task>" --tool curl

# a gated agent asked to run unattended
python3 scripts/hermes_run.py <gated_id> --task "<task>" --go

# an agent whose credential is not in the environment
python3 scripts/hermes_run.py <creds_id> --task "<task>" --go

# an on-demand agent, asked by the timer rather than a human
python3 scripts/hermes_run.py <ondemand_id> --task "<task>" --go --by timer

# an action on the human-in-the-loop list: drafted, never executed
python3 scripts/hermes_run.py <agent_id> --task "<task>" --action issue_refund

# an agent that does not exist
python3 scripts/hermes_run.py ghost --task "<task>"

# the kill switch, which is the one guardrail they will reach for in a hurry
python3 scripts/hermes_halt.py --reason "testing the switch"
python3 scripts/hermes_run.py <agent_id> --task "<task>"
python3 scripts/hermes_halt.py --resume
```

Each refuses, writes a dated record in `records/ops/runs/` and appends
to `records/ops/audit.log`. Open them and read them with the student.

The human-in-the-loop refusal also routes to the escalation channel,
because that one is not an error: the work was drafted and a person
has to finish it.

If any executes instead of refusing, stop. That is a real bug in the
layer and it gets fixed before anything runs on its own.

### Step 5 — Event-driven work, where a timer is the wrong shape

Some jobs are not a cadence. A ticket arrives, an order lands, a form
is submitted. The contract is one JSON file in
`records/ops/events/inbox/`, and the orchestrator drains the folder on
its next tick, running each event through the same refusals.

```bash
python3 scripts/hermes_events.py drop <agent_id> --task "<what happened>"
python3 scripts/hermes_events.py list
```

Anything can write that file: a shortcut, an automation step, a script,
the student with an editor. For a local webhook:

```bash
python3 scripts/hermes_events.py listen --port 8799
```

It binds to `127.0.0.1` only, and it queues events rather than running
them, so a flood costs disk and not actions. Exposing it to the
internet is a decision for later and not part of this lesson.

### Step 6 — Schedule, then pick a host

Add the least dangerous agent to the schedule:

```bash
python3 scripts/hermes_schedule.py add <agent_id> --task "<task>" --every 60
```

Gated and on-demand agents are refused here by design, so a spend never
reaches a timer. Adding a second agent later changes this file only:
the host always runs one job, the orchestrator, which runs whatever is
due.

Then the honest conversation about the host:

```bash
python3 scripts/hermes_schedule.py install --host launchd --every 5
```

That prints the job and installs nothing. `--yes` installs it. It runs
on the student's Mac, which is free and real, and stops when the Mac
sleeps.

```bash
python3 scripts/hermes_schedule.py install --host docker
```

That writes `records/ops/docker/Dockerfile` and `docker-compose.yml`
and prints the command. The container mounts the repo, so records stay
on the student's disk and never enter the image, and credentials come
from their gitignored `.env`. This is the honest answer to "runs 24/7",
and it needs Docker and a machine that stays on.

Never pass `--yes` in the same breath as the first print. Never
schedule more than one agent in this lesson.

### Step 7 — Watch a tick, then write the runbook

```bash
python3 scripts/hermes_orchestrator.py --dry-run   # what is due
python3 scripts/hermes_orchestrator.py             # run it once, by hand
python3 scripts/hermes_schedule.py status
cat records/ops/heartbeat.json                     # who is alive, and when
tail -5 records/ops/audit.log
```

Every run updates the heartbeat, so a tile on Mission Control can show
when each agent last finished cleanly. An agent whose heartbeat has
stopped moving is the thing a dashboard exists to make obvious.

The run landed, the output went where the spec said, and Mission
Control shows it. Reload the dashboard. An agent that ran and does not
appear there is a visibility bug, fixed now while the student is
watching.

Then write `records/ops/RUNBOOK.md`:

```
# Hermes runbook

## Stop everything
python3 scripts/hermes_halt.py            # kill switch: every agent refuses, now
python3 scripts/hermes_schedule.py stop   # and take the host down

Running:     [agents, cadence, host]
Exceptions:  [channel, and where the queue is]
Allowlist:   records/ops/allowlist.json
Audit:       records/ops/audit.log (append-only)
Records:     records/ops/runs/
Logs:        records/ops/launchd.*.log, or docker logs -f byb-hermes

## Inspect
python3 scripts/hermes_schedule.py status
python3 scripts/allowlist_build.py --check

## Rotate a key
1. Issue the new scoped key at the provider.
2. Replace it in .env (or the host's environment). Never in the repo.
3. Revoke the old one.
4. Run the agent in check mode and confirm no credential is missing.

## When a run is wrong
1. Stop first, then read. Never debug a live timer.
2. The record names the task and the output path. Open both.
3. Tighten the spec, rebuild the allowlist, prove the refusal, restart.
```

The stop command goes at the top, and the student types it once, now,
to confirm it works. Someone who cannot stop the system does not own
the system.

### Step 8 — Verify the whole chain, then say it plainly

Deployed is not working. Run one real task through every link in front
of the student, and report what actually happened:

1. **The agent does the work.** A genuine task it owns, within its
   allowlist, in the brand voice.
2. **The dashboard shows it.** The run appears in the feed and the
   heartbeat moves.
3. **The audit log recorded it**, appended, with the decision.
4. **An exception routes.** Trigger something that should escalate.
   Confirm it did not execute, that it reached the channel, and that it
   is in the log.
5. **A guardrail refuses.** Ask for a tool off the effective list.
   Confirm a refusal, not an execution.
6. **The kill switch halts everything.** Fire it, confirm the next run
   refuses, then resume.
7. **It comes back.** On Docker, `docker compose restart` and confirm
   the container returns and ticks. On launchd, stop and reinstall and
   confirm a tick fires.

Also verify, do not assume, that `.gitignore` covers `.env`,
`records/ops/audit.log` and anything else local:

```bash
git check-ignore -v .env records/ops/audit.log
```

**Do not call the layer live until that chain has run in front of
you.** Say which parts you watched and which you did not. "Running
24/7" is only true on a host that stays on, and only after you have
restarted something and watched it come back.

## Hard rules

- Never schedule a gated or on-demand agent. The scripts refuse them;
  do not work around the refusal.
- Never install a host without the student reading the printed job
  first.
- Never put a credential in the plist, the compose file, a record or
  the repo. Named env vars only.
- Never let an escalation go only to a log file. It goes to the chosen
  channel, and the channel is proved with `--test`.
- Never truncate or rewrite `records/ops/audit.log`.
- Never claim the layer is running until a tick has completed and left
  a record, and never claim 24/7 on a laptop.
- Never mount an MCP server or a skill the agents have not been tested
  against. An unvetted tool is an unlocked door.
- Never execute a `human_in_the_loop` action. It is drafted and handed
  over, always.

## On record

- `records/ops/allowlist.json`, the one file to audit
- `records/ops/channel.json`, and a test escalation the student saw
- `records/ops/runs/` with five refusals and one real run
- `records/ops/audit.log`, append-only
- `records/ops/schedule.json`, what is scheduled and on what cadence
- `records/ops/heartbeat.json`, who is alive and when they last
  finished cleanly
- `records/ops/RUNBOOK.md`, stop command first, typed once to prove it
