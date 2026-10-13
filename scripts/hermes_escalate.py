#!/usr/bin/env python3
"""Put an escalation somewhere a human will actually see it.

An exception that lands only in a log file is an exception nobody
handles. Every escalation goes to the queue AND to the channel the
student chose in records/ops/channel.json.

Channels, free first:
  queue    a dated file in records/ops/escalations/ (always, the record)
  notify   a macOS notification (free, no account)
  webhook  POST to a URL in the env var named by the channel config
           (Slack incoming webhook, Discord, whatever takes JSON)
  email    SMTP from the env vars named in the channel config

Usage:
  python3 scripts/hermes_escalate.py <agent_id> --reason "..." [--task "..."]
  python3 scripts/hermes_escalate.py --configure            # write channel.json
  python3 scripts/hermes_escalate.py --test                 # prove the channel

Secrets are read from the environment by NAME. No credential is ever
written to a record, a log or this repo.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "records" / "ops"
QUEUE = OPS / "escalations"
CHANNEL = OPS / "channel.json"
AUDIT = OPS / "audit.log"

DEFAULT = {
    "channel": "queue",
    "webhook_env": "BYB_WEBHOOK_URL",
    "smtp": {"host_env": "BYB_SMTP_HOST", "user_env": "BYB_SMTP_USER",
             "pass_env": "BYB_SMTP_PASS", "to": ""},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def audit(event: dict) -> None:
    """Append-only. Never rewritten, never truncated by this repo."""
    OPS.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({"at": now(), **event}) + "\n")


def config() -> dict:
    if CHANNEL.exists():
        return {**DEFAULT, **json.loads(CHANNEL.read_text())}
    return dict(DEFAULT)


def to_queue(agent_id: str, reason: str, task: str) -> Path:
    QUEUE.mkdir(parents=True, exist_ok=True)
    stamp = now().replace(":", "").replace("-", "")
    path = QUEUE / f"{stamp}-{agent_id}.json"
    n = 2
    while path.exists():
        path = QUEUE / f"{stamp}-{agent_id}-{n}.json"
        n += 1
    path.write_text(json.dumps({
        "agent_id": agent_id, "raised_at": now(), "task": task,
        "reason": reason, "handled": False,
    }, indent=2))
    return path


def to_notify(agent_id: str, reason: str) -> tuple[bool, str]:
    if sys.platform != "darwin":
        return False, "notify is macOS only"
    script = (f'display notification {json.dumps(reason[:200])} '
              f'with title "Hermes" subtitle {json.dumps(agent_id)}')
    proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return proc.returncode == 0, proc.stderr.strip()


def to_webhook(cfg: dict, agent_id: str, reason: str, task: str) -> tuple[bool, str]:
    url = os.environ.get(cfg["webhook_env"], "")
    if not url:
        return False, f"{cfg['webhook_env']} is not set in this environment"
    body = json.dumps({"text": f"Hermes · {agent_id} escalated\n{reason}\nTask: {task}"}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return 200 <= r.status < 300, f"HTTP {r.status}"
    except urllib.error.URLError as e:
        return False, f"{type(e).__name__}: {e.reason}"


def to_email(cfg: dict, agent_id: str, reason: str, task: str) -> tuple[bool, str]:
    import smtplib
    from email.message import EmailMessage
    smtp = cfg["smtp"]
    host = os.environ.get(smtp["host_env"], "")
    user = os.environ.get(smtp["user_env"], "")
    pw = os.environ.get(smtp["pass_env"], "")
    if not (host and user and pw and smtp.get("to")):
        missing = [k for k, v in
                   ((smtp["host_env"], host), (smtp["user_env"], user), (smtp["pass_env"], pw))
                   if not v]
        if not smtp.get("to"):
            missing.append("smtp.to in channel.json")
        return False, "missing: " + ", ".join(missing)
    msg = EmailMessage()
    msg["Subject"] = f"Hermes · {agent_id} escalated"
    msg["From"], msg["To"] = user, smtp["to"]
    msg.set_content(f"{reason}\n\nTask: {task}\nRaised: {now()}")
    try:
        with smtplib.SMTP(host, 587, timeout=15) as s:
            s.starttls()
            s.login(user, pw)
            s.send_message(msg)
        return True, "sent"
    except Exception as e:  # noqa: BLE001 - the reason is what the student needs
        return False, f"{type(e).__name__}: {e}"


def configure() -> int:
    OPS.mkdir(parents=True, exist_ok=True)
    if not CHANNEL.exists():
        CHANNEL.write_text(json.dumps(DEFAULT, indent=2) + "\n")
        print(f"written: {CHANNEL.relative_to(ROOT)}")
    print(CHANNEL.read_text())
    print('Set "channel" to queue, notify, webhook or email, then put the')
    print("credentials in your environment under the names above. Never in this file.")
    return 0


def deliver(agent_id: str, reason: str, task: str) -> int:
    cfg = config()
    path = to_queue(agent_id, reason, task)
    name = cfg["channel"]
    if name == "queue":
        ok, detail = True, "queue only"
    elif name == "notify":
        ok, detail = to_notify(agent_id, reason)
    elif name == "webhook":
        ok, detail = to_webhook(cfg, agent_id, reason, task)
    elif name == "email":
        ok, detail = to_email(cfg, agent_id, reason, task)
    else:
        ok, detail = False, f"unknown channel '{name}'"

    audit({"event": "escalation", "agent_id": agent_id, "reason": reason,
           "channel": name, "delivered": ok, "detail": detail,
           "queue_file": str(path.relative_to(ROOT))})
    print(f"ESCALATED · {agent_id}")
    print(f"queued:  {path.relative_to(ROOT)}")
    print(f"channel: {name} · {'delivered' if ok else 'NOT DELIVERED'} · {detail}")
    if not ok:
        print("The queue file is still the record. Fix the channel before you walk away.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id", nargs="?")
    ap.add_argument("--reason", default=None)
    ap.add_argument("--task", default="")
    ap.add_argument("--configure", action="store_true")
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    if args.configure:
        return configure()
    if args.test:
        return deliver(args.agent_id or "channel-test",
                       args.reason or "Test escalation. If you can read this, the channel works.",
                       args.task or "a deliberate test")
    if not args.agent_id or not args.reason:
        print("ERROR: need <agent_id> and --reason (or --configure / --test)", file=sys.stderr)
        return 2
    return deliver(args.agent_id, args.reason, args.task)


if __name__ == "__main__":
    raise SystemExit(main())
