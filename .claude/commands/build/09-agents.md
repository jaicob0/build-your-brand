---
description: "Build Your Brand, Lesson 9: The cast. Agents that own a job, with an allowlist, named escalations, and one refusal proved on record."
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
About twenty-five minutes. You leave with two or three agents that own a named job, and one that stopped and handed the work back, on record.

---

## A brand is how you are seen. Agents are how the work gets done

You have used two agents already. Aphrodite decided and Hephaestus
built, and a typed brief passed between them. That shape is not
specific to images. It is what an agent is: one job, written down, with
an allowlist in front of it and a human at the part that needs
judgement.

This lesson runs that shape on the work that eats your week.

The thing that makes it an agent rather than a prompt you keep retyping
is the part most people skip: the list of what it must not do, and the
list of what it stops for. We write both before anything runs.

---

## STEP 1 · Name the jobs, cut them down

Pick two or three jobs you do by hand every week. Say them out loud as
one sentence each, with a verb and an object.

"Handles support" is a department. "Drafts the reply to every email
asking where an order is" is a job. The second one can be owned. The
first one cannot.

For each, name the part that needs you. Every real job has one: the
refund that is bigger than the rule, the reply that is actually a
complaint, the invoice that does not match. That part is not a failure
of the agent. It is the reason you can let the rest run.

> **CHECK.** Two or three jobs, one sentence each, each with the part
> that needs you named. Say `next`.

---

## STEP 2 · The spec, typed

> **RUN (Claude, in this session):** Use `agent-forge` on the jobs from
> STEP 1.

It writes `records/agents/<agent_id>/spec.json` for each: the job, what
it owns, what it may read, the one directory it writes to, the voice
file it speaks from, the allowlist, what it is forbidden from doing,
and what it stops for.

```bash
python3 scripts/validate_brief.py records/agents/<agent_id>/spec.json
```

`VALID`, or it doesn't move.

Then read it as the agent would. Two fields decide whether this is safe
to own: `allowed_tools` and `escalate_when`. An allowlist with
"anything it needs" in it is not an allowlist. An escalation rule that
says "if something seems wrong" has not been thought about yet, and it
will not fire when it matters.

The `writes` field is one directory on purpose. An agent that can write
anywhere is an agent you cannot audit.

> **CHECK.** Every spec `VALID`, read with your own eyes, allowlist and
> escalations specific enough to argue with. Say `next`.

---

## STEP 3 · The agent, in your voice

> **RUN (Claude, in this session):** Continue `agent-forge` to STEP 3
> and STEP 4: write each `AGENT.md`, then run each agent on a real task
> I give you.

`records/agents/<agent_id>/AGENT.md` is the spec written in your brand
voice, quoted from `project-knowledge.md` rather than summarised. The
voice is the same one on the site. A support reply that sounds like a
different company is a brand defect, not a support defect.

Give it a real task. Not a test case you invented, something off your
actual week. Read the output against the `acceptance` checks in the
spec and answer pass or fail on each.

> **CHECK.** Each agent has an `AGENT.md` and at least one real run in
> `records/agents/<agent_id>/runs/`. Say `next`.

---

## STEP 4 · Make one stop on purpose

Give an agent a task that trips one of its own `escalate_when` rules.
The refund over the limit. The email that is actually a complaint.

It should stop, say why, and hand the work back. If it has a go at it
anyway, the rule is written too loosely, and that is worth knowing now
rather than at three in the morning. Tighten it and run it again.

The run gets recorded with `"escalated": true`, next to the one that
worked.

An agent with no refusal on record has guardrails nobody has tested.
Same principle as the refusal you put on file in Lesson 8: the record
only means something because it holds both.

> **CHECK.** One escalation on record, read, and the rule tightened if
> it did not fire. Say `next`.

---

## If something goes wrong

- **`INVALID` on the spec.** The message names the field. `escalate_when`
  needs at least one entry and `allowed_tools` cannot be empty, both on
  purpose.
- **The agent sounds generic.** Its `voice_source` is wrong or the
  AGENT.md paraphrased the voice rules instead of quoting them. Point it
  at `records/brands/<brand_id>/project-knowledge.md` and rebuild the
  file.
- **It escalates everything.** The rules are too broad. An agent that
  stops on all of it owns none of it.
- **It escalates nothing.** Usually a rule written as a feeling rather
  than a signal. Give it something countable: an amount, a word in the
  subject line, a missing field.
- **You cannot name the part that needs you.** Then you do not know the
  job well enough yet to hand it over. Do it by hand once more this
  week and watch for where you hesitate.

---

## On record

- `records/agents/<agent_id>/spec.json`, `VALID`, one per agent
- `records/agents/<agent_id>/AGENT.md`, in your voice, quoted from your
  own files
- Runs on both sides: work done, and work handed back

Next: `/build:10-dashboard`. One view that reads your disk and shows
you what these agents actually did.
