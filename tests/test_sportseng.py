"""Tests for sports-analytics-for-engineers."""

from sportseng.collector import TeamStats, _mock_stats
from sportseng.dora import compute_dora, DORAReport, DORA_BANDS


def make_team(**kwargs) -> TeamStats:
    defaults = dict(
        team="Test Team", sport="nba", wins=40, losses=25,
        points_per_game=115.0, points_allowed_per_game=112.0,
        turnover_rate=13.0, possession_seconds=14.5,
        comeback_wins=6, total_games=65, avg_margin=3.0, streak="W2",
    )
    defaults.update(kwargs)
    return TeamStats(**defaults)


def test_compute_dora_returns_report() -> None:
    stats = make_team()
    report = compute_dora(stats)
    assert isinstance(report, DORAReport)
    assert report.team == "Test Team"
    assert report.overall_band in DORA_BANDS


def test_elite_scorer_gets_high_df_band() -> None:
    stats = make_team(points_per_game=125.0)
    report = compute_dora(stats)
    assert report.deployment_frequency_band == "ELITE"


def test_low_scorer_gets_low_df_band() -> None:
    stats = make_team(points_per_game=98.0)
    report = compute_dora(stats)
    assert report.deployment_frequency_band == "LOW"


def test_low_turnover_gets_elite_cfr_band() -> None:
    stats = make_team(turnover_rate=9.0)
    report = compute_dora(stats)
    assert report.change_failure_rate_band == "ELITE"


def test_high_turnover_gets_low_cfr_band() -> None:
    stats = make_team(turnover_rate=18.0)
    report = compute_dora(stats)
    assert report.change_failure_rate_band == "LOW"


def test_comeback_rate_affects_mttr() -> None:
    good = make_team(comeback_wins=15, total_games=65)
    bad = make_team(comeback_wins=1, total_games=65)
    report_good = compute_dora(good)
    report_bad = compute_dora(bad)
    band_score = {"ELITE": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    assert band_score[report_good.mttr_band] >= band_score[report_bad.mttr_band]


def test_win_rate_calculated() -> None:
    stats = make_team(wins=50, total_games=65)
    report = compute_dora(stats)
    assert abs(report.win_rate - 76.9) < 1.0


def test_mock_stats_fallback() -> None:
    stats = _mock_stats("unknown team", "nba")
    assert stats.team == "unknown team"
    assert stats.wins > 0


def test_mock_celtics() -> None:
    stats = _mock_stats("celtics", "nba")
    assert "Celtics" in stats.team
    assert stats.wins > 40


def test_verdict_not_empty() -> None:
    stats = make_team()
    report = compute_dora(stats)
    assert len(report.engineering_verdict) > 0