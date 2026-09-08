---
name: ad-factory
description: Use when the student wants ad creatives — mine angles from the foundation, write a Meta-ready copy bank, then produce static and video ads through the approval gate. Text-free plates + brand-locked HTML overlay, never image-model text.
---

# Ad Factory

You turn the brand foundation into a launch-ready ad set: angles
mined from real research, a copy bank, static ads, and video ad
scripts — every generated asset through the approval gate, every
claim sourced.

Two hard rules that make this better than the naive version:

1. **No image-model text. Ever.** Image models garble rendered text —
   that's how you get trash ads. The image model generates a
   **text-free background plate**; the hook, headline, and CTA are
   overlaid afterwards as brand-locked HTML rendered to PNG. Crisp
   type, exact brand fonts and colours, every time.
2. **No ungated spend.** Every plate/video build goes through the
   approval gate like any other asset. Copy and angle work are
   generated and student-reviewed (no generation, no gate needed);
   image/video generation is gated — and free: the student generates
   in ChatGPT on the free path.

## Prerequisites

- A validated foundation: `records/brands/<brand_id>/` with
  `necessary-beliefs.md`, `avatar-sheet.md`, `offerbrief.md`.
- `design.md` at the repo root (exact palette/type/voice — Lesson 4).
- For image/video builds: a free ChatGPT account, logged in (Lesson 1).
  Optional pro engine: Higgsfield CLI authenticated — only when the
  student chooses it at the gate.

## What you do

### Step 1 — Mine the angles (from research, not imagination)

Read `avatar-sheet.md` for the customer's own words about what hurts,
what they fear, what they've tried and what they'd object to, `necessary-beliefs.md`, `offerbrief.md` (mechanism,
pricing), and `deepresearch.md`'s competitor section (what the
category already over-says).

Produce **5-8 ad concepts**, each mapped to ONE necessary belief.
Give each concept one of these shapes, and only where the research
supports it:

- **What it costs to wait** — the running price of the unsolved
  problem, traced to a fact in the dossier
- **Why the usual fix fails** — the category's default answer, its
  failure, and this brand's mechanism in its place
- **The refusal** — what this brand deliberately isn't, from the
  avoid list
- **The objection, answered** — the top objection on the avatar sheet,
  met directly
- **The comparison** — this model against the category's, grounded in
  the competitor teardown
- **Who they become** — the customer's aspired self, from the avatar
  sheet

**Kill rule:** any angle a competitor could run unchanged is not an
angle — cut it. Any hook that needs a stat no source backs is cut.
If a concept's power comes from an UNVERIFIED claim, it does not run.

Write to `records/ads/<brand_id>/ad-concepts.md`:

```
## Concept N — [angle type] (advances Belief #X)
- Psychological wedge: [one line]
- Hook A: [pattern-interrupt, first 1.5s]
- Hook B: [different pattern]
- Hook C: [different pattern]
- Primary text: [1-3 sentences, problem → mechanism → CTA]
- Headline (≤40 chars): [...]
- Description: [...]
- CTA button: [...]
- Source lines: [which research/avatar/offer lines this is built from]
```

Three hooks per concept, each a DIFFERENT pattern — they exist to be
tested against each other.

### Step 2 — The copy bank (Meta-ready)

Compile all concepts into `records/ads/<brand_id>/copy-bank.md` in
the platform-ready format above, plus a launch sheet mapping
concept → belief → hooks → asset status. **The student reviews and
edits this file** — it's the campaign's source of truth, in their
words, before anything is spent.

### Step 3 — Static ads: plate + overlay, through the gate

For each concept the student approves for production:

1. **The plate (gated):** ask `aphrodite-direction` for a brief with
   `brief_id` ending `-ad-plate` and `asset_type: "ad-plate"` — a
   text-free background in the concept's aspect ratio (1:1 or 9:16),
   built to `design.md` palette and mood, with clear negative space
   where the copy will sit. `forbidden` must include on-image text,
   logos, watermarks — per-surface where the plate has multiple
   surfaces. Validate, run through the Hephaestus gate, paste the
   printed prompt into ChatGPT, then collect the download to
   `records/assets/`.
2. **The overlay (no generation):** build a brand-locked HTML file per
   ad — the plate as background image, hook/headline/CTA in the
   brand's exact fonts and colours from `design.md` — and render to
   PNG with headless Chrome at the plate's resolution. Save to
   `records/ads/<brand_id>/static/concept-N-{1x1|9x16}.png`.
3. **Judge it** like Lesson 8: copy legible, palette exact, nothing
   garbled. If the plate is weak the fix is upstream — new plate
   brief, not a patched overlay.

### Step 4 — Video ads: scripted beats, gated plates, honest assembly

Per approved concept, write a beat script to
`records/ads/<brand_id>/video/concept-N-script.md`:

```
Beat 1 (0-1.5s) hook:    VO "[hook line]" / on-screen "[≤5 words]"
Beat 2 (1.5-7s) problem: VO "[pain, customer words verbatim]"
Beat 3 (7-12s) mechanism: VO "[the fix]" / on-screen "[sourced proof]"
Beat 4 (12-15s) cta:     VO "[CTA]" / end-card
```

Plates for each visual beat follow Step 3's gate (brief_id suffix
`-ad-plate`). Motion and VO assembly are the student's call — this
skill scripts and gates; it does not silently assemble final video.
Where the student has the tools (image-to-video for beat motion,
TTS for VO, ffmpeg for captions burned into the bottom safe zone at
1080×1920), provide the exact commands and naming
(`CONCEPT-N_{angle}_HOOK-{A|B|C}.mp4`) but run nothing without the
student saying go.

## Output layout

```
records/ads/<brand_id>/
  ad-concepts.md        the angles, source-mapped
  copy-bank.md         Meta-ready copy, student-reviewed
  launch-sheet.md      concept → belief → hooks → asset status
  static/              rendered final statics (plate + overlay)
  video/               beat scripts + assembled cuts (if built)
```

## Boundaries — never do these

- Never let the image model render text, a logo, or a wordmark —
  plates are text-free, overlays carry all type.
- Never generate an image or video outside the approval gate.
- Never use an UNVERIFIED claim in any hook, headline, or script —
  if the concept needs one to work, the concept is wrong.
- Never invent a stat, testimonial, or urgency. Earned urgency only
  (a real deadline, a real limit) — and only if the offer brief
  actually states one.
- Never write a hook in words the customer didn't use or the brand
  wouldn't say — check both against `avatar-sheet.md` language
  patterns and the `tone`/`avoid` fields.

## How this connects

Plates run the standard `aphrodite-direction` →
`hephaestus-production` pipeline (`asset_type: "ad-plate"`). The
foundation's `positioning`, `tone`, and `avoid` fold into every brief
automatically. Copy bank and concepts reference (never re-source)
`deepresearch.md`.
