"""sports-analytics-for-engineers CLI."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sportseng.collector import get_team_stats
from sportseng.dora import compute_dora, DORAReport

app = typer.Typer(name="sports-eng", help="DORA metrics for sports teams.")
console = Console()

BAND_COLORS = {"ELITE": "green", "HIGH": "cyan", "MEDIUM": "yellow", "LOW": "red"}
BAND_EMOJI = {"ELITE": "🚀", "HIGH": "✅", "MEDIUM": "⚠️", "LOW": "🔴"}


def _render_report(report: DORAReport) -> None:
    color = BAND_COLORS.get(report.overall_band, "white")
    emoji = BAND_EMOJI.get(report.overall_band, "")

    console.print(Panel.fit(
        f"Overall DORA band: [{color}]{report.overall_band}[/{color}] {emoji}\n"
        f"Win rate: [bold]{report.win_rate}%[/bold]\n\n"
        f"[dim italic]{report.engineering_verdict}[/dim italic]",
        title=f"DORA Report — {report.team}",
        border_style=color,
        padding=(1, 2),
    ))

    table = Table(border_style="dim", show_header=True)
    table.add_column("DORA Metric", style="bold")
    table.add_column("Sports equivalent", style="dim")
    table.add_column("Value", justify="right")
    table.add_column("Band", justify="center")

    metrics = [
        ("Deployment Frequency", report.deployment_frequency_label,
         f"{report.deployment_frequency:.1f}", report.deployment_frequency_band),
        ("Lead Time", report.lead_time_label,
         f"{report.lead_time:.1f}s" if report.lead_time > 0 else "N/A", report.lead_time_band),
        ("Change Failure Rate", report.change_failure_rate_label,
         f"{report.change_failure_rate:.1f}%", report.change_failure_rate_band),
        ("MTTR", report.mttr_label,
         f"{report.mttr:.1f}%", report.mttr_band),
    ]

    for metric, label, value, band in metrics:
        bc = BAND_COLORS.get(band, "white")
        table.add_row(metric, label, value, f"[{bc}]{band}[/{bc}]")

    console.print(table)


@app.command("report")
def report(
    team: str = typer.Option(..., "--team", "-t", help="Team name"),
    sport: str = typer.Option("nba", "--sport", "-s", help="Sport: nba/nfl/epl/mlb"),
) -> None:
    """Generate a DORA metrics report for a sports team."""
    console.print(f"\n[dim]Fetching stats for [cyan]{team}[/cyan]...[/dim]\n")
    stats = get_team_stats(team, sport)
    dora = compute_dora(stats)
    _render_report(dora)


@app.command("compare")
def compare(
    team1: str = typer.Option(..., "--team1"),
    team2: str = typer.Option(..., "--team2"),
    sport: str = typer.Option("nba", "--sport", "-s"),
) -> None:
    """Compare DORA metrics between two teams."""
    console.print(f"\n[dim]Comparing [cyan]{team1}[/cyan] vs [cyan]{team2}[/cyan]...[/dim]\n")

    stats1 = get_team_stats(team1, sport)
    stats2 = get_team_stats(team2, sport)
    dora1 = compute_dora(stats1)
    dora2 = compute_dora(stats2)

    table = Table(title=f"{team1} vs {team2} — DORA Comparison", border_style="dim")
    table.add_column("Metric")
    table.add_column(dora1.team, justify="center")
    table.add_column(dora2.team, justify="center")

    band_score = {"ELITE": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

    pairs = [
        ("Deployment Frequency", dora1.deployment_frequency_band, dora2.deployment_frequency_band),
        ("Lead Time", dora1.lead_time_band, dora2.lead_time_band),
        ("Change Failure Rate", dora1.change_failure_rate_band, dora2.change_failure_rate_band),
        ("MTTR", dora1.mttr_band, dora2.mttr_band),
        ("Overall", dora1.overall_band, dora2.overall_band),
    ]

    for metric, b1, b2 in pairs:
        c1 = BAND_COLORS.get(b1, "white")
        c2 = BAND_COLORS.get(b2, "white")
        winner1 = " ←" if band_score.get(b1, 0) > band_score.get(b2, 0) else ""
        winner2 = " ←" if band_score.get(b2, 0) > band_score.get(b1, 0) else ""
        table.add_row(metric, f"[{c1}]{b1}{winner1}[/{c1}]", f"[{c2}]{b2}{winner2}[/{c2}]")

    console.print(table)


@app.command("elite-check")
def elite_check(
    team: str = typer.Option(..., "--team", "-t"),
    sport: str = typer.Option("nba", "--sport", "-s"),
) -> None:
    """Check if a team meets elite DORA band criteria."""
    stats = get_team_stats(team, sport)
    dora = compute_dora(stats)
    is_elite = dora.overall_band == "ELITE"
    color = "green" if is_elite else "red"
    console.print(f"\n[{color}]{'✓ ELITE DORA performer' if is_elite else '✗ Not yet elite'}[/{color}] — {dora.team}\n")
    console.print(f"  [dim]{dora.engineering_verdict}[/dim]\n")


if __name__ == "__main__":
    app()