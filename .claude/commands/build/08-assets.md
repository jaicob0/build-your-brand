---
description: "Build Your Brand, Lesson 8: The gate. A typed brief, a gated build, one real asset, and one refusal on purpose."
---

# /build:08-assets

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 8 OF 10 · THE GATE**
About fifteen minutes. You leave with one real asset and one refusal, both on record.

---

## Two jobs, two agents, one contract between them

Deciding what should exist is Aphrodite's job. Building it is
Hephaestus's. A typed brief passes between them, and Aphrodite never
names a tool or a model. If she does, the brief is wrong. Stop and fix
it before anything else.

---

## STEP 1 · One line, one brief

Think of one line: a product, a scene, a concept.

> **RUN (Claude, in this session):** Use `aphrodite-direction` to write
> a creative brief for: `<your one-liner>`.

It reads your foundation and folds positioning, audience, tone, visual
pillars and the avoid list into the brief on its own.

Open `records/briefs/<brief_id>.json`. It's typed JSON, not prose.
Every field is a slot the next skill reads directly, so a vague
`placement` or a missing `must_preserve` becomes a production defect
the moment it reaches the build.

The bar: read it as the image model would. If any field could produce
two different images, tighten it now. "A premium scene" is empty.
"Deep green #1E3A2F background, cream product, soft morning side-light,
no people" is a slot the model can fill exactly. A vague brief costs a
minute here and a wasted generation at the gate.

```bash
python3 scripts/validate_brief.py records/briefs/<brief_id>.json
```

`VALID`, or it doesn't move.

> **CHECK.** Brief written, read, `VALID`. Say `next`.

---

## STEP 2 · Build through the gate, then ChatGPT

> **RUN (Claude, in this session):** Use `hephaestus-production` on
> `records/briefs/<brief_id>.json`.

Two keystrokes, neither of them Claude's. Claude shows you the brief
and asks `Approve build? [y/N]`; you answer here. Then Claude Code's
permission dialog shows the exact gate command with your answer in it,
and you allow it. Prefer your own terminal? Run
`python3 scripts/approval_gate.py records/briefs/<brief_id>.json`
there and answer the prompt. Same gate, same record.

On `y`, the gate prints a paste-ready prompt. Paste it into ChatGPT,
generate (free), download the result, save it as
`records/assets/inbox/<brief_id>.png`, then run
`python3 scripts/collect_asset.py records/briefs/<brief_id>.json`.
The file lands in `records/assets/`, the dated record in
`records/runs/`. (Have a Higgsfield account? Say `pro` at the gate and
it builds automatically — real credits — instead of the ChatGPT step.)

Then judge it hard. Does it keep every `must_preserve`? Does it break
any `forbidden`? Zoom in. A clean exit isn't proof the image is right;
you are the proof step. A broken rule means a tighter brief and a
regeneration, and both attempts stay on record.

One honest note: this lesson lets the image model render your headline
so you can see how it does. Lesson 10 does it the production way, a
text-free plate with type laid over it afterwards, because image
models garble text often enough that ads can't depend on it.

> **CHECK.** Brief read, `y` given, dialog allowed, prompt pasted into
> ChatGPT, file collected, asset opened and inspected. Say `next`.

---

## STEP 3 · Refuse one on purpose

Run STEP 2 again with any brief and answer anything but `y`. No
account needed; a refusal spends nothing. Open the record in
`records/runs/`. The refusal is on file, dated, with no asset produced
and nothing generated.

A record that only holds the wins is a highlight reel. The refusals
are what make it a record.

> **CHECK.** One refusal on file in `records/runs/`. Say `next`.

---

## If something goes wrong

- **ChatGPT daily limit hit.** Free tiers cap generations per day.
  Nothing is lost — the brief and your approval are on record; finish
  tomorrow where you left off.
- **Pro engine trouble (if you chose Higgsfield).** Auth error:
  `higgsfield auth login`, re-run. Rate limit: wait a minute. Out of
  credits: top up at higgsfield.ai, or drop back to the free path —
  the same brief works on either.
- **The download won't save as PNG/MP4.** `collect_asset.py` checks
  the file's real type, not its name. Save the original export; don't
  rename another file to match.
- **Content filter.** Usually a false positive on a brand name.
  Re-run `aphrodite-direction` without the specific name.

A raw Python traceback instead of a clean message is a real bug. Dig
in rather than retrying.

---

## On record

- One real asset in `records/assets/`, traceable from brief to gate to
  build
- One refusal in `records/runs/`, dated
- The pattern: decision split from execution, a typed contract between
  them, a human at the step that costs money, a record either way

Next: `/build:09-done`. Look at everything you built, and the pattern
underneath it.
