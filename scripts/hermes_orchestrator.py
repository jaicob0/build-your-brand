#!/usr/bin/env python3
"""One tick of the operations layer: run what is due, record all of it.

The timer calls this, not the agents. One job on the host, one file to
read, one audit trail. Adding an agent to the schedule never means
installing another timer.

Each tick:
  1. stops immediately if the kill switch is on
  2. refuses to start if the central allowlist has drifted from the specs
  3. drains records/ops/events/inbox/ and runs what the events name
  4. finds the scheduled agents whose cadence is due
  5. runs each through scripts/hermes_run.py --go --by timer, which
     enforces the halt, the allowlist, the human-in-the-loop tier, the
     gate, the credentials and the trigger
  6. writes last_run back to records/ops/schedule.json
  7. appends a tick summary to the append-only audit log

Usage:
  python3 scripts/hermes_orchestrator.py            # run what is due
  python3 scripts/hermes_orchestrator.py --dry-run  # say what is due, run nothing
  python3 scripts/hermes_orchestrator.py --force    # ignore cadence, run all scheduled

Exit 0 when the tick completed, 1 when a run failed or the allowlist
drifted.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "records" / "ops"
SCHEDULE = OPS / "schedule.json"
AUDIT = OPS / "audit.log"


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp() -> str:
    return now().isoformat(timespec="seconds")


def audit(event: dict) -> None:
    OPS.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({"at": stamp(), **event}) + "\n")


def due(entry: dict, force: bool) -> bool:
    if not entry.get("installed"):
        return False
    if force:
        return True
    last = entry.get("last_run")
    if not last:
        return True
    try:
        elapsed = (now() - datetime.fromisoformat(last)).total_seconds() / 60
    except ValueError:
        return True
    return elapsed >= float(entry.get("every_minutes", 60))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT / "scripts"))
    from hermes_halt import halted  # noqa: E402 - same directory, stdlib only
    from hermes_events import archive, pending  # noqa: E402

    is_halted, why = halted()
    if is_halted:
        audit({"event": "tick_halted", "reason": why})
        print(f"HALTED · {why}")
        print("Nothing ran. Resume with: python3 scripts/hermes_halt.py --resume")
        return 0

    drift = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "allowlist_build.py"), "--check"],
        capture_output=True, text=True,
    )
    if drift.returncode == 1:
        audit({"event": "tick_refused", "reason": "allowlist drifted from specs"})
        print("REFUSED: the central allowlist no longer matches the specs.")
        print(drift.stdout.strip())
        print("Run scripts/allowlist_build.py, read the difference, then start the layer again.")
        return 1

    ran, skipped, failed, events = [], [], [], []

    # Events first: something already happened, so it is older than any timer.
    for path in pending():
        try:
            event = json.loads(path.read_text())
        except json.JSONDecodeError:
            print(f"SKIPPED (not valid JSON): {path.name}")
            continue
        if args.dry_run:
            print(f"EVENT: {event['agent_id']} · {event.get('task', '')}")
            events.append(event["agent_id"])
            continue
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "hermes_run.py"), event["agent_id"],
             "--task", event.get("task", ""), "--go", "--by", "timer"],
            cwd=ROOT, capture_output=True, text=True,
        )
        print(proc.stdout.strip())
        archive(path)
        events.append(event["agent_id"])
        if proc.returncode != 0:
            failed.append(event["agent_id"])

    if not SCHEDULE.exists():
        audit({"event": "tick", "ran": ran, "events": events, "skipped": skipped,
               "failed": failed, "dry_run": args.dry_run})
        print(f"tick · events {len(events)} · nothing scheduled")
        return 1 if failed else 0

    schedule = json.loads(SCHEDULE.read_text())

    for agent_id, entry in schedule.items():
        if not due(entry, args.force):
            skipped.append(agent_id)
            continue
        if args.dry_run:
            ran.append(agent_id)
            print(f"DUE: {agent_id} · {entry.get('task', '')}")
            continue
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "hermes_run.py"), agent_id,
             "--task", entry.get("task", ""), "--go", "--by", "timer"],
            cwd=ROOT, capture_output=True, text=True,
        )
        print(proc.stdout.strip())
        entry["last_run"] = stamp()
        (failed if proc.returncode != 0 else ran).append(agent_id)

    if not args.dry_run:
        SCHEDULE.write_text(json.dumps(schedule, indent=2) + "\n")

    audit({"event": "tick", "ran": ran, "events": events, "skipped": skipped,
           "failed": failed, "dry_run": args.dry_run})
    print(f"tick · ran {len(ran)} · events {len(events)} · not due {len(skipped)} · failed {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
