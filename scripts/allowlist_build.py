#!/usr/bin/env python3
"""Build the one permissions file the whole layer is read and audited from.

Every agent carries its own allowlist in its spec. This collects them
into records/ops/allowlist.json, which is the file a human reads when
they want to know what the system can do, and the file they tighten
when the answer is "too much".

At run time the effective permission is the INTERSECTION of the two:
an agent may use a tool only if its spec allows it AND this file
allows it. Tightening here can never be undone by editing a spec.

Usage:
  python3 scripts/allowlist_build.py            # build or refresh
  python3 scripts/allowlist_build.py --check    # diff only, write nothing

Existing entries are preserved: if you have hand-tightened an agent's
list, a rebuild keeps your narrower list and records what it withheld.
A tool a spec later asks for that is in neither list is a tool nobody
reviewed, and --check calls that drift.
Exit 0 on success, 1 when --check finds drift.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "records" / "agents"
OPS = ROOT / "records" / "ops"
ALLOWLIST = OPS / "allowlist.json"


def specs() -> dict[str, dict]:
    out = {}
    if not AGENTS.exists():
        return out
    for spec_path in sorted(AGENTS.glob("*/spec.json")):
        try:
            spec = json.loads(spec_path.read_text())
        except json.JSONDecodeError:
            print(f"SKIPPED (not valid JSON): {spec_path.relative_to(ROOT)}", file=sys.stderr)
            continue
        out[spec.get("agent_id", spec_path.parent.name)] = spec
    return out


def entry(spec: dict) -> dict:
    return {
        "job": spec["job"],
        # The three tiers, in the order the runner applies them:
        # runs alone / drafts for a human / refuses outright.
        "allowed_tools": sorted(spec["allowed_tools"]),
        "human_in_the_loop": sorted(spec.get("human_in_the_loop", [])),
        "escalate_when": sorted(spec["escalate_when"]),
        "forbidden": sorted(spec["forbidden"]),
        "mcp": sorted(spec.get("mcp", [])),
        "gated": bool(spec["gate"]["required"]),
        "gate_trigger": spec["gate"]["trigger"],
        "credentials": sorted(spec.get("credentials", [])),
        "trigger": spec["trigger"]["mode"],
        "autonomous": not bool(spec["gate"]["required"]) and not spec.get("dry_run", False),
        # Tools the spec asks for and a human deliberately withheld here.
        # A tool in neither list is one nobody has reviewed.
        "withheld": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    found = specs()
    if not found:
        print("No agent specs in records/agents/. Nothing to collect.")
        return 0

    current = {}
    if ALLOWLIST.exists():
        current = json.loads(ALLOWLIST.read_text()).get("agents", {})

    agents, notes = {}, []
    for agent_id, spec in found.items():
        fresh = entry(spec)
        held = current.get(agent_id)
        if held:
            # A hand-tightened list is never widened by a rebuild.
            kept = [t for t in fresh["allowed_tools"] if t in held.get("allowed_tools", [])]
            dropped = sorted(set(fresh["allowed_tools"]) - set(kept))
            unreviewed = sorted(set(dropped) - set(held.get("withheld", [])))
            if unreviewed:
                notes.append(
                    f"{agent_id}: spec now asks for {', '.join(unreviewed)}, "
                    "which nobody has allowed or withheld here")
            if dropped:
                notes.append(f"{agent_id}: kept tightened list, withholding {', '.join(dropped)}")
            fresh["allowed_tools"] = kept or held.get("allowed_tools", [])
            fresh["withheld"] = dropped
            extra = sorted(set(held.get("forbidden", [])) - set(fresh["forbidden"]))
            if extra:
                fresh["forbidden"] = sorted(set(fresh["forbidden"]) | set(extra))
        agents[agent_id] = fresh

    gone = sorted(set(current) - set(agents))
    for agent_id in gone:
        notes.append(f"{agent_id}: in allowlist but has no spec, left in place for you to remove")
        agents[agent_id] = current[agent_id]

    payload = {
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rule": "effective permission = spec.allowed_tools INTERSECT allowlist.allowed_tools",
        "tiers": {
            "allowed_tools": "runs alone, the safe and well-trodden work",
            "human_in_the_loop": "drafted and handed over: irreversible, money-moving, reputation-risking",
            "escalate_when": "stops and routes to the channel in records/ops/channel.json",
            "forbidden": "refused outright, even when asked directly",
        },
        "agents": agents,
    }

    if args.check:
        # Drift is either a changed entry, or a tool the spec now asks for
        # that this file neither allows nor deliberately withholds.
        unreviewed = [n for n in notes if "nobody has allowed or withheld" in n]
        same = current == agents and not unreviewed
        print("allowlist matches the specs" if same else "allowlist DRIFTS from the specs")
        for n in notes:
            print(f"  - {n}")
        return 0 if same else 1

    OPS.mkdir(parents=True, exist_ok=True)
    ALLOWLIST.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{ALLOWLIST.relative_to(ROOT)} written: {len(agents)} agent(s)")
    for agent_id, a in agents.items():
        shape = "gated" if a["gated"] else ("dry-run" if not a["autonomous"] else "autonomous")
        print(f"  {agent_id:<24} {shape:<12} tools: {', '.join(a['allowed_tools']) or 'none'}")
        if a["human_in_the_loop"]:
            print(f"  {'':<24} {'':<12} drafts only: {', '.join(a['human_in_the_loop'])}")
    for n in notes:
        print(f"  - {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
