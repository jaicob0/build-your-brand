#!/usr/bin/env python3
"""Approval gate: show a brief, take a human decision, write a dated record.

Usage:
  python3 scripts/approval_gate.py <brief.json>                 # in YOUR terminal: prompts you
  python3 scripts/approval_gate.py --decision y <brief.json>    # after you typed y to Claude
  python3 scripts/approval_gate.py --decision n <brief.json>    # after you typed anything else
  python3 scripts/approval_gate.py --decision y --engine higgsfield <brief.json>
                                                                # optional pro engine: automated
                                                                # build via the Higgsfield CLI
                                                                # (spends real credits)

How the gate holds:
  - In a real terminal with no --decision, it prints the brief and asks
    "Approve build? [y/N]". You type the answer.
  - With --decision, it records the decision you already gave Claude in the
    session. Claude Code's own permission dialog shows the exact command,
    --decision included, before it runs; only a human can allow it
    (.claude/settings.json lists this script under "ask").
  - Piped stdin is refused. `echo y | approval_gate.py` writes no record.
  - On y with the default free engine it prints a paste-ready prompt for
    ChatGPT and records the approval; you generate the asset yourself
    (free, no credits spent), save it to records/assets/inbox/<brief_id>.<ext>,
    then run scripts/collect_asset.py to verify, install and record it.
  - On y with --engine higgsfield it runs scripts/hephaestus_build.py, which
    builds via the Higgsfield CLI (real credits) and downloads the asset.
    Direct calls to hephaestus_build.py are denied in .claude/settings.json,
    so the gate and its record wrap every build on either engine.

Record file: records/runs/<brief_id>-<timestamp>.json
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "records" / "runs"
BUILD_SCRIPT = ROOT / "scripts" / "hephaestus_build.py"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_slug() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def prompt_from_brief(brief: dict) -> str:
    """The paste-ready prompt the free path prints: the brief's creative
    intent, as written, for the student to paste into ChatGPT."""
    parts = [
        brief.get("big_idea", ""),
        brief.get("visual_description", ""),
        brief.get("style_notes", ""),
    ]
    if brief.get("must_preserve"):
        parts.append("Must preserve: " + "; ".join(brief["must_preserve"]) + ".")
    if brief.get("forbidden"):
        parts.append("Do not include: " + "; ".join(brief["forbidden"]) + ".")
    prompt = " ".join(p.strip() for p in parts if p and p.strip())
    ar = brief.get("aspect_ratio")
    if ar:
        prompt += f" Aspect ratio {ar}."
    return prompt


def write_record(brief: dict, decision: str, decided_via: str, produced: dict | None, error: str | None) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "brief_id": brief.get("brief_id"),
        "recorded_at": now_iso(),
        "asked": brief.get("one_line_input"),
        "brief_snapshot": brief,
        "decision": decision,
        "decided_via": decided_via,
        "produced": produced,
        "error": error,
    }
    path = RUNS_DIR / f"{brief.get('brief_id', 'unknown')}-{now_slug()}.json"
    path.write_text(json.dumps(record, indent=2))
    return path


def show(brief: dict) -> None:
    print("=" * 60)
    print("CREATIVE BRIEF — REVIEW BEFORE BUILD")
    print("=" * 60)
    print(f"brief_id:      {brief.get('brief_id')}")
    print(f"asset_type:    {brief.get('asset_type', 'general')}")
    print(f"one_line_input:{brief.get('one_line_input')}")
    print(f"big_idea:      {brief.get('big_idea')}")
    print(f"visual:        {brief.get('visual_description')}")
    print(f"style:         {brief.get('style_notes')}")
    print(f"aspect_ratio:  {brief.get('aspect_ratio')}")
    print(f"must_preserve: {brief.get('must_preserve')}")
    print(f"forbidden:     {brief.get('forbidden')}")
    is_video = str(brief.get("brief_id", "")).find("-hero-video") != -1 or brief.get("asset_type") == "hero-video"
    tool = "ChatGPT/Sora (video)" if is_video else "ChatGPT (image)"
    print(f"will use:      {tool} — free path, you generate, nothing is spent")
    print(f"pro option:    --engine higgsfield — automated build, real credits")
    print("=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--decision", choices=["y", "n"], default=None,
                        help="the answer the human already gave in the Claude session")
    parser.add_argument("--engine", choices=["free", "higgsfield"], default="free",
                        help="free (default): you generate in ChatGPT, nothing spent. "
                             "higgsfield: automated build via the Higgsfield CLI — real credits.")
    args = parser.parse_args()

    if not args.brief.exists():
        print(f"ERROR: brief not found: {args.brief}", file=sys.stderr)
        return 2
    brief = json.loads(args.brief.read_text())

    show(brief)

    if args.decision is not None:
        answer = args.decision
        decided_via = "session-answer-then-permission-dialog"
    elif sys.stdin.isatty():
        answer = input("Approve build? [y/N] ").strip().lower()
        decided_via = "terminal"
    else:
        sys.stdout.flush()
        print(
            "NO HUMAN AT THE GATE: stdin is not a terminal and no --decision was given.\n"
            "Piped input is not accepted. Either run this in your own terminal, or answer\n"
            "Claude's `Approve build? [y/N]` in the session and let it re-run with\n"
            "--decision y or --decision n. Nothing was built and nothing was recorded.",
            file=sys.stderr,
        )
        return 2

    if answer != "y":
        record_path = write_record(brief, "rejected", decided_via, None, None)
        print(f"REJECTED. Record written: {record_path}")
        return 0

    if args.engine == "higgsfield":
        print("APPROVED. Pro engine — Higgsfield CLI, real credits. Building...")
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT), str(args.brief)],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            record_path = write_record(brief, "approved-build-failed", decided_via, None, result.stderr.strip()[-2000:])
            print(f"BUILD FAILED. Record written: {record_path}")
            return 1
        produced = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    produced = json.loads(line)
                except json.JSONDecodeError:
                    pass
        record_path = write_record(brief, "built", decided_via, produced, None)
        print(f"BUILT. Record written: {record_path}")
        return 0

    print("APPROVED. Free path — nothing is spent, nothing is auto-generated.")
    print()
    print("-" * 60)
    print("PASTE THIS PROMPT INTO CHATGPT")
    print("(ChatGPT for images; ChatGPT/Sora for video):")
    print("-" * 60)
    print()
    print(prompt_from_brief(brief))
    print()
    print("-" * 60)
    print("THEN")
    print("-" * 60)
    print(f"1. Download the result from ChatGPT.")
    print(f"2. Save it as records/assets/inbox/{brief.get('brief_id', 'unknown')}.png")
    print(f"   (or .mp4 for video — keep the extension the download gave you).")
    print(f"3. Run:  python3 scripts/collect_asset.py {args.brief}")
    print(f"   That verifies the file, installs it to records/assets/, and")
    print(f"   writes the dated build record.")
    print("-" * 60)
    record_path = write_record(brief, "approved-free-path", decided_via, None, None)
    print(f"APPROVAL recorded: {record_path}")
    print("When the file is in the inbox, collect it with scripts/collect_asset.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
