import json
import os
import time
import urllib.request
import urllib.error
from datetime import date

OWNER = "Psy-Fer"
REPOS = [
    "kuva",
    "buttery-eel",
    "blue-crab",
    "bedpull",
    "SquiggleKit",
    "deeplexicon",
    "interARTIC",
    "poa-consensus",
    "svb",
    "pod5lib-rs",
    "slow5lib-rs",
]

TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def gh(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} for {path}")
        return None


# Search API is capped at 30 req/min; enforce 2.1s between calls.
_search_ts = 0.0

def search_gh(path):
    global _search_ts
    gap = time.monotonic() - _search_ts
    if gap < 2.1:
        time.sleep(2.1 - gap)
    result = gh(path)
    _search_ts = time.monotonic()
    return result


def badge(path, label, message, color="blue"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"schemaVersion": 1, "label": label, "message": str(message), "color": color}, f)


def accumulate_clones(repo, traffic):
    path = f"data/clones/{repo}.json"
    existing = {}
    if os.path.exists(path):
        with open(path) as f:
            existing = json.load(f)
    if traffic:
        for entry in traffic.get("clones", []):
            day = entry["timestamp"][:10]
            existing[day] = {"count": entry["count"], "uniques": entry["uniques"]}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(existing, f, indent=2, sort_keys=True)
    total = sum(v["count"] for v in existing.values())
    uniques = sum(v["uniques"] for v in existing.values())
    return total, uniques


def main():
    stats = {}
    lang_totals = {}

    for repo in REPOS:
        print(f"fetching {repo}...")
        info = gh(f"/repos/{OWNER}/{repo}")
        if not info:
            continue

        # open_issues_count includes PRs; split via search
        open_pr_s   = search_gh(f"/search/issues?q=repo:{OWNER}/{repo}+is:pr+is:open&per_page=1")
        closed_pr_s = search_gh(f"/search/issues?q=repo:{OWNER}/{repo}+is:pr+is:closed&per_page=1")
        closed_is_s = search_gh(f"/search/issues?q=repo:{OWNER}/{repo}+is:issue+is:closed&per_page=1")
        prs_open      = open_pr_s["total_count"]   if open_pr_s   else 0
        prs_closed    = closed_pr_s["total_count"] if closed_pr_s else 0
        issues_open   = max(0, info["open_issues_count"] - prs_open)
        issues_closed = closed_is_s["total_count"] if closed_is_s else 0

        langs = gh(f"/repos/{OWNER}/{repo}/languages") or {}
        for lang, b in langs.items():
            lang_totals[lang] = lang_totals.get(lang, 0) + b

        # requires Administration → Read-only PAT scope
        traffic = gh(f"/repos/{OWNER}/{repo}/traffic/clones")
        clones_total, clones_unique = accumulate_clones(repo, traffic)

        badge(f"badges/stars/{repo}.json",  "stars",   info["stargazers_count"], "yellow")
        badge(f"badges/forks/{repo}.json",  "forks",   info["forks_count"],      "blue")
        badge(f"badges/issues/{repo}.json", "issues",  f"{issues_open} open | {issues_closed} closed", "orange")
        badge(f"badges/prs/{repo}.json",    "PRs",     f"{prs_open} open | {prs_closed} closed",       "blue")
        badge(f"badges/clones/{repo}.json", "clones",  f"{clones_total} | {clones_unique}",             "green")

        stats[repo] = {
            "stars":          info["stargazers_count"],
            "forks":          info["forks_count"],
            "issues_open":    issues_open,
            "issues_closed":  issues_closed,
            "prs_open":       prs_open,
            "prs_closed":     prs_closed,
            "clones_total":   clones_total,
            "clones_unique":  clones_unique,
            "language":       info.get("language") or "",
        }

    total_stars          = sum(r["stars"]          for r in stats.values())
    total_forks          = sum(r["forks"]          for r in stats.values())
    total_clones         = sum(r["clones_total"]   for r in stats.values())
    total_unique         = sum(r["clones_unique"]  for r in stats.values())
    total_prs_open       = sum(r["prs_open"]       for r in stats.values())
    total_prs_closed     = sum(r["prs_closed"]     for r in stats.values())
    total_issues_open    = sum(r["issues_open"]    for r in stats.values())
    total_issues_closed  = sum(r["issues_closed"]  for r in stats.values())

    badge("badges/total_stars.json",  "total stars",  total_stars,  "yellow")
    badge("badges/total_forks.json",  "total forks",  total_forks,  "blue")
    badge("badges/total_clones.json", "total clones", f"{total_clones} | {total_unique}", "green")
    badge("badges/total_prs.json",    "total PRs",    f"{total_prs_open} open | {total_prs_closed} closed", "blue")

    top_langs = sorted(lang_totals, key=lang_totals.get, reverse=True)[:3]
    badge("badges/languages.json", "languages", " | ".join(top_langs), "blueviolet")

    os.makedirs("data", exist_ok=True)
    with open("data/languages.json", "w") as f:
        json.dump(dict(sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)), f, indent=2)
    with open("data/stats.json", "w") as f:
        json.dump({
            "updated": str(date.today()),
            "repos": stats,
            "totals": {
                "stars":           total_stars,
                "forks":           total_forks,
                "clones_total":    total_clones,
                "clones_unique":   total_unique,
                "prs_open":        total_prs_open,
                "prs_closed":      total_prs_closed,
                "issues_open":     total_issues_open,
                "issues_closed":   total_issues_closed,
            },
            "languages": dict(sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)),
        }, f, indent=2)

    print(f"done. {total_stars} stars, {total_clones} clones across {len(stats)} repos.")


if __name__ == "__main__":
    main()
