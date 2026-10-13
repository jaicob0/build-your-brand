#!/usr/bin/env python3
"""Write dashboard status.json by checking what's actually in records/.

Real-file-based, not self-reported: a stage counts as done only if its
output files genuinely exist on disk. Thirteen stages, matching
.claude/commands/build/01-setup.md through 13-grow.md.

Usage:
  python3 scripts/dashboard_status.py
Writes status.json at the repo root (same dir dashboard.html serves from).
Run this after each stage, or leave scripts/serve_dashboard.py running and
it refreshes on every dashboard page load.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def has_files(dir_path: Path, pattern: str) -> bool:
    return dir_path.exists() and any(dir_path.glob(pattern))


def main() -> int:
    brands_dir = ROOT / "records" / "brands"
    briefs_dir = ROOT / "records" / "briefs"
    runs_dir = ROOT / "records" / "runs"
    website_dir = ROOT / "records" / "website"
    assets_dir = ROOT / "records" / "assets"
    agents_dir = ROOT / "records" / "agents"
    mc_dir = ROOT / "records" / "mission-control"
    ops_dir = ROOT / "records" / "ops"
    ops_runs_dir = ops_dir / "runs"
    design_md = ROOT / "design.md"
    guide_html = ROOT / "brand-guide.html"
    guide_pdf = ROOT / "brand-guide.pdf"

    def any_asset_built() -> bool:
        if not runs_dir.exists():
            return False
        return any(
            json.loads(p.read_text()).get("decision") == "built"
            for p in runs_dir.glob("*.json")
        )

    status = {
        # Lesson 1: setup has no on-disk artifact — always considered
        # "done" once the dashboard itself is running; left true so the
        # bar reflects real build progress, not tooling checks.
        "setup": True,
        # Lesson 2/3: brand-foundation's seven-file output, per brand.
        "research": has_files(brands_dir, "*/deepresearch.md"),
        "foundation": has_files(brands_dir, "*/brand_foundation.json"),
        # Lesson 4: design.md at the repo root.
        "design": design_md.exists(),
        # Lesson 5: brand-guide HTML + PDF.
        "guide": guide_html.exists() and guide_pdf.exists(),
        # Lesson 6: hero-still is the bar for "done" here — hero-video is
        # optional/unapproved-spend in this repo, so it's not required.
        "hero": has_files(assets_dir, "hero-still.png"),
        # Lesson 7: the site.
        "website": has_files(website_dir, "*/index.html"),
        # Lesson 8: at least one real built asset AND at least one
        # rejection on record — the lesson explicitly asks for both.
        "assets": (
            any_asset_built()
            and any(
                json.loads(p.read_text()).get("decision") == "rejected"
                for p in runs_dir.glob("*.json")
            ) if runs_dir.exists() else False
        ),
        # Lesson 9: an agent counts as built with the shared voice file, a
        # spec, a run on record AND the honest test log — a spec on its
        # own is a document.
        "agents": (
            (agents_dir / "_voice.md").exists()
            and has_files(agents_dir, "*/spec.json")
            and has_files(agents_dir, "*/runs/*.json")
            and has_files(agents_dir, "*/test-log.md")
        ),
        # Lesson 10: the tile map, the student's own dashboard and the
        # render they were asked to look at.
        "dashboard": (
            (mc_dir / "sources.json").exists()
            and (mc_dir / "index.html").exists()
            and (mc_dir / "preview.png").exists()
        ),
        # Lesson 11: the layer counts as live with the central allowlist,
        # at least two kinds of refusal on record, the audit log, and a
        # runbook holding the stop command.
        "hermes": (
            (ops_dir / "allowlist.json").exists()
            and (ops_dir / "audit.log").exists()
            and (ops_dir / "RUNBOOK.md").exists()
            and len({
                json.loads(p.read_text()).get("decision", "")
                for p in ops_runs_dir.glob("*.json")
                if json.loads(p.read_text()).get("decision", "").startswith("refused")
            }) >= 2 if ops_runs_dir.exists() else False
        ),
        # Lesson 13: any of the three engine outputs on disk.
        "grow": (
            ROOT.joinpath("records/ads").exists()
            and any(ROOT.joinpath("records/ads").glob("*/ad-concepts.md"))
        ) or (
            ROOT.joinpath("records/email").exists()
            and any(ROOT.joinpath("records/email").glob("*/emails.md"))
        ) or (
            ROOT.joinpath("records/content").exists()
            and any(ROOT.joinpath("records/content").glob("*/calendar.md"))
        ),
        # Lesson 12: no new artifact of its own — done once everything
        # upstream is done.
        "done": False,  # computed below
    }
    status["done"] = all(
        status[k] for k in (
            "research", "foundation", "guide", "design", "hero", "website",
            "assets", "agents", "dashboard", "hermes",
        )
    )

    out_path = ROOT / "status.json"
    out_path.write_text(json.dumps(status, indent=2))
    print(f"status.json written: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
