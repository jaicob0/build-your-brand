---
description: "Build Your Brand, Lesson 7: The storefront. A one-page site, words first, styled from design.md, hero-aware."
---

# /build:07-website

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 7 OF 13 · THE STOREFRONT**
About twenty minutes. You leave with a one-page site running locally with nothing on it you can't back.

---

## Words first. Design is what they wear.

The site reads the same sources as everything else: the foundation,
the beliefs, `design.md`, and the hero if you built one. No framework,
no external tool, one self-contained file plus its own `assets/`
folder.

---

## STEP 1 · Sections from beliefs

Open `necessary-beliefs.md`. Each belief a stranger has to accept
before they act becomes one section, in the order the file gives them.
The words decide what sections exist. Design comes after.

> **CHECK.** Your section list written, one per belief. Say `next`.

---

## STEP 2 · Build

> **RUN (Claude, in this session):** Use the `brand-website` skill for
> `<brand_id>` now, with the section map from STEP 1.

It reads:
- `brand_foundation.json`, the contract
- `necessary-beliefs.md`, one section each, in your order
- `design.md`; its exact values win over anything derived from
  `visual_pillars`
- The hero, if it exists: `hero.mp4` and `hero-poster.jpg` become an
  autoplaying, muted, looping background; no hero means a CSS hero
  from `design.md` and nothing broken

> If the skill stops to ask where the button should point, answer it.
> A waitlist marked `[FILL: connect to real signup]` is fine before
> launch. It won't invent a destination.

> **CHECK.** `records/website/<brand_id>/index.html` exists. Say
> `next`.

---

## STEP 3 · Serve it and read it as a stranger

From the repo root:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/records/website/<brand_id>/index.html`.
The site folder carries its own copy of the hero under `assets/`, so
it also runs and deploys on its own.

Read it the way someone who's never heard of you would:

- **Five seconds.** Does the top of the page say what this is, who
  it's for, and why it's different, before any scrolling?
- **One belief per section.** Does each section move exactly one
  belief, in order? A section that exists because websites have those
  is dead weight. Cut it.
- **Nothing you can't back.** An invented testimonial, stat or logo
  means something went wrong upstream. Go back to the source files.
  Don't publish it.
- **One action.** Is there exactly one thing to do, and does every
  section lead there?
- **Phone width.** Half your visitors meet it there first.

> **CHECK.** Renders with hero or fallback, the first line works, no
> unbackable claims. Say `next`.

---

## On record

- `records/website/<brand_id>/index.html`, served and read in your
  browser
- Every line on it traceable to the foundation

Next: `/build:08-assets`. One more asset through brief, gate and
build, and one refusal on purpose.
