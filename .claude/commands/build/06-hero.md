---
description: "Build Your Brand, Lesson 6: The face. A hero still through the gate, then motion if you choose to spend the time on it."
---

# /build:06-hero

```
     ██  ▓▓▓▓▓  ▓▓  ██████  ██████  ██████
     ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
     ██ ▓▓▓▓▓▓▓ ▓▓ ██      ██    ██ ██████
██   ██ ▓▓   ▓▓ ▓▓ ██      ██    ██ ██   ██
 █████  ▓▓   ▓▓ ▓▓  ██████  ██████  ██████

          T H E   C R E A T I V E   A R C H I T E C T
```

**LESSON 6 OF 10 · THE FACE**
About twenty minutes. You leave with a hero still that went through the gate and that you inspected up close.

---

## The still decides the video

Motion adds nothing a bad frame lacks. So the order is fixed: generate
the still, approve it, inspect it, and only then animate it. Nothing
is generated until you've read the brief and typed `y` — and even then,
**you** generate it, in ChatGPT, free. The gate prints the prompt; you
paste it, download the result, drop it in the repo. No credits, no paid
accounts.

---

## STEP 1 · The brief

> **RUN (Claude, in this session):** Use `aphrodite-direction` to write
> the hero-still brief for `<brand_id>`, `brief_id` ending in
> `-hero-still`, `asset_type: hero-still`.

Be exact about what's forbidden. Image models will print fabricated
text or a logo onto any surface with texture, however clearly you said
not to. If the still has several surfaces (a mat, a switch, a tray, a
housing), forbid text on each one by name rather than once in general.

> **CHECK.** Brief open at `records/briefs/<brief_id>.json`; the
> forbidden list names each surface. Say `next`.

---

## STEP 2 · Through the gate, then ChatGPT

> **RUN (Claude, in this session):** Use `hephaestus-production` on
> `records/briefs/<brief_id>.json`.

The gate is two keystrokes and neither is Claude's. Claude shows you
the brief and asks `Approve build? [y/N]`; you answer here. Then Claude
Code's own permission dialog shows the exact gate command with your
answer inside it, and you allow it. Claude can't click that dialog.

On `y`, the gate prints a **paste-ready prompt** — the brief's creative
intent, exactly as written. Paste it into ChatGPT, generate (free),
download the result, and save it as
`records/assets/inbox/<brief_id>.png`. Then collect it:

```bash
python3 scripts/collect_asset.py records/briefs/<brief_id>.json
```

That verifies the file is real, installs it to
`records/assets/hero-still.png` and `hero-poster.jpg`, and writes the
dated run record in `records/runs/`.

**Have a Higgsfield account?** Say `pro` when Claude offers the engine
and the gate builds it automatically (`--engine higgsfield`) — real
credits, no pasting. The course works either way; free is the default.

Judge it like an art director. "Fine" is bad. Are the colours your
hex? Is the mood the one in `design.md`, or the model's default mood?
Is there text anywhere?

If it's mediocre, generate again with a sharper brief. It's free —
your only cost is a minute and a daily limit.

> **CHECK.** Brief read, `y` given, dialog allowed, prompt pasted into
> ChatGPT, file collected, still inspected. Say `next`.

---

## STEP 3 · Look at it up close

A clean exit isn't a clean image. Zoom into every textured surface and
look for readable fabricated text. If it's there, the fix is upstream:
a new brief named `-hero-still-v2` (the build recognises version
suffixes), not a patched video prompt.

> **CHECK.** Still inspected at full size, textured surfaces
> especially. Clean, or a new brief written. Say `next`.

---

## OPTIONAL · Logo and section images

While the pipeline is warm, round out the set the same way: a mark and
wordmark if the brand has none, product shots or textures the site
will need. Same rules. Aphrodite writes the brief, Hephaestus gates
it, `design.md` hex goes in the brief, no baked-in text where the site
will lay copy. Each one is a dated record, approved or refused, like
the hero.

---

## OPTIONAL · Motion

Quiet only. A slow move toward the subject, a little air in the scene,
colours locked to the still, nothing new entering frame. It's a
background for text and has to stay readable underneath. Five to eight
seconds, looping.

> **RUN (Claude, in this session):** Use `aphrodite-direction` for the
> `<brand_id>` hero video, `brief_id` ending in `-hero-video`, then
> `hephaestus-production` on the resulting brief.

Same gate, then the same free path — but in ChatGPT/Sora, video this
time. For image-to-video, upload `records/assets/hero-still.png` with
the prompt (Sora animates from the still, which keeps the motion
locked to the frame you approved). Save the download as
`records/assets/inbox/<brand_id>-hero-video.mp4` and collect it the
same way. Lands at `records/assets/hero.mp4`.

**Pro option worth knowing:** Higgsfield's `seedance` image-to-video is
the strongest engine for this exact job — hero motion from a still.
If you have credits there, say `pro` at the gate and it runs
automatically.

Stopping at the still is fine. Lesson 7 works either way.

---

## On record

- A hero still in `records/assets/`, approved by you at the gate,
  inspected by you up close
- The decision, dated, in `records/runs/`
- The video, only if you chose to make it

Next: `/build:07-website`. The site: words first, `design.md` second.
