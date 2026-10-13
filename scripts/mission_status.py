#!/usr/bin/env python3
"""Emit the numbers Mission Control renders, and label every one of them.

Reads records/mission-control/sources.json (the tile map the student
agreed in Lesson 10) and writes records/mission-control/status.json.

Every tile comes out carrying its own provenance:
  live        a real value, from a file on disk or a connected source
  placeholder no source wired yet, the value is illustrative
  missing     a source was named and it is not there

A tile never carries yesterday's number, and never a guess. The page
renders the label next to the value, so nobody quotes a placeholder by
accident.

Sources a tile can declare:
  {"kind": "count_files", "path": "records/assets", "pattern": "*.png"}
  {"kind": "count_runs",  "decision": "built"}
  {"kind": "json_field",  "path": "records/x.json", "field": "a.b.c"}
  {"kind": "agent_runs",  "agent_id": "support-drafts"}
  {"kind": "http",        "url_env": "BYB_METRIC_URL", "field": "data.total"}
  {"kind": "placeholder", "value": 128}

Usage:
  python3 scripts/mission_status.py [--print]
"""
from __future__ import annotations
import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "records" / "mission-control"
SOURCES = MC / "sources.json"
AGENTS = ROOT / "records" / "agents"
OPS_RUNS = ROOT / "records" / "ops" / "runs"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dig(data, dotted: str):
    for part in dotted.split("."):
        if isinstance(data, list):
            try:
                data = data[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(data, dict):
            data = data.get(part)
        else:
            return None
    return data


def resolve(src: dict) -> tuple[object, str, str]:
    """Return (value, state, note). State is live, placeholder or missing."""
    kind = src.get("kind")

    if kind == "placeholder":
        return src.get("value"), "placeholder", "no source wired yet"

    if kind == "count_files":
        d = ROOT / src["path"]
        if not d.exists():
            return None, "missing", f"{src['path']} does not exist"
        return len(list(d.glob(src.get("pattern", "*")))), "live", src["path"]

    if kind == "count_runs":
        if not (ROOT / "records" / "runs").exists():
            return None, "missing", "records/runs does not exist"
        want = src.get("decision")
        n = 0
        for p in (ROOT / "records" / "runs").glob("*.json"):
            try:
                if json.loads(p.read_text()).get("decision") == want:
                    n += 1
            except json.JSONDecodeError:
                continue
        return n, "live", f"records/runs decision={want}"

    if kind == "json_field":
        p = ROOT / src["path"]
        if not p.exists():
            return None, "missing", f"{src['path']} does not exist"
        try:
            return dig(json.loads(p.read_text()), src["field"]), "live", src["path"]
        except json.JSONDecodeError:
            return None, "missing", f"{src['path']} is not valid JSON"

    if kind == "agent_runs":
        d = AGENTS / src["agent_id"] / "runs"
        if not d.exists():
            return None, "missing", f"no runs for {src['agent_id']}"
        return len(list(d.glob("*.json"))), "live", f"records/agents/{src['agent_id']}/runs"

    if kind == "http":
        url = os.environ.get(src.get("url_env", ""), "")
        if not url:
            return None, "placeholder", f"{src.get('url_env')} not set, nothing fetched"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                payload = json.loads(r.read().decode())
            return dig(payload, src["field"]), "live", src.get("url_env")
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
            return None, "missing", f"{type(e).__name__}"

    return None, "missing", f"unknown source kind: {kind}"


def agent_feed(limit: int = 25) -> list[dict]:
    """Newest first, across every agent and the unattended runs."""
    events = []
    for p in AGENTS.glob("*/runs/*.json"):
        try:
            r = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        events.append({
            "agent_id": r.get("agent_id", p.parent.parent.name),
            "at": r.get("ran_at", ""),
            "what": r.get("task", ""),
            "outcome": "escalated" if r.get("escalated") else "handled",
            "source": "lesson run",
        })
    if OPS_RUNS.exists():
        for p in OPS_RUNS.glob("*.json"):
            try:
                r = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            events.append({
                "agent_id": r.get("agent_id", ""),
                "at": r.get("ran_at", ""),
                "what": r.get("task", ""),
                "outcome": r.get("decision", ""),
                "source": "unattended",
            })
    events.sort(key=lambda e: e["at"], reverse=True)
    return events[:limit]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", dest="show", action="store_true")
    args = ap.parse_args()

    if not SOURCES.exists():
        print(f"No tile map at {SOURCES.relative_to(ROOT)}. Lesson 10 STEP 1 writes it.")
        return 0

    spec = json.loads(SOURCES.read_text())
    pages = {}
    for page, tiles in spec.get("pages", {}).items():
        out = []
        for tile in tiles:
            value, state, note = resolve(tile.get("source", {}))
            out.append({
                "label": tile.get("label", "untitled"),
                "question": tile.get("question", ""),
                "value": value,
                "state": state,
                "note": note,
            })
        pages[page] = out

    status = {
        "generated_at": now(),
        "pages": pages,
        "agent_feed": agent_feed(),
        "counts": {
            "live": sum(1 for t in sum(pages.values(), []) if t["state"] == "live"),
            "placeholder": sum(1 for t in sum(pages.values(), []) if t["state"] == "placeholder"),
            "missing": sum(1 for t in sum(pages.values(), []) if t["state"] == "missing"),
        },
    }
    MC.mkdir(parents=True, exist_ok=True)
    (MC / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    c = status["counts"]
    print(f"status.json written · {c['live']} live · {c['placeholder']} placeholder · {c['missing']} missing")
    if c["missing"]:
        for page, tiles in pages.items():
            for t in tiles:
                if t["state"] == "missing":
                    print(f"  MISSING  {page}/{t['label']}: {t['note']}")
    if args.show:
        print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
