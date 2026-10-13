# Build Your Brand

**Free. 13 lessons, ~5 hours.** Cold clone to a researched brand, a
design system, a visual brand guide, a hero, a one-page site, one
finished asset, agents that own a job and an operations layer that runs
without you — entirely inside Claude Code, with a human approval gate
on anything that spends money, and a dated record of every decision,
including the ones you said no to.

It is the free, complete first function of **The Creative Architect**
course: https://thecreativearchitect.uk

## Quickstart

```bash
git clone https://github.com/jaicob0/build-your-brand.git
cd build-your-brand
claude
```

Then type `/build:01-setup` and follow the lessons in order. Every
lesson runs inside the Claude session you just opened: the lesson
tells Claude which skill to run, Claude runs it, and it stops wherever
you need to read, choose or approve. Don't run the lessons through
`claude -p` — print mode can't ask you questions or wait for answers.

| # | Command | What it does |
|---|---|---|
| 1 | `/build:01-setup` | The toolchain: tools confirmed, twelve skills visible, dashboard reading the disk |
| 2 | `/build:02-research` | The evidence: the interview, then sourced research, `deepresearch.md` first |
| 3 | `/build:03-foundation` | The contract: validate the foundation, read every file, correct what isn't you |
| 4 | `/build:04-design` | The tokens: choose a direction from real options, lock `design.md` |
| 5 | `/build:05-guide` | The book: a scrollable brand guide, HTML and PDF, verified by looking |
| 6 | `/build:06-hero` | The face: a hero still through the gate, inspected for fabricated text; video optional |
| 7 | `/build:07-website` | The storefront: a one-page site, words first, styled from `design.md` |
| 8 | `/build:08-assets` | The gate: a typed brief, a gated build, one asset and one refusal on record |
| 9 | `/build:09-agents` | The cast: one voice file, typed specs, five real tasks each, an honest log |
| 10 | `/build:10-dashboard` | Mission Control: overview plus department pages, every tile labelled live or placeholder |
| 11 | `/build:11-hermes` | The layer: central allowlist, five refusals proved, launchd or Docker, append-only audit |
| 12 | `/build:12-done` | The record: review everything, ship the site if you want, name the pattern |
| 13 | `/build:13-grow` | The engines: ads through the gate, a belief-mapped email sequence, rendered content |

Lessons 1 to 12 take about four and a quarter hours. Lesson 13 is
another thirty to forty-five minutes and can be run any time after.

## What you need

- **macOS.** That is what this is tested on. Linux mostly works if you
  point the skills at your Chrome binary. Windows is untested.
- **Claude Code**, logged in, on a Claude subscription. Pro works; Max
  is safer for Lesson 2's research pass, which runs Claude for half an
  hour straight.
- **Python 3.**
- **Google Chrome** at its standard path — it renders the brand guide
  PDF, the Lesson 10 dashboard check, and the Lesson 13 emails and
  carousels.
- **poppler** for the PDF check in Lesson 5: `brew install poppler`.
- **A free ChatGPT account**, logged into your browser. Lesson 6,
  Lesson 8 and the ad plates in Lesson 13 generate images there — free.
  Free tiers have daily generation limits; hitting one just means
  finishing tomorrow. Everything else runs without it, and the site
  falls back to a CSS hero.

No API keys, and nothing to buy from me. The Claude subscription above
is the one paid thing you need, and you pay it to Anthropic, not here.

**Optional pro engine:** a Higgsfield account with credits unlocks
automated builds (`--engine higgsfield` at the gate) — and its
`seedance` image-to-video is the strongest engine for hero motion.
Free stays the default; the whole course runs without it.

## What's in the repo

