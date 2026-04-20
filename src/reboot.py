"""Reboot script — generates a session summary for continuity.

Run after any work session to capture:
- Current state of all source files (with sizes and last modified)
- Git log of recent changes
- Profile status (if profiles exist)
- Generated reports inventory
- Open issues / next steps from roadmap
- Changelog of what was modified this session

Output: reports/SESSION.md (local, gitignored) + terminal summary.

This allows any future Claude session (or human) to pick up exactly
where the last session left off without re-reading every file.
"""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def generate_reboot_summary(repo_root: Path | None = None):
    """Generate a comprehensive session summary."""
    if repo_root is None:
        repo_root = Path.cwd()

    lines = []
    lines.append(f"# Session Summary — legal-tax-ops")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Repo: {repo_root}")
    lines.append("")

    # ── Git state ────────────────────────────────────────────
    lines.append("## Git State")
    lines.append("")

    branch = _run("git branch --show-current", repo_root)
    lines.append(f"Branch: `{branch}`")

    status = _run("git status --short", repo_root)
    if status:
        lines.append(f"\nUncommitted changes:")
        lines.append(f"```")
        lines.append(status)
        lines.append(f"```")
    else:
        lines.append("Working tree clean.")

    lines.append("")

    # ── Recent commits ───────────────────────────────────────
    lines.append("## Recent Commits (last 10)")
    lines.append("")
    log = _run("git log --oneline -10", repo_root)
    lines.append(f"```")
    lines.append(log)
    lines.append(f"```")
    lines.append("")

    # ── Source file inventory ────────────────────────────────
    lines.append("## Source Files")
    lines.append("")
    lines.append("| File | Lines | Last Modified |")
    lines.append("|------|-------|---------------|")

    for py_file in sorted(repo_root.glob("src/**/*.py")):
        if py_file.name == "__pycache__":
            continue
        try:
            line_count = len(py_file.read_text().splitlines())
            mtime = datetime.fromtimestamp(py_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            rel = py_file.relative_to(repo_root)
            lines.append(f"| `{rel}` | {line_count} | {mtime} |")
        except Exception:
            pass

    lines.append("")

    # ── Reference docs ───────────────────────────────────────
    lines.append("## Reference Documents")
    lines.append("")
    for md_dir in ["legal", "tax", "guides", "templates"]:
        d = repo_root / md_dir
        if d.exists():
            for f in sorted(d.glob("*.md")):
                rel = f.relative_to(repo_root)
                size = f.stat().st_size
                lines.append(f"- `{rel}` ({size:,} bytes)")
    lines.append("")

    # ── Profiles ─────────────────────────────────────────────
    profiles_dir = repo_root / "profiles"
    if profiles_dir.exists():
        profiles = list(profiles_dir.glob("*.yaml"))
        lines.append(f"## Profiles ({len(profiles)} found)")
        lines.append("")
        for p in profiles:
            size = p.stat().st_size
            lines.append(f"- `{p.name}` ({size:,} bytes)")
        lines.append("")

    # ── Generated reports ────────────────────────────────────
    reports_dir = repo_root / "reports"
    if reports_dir.exists():
        reports = list(reports_dir.glob("*.html"))
        lines.append(f"## Generated Reports ({len(reports)} found)")
        lines.append("")
        for r in sorted(reports):
            mtime = datetime.fromtimestamp(r.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            size = r.stat().st_size
            lines.append(f"- `{r.name}` ({size:,} bytes, {mtime})")
        lines.append("")

    # ── Docs (public HTML) ───────────────────────────────────
    docs_dir = repo_root / "docs"
    if docs_dir.exists():
        docs = list(docs_dir.glob("*.html"))
        if docs:
            lines.append(f"## Public Docs ({len(docs)} found)")
            lines.append("")
            for d in sorted(docs):
                lines.append(f"- `{d.name}` ({d.stat().st_size:,} bytes)")
            lines.append("")

    # ── Roadmap status ───────────────────────────────────────
    lines.append("## Roadmap Status")
    lines.append("")
    try:
        from .roadmap import PHASES
        for phase in PHASES:
            done = sum(1 for t in phase["tasks"] if t["status"] == "done")
            total = len(phase["tasks"])
            status = phase["status"].upper()
            lines.append(f"- **Phase {phase['id']}: {phase['title']}** [{status}] — {done}/{total} complete")
    except Exception:
        lines.append("- (Could not load roadmap phases)")
    lines.append("")

    # ── Changed files this session ───────────────────────────
    lines.append("## Files Changed Today")
    lines.append("")
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_log = _run(f'git log --oneline --since="{today_str} 00:00:00" --name-only', repo_root)
    if today_log:
        # Extract unique filenames
        changed = set()
        for line in today_log.splitlines():
            if "/" in line or "." in line:
                if not line.startswith(" ") and not line[0].isdigit():
                    changed.add(line.strip())
        if changed:
            for f in sorted(changed):
                lines.append(f"- `{f}`")
        else:
            lines.append("(No file changes logged today)")
    else:
        lines.append("(No commits today)")
    lines.append("")

    # ── Next steps ───────────────────────────────────────────
    lines.append("## Next Steps (from roadmap Phase 2)")
    lines.append("")
    try:
        from .roadmap import PHASES
        phase2 = next(p for p in PHASES if p["id"] == 2)
        for t in phase2["tasks"]:
            if t["status"] != "done":
                lines.append(f"- [ ] **{t['name']}**: {t['detail'][:100]}...")
    except Exception:
        lines.append("- (Could not load next steps)")
    lines.append("")

    # ── Write output ─────────────────────────────────────────
    content = "\n".join(lines)
    output_path = repo_root / "reports" / "SESSION.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)

    return content, output_path


def _run(cmd: str, cwd: Path) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=str(cwd), timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def print_reboot_summary(repo_root: Path | None = None):
    """Generate and print the reboot summary."""
    content, path = generate_reboot_summary(repo_root)

    # Print key stats to terminal
    console.print(Panel(
        f"[bold]Session summary saved to {path}[/bold]\n\n"
        "Key sections: Git State, Source Files, Profiles, Reports,\n"
        "Roadmap Status, Files Changed Today, Next Steps",
        title="Reboot Summary",
        border_style="green",
    ))

    # Print a compact version
    for line in content.splitlines():
        if line.startswith("## "):
            console.print(f"\n[bold cyan]{line[3:]}[/bold cyan]")
        elif line.startswith("- **Phase"):
            console.print(f"  {line}")
        elif line.startswith("- [ ]"):
            console.print(f"  [yellow]{line}[/yellow]")
        elif line.startswith("Branch:"):
            console.print(f"  {line}")
        elif "Uncommitted" in line:
            console.print(f"  [red]{line}[/red]")
