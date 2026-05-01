"""Sports data collector — ESPN public API with mock fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
import httpx


@dataclass
class TeamStats:
    """Raw stats for a sports team."""
    team: str
    sport: str
    wins: int = 0
    losses: int = 0
    points_per_game: float = 0.0
    points_allowed_per_game: float = 0.0
    turnover_rate: float = 0.0
    possession_seconds: float = 0.0
    comeback_wins: int = 0
    total_games: int = 0
    avg_margin: float = 0.0
    streak: str = ""


ESPN_SPORT_MAP = {
    "nba": "basketball/nba",
    "nfl": "football/nfl",
    "epl": "soccer/eng.1",
    "mlb": "baseball/mlb",
}

MOCK_TEAMS: dict[str, dict] = {
    "warriors": dict(team="Golden State Warriors", sport="nba", wins=45, losses=20,
        points_per_game=118.4, points_allowed_per_game=112.1, turnover_rate=13.2,
        possession_seconds=14.2, comeback_wins=8, total_games=65, avg_margin=6.3, streak="W3"),
    "lakers": dict(team="Los Angeles Lakers", sport="nba", wins=38, losses=27,
        points_per_game=114.2, points_allowed_per_game=115.8, turnover_rate=14.8,
        possession_seconds=15.1, comeback_wins=5, total_games=65, avg_margin=-1.6, streak="L1"),
    "celtics": dict(team="Boston Celtics", sport="nba", wins=52, losses=13,
        points_per_game=120.6, points_allowed_per_game=108.3, turnover_rate=11.4,
        possession_seconds=13.8, comeback_wins=12, total_games=65, avg_margin=12.3, streak="W7"),
    "chiefs": dict(team="Kansas City Chiefs", sport="nfl", wins=14, losses=3,
        points_per_game=27.4, points_allowed_per_game=17.2, turnover_rate=8.2,
        possession_seconds=31.0, comeback_wins=4, total_games=17, avg_margin=10.2, streak="W2"),
    "manchester city": dict(team="Manchester City", sport="epl", wins=22, losses=4,
        points_per_game=2.8, points_allowed_per_game=0.9, turnover_rate=9.1,
        possession_seconds=0.0, comeback_wins=3, total_games=30, avg_margin=1.9, streak="W5"),
    "yankees": dict(team="New York Yankees", sport="mlb", wins=88, losses=54,
        points_per_game=4.8, points_allowed_per_game=3.9, turnover_rate=6.2,
        possession_seconds=0.0, comeback_wins=18, total_games=142, avg_margin=0.9, streak="W2"),
}


def get_team_stats(team: str, sport: str) -> TeamStats:
    """Fetch team stats — tries ESPN API, falls back to mock data."""
    stats = _try_espn(team, sport)
    if stats:
        return stats
    return _mock_stats(team, sport)


def _try_espn(team: str, sport: str) -> TeamStats | None:
    sport_path = ESPN_SPORT_MAP.get(sport.lower())
    if not sport_path:
        return None
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/teams",
                           params={"limit": 100})
            if r.status_code != 200:
                return None
            teams = r.json().get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
            for t in teams:
                name = t.get("team", {}).get("displayName", "").lower()
                if team.lower() in name or name in team.lower():
                    return _parse_espn_team(t.get("team", {}), sport)
    except Exception:
        pass
    return None


def _parse_espn_team(data: dict, sport: str) -> TeamStats:
    record = data.get("record", {}).get("items", [{}])[0].get("stats", [])
    stat_map = {s.get("name"): s.get("value", 0) for s in record}
    return TeamStats(
        team=data.get("displayName", "Unknown"),
        sport=sport,
        wins=int(stat_map.get("wins", 0)),
        losses=int(stat_map.get("losses", 0)),
        points_per_game=float(stat_map.get("pointsPerGame", 100.0)),
        points_allowed_per_game=float(stat_map.get("oppPointsPerGame", 100.0)),
        total_games=int(stat_map.get("gamesPlayed", 0)),
    )


def _mock_stats(team: str, sport: str) -> TeamStats:
    key = team.lower()
    for k, v in MOCK_TEAMS.items():
        if k in key or key in k:
            return TeamStats(**v)
    return TeamStats(
        team=team, sport=sport, wins=40, losses=25,
        points_per_game=108.0, points_allowed_per_game=107.0,
        turnover_rate=14.0, possession_seconds=15.0,
        comeback_wins=6, total_games=65, avg_margin=1.0, streak="W1",
    )