```
.claude/commands/build/   the thirteen /build: slash-command lessons
.claude/skills/
  brand-foundation/       interview (intake.md) -> real web research ->
                          nine files per brand: intake, copywriter
                          prompt, deepresearch, avatar-sheet, offerbrief,
                          necessary-beliefs, project-knowledge
                          (VERIFIED / UNVERIFIED split), brand-book,
                          brand_foundation.json (the machine contract)
  design-tokens/          foundation + research -> 2-3 real options ->
                          design.md: exact hex, named fonts, voice
                          USE/AVOID, component rules
  brand-guide/            foundation + design.md -> brand-guide.html
                          (scrollable, swatches, type specimens,
                          components) + brand-guide.pdf via headless
                          Chrome, rasterised and looked at
  aphrodite-direction/    one-line idea -> typed creative_brief.json
                          (never picks a tool or model; asset_type-aware)
  hephaestus-production/  validated brief -> the gate -> free path
                          (paste-ready ChatGPT prompt, you generate and
                          collect the download) or optional pro engine
                          (Higgsfield CLI, real credits) -> asset + dated
                          run record. Also the hero still and hero video.
  brand-website/          foundation + necessary-beliefs.md (one section
                          per belief) + design.md + hero -> a single
                          self-contained index.html with its own assets/
  agent-forge/            one shared _voice.md quoted from the brand files
                          -> typed agent_spec.json per agent (allowlist,
                          forbidden list, escalations, scoped credential
                          NAMES, trigger mode, dry-run) -> AGENT.md ->
                          five real tasks each with an honest PASS/FAIL
                          test log, including one escalation
  mission-control/        a tile map with a source per tile ->
                          mission_status.py labelling every value live,
                          placeholder or missing -> an overview plus a
                          page per department, all in your design.md
                          tokens, refresh + cache, rendered and looked at
  hermes-ops/             central allowlist (effective = spec INTERSECT
                          allowlist), an escalation channel proved with a
                          test, five refusals on record, one orchestrator
                          on launchd or in Docker, append-only audit log,
                          a runbook with the stop command at the top
  ad-factory/             research-mined angles -> Meta-ready copy bank
                          -> gated text-free plates + brand-locked HTML
                          overlay (never image-model text)
  email-sequence/         belief-mapped 5-7 email arc, A/B subjects,
                          inline-style HTML templates, render-verified
  content-engine/         pillars + sourced ideas -> carousels built as
                          HTML and rendered to PNG + captions + calendar
.claude/settings.json     the permission rules that make the gate hold
schema/                   brand_foundation, creative_brief, agent_spec
.env.example              env var NAMES only; .env is gitignored
scripts/
  validate_brief.py       stdlib-only schema validator (all three schemas)
  approval_gate.py        the human approval gate — the only path to a
                          build, on either engine
  collect_asset.py        verifies your ChatGPT download, installs the
                          asset, writes the dated run record
  hephaestus_build.py     pro engine: real Higgsfield CLI build (optional,
                          real credits)
  dashboard_status.py     writes status.json from what is actually on disk
  serve_dashboard.py      serves dashboard.html, refreshes on load
  mission_status.py       reads the tile map, labels every value live /
                          placeholder / missing, builds the agent feed
  allowlist_build.py      collects every spec into one auditable
                          allowlist; --check calls unreviewed tools drift
  hermes_run.py           runs one agent under spec INTERSECT allowlist:
                          five refusals built in, a dated record every time
  hermes_orchestrator.py  one tick: refuses on allowlist drift, runs what
                          is due, writes last_run and the audit line
  hermes_schedule.py      add / install / status / stop. Prints the host
                          job by default, installs on --yes, refuses gated
                          and on-demand agents
  hermes_escalate.py      routes an exception to queue, notification,
                          webhook or email, and records whether it landed
dashboard.html            build-progress view, reads status.json only
records/                  everything the skills write (gitignored; empty
                          folders tracked)
```

## How it works

- **Brand Foundation** interviews you first and writes `intake.md`
  before anything else. Then real research, with URLs, before any
  reasoning about positioning. It separates VERIFIED claims from
  UNVERIFIED ones and writes nine files; `brand_foundation.json` is the
  contract every later skill reads.
- **Design Tokens** presents two or three real directions grounded in
  the competitor teardown and your stated preferences, waits for your
  pick, then locks `design.md`. Specific values only.
- **Brand Guide** turns the documents into one shareable HTML file and
  a PDF, including a "Never claimed" panel for anything UNVERIFIED.
- **Aphrodite** turns a one-line idea into a typed creative brief. She
  decides what should exist, never how.
