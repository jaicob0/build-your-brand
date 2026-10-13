#!/usr/bin/env python3
"""Put an agent on the schedule, and stand the layer up on a host.

Adding an agent writes it to records/ops/schedule.json. The host runs
ONE job, the orchestrator, which runs whatever is due. Adding the
second agent never means installing a second timer.

Two hosts:
  launchd   your Mac. Free, nothing to install, stops when the Mac does.
  docker    an always-on container. Survives reboots and closed lids,
            and is the honest answer to "runs 24/7".

Nothing is installed unless you ask in the same command you read.

Usage:
  python3 scripts/hermes_schedule.py add <agent_id> --task "..." --every 60
  python3 scripts/hermes_schedule.py install [--host launchd|docker] [--every 5]
  python3 scripts/hermes_schedule.py status
  python3 scripts/hermes_schedule.py stop

`add` refuses gated and on-demand agents. `install` prints the job and
writes nothing until you pass --yes. `stop` unloads the timer or stops
the container; the records stay.
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
SCHEDULE = OPS / "schedule.json"
AUDIT = OPS / "audit.log"
LAUNCH_AGENTS = Path.home() / "Library" / "LaunchAgents"
LABEL = "uk.thecreativearchitect.byb.hermes"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def audit(event: dict) -> None:
    OPS.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({"at": now(), **event}) + "\n")


def schedule() -> dict:
    return json.loads(SCHEDULE.read_text()) if SCHEDULE.exists() else {}


def save(data: dict) -> None:
    OPS.mkdir(parents=True, exist_ok=True)
    SCHEDULE.write_text(json.dumps(data, indent=2) + "\n")


def plist(every: int) -> dict:
    return {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(ROOT / "scripts" / "hermes_orchestrator.py")],
        "WorkingDirectory": str(ROOT),
        "StartInterval": every * 60,
        "RunAtLoad": False,
        "StandardOutPath": str(OPS / "launchd.out.log"),
        "StandardErrorPath": str(OPS / "launchd.err.log"),
    }


DOCKERFILE = """# Hermes, the operations layer. Python and the Claude Code CLI, nothing else.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \\
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://claude.ai/install.sh | bash || \\
    echo "Install the Claude Code CLI into the image yourself if that script moves."
WORKDIR /layer
# The repo is mounted at run time, so the image never carries your records.
CMD ["python3", "scripts/hermes_loop.py"]
"""

COMPOSE = """services:
  hermes:
    build: .
    container_name: byb-hermes
    restart: unless-stopped
    working_dir: /layer
    volumes:
      # Your records stay on your disk. The container only borrows them.
      - ../../..:/layer
    environment:
      - HERMES_TICK_MINUTES=${HERMES_TICK_MINUTES:-5}
    # Credentials come from your own .env, which is gitignored and never
    # baked into the image.
    env_file:
      - ../../../.env
"""

LOOP = '''#!/usr/bin/env python3
"""Tick the orchestrator forever. The container's only job."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINUTES = float(os.environ.get("HERMES_TICK_MINUTES", "5"))

while True:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "hermes_orchestrator.py")], cwd=ROOT)
    time.sleep(MINUTES * 60)
