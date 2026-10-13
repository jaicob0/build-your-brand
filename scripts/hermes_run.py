#!/usr/bin/env python3
"""Run one agent under the Hermes rules, and write the record either way.

Hermes is the part that says no. Every run is checked against the
agent's own spec.json before anything happens, and every run leaves a
dated record in records/ops/runs/ whether it ran, refused or failed.

Three refusals are built in:
  - the spec is missing or invalid          -> refused:spec
  - the tool named is not on the allowlist  -> refused:allowlist
  - the agent needs the gate and has no
    approval on record for this run         -> refused:gate

Usage:
  python3 scripts/hermes_run.py <agent_id> --task "..." [--tool NAME] [--go]

Default is a check: it validates, records, and prints what would run,
without executing anything. --go executes, and only for agents whose
spec says gate.required is false. Anything gated goes through
scripts/approval_gate.py and a human keystroke first, exactly as in
Lesson 8.

Exit 0 when the outcome is the correct one (including a correct
refusal). Exit 1 on a real failure.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "records" / "agents"
RUNS = ROOT / "records" / "ops" / "runs"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record(agent_id: str, decision: str, detail: dict) -> Path:
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = now().replace(":", "").replace("-", "")
    path = RUNS / f"{stamp}-{agent_id}.json"
    # Two runs inside the same second must not overwrite each other. A
    # record that can be silently replaced is not a record.
    n = 2
    while path.exists():
        path = RUNS / f"{stamp}-{agent_id}-{n}.json"
        n += 1
    payload = {"agent_id": agent_id, "ran_at": now(), "decision": decision}
    payload.update(detail)
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_spec(agent_id: str) -> tuple[dict | None, str]:
    spec_path = AGENTS / agent_id / "spec.json"
    if not spec_path.exists():
        return None, f"no spec at {spec_path.relative_to(ROOT)}"
    try:
        spec = json.loads(spec_path.read_text())
    except json.JSONDecodeError as e:
        return None, f"spec is not valid JSON: {e}"
    validator = ROOT / "scripts" / "validate_brief.py"
    proc = subprocess.run(
        [sys.executable, str(validator), str(spec_path), "--schema", "agent_spec"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None, proc.stdout.strip() or "spec failed validation"
    return spec, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    ap.add_argument("--task", required=True, help="the real task, in the student's words")
    ap.add_argument("--tool", default=None, help="the tool or command this run would use")
    ap.add_argument("--go", action="store_true", help="execute, instead of checking")
    args = ap.parse_args()

    spec, err = load_spec(args.agent_id)
    if spec is None:
        path = record(args.agent_id, "refused:spec", {"task": args.task, "reason": err})
        print(f"REFUSED (spec): {err}")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    if args.tool and args.tool not in spec["allowed_tools"]:
        path = record(args.agent_id, "refused:allowlist", {
            "task": args.task, "tool": args.tool, "allowed_tools": spec["allowed_tools"],
        })
        print(f"REFUSED (allowlist): '{args.tool}' is not on {args.agent_id}'s allowlist")
        print(f"allowed: {', '.join(spec['allowed_tools'])}")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    gated = bool(spec["gate"]["required"])
    if gated and args.go:
        path = record(args.agent_id, "refused:gate", {
            "task": args.task, "trigger": spec["gate"]["trigger"],
        })
        print(f"REFUSED (gate): {args.agent_id} is gated on {spec['gate']['trigger']}.")
        print("Run scripts/approval_gate.py and answer it yourself before this runs.")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    if not args.go:
        path = record(args.agent_id, "checked", {
            "task": args.task, "tool": args.tool, "gated": gated,
            "escalate_when": spec["escalate_when"],
        })
        print(f"OK: {args.agent_id} may run this task.")
        print(f"  job:       {spec['job']}")
        print(f"  writes:    {spec['writes']}")
        print(f"  gated:     {'yes, on ' + spec['gate']['trigger'] if gated else 'no'}")
        print(f"  escalates: {'; '.join(spec['escalate_when'])}")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    agent_md = AGENTS / args.agent_id / "AGENT.md"
    if not agent_md.exists():
        path = record(args.agent_id, "refused:spec", {
            "task": args.task, "reason": f"no AGENT.md at {agent_md.relative_to(ROOT)}",
        })
        print(f"REFUSED (spec): {args.agent_id} has no AGENT.md to run from")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    claude = shutil.which("claude")
    if not claude:
        path = record(args.agent_id, "failed", {"task": args.task, "reason": "claude not on PATH"})
        print("FAILED: claude is not on PATH. launchd does not inherit your shell PATH;")
        print("scripts/hermes_schedule.py writes the absolute path into the job for that reason.")
        print(f"record: {path.relative_to(ROOT)}")
        return 1

    prompt = (
        f"{agent_md.read_text()}\n\n"
        f"---\nUnattended run. Task: {args.task}\n"
        f"Write your output into {spec['writes']}. "
        "If any escalation rule above applies, write nothing and reply with "
        "ESCALATE followed by the reason."
    )
    proc = subprocess.run(
        [claude, "-p", prompt], cwd=ROOT, capture_output=True, text=True,
    )
    out = (proc.stdout or "").strip()
    escalated = out.startswith("ESCALATE")
    path = record(args.agent_id, "escalated" if escalated else "ran", {
        "task": args.task,
        "writes": spec["writes"],
        "exit_code": proc.returncode,
        "output": out[:4000],
        "stderr": (proc.stderr or "").strip()[:2000],
    })
    print("ESCALATED" if escalated else f"RAN (exit {proc.returncode})")
    print(f"record: {path.relative_to(ROOT)}")
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
