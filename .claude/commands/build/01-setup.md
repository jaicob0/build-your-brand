---
description: "Build Your Brand, Lesson 1: The toolchain. Confirm the tools and the skills, open the dashboard."
---

# /build:01-setup

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 1 OF 10 · THE TOOLCHAIN**
About five minutes. You leave with the tools confirmed, nine skills visible, and a dashboard that reads your disk.

---

## What this is

One assistant and forty tabs is how most people use AI. Nothing
remembers, nothing is recorded, and every job starts from zero.

This course builds the other thing, on your own machine: agents with
fixed jobs, a gate that needs your keystroke before anything spends
money, and a dated record of every decision, including the ones you
refused. You practise on a brand because a brand is a whole business
in miniature: evidence, a contract, a design system, a book, a face,
a storefront, a factory.

By the end of Lesson 9, all from an empty folder:

- A researched brand foundation: nine files, including a copywriter
  prompt you can paste into any assistant
- A `design.md`: exact colours, fonts and voice, chosen from real
  options
- A visual brand book, HTML and PDF, with every rule shown rather
  than described
- A hero still, and a video if you choose to spend the time on it, both
  through the gate
- A one-page site with nothing on it you can't back
- One finished asset and one refusal, both on record

Lesson 10 adds the engines: ads, email and content that read the same
foundation.

This free run is one function of a larger build. The Creative
Architect course puts the same owners, gates and records on your whole
business. That comes after. First, the brand.

| # | Lesson | Time |
|---|---|---|
| 1 | The toolchain | 5 min |
| 2 | The evidence: interview and research | 35 min |
| 3 | The contract: validate and own the foundation | 10 min |
| 4 | The tokens: `design.md` | 10 min |
| 5 | The book: visual brand guide | 15 min |
| 6 | The face: hero through the gate | 20 min |
| 7 | The storefront: the site | 20 min |
| 8 | The gate: brief, build, refuse | 15 min |
| 9 | The record: review and ship | 10 min |
| 10 | The engines: ads, email, content | 30 to 45 min |

Everything lands as files you can open, diff and audit. Nothing lives
in a chat you'll never scroll back to.

**What you need:** a Mac, Claude Code logged in on a Claude
subscription (Pro works; Max is safer for Lesson 2's research), Python
3, Google Chrome, a free ChatGPT account, and about three hours. No
design tools, no API keys, no paid image or video accounts.

Image and video generation in Lessons 6, 8 and 10 run on the **free
path**: the gate prints a paste-ready prompt, you generate in ChatGPT
(free) — ChatGPT for images, ChatGPT/Sora for video — download the
result, and drop it in the repo. Free tiers have daily limits; if you
hit one, the lesson picks up where it left off the next day.

---

## STEP 1 · Confirm the toolchain

You're inside Claude Code, so that check is done. Two more, in a
second terminal:

```bash
python3 --version
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
```

Both print a version. Chrome renders the brand guide PDF and the
Lesson 10 assets; if it isn't at that path, install it before Lesson 5.

Log into ChatGPT in your browser now if you aren't already — Lessons
6, 8 and 10 generate images there, free, and hitting a daily limit just
means finishing tomorrow.

> **CHECK.** Python and Chrome report versions. ChatGPT logged in.
> Say `next`.

---

## STEP 2 · Confirm the skills

Claude Code loads every skill in this project folder on its own. Ask,
here:

> list your available skills

Nine names come back: `brand-foundation`, `design-tokens`,
`brand-guide`, `aphrodite-direction`, `hephaestus-production`,
`brand-website`, `ad-factory`, `email-sequence`, `content-engine`.
None? You opened `claude` outside the repo. Skills are project-scoped:
`cd` in and start again.

How every lesson runs from here: the lesson names a skill, Claude runs
it in this session, and stops wherever you need to read, choose or
approve. You never open another terminal to run a skill and you never
use `claude -p`. Print mode can't ask you anything or wait for an
answer.

> **CHECK.** Nine skills listed. Say `next`.

---

## STEP 3 · Open the dashboard

Second terminal:

```bash
python3 scripts/serve_dashboard.py
```

The banner prints in that terminal in the brand's orange, and the same
banner heads the dashboard. Open `http://localhost:8787/dashboard.html`.
It reads the files in `records/` and reports what exists. Not a progress bar that flatters
you; a view of the disk. It fills in as you build.

> **CHECK.** Dashboard open. Say `next`.

---

## On record

- Claude Code running; Python and Chrome confirmed; ChatGPT logged in
- Nine skills visible
- A dashboard that reads the disk

Next: `/build:02-research`. The interview, then the research.
Everything after stands on what that lesson produces.
