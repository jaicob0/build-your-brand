#!/usr/bin/env python3
"""Hephaestus production: consume a validated creative_brief.json, build the
asset via the Higgsfield CLI, save it to disk. Builds AS WRITTEN — never
reinterprets the brief's intent.

Usage:
  python3 scripts/hephaestus_build.py <brief.json>

Mode is inferred from brief_id suffix (no schema change needed):
  <anything>-hero-still   -> still image build (as before), PLUS copies the
                              result to assets/hero-still.png and produces
                              assets/hero-poster.jpg (fixed names, overwritten
                              each run — brand-website reads these).
  <anything>-hero-video   -> image-to-video build via the Higgsfield CLI's
                              video model, using assets/hero-still.png as the
                              start image (must already exist — run the
                              hero-still brief first). Copies the result to
                              assets/hero.mp4 (fixed name).
  anything else            -> normal one-off asset build (unchanged behavior).

On success: prints a human status line, then a final line of JSON:
  {"asset_path": "...", "bytes": N, "model": "..."}
On failure (auth, rate limit, CLI missing): prints a clean human-readable
error to stderr and exits 1. Never lets a raw stack trace reach the screen.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "records" / "assets"
IMAGE_MODEL = "gpt_image_2"  # production decides the mechanism, never the brief. Change here if Higgsfield renames or retires the model.
VIDEO_MODEL = "seedance_2_0"  # supports image-to-video via --start-image; chosen for quality/cost balance at time of writing — production's call, not the brief's.
QUALITY = "high"
RESOLUTION = "2k"
VIDEO_RESOLUTION = "1080p"
VIDEO_DURATION = 7  # seconds — within the 5-8s hero-loop spec
# gpt_image_2 supports: auto,1:1,4:3,3:4,16:9,21:9,9:16,3:2,2:3 — no 4:5. Map the
# brief's aspect_ratio (which uses a wider vocabulary) to the nearest supported value.
ASPECT_RATIO_MAP = {
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:5": "3:4",  # nearest supported portrait ratio
}
# seedance_2_0 supports: auto,16:9,9:16,4:3,3:4,1:1,21:9 — same 4:5 gap.
VIDEO_ASPECT_RATIO_MAP = {
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:5": "3:4",
}

HERO_STILL_PATH = ASSETS_DIR / "hero-still.png"
HERO_POSTER_PATH = ASSETS_DIR / "hero-poster.jpg"
HERO_VIDEO_PATH = ASSETS_DIR / "hero.mp4"


def clean_error(stderr: str, returncode: int) -> str:
    low = stderr.lower()
    if "not logged in" in low or "unauthorized" in low or "401" in low or "auth" in low and "login" in low:
        return (
            "HIGGSFIELD AUTH ERROR: the CLI is not logged in.\n"
            "Fix: run `higgsfield auth login` in a terminal, then re-run this build."
        )
    if "rate limit" in low or "429" in low or "too many requests" in low:
        return (
            "HIGGSFIELD RATE LIMIT: too many requests right now.\n"
            "Fix: wait ~60 seconds and re-run this build."
        )
    if "insufficient" in low and "credit" in low:
        return (
            "HIGGSFIELD OUT OF CREDITS: the account has no credits left.\n"
            "Fix: top up at higgsfield.ai, then re-run this build."
        )
    if '"nsfw"' in low or "status \"nsfw\"" in low or "flagged" in low:
        return (
            "HIGGSFIELD CONTENT FILTER: the model flagged this job (often a false positive on brand names / logos / real people).\n"
            "Fix: soften the brief's wording (drop the brand name, describe it generically) and re-run this build, "
            "or try a different model with `higgsfield model list --image`."
        )
    return f"HIGGSFIELD BUILD FAILED (exit {returncode}):\n{stderr.strip()[-800:]}"


def extract_result_url(stdout: str) -> str | None:
    """Best-effort extraction of a downloadable result URL from `--json` output.
    Real `higgsfield ... --wait --json` shape: a top-level array of job
    objects, each with "result_url" (full-res) — confirmed by a live test
    call. Stay defensive for other shapes too."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            return first.get("result_url") or first.get("min_result_url") or first.get("url")
    elif isinstance(data, dict):
        if "result_url" in data:
            return data["result_url"]
        if "url" in data:
            return data["url"]
        if "results" in data and isinstance(data["results"], list) and data["results"]:
            return data["results"][0].get("url") or data["results"][0].get("result_url")
    return None


