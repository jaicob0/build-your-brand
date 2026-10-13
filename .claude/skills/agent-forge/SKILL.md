---
name: agent-forge
description: Use when the student wants an agent that owns a job in their business — a typed spec with an allowlist, named escalations and acceptance checks, an AGENT.md written in the brand voice, and one real task run end to end before it counts as built.
---

# Agent Forge

You turn a job the student does by hand into an agent that owns it:
one job, a typed spec, a written allowlist, named exceptions that come
back to the human, and a dated record of the first real run.

An agent without an allowlist is a liability. An agent without an
escalation rule is a script. Neither ships from here.

## Prerequisites

- `records/brands/<brand_id>/` with `project-knowledge.md` and
  `necessary-beliefs.md`. The voice comes from the files, never from
  your impression of the brand.
- `design.md` at the repo root, for anything the agent produces that
  a customer will see.
- The student has named the jobs. If they have not, stop and ask. Never
  pick the jobs for them.

## What you do

### Step 1 — One job per agent

Take each job the student named and cut it down until one sentence
covers it, with a verb and an object: "drafts the reply to every
support email about delivery", not "handles support".

Two tests before you write anything:

- **The volume test.** They do it at least weekly. A job done twice a
  year is not worth an agent.
- **The judgement test.** Name the part that needs a human. Every real
  job has one. If you cannot find it, you have not understood the job
  yet, so ask rather than invent.

A job that fails the volume test gets said out loud and dropped. Two or
three agents is a good first build. Five is someone avoiding the hard
one.

### Step 2 — The spec

For each agent, write `records/agents/<agent_id>/spec.json` against
`schema/agent_spec.schema.json`. Typed JSON, not prose, because the
next skill reads it directly.

Fill these honestly, from the student's answers:

- `job` — the Step 1 sentence.
- `owns` — the concrete steps it performs end to end.
- `reads` — every path or source it may read. Anything absent is out
  of scope, and that is the point.
- `writes` — one directory. One agent, one output location.
- `voice_source` — the brand file that fixes its voice.
- `allowed_tools` — the allowlist. Name the tools and commands it may
  use. Never write `*`, never write "anything it needs".
- `forbidden` — what it must refuse even when asked directly. Sending
  outside, spending, publishing and deleting belong here unless the
  gate covers them.
- `escalate_when` — the exceptions that stop it and come to the human.
  At least one. This is the judgement test from Step 1, written down.
- `gate` — `required: true` the moment an action spends money, sends
  outside, publishes or deletes.
- `acceptance` — at least two checks a human can run on a finished
  output and answer pass or fail. "Reads well" is not a check. "Quotes
  the customer's own words from the thread" is.

Then:

```bash
python3 scripts/validate_brief.py records/agents/<agent_id>/spec.json
```

`VALID`, or it doesn't move. Show the student the spec and let them
read it before you build anything from it. A vague `escalate_when` is
the defect that reaches production as an agent doing something nobody
sanctioned.

### Step 3 — The agent file

Write `records/agents/<agent_id>/AGENT.md`: the spec in the brand's
own voice, in the order the agent reads it.

```
# <Agent name> — <job sentence>

## What I own
[the owns list, as steps]

## What I read
[the reads list, as paths]

## How I sound
[voice rules lifted from project-knowledge.md: USE and AVOID, verbatim.
 Never paraphrase the brand voice into your own.]

## What I will not do
[forbidden, as flat statements]

## When I stop and come to you
[escalate_when, each one with the signal that triggers it]

## Done means
[acceptance, as a checklist]
```

Voice rules are quoted from the brand files, not summarised. An agent
drifts the moment its voice is a paraphrase of a paraphrase.

### Step 4 — One real task, on record

An agent that has never run is a document. Run each one on a real task
the student supplies, in this session, and write the result to
`records/agents/<agent_id>/runs/<timestamp>.json`:

```json
{
  "agent_id": "...",
  "ran_at": "ISO 8601",
  "task": "the real task, in the student's words",
  "output_path": "where the output landed",
  "acceptance": [{"check": "...", "result": "pass|fail"}],
  "escalated": false,
  "notes": "what you would tighten"
}
```

Then make it fail on purpose: give it a task that trips one
`escalate_when` rule, and confirm it stops and hands back rather than
guessing. Record that run too, with `"escalated": true`.

An agent that never escalates in testing has an escalation rule nobody
has proven. Both runs stay on file.

## Hard rules

- Never give an agent a tool the student has not approved by name.
- Never write a spec with an empty or hand-waved `escalate_when`.
- Never run an agent against a live account, inbox or store in this
  lesson. Real tasks, local outputs. Connecting an agent to a live
  account is the student's decision, made later, with the gate in
  front of it.
- Never invent the brand's voice. Quote the files.
- If the student asks for an agent that spends money, `gate.required`
  is `true` and `scripts/approval_gate.py` runs before the spend, the
  same gate Lesson 8 uses.

## On record

- `records/agents/<agent_id>/spec.json`, `VALID`
- `records/agents/<agent_id>/AGENT.md`, in the brand voice
- At least two runs in `records/agents/<agent_id>/runs/`: one that did
  the work, one that stopped and escalated
