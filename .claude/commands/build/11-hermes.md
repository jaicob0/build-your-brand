---
description: "Build Your Brand, Lesson 11: The layer. A central allowlist, an escalation channel you proved, five refusals on record, one orchestrator on a host, and a stop command you typed."
---

# /build:11-hermes

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 11 OF 13 · THE LAYER**
About forty minutes. You leave with one agent running on a host, five refusals on record, exceptions arriving somewhere you actually look, and a stop command you have typed.

---

## Scheduling is the step that changes what this is

Everything so far happened with you in the room. You typed, it ran, you
read the result. This lesson takes you out of the loop for one small
job, deliberately, and the whole lesson is about what has to be true
first.

Hermes is the layer: your agents, your dashboard, and the thing that
runs them. Owned, in your environment, not rented.

The hardening is not a feature of the agents. It is that a wrong
instruction produces a dated refusal instead of an action, and that you
can watch it happen before you walk away.

Nothing gets scheduled until five refusals have been run and read.

---

## STEP 1 · One file to audit

```bash
python3 scripts/allowlist_build.py
```

Every agent carries its own allowlist. This collects them into
`records/ops/allowlist.json`: per agent, the tools, the forbidden list,
whether it is gated, which credential names it needs, and its trigger.
One file to read when you want to know what the system can do.

At run time the effective permission is the **intersection** of the two.
Tighten a list here and no edit to a spec can widen it back. Try it:
delete a tool from an agent's list in that file, rebuild, and watch the
rebuild keep your narrower version and record what it withheld.

A tool a spec asks for later that is in neither list is a tool nobody
reviewed. The orchestrator refuses to run until you have looked at it.

> **CHECK.** `allowlist.json` built, read, and tightened anywhere it
> reads wider than the job needs. Say `next`.

---

## STEP 2 · Where the exceptions go

An escalation that lands only in a log file is an exception nobody
handles.

```bash
python3 scripts/hermes_escalate.py --configure
```

Pick a channel in `records/ops/channel.json`:

| Channel | What it needs |
|---|---|
| `queue` | nothing. A dated file in `records/ops/escalations/`, always written |
| `notify` | nothing. A macOS notification |
| `webhook` | a Slack or Discord URL in `BYB_WEBHOOK_URL` |
| `email` | SMTP host, user and password in your `.env` |

Credentials are read by name from your environment. Never in the config
file, never in a record, never in this repo.

Then prove it:

```bash
python3 scripts/hermes_escalate.py --test
```

You have to actually see that arrive. A channel you have not tested is
a channel that does not exist.

> **CHECK.** Channel chosen, test escalation seen with your own eyes.
> Say `next`.

---

## STEP 3 · Read the posture back

For each agent from Lesson 9, with a real task:

```bash
python3 scripts/hermes_run.py <agent_id> --task "<a real task>"
```

Check mode: it prints the effective tool list and where it came from,
the trigger, whether it is gated, whether it is in dry run, any missing
credentials, and what it stops for. It writes the record and executes
nothing.

Then one question per agent, answered honestly: **if this ran at three
in the morning with nobody watching, what is the worst thing it could
do?**

If the answer is worse than you are willing to wake up to, the spec is
wrong. Back to `/build:09-agents`, tighten, rebuild the allowlist.
Going backwards here is the lesson working.

> **CHECK.** Every agent's posture read, worst case named out loud,
> specs tightened if needed. Say `next`.

---

## STEP 4 · Prove the refusals

Five, for real, before anything touches a timer:

```bash
# a tool off the effective list
python3 scripts/hermes_run.py <agent_id> --task "<task>" --tool curl

# a gated agent asked to run unattended
python3 scripts/hermes_run.py <gated_id> --task "<task>" --go

# a credential that is not in this environment
python3 scripts/hermes_run.py <creds_id> --task "<task>" --go

# an on-demand agent, asked by the timer instead of a human
python3 scripts/hermes_run.py <ondemand_id> --task "<task>" --go --by timer

# an agent that does not exist
python3 scripts/hermes_run.py ghost --task "<task>"
```

Each prints a refusal, writes a dated record in `records/ops/runs/` and
appends a line to `records/ops/audit.log`, which is append-only and
never rewritten.

Read all five.

