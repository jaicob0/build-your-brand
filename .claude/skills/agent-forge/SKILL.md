---
name: agent-forge
description: Use when the student wants an agent that owns a job in their business — one shared voice file, a typed spec with an allowlist, scoped credentials, named escalations, and a batch of five real tasks tested with an honest PASS/FAIL log before it counts as built.
---

# Agent Forge

You turn a job the student does by hand into an agent that owns it:
one job, one voice, a typed spec, a written allowlist, named exceptions
that come back to a human, and a test log that reports what actually
happened.

An agent without an allowlist is a liability. An agent without an
escalation rule is a script. An agent that has never been tested on
real work is a document. None of the three ship from here.

## Prerequisites

- `records/brands/<brand_id>/` with `project-knowledge.md`,
  `necessary-beliefs.md` and `avatar-sheet.md`. The voice comes from
  the files, never from your impression of the brand.
- `design.md` at the repo root, for anything the agent produces that a
  customer will see.
- The student has named the jobs. If they have not, stop and ask. Never
  pick the jobs for them.

## What you do

### Step 1 — One job per agent

Cut each job the student named until one sentence covers it, with a
verb and an object: "drafts the reply to every support email about
delivery", not "handles support".

Three questions per job, asked one at a time:

- **Volume.** How often, honestly? Weekly or more, or it is not worth
  an agent.
- **Judgement.** Where would a good junior get this wrong? That answer
  is the escalation boundary, and every real job has one. If the
  student cannot find it, they do not know the job well enough to hand
  it over yet. Say so.
- **Worst case.** What is the worst thing this agent could do if it
  misread the situation? Refund the wrong amount, email the wrong list,
  publish something off-brand. That answer sets the allowlist and
  whether the gate is on.

Two or three agents is a good first build. Five is someone avoiding the
hard one.

### Step 2 — One voice, written once

Before any agent exists, write `records/agents/_voice.md`. Every agent
inherits this block, so they all sound like one operator rather than
three different companies:

```
# Brand voice — all agents
Persona:        [one line, from project-knowledge.md]
Sentence shapes: [2-4 real patterns, quoted from the brand files with examples]
USE:            [the word list, verbatim]
AVOID:          [the word list, verbatim]
Proof rule:     Never state a claim, stat, price or testimonial that is not in
                project-knowledge.md or deepresearch.md. These are UNVERIFIED
                and never said: [list them]
Unsure:         Ask or escalate. Never guess in the brand's name.
Never:          The AI tells — "I hope this helps", "As an AI", hype adjectives
                the AVOID list names, and em-dash salad.
```

Quote the brand files. Do not paraphrase them. A voice that is a
paraphrase of a paraphrase drifts within a week.

**The test for this step:** write the same reply twice, once through
this block and once as a generic assistant, and put them side by side
for the student. If someone who knows the brand cannot tell which is
which, the block is not finished.

### Step 3 — The spec

For each agent, write `records/agents/<agent_id>/spec.json` against
`schema/agent_spec.schema.json`. Typed JSON, because scripts read it
and enforce it.

Fill these from the student's own answers:

- `job` — the Step 1 sentence.
- `owns` — the concrete steps, end to end.
- `reads` — every path or source it may read. Anything absent is out of
  scope, and that is the point.
- `writes` — one directory. One agent, one output location.
- `voice_source` — the brand file behind `_voice.md`.
- `allowed_tools` — the allowlist. Name tools and commands. Never `*`,
  never "anything it needs".
- `human_in_the_loop` — the actions it may **draft but never execute
  alone**: anything irreversible, anything that moves money, anything
  that carries reputation risk. This is the 90/10 line. The agent runs
  the safe, well-trodden 90 per cent by itself and hands the rest over
  with the work already done. The runner refuses these and routes them
  to a person, so getting this list right is what lets the agent be
  useful without being dangerous.
- `forbidden` — what it refuses outright, even when asked directly.
  Different from the list above: forbidden is never drafted at all.
- `mcp` — the MCP servers this agent may reach, by name, and only ones
  it has been tested against. An unvetted server is an unlocked door.
- `escalate_when` — the Step 1 judgement answer, written as signals a
  script could check: an amount, a word in a subject line, a missing
  field. At least one.
- `gate` — `required: true` the moment an action spends money, sends
  outside, publishes or deletes.
- `credentials` — environment variable NAMES only, one scoped key per
  agent, read-only wherever the job allows, so one can be revoked
  without touching the others. Never a value. Add the names to
  `.env.example` with a comment, never to a record.
- `trigger` — `schedule` with a cadence in minutes, `event` with what
  fires it, or `on-demand` for anything that should only ever run when
  a human asks. Lesson 11 refuses to put an on-demand agent on a timer.
- `dry_run` — `true` while its tools are not connected. It composes the
  action and hands it to a human instead of performing it. This is the
  honest default for anything touching a live account.
- `acceptance` — at least two checks a human can answer pass or fail
  on. "Reads well" is not a check. "Quotes the order number from the
  thread" is.

Then:

```bash
python3 scripts/validate_brief.py records/agents/<agent_id>/spec.json
```

`VALID`, or it doesn't move. Show the student the spec and let them
read it before anything is built from it.

### Step 4 — Connect the tools, scoped down

Wire only what one workflow needs, nothing more.

- **Prefer MCP** for real tools: a store, an email platform, a
  helpdesk, a calendar. Configure the server, confirm it
  authenticates, and name in `allowed_tools` the exact calls the agent
  may make. Name the server in `mcp`.
