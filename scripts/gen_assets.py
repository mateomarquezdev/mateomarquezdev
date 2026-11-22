"""Generate the ASCII-room README assets (dark + light) for the profile repo."""
import os, sys
from xml.sax.saxutils import escape


AGENT = "#D97757"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
THEMES = {
    "dark": dict(bg="#0B0B0B", ascii="#333333", text="#EDEDED", dim="#8C8C8C", line="#2A2A2A", panel="#121212", code="#A3A3A3"),
    "light": dict(bg="#FAFAFA", ascii="#CFCFCF", text="#111111", dim="#5E5E5E", line="#DDDDDD", panel="#FFFFFF", code="#444444"),
}

# ---------- ascii room grid ----------
W, H = 78, 44
CW, CH = 8, 12
PAD = 16


def room():
    g = [[" "] * W for _ in range(H)]

    def put(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            g[y][x] = c

    def text(x, y, s):
        for i, c in enumerate(s):
            put(x + i, y, c)

    for y in range(H):
        for x in range(W):
            if (x * 7 + y * 13) % 11 == 0:
                put(x, y, ".")

    def box(x, y, w, h, fill):
        for j in range(h):
            for i in range(w):
                ex, ey = i in (0, w - 1), j in (0, h - 1)
                put(x + i, y + j, "+" if ex and ey else "-" if ey else "|" if ex else fill)

    box(3, 2, 21, 14, " ")
    for j in range(3, 15):
        put(13, j, "|")
    for i in range(4, 23):
        put(i, 8, "-")
    for j in range(3, 15):
        for i in range(4, 23):
            if (i * 5 + j * 3) % 9 == 0 and i != 13 and j != 8:
                put(i, j, ":")
    box(26, 4, 13, 9, ":")
    text(30, 7, "</>")
    text(28, 9, " ship it ")
    box(2, 19, 19, 20, " ")
    for y in (24, 29, 34):
        for i in range(3, 20):
            put(i, y, "=")
    books = "[|#]|[##]|[|]#|["
    for y0 in (20, 25, 30, 35):
        for k in range(4):
            for i in range(3, 20):
                if k > 0 or i % 3:
                    put(i, y0 + k, books[(i + y0 + k) % len(books)])
    box(42, 3, 33, 17, " ")
    text(55, 2, "[ ]")
    for i in range(38, 77):
        put(i, 34, "=")
        put(i, 35, "-")
    for j in range(36, 43):
        put(39, j, "|")
        put(75, j, "|")
    text(41, 30, "\\|/"); text(42, 31, "|"); text(41, 32, "[_]"); text(41, 33, "[_]")
    text(69, 27, "/^^\\")
    for j in range(28, 34):
        put(71, j, "|")
    box(33, 36, 5, 7, " "); put(35, 38, "o"); put(35, 40, "O")
    for i in range(W):
        put(i, 43, "_")
    return ["".join(r) for r in g]


# ---------- sprites (Clawd-style fan art) ----------
TOP = ["..BBBBBBBBBBBB..", "..BBkBBBBBBkBB..", "..BBkBBBBBBkBB.."]
LAPTOP = ["..LLLLLLLLLLLL..", "..LLLLLggLLLLL..", "..LLLLLLLLLLLL..", ".DDDDDDDDDDDDDD."]
CODER_A = TOP + ["BBBBBBBBBBBBBBBB", "..BBBBBBBBBBBB..", "..BBBBBBBBBBBB.."] + LAPTOP
CODER_B = TOP + ["..BBBBBBBBBBBB..", "BBBBBBBBBBBBBBBB", "..BBBBBBBBBBBB.."] + LAPTOP
DJ = ["...hhhhhhhh...", "..h........h..", ".hBBBBBBBBBBh.", "hhBkkBBBBkkBhh", "hhBBBBBBBBBBhh",
      "BBBBBBBBBBBBBB", "..BBBBBBBBBB..", "..B.B....B.B..", "..B.B....B.B.."]
SLEEPER = ["..BBBBBBBBBB..", "..BBBBBBBBBB..", "..BkkBBBBkkB..", "BBBBBBBBBBBBBB", "..BBBBBBBBBB..", "..B.B....B.B.."]
WAVER = ["B............B", "B.BBBBBBBBBB.B", "BBBkBBBBBBkBBB", "..BkBBBBBBkB..", "..BBBBBBBBBB..",
         "..BBBBBBBBBB..", "..B.B....B.B..", "..B.B....B.B.."]
PAL = {"B": AGENT, "k": "#111111", "L": "#262626", "g": "#FFFFFF", "D": "#4D4D4D", "h": "#9A9A9A"}


def sprite(rows, x, y, cell, cls=""):
    out = [f'<g class="{cls}" transform="translate({x} {y})">' if cls else f'<g transform="translate({x} {y})">']
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c in PAL:
                out.append(f'<rect x="{i*cell}" y="{j*cell}" width="{cell}" height="{cell}" fill="{PAL[c]}"/>')
    out.append("</g>")
    return "".join(out)


CODE = ['@GetMapping("/orders")', 'public List<Order> all() {', '  return repo.findAll();', '}', '',
        'def run(task):', '  plan = llm.plan(task)', '  for step in plan:', '    tools[step.name](**step.args)', '',
        '$ docker build -t api .', '$ git push origin main', 'ok  tests passed', '']

CSS = """
.fa{animation:fa .45s steps(1) infinite}.fb{animation:fb .45s steps(1) infinite}
@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}
.bob{animation:bob .55s ease-in-out infinite alternate}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(-6px)}}
.breathe{transform-box:fill-box;transform-origin:50% 100%;animation:br 2.6s ease-in-out infinite}
@keyframes br{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.9)}}
.zz{animation:zz 2.6s linear infinite;opacity:0}
@keyframes zz{0%{opacity:0;transform:translate(0,8px)}30%{opacity:1}100%{opacity:0;transform:translate(14px,-26px)}}
.note{transform-box:fill-box;transform-origin:center;animation:nt 1.1s ease-in-out infinite alternate}
@keyframes nt{from{transform:translateY(0) rotate(-8deg)}to{transform:translateY(-8px) rotate(8deg)}}
.scroll{animation:sc 12s linear infinite}
@keyframes sc{from{transform:translateY(0)}to{transform:translateY(-%dpx)}}
.cur{animation:cu 1s steps(1) infinite}@keyframes cu{0%%{opacity:1}50%%{opacity:0}}
"""


def room_svg(t):
    lines = room()
    sw, sh = W * CW + PAD * 2, H * CH + PAD * 2
    lh = 16
    css = (CSS.replace("%dpx", f"{len(CODE)*lh}px").replace("%%", "%"))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{sw}" height="{sh}" viewBox="0 0 {sw} {sh}" role="img" '
         f'aria-label="An ASCII room where four little agents work: one codes on a laptop, one listens to music, one sleeps on a bookshelf">',
         f"<style>{css}text{{font-family:{FONT}}}</style>",
         f'<rect width="{sw}" height="{sh}" fill="{t["bg"]}"/>']
    o.append(f'<g fill="{t["ascii"]}" font-size="12" style="white-space:pre">')
    for j, ln in enumerate(lines):
        o.append(f'<text x="{PAD}" y="{PAD + j*CH + 10}" textLength="{W*CW}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{escape(ln)}</text>')
    o.append("</g>")
    # monitor code
    mx, my, mw, mh = PAD + 43 * CW, PAD + 4 * CH, 31 * CW, 15 * CH
    o.append(f'<clipPath id="scr"><rect x="{mx}" y="{my}" width="{mw}" height="{mh}"/></clipPath>')
    o.append(f'<g clip-path="url(#scr)"><g class="scroll" fill="{t["code"]}" font-size="11" style="white-space:pre">')
    for k, ln in enumerate(CODE + CODE):
        if ln:
            o.append(f'<text x="{mx+8}" y="{my + 16 + k*lh}" xml:space="preserve">{escape(ln)}</text>')
    o.append("</g></g>")
    # status
    o.append(f'<rect x="{sw-170}" y="{PAD-2}" width="154" height="18" fill="{t["panel"]}"/>')
    o.append(f'<text x="{sw-PAD-4}" y="{PAD+11}" text-anchor="end" font-size="12" fill="{t["dim"]}">● 4 agents online<tspan class="cur">_</tspan></text>')
    # agents
    desk_y = PAD + 34 * CH
    o.append(sprite(CODER_A, PAD + 52 * CW, desk_y + 8 - 80, 8, "fa"))
    o.append(sprite(CODER_B, PAD + 52 * CW, desk_y + 8 - 80, 8, "fb"))
    floor_y = PAD + 44 * CH
    o.append(f'<g class="bob">{sprite(DJ, PAD + 21*CW, floor_y - 6 - 9*6, 6)}</g>')
    o.append(f'<g class="note"><text x="{PAD + 33*CW}" y="{floor_y - 70}" font-size="18" fill="{t["text"]}">♪</text></g>')
    o.append(f'<g class="note" style="animation-delay:.5s"><text x="{PAD + 35*CW}" y="{floor_y - 88}" font-size="14" fill="{t["dim"]}">♫</text></g>')
    shelf_y = PAD + 19 * CH
    o.append(f'<g class="breathe">{sprite(SLEEPER, PAD + 4*CW, shelf_y - 36, 6)}</g>')
    o.append(f'<text class="zz" x="{PAD + 15*CW}" y="{shelf_y - 30}" font-size="16" font-weight="700" fill="{t["dim"]}">z</text>')
    o.append(f'<text class="zz" style="animation-delay:1.3s" x="{PAD + 17*CW}" y="{shelf_y - 44}" font-size="12" font-weight="700" fill="{t["dim"]}">z</text>')
    o.append("</svg>")
    return "".join(o)


