"""CLI interface for legal-tax-ops."""
from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .analyzer import analyze, load_profile
from .models import Severity
from .report import generate_html_report
from .roadmap import generate_public_roadmap, generate_personal_roadmap
from .dashboard import generate_dashboard


console = Console()

SEVERITY_COLORS = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "blue",
    Severity.OK: "green",
}

SEVERITY_ICONS = {
    Severity.CRITICAL: "[!!!]",
    Severity.HIGH: "[!!]",
    Severity.MEDIUM: "[!]",
    Severity.LOW: "[i]",
    Severity.OK: "[ok]",
}


@click.group()
def cli():
    """Legal & Tax Operations Toolkit."""
    pass


@cli.command()
@click.argument("profile_path", type=click.Path(exists=True))
@click.option("--html", type=click.Path(), help="Generate HTML report to this path")
def scan(profile_path: str, html: str | None):
    """Scan a profile and show all obligations."""
    profile = load_profile(profile_path)
    result = analyze(profile)

    # Header
    console.print()
    console.print(Panel(
        f"[bold]{result.name}[/bold]\n"
        f"Analysis date: {result.analysis_date}\n"
        f"{result.summary}",
        title="Tax Profile Scan",
        border_style="blue",
    ))

    # Government views
    console.print("\n[bold cyan]How Governments See You[/bold cyan]")
    for gv in result.government_views:
        color = SEVERITY_COLORS[gv.risk_level]
        console.print(f"\n  [{color}]{gv.country}[/{color}] — {gv.why}")
        for src in gv.information_sources:
            console.print(f"    [dim]Source:[/dim] {src}")
        if gv.gaps:
            for gap in gv.gaps:
                console.print(f"    [red]Missing:[/red] {gap}")
        if gv.notes:
            console.print(f"    [dim]{gv.notes}[/dim]")

    # Obligations table
    console.print()
    table = Table(title="Filing Obligations", show_lines=True)
    table.add_column("Sev", width=5)
    table.add_column("Jurisdiction", width=8)
    table.add_column("Obligation", width=30)
    table.add_column("Year", width=8)
    table.add_column("Status", width=12)
    table.add_column("Action", width=40)
    table.add_column("Risk", width=12, justify="right")

    # Sort by severity
    severity_order = {
        Severity.CRITICAL: 0, Severity.HIGH: 1,
        Severity.MEDIUM: 2, Severity.LOW: 3, Severity.OK: 4,
    }
    sorted_obligations = sorted(
        result.obligations,
        key=lambda o: severity_order.get(o.severity, 5),
    )

    for ob in sorted_obligations:
        color = SEVERITY_COLORS[ob.severity]
        icon = SEVERITY_ICONS[ob.severity]
        risk_str = f"${ob.amount_at_risk:,.0f}" if ob.amount_at_risk > 0 else ""
        table.add_row(
            Text(icon, style=color),
            ob.jurisdiction,
            ob.name,
            ob.tax_year,
            Text(ob.status, style=color),
            ob.action,
            Text(risk_str, style="red" if ob.amount_at_risk > 0 else ""),
        )

    console.print(table)

    # Entity issues
    if result.entity_issues:
        console.print("\n[bold yellow]Entity Issues[/bold yellow]")
        for issue in result.entity_issues:
            console.print(f"  [yellow]![/yellow] {issue}")

    # FBAR/FATCA flags
    if result.fbar_required:
        console.print("\n[bold red]FBAR REQUIRED[/bold red] — foreign accounts exceed $10,000 aggregate")
    if result.fatca_required:
        console.print("[bold red]FATCA (8938) REQUIRED[/bold red] — foreign assets exceed threshold")

    # Total exposure
    if result.total_penalty_exposure > 0:
        console.print(f"\n[bold red]Total estimated penalty exposure: ${result.total_penalty_exposure:,.0f}[/bold red]")

    console.print()

    # Generate HTML if requested
    if html:
        html_path = Path(html)
        generate_html_report(result, html_path)
        console.print(f"[green]HTML report saved to {html_path}[/green]")


@cli.command()
def init():
    """Initialize a new profile from the template."""
    profiles_dir = Path("profiles")
    profiles_dir.mkdir(exist_ok=True)

    template = Path("profile.example.yaml")
    if not template.exists():
        console.print("[red]profile.example.yaml not found in current directory[/red]")
        return

    name = click.prompt("Your name (for filename)")  # type: ignore[arg-type]
    slug = name.lower().replace(" ", "_")
    target = profiles_dir / f"{slug}.yaml"

    if target.exists():
        if not click.confirm(f"{target} already exists. Overwrite?"):
            return

    target.write_text(template.read_text())
    console.print(f"[green]Created {target}[/green]")
    console.print(f"Edit this file with your information, then run:")
    console.print(f"  [bold]uv run taxops scan {target}[/bold]")


@cli.command()
@click.argument("profile_path", type=click.Path(exists=True))
def governments(profile_path: str):
    """Show what each government knows about you."""
    profile = load_profile(profile_path)
    result = analyze(profile)

    for gv in result.government_views:
        color = SEVERITY_COLORS[gv.risk_level]
        console.print(Panel(
            f"[bold]Knows about you:[/bold] {'Yes' if gv.knows_about_you else 'No'}\n"
            f"[bold]Why:[/bold] {gv.why}\n\n"
            f"[bold]Information sources:[/bold]\n"
            + "\n".join(f"  - {s}" for s in gv.information_sources) + "\n\n"
            f"[bold]What they expect:[/bold]\n"
            + "\n".join(f"  - {e}" for e in gv.what_they_expect) + "\n\n"
            + ("[bold red]Gaps:[/bold red]\n"
               + "\n".join(f"  - {g}" for g in gv.gaps)
               if gv.gaps else "[green]No gaps identified[/green]")
            + (f"\n\n[dim]{gv.notes}[/dim]" if gv.notes else ""),
            title=f"[{color}]{gv.country}[/{color}]",
            border_style=color,
        ))


@cli.command()
@click.option("--output", "-o", type=click.Path(), default="docs/roadmap.html",
              help="Output path for public roadmap")
def roadmap(output: str):
    """Generate the public project roadmap (no personal data)."""
    out = Path(output)
    generate_public_roadmap(out)
    console.print(f"[green]Public roadmap saved to {out}[/green]")


@cli.command()
@click.argument("profile_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output path (default: reports/<name>_roadmap.html)")
def my_roadmap(profile_path: str, output: str | None):
    """Generate a personalized roadmap with your status overlay."""
    profile = load_profile(profile_path)
    result = analyze(profile)

    if output is None:
        slug = result.name.lower().replace(" ", "_")
        out = Path(f"reports/{slug}_roadmap.html")
    else:
        out = Path(output)

    generate_personal_roadmap(result, out)
    console.print(f"[green]Personal roadmap saved to {out}[/green]")


@cli.command()
@click.argument("profile_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output path (default: reports/<name>_dashboard.html)")
@click.option("--open", "open_browser", is_flag=True, help="Open in browser after generating")
def dashboard(profile_path: str, output: str | None, open_browser: bool):
    """Generate a comprehensive Palantir-style dashboard."""
    profile = load_profile(profile_path)

    if output is None:
        name = profile.get("identity", {}).get("name", "unknown")
        slug = name.lower().replace(" ", "_")
        out = Path(f"reports/{slug}_dashboard.html")
    else:
        out = Path(output)

    generate_dashboard(profile_path, out)
    console.print(f"[green]Dashboard saved to {out}[/green]")

    if open_browser:
        import subprocess
        subprocess.run(["open", "-a", "Google Chrome", str(out.resolve())])
