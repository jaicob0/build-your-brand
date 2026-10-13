---
description: "Build Your Brand, Lesson 5: The book. Build the visual brand guide as HTML and PDF, then verify the export by looking at it."
---

# /build:05-guide

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 5 OF 13 · THE BOOK**
About fifteen minutes. You leave with a scrollable brand book in HTML and PDF that you've actually looked at.

---

## Documents aren't a brand guide

Markdown is raw material. A brand guide is what you hand a designer,
a client or a collaborator so they stop asking. It has to be a thing
you scroll, with every rule rendered on the page, not described.

---

## STEP 1 · Inputs

Three quick things before the build:

1. **Logo.** Have one? Drop it in `records/brands/<brand_id>/assets/`.
   None? The book sets a typographic wordmark from `design.md`.
2. **Photos.** Founder, product, environment. Same folder. None is
   fine.
3. **Mood.** Your three words for how the brand feels, and one or two
   sites whose look you respect.

> **CHECK.** Answers ready, or "skip". Say `next`.

---

## STEP 2 · Build the book

> **RUN (Claude, in this session):** Use the `brand-guide` skill for
> `<brand_id>` now. Ask the three input questions first if they
> haven't been answered.

It reads the foundation and `design.md`, writes one self-contained
`brand-guide.html`, screenshots the cover, and exports
`brand-guide.pdf` through headless Chrome:

- **Part I, the story.** What this brand believes, who it's for, what
  it stands against.
- **Part II, the book.** Palette as swatches with hex and role. Type
  as live specimens at real sizes. A real button and card built from
  your component rules. Voice as two columns, use and never. A
  messaging library set in the brand's own type.
- **Atmosphere.** The brand's photographic direction.
- **Never claimed.** A panel naming every UNVERIFIED claim so no one
  uses it.

The guide is styled in your palette. It demonstrates the brand rather
than describing it.

> **CHECK.** `brand-guide.html`, `brand-guide-cover.png` and
> `brand-guide.pdf` exist. Say `next`.

---

## STEP 3 · Verify by looking

Exit code zero means Chrome didn't crash. It doesn't mean the PDF has
pages. Check the size:

```bash
ls -la brand-guide.pdf
```

Well over 20KB. Then look at the pages:

```bash
pdftoppm -r 100 -png brand-guide.pdf /tmp/brand-guide-check
```

(`pdftoppm` comes with poppler: `brew install poppler`.) Open the
PNGs. Text not cut off, colours rendered, no blank pages.

Then read the HTML and the PDF and hold them to this:

- **Real quotes.** Are the customer quotes verbatim from
  `deepresearch.md`, with sources, or invented?
- **The Never Claimed panel.** Does it name real gaps (no price set,
  no measured results yet)? Generic hedging means it isn't doing its
  job.
- **The voice test.** Read the story aloud. Your brand, or a brand?
- **The stranger test.** Someone who knows nothing about you reads it.
  Can they say what this is, who it's for, and what it looks like,
  without asking?
- **The designer test.** Could a designer build the next page from
  Part II alone, with no question about colour, type or tone? If
  they'd have to ask, Part II isn't done.

Anything off: say exactly what, and re-export.

> **CHECK.** Size checked, pages viewed, both files read. Say `next`.

---

## On record

- `brand-guide.html`: palette, type and components shown live, in your
  own tokens
- A cover screenshot and a PDF you verified by looking

Next: `/build:06-hero`. A hero image, through the gate.
