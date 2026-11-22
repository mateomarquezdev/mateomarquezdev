"""Render an ASCII activity card (dark + light) from the GitHub contribution calendar.

Usage:  GITHUB_TOKEN=... python3 scripts/activity.py <user> <out_dir>
        python3 scripts/activity.py --sample <out_dir>   (fake data, for previews)

The calendar counts private contributions too when "Include private contributions
on my profile" is enabled in the GitHub profile settings.
"""
import json, os, random, sys, urllib.request
from datetime import date, timedelta
from xml.sax.saxutils import escape

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
THEMES = {
    "dark": dict(bg="#121212", line="#2A2A2A", text="#EDEDED", dim="#8C8C8C", faint="#3A3A3A"),
    "light": dict(bg="#FFFFFF", line="#DDDDDD", text="#111111", dim="#5E5E5E", faint="#D0D0D0"),
}
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch(user):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return cal["totalContributions"], days


def sample():
    random.seed(7)
    start = date.today() - timedelta(days=364)
    days = [((start + timedelta(i)).isoformat(), max(0, int(random.gauss(3, 4)))) for i in range(365)]
    return sum(c for _, c in days), days


def stats(days):
    counts = [c for _, c in days]
    tail = counts[:-1] if counts and counts[-1] == 0 else counts  # today may still be empty
    cur = 0
    for c in reversed(tail):
        if c == 0:
            break
        cur += 1
    best = run = 0
    for c in counts:
        run = run + 1 if c else 0
        best = max(best, run)
    active = sum(1 for c in counts if c)
    top = max(days, key=lambda d: d[1])
    return cur, best, active, top


def render(t, total, days, cur, best, active, top):
    w, h, x0 = 640, 132, 22
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
         f'aria-label="{total} contributions in the last year, current streak {cur} days, longest streak {best} days, {active} active days">',
         f"<style>text{{font-family:{FONT}}}.cur{{animation:cu 1s steps(1) infinite}}@keyframes cu{{0%{{opacity:1}}50%{{opacity:0}}}}</style>",
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}" stroke-width="2"/>',
         f'<text x="{x0}" y="34" font-size="15" fill="{t["dim"]}">$ git log --stats --last 52w</text>']
    cols = [("contributions", f"{total:,}"), ("current streak", f"{cur}d"), ("longest streak", f"{best}d"), ("active days", f"{active}")]
    for i, (k, v) in enumerate(cols):
        x = x0 + i * ((w - 2 * x0) // 4)
        o.append(f'<text x="{x}" y="72" font-size="24" font-weight="700" fill="{t["text"]}">{escape(v)}</text>')
        o.append(f'<text x="{x}" y="94" font-size="12" fill="{t["dim"]}">{escape(k)}</text>')
    o.append(f'<text x="{x0}" y="118" font-size="12" fill="{t["dim"]}">best day {escape(top[0])} · {top[1]} contributions<tspan class="cur">▍</tspan></text>')
    o.append("</svg>")
    return "".join(o)


def main():
    if sys.argv[1] == "--sample":
        total, days = sample()
    else:
        total, days = fetch(sys.argv[1])
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    s = stats(days)
    for name, t in THEMES.items():
        with open(os.path.join(out, f"activity-{name}.svg"), "w") as f:
            f.write(render(t, total, days, *s))


if __name__ == "__main__":
    main()
