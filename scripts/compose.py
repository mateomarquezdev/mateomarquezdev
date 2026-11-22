"""Compose the whole profile as one terminal-window canvas (dark + light).

Usage:  GITHUB_TOKEN=... python3 scripts/compose.py <user> <out_dir>
        python3 scripts/compose.py --sample <out_dir>

Expects snake.svg / snake-light.svg in <out_dir> (from Platane/snk) if available.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import activity  # noqa: E402
from gen_assets import THEMES, FONT, WHOAMI, card_svg, tree_svg, room_svg  # noqa: E402

W = 640


def size(svg):
    m = re.search(r'<svg[^>]*?width="([\d.]+)"[^>]*?height="([\d.]+)"', svg)
    return float(m.group(1)), float(m.group(2))


def bare(svg):
    """Drop a part's own frame or background so it blends into the canvas."""
    svg = re.sub(r'<rect x="1" y="1" width="[\d.]+" height="[\d.]+" rx="10"[^>]*/>', "", svg, count=1)
    svg = re.sub(r'<rect width="[\d.]+" height="[\d.]+" fill="#[0-9A-Fa-f]{6}"/>', "", svg, count=1)
    return svg


def nest(svg, x, y, w=None):
    sw, sh = size(svg)
    w = w or sw
    h = sh * w / sw
    svg = re.sub(r"<svg[^>]*>", f'<svg x="{x}" y="{y}" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {sw:.0f} {sh:.0f}">',
                 bare(svg), count=1)
    return svg, h


def divider(t, y, label):
    return (f'<text x="22" y="{y}" font-size="13" fill="{t["dim"]}" xml:space="preserve">── {label} '
            f'{"─" * (60 - len(label))}</text>')


def canvas(t, act_svg):
    parts, y = [], 0
    # window bar
    bar = [f'<circle cx="{22 + i*20}" cy="20" r="6" fill="none" stroke="{t["dim"]}" stroke-width="1.5"/>' for i in range(3)]
    bar.append(f'<text x="{W/2}" y="25" text-anchor="middle" font-size="12" fill="{t["dim"]}">~/mateomarquezdev — zsh</text>')
    bar.append(f'<line x1="0" y1="40" x2="{W}" y2="40" stroke="{t["line"]}" stroke-width="2"/>')
    parts += bar
    y = 44
    for label, svg, width in [
        (None, card_svg(t, W, 330, WHOAMI, "whoami"), None),
        ("stack", tree_svg(t), None),
        ("activity", act_svg, None),
        ("agents", room_svg(t), W - 44),
    ]:
        if label:
            y += 18
            parts.append(divider(t, y, label))
            y += 6
        x = 22 if width else 0
        s, h = nest(svg, x, y, width)
        parts.append(s)
        y += h
    y += 16
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y:.0f}" viewBox="0 0 {W} {y:.0f}" role="img" '
            f'aria-label="Terminal window: whoami (backend developer and applied AI, Buenos Aires), tech stack, '
            f'contribution activity with a snake, and an ASCII room with little agents">'
            f'<style>text{{font-family:{FONT}}}</style>'
            f'<rect x="1" y="-11" width="{W-2}" height="{y+10:.0f}" rx="10" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>')
    return head + "".join(parts) + "</svg>"


def main():
    if sys.argv[1] == "--sample":
        total, days = activity.sample()
    else:
        total, days = activity.fetch(sys.argv[1])
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    st = activity.stats(days)
    snakes = {"dark": os.path.join(out, "snake.svg"), "light": os.path.join(out, "snake-light.svg")}
    for name, t in THEMES.items():
        act = activity.render(activity.THEMES[name], total, days, *st, snake=snakes[name])
        with open(os.path.join(out, f"activity-{name}.svg"), "w") as f:
            f.write(act)
        with open(os.path.join(out, f"canvas-{name}.svg"), "w") as f:
            f.write(canvas(t, act))


if __name__ == "__main__":
    main()
