---
description: "Build Your Brand, Lesson 10: Mission Control. One owned view, built from design.md, reading real files, with every number that isn't live labelled as such."
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
About twenty-five minutes. You leave with a dashboard in your own brand that reads your disk, and a screenshot you have actually looked at.

---

## The course dashboard, and yours

You already have one dashboard: `dashboard.html`, the course progress
board that reads `records/` and tells you which lessons are genuinely
done. It is deliberately plain, and it is not yours.

This lesson builds the one that is. Same principle, your brand: it
reads files on your disk and reports what it finds. Your agents, what
they did, what they stopped on, and the handful of numbers you would
actually change your week over.

The rule that makes it worth keeping open: **every number has a source
on disk, or it is labelled a placeholder, in the tile, where you can
see it.** A dashboard that quietly carries a made-up number is worse
than no dashboard, because you will quote it.

---

## STEP 1 · Decide what earns a tile

List what you check, or wish you could check, every day. Then cut it
with two questions:

- Would you do something differently this week if this moved?
- Is there a file, or a source you can actually reach, that answers it?

No to the first is noise. No to the second is a placeholder, clearly
marked, wired later. The agent feed is already live, because
`records/agents/*/runs/` is on your disk from Lesson 9.

A board that shows everything shows nothing. Six tiles you read is
better than twenty you scroll past.

> **CHECK.** Your tile list, each with the file or source behind it.
> Say `next`.

---

## STEP 2 · Build it from your own tokens

> **RUN (Claude, in this session):** Use `mission-control` for the tiles
> from STEP 1.

It writes `records/mission-control/scope.md` first: every tile, its
question, its source, live or placeholder. Read that before the build.

Then it writes `scripts/mission_status.py`, which walks `records/` and
emits the numbers, and `records/mission-control/index.html`, styled
from `design.md`. Not a template, not a palette it liked better. Your
hexes, your fonts, your spacing, the same ones the site and the brand
guide use. If it cannot find a value in `design.md`, it asks you rather
than choosing.

Serve it:

```bash
python3 scripts/serve_dashboard.py 8788
```

Then open `http://localhost:8788/records/mission-control/index.html`.

> **CHECK.** It opens, it shows your tiles, and the agent feed lists the
> runs that are really in `records/agents/`. Say `next`.

---

## STEP 3 · Look at it, token by token

Exit codes do not tell you a page is right. Looking does.

Claude renders `records/mission-control/preview.png` and you open it.
Check three things, in this order:

- **Honesty.** Every placeholder says so, in the tile. Any number you
  cannot trace to a file gets removed or labelled, now.
- **Brand.** Hold it next to `brand-guide.pdf`. Same hexes, same type,
  same weight of thing. A dashboard that looks like someone else's SaaS
  is a brand leak you will see every morning.
- **Phone width.** You will check this from your phone first. If it does
  not read at 390 wide, it does not count as built.

Fix and render again. Twice is normal.

> **CHECK.** Preview opened and looked at, placeholders labelled, brand
> matches, phone width reads. Say `next`.

---

## If something goes wrong

- **Empty tiles everywhere.** `mission_status.py` is looking in the
  wrong folders. Run it directly and read what it prints before
  touching the HTML.
- **A number appears with no source.** That is the defect this lesson
  exists to catch. Delete it or label it, do not keep it because it
  looks good.
- **Colours drift from the brand guide.** The build approximated
  `design.md` instead of reading it. Point it back at the file and have
  it pull the exact values.
- **The screenshot command fails.** Chrome is not at the standard path,
  the same check as Lesson 1. Serve the page and screenshot it by hand
  rather than skipping the look.
- **The agent feed is empty but runs exist.** It is reading
  `records/agents/*/runs/*.json`. Open one and check the shape matches
  what Lesson 9 wrote.

---

## On record

- `records/mission-control/scope.md`, every tile with its source named
- `scripts/mission_status.py`, reading the disk, guessing nothing
- `records/mission-control/index.html`, in your tokens
- `records/mission-control/preview.png`, the render you looked at

Next: `/build:11-hermes`. The agents and this view, tied into one layer
that runs without you, and stops when you tell it to.
