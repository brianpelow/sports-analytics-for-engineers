"""DORA metrics calculator for sports teams."""

from __future__ import annotations

from dataclasses import dataclass
from sportseng.collector import TeamStats


DORA_BANDS = ["LOW", "MEDIUM", "HIGH", "ELITE"]


@dataclass
class DORAReport:
    """DORA metrics report for a sports team."""
    team: str
    sport: str
    deployment_frequency: float
    deployment_frequency_band: str
    deployment_frequency_label: str
    lead_time: float
    lead_time_band: str
    lead_time_label: str
    change_failure_rate: float
    change_failure_rate_band: str
    change_failure_rate_label: str
    mttr: float
    mttr_band: str
    mttr_label: str
    overall_band: str
    engineering_verdict: str
    win_rate: float


def compute_dora(stats: TeamStats) -> DORAReport:
    """Map sports stats to DORA metrics."""
    win_rate = stats.wins / max(stats.total_games, 1) * 100

    # Deployment Frequency = scoring rate (points per game)
    df = stats.points_per_game
    if stats.sport == "nfl":
        df_band = "ELITE" if df >= 28 else "HIGH" if df >= 24 else "MEDIUM" if df >= 20 else "LOW"
    elif stats.sport in ("epl", "mlb"):
        df_band = "ELITE" if df >= 2.5 else "HIGH" if df >= 1.8 else "MEDIUM" if df >= 1.2 else "LOW"
    else:
        df_band = "ELITE" if df >= 120 else "HIGH" if df >= 112 else "MEDIUM" if df >= 105 else "LOW"

    # Lead Time = possession efficiency (lower = better, so invert)
    lt = stats.possession_seconds
    if lt == 0:
        lt_band = "HIGH"
    elif stats.sport == "nba":
        lt_band = "ELITE" if lt <= 13 else "HIGH" if lt <= 15 else "MEDIUM" if lt <= 17 else "LOW"
    else:
        lt_band = "HIGH"

    # Change Failure Rate = turnover rate (lower = better)
    cfr = stats.turnover_rate
    if stats.sport == "nba":
        cfr_band = "ELITE" if cfr <= 11 else "HIGH" if cfr <= 13 else "MEDIUM" if cfr <= 15 else "LOW"
    elif stats.sport == "nfl":
        cfr_band = "ELITE" if cfr <= 6 else "HIGH" if cfr <= 9 else "MEDIUM" if cfr <= 12 else "LOW"
    else:
        cfr_band = "ELITE" if cfr <= 8 else "HIGH" if cfr <= 11 else "MEDIUM" if cfr <= 14 else "LOW"

    # MTTR = comeback ability (more comeback wins = better recovery)
    comeback_rate = stats.comeback_wins / max(stats.total_games, 1) * 100
    mttr_band = "ELITE" if comeback_rate >= 15 else "HIGH" if comeback_rate >= 10 else "MEDIUM" if comeback_rate >= 5 else "LOW"
    mttr_val = round(comeback_rate, 1)

    bands = [df_band, lt_band, cfr_band, mttr_band]
    band_scores = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "ELITE": 3}
    avg = sum(band_scores[b] for b in bands) / 4
    overall = DORA_BANDS[round(avg)]

    verdict = _generate_verdict(stats, df_band, cfr_band, mttr_band, overall, win_rate)

    return DORAReport(
        team=stats.team, sport=stats.sport,
        deployment_frequency=df, deployment_frequency_band=df_band,
        deployment_frequency_label="Points/game (scoring rate)",
        lead_time=lt, lead_time_band=lt_band,
        lead_time_label="Avg possession length (seconds)",
        change_failure_rate=cfr, change_failure_rate_band=cfr_band,
        change_failure_rate_label="Turnover rate (%)",
        mttr=mttr_val, mttr_band=mttr_band,
        mttr_label="Comeback win rate (%)",
        overall_band=overall,
        engineering_verdict=verdict,
        win_rate=round(win_rate, 1),
    )


def _generate_verdict(
    stats: TeamStats, df_band: str, cfr_band: str,
    mttr_band: str, overall: str, win_rate: float,
) -> str:
    verdicts = []
    if overall == "ELITE":
        verdicts.append("Elite DORA performer. This team ships fast and recovers faster.")
    elif overall == "HIGH":
        verdicts.append("High performer. Strong fundamentals with room to optimize.")
    elif overall == "MEDIUM":
        verdicts.append("Medium performer. Inconsistent delivery, tech debt accumulating.")
    else:
        verdicts.append("Low performer. The pipeline is broken and the team knows it.")

    if cfr_band == "LOW":
        verdicts.append("Turnover rate is your change failure rate — this is where features go to die.")
    if df_band == "ELITE":
        verdicts.append("Deployment frequency is elite — shipping constantly.")
    if mttr_band == "ELITE":
        verdicts.append("Recovery time is exceptional — incident response is a strength.")
    if win_rate < 40:
        verdicts.append("Win rate suggests the on-call rotation is suffering.")

    return " ".join(verdicts)