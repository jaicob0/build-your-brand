---
description: "Build Your Brand, Lesson 10: Mission Control. A multi-page dashboard in your own tokens, every tile labelled live or placeholder, the agent feed, refresh and cache, verified by looking."
---

# /build:10-dashboard

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 10 OF 13 · MISSION CONTROL**
About thirty-five minutes. You leave with an overview and a page per department, in your own brand, and a screenshot you have actually looked at.

---

## The course dashboard, and yours

You already have one dashboard: `dashboard.html`, the course progress
board that reads `records/` and tells you which lessons are genuinely
done. It is deliberately plain, and it is not yours.

This lesson builds the one that is. Your departments, your numbers,
your agents, in your tokens.

Two rules carry the whole build:

**It renders in your brand.** Every colour, font, radius and treatment
comes from `design.md`. Two people running this lesson on two brands
end up with two dashboards that look nothing alike. If yours looks like
a template, it is wrong.

**Every number says where it came from.** `LIVE`, `PLACEHOLDER` or
missing, labelled in the tile, not in a footnote. A dashboard that
quietly carries a made-up number is worse than no dashboard, because
you will quote it in a meeting.

---

## STEP 1 · Departments, then tiles

List what you check, or wish you could check, daily. Group it into the
departments your business actually runs. Those groups become your
pages: maybe overview, performance, customers, agents. Maybe overview,
pipeline, delivery, agents. Yours, not a template's.

Then cut each tile with two questions:

- Would you do something differently this week if it moved?
- Can anything answer it: a file, or a source you can reach?

No to the first is noise. No to the second is a placeholder, labelled,
wired later. Four to eight tiles a page. A page that shows everything
shows nothing.

> **CHECK.** Your page map: each department, its tiles, and the source
> behind each one. Say `next`.

---

## STEP 2 · The tile map, before any HTML

> **RUN (Claude, in this session):** Use `mission-control`, STEP 1:
> write `records/mission-control/sources.json` and `scope.md` from my
> page map.

Then read the numbers before anything renders them:

```bash
python3 scripts/mission_status.py
```

It prints how many tiles are live, how many are placeholders and how
many are **missing**, and names every missing one. Missing means you
pointed at a file that is not there. Fix the map until the only
non-live tiles are the ones you meant.

The agent feed is already live: it reads `records/agents/*/runs/` from
Lesson 9 and the unattended runs from Lesson 11 once they exist.

> **CHECK.** `mission_status.py` runs, and you recognise every
> placeholder in the list. Say `next`.

---

## STEP 3 · Build it from your own tokens

> **RUN (Claude, in this session):** Continue `mission-control`, STEP 2
> to STEP 5: lock the design system from `design.md`, build the
> overview, mirror it into the department pages, wire refresh and the
> cache.

The overview carries the briefing line, the tiles with their state
chips, sparklines where a tile is time-series, and the agent feed with
escalations shown prominently. Every department page mirrors the same
`:root` block and the same nav, changing only the active item and the
content, so the whole thing reads as one product rather than four.

```bash
python3 scripts/serve_dashboard.py 8788
```

Then `http://localhost:8788/records/mission-control/index.html`.

If a tile pulls from a real endpoint, its URL comes from an env var
named in `sources.json`, and the value lives in your `.env`, which is
gitignored. No key goes in the HTML.

> **CHECK.** Overview and every department page open, nav works, the
> feed lists runs that are really in `records/agents/`. Say `next`.

---

## STEP 4 · Look at it, token by token

Exit codes do not tell you a page is right. Looking does.

Claude renders `records/mission-control/preview.png`. Open it and check
three things in this order:

- **Honesty.** Every non-live tile is labelled in the tile. Any number
  you cannot trace gets removed or labelled, now.
- **Brand.** Hold it next to `brand-guide.pdf`. Same hexes, same type,
  same weight of thing. A dashboard that looks like someone else's SaaS
  is a brand leak you see every morning.
- **Phone width.** Render again at 390 wide. You check this from your
  phone first.

Fix and render again. Twice is normal.

> **CHECK.** Preview opened and looked at, placeholders labelled, brand
> matches, phone width reads. Say `next`.

---

## If something goes wrong

- **Tiles say `missing`.** That is the script doing its job. The note
  names the path it could not find. Fix `sources.json`, not the HTML.
- **A number appears with no source.** That is the defect this lesson
  exists to catch. Delete it or label it; never keep it because it
  looks good.
- **Colours drift from the brand guide.** The build approximated
  `design.md` instead of reading it. Point it back at the file and ask
  for the exact values.
- **Pages look like four different products.** One line fixes it: match
  the exact `:root` block and nav markup from `index.html`.
- **The screenshot command fails.** Chrome is not at the standard path,
  the same check as Lesson 1. Serve the page and screenshot by hand
  rather than skipping the look.
- **The feed is empty but runs exist.** It reads
  `records/agents/*/runs/*.json`. Open one and check the shape matches
  what Lesson 9 wrote.

---

## On record

- `records/mission-control/sources.json` and `scope.md`, every tile
  with its source named
- `records/mission-control/status.json`, from the script, labelled
- `index.html` plus a page per department, same tokens, same nav
- `records/mission-control/preview.png`, the render you looked at

Next: `/build:11-hermes`. The agents and this view, tied into one layer
that runs without you, and stops when you tell it to.
