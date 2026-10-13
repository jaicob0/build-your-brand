---
description: "Build Your Brand, Lesson 9: The cast. One voice file, agents with typed specs and scoped keys, five real tasks each, and an honest PASS/FAIL log."
---

# /build:09-agents

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 9 OF 13 · THE CAST**
About forty-five minutes. You leave with two or three agents that own a named job, five real tasks tested on each, and an honest log including the ones they got wrong.

---

## A brand is how you are seen. Agents are how the work gets done

You have used two agents already. Aphrodite decided and Hephaestus
built, and a typed brief passed between them. That shape is not
specific to images. It is what an agent is: one job, written down, with
an allowlist in front of it and a human at the part that needs
judgement.

This lesson runs that shape on the work that eats your week.

Three things separate this from a prompt you keep retyping, and all
three are files: the voice they share, the fence around each one, and
the log of what happened when you tested them on real work.

---

## STEP 1 · Name the jobs, cut them down

Pick two or three jobs you do by hand every week. Say each as one
sentence with a verb and an object.

"Handles support" is a department. "Drafts the reply to every email
asking where an order is" is a job. Only the second can be owned.

Then answer three questions per job, out loud:

- **How often, honestly?** Weekly or more, or it is not worth an agent.
- **Where would a good junior get this wrong?** That is the escalation
  boundary. Every real job has one.
- **What is the worst thing this could do if it misreads the
  situation?** Refund the wrong amount, email the wrong list, publish
  something off-brand. That answer sets the fence, and whether the gate
  is on.

If you cannot answer the second one, you do not know the job well
enough to hand it over. Do it by hand once more this week and watch
where you hesitate.

> **CHECK.** Two or three jobs, one sentence each, all three questions
> answered. Say `next`.

---

## STEP 2 · One voice, written once

> **RUN (Claude, in this session):** Use `agent-forge`, STEP 2: write
> `records/agents/_voice.md` from my brand files.

Every agent inherits that one block, so they sound like one operator
instead of three different companies. It is quoted from
`project-knowledge.md`, not paraphrased, because a voice that is a
paraphrase of a paraphrase drifts inside a week.

Claude writes the same reply twice for you, once through the block and
once as a generic assistant, side by side. **If you cannot tell which
is which, the block is not finished.** Say so and have it pull harder
on the real sentence shapes and the USE / AVOID lists.

> **CHECK.** `_voice.md` exists, and the two replies are obviously
> different. Say `next`.

---

## STEP 3 · The spec, typed

> **RUN (Claude, in this session):** Continue `agent-forge` to STEP 3:
> write and validate a spec for each job from STEP 1.

```bash
python3 scripts/validate_brief.py records/agents/<agent_id>/spec.json
```

`VALID`, or it doesn't move.

Then read each one as the agent would. Six fields decide whether this
is safe to own:

| Field | What a wrong answer costs you |
|---|---|
| `allowed_tools` | "anything it needs" is not an allowlist |
| `human_in_the_loop` | the 90/10 line: what it drafts and hands over rather than doing. Refunds, cancellations, anything public |
| `forbidden` | what it refuses outright, never even drafts |
| `escalate_when` | "if something seems wrong" never fires. Use a signal: an amount, a word in a subject, a missing field |
| `gate` | `true` the moment it spends, sends, publishes or deletes |
| `credentials` | env var NAMES only, one scoped key per agent, so you can revoke one without touching the others |
| `trigger` | `on-demand` means a timer may never ask. Lesson 11 enforces that |

`writes` is one directory on purpose. An agent that can write anywhere
is an agent you cannot audit. And `dry_run: true` is the honest setting
while a tool is not connected: it composes the action and hands it to
you instead of performing it.

The split between the middle two rows is the one worth sitting with.
**Forbidden** means it never touches that, ever. **Human in the loop**
means it does the work and stops short of the irreversible bit, so a
refund arrives on your desk already written, needing a keystroke rather
than ten minutes. That line is what makes an agent useful without
making it dangerous, and the runner enforces it in Lesson 11.

The access paradox, plainly: the more an agent can reach, the longer
its `human_in_the_loop` list has to be. Power and guardrails scale
together. Never grant a capability just in case.

> **CHECK.** Every spec `VALID` and read with your own eyes, with an
> allowlist and escalations specific enough to argue with. Say `next`.

---

## STEP 4 · Connect the tools, scoped down

> **RUN (Claude, in this session):** Continue `agent-forge`, STEP 4:
> wire only the tools each agent's one workflow needs.

