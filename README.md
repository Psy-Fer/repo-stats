# repo-stats

Self-hosted GitHub stats tracker for [Psy-Fer](https://github.com/Psy-Fer).

Runs a scheduled Action every 5 days. Fetches stars, forks, issues, PRs, languages, and clone traffic across tracked repos, accumulates clone history (GitHub only retains 14 days), writes shields.io badge endpoints and SVG stat cards, and commits everything back. No external services — badges point at `raw.githubusercontent.com` directly.

## Output layout

After the first run:

```
badges/
  stars/{repo}.json       shields.io endpoint — star count
  forks/{repo}.json       shields.io endpoint — fork count
  issues/{repo}.json      shields.io endpoint — open issues (PRs excluded)
  prs/{repo}.json         shields.io endpoint — open PRs
  clones/{repo}.json      shields.io endpoint — accumulated clones (total | unique)
  languages.json          shields.io endpoint — top 3 languages across all repos
  total_stars.json        shields.io endpoint — aggregate totals
  total_forks.json
  total_clones.json
data/
  clones/{repo}.json      accumulated daily clone history keyed by YYYY-MM-DD
  languages.json          language bytes breakdown
  stats.json              master summary: all repos, all metrics, updated date
cards/
  stats-plain.svg         clean dark stats card
  stats-weird.svg         same data, different energy
```

## Badge URL pattern

```
https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Psy-Fer/repo-stats/main/badges/stars/{repo}.json&style=flat-square
```

## Setup

1. Add `TRAFFIC_PSYFER` secret: repo Settings → Secrets and variables → Actions → New repository secret.
   The PAT needs fine-grained permissions: Administration → Read-only (required for the traffic API).
2. Trigger a bootstrap run: Actions tab → "Update repo stats" → Run workflow.

## Adding a repo

Append the name to `REPOS` in `collect_stats.py` and push. It'll be picked up on the next run.