def card_svg(t, w, h, lines, label):
    """A terminal card: list of (text, role) where role in cmd|out|strong."""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">',
         f"<style>text{{font-family:{FONT}}}.cur{{animation:cu 1s steps(1) infinite}}@keyframes cu{{0%{{opacity:1}}50%{{opacity:0}}}}</style>",
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>']
    y = 34
    for i, (s, role) in enumerate(lines):
        color = t["dim"] if role == "cmd" else t["text"]
        weight = "700" if role == "strong" else "400"
        cur = '<tspan class="cur">▍</tspan>' if i == len(lines) - 1 else ""
        o.append(f'<text x="22" y="{y}" font-size="15" font-weight="{weight}" fill="{color}" xml:space="preserve">{escape(s)}{cur}</text>')
        y += 26 if role != "gap" else 12
    o.append("</svg>")
    return "".join(o)


def link_svg(t, cmd, label, art, primary):
    w, h = 260, 84
    bg, fg = (t["text"], t["bg"]) if primary else (t["panel"], t["text"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">',
         f"<style>text{{font-family:{FONT}}}</style>",
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{bg}" stroke="{t["text"] if primary else t["line"]}" stroke-width="2"/>']
    for j, a in enumerate(art):
        o.append(f'<text x="16" y="{30 + j*13}" font-size="12" fill="{fg}" xml:space="preserve">{escape(a)}</text>')
    o.append(f'<text x="80" y="36" font-size="12" fill="{fg}" opacity=".7">{escape(cmd)}</text>')
    o.append(f'<text x="80" y="58" font-size="17" font-weight="700" fill="{fg}">{escape(label)}</text>')
    o.append(f'<text x="{w-18}" y="58" text-anchor="end" font-size="17" fill="{fg}">↗</text>')
    o.append("</svg>")
    return "".join(o)


WHOAMI = [("$ whoami", "cmd"), ("backend developer · applied AI", "strong"), ("buenos aires, ar", "cmd"),
          ("", "gap"), ("$ cat about.txt", "cmd"),
          ("I design APIs and services in Java/Spring and .NET,", "out"),
          ("and build AI agents in Python that operate real", "out"),
          ("production tools: they read data, call APIs and", "out"),
          ("automate the repetitive work.", "out"),
          ("", "gap"), ("$ uptime", "cmd"),
          ("on github since 2022 · 22 repos · 16 tools", "out")]


STACK = [
    ("backend/", None, "dir"),
    ("├── java · spring boot", "REST APIs, auth, tests", "item"),
    ("├── c# · .net", "APIs, business logic", "item"),
    ("└── architecture", "controller → service → repo", "item"),
    ("applied-ai/", None, "dir"),
    ("├── python", "AI work, automations", "item"),
    ("├── llm apis · tool calling", "agents that use real tools", "item"),
    ("└── automations", "no more repetitive work", "item"),
    ("data/", None, "dir"),
    ("├── mysql", "relational, SQL", "item"),
    ("├── mongodb", "documents", "item"),
    ("└── redis", "caching", "item"),
    ("cloud-ops/", None, "dir"),
    ("├── docker · linux", "containers", "item"),
    ("├── google cloud", "deploys", "item"),
    ("└── github actions", "CI/CD", "item"),
    ("frontend/", None, "dir"),
    ("└── angular · react · ts", "UIs for my own APIs", "item"),
]


def tree_svg(t):
    w, lh = 640, 24
    rows = []
    y = 34
    rows.append((y, "$ tree ~/stack", None, "cmd"))
    y += 34
    for i, (name, desc, kind) in enumerate(STACK):
        if kind == "dir" and i > 0:
            y += 10
        rows.append((y, name, desc, kind))
        y += lh
    rows.append((y + 6, "5 directories, 13 files", None, "cmd"))
    h = y + 34
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Tech stack: backend, applied AI, data, cloud and ops, frontend">',
         f"<style>text{{font-family:{FONT}}}.r{{opacity:0;animation:in .3s forwards}}@keyframes in{{to{{opacity:1}}}}"
         f".cur{{animation:cu 1s steps(1) infinite}}@keyframes cu{{0%{{opacity:1}}50%{{opacity:0}}}}</style>",
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>']
    for k, (yy, name, desc, kind) in enumerate(rows):
        delay = f' style="animation-delay:{k*0.06:.2f}s"'
        color = t["dim"] if kind == "cmd" else t["text"]
        weight = "700" if kind == "dir" else "400"
        cur = '<tspan class="cur">▍</tspan>' if k == len(rows) - 1 else ""
        o.append(f'<g class="r"{delay}><text x="22" y="{yy}" font-size="15" font-weight="{weight}" fill="{color}" xml:space="preserve">{escape(name)}{cur}</text>')
        if desc:
            o.append(f'<text x="300" y="{yy}" font-size="14" fill="{t["dim"]}" xml:space="preserve">{escape(desc)}</text>')
        o.append("</g>")
    o.append("</svg>")
    return "".join(o)

LINKS = {
    "site": ("$ open mateomarquez.com", "portfolio", [" .--. ", "| () |", " `--´ "], False),
    "linkedin": ("$ ssh linkedin/mateo-marquez", "linkedin", ["+----+", "| in |", "+----+"], False),
    "mail": ("$ mail --to me", "say hi", ["+----+", "|\\  /|", "+----+"], True),
}


def tab_svg(t, icon, label, sub):
    """A tab of the window's top bar: monochrome icon + label."""
    w, h = 260, 56
    fg, dim = t["text"], t["dim"]
    icons = {
        "globe": f'<g fill="none" stroke="{fg}" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 7h14M5 17h14"/></g>',
        "linkedin": f'<rect x="3" y="3" width="18" height="18" rx="3" fill="{fg}"/><text x="12" y="17" text-anchor="middle" font-size="12" font-weight="700" fill="{t["panel"]}" font-family="Arial, Helvetica, sans-serif">in</text>',
        "mail": f'<g fill="none" stroke="{fg}" stroke-width="1.8" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/></g>',
    }
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'<style>text{{font-family:{FONT}}}</style>'
            f'<path d="M1 {h} V11 Q1 1 11 1 H{w-11} Q{w-1} 1 {w-1} 11 V{h}" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>'
            f'<g transform="translate(18 16)">{icons[icon]}</g>'
            f'<text x="54" y="26" font-size="15" font-weight="700" fill="{fg}">{escape(label)}</text>'
            f'<text x="54" y="44" font-size="11" fill="{dim}">{escape(sub)}</text>'
            f'<text x="{w-18}" y="34" text-anchor="end" font-size="15" fill="{fg}">↗</text></svg>')


TABS = {"site": ("globe", "portfolio", "mateomarquez.com"),
        "linkedin": ("linkedin", "linkedin", "/in/mateo-marquez"),
        "mail": ("mail", "email", "say hi")}


def main(OUT):
    os.makedirs(OUT, exist_ok=True)
    for name, t in THEMES.items():
        for key, (icon, label, sub) in TABS.items():
            open(os.path.join(OUT, f"tab-{key}-{name}.svg"), "w").write(tab_svg(t, icon, label, sub))


if __name__ == "__main__":
    main(sys.argv[1])
