---
description: "Build Your Brand, Lesson 2: The evidence. The interview, then sourced research on competitors and customers, before any brand decision."
---

# /build:02-research

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 2 OF 13 · THE EVIDENCE**
Thirty to forty minutes, most of it Claude searching. You leave with your answers on file and a sourced dossier you have read.

---

## Why this lesson carries the rest

Generic output has one cause: a prompt with nothing behind it. The
model fills the gaps with the average of everything it has seen, and
the average looks like everyone else.

Evidence is the fix. Real competitors taken apart: their type, their
palette, their promise, where they're thin. The words customers
actually use, quoted, with the URL beside them. The opening nobody in
the category is standing in.

Every lesson after this one reads what this one writes. Get it wrong
here and everything downstream is wrong with confidence.

---

## STEP 1 · The interview

Claude asks first and writes nothing until you've answered. Seven
questions, in your own words, as long or as short as you like:

1. **Who are you?** What you've built, sold or done before, and what
   you want to be known for.
2. **What are you building?** What it is, who it's for, why it's
   different, what it refuses to look like. Two to four sentences.
3. **Who exactly buys it?** One real person, not a segment.
4. **What does it cost?** A price, a range, a model, or an honest
   "not set".
5. **Is anything live already?** A sales page, a site, ads. A URL
   gets audited before the research starts.
6. **Which two or three competitors do you already know?**
7. **The result your customer most wants, and the fear or frustration
   they most want gone.** Plus anything else that matters: founder
   story, testimonials, press.

And one for Lesson 4: **how should it feel?** Colour and type
preferences, and any look you can't stand.

Half-formed answers are fine. Say what you know. The research does the
rest, and it works from what you said rather than from a guess about
you.

> **RUN (Claude, in this session):** Start the `brand-foundation` skill
> now. Ask the seven questions and the feel question, one at a time or
> as one list, and wait for real answers. Never fill one in. Write
> `records/brands/<brand_id>/intake.md`, then continue into STEP 2.
> Never `claude -p`, never a second terminal.

> **CHECK.** `intake.md` exists with your answers in it. Say `next`;
> the research is already running.

---

## STEP 2 · The research

The same skill run continues from your `intake.md`. Nothing to type.

It searches first and reasons later, and it runs long. The bar: a
dossier of roughly 3,000 words with a teardown of each competitor
(visual language, type, palette, positioning, pricing, weaknesses),
the shape of the category and its openings, twenty or more customer
quotes verbatim with what they tried before and what they fear, proof
points, and the mechanisms this brand could own. If you gave a URL,
its audit lands at the top.

Nine files, written in this order to `records/brands/<brand_id>/`:

```
intake.md               your answers, verbatim, first
copywriter-prompt.md    a system prompt for any AI assistant, tuned to
                        this brand, that flags gaps instead of inventing
deepresearch.md         the dossier, sourced
avatar-sheet.md         the customer in their own words
offerbrief.md           product, promise, mechanism, proof, pricing
necessary-beliefs.md    what someone must accept before they buy
project-knowledge.md    the synthesis, VERIFIED and UNVERIFIED kept apart
brand-book.md           the readable brand book
brand_foundation.json   the contract every later skill reads
```

This is the long step. Leave it running.

> **CHECK.** Nine files on disk. Say `next`.

---

## STEP 3 · Read it before you move

The step people skip and pay for later. Open `deepresearch.md` and
read all of it, the competitor teardown especially. A wrong assumption
about your customer, a competitor you'd never heard of, a claim with
nothing under it: this is where it shows, and this is where it's cheap
to fix.

Then open `project-knowledge.md` and read the UNVERIFIED section.
Those claims stay out of everything you build. A brand that only says
what it can prove is the one people believe.

Hold the dossier to this:

- **Every market claim has a URL beside it.** No source is a guess
  wearing a suit. Tell Claude to source it or cut it.
- **The teardown describes what you can see.** Actual colours, actual
  type, an actual promise from a homepage. "They focus on quality"
  describes nothing.
- **Twenty or more quotes, verbatim.** Fewer means it paraphrased, and
  a paraphrase is worth nothing here.
- **It told you something you didn't know.** If you could have
  written it before the run, name the competitor or angle to dig into
  and run it again.

Weak evidence isn't a phase you pass through. Everything downstream
inherits it. Redo it here.

> **CHECK.** Dossier read against what you know; two URLs clicked;
> UNVERIFIED section read. Say `next`.

---

## On record

- Your answers, verbatim: `intake.md`
- A copywriter prompt grounded in this brand: `copywriter-prompt.md`
- A sourced dossier: competitors, category, quotes, proof, mechanisms
- The customer's language, a named mechanism, beliefs with bridges,
  and a VERIFIED/UNVERIFIED split

Next: `/build:03-foundation`. Validate the contract and make it yours.
Short.
