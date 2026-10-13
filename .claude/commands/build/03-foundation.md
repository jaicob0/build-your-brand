---
description: "Build Your Brand, Lesson 3: The contract. Validate the foundation, read every file, correct what isn't you."
---

# /build:03-foundation

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 3 OF 13 · THE CONTRACT**
About ten minutes. You leave with a validated contract you have read and corrected.

---

## The agent proposes. You decide.

Lesson 2 wrote nine files. Nothing new is built here. This lesson is
you reading them and changing what's wrong, because every later skill
reads `brand_foundation.json` as fact.

---

## STEP 1 · Validate the JSON

```bash
python3 scripts/validate_brief.py records/brands/<brand_id>/brand_foundation.json --schema brand_foundation
```

It prints `VALID` or it doesn't. If it doesn't, fix the JSON or run
`brand-foundation` again. Never move on with an unvalidated contract.

> **CHECK.** `VALID` on screen. Say `next`.

---

## STEP 2 · Read every file. Correct every line that isn't you.

- **`avatar-sheet.md`.** Does this customer sound like someone you've
  met? Are the pains the ones you hear on calls? Is anything stated as
  fact that's actually inference?
- **`offerbrief.md`.** Would a customer repeat the promise back to
  you? Is the mechanism yours, or could a competitor claim it
  tomorrow? Does the price match what you said?
- **`necessary-beliefs.md`.** Could you sell to someone who held these
  beliefs? A belief everyone already holds isn't earning its place.
- **`brand-book.md`.** Could a competitor paste the positioning onto
  their homepage unchanged? Does the avoid list have teeth? "We never
  show a person smiling at a laptop" has teeth. "We avoid clichés"
  doesn't.
- **`deepresearch.md`.** Click two or three cited URLs. Do they say
  what the file says they say?

Edit by hand. It's your file. If you change `brand-book.md`, make the
same change in `brand_foundation.json`, because the JSON is what the
skills read.

The bar for positioning: read it aloud. If a competitor could use it
unchanged, it isn't yours yet. If it commits to something checkable
and makes you slightly uncomfortable, it's right. "Premium coffee for
people who care" fails. "Beans that arrive when you're actually
running low, not when a calendar says so" passes.

> **CHECK.** Every line reads like something you'd say about your own
> business. Say `next`.

---

## On record

- `brand_foundation.json`, validated: the contract every later skill
  reads
- A brand book you've read and corrected

Next: `/build:04-design`. Choose a visual direction from real options
and lock it into `design.md`.
