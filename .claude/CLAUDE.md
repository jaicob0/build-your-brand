# Build Your Brand — agent rules

This repo is an interactive course. A human student is driving, one
lesson at a time, by typing `/build:NN` commands themselves.

## Never start on your own

- **Do not begin any lesson, run any script, or do any research until
  the student types the lesson's command** (`/build:01-setup` through
  `/build:10-grow`) or explicitly asks for it in their own words.
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
- **Deploy path selection (Lesson 9):** detect what's installed and
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
- The interview in `brand-foundation` and the option pick in
  `design-tokens` are conversations here. Ask, then stop and wait.

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
- The one outward link is the course site, at the close of Lessons 9
  and 10 and on the dashboard. Print it as written. Never state a
  price, a seat count or a deadline; the site carries those.
