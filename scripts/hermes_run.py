#!/usr/bin/env python3
"""Run one agent under the Hermes rules, and write the record either way.

Hermes is the part that says no. Every run is checked against the
agent's own spec AND the central records/ops/allowlist.json before
anything happens, and every run appends to the audit log whether it
ran, refused, escalated or failed.

Effective permission is the INTERSECTION of the two lists, so
tightening the central file can never be undone by editing a spec.

Seven refusals are built in:
  - the kill switch is on                     -> refused:halt
  - the spec is missing or invalid            -> refused:spec
  - the tool named is off the effective list  -> refused:allowlist
  - the action is human-in-the-loop, so it is
    drafted and handed over, never executed   -> refused:hitl
  - a credential the spec names is not in
    the environment                           -> refused:credentials
  - the agent needs the gate and has no
    approval on record for this run           -> refused:gate
  - the agent is on-demand and something
    other than a human asked                  -> refused:trigger

Every run updates records/ops/heartbeat.json, so the dashboard can show
which agents are alive and when each last finished cleanly. Customer
data in a recorded output is masked before it is written.

Usage:
  python3 scripts/hermes_run.py <agent_id> --task "..." [--tool NAME]
                                [--action NAME] [--go] [--by human|timer]

Default is a check: it validates, records, prints what would run, and
executes nothing. --go executes, and only for agents whose spec says
gate.required is false. Anything gated goes through
scripts/approval_gate.py and a human keystroke first, as in Lesson 8.

Exit 0 when the outcome is the correct one (including a correct
refusal). Exit 1 on a real failure.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "records" / "agents"
OPS = ROOT / "records" / "ops"
RUNS = OPS / "runs"
AUDIT = OPS / "audit.log"
ALLOWLIST = OPS / "allowlist.json"
HEARTBEAT = OPS / "heartbeat.json"

# Anything that could identify a real customer is masked before it is
# written, so a record and a screen recording are safe to share.
# Order matters: the longest, most specific pattern goes first, or a card
# number gets masked as a phone number.
MASKS = (
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    (re.compile(r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)"), "[CARD]"),
    (re.compile(r"\+?\d[\d ()-]{8,}\d"), "[PHONE]"),
    (re.compile(r"#\d{4,}"), "[ORDER#]"),
)


def mask(text: str) -> str:
    for pattern, token in MASKS:
        text = pattern.sub(token, text)
    return text


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def audit(event: dict) -> None:
    """Append-only. Nothing in this repo rewrites or truncates it."""
    OPS.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({"at": now(), **event}) + "\n")


def heartbeat(agent_id: str, decision: str) -> None:
    OPS.mkdir(parents=True, exist_ok=True)
    beats = json.loads(HEARTBEAT.read_text()) if HEARTBEAT.exists() else {}
    beat = beats.get(agent_id, {})
    beat["last_seen"] = now()
    beat["last_decision"] = decision
    if decision in ("ran", "checked"):
        beat["last_ok"] = now()
    beats[agent_id] = beat
    HEARTBEAT.write_text(json.dumps(beats, indent=2) + "\n")


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
    audit({"event": "run", "agent_id": agent_id, "decision": decision,
           "record": str(path.relative_to(ROOT))})
    heartbeat(agent_id, decision)
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


def effective_tools(spec: dict) -> tuple[list[str], str]:
    """spec.allowed_tools INTERSECT the central allowlist, when one exists."""
    tools = list(spec["allowed_tools"])
    if not ALLOWLIST.exists():
        return tools, "spec only (no central allowlist built yet)"
    central = json.loads(ALLOWLIST.read_text()).get("agents", {}).get(spec["agent_id"])
    if not central:
        return [], "the central allowlist has no entry for this agent"
    narrowed = [t for t in tools if t in central.get("allowed_tools", [])]
    return narrowed, "spec INTERSECT records/ops/allowlist.json"


def missing_credentials(spec: dict) -> list[str]:
    return [name for name in spec.get("credentials", []) if not os.environ.get(name)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    ap.add_argument("--task", required=True, help="the real task, in the student's words")
    ap.add_argument("--tool", default=None, help="the tool or command this run would use")
    ap.add_argument("--action", default=None,
                    help="the business action this run would take, e.g. issue_refund")
    ap.add_argument("--go", action="store_true", help="execute, instead of checking")
    ap.add_argument("--by", choices=["human", "timer"], default="human",
                    help="who asked for this run. The timer passes 'timer'.")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT / "scripts"))
    from hermes_halt import halted  # noqa: E402 - same directory, stdlib only

    is_halted, why = halted()
    if is_halted:
        path = record(args.agent_id, "refused:halt", {"task": args.task, "reason": why})
        print(f"REFUSED (halt): the kill switch is on — {why}")
        print("Resume with: python3 scripts/hermes_halt.py --resume")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    spec, err = load_spec(args.agent_id)
    if spec is None:
        path = record(args.agent_id, "refused:spec", {"task": args.task, "reason": err})
        print(f"REFUSED (spec): {err}")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    tools, source = effective_tools(spec)

    if args.tool and args.tool not in tools:
        path = record(args.agent_id, "refused:allowlist", {
            "task": args.task, "tool": args.tool,
            "effective_tools": tools, "allowlist_source": source,
        })
        print(f"REFUSED (allowlist): '{args.tool}' is not on {args.agent_id}'s effective list")
        print(f"allowed: {', '.join(tools) or 'nothing'}  ({source})")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    if args.action and args.action in spec.get("human_in_the_loop", []):
        path = record(args.agent_id, "refused:hitl", {
            "task": args.task, "action": args.action,
            "human_in_the_loop": spec.get("human_in_the_loop", []),
        })
        print(f"REFUSED (human in the loop): '{args.action}' is drafted, never executed alone.")
        print("It is irreversible, moves money, or carries reputation risk. A person does it.")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "hermes_escalate.py"),
                        args.agent_id, "--reason",
                        f"'{args.action}' needs a human. Drafted, not executed.",
                        "--task", args.task])
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    if args.by == "timer" and spec["trigger"]["mode"] == "on-demand":
        path = record(args.agent_id, "refused:trigger", {
            "task": args.task, "trigger": spec["trigger"],
        })
        print(f"REFUSED (trigger): {args.agent_id} is on-demand. A timer does not get to ask.")
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

    absent = missing_credentials(spec)
    if absent and args.go:
        path = record(args.agent_id, "refused:credentials", {
            "task": args.task, "missing": absent,
        })
        print(f"REFUSED (credentials): not set in this environment: {', '.join(absent)}")
        print("Set them where the layer runs. Never in the repo, never in a record.")
        print(f"record: {path.relative_to(ROOT)}")
        return 0

    if not args.go:
        path = record(args.agent_id, "checked", {
            "task": args.task, "tool": args.tool, "gated": gated,
            "effective_tools": tools, "allowlist_source": source,
            "dry_run": bool(spec.get("dry_run", False)),
            "credentials_missing": absent,
            "human_in_the_loop": spec.get("human_in_the_loop", []),
            "escalate_when": spec["escalate_when"],
        })
        print(f"OK: {args.agent_id} may run this task.")
        print(f"  job:       {spec['job']}")
        print(f"  writes:    {spec['writes']}")
        print(f"  trigger:   {spec['trigger']['mode']} · {spec['trigger']['cadence']}")
        print(f"  tools:     {', '.join(tools) or 'nothing'}  ({source})")
        print(f"  gated:     {'yes, on ' + spec['gate']['trigger'] if gated else 'no'}")
        hitl = spec.get("human_in_the_loop", [])
        print(f"  drafts only: {'; '.join(hitl) if hitl else 'nothing — it executes everything it may do'}")
        print(f"  dry run:   {'yes, composes and hands back' if spec.get('dry_run') else 'no'}")
        if absent:
            print(f"  missing:   {', '.join(absent)} (would refuse on --go)")
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

    mode = ("DRY RUN. Compose the action and write it as a draft for a human to send or "
            "execute. Perform nothing yourself."
            if spec.get("dry_run") else
            "Unattended run.")
    prompt = (
        f"{agent_md.read_text()}\n\n"
        f"---\n{mode}\nTask: {args.task}\n"
        f"You may use only these tools: {', '.join(tools) or 'none'}.\n"
        + (f"Draft, never execute, any of these: {', '.join(spec['human_in_the_loop'])}.\n"
           if spec.get("human_in_the_loop") else "")
        + 
        f"Write your output into {spec['writes']}. "
        "If any escalation rule above applies, write nothing and reply with "
        "ESCALATE followed by the reason."
    )
    proc = subprocess.run([claude, "-p", prompt], cwd=ROOT, capture_output=True, text=True)
    out = (proc.stdout or "").strip()
    escalated = out.startswith("ESCALATE")
    path = record(args.agent_id, "escalated" if escalated else "ran", {
        "task": args.task,
        "writes": spec["writes"],
        "dry_run": bool(spec.get("dry_run", False)),
        "exit_code": proc.returncode,
        "output": mask(out[:4000]),
        "stderr": mask((proc.stderr or "").strip()[:2000]),
    })
    if escalated:
        reason = out[len("ESCALATE"):].strip(" :-\n") or "no reason given"
        subprocess.run([sys.executable, str(ROOT / "scripts" / "hermes_escalate.py"),
                        args.agent_id, "--reason", reason, "--task", args.task])
    print("ESCALATED" if escalated else f"RAN (exit {proc.returncode})")
    print(f"record: {path.relative_to(ROOT)}")
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
