#!/usr/bin/env python3
"""The kill switch. One command halts every agent at once.

A guardrail you have not tested is a belief, and this is the one you
will reach for in a hurry. It is a single file, checked by every run,
so it works whether the layer is on a timer, in a container, or being
run by hand.

Usage:
  python3 scripts/hermes_halt.py            # halt everything, now
  python3 scripts/hermes_halt.py --resume   # let it run again
  python3 scripts/hermes_halt.py --status

While halted, every agent refuses with decision "refused:halt" and
writes the record, so the pause is on file like everything else. The
environment variable HERMES_HALT=1 does the same thing for a container
without touching the repo.
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "records" / "ops"
HALT = OPS / "HALT"
AUDIT = OPS / "audit.log"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def halted() -> tuple[bool, str]:
    if os.environ.get("HERMES_HALT") == "1":
        return True, "HERMES_HALT=1 in the environment"
    if HALT.exists():
        return True, HALT.read_text().strip() or f"halted, {HALT.relative_to(ROOT)}"
    return False, ""


def audit(event: dict) -> None:
    OPS.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({"at": now(), **event}) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--reason", default="halted by hand")
    args = ap.parse_args()

    if args.status:
        is_halted, why = halted()
        print(f"HALTED · {why}" if is_halted else "running (not halted)")
        return 0

    if args.resume:
        if HALT.exists():
            HALT.unlink()
        audit({"event": "resumed"})
        print("resumed. Agents may run again.")
        if os.environ.get("HERMES_HALT") == "1":
            print("NOTE: HERMES_HALT=1 is still set in this environment and still halts runs.")
        return 0

    OPS.mkdir(parents=True, exist_ok=True)
    HALT.write_text(f"{args.reason} · {now()}\n")
    audit({"event": "halted", "reason": args.reason})
    print(f"HALTED. Every agent now refuses. ({HALT.relative_to(ROOT)})")
    print("Resume with: python3 scripts/hermes_halt.py --resume")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
