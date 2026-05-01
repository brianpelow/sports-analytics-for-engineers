# sports-analytics-for-engineers

> DORA metrics for sports teams — because your favorite team has a deployment problem.

![CI](https://github.com/brianpelow/sports-analytics-for-engineers/actions/workflows/ci.yml/badge.svg)

## The concept

DORA metrics measure software delivery performance. But what if we applied them to sports?

| DORA Metric | Software meaning | Sports meaning |
|-------------|-----------------|----------------|
| Deployment Frequency | How often you ship | How often you score |
| Lead Time for Changes | PR to production | Play call to execution |
| Change Failure Rate | Bad deploys / total deploys | Turnovers / total possessions |
| MTTR | Time to restore after incident | Time to recover from a deficit |

## Usage

```bash
pip install sports-analytics-for-engineers

sports-eng report --team "Golden State Warriors" --sport nba
sports-eng report --team "Manchester City" --sport epl
sports-eng compare --team1 "Lakers" --team2 "Celtics" --sport nba
sports-eng elite-check --team "Chiefs" --sport nfl
```

## Example output

```
DORA Report: Golden State Warriors

Deployment Frequency:  HIGH    112.4 points/game
Lead Time:             ELITE   8.2 seconds avg possession
Change Failure Rate:   MEDIUM  14.2% turnover rate
MTTR:                  HIGH    Recovers from deficits in 4.2 minutes avg

Overall DORA Band: HIGH performer
Engineering verdict: Strong CI/CD pipeline, turnover rate is your tech debt.
```

## Supported sports

NBA, NFL, EPL, MLB — uses ESPN public API for live data.
Falls back to mock data for offline use.

## License

Apache 2.0
