"""Build an animated orange/black GitHub stats card from the GitHub GraphQL API.

Usage:
  GITHUB_TOKEN=... python tools/stats.py <login> <out.svg>
  python tools/stats.py <login> <out.svg> --demo     # sample numbers, no network
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import (Anim, LINE, MUTED, ORANGE, TXT, appear, content_group,  # noqa: E402
                 final_prompt, prompt_line, svg, text, window, esc)

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100,
                 orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch(login):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
                 "Content-Type": "application/json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    u = data["data"]["user"]
    repos = u["repositories"]["nodes"]
    sizes = {}
    for repo in repos:
        for e in repo["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    stats = [
        ("Contributions (1y)", u["contributionsCollection"]["contributionCalendar"]["totalContributions"]),
        ("Commits (1y)", u["contributionsCollection"]["totalCommitContributions"]),
        ("Pull Requests", u["pullRequests"]["totalCount"]),
        ("Issues", u["issues"]["totalCount"]),
        ("Stars Earned", sum(r["stargazerCount"] for r in repos)),
        ("Contributed To", u["repositoriesContributedTo"]["totalCount"]),
        ("Public Repos", u["repositories"]["totalCount"]),
    ]
    return stats, sizes


def demo():
    return ([("Contributions (1y)", 812), ("Commits (1y)", 640), ("Pull Requests", 57), ("Issues", 23),
             ("Stars Earned", 41), ("Contributed To", 12), ("Public Repos", 38)],
            {"Python": 620000, "Jupyter Notebook": 410000, "JavaScript": 180000, "TypeScript": 90000,
             "C++": 40000, "HTML": 30000, "Shell": 8000})


def build(login, stats, sizes):
    W, H, T = 860, 316, 14
    a = Anim(T)
    parts = []
    l, e = prompt_line(a, 32, 72, f"gh stats {login}", 0.4)
    parts.append(l)
    first = e + 0.35
    y0, step = 108, 26

    for i, (label, value) in enumerate(stats):
        y = y0 + i * step
        row = (text(32, y, esc(label), 14, MUTED)
               + f'<path d="M190 {y - 4} H352" stroke="{LINE}" stroke-dasharray="2 4"/>'
               + text(388, y, f"{value:,}", 15, ORANGE, weight=700, extra='text-anchor="end"'))
        parts.append(appear(a, row, first + i * 0.12, dx=-10, dy=0))

    parts.append(appear(a, f'<path d="M420 92 V{y0 + step * 6 + 6}" stroke="{LINE}"/>', first, dy=0))
    parts.append(appear(a, text(450, 92, "TOP LANGUAGES", 11, MUTED, extra='letter-spacing="1.5"'), first, dy=0))

    total = sum(sizes.values()) or 1
    langs = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    for i, (name, size) in enumerate(langs):
        y = y0 + 10 + i * step
        pct = size / total * 100
        bw = max(210 * pct / 100, 3)
        t = first + 0.3 + i * 0.15
        grow = a.add([(0, "transform:scaleX(0)", None), (t, "transform:scaleX(0)", "cubic-bezier(.2,.8,.2,1)"),
                      (t + 0.9, "transform:scaleX(1)", None)],
                     extra="transform-box:fill-box;transform-origin:left")
        opacity = 1 - i * 0.13
        row = (text(450, y, esc(name), 13, TXT)
               + f'<rect x="572" y="{y - 9}" width="210" height="8" rx="4" fill="#1C1C1C"/>'
               + f'<rect class="{grow}" x="572" y="{y - 9}" width="{bw:.1f}" height="8" rx="4" '
                 f'fill="{ORANGE}" fill-opacity="{opacity:.2f}"/>'
               + text(828, y, f"{pct:.1f}%", 12, MUTED, extra='text-anchor="end"'))
        parts.append(appear(a, row, t - 0.1, dy=0, fade=0.25))

    parts.append(final_prompt(a, 32, H - 20, first + 0.3 + len(langs) * 0.15 + 1.0))
    return svg(W, H, a, window(W, H, f"~/stats — {login}") + content_group(a, "".join(parts)))


if __name__ == "__main__":
    login, out = sys.argv[1], sys.argv[2]
    stats, sizes = demo() if "--demo" in sys.argv else fetch(login)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(login, stats, sizes))
    print("wrote", out)
