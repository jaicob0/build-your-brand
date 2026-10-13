---
description: "Build Your Brand, Lesson 4: The tokens. Choose a visual direction from real options, then lock exact values every build inherits."
---

# /build:04-design

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 4 OF 13 · THE TOKENS**
About ten minutes. You leave with a direction you chose, locked into `design.md`.

---

## Why AI sites look alike

Same instruction, same model, no design system. The model reaches for
its default, and its default is everyone's.

`design.md` is the fix: exact hex, named fonts, the rule for when the
accent appears, the words the brand uses and the words it never does.
It sits at the repo root and every build reads it. Colour and type get
settled here, before the brand book, so you never build the book and
then go back.

---

## STEP 1 · See the options. Pick one.

> **RUN (Claude, in this session):** Use the `design-tokens` skill for
> `<brand_id>` now. Present the options and wait for the pick. Never
> write `design.md` before the student has chosen.

The skill reads the competitor teardown in `deepresearch.md` and your
preferences in `intake.md`, then puts two or three real directions in
front of you. Each has a palette in hex, a type pairing, and one
sentence on why, grounded in what your competitors already look like.
One might lean into the category pattern. Another might break it
exactly where it's thinnest.

What lands in `design.md`:

- Palette: exact hex and a role for every colour, with the rule that
  the accent is not decoration
- Typography: named families, the type scale, when each is used
- Voice: words to use, words never to use, and the two or three
  sentence shapes the brand repeats until they're recognisable
- Components: button, card and spacing rules you can check a build
  against
- Motion: how things move, and how they never move
- Mood: one paragraph for the cases no rule covers

You choose. You're the one who looks at this brand every day.

> **CHECK.** Direction chosen. Say `next`.

---

## STEP 2 · Cross-check, if you're torn

Unsure between two, or want to test the one you picked? Give Claude
five specifics. Not "clean", not "modern": hex codes and named brands.

- The name and what you sell
- Three words for the brand
- Colours, as hex
- Three brands you'd borrow from, and the one thing you'd take from
  each
- Voice: what it always does, what it never does

Claude re-derives the tokens from your answers and shows you where
they differ from the direction you picked. The disagreement is where
the real decision is.

---

## STEP 3 · Specific, or it isn't finished

Open `design.md`. Any line that could describe two different brands
isn't done. `#1B4B8F` is a decision. "Warm blue" leaves the model
guessing. If you can't say which research line or interview answer
forced a value, cut it.

> If a `design.md` from another brand already sits at the root, the
> skill stops and asks before overwriting. Answer it. It's protecting
> the other brand.

> **CHECK.** Every value in `design.md` is specific. Say `next`.

---

## On record

- `design.md` at the repo root: hex with roles, named fonts, voice,
  components, mood
- A direction you chose, with the evidence for it

Next: `/build:05-guide`. Turn the tokens into a brand book you can
scroll.