If any of them executes instead of refusing, stop the lesson. That is a
real bug and it gets fixed before anything runs on its own.

An untested guardrail is a belief. You have now tested five.

> **CHECK.** Five refusals run, five records read. Say `next`.

---

## STEP 5 · Schedule one agent, then pick a host

```bash
python3 scripts/hermes_schedule.py add <agent_id> --task "<task>" --every 60
```

The least dangerous agent, on the longest cadence that still proves it
works. Gated and on-demand agents are refused here, so a spend never
reaches a timer.

Adding a second agent later changes that one file. The host always runs
a single job, the orchestrator, which runs whatever is due. You never
install a second timer.

Now the host, and this is an honest choice:

```bash
python3 scripts/hermes_schedule.py install --host launchd --every 5
```

Prints the job, installs nothing. Read it: absolute paths, interval,
where the logs land. Absolute paths are there because launchd does not
inherit your shell PATH, the most common reason a scheduled job never
fires. Add `--yes` when you have read it. **It stops when your Mac
sleeps.** That is real, and it is free.

```bash
python3 scripts/hermes_schedule.py install --host docker
```

Writes `records/ops/docker/Dockerfile` and `docker-compose.yml` and
prints the command. The container mounts this repo, so your records
stay on your disk and never enter the image, and credentials come from
your gitignored `.env`. This is the honest answer to "runs 24/7", and
it needs Docker and a machine that stays on. Start it yourself when you
mean it.

> **CHECK.** One agent scheduled, host chosen and installed
> deliberately. Say `next`.

---

## STEP 6 · Watch a tick, then write the stop command

```bash
python3 scripts/hermes_orchestrator.py --dry-run
python3 scripts/hermes_orchestrator.py
python3 scripts/hermes_schedule.py status
tail -5 records/ops/audit.log
```

The run landed, the output went where the spec said, and the dashboard
shows it. Reload Mission Control. An agent that ran and does not appear
there is a visibility bug, and you fix it now, while you are watching.

Then `records/ops/RUNBOOK.md`, with the stop command at the top:

```bash
python3 scripts/hermes_schedule.py stop
```

Type it once, now. Watch the timer unload and the container go. Then
start it again if you want it running.

The runbook also carries how to inspect, how to rotate a key, and what
to do when a run is wrong: stop first, then read, never debug a live
timer.

Someone who cannot stop the system does not own the system, and the
morning it does something you did not expect is the wrong time to learn
the command.

> **CHECK.** A tick completed and recorded, the dashboard shows it, the
> runbook exists, and you have typed the stop command yourself. Say
> `next`.

---

## If something goes wrong

- **The orchestrator refuses to tick.** The allowlist drifted from the
  specs: a spec now asks for a tool nobody reviewed. Run
  `python3 scripts/allowlist_build.py`, read the difference, then start
  again. This is the layer doing its job.
- **The job never fires.** Almost always PATH. `claude` has to resolve
  absolutely, which is why the plist carries absolute paths. Check
  `records/ops/launchd.err.log` first.
- **`launchctl load` errors.** It is already loaded. `stop`, then
  install again.
- **A refusal executed instead of refusing.** Stop. Do not schedule
  anything. Read the spec: a missing `gate.required`, or a tool in
  `allowed_tools` you did not mean to put there.
- **The test escalation never arrived.** The channel is not configured.
  For `webhook`, `BYB_WEBHOOK_URL` is not set in the environment the
  script ran in. The queue file is still written either way; the queue
  is the record, the channel is the alert.
- **The run worked but wrote somewhere unexpected.** The `writes` field
  is the only place it should land. Fix the spec, not the output.
- **You want it off, now.** `python3 scripts/hermes_schedule.py stop`.
  That is the whole answer.

---

## On record

- `records/ops/allowlist.json`, the one file to audit
- `records/ops/channel.json`, and a test escalation you saw arrive
- `records/ops/runs/`, five refusals and at least one real run, dated
- `records/ops/audit.log`, append-only
- `records/ops/schedule.json`, what is scheduled and where it runs
- `records/ops/RUNBOOK.md`, stop command first, typed once to prove it
- A dashboard that shows work you did not watch happen

Next: `/build:12-done`. Look at everything you built, and the pattern
underneath it.
