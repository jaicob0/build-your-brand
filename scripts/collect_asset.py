#!/usr/bin/env python3
"""Collect a free-path asset the student generated themselves (ChatGPT /
Sora free tier) and dropped into records/assets/inbox/.

Usage:
  python3 scripts/collect_asset.py records/briefs/<brief_id>.json

The free path, end to end:
  1. Aphrodite writes the brief (unchanged).
  2. The approval gate records the student's `y` and prints a paste-ready
     prompt for ChatGPT. Nothing is auto-generated; nothing is spent.
  3. The student generates in ChatGPT (image) or ChatGPT/Sora (video),
     downloads the result, and saves it as
     `records/assets/inbox/<brief_id>.<png|jpg|jpeg|webp|mp4>`
  4. THIS script: verifies the file is real (magic bytes, not zero bytes),
     installs it to the same fixed paths the automated path uses
     (hero-still.png / hero-poster.jpg / hero.mp4), and writes the dated
     `built` run record with engine "free".

Same fixed-path contract brand-website
and later lessons read those names either way. The record-keeping is
identical too: no asset lands without a dated record naming how it came
in.

On success: prints a human status line, then a final line of JSON:
  {"asset_path": "...", "bytes": N, "engine": "free", "model": "chatgpt-free"}
"""
from __future__ import annotations
import json
import shutil
import sys
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "records" / "assets"
INBOX_DIR = ASSETS_DIR / "inbox"
RUNS_DIR = ROOT / "records" / "runs"

HERO_STILL_PATH = ASSETS_DIR / "hero-still.png"
HERO_POSTER_PATH = ASSETS_DIR / "hero-poster.jpg"
HERO_VIDEO_PATH = ASSETS_DIR / "hero.mp4"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".webm"}

sys.path.insert(0, str(Path(__file__).resolve().parent))


def convert_to_jpg(src: Path, dst: Path) -> bool:
    """Real JPEG conversion via sips (macOS) with a Pillow fallback.
    Same behaviour the repo has always had for the hero poster."""
    if shutil.which("sips"):
        import subprocess
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


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_slug() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _is_hero(bid: str, kind: str) -> bool:
    """Hero brief suffix rule: `-hero-<kind>` or `-hero-<kind>-vN`."""
    marker = f"-hero-{kind}"
    if bid.endswith(marker):
        return True
    idx = bid.find(marker)
    rest = bid[idx + len(marker):] if idx != -1 else ""
    rest = rest.lstrip("-")
    return rest.startswith("v") and rest[1:].isdigit()


def sniff_kind(path: Path) -> str | None:
    """Return 'png' | 'jpeg' | 'webp' | 'mp4-family' | 'webm' | None."""
    try:
        head = path.read_bytes()[:32]
    except OSError:
        return None
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "webp"
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"
    if len(head) >= 8 and head[4:8] == b"ftyp":
        return "mp4-family"  # mp4 and mov share the ftyp box
    return None


def write_record(brief: dict, produced: dict) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "brief_id": brief.get("brief_id"),
        "recorded_at": now_iso(),
        "asked": brief.get("one_line_input"),
        "brief_snapshot": brief,
        "decision": "built",
        "decided_via": "free-path-collect",
        "engine": "free",
        "produced": produced,
        "error": None,
    }
    path = RUNS_DIR / f"{brief.get('brief_id', 'unknown')}-{now_slug()}.json"
    path.write_text(json.dumps(record, indent=2))
    return path


