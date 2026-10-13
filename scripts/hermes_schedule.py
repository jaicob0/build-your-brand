#!/usr/bin/env python3
"""Write the launchd job that runs one agent on a cadence. Print by default.

Scheduling is the step where an agent starts acting without you in the
room, so nothing is installed unless you ask for it in the same command
you read.

Usage:
  python3 scripts/hermes_schedule.py <agent_id> --task "..." --every <minutes>
  python3 scripts/hermes_schedule.py <agent_id> --task "..." --every 60 --install
  python3 scripts/hermes_schedule.py <agent_id> --uninstall

Default prints the plist and the two commands that would install it,
and writes nothing outside records/ops/. --install writes the plist to
~/Library/LaunchAgents/ and loads it. --uninstall unloads and removes
it.

launchd does not inherit your shell PATH, so the job carries absolute
paths for python3 and for the repo. That is the single most common
reason a scheduled job never fires.
"""
from __future__ import annotations
import argparse
import json
import plistlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "records" / "ops"
LAUNCH_AGENTS = Path.home() / "Library" / "LaunchAgents"


def label(agent_id: str) -> str:
    return f"uk.thecreativearchitect.byb.{agent_id}"


def build_plist(agent_id: str, task: str, every: int) -> dict:
    return {
        "Label": label(agent_id),
        "ProgramArguments": [
            sys.executable,
            str(ROOT / "scripts" / "hermes_run.py"),
            agent_id,
            "--task", task,
            "--go",
        ],
        "WorkingDirectory": str(ROOT),
        "StartInterval": every * 60,
        "RunAtLoad": False,
        "StandardOutPath": str(OPS / "launchd.out.log"),
        "StandardErrorPath": str(OPS / "launchd.err.log"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    ap.add_argument("--task", default=None)
    ap.add_argument("--every", type=int, default=None, help="minutes between runs")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()

    OPS.mkdir(parents=True, exist_ok=True)
    plist_path = LAUNCH_AGENTS / f"{label(args.agent_id)}.plist"

    if args.uninstall:
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        if plist_path.exists():
            plist_path.unlink()
        print(f"unloaded and removed: {plist_path}")
        return 0

    if not args.task or not args.every:
        print("ERROR: --task and --every are required unless you pass --uninstall", file=sys.stderr)
        return 2

    spec = ROOT / "records" / "agents" / args.agent_id / "spec.json"
    if not spec.exists():
        print(f"ERROR: no spec at {spec.relative_to(ROOT)}. Build the agent first.", file=sys.stderr)
        return 2
    if json.loads(spec.read_text())["gate"]["required"]:
        print(f"REFUSED: {args.agent_id} is gated. A gated agent does not run unattended.")
        print("Drop the gated action from its spec, or run it by hand through the gate.")
        return 0
    if not shutil.which("claude"):
        print("WARNING: claude is not on your PATH. The job will fail at run time.")

    plist = build_plist(args.agent_id, args.task, args.every)
    rendered = plistlib.dumps(plist).decode()

    manifest = OPS / "schedule.json"
    existing = json.loads(manifest.read_text()) if manifest.exists() else {}
    existing[args.agent_id] = {
        "label": plist["Label"], "task": args.task, "every_minutes": args.every,
        "installed": bool(args.install),
        "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    manifest.write_text(json.dumps(existing, indent=2))

    if not args.install:
        print(rendered)
        print(f"Would install to: {plist_path}")
        print(f"Then: launchctl load {plist_path}")
        print(f"\nRecorded in {manifest.relative_to(ROOT)} as not installed.")
        print("Re-run with --install when you have read the above.")
        return 0

    LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)
    plist_path.write_bytes(plistlib.dumps(plist))
    subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
    proc = subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"launchctl load failed: {proc.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"installed and loaded: {plist_path}")
    print(f"every {args.every} minutes · logs in {OPS.relative_to(ROOT)}/launchd.*.log")
    print(f"stop it with: python3 scripts/hermes_schedule.py {args.agent_id} --uninstall")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