MCP first where a real tool has a server: a store, an inbox, a
helpdesk, a calendar. Then scope it down. A support agent reads orders
and drafts replies; it does not get write access to the storefront.
Read-only wherever the job allows, one key per agent so revoking one
does not touch the others.

Nothing connected yet? That is fine, and it is most people on the first
pass. `dry_run: true` and the agent composes the action for you to
send. That is a real result, not a stub, and it is the honest state for
anything pointed at a live account on day one.

Keys go in `.env` by name. Never in the spec, never in a record, never
in this repo.

> **CHECK.** Each agent reaches only what its own job needs, and
> anything unconnected is in dry run. Say `next`.

---

## STEP 5 · Five real tasks, logged honestly

> **RUN (Claude, in this session):** Continue `agent-forge` to STEP 4
> and STEP 5: write each `AGENT.md`, then run five real tasks per
> agent, including the edge cases, and log them.

Give it five tasks off your actual week, not invented ones, and at
least two of them the hard cases from STEP 1. Each goes in
`records/agents/<agent_id>/test-log.md` with the agent's real output
and a PASS or FAIL on voice and on accuracy.

Read the log yourself. The number that matters is accuracy over the
batch, and **a correct escalation counts as a pass**, not a failure.

A FAIL you tuned is worth more than a PASS nobody checked. If the log
has no FAIL in it at all, either the tasks were too easy or someone
rounded up.

> **CHECK.** Five logged tests per agent, read by you, accuracy named
> out loud. Say `next`.

---

## STEP 6 · Make one stop on purpose

Give an agent a task that trips one of its own `escalate_when` rules.
The refund over the limit. The email that is actually a complaint.

It should stop, say why, and hand the work back. If it has a go anyway,
the rule is written as a feeling rather than a signal, and that is
worth knowing now rather than at three in the morning.

Then tune and run again until you would let it handle the routine work
unsupervised, and not a moment before.

An agent with no refusal on record has guardrails nobody has tested.
Same principle as the refusal you put on file in Lesson 8.

> **CHECK.** One escalation on record, read, and the rule tightened if
> it did not fire. Say `next`.

---

## STEP 7 · Make it runnable, and know how to switch it off

> **RUN (Claude, in this session):** Continue `agent-forge`, STEP 8:
> write each agent's runnable definition and `records/agents/README.md`.

An agent that exists only as a markdown description is a description.
Each one gets `agent.md`, a Claude Code subagent definition with its
name, the tools it may use and its system prompt. Claude asks before
copying anything into `.claude/agents/`.

Then the README: a table of the cast, what each touches, what it only
drafts, which key it uses, and the three steps to revoke access.

Write the revoke steps now, while nothing has gone wrong. The morning
a key leaks is the wrong time to work out which agent holds it.

> **CHECK.** Each agent has a runnable definition, and
> `records/agents/README.md` tells a stranger what the cast can touch
> and how to cut it off. Say `next`.

---

## If something goes wrong

- **`INVALID` on the spec.** The message names the field.
  `escalate_when` needs at least one entry, `allowed_tools` cannot be
  empty, and `trigger.mode` must be `schedule`, `event` or `on-demand`.
- **The two replies in STEP 2 look the same.** The voice block
  summarised the brand instead of quoting it. Point it back at
  `project-knowledge.md` and ask for the real sentence shapes.
- **It escalates everything.** The rules are too broad. An agent that
  stops on all of it owns none of it.
- **It escalates nothing.** Usually a rule written as a feeling. Give
  it something countable.
- **A key is needed.** Put the NAME in `credentials` and in
  `.env.example`, and the value in your own `.env`, which is
  gitignored. Never in the spec, never in a record.
- **Everything ends up in `human_in_the_loop`.** Then the agent has no
  job. Find the routine 90 per cent it can genuinely own; if there
  isn't one, this is not an agent-shaped job.
- **The tool is not connected yet.** Set `dry_run: true`. The agent
  composes and hands back, which is a real result, not a stub.

---

## On record

- `records/agents/_voice.md`, quoted from your own files
- `records/agents/<agent_id>/spec.json`, `VALID`, one per agent
- `records/agents/<agent_id>/AGENT.md`, in your voice
- `records/agents/<agent_id>/test-log.md`, five tasks, honest results
- `records/agents/<agent_id>/agent.md`, the runnable definition
- `records/agents/README.md`, the cast and how to revoke access
- Runs on both sides: work done, and work handed back

Next: `/build:10-dashboard`. One view that reads your disk and shows
you what these agents actually did.