def find_inbox_file(brief_id: str) -> Path:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    matches = sorted(p for p in INBOX_DIR.iterdir() if p.is_file() and p.stem == brief_id)
    if not matches:
        print(
            f"NO FILE IN INBOX: expected records/assets/inbox/{brief_id}.<png|jpg|jpeg|webp|mp4>\n"
            f"Generate it in ChatGPT with the prompt the gate printed, download it,\n"
            f"and save it under exactly that name (keep the extension the download gave you).",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if len(matches) > 1:
        listed = ", ".join(p.name for p in matches)
        print(
            f"AMBIGUOUS INBOX: multiple files for this brief ({listed}).\n"
            f"Keep the one you want, delete the others, re-run.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return matches[0]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: collect_asset.py <brief.json>", file=sys.stderr)
        return 2
    brief_path = Path(sys.argv[1])
    if not brief_path.exists():
        print(f"ERROR: brief not found: {brief_path}", file=sys.stderr)
        return 2

    brief = json.loads(brief_path.read_text())
    brief_id = brief.get("brief_id", "unknown")
    src = find_inbox_file(brief_id)

    if src.stat().st_size == 0:
        print(f"EMPTY FILE: {src} is 0 bytes — the download failed. Re-download and re-run.", file=sys.stderr)
        return 1

    kind = sniff_kind(src)
    ext = src.suffix.lower()
    is_image_ext, is_video_ext = ext in IMAGE_EXTS, ext in VIDEO_EXTS
    if kind is None:
        print(
            f"UNRECOGNIZED FILE: {src.name} is not a PNG, JPEG, WebP, MP4/MOV or WebM "
            f"(magic bytes don't match any of them). ChatGPT exports as PNG or MP4 — "
            f"re-download the original export, don't rename another file to match.",
            file=sys.stderr,
        )
        return 1
    if kind == "mp4-family" and ext not in (".mp4", ".mov"):
        print(
            f"EXTENSION MISMATCH: {src.name} looks like video but its extension is {ext}. "
            f"Save the download with the extension it came with.",
            file=sys.stderr,
        )
        return 1
    if kind in ("png", "jpeg", "webp") and not is_image_ext:
        print(f"EXTENSION MISMATCH: {src.name} looks like an image ({kind}) but its extension is {ext}.", file=sys.stderr)
        return 1

    is_video = kind in ("mp4-family", "webm")

    # A .mov ChatGPT won't produce, but accept it for general briefs; hero needs mp4.
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ts = now_slug()

    if _is_hero(brief_id, "video"):
        if not HERO_STILL_PATH.exists():
            print(
                "HERO STILL NOT FOUND: expected `records/assets/hero-still.png` to already exist.\n"
                "Fix: collect the `<brand_id>-hero-still` brief first, then re-run this one.",
                file=sys.stderr,
            )
            return 1
        if ext != ".mp4":
            print(
                f"HERO VIDEO MUST BE .mp4: got {ext}. The site's <video> tag reads records/assets/hero.mp4.\n"
                "Re-download from ChatGPT/Sora as MP4 (their default export).",
                file=sys.stderr,
            )
            return 1
        dest = ASSETS_DIR / f"{brief_id}-{ts}.mp4"
        shutil.copyfile(src, dest)
        shutil.copyfile(dest, HERO_VIDEO_PATH)
        print(f"Hero video installed at fixed path: {HERO_VIDEO_PATH}")
        final = dest
    elif _is_hero(brief_id, "still"):
        dest = ASSETS_DIR / f"{brief_id}-{ts}{ext}"
        shutil.copyfile(src, dest)
        # hero-still.png is the fixed name everything reads — convert if needed.
        if kind == "png":
            shutil.copyfile(dest, HERO_STILL_PATH)
        else:
            converted = ASSETS_DIR / f"{brief_id}-{ts}-still.png"
            r = shutil.which("sips")
            import subprocess
            res = subprocess.run(["sips", "-s", "format", "png", str(dest), "--out", str(converted)],
                                 capture_output=True, text=True) if r else None
            if res is None or res.returncode != 0 or not converted.exists():
                print(
                    f"NOTE: could not convert {ext} to PNG (no `sips`). Save the ChatGPT\n"
                    f"download as PNG and re-run so {HERO_STILL_PATH} can be written.",
                    file=sys.stderr,
                )
                return 1
            shutil.copyfile(converted, HERO_STILL_PATH)
        print(f"Hero still installed at fixed path: {HERO_STILL_PATH}")
        if convert_to_jpg(HERO_STILL_PATH, HERO_POSTER_PATH):
            print(f"Hero poster written: {HERO_POSTER_PATH}")
        final = dest
    else:
        dest = ASSETS_DIR / f"{brief_id}-{ts}{ext}"
        shutil.copyfile(src, dest)
        print(f"Asset installed: {dest}")
        final = dest

    produced = {"asset_path": str(final), "bytes": final.stat().st_size,
                "engine": "free", "model": "chatgpt-free", "inbox_source": str(src)}
    record_path = write_record(brief, produced)
    print(f"Run record written: {record_path}")
    print(json.dumps(produced))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