def build_prompt_from_brief(brief: dict) -> str:
    """Build the prompt AS WRITTEN from the brief. Never add, drop, or
    reinterpret the creative intent — but ad_copy, when present, MUST be
    rendered as real on-image text, or a "static ad" comes out as bare
    product photography."""
    prompt_parts = [
        brief.get("big_idea", ""),
        brief.get("visual_description", ""),
        brief.get("style_notes", ""),
    ]
    ad_copy = brief.get("ad_copy", {})
    if ad_copy.get("has_copy"):
        copy_instruction = f'Render this exact text on the image as real, legible typography: headline "{ad_copy.get("headline", "")}"'
        if ad_copy.get("subhead"):
            copy_instruction += f', subhead "{ad_copy["subhead"]}"'
        if ad_copy.get("cta"):
            copy_instruction += f', call-to-action "{ad_copy["cta"]}"'
        if ad_copy.get("placement"):
            copy_instruction += f'. Placement: {ad_copy["placement"]}.'
        copy_instruction += " Spell the text exactly as given, no substitutions."
        prompt_parts.append(copy_instruction)
    elif brief.get("asset_type") == "ad-plate":
        prompt_parts.append(
            "This is a text-free background plate. Absolutely no text, no words, "
            "no letters, no numbers, no logos, no wordmarks, no watermarks, no "
            "signage, no labels, no fabricated readable characters anywhere in "
            "the image — on any surface, in any style, however subtle. All type "
            "is added later in post."
        )
    return " ".join(p for p in prompt_parts if p).strip()


