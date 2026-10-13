---
description: "Build Your Brand, Lesson 11: The layer. Agents and dashboard tied into one scheduled operations layer, three refusals proved first, and a stop command you type yourself."
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
About thirty minutes. You leave with one agent running on a timer in your own environment, three refusals on record, and a stop command you have typed.

---

## Scheduling is the step that changes what this is

Up to now, everything has happened with you in the room. You typed, it
ran, you read the result. This lesson removes you from the loop for one
small job, on purpose, and the whole lesson is about what has to be
true first.

Hermes is the layer: your agents, your dashboard, and the thing that
runs them, hardened. Owned, in your environment, not rented.

The hardening is not a feature of the agents. It is the fact that a
wrong instruction produces a dated refusal instead of an action, and
that you can prove it before you walk away.

Nothing gets scheduled in this lesson until three refusals have
actually been run and read.

---

## STEP 1 · Read the posture back

For each agent from Lesson 9, with a real task:

```bash
python3 scripts/hermes_run.py <agent_id> --task "<a real task>"
```

That is check mode. It validates the spec, prints the allowlist, says
whether the agent is gated, lists what it stops for, and writes the
record to `records/ops/runs/`. Nothing executes.

Then one question per agent, and answer it honestly: **if this ran at
three in the morning with nobody watching, what is the worst thing it
could do?**

If the answer is worse than you are willing to wake up to, the spec is
wrong. Go back to `/build:09-agents`, tighten `forbidden` or
`allowed_tools`, re-validate. Going backwards here is the lesson
working, not you failing it.

> **CHECK.** Every agent's posture printed and read, worst case named
> out loud, specs tightened if needed. Say `next`.

---

## STEP 2 · Prove the refusals

Three, for real, before anything touches a timer:

```bash
# a tool that is not on the allowlist
python3 scripts/hermes_run.py <agent_id> --task "<task>" --tool curl

# a gated agent, asked to run unattended
python3 scripts/hermes_run.py <gated_agent_id> --task "<task>" --go

# an agent that does not exist
python3 scripts/hermes_run.py ghost --task "<task>"
```

Each prints a refusal and writes a dated record. Open
`records/ops/runs/` and read all three.

If any of them executes instead of refusing, stop the lesson. That is a
real bug and it gets fixed before anything runs on its own.

An untested guardrail is a belief. You have now tested three.

> **CHECK.** Three refusals run, three records read. Say `next`.

---

## STEP 3 · Schedule exactly one thing

> **RUN (Claude, in this session):** Use `hermes-ops` from STEP 3:
> schedule the least dangerous agent, print the job, install nothing.

```bash
python3 scripts/hermes_schedule.py <agent_id> --task "<task>" --every 60
```

That prints the launchd job and writes nothing outside
`records/ops/`. Read it: the absolute paths, the interval, where the
logs land. Absolute paths are there because launchd does not inherit
your shell PATH, which is the single most common reason a scheduled job
never fires.

Gated agents are refused here by design. A spend never reaches a timer.

When you have read it, and only then:

```bash
python3 scripts/hermes_schedule.py <agent_id> --task "<task>" --every 60 --install
```

One agent. The longest cadence that still proves it works. You can add
more once you have watched this one for a week.

> **CHECK.** Job printed, read, installed deliberately. Say `next`.

---

## STEP 4 · Watch one cycle, then write the stop command

Wait for one run. Then:

```bash
ls -t records/ops/runs/ | head -3
cat records/ops/launchd.err.log
```

The run landed, the output went where the spec said it would, and
Mission Control shows it. Reload the dashboard from Lesson 10. An agent
that ran and does not appear there is a visibility bug, and you fix it
now, not later.

Then `records/ops/RUNBOOK.md`, with the stop command at the top:

```bash
python3 scripts/hermes_schedule.py <agent_id> --uninstall
```

Type it once, now, and watch it unload. Reinstall it after if you want
it running. Someone who cannot stop the system does not own the system,
and the time to learn the stop command is not the morning it does
something you did not expect.

> **CHECK.** One cycle completed and recorded, the dashboard shows it,
> the runbook exists, and you have typed the stop command yourself.
> Say `next`.

---

## If something goes wrong

- **The job never fires.** Almost always PATH. `claude` has to resolve
  absolutely; `scripts/hermes_schedule.py` writes absolute paths for
  exactly this reason. Check `records/ops/launchd.err.log` first.
- **`launchctl load` errors.** It is already loaded. Unload it, then
  load it again. The script does that for you on `--install`.
- **A refusal executed instead of refusing.** Stop. Do not schedule
  anything. Read the spec: a missing `gate.required`, or a tool name in
  `allowed_tools` you did not mean to put there.
- **The run worked but wrote somewhere unexpected.** The `writes` field
  in the spec is the only place it should land. Fix the spec, not the
  output.
- **You want it off, now.** `python3 scripts/hermes_schedule.py
  <agent_id> --uninstall`. That is the whole answer. Nothing else keeps
  running.

---

## On record

- `records/ops/runs/`, three refusals and at least one real run, dated
- `records/ops/schedule.json`, what is installed and on what cadence
- `records/ops/RUNBOOK.md`, stop command first, typed once to prove it
- A dashboard that shows work you did not watch happen

Next: `/build:12-done`. Look at everything you built, and the pattern
underneath it.