'''


def cmd_add(args) -> int:
    spec_path = ROOT / "records" / "agents" / args.agent_id / "spec.json"
    if not spec_path.exists():
        print(f"ERROR: no spec at {spec_path.relative_to(ROOT)}. Build the agent first.", file=sys.stderr)
        return 2
    spec = json.loads(spec_path.read_text())
    if spec["gate"]["required"]:
        print(f"REFUSED: {args.agent_id} is gated on {spec['gate']['trigger']}.")
        print("A gated agent does not run unattended. Run it by hand through the gate.")
        audit({"event": "schedule_refused", "agent_id": args.agent_id, "reason": "gated"})
        return 0
    if spec["trigger"]["mode"] == "on-demand":
        print(f"REFUSED: {args.agent_id} is on-demand. It runs when a human asks, not on a timer.")
        audit({"event": "schedule_refused", "agent_id": args.agent_id, "reason": "on-demand"})
        return 0

    data = schedule()
    data[args.agent_id] = {
        "task": args.task, "every_minutes": args.every, "installed": True,
        "dry_run": bool(spec.get("dry_run", False)),
        "added_at": now(), "last_run": None,
    }
    save(data)
    audit({"event": "scheduled", "agent_id": args.agent_id, "every_minutes": args.every})
    print(f"{args.agent_id} added to {SCHEDULE.relative_to(ROOT)} · every {args.every} min")
    print(f"{len(data)} agent(s) on the schedule. The host runs one job for all of them.")
    print("Nothing runs until you install a host: hermes_schedule.py install")
    return 0


def cmd_install(args) -> int:
    if not schedule():
        print("Nothing on the schedule yet. Add an agent first.")
        return 0

    if args.host == "launchd":
        path = LAUNCH_AGENTS / f"{LABEL}.plist"
        job = plist(args.every)
        if not args.yes:
            print(plistlib.dumps(job).decode())
            print(f"Would install to: {path}")
            print(f"Then: launchctl load {path}")
            print("\nRead it, then run the same command with --yes.")
            return 0
        if not shutil.which("claude"):
            print("WARNING: claude is not on your PATH. Runs will fail until it is.")
        LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)
        path.write_bytes(plistlib.dumps(job))
        subprocess.run(["launchctl", "unload", str(path)], capture_output=True)
        proc = subprocess.run(["launchctl", "load", str(path)], capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"launchctl load failed: {proc.stderr.strip()}", file=sys.stderr)
            return 1
        audit({"event": "host_installed", "host": "launchd", "every_minutes": args.every})
        print(f"installed and loaded: {path}")
        print(f"ticks every {args.every} min · logs in {OPS.relative_to(ROOT)}/launchd.*.log")
        print("stop it with: python3 scripts/hermes_schedule.py stop")
        return 0

    # docker
    docker_dir = OPS / "docker"
    docker_dir.mkdir(parents=True, exist_ok=True)
    (docker_dir / "Dockerfile").write_text(DOCKERFILE)
    (docker_dir / "docker-compose.yml").write_text(COMPOSE)
    (ROOT / "scripts" / "hermes_loop.py").write_text(LOOP)
    print(f"written: {(docker_dir / 'Dockerfile').relative_to(ROOT)}")
    print(f"written: {(docker_dir / 'docker-compose.yml').relative_to(ROOT)}")
    print(f"written: scripts/hermes_loop.py")
    print("\nThe container mounts this repo, so your records never enter the image,")
    print("and credentials come from your own gitignored .env.")
    print(f"\n  cd {docker_dir.relative_to(ROOT)} && docker compose up -d --build")
    print(f"  docker logs -f byb-hermes")
    if not args.yes:
        print("\nRead the two files, then run that command yourself when you mean it.")
        return 0
    if not shutil.which("docker"):
        print("\nERROR: docker is not installed. The files are written; install Docker to use them.")
        return 1
    proc = subprocess.run(["docker", "compose", "up", "-d", "--build"],
                          cwd=docker_dir, capture_output=True, text=True)
    print(proc.stdout.strip() or proc.stderr.strip())
    if proc.returncode != 0:
        return 1
    audit({"event": "host_installed", "host": "docker"})
    print("byb-hermes is up. Stop it with: python3 scripts/hermes_schedule.py stop")
    return 0


def cmd_status(args) -> int:
    data = schedule()
    if not data:
        print("Nothing scheduled.")
    for agent_id, e in data.items():
        last = e.get("last_run") or "never"
        shape = "dry run" if e.get("dry_run") else "live"
        print(f"{agent_id:<24} every {e['every_minutes']:>4} min · {shape:<8} · last run {last}")
    path = LAUNCH_AGENTS / f"{LABEL}.plist"
    print(f"\nlaunchd job: {'installed' if path.exists() else 'not installed'}")
    if shutil.which("docker"):
        proc = subprocess.run(["docker", "ps", "--filter", "name=byb-hermes", "--format", "{{.Status}}"],
                              capture_output=True, text=True)
        print(f"container:   {proc.stdout.strip() or 'not running'}")
    return 0


def cmd_stop(args) -> int:
    path = LAUNCH_AGENTS / f"{LABEL}.plist"
    if path.exists():
        subprocess.run(["launchctl", "unload", str(path)], capture_output=True)
        path.unlink()
        print(f"unloaded and removed: {path}")
    if shutil.which("docker"):
        proc = subprocess.run(["docker", "rm", "-f", "byb-hermes"], capture_output=True, text=True)
        if proc.returncode == 0:
            print("container stopped and removed")
    audit({"event": "host_stopped"})
    print("Nothing is running now. records/ops/ is untouched.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="put an agent on the schedule")
    a.add_argument("agent_id")
    a.add_argument("--task", required=True)
    a.add_argument("--every", type=int, required=True, help="minutes between runs")
    a.set_defaults(func=cmd_add)

    i = sub.add_parser("install", help="stand the layer up on a host")
    i.add_argument("--host", choices=["launchd", "docker"], default="launchd")
    i.add_argument("--every", type=int, default=5, help="minutes between orchestrator ticks")
    i.add_argument("--yes", action="store_true", help="install, having read the printed job")
    i.set_defaults(func=cmd_install)

    s = sub.add_parser("status", help="what is scheduled and what is running")
    s.set_defaults(func=cmd_status)

    t = sub.add_parser("stop", help="stop everything, keep the records")
    t.set_defaults(func=cmd_stop)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