def convert_to_jpg(src: Path, dst: Path) -> bool:
    """Convert src (any raster image) to a real JPEG at dst. Tries macOS
    `sips` first (always present on macOS, no dependency), falls back to
    Pillow if installed. Returns False (with a printed note) if neither is
    available — caller should not treat that as fatal."""
    if shutil.which("sips") is not None:
        result = subprocess.run(
            ["sips", "-s", "format", "jpeg", str(src), "--out", str(dst)],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and dst.exists():
            return True
    try:
        from PIL import Image  # type: ignore
        Image.open(src).convert("RGB").save(dst, "JPEG", quality=90)
        return True
    except Exception:
        pass
    print(f"NOTE: could not convert {src} to a real JPEG (no `sips` or Pillow available) — {dst} not written.")
    return False


def build_still(brief_path: Path, brief: dict, brief_id: str, is_hero_still: bool) -> int:
    prompt = build_prompt_from_brief(brief)
    aspect_ratio = ASPECT_RATIO_MAP.get(brief.get("aspect_ratio", "1:1"), "1:1")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = ASSETS_DIR / f"{brief_id}-{ts}.json"

    cmd = [
        "higgsfield", "generate", "create", IMAGE_MODEL,
        "--prompt", prompt,
        "--aspect_ratio", aspect_ratio,
        "--quality", QUALITY,
        "--resolution", RESOLUTION,
        "--wait",
        "--json",
    ]

    print(f"Running: higgsfield generate create {IMAGE_MODEL} --prompt \"<brief text>\" --aspect_ratio {aspect_ratio} --quality {QUALITY} --resolution {RESOLUTION} --wait --json")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        print(clean_error(result.stderr, result.returncode), file=sys.stderr)
        return 1

    out_path.write_text(result.stdout)

    asset_file_path = None
    asset_bytes = 0
    try:
        url = extract_result_url(result.stdout)
        if url:
            import urllib.request
            ext = ".png" if ".png" in url else (".jpg" if ".jpg" in url or ".jpeg" in url else ".bin")
            asset_file_path = ASSETS_DIR / f"{brief_id}-{ts}{ext}"
            urllib.request.urlretrieve(url, asset_file_path)
            asset_bytes = asset_file_path.stat().st_size
    except Exception as e:
        print(f"NOTE: could not auto-download asset file ({e}); raw result saved at {out_path}")

    print(f"Result metadata saved: {out_path}")
    if not asset_file_path:
        print(json.dumps({"asset_path": str(out_path), "bytes": out_path.stat().st_size, "model": IMAGE_MODEL, "note": "metadata only, no direct file URL found"}))
        return 0

    print(f"Asset downloaded: {asset_file_path} ({asset_bytes} bytes)")

    if is_hero_still:
        # Fixed-name copies brand-website (and the hero-video step) read.
        shutil.copyfile(asset_file_path, HERO_STILL_PATH)
        print(f"Hero still copied to fixed path: {HERO_STILL_PATH}")
        if convert_to_jpg(HERO_STILL_PATH, HERO_POSTER_PATH):
            print(f"Hero poster written: {HERO_POSTER_PATH}")

    print(json.dumps({"asset_path": str(asset_file_path), "bytes": asset_bytes, "model": IMAGE_MODEL}))
    return 0


def build_video(brief_path: Path, brief: dict, brief_id: str) -> int:
    if not HERO_STILL_PATH.exists():
        print(
            "HERO STILL NOT FOUND: expected `records/assets/hero-still.png` to already exist.\n"
            "Fix: build the `<brand_id>-hero-still` brief first (through the same approval gate), "
            "then re-run this hero-video brief.",
            file=sys.stderr,
        )
        return 1

    prompt = build_prompt_from_brief(brief)
    aspect_ratio = VIDEO_ASPECT_RATIO_MAP.get(brief.get("aspect_ratio", "16:9"), "16:9")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = ASSETS_DIR / f"{brief_id}-{ts}.json"

    cmd = [
        "higgsfield", "generate", "create", VIDEO_MODEL,
        "--prompt", prompt,
        "--start-image", str(HERO_STILL_PATH),
        "--duration", str(VIDEO_DURATION),
        "--resolution", VIDEO_RESOLUTION,
        "--aspect_ratio", aspect_ratio,
        "--wait",
        "--json",
    ]

    print(f"Running: higgsfield generate create {VIDEO_MODEL} --prompt \"<brief text>\" --start-image {HERO_STILL_PATH} --duration {VIDEO_DURATION} --resolution {VIDEO_RESOLUTION} --aspect_ratio {aspect_ratio} --wait --json")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)

    if result.returncode != 0:
        print(clean_error(result.stderr, result.returncode), file=sys.stderr)
        return 1

    out_path.write_text(result.stdout)

    asset_file_path = None
    asset_bytes = 0
    try:
        url = extract_result_url(result.stdout)
        if url:
            import urllib.request
            ext = ".mp4" if ".mp4" in url else ".bin"
            asset_file_path = ASSETS_DIR / f"{brief_id}-{ts}{ext}"
            urllib.request.urlretrieve(url, asset_file_path)
            asset_bytes = asset_file_path.stat().st_size
    except Exception as e:
        print(f"NOTE: could not auto-download asset file ({e}); raw result saved at {out_path}")

    print(f"Result metadata saved: {out_path}")
    if not asset_file_path:
        print(json.dumps({"asset_path": str(out_path), "bytes": out_path.stat().st_size, "model": VIDEO_MODEL, "note": "metadata only, no direct file URL found"}))
        return 0

    print(f"Asset downloaded: {asset_file_path} ({asset_bytes} bytes)")

    if asset_file_path.suffix == ".mp4":
        shutil.copyfile(asset_file_path, HERO_VIDEO_PATH)
        print(f"Hero video copied to fixed path: {HERO_VIDEO_PATH}")
    else:
        print(f"NOTE: downloaded file is not an .mp4 ({asset_file_path.suffix}) — {HERO_VIDEO_PATH} not written. Inspect {asset_file_path} manually.")

    print(json.dumps({"asset_path": str(asset_file_path), "bytes": asset_bytes, "model": VIDEO_MODEL}))
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: hephaestus_build.py <brief.json>", file=sys.stderr)
        return 2
    brief_path = Path(sys.argv[1])
    if not brief_path.exists():
        print(f"ERROR: brief not found: {brief_path}", file=sys.stderr)
        return 2

    if shutil.which("higgsfield") is None:
        print(
            "HIGGSFIELD CLI NOT FOUND: install it first (see README prerequisites).",
            file=sys.stderr,
        )
        return 1

    brief = json.loads(brief_path.read_text())
    brief_id = brief.get("brief_id", "unknown")

    # Hero mode detection: match "-hero-video"/"-hero-still" as a suffix OR
    # followed by "-v<N>" (revisions, e.g. "<brand>-hero-still-v2" after a
    # rejected first attempt) — a revision brief must still get the fixed-path
    # copy behavior, not silently fall through to a one-off build.
    def _is_hero(bid: str, kind: str) -> bool:
        marker = f"-hero-{kind}"
        if bid.endswith(marker):
            return True
        idx = bid.find(marker)
        return idx != -1 and bid[idx + len(marker):].lstrip("-").startswith("v") \
            and bid[idx + len(marker):].lstrip("-")[1:].isdigit()

    if _is_hero(brief_id, "video"):
        return build_video(brief_path, brief, brief_id)
    is_hero_still = _is_hero(brief_id, "still")
    return build_still(brief_path, brief, brief_id, is_hero_still)


if __name__ == "__main__":
    raise SystemExit(main())
