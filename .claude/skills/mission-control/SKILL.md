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

Source kinds that read the disk and need nothing: `count_files`,
`count_runs`, `json_field`, `agent_runs`, `heartbeat`, `placeholder`.

Source kinds that need a key, all optional, all reading the key from
the environment by name:

| Kind | What it does | Needs |
|---|---|---|
| `http` | any JSON endpoint, optional bearer auth | `url_env`, `auth_env` |
| `youtube` | the three-call chain: channel, then search, then videos. One call cannot answer a per-video question | `key_env`, `handle` |
| `apify` | reads an actor's dataset after you have run it | `token_env`, `dataset_env` |
| `shopify` | Admin API counts, read-only scopes | `shop_env`, `token_env` |

Anything else with a documented REST endpoint goes through `http` with
its token in `auth_env`. Prefer an MCP server where one exists and the
agent already uses it.

The script labels each result `live`, `placeholder` or `missing`, and
never carries a stale number forward. **A tile whose key is absent
renders as a labelled placeholder, never as a zero**, so the free path
builds the whole dashboard and wires the numbers up later.

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
- **Blur and label any real figure** that identifies a person or an
  order: `[CUSTOMER]`, `[ORDER#]`, a masked total behind a light blur
  that lifts on hover. The screen has to be safe to record and share.
- **Empty states in the brand voice**, from `brand-guide.html`. "No
  content yet" written the way the brand writes.
- **Loading states per tile** while a connected pull is in flight.
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

### Step 6 — First look

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

### Step 7 — Optional, only if a real workflow needs it

Both are local, both are free, neither gets hosted.

**`scripts/proxy.js` — generate from the dashboard, with no API key.**
Built-in Node modules only. It serves the dashboard and accepts
`POST /generate`, piping the prompt to the Claude Code CLI the student
is already logged into.

```bash
node scripts/proxy.js
open http://localhost:3001/records/mission-control/index.html
```

Open it through that URL, not `file://`, or the page cannot reach the
proxy. Wire any generate button to it: a reply draft, an email, a
caption. Show a brand-voiced generating state, then drop the result
into an editable textarea. Anything it writes obeys the same proof
discipline as the agents: no claim, stat or testimonial that is not in
the brand files.

**A board that remembers, with no backend.** For a pipeline or kanban
page: serialise the board to a namespaced `localStorage` key
(`<brand>_pipeline_board`) after every move and restore it on load. Use
a second shared key (`<brand>_pipeline_inbox`) as the glue between
pages: one page writes an item, the pipeline page reads it on load,
injects it as a card and clears the key. That is how the pages talk to
each other without a server.

### Step 8 — Verify on brand, then capture it

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1440,2200 --virtual-time-budget=8000 \
  --screenshot=records/mission-control/preview.png \
  http://localhost:8788/records/mission-control/index.html
```

Open the PNG and check, fixing and re-capturing until each holds:

- **The fonts from `design.md` actually loaded**, rather than falling
  back to a system face. Compare a heading against the brand guide.
- **The palette is the brand's**, not a stock dashboard look.
- **The logo is visible and correctly treated.** A dark logo on a dark
  canvas needs the brand's light variant.
- **The accent is status and emphasis only**, not every border.
- **Nav and active state correct on every page**, no overlaps.
- **Every `LIVE` chip sits on a card backed by a real pull**, and
  everything else says placeholder.
- **Escalations read first** in the feed.
- **It collapses to one column** at 390 wide.

A top-anchored headless screenshot will not fire scroll-reveal motion,
so interior panels can look empty. Capture a tall window, or set the
fade-in elements visible for the shot.

**If it looks like a generic template rather than the brand, the design
system did not bind.** Go back to Step 2, fix the tokens, re-capture.

## Hard rules

- Never invent a number. Missing is missing.
- Never style outside `design.md`.
- Never put a key in the HTML, a record or the repo.
- Never ship a tile whose source is "the student said so".
- Never show a real customer, order or revenue figure unmasked.
- Never host the proxy or the board. Local only, `127.0.0.1`.
- Never let a page drift from the overview's tokens or nav.

## On record

- `records/mission-control/sources.json` and `scope.md`
- `records/mission-control/status.json`, from the script
- `index.html` plus one page per department, same tokens, same nav
- `records/mission-control/preview.png`, the full-page render you
  looked at
- `scripts/proxy.js` only if a real workflow needed it
