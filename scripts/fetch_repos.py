"""Save public repo metadata to data/repos.json for the README cards."""
import json
import os
import sys

import requests


def main(username="Sourish-19", out="data/repos.json"):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(
        f"https://api.github.com/users/{username}/repos",
        params={"per_page": 100, "sort": "pushed", "type": "owner"},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    repos = [
        {
            "name": r["name"],
            "description": r["description"] or "",
            "language": r["language"] or "",
            "stars": r["stargazers_count"],
            "pushed_at": r["pushed_at"],
            "url": r["html_url"],
        }
        for r in resp.json()
        if not r["fork"] and not r["private"]
    ]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"username": username, "public_repos": len(repos), "repos": repos}, f, indent=2)
    print(f"saved {len(repos)} repos to {out}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
