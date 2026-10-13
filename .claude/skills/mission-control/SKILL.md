---
name: mission-control
description: Use when the student wants one owned view of their operation — a multi-page dashboard built entirely from design.md tokens, department pages decided by their business, live and placeholder states labelled per tile, an agent activity feed, refresh with a local cache, and a render they looked at.
---

# Mission Control

You build the screen the student runs the operation from: their
numbers, their agents, their escalations, across one overview and a
page per department, styled entirely from `design.md` so it reads as a
native extension of their brand.

Two students with two brands must get two completely different-looking
dashboards out of this skill. If the result looks like a template you
have seen before, you have failed the build.

The second discipline is honesty. Every tile carries where its number
came from. A dashboard that quietly shows a made-up number is worse
than no dashboard, because it gets quoted.

## Prerequisites

- `design.md` at the repo root. Every colour, font, radius and
  treatment comes from it.
- `brand-guide.html`, for anything `design.md` leaves open: logo
  treatment, empty-state wording, the voice of labels.
- `records/agents/` with at least one spec and one run, from
  `agent-forge`. Without agents the feed ships as a labelled
  placeholder and wires up later.

## What you do

### Step 0 — Read the brand, then scope the operation

Read `design.md` in full and pull every token into your notes by name:
canvas, surfaces, text primary/secondary/tertiary, borders, the one
accent and its usage rule, radius, shadow or glow treatment, the font
families and the type scale, the motion rules. Then skim
`brand-guide.html` for whatever `design.md` leaves ambiguous.

Then read `records/agents/*/spec.json` and `test-log.md`. That is the
raw material for the feed.

Then ask, one question at a time:

1. **The departments.** Group what the student checks daily into the
   departments their business actually runs. Those groups become the
   pages. A DTC brand might be overview, performance, customers,
   agents. A service business might be overview, pipeline, delivery,
   agents. Let the business decide. Never inherit someone else's page
   set.
2. **The tiles per page.** Four to eight numbers that earn a card. Each
   one has to pass two tests: the student would act differently this
   week if it moved, and something can answer it.
3. **The source per tile.** A file on disk, a connected source, or
   nothing yet.
4. **The feed.** Which agents appear, and is their run log readable.

### Step 1 — The tile map, before any HTML

Write `records/mission-control/sources.json`, which
`scripts/mission_status.py` reads:

```json
{
  "pages": {
    "overview": [
      {"label": "Assets built", "question": "How much got made this week?",
       "source": {"kind": "count_runs", "decision": "built"}},
      {"label": "Revenue today", "question": "Did we sell?",
       "source": {"kind": "placeholder", "value": 0}}
    ],
    "agents": [
      {"label": "Support drafts", "question": "Is the cast working?",
       "source": {"kind": "agent_runs", "agent_id": "support-drafts"}}
    ]
  }
}
```

Source kinds: `count_files`, `count_runs`, `json_field`, `agent_runs`,
`http` (a JSON endpoint whose URL comes from a named env var), and
`placeholder`. The script labels each result `live`, `placeholder` or
`missing` and never carries a stale number forward.

Also write `records/mission-control/scope.md` in plain words: every
tile, the question it answers, its source, and its state. The student
reads that before the build.

```bash
python3 scripts/mission_status.py
```

It prints the live / placeholder / missing counts and names anything
missing. Fix the map until the only non-live tiles are ones you meant.

### Step 2 — Lock the design system

Before writing markup, translate `design.md` into CSS custom
properties defined once at `:root`, so the whole look is editable in
one place and every page inherits it:

```
:root{
  --canvas: …; --surface-1: …; --surface-2: …;
  --text: …; --text-muted: …; --text-dim: …;
  --border: …; --border-strong: …;
  --accent: …; --accent-soft: …;
  --good: …; --warn: …; --bad: …;   /* derived in-brand, not imported */
  --radius: …; --shadow: …;          /* the brand's treatment, not a default glow */
  --font-display: …; --font-label: …;
}
```

Rules that make it theirs:

- **Every value comes from `design.md`.** If one is not there, ask
  rather than choose.
- **One accent, used sparingly.** Status, a live dot, one emphasis.
  Never body text, never every border.
- **Treatment, not glow by default.** A dark atmospheric brand earns
  ambient depth. A light precise brand earns hairline borders and soft
  shadows. Read which one `design.md` implies.
- **Depth, never flat.** A dead background is a broken section.

### Step 3 — The overview page

Build `records/mission-control/index.html` first. Every other page
mirrors it. Inline CSS driven by the Step 2 properties, reading
`status.json` from the same folder.

- **Nav** with a link per page, the logo treated per `design.md`, and
  the active state set per page. Write this block clean; you will
  mirror it exactly.
- **Topbar** with the operation name, the date and a **Refresh**
  control.
- **Briefing line**: what matters right now, including anything an
  agent escalated. Brand voice, from `brand-guide.html`.
- **Tiles**: the big numeral in the display face, the label in the
  label face, and a state chip reading `LIVE` or `PLACEHOLDER` **in
  the tile**, never in a footnote. A `missing` tile says missing and
  shows no number at all.
- **Sparklines** where a tile is time-series: a small inline SVG
  helper taking an array. No chart library.
- **The agent feed**: newest first, from `status.json`, showing what
  each agent handled and, prominently, what it escalated. A clean
  escalation is the system working, so it reads as signal, not error.
- **Motion**: the brand's motion. A subtle staggered fade-up on cards,
  never aggressive.
- Readable at 390 wide. The student checks this from a phone first.

### Step 4 — The department pages

One page per department from Step 0, each in the same folder. Read
`index.html` first and mirror the nav markup and the `:root` block
exactly, changing only the active nav item and the content. If a page
drifts, the fix is one line: match the exact variables and nav from
`index.html`.

Keep components identical across pages: same card, same table, same
chip, same status dot. The whole thing has to read as one product.

### Step 5 — Refresh and cache

Wire the Refresh control to re-read `status.json`, show a per-tile
loading state, update every value, chip and sparkline, and write a
last-refreshed timestamp to `localStorage` along with the last payload,
so a reload shows the latest numbers instantly.

Serve it:

```bash
python3 scripts/serve_dashboard.py 8788
```

Then `http://localhost:8788/records/mission-control/index.html`.

For a tile pulling from a real endpoint, the URL comes from an env var
named in `sources.json`. Never paste a key into the HTML, a record or
this repo.

### Step 6 — Verify by looking

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --screenshot=records/mission-control/preview.png \
  --window-size=1280,1800 http://localhost:8788/records/mission-control/index.html
```

Open the PNG and check three things in this order:

- **Honesty.** Every non-live tile is labelled in the tile. Any number
  you cannot trace to a source is removed or labelled now.
- **Brand.** Hold it next to `brand-guide.pdf`. Same hexes, same type,
  same weight of thing.
- **Phone width.** Render again at 390 and read it.

Exit codes do not tell you a page is right. Looking does. Twice is
normal.

## Hard rules

- Never invent a number. Missing is missing.
- Never style outside `design.md`.
- Never put a key in the HTML, a record or the repo.
- Never ship a tile whose source is "the student said so".
- Never let a page drift from the overview's tokens or nav.

## On record

- `records/mission-control/sources.json` and `scope.md`
- `records/mission-control/status.json`, from the script
- `index.html` plus one page per department, same tokens, same nav
- `records/mission-control/preview.png`, the render you looked at
