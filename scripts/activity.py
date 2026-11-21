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
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)][-52:]
    nz = sorted(c for _, c in days if c)
    q = [nz[int(len(nz) * f)] if nz else 1 for f in (0.25, 0.5, 0.75)]

    def cell(c):
        if c == 0:
            return "·", t["faint"]
        if c <= q[0]:
            return ":", t["dim"]
        if c <= q[1]:
            return "+", t["dim"]
        if c <= q[2]:
            return "#", t["text"]
        return "@", t["text"]

    cw, ch, x0, y0 = 11, 13, 22, 112
    w = x0 * 2 + 52 * cw
    h = y0 + 7 * ch + 56
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
         f'aria-label="{total} contributions in the last year, current streak {cur} days, longest streak {best} days">',
         f"<style>text{{font-family:{FONT}}}.c{{opacity:0;animation:in .5s forwards}}@keyframes in{{to{{opacity:1}}}}"
         f".cur{{animation:cu 1s steps(1) infinite}}@keyframes cu{{0%{{opacity:1}}50%{{opacity:0}}}}</style>",
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}" stroke-width="2"/>',
         f'<text x="{x0}" y="34" font-size="13" fill="{t["dim"]}">$ git log --stats --last 52w</text>']
    cols = [("contributions", f"{total:,}"), ("current streak", f"{cur}d"), ("longest streak", f"{best}d"), ("active days", f"{active}")]
    for i, (k, v) in enumerate(cols):
        x = x0 + i * ((w - 2 * x0) // 4)
        o.append(f'<text x="{x}" y="66" font-size="22" font-weight="700" fill="{t["text"]}">{escape(v)}</text>')
        o.append(f'<text x="{x}" y="86" font-size="11" fill="{t["dim"]}">{escape(k)}</text>')
    for wi, wk in enumerate(weeks):
        for di, (_, c) in enumerate(wk):
            s, col = cell(c)
            o.append(f'<text class="c" style="animation-delay:{wi*0.02:.2f}s" x="{x0 + wi*cw + 2}" y="{y0 + di*ch + 10}" '
                     f'font-size="12" fill="{col}">{s}</text>')
    yb = y0 + 7 * ch + 28
    o.append(f'<text x="{x0}" y="{yb}" font-size="11" fill="{t["dim"]}">less · : + # @ more</text>')
    o.append(f'<text x="{w - x0}" y="{yb}" text-anchor="end" font-size="11" fill="{t["dim"]}">best day {escape(top[0])} · {top[1]}<tspan class="cur">▍</tspan></text>')
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
