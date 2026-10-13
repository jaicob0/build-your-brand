#!/usr/bin/env python3
"""Event-driven work: a drop folder, and an optional local webhook.

Not every job is a timer. A new ticket, an order, a form submission:
something happens, and an agent should pick it up. The contract is one
JSON file in records/ops/events/inbox/.

Anything can write that file — a webhook, a Zapier step, a shortcut,
you with a text editor. The orchestrator drains the folder on its next
tick and runs the agent the event names, through the same allowlist,
gate and kill switch as everything else.

Usage:
  python3 scripts/hermes_events.py drop <agent_id> --task "..."
  python3 scripts/hermes_events.py listen [--port 8799]
  python3 scripts/hermes_events.py list

`listen` binds to 127.0.0.1 only. It is for a local tunnel or a service
on the same machine, never a port you open to the internet. It writes
events and runs nothing itself, so a flood of requests costs you disk
and not actions.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "records" / "ops" / "events"
INBOX = EVENTS / "inbox"
DONE = EVENTS / "done"
AUDIT = ROOT / "records" / "ops" / "audit.log"
MAX_BODY = 64 * 1024


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def audit(event: dict) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({"at": now(), **event}) + "\n")


def drop(agent_id: str, task: str, source: str = "hand") -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    stamp = now().replace(":", "").replace("-", "")
    path = INBOX / f"{stamp}-{agent_id}.json"
    n = 2
    while path.exists():
        path = INBOX / f"{stamp}-{agent_id}-{n}.json"
        n += 1
    path.write_text(json.dumps(
        {"agent_id": agent_id, "task": task, "source": source, "dropped_at": now()},
        indent=2))
    audit({"event": "event_dropped", "agent_id": agent_id, "source": source,
           "file": str(path.relative_to(ROOT))})
    return path


def pending() -> list[Path]:
    return sorted(INBOX.glob("*.json")) if INBOX.exists() else []


def archive(path: Path) -> None:
    DONE.mkdir(parents=True, exist_ok=True)
    path.rename(DONE / path.name)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 - http.server's naming
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            self.send_error(413, "body too large")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode())
            agent_id = payload["agent_id"]
            task = payload.get("task", "")
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
            self.send_error(400, 'expected {"agent_id": "...", "task": "..."}')
            return
        path = drop(agent_id, task, source="webhook")
        body = json.dumps({"queued": path.name}).encode()
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # keep the terminal readable
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("drop", help="queue one event by hand")
    d.add_argument("agent_id")
    d.add_argument("--task", required=True)

    li = sub.add_parser("listen", help="accept local webhooks and queue them")
    li.add_argument("--port", type=int, default=8799)

    sub.add_parser("list", help="what is waiting")

    args = ap.parse_args()

    if args.cmd == "drop":
        path = drop(args.agent_id, args.task)
        print(f"queued: {path.relative_to(ROOT)}")
        print("The next orchestrator tick picks it up.")
        return 0

    if args.cmd == "list":
        waiting = pending()
        if not waiting:
            print("nothing waiting")
        for p in waiting:
            e = json.loads(p.read_text())
            print(f"{e['agent_id']:<24} {e.get('source', ''):<8} {e['task'][:60]}")
        return 0

    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"listening on http://127.0.0.1:{args.port} · POST {{\"agent_id\": \"...\", \"task\": \"...\"}}")
    print("It queues events and runs nothing. Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