- **Scope the permission to the minimum.** A support agent reads
  orders and drafts replies; it does not get write access to the
  storefront. Read-only wherever the job allows.
- **One key per agent**, so revoking one does not touch the others.
- **The access paradox, said out loud in the spec:** the more an agent
  can do, the longer its `human_in_the_loop` list has to be. Power and
  guardrails scale together. Never grant a capability just in case.
- **Not connected yet?** `dry_run: true`. It composes the action and
  hands it over. That is a real result, not a stub, and it is the
  honest state for anything touching a live account on day one.

### Step 5 — The agent file

Write `records/agents/<agent_id>/AGENT.md`: the spec in the brand's
voice, in the order the agent reads it.

```
# <Agent name> — <job sentence>

## What I own
[owns, as steps]

## What I read
[reads, as paths]

## How I sound
[the whole _voice.md block, inlined]

## What I will not do
[forbidden, as flat statements]

## When I stop and come to you
[escalate_when, each with the signal that triggers it]

## Done means
[acceptance, as a checklist]
```

### Step 6 — Five real tasks, logged honestly

Five tasks per agent, drawn from the student's actual recent work, and
at least two of them the edge cases from Step 1. Not invented test
cases. Append each to `records/agents/<agent_id>/test-log.md`:

```
## Test N — <the real task>
Expected:   [what a good operator would do]
Agent did:  [its actual output, pasted]
Voice:      PASS | FAIL
Accuracy:   PASS | FAIL
Escalated:  yes | no — and was that the right call?
Notes:      [what to tune]
```

Also write each run to `records/agents/<agent_id>/runs/<timestamp>.json`
so Mission Control and the dashboard can read it:

```json
{"agent_id": "...", "ran_at": "ISO 8601", "task": "...",
 "output_path": "...", "acceptance": [{"check": "...", "result": "pass"}],
 "escalated": false, "notes": "..."}
```

Then report per agent: accuracy over the batch ("7 of 8"), which cases
it escalated, and whether each escalation was correct. **An agent that
correctly escalates a hard case is passing, not failing.**

Honesty is not optional. Never round a wrong answer up to close enough,
never write a PASS you did not see. A tuned agent with an honest log is
worth more than a perfect one nobody can trust. Mask real customer data
in the log — `[CUSTOMER]`, `[ORDER#]`, `[EMAIL]` — so it is safe to
share or screen-record.

### Step 7 — Make one stop, then tune

Give each agent a task that trips one of its own `escalate_when` rules.
It stops, says why, and hands back. If it has a go anyway, the rule is
written as a feeling rather than a signal: tighten it and run again.

Loop Steps 6 and 7 until the student would let it run unsupervised on
the routine work and not a moment before. Tighten any allowlist that
let something risky through. Loosen any rule crying wolf on safe cases.

### Step 8 — Make it runnable, and write down how to switch it off

An agent that only exists as a markdown file is a description. Give
each one a runnable definition the student can invoke by name:

- **A Claude Code subagent** is the default. Write
  `records/agents/<agent_id>/agent.md` with `name`, `description`, the
  `tools` it is allowed, and the system prompt: role, the `_voice.md`
  block, then the guardrails. Offer to copy it into `.claude/agents/`
  so it is invokable in this project. Ask before copying.
- **A skill** instead, if the workflow is a procedure invoked by name.
- **A script**, only when the work is genuinely deterministic.

Keep it framework-light: Claude Code subagents or skills plus MCP. No
heavy agent framework, nothing that ties the build to one vendor. The
artifact should still make sense if the brand swaps helpdesk next year.

Then write `records/agents/README.md`, which is the page a stranger
reads to understand the cast:

```
# The cast

| Agent | Job | Runs | Touches | Drafts only | Key |
|---|---|---|---|---|---|
| <id> | <job sentence> | schedule 60m | <reads/writes> | <hitl list> | <ENV NAME> |

## How to run one
python3 scripts/hermes_run.py <agent_id> --task "..."       # check, runs nothing
python3 scripts/hermes_run.py <agent_id> --task "..." --go   # run it

## How to revoke access
1. Remove the tool from records/ops/allowlist.json and rebuild.
2. Revoke the key at the provider, then clear it from .env.
3. Run the agent in check mode and confirm it now refuses.
```

## Hard rules

- Never give an agent a tool, or an MCP server, the student has not
  approved by name.
- Never put an irreversible, money-moving or reputation-risking action
  in `allowed_tools`. It belongs in `human_in_the_loop` or `forbidden`.
- Never write a credential value anywhere. Names only, in the spec and
  in `.env.example`.
- Never run an agent against a live account, inbox or store in this
  lesson. Real tasks, local outputs, `dry_run: true` where a tool is
  not connected.
- Never invent the brand's voice. Quote the files.
- Never fake a PASS.
- If the student asks for an agent that spends money, `gate.required`
  is `true` and `scripts/approval_gate.py` runs before the spend, the
  same gate Lesson 8 uses.

## On record

- `records/agents/_voice.md`, quoted from the brand files
- `records/agents/<agent_id>/spec.json`, `VALID`
- `records/agents/<agent_id>/AGENT.md`
- `records/agents/<agent_id>/test-log.md`, five tasks, honest results
- `records/agents/<agent_id>/agent.md`, the runnable definition
- `records/agents/<agent_id>/runs/`, including one escalation
- `records/agents/README.md`, including how to revoke access