- **Hephaestus** reads the brief exactly as written, runs the gate, and
  only on a human `y` prints a paste-ready prompt for ChatGPT. You
  generate (free), download, drop the file in the inbox, and
  `collect_asset.py` verifies and installs it. Every decision, built
  or rejected, is a dated file in `records/runs/`.
- **Brand Website** reads the foundation, the beliefs, `design.md` and
  the hero if one exists. Copy first, then styled. One file plus its
  own `assets/` folder, so it deploys as-is.
- **Agent Forge** writes the brand voice once, then takes a job you do
  by hand every week and writes it down as a typed spec: what it may
  read, the one place it writes, the tools it is allowed, the scoped
  key it uses by name, what it must refuse, and what it stops for. An
  agent counts as built after five real tasks with an honest PASS/FAIL
  log, including one it correctly handed back.
- **Mission Control** builds your own dashboard from `design.md`: an
  overview plus a page per department your business actually runs, all
  sharing one set of tokens. Every tile names the source behind it and
  carries a LIVE or PLACEHOLDER chip in the tile, never a footnote, and
  the agent feed comes straight out of `records/agents/`.
- **Hermes** ties the two together and puts one agent on a host:
  launchd on your Mac for free, or a container when "runs 24/7" has to
  be true with the lid shut. Five refusals are proved first: a tool off
  the effective list, a gated agent asked to run unattended, a missing
  credential, an on-demand agent asked by the timer, and an agent that
  does not exist. Permissions are the intersection of each spec and one
  central allowlist, so tightening it cannot be undone by editing a
  spec. Exceptions go to a channel you tested. The audit log is
  append-only, and the runbook opens with the stop command, which you
  type once before you walk away.

Nothing in this loop invents a claim, a testimonial or a stat that
isn't in the foundation or the research file. If a section needs
something the research doesn't have, the skills ask or leave a marked
placeholder.

## The gate

A build is two keystrokes, and neither belongs to Claude.

1. Claude shows you the brief and asks `Approve build? [y/N]` in the
   session. You answer.
2. Claude runs `python3 scripts/approval_gate.py --decision y <brief>`.
   Claude Code's own permission dialog shows you that exact command,
   your answer included, and only you can allow it. `.claude/settings.json`
   lists the gate script under `ask`, so the dialog appears even if
   you've allowed other Python commands.

The gate refuses piped input, so `echo y |` writes no record and
generates nothing. On the default free engine, you generate — in
ChatGPT, free — and `collect_asset.py` verifies and installs the
download. With `--engine higgsfield` the gate builds automatically via
the Higgsfield CLI (real credits), and direct calls to
`hephaestus_build.py` and `higgsfield generate` stay denied for Claude
in the settings file, so the gate and its record wrap every build on
either engine. You can also run the gate yourself in a second terminal
and answer there; it's the same prompt and the same record. A rejection
generates nothing and spends nothing.

One caveat, stated plainly: if you start Claude Code in
`bypassPermissions` mode, the dialog is skipped and the gate is only as
good as Claude's instructions. Don't run this course in that mode.

## Your files stay yours

Everything the skills write — your intake with its pricing, your
competitor research, your brand foundation, your assets, your records —
is gitignored. So are `design.md` and the brand guide at the repo root.
If you fork this repo and push, none of that leaves your machine.
Lesson 12 deploys only `records/website/<brand_id>/`, never this repo.

## Serving the site or dashboard

```bash
python3 scripts/serve_dashboard.py     # -> localhost:8787/dashboard.html
python3 scripts/serve_dashboard.py 8788  # -> .../records/mission-control/index.html
python3 -m http.server 8000            # -> localhost:8000/records/website/<brand_id>/index.html
```

The site folder carries its own `assets/`, so it also serves or
deploys on its own.

## After the course

You will have run the whole pattern once, on one function, with your
own hands on the gate. The Creative Architect course runs it on every
function of your business: a named owner for each job, a gate on every
spend, a date on every decision, seven checks before it counts as
done. The brand you built here plugs in as the first function.

Build yours: https://thecreativearchitect.uk/?src=readme
