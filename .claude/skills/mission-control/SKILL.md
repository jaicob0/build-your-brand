---
name: mission-control
description: Use when the student wants one owned view of their operation — a dashboard built from design.md that reads real files on their disk, shows what each agent did and what it escalated, and labels every number that isn't live.
---

# Mission Control

You build the dashboard the student owns: their numbers, their agents,
their escalations, in one view, styled from `design.md` so it looks
like their brand rather than a template.

It reads files. It does not ask to be told what happened. A dashboard
that reports what it was told is a slide, and a slide can be wrong for
a week before anyone notices.

## Prerequisites

- `design.md` at the repo root. Every colour, font and treatment comes
  from it. No new palette, no borrowed template.
- `records/agents/` with at least one agent spec and one run, from
  `agent-forge`. Without agents there is nothing live to show.
- `records/brands/<brand_id>/project-knowledge.md` for the wording.

## What you do

### Step 1 — Decide what earns a tile

Ask the student what they check, or wish they could check, daily. Then
cut it. Each tile has to pass:

- They would act differently this week if the number moved.
- Something on disk, or a source they can actually reach, can answer
  it.

Anything that fails the first is noise. Anything that fails the second
goes on the board as a clearly labelled placeholder, never as a number
that looks real.

Write the list to `records/mission-control/scope.md`: every tile, the
question it answers, the file or source behind it, and whether it is
live or placeholder. The student reads this before you build.

### Step 2 — The reader

Write `scripts/mission_status.py`, modelled on
`scripts/dashboard_status.py`: it walks `records/` and emits
`records/mission-control/status.json`. One function per tile, each
returning a value and a `source` field of `"live"` or `"placeholder"`.

It reads the disk and nothing else. No network call, no key, no
account, unless the student has supplied a source and asked for it
explicitly. The agent feed comes from `records/agents/*/runs/*.json`:
what ran, what it produced, what it escalated, newest first.

If a file is missing, the tile reports missing. It never guesses a
number, and it never carries forward yesterday's.

### Step 3 — Build the view

Write `records/mission-control/index.html`, one self-contained file,
reading `status.json` next to it.

- Every colour, font, radius and spacing value comes from `design.md`.
  Pull the tokens; do not approximate them from memory.
- A header, a row of tiles, and the agent feed under them: what each
  agent did, when, and whether it escalated.
- Anything not live carries a visible `placeholder` label in the tile
  itself, not in a footnote. A number without a source label is a lie
  waiting to be quoted.
- Readable at phone width. The student will check it from their phone
  before they check it from a desk.
- No build step, no framework, no CDN beyond the fonts `design.md`
  already names.

Serve it the way the course already serves a dashboard:

```bash
python3 scripts/serve_dashboard.py 8788
```

### Step 4 — Verify by looking

Render it and look at it, do not assume it:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --screenshot=records/mission-control/preview.png \
  --window-size=1200,1600 http://localhost:8788/records/mission-control/index.html
```

Open the PNG. Check it against `design.md` token by token: the
hexes, the type, the spacing. Check that every placeholder is labelled.
Check that the agent feed shows the runs that are genuinely in
`records/agents/`. Fix what is wrong and render again.

A clean exit code is not evidence the page is right. Looking at it is.

## Hard rules

- Never invent a number. Missing is missing.
- Never style outside `design.md`. If a value is not there, ask the
  student rather than choosing.
- Never connect a live account or paste a key into the HTML. Sources
  that need credentials get wired later, through the student's own
  environment, never committed.
- Never ship a tile whose source is "the student told me".

## On record

- `records/mission-control/scope.md`, every tile with its source
- `scripts/mission_status.py`, reading the disk
- `records/mission-control/index.html`, built from `design.md`
- `records/mission-control/preview.png`, the render you actually looked
  at
