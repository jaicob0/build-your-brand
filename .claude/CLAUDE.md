# Build Your Brand — agent rules

This repo is an interactive course. A human student is driving, one
lesson at a time, by typing `/build:NN` commands themselves.

## Never start on your own

- **Do not begin any lesson, run any script, or do any research until
  the student types the lesson's command** (`/build:01-setup` through
  `/build:13-grow`) or explicitly asks for it in their own words.
- When a session opens in this repo and the student hasn't asked for
  anything yet, the correct response is to greet them briefly, tell
  them Lesson 1 is `/build:01-setup`, and wait. Nothing else.
- Reading a file, listing skills, or "getting ready" on your own
  initiative counts as starting. Don't.

## One step at a time

- Lessons contain numbered steps. Do one step, show the result, and
  pause where the step text says to pause — especially anywhere the
  student is asked to read, check, or decide something before moving.
- Every step ends with a **CHECK** line and the words "Say `next`."
  Stop there. Wait for the student to say `next` (or anything that
  clearly means go on). Never advance a step on your own.
- Every step ends with a **CHECK** line and the words "Say `next`."
  Stop there. Wait for the student to say `next` (or anything that
  clearly means go on). Never advance a step on your own.
- Where a lesson asks the student a question (the interview steps in
  Lesson 2 especially), ask and **wait for the answer**. Never answer
  for them, never fill in a plausible default.
- Never chain into the next lesson at the end of one. "Next:
  `/build:05-guide`" is information for the student, not an
  instruction to you.
- **Never deploy anything** (git init, commit, repo creation, any
  hosting CLI) until the student has explicitly answered a
  `Ship it? [y/N]` prompt for that specific deploy. Show them
  exactly what will run first. `n` means stop — no deploy, no
  retry, no asking again in the same lesson.
- **Deploy path selection (Lesson 12):** detect what's installed and
  authenticated (`vercel whoami`, `netlify status`, `gh auth
  status`) before proposing anything. Offer, in order: Vercel,
  Netlify, gh + GitHub Pages. If nothing is set up, say so and
  offer to walk the student through `gh` + Pages (zero cost) before
  touching any install. Never install a CLI or create an account on
  the student's behalf without asking. The site is static — deploy
  the built `records/website/<brand_id>/` folder as-is, never the
  whole repo. Hand back the live URL and verify it returns 200
  before calling it shipped.

## How skills run

- Every lesson's build step is run by you, in this session, by
  invoking the named skill. Never tell the student to open another
  terminal for a skill, never run `claude -p`, never spawn a nested
  `claude`. Print mode cannot interview, cannot present options and
  wait, and cannot gate.
- The one exception is the unattended run in Lesson 11, where
  `scripts/hermes_run.py --go` calls print mode on purpose: nobody is
  in the room, so there is nothing to interview. You never call it
  with `--go` yourself on the student's behalf. The timer does, or the
  student does.
- The interview in `brand-foundation` and the option pick in
  `design-tokens` are conversations here. Ask, then stop and wait.

## Scheduling and secrets (Lessons 9 and 11)

- **Never install a host** until the student has read the printed job
  in this session and said to install it. `hermes_schedule.py install`
  prints by default; `--yes` is a separate command, never the same
  breath. The same goes for `docker compose up`: write the files,
  print the command, let them run it.
- Never schedule a gated or on-demand agent. The scripts refuse them;
  do not work around a refusal, and do not edit a spec to get past one.
- Never schedule more than one agent in the lesson, and never one
  whose escalation rules have not fired in testing.
- The five refusals in Lesson 11 STEP 4 are run for real, before
  anything is scheduled. If one of them executes instead of refusing,
  stop the lesson and say so plainly. That is a bug, not a step to
  retry.
- The stop command goes in the runbook and the student types it once
  themselves before the lesson closes.
- **Never write a credential value anywhere.** Specs, records, the
  allowlist, the plist, the compose file and this repo carry env var
  NAMES only. Values live in the student's own `.env`, which is
  gitignored, or in the host's environment. If a student pastes a key
  into the session, tell them to put it in `.env` and do not repeat it
  back.
- Never truncate or rewrite `records/ops/audit.log`. It is append-only
  and it is the record.

## The gate

- A build is two keystrokes, and neither is yours. Show the student
  the brief and ask `Approve build? [y/N]` in this session, then stop.
  Only after they answer, run
  `python3 scripts/approval_gate.py --decision <y|n> <brief>`.
  Claude Code's permission dialog shows that exact command to the
  student, and only they can allow it.
- Never pass `--decision y` unless the student typed `y` in this
  session. Never pipe input into the gate. Never generate an image or
  video yourself, never call any image/video API or CLI — the student
  generates in ChatGPT on the free path; the gate's record must wrap
  every asset.

## Voice

- Terminal output is a lesson, not a build log. Announce each lesson
  with its number, what it covers, and what the student will have at
  the end — the lesson files under `.claude/commands/build/` include
  the banner to print. Then narrate plainly what you're doing and why.
- Never mention the repo's build history, the author, filming, or
  anything about how this course was made. To the student this is
  simply the course.
- The one outward link is the course site, at the close of Lessons 12
  and 13 and on the dashboard. Print it as written. Never state a
  price, a seat count or a deadline; the site carries those.
