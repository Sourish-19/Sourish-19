"""Render every README card into cards/ from data/*.json.

Cards are shown on GitHub through <img>, so each SVG is self-contained:
fonts are embedded as base64 WOFF, animation is CSS keyframes only, and
everything switches off under prefers-reduced-motion.

    python scripts/render_readme_cards.py          # animated
    STATIC=1 python scripts/render_readme_cards.py # final frame, for screenshots
"""
import base64
import json
import os
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"
STATIC = os.environ.get("STATIC") == "1"

# ------------------------------------------------------------------ profile
USER = "Sourish-19"
NAME = "Sourish"
FULL_NAME = "Sourish Sri Vignesh S"
TAGLINE = ("UI/UX designer &", "GenAI developer.")
ABOUT = (
    "B.E. Computer Engineering · MIT Bengaluru · '28",
    "Previously UI/UX Designer @ Crescentia One",
)
TILES = [
    {
        "key": "design", "no": "01", "word": "Design", "color": "#D9481F",
        "lines": ["1st place × 2, UI/UX Sprint", "Figma prototypes → handoff", "Usability tests that iterate"],
        "cta": "connect on LinkedIn",
    },
    {
        "key": "genai", "no": "02", "word": "GenAI", "color": "#6B4EFF",
        "lines": ["QLoRA + DPO on Qwen2.5-7B", "Hybrid RAG · FAISS + BM25", "Red-teaming & guardrails"],
        "cta": "see IndicVoice RAG",
    },
    {
        "key": "build", "no": "03", "word": "Build", "color": "#0E8F69",
        "lines": ["FastAPI · React · TypeScript", "Azure · Modal · Firebase", "Serverless, scale-to-zero"],
        "cta": "all repositories",
    },
]

# "By the numbers": (value, decimals, prefix, suffix, label line 1, label line 2)
NUMBERS = [
    (24.55, 2, "", " ms", "P50 retrieval latency", "IndicVoice RAG"),
    (95, 0, "", "%+", "Socratic compliance", "fine-tuned Qwen2.5-7B"),
    (11298, 0, "", "", "passages indexed", "FAISS + BM25 hybrid"),
    (2, 0, "", "×", "UI/UX Sprint wins", "TechSolstice '24 & '25"),
    (10, 0, "Top ", "", "of 1,500+ teams", "PEC HACK 3.0"),
]

# Project cards; "repo" pulls live metadata from data/repos.json when public
PROJECTS = [
    {
        "name": "IndicVoice RAG", "repo": "indic-voice", "kicker": "RETRIEVAL · VOICE", "color": "#6B4EFF",
        "blurb": "Hybrid FAISS + BM25 search fused with Reciprocal Rank Fusion over 11,298 passages, "
                 "with speech-to-text in 15 Indian languages and verified, extractive answers.",
        "metric": ("24.55 ms", "P50 latency on a 200 ms budget"),
        "stack": ["Python", "FastAPI", "FAISS", "BM25", "React"],
    },
    {
        "name": "Socratic AI", "repo": None, "kicker": "FINE-TUNING · SAFETY", "color": "#D9481F",
        "blurb": "Qwen2.5-7B tuned with QLoRA and DPO so answer-withholding lives in the weights, "
                 "served scale-to-zero on Modal with dynamic LoRA adapters.",
        "metric": ("<2%", "answer leakage, 6 jailbreak vectors"),
        "stack": ["Qwen2.5-7B", "QLoRA", "DPO", "PyTorch", "Modal"],
    },
    {
        "name": "AcaEdge", "repo": None, "kicker": "PLATFORM · TEAM OF 6", "color": "#0E8F69",
        "blurb": "Multi-role NBA accreditation platform for MIT Bengaluru: CO-PO attainment, marks "
                 "pipelines and Index 1–11 reports. I delivered the complete frontend.",
        "metric": ("4 roles", "under review for campus-wide rollout"),
        "stack": ["React", "TypeScript", "Node.js", "SQL", "Azure"],
    },
    {
        "name": "AI-PR-Reviewer", "repo": "ai-pr-reviewer", "kicker": "LLM TOOLING", "color": "#3178C6",
        "blurb": "Local-first REST service that reviews GitHub PR diffs for bugs and vulnerabilities "
                 "with diff-aware prompting, in modular, unit-tested layers.",
        "metric": None,
        "stack": ["Python", "FastAPI", "React", "Gemini API"],
    },
    {
        "name": "ORCA", "repo": "ORCA", "kicker": "MULTI-AGENT · SIH", "color": "#0B7A8C",
        "blurb": "Marine ecosystem reasoning with collaborative agents: turns natural-language "
                 "questions into evidence-backed, safety-checked decisions for coastal India.",
        "metric": None,
        "stack": ["TypeScript", "Python", "Multi-agent"],
    },
    {
        "name": "ISL Platform", "repo": "isl", "kicker": "VISION · ACCESSIBILITY", "color": "#B4579A",
        "blurb": "Indian Sign Language recognition and translation platform, "
                 "with a FastAPI backend serving the recognition pipeline.",
        "metric": None,
        "stack": ["Python", "FastAPI", "Computer vision"],
    },
]

TIMELINE = [
    ("Jul 2024", "MIT Bengaluru", "Started B.E. in Computer Engineering", False),
    ("2024", "First place", "UI/UX Design Sprint, TechSolstice '24", False),
    ("Feb 2025", "Graphic Designer", "Branding for 10+ events, Tech Solstice '25", False),
    ("2025", "First place, again", "UI/UX Design Sprint, TechSolstice '25", False),
    ("Aug 2025", "UI/UX Designer", "Crescentia One · Figma, Agile, usability tests", False),
    ("May 2028", "Graduating", "B.E. Computer Engineering", True),
]

STACK = [
    ("LANGUAGES", "#19181D", ["Python", "TypeScript", "JavaScript", "Java", "SQL"]),
    ("ML & RETRIEVAL", "#6B4EFF", ["PyTorch", "Transformers", "PEFT / QLoRA", "DPO", "FAISS", "BM25", "E5"]),
    ("BACKEND & CLOUD", "#0E8F69", ["FastAPI", "Node.js", "Express", "Azure", "Firebase", "Modal", "Vercel", "GitHub Actions"]),
    ("FRONTEND & DESIGN", "#D9481F", ["React", "Vite", "Figma", "Design systems", "Usability testing"]),
    ("DATA", "#3178C6", ["SQL schema design", "MongoDB"]),
]

LINKEDIN = "https://www.linkedin.com/in/sourish-sri-vignesh-s"

# ------------------------------------------------------------------ palette
PAPER = "#F6F2EA"
PANEL = "#EEE8DC"
LINE = "#E1DACB"
INK = "#19181D"
MUTED = "#76716A"
FAINT = "#A9A296"
CREAM = "#FFF9EF"
VIOLET = "#6B4EFF"
GREEN = "#0E8F69"
GRAPH = ["#E9E3D6", "#D7CEFF", "#AE9BFF", "#7F63FF", "#5233E8"]
LANG_COLORS = {
    "TypeScript": "#3178C6", "JavaScript": "#E3B341", "Python": "#3572A5",
    "HTML": "#E34C26", "CSS": "#663399", "Java": "#B07219",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ------------------------------------------------------------------ svg kit
FONTS = {
    "serif": ("DM Serif Display", "serif-400.woff", "normal"),
    "serif-i": ("DM Serif Display", "serif-400i.woff", "italic"),
    "mono": ("Plex Mono", "mono-400.woff", "normal"),
    "mono-m": ("Plex Mono Medium", "mono-500.woff", "normal"),
}
_font_cache = {}

BASE_CSS = """
.serif{font-family:'DM Serif Display',Georgia,'Times New Roman',serif}
.it{font-style:italic}
.mono{font-family:'Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.mm{font-family:'Plex Mono Medium','Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.fb{transform-box:fill-box;transform-origin:center}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}65%{opacity:1;transform:scale(1.18)}100%{opacity:1;transform:scale(1)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes swing{0%{opacity:0;transform:translateY(80px) rotate(7deg)}55%{opacity:1;transform:translateY(-8px) rotate(-1.6deg)}78%{transform:translateY(3px) rotate(.6deg)}100%{opacity:1;transform:none}}
@keyframes pulse{0%{opacity:.75;transform:scale(1)}100%{opacity:0;transform:scale(3.4)}}
@keyframes beat{0%,100%{transform:scale(1)}50%{transform:scale(1.35)}}
@keyframes nudge{0%,72%,100%{transform:translate(0,0)}82%{transform:translate(4px,-4px)}91%{transform:translate(0,0)}}
@keyframes sweep{0%{transform:translateX(0)}32%,100%{transform:translateX(var(--d,700px))}}
@keyframes flash{from,to{opacity:1}}
.rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.fade{animation:fade .5s ease-out both}
.pop{animation:pop .45s cubic-bezier(.2,.8,.2,1) both}
.grow{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
.swing{transform-box:fill-box;transform-origin:50% 100%;animation:swing 1.1s cubic-bezier(.2,.8,.2,1) both}
.ring{transform-box:fill-box;transform-origin:center;opacity:0;animation:pulse 2.6s ease-out infinite}
.beat{transform-box:fill-box;transform-origin:center;animation:beat 1.6s ease-in-out infinite}
.nudge{animation:nudge 3.2s ease-in-out infinite}
.sweep{animation:sweep 6s cubic-bezier(.45,0,.2,1) infinite both}
.cf{opacity:0;animation:flash .05s step-end}
.cl{animation:fade .01s linear both}
"""
# Same rules serve reduced motion and the STATIC screenshot mode.
STILL = "*{animation:none!important}.ring,.sweep,.cf{display:none}"


def font_face(key):
    if key not in _font_cache:
        family, file, style = FONTS[key]
        b64 = base64.b64encode((ROOT / "fonts" / file).read_bytes()).decode()
        _font_cache[key] = (
            f"@font-face{{font-family:'{family}';font-style:{style};"
            f"src:url(data:font/woff;base64,{b64}) format('woff')}}"
        )
    return _font_cache[key]


def svg(w, h, body, fonts=("serif", "mono"), css=""):
    style = "".join(font_face(f) for f in fonts) + BASE_CSS + css
    style += STILL if STATIC else f"@media (prefers-reduced-motion:reduce){{{STILL}}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none">\n<style>{style}</style>\n{body}\n</svg>\n'
    )


def d(s):
    """animation-delay style attribute."""
    return f' style="animation-delay:{s:.3f}s"'


def card_bg(w, h, fill=PAPER, stroke=LINE, r=18):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'


def fmt_date(s):
    dt = datetime.strptime(s[:10], "%Y-%m-%d")
    return f"{dt.day} {MONTHS[dt.month - 1]} {dt.year}"


def count_up(x, y, value, cls, fill, start, size, anchor="start", suffix="", prefix="", decimals=0):
    """Count from 0 to value with 18 frames; CSS can't change text, so each
    frame is its own <text> shown for 50 ms."""
    frames = 18
    out = []
    for i in range(frames):
        t = i / (frames - 1)
        v = value * (1 - (1 - t) ** 3)
        v = round(v, decimals) if decimals else round(v)
        delay = start + i * 0.05
        last = i == frames - 1
        klass = "cl" if last else "cf"
        out.append(
            f'<text x="{x}" y="{y}" class="{cls} {klass}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{d(delay)}>{escape(prefix)}{v:,.{decimals}f}{escape(suffix)}</text>'
        )
    return "\n".join(out)


# ------------------------------------------------------------------ data
def load_json(name, default):
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def contribution_stats(days):
    active = sum(1 for x in days if x["count"] > 0)
    longest = run = 0
    for x in days:
        run = run + 1 if x["count"] > 0 else 0
        longest = max(longest, run)
    # the last cell is "today" and still in progress: a 0 there doesn't break the streak
    tail = days[:-1] if days and days[-1]["count"] == 0 else days
    current = 0
    for x in reversed(tail):
        if x["count"] <= 0:
            break
        current += 1
    best = max(days, key=lambda x: x["count"], default={"date": "", "count": 0})
    months = OrderedDict()
    for x in days:
        months[x["date"][:7]] = months.get(x["date"][:7], 0) + x["count"]
    return {
        "total": sum(x["count"] for x in days),
        "active": active,
        "longest": longest,
        "current": current,
        "best_day": best,
        "months": list(months.items())[-12:],
    }


# ------------------------------------------------------------------ cards
def hero(stats, repos, portrait):
    W, H = 860, 340
    b = [card_bg(W, H)]

    # header line
    b.append(f'<text x="44" y="50" class="mm fade" font-size="11" letter-spacing="1.6" fill="{MUTED}"{d(0)}>'
             f'{escape(FULL_NAME.upper())}  ·  @{escape(USER.upper())}</text>')

    # name with a violet shine sweeping across it every few seconds
    b.append('<defs><mask id="shine" maskUnits="userSpaceOnUse" x="0" y="0" width="860" height="340">'
             '<polygon class="sweep" points="-150,40 -100,40 -150,190 -200,190" fill="#fff" '
             'style="--d:620px;animation-delay:1.6s"/></mask></defs>')
    b.append(f'<g class="rise"{d(0.1)}>'
             f'<text x="40" y="152" class="serif" font-size="104" letter-spacing="-2" fill="{INK}">{escape(NAME)}</text>'
             f'<text x="40" y="152" class="serif" font-size="104" letter-spacing="-2" fill="{VIOLET}" mask="url(#shine)">{escape(NAME)}</text>'
             f'</g>')

    # tagline, one line at a time
    b.append(f'<text x="44" y="200" class="serif rise" font-size="32" fill="{INK}"{d(0.35)}>{escape(TAGLINE[0])}</text>')
    b.append(f'<text x="44" y="236" class="serif it rise" font-size="32" fill="{VIOLET}"{d(0.5)}>{escape(TAGLINE[1])}</text>')
    for i, line in enumerate(ABOUT):
        b.append(f'<text x="44" y="{272 + i * 19}" class="mono rise" font-size="12" fill="{MUTED}"{d(0.65 + i * 0.1)}>{escape(line)}</text>')

    # live status: latest push
    latest = next((r for r in repos if r["name"] != USER), None)
    if latest:
        b.append(f'<g class="fade"{d(1.0)}>'
                 f'<circle cx="49" cy="314" r="4" fill="{GREEN}" class="beat"/>'
                 f'<circle cx="49" cy="314" r="4" fill="{GREEN}" class="ring" style="animation-delay:1.2s"/>'
                 f'<text x="62" y="318" class="mono" font-size="11.5" fill="{INK}">latest push → '
                 f'<tspan class="mm">{escape(latest["name"])}</tspan>'
                 f'<tspan fill="{MUTED}">  · {fmt_date(latest["pushed_at"])}</tspan></text></g>')

    # ASCII portrait panel, printed in row by row
    px, py, pw, ph = 528, 22, 310, 296
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{PANEL}" class="fade"{d(0)}/>')
    fs, lh = 5.0, 4.3
    cols = max((len(r) for r in portrait), default=1)
    tx = px + (pw - cols * fs * 0.6) / 2
    ty = py + (ph - 22 - len(portrait) * lh) / 2 + fs * 0.8
    for i, row in enumerate(portrait):
        if row.strip():
            b.append(f'<text x="{tx:.1f}" y="{ty + i * lh:.2f}" class="mm fade" font-size="{fs}" '
                     f'fill="{INK}" xml:space="preserve"{d(0.25 + i * 0.018)}>{escape(row)}</text>')
    b.append(f'<text x="{px + pw - 12}" y="{py + ph - 12}" text-anchor="end" class="mono fade" font-size="9.5" '
             f'fill="{MUTED}"{d(0.25 + len(portrait) * 0.018)}>portrait.txt · {len(portrait)} rows</text>')
    return svg(W, H, "\n".join(b), fonts=("serif", "serif-i", "mono", "mono-m"))


def graph(days, stats):
    W, H = 860, 226
    b = [card_bg(W, H)]
    b.append(f'<text x="40" y="52" class="serif rise" font-size="28" fill="{INK}"{d(0.2)}>A year of commits</text>')
    if days:
        span = f"{fmt_date(days[0]['date'])} — {fmt_date(days[-1]['date'])}"
        b.append(f'<text x="{W - 40}" y="50" text-anchor="end" class="mono fade" font-size="11.5" fill="{MUTED}"{d(0.3)}>'
                 f'<tspan class="mm" fill="{VIOLET}">{stats["total"]:,}</tspan> contributions · {span}</text>')

    cols, step, size = 53, 14.15, 11
    x0, y0 = 68, 88
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d") if days else datetime.now()
    lead = (first.weekday() + 1) % 7
    skip = max(0, (lead + len(days) + 6) // 7 - cols)
    last_month, labels = -1, []
    for idx, day in enumerate(days):
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        col = (lead + idx) // 7 - skip
        row = (dt.weekday() + 1) % 7
        if not 0 <= col < cols:
            continue
        if row == 0 and dt.month != last_month:
            last_month = dt.month
            if not labels or col - labels[-1][0] >= 3:
                labels.append((col, MONTHS[dt.month - 1]))
        x, y = x0 + col * step, y0 + row * step
        lvl = max(0, min(int(day.get("level", 0)), 4))
        n = day["count"]
        b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="3" fill="{GRAPH[lvl]}" '
                 f'class="pop fb"{d(0.35 + col * 0.022 + row * 0.008)}>'
                 f'<title>{n} contribution{"s" if n != 1 else ""} on {fmt_date(day["date"])}</title></rect>')
    for col, m in labels:
        b.append(f'<text x="{x0 + col * step:.1f}" y="{y0 - 9}" class="mono fade" font-size="10" fill="{MUTED}"{d(0.3)}>{m}</text>')
    for r, wd in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b.append(f'<text x="40" y="{y0 + r * step + 9.5:.1f}" class="mono fade" font-size="10" fill="{FAINT}"{d(0.3)}>{wd}</text>')

    # legend
    lx = W - 40 - 5 * 15 - 34
    b.append(f'<g class="fade"{d(1.6)}><text x="{lx - 8}" y="{H - 24}" text-anchor="end" class="mono" font-size="10" fill="{MUTED}">less</text>')
    for i, c in enumerate(GRAPH):
        b.append(f'<rect x="{lx + i * 15}" y="{H - 34}" width="11.6" height="11.6" rx="3" fill="{c}"/>')
    b.append(f'<text x="{lx + 5 * 15 + 4}" y="{H - 24}" class="mono" font-size="10" fill="{MUTED}">more</text></g>')
    b.append(f'<text x="40" y="{H - 24}" class="mono fade" font-size="10.5" fill="{MUTED}"{d(1.6)}>'
             f'refreshed daily by a GitHub Action</text>')
    return svg(W, H, "\n".join(b), fonts=("serif", "mono", "mono-m"))


def activity(stats):
    W, H = 860, 300
    b = [card_bg(W, H)]
    b.append(f'<text x="40" y="52" class="serif rise" font-size="28" fill="{INK}"{d(0.2)}>Month by month</text>')

    months = stats["months"]
    best_i = max(range(len(months)), key=lambda i: months[i][1]) if months else -1
    top = max((v for _, v in months), default=1) or 1
    base, maxh, bw, gap, x0 = 248, 150, 28, 11, 40
    b.append(f'<line x1="{x0 - 4}" y1="{base + .5}" x2="{x0 + 12 * (bw + gap) - gap + 4}" y2="{base + .5}" stroke="{LINE}" class="fade"{d(0.3)}/>')
    for i, (ym, v) in enumerate(months):
        h = max(3, v / top * maxh)
        x = x0 + i * (bw + gap)
        fill = VIOLET if i == best_i else "#D3CCBE"
        b.append(f'<rect x="{x}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="5" fill="{fill}" class="grow"{d(0.4 + i * 0.06)}>'
                 f'<title>{v} contributions in {MONTHS[int(ym[5:]) - 1]} {ym[:4]}</title></rect>')
        b.append(f'<text x="{x + bw / 2}" y="{base + 20}" text-anchor="middle" class="mono fade" font-size="10" '
                 f'fill="{INK if i == best_i else MUTED}"{d(0.4 + i * 0.06)}>{MONTHS[int(ym[5:]) - 1]}</text>')
        if i == best_i:
            b.append(f'<text x="{x + bw / 2}" y="{base - h - 10:.1f}" text-anchor="middle" class="mm pop fb" font-size="12" '
                     f'fill="{VIOLET}"{d(1.45)}>{v}</text>')

    # stats panel
    sx = 520
    b.append(f'<rect x="{sx}" y="76" width="{W - sx - 32}" height="196" rx="12" fill="{PANEL}" class="fade"{d(0.3)}/>')
    cells = [
        ("contributions", stats["total"], ""),
        ("active days", stats["active"], ""),
        ("longest streak", stats["longest"], "d"),
        ("current streak", stats["current"], "d"),
    ]
    for i, (label, val, suf) in enumerate(cells):
        cx = sx + 24 + (i % 2) * 148
        cy = 128 + (i // 2) * 74
        b.append(count_up(cx, cy, val, "serif", VIOLET if i == 0 else INK, 0.6 + i * 0.12, 38, suffix=suf))
        b.append(f'<text x="{cx}" y="{cy + 20}" class="mono fade" font-size="10.5" letter-spacing=".6" fill="{MUTED}"{d(0.6 + i * 0.12)}>{label.upper()}</text>')
    bd = stats["best_day"]
    if bd.get("date"):
        b.append(f'<text x="{sx + 24}" y="256" class="mono fade" font-size="10.5" fill="{MUTED}"{d(1.6)}>busiest day · '
                 f'<tspan fill="{INK}">{fmt_date(bd["date"])}</tspan> · {bd["count"]} contributions</text>')
    return svg(W, H, "\n".join(b), fonts=("serif", "mono", "mono-m"))


def tile(t, i):
    W, H = 280, 330
    c = t["color"]
    start = 0.5 + i * 0.16
    b = [f'<defs><clipPath id="clip"><rect x="0" y="0" width="{W}" height="{H}" rx="20"/></clipPath></defs>',
         f'<g class="swing"{d(start)}>',
         f'<g clip-path="url(#clip)">',
         f'<rect width="{W}" height="{H}" fill="{c}"/>',
         # big faint number in the background
         f'<text x="{W + 14}" y="{H + 34}" text-anchor="end" class="serif" font-size="230" fill="{CREAM}" opacity=".09">{t["no"]}</text>',
         # periodic shine
         f'<polygon class="sweep" points="-120,0 -60,0 -150,{H} -210,{H}" fill="#fff" opacity=".16" '
         f'style="--d:{W + 260}px;animation-delay:{start + 1.4 + i * 0.5:.2f}s"/>',
         '</g>',
         f'<text x="26" y="44" class="mm" font-size="11" letter-spacing="1.8" fill="{CREAM}" opacity=".85">{t["no"]} / {t["key"].upper()}</text>',
         f'<circle cx="{W - 32}" cy="40" r="5" fill="{CREAM}"/>',
         f'<circle cx="{W - 32}" cy="40" r="5" fill="none" stroke="{CREAM}" stroke-width="1.5" class="ring" style="animation-delay:{start + 1.1:.2f}s"/>',
         f'<text x="22" y="156" class="serif" font-size="70" letter-spacing="-1.5" fill="{CREAM}">{escape(t["word"])}</text>']
    for j, line in enumerate(t["lines"]):
        b.append(f'<text x="26" y="{196 + j * 22}" class="mono" font-size="12.5" fill="{CREAM}" opacity=".92">{escape(line)}</text>')
    b.append(f'<line x1="26" y1="{H - 56}" x2="{W - 26}" y2="{H - 56}" stroke="{CREAM}" opacity=".3"/>')
    b.append(f'<text x="26" y="{H - 28}" class="mm" font-size="12" fill="{CREAM}">{escape(t["cta"])}</text>')
    b.append(f'<g class="nudge" style="animation-delay:{start + 1.5:.2f}s">'
             f'<path d="M{W - 44} {H - 26}l12-12M{W - 41} {H - 38}h9v9" stroke="{CREAM}" stroke-width="1.8" stroke-linecap="round"/></g>')
    b.append('</g>')
    return svg(W, H, "\n".join(b), fonts=("serif", "mono-m", "mono"))


def wrap(text, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + (1 if cur else 0) > width:
            lines.append(cur)
            cur = w_
        else:
            cur = f"{cur} {w_}".strip()
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: width - 1].rstrip(" ,.;:-") + "…"
    return lines


def chip(x, y, text, h=22, fs=10.5, fill=PANEL, stroke="none", color=INK, dot=None):
    """A rounded label; returns (svg, width)."""
    pad = 11
    w = len(text) * fs * 0.6 + pad * 2 + (12 if dot else 0)
    out = f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{fill}" stroke="{stroke}"/>'
    tx = x + pad
    if dot:
        out += f'<circle cx="{x + pad + 3:.1f}" cy="{y + h / 2}" r="3.2" fill="{dot}"/>'
        tx += 12
    out += (f'<text x="{tx:.1f}" y="{y + h / 2 + fs * 0.36:.1f}" class="mono" font-size="{fs}" '
            f'fill="{color}">{escape(text)}</text>')
    return out, w


def project_card(p, repo, i):
    W, H = 420, 252
    c = p["color"]
    start = 0.2 + (i % 2) * 0.12 + (i // 2) * 0.1
    b = [f'<g class="rise"{d(start)}>', card_bg(W, H)]
    b.append(f'<rect x="28" y="33" width="8" height="8" rx="2" fill="{c}"/>')
    b.append(f'<text x="44" y="41" class="mm" font-size="10.5" letter-spacing="1.4" fill="{c}">{escape(p["kicker"])}</text>')
    if repo:
        b.append(f'<text x="{W - 28}" y="41" text-anchor="end" class="mono" font-size="10" fill="{FAINT}">'
                 f'updated {fmt_date(repo["pushed_at"])}</text>')
    b.append(f'<text x="27" y="78" class="serif" font-size="28" fill="{INK}">{escape(p["name"])}</text>')
    b.append(f'<g class="nudge" style="animation-delay:{start + 1.2:.2f}s">'
             f'<path d="M{W - 40} 72l11-11M{W - 37} 61h8v8" stroke="{MUTED}" stroke-width="1.6" stroke-linecap="round"/></g>')
    for j, line in enumerate(wrap(p["blurb"], 54, 3)):
        b.append(f'<text x="28" y="{106 + j * 17}" class="mono" font-size="11" fill="{MUTED}">{escape(line)}</text>')
    if p.get("metric"):
        val, label = p["metric"]
        b.append(f'<text x="27" y="183" class="serif pop fb" font-size="26" fill="{c}"{d(start + 0.5)}>{escape(val)}</text>')
        b.append(f'<text x="{28 + len(val) * 12.5 + 12:.0f}" y="181" class="mono" font-size="10.5" fill="{INK}">{escape(label)}</text>')
    elif repo:
        lang = repo.get("language") or "Code"
        b.append(f'<circle cx="33" cy="177" r="5" fill="{LANG_COLORS.get(lang, MUTED)}"/>')
        b.append(f'<text x="46" y="181" class="mono" font-size="11" fill="{INK}">{escape(lang)}  ·  public repo on GitHub</text>')
    x = 28
    for j, t in enumerate(p["stack"]):
        svg_, w = chip(x, 206, t)
        b.append(f'<g class="pop fb"{d(start + 0.6 + j * 0.06)}>{svg_}</g>')
        x += w + 6
    b.append('</g>')
    return svg(W, H, "\n".join(b), fonts=("serif", "mono", "mono-m"))


def numbers():
    W, H = 860, 206
    b = [card_bg(W, H)]
    b.append(f'<text x="40" y="52" class="serif rise" font-size="28" fill="{INK}"{d(0.1)}>By the numbers</text>')
    b.append(f'<text x="{W - 40}" y="50" text-anchor="end" class="mono fade" font-size="11.5" fill="{MUTED}"{d(0.2)}>'
             f'projects, benchmarks &amp; competitions</text>')
    colors = [VIOLET, "#D9481F", GREEN, INK, "#3178C6"]
    cw = (W - 80) / len(NUMBERS)
    for i, (val, dec, pre, suf, l1, l2) in enumerate(NUMBERS):
        x = 40 + i * cw
        if i:
            b.append(f'<line x1="{x - 14:.1f}" y1="88" x2="{x - 14:.1f}" y2="170" stroke="{LINE}" class="fade"{d(0.3)}/>')
        b.append(count_up(f"{x:.1f}", 124, val, "serif", colors[i % len(colors)], 0.35 + i * 0.12, 30,
                          prefix=pre, suffix=suf, decimals=dec))
        b.append(f'<text x="{x:.1f}" y="150" class="mm fade" font-size="10.5" fill="{INK}"{d(0.4 + i * 0.12)}>{escape(l1)}</text>')
        b.append(f'<text x="{x:.1f}" y="168" class="mono fade" font-size="10" fill="{MUTED}"{d(0.45 + i * 0.12)}>{escape(l2)}</text>')
    return svg(W, H, "\n".join(b), fonts=("serif", "mono", "mono-m"))


def timeline():
    W, H = 860, 300
    css = ("@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}"
           ".draw{animation:draw 1.6s cubic-bezier(.45,0,.2,1) both}")
    b = [card_bg(W, H)]
    b.append(f'<text x="40" y="52" class="serif rise" font-size="28" fill="{INK}"{d(0.1)}>Timeline</text>')
    b.append(f'<text x="{W - 40}" y="50" text-anchor="end" class="mono fade" font-size="11.5" fill="{MUTED}"{d(0.2)}>'
             f'2024 → 2028</text>')
    ay, n = 172, len(TIMELINE)
    xs = [110 + k * (640 / (n - 1)) for k in range(n)]
    solid = xs[-2] - xs[0] + 30
    b.append(f'<path d="M{xs[0] - 30} {ay}H{xs[-2]}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="{solid:.0f}" '
             f'class="draw" style="--len:{solid:.0f}px;animation-delay:.3s"/>')
    b.append(f'<path d="M{xs[-2]} {ay}H{xs[-1] + 30}" stroke="{FAINT}" stroke-width="1.5" stroke-dasharray="4 5" class="fade"{d(1.8)}/>')
    for k, (when, title, sub, future) in enumerate(TIMELINE):
        x = xs[k]
        t0 = 0.4 + (k / (n - 1)) * 1.4
        above = k % 2 == 0
        b.append(f'<line x1="{x}" y1="{ay - 10 if above else ay + 10}" x2="{x}" y2="{ay - 24 if above else ay + 24}" '
                 f'stroke="{LINE}" stroke-width="1.5" class="fade"{d(t0)}/>')
        if future:
            b.append(f'<circle cx="{x}" cy="{ay}" r="6" fill="{PAPER}" stroke="{VIOLET}" stroke-width="2" class="pop fb"{d(t0)}/>')
        else:
            b.append(f'<circle cx="{x}" cy="{ay}" r="6" fill="{VIOLET if k == n - 2 else INK}" class="pop fb"{d(t0)}/>')
        if k == n - 2:
            b.append(f'<circle cx="{x}" cy="{ay}" r="6" fill="none" stroke="{VIOLET}" stroke-width="1.5" class="ring" '
                     f'style="animation-delay:{t0 + 0.6:.2f}s"/>')
        lines = wrap(sub, 30, 2)
        if above:
            # stack upwards from the stem so 1- and 2-line subs both sit snug
            base = ay - 34
            ys_sub = [base - 15 * (len(lines) - 1 - j) for j in range(len(lines))]
            y_title = ys_sub[0] - 19
            y_when = y_title - 21
        else:
            y_when = ay + 42
            y_title = y_when + 22
            ys_sub = [y_title + 19 + 15 * j for j in range(len(lines))]
        g = [f'<text x="{x}" y="{y_when}" text-anchor="middle" class="mm" font-size="10.5" letter-spacing="1" fill="{VIOLET}">{escape(when.upper())}</text>',
             f'<text x="{x}" y="{y_title}" text-anchor="middle" class="serif" font-size="18" fill="{INK}">{escape(title)}</text>']
        for j, line in enumerate(lines):
            g.append(f'<text x="{x}" y="{ys_sub[j]}" text-anchor="middle" class="mono" font-size="10.2" fill="{MUTED}">{escape(line)}</text>')
        b.append(f'<g class="rise"{d(t0 + 0.1)}>{"".join(g)}</g>')
    return svg(W, H, "\n".join(b), fonts=("serif", "mono", "mono-m"), css=css)


def stack():
    W = 860
    b, y, k = [], 84, 0
    x0, xmax = 214, W - 40
    for label, color, items in STACK:
        b.append(f'<text x="40" y="{y + 16}" class="mm fade" font-size="10.5" letter-spacing="1.2" fill="{color}"{d(0.2 + k * 0.03)}>{escape(label)}</text>')
        x = x0
        for t in items:
            w = len(t) * 10.5 * 0.6 + 22 + 12
            if x + w > xmax:
                x, y = x0, y + 32
            svg_, w = chip(x, y, t, h=24, fill="#FBF8F2", stroke=LINE, dot=color)
            b.append(f'<g class="pop fb"{d(0.3 + k * 0.035)}>{svg_}</g>')
            x += w + 7
            k += 1
        y += 42
    H = y + 8
    head = [card_bg(W, H),
            f'<text x="40" y="52" class="serif rise" font-size="28" fill="{INK}"{d(0.1)}>Toolbox</text>',
            f'<text x="{W - 40}" y="50" text-anchor="end" class="mono fade" font-size="11.5" fill="{MUTED}"{d(0.2)}>'
            f'what I reach for</text>']
    return svg(W, H, "\n".join(head + b), fonts=("serif", "mono", "mono-m"))


def connect():
    W, H = 860, 160
    b = [card_bg(W, H)]
    b.append(f'<text x="40" y="76" class="serif rise" font-size="32" fill="{INK}"{d(0.1)}>Let’s build something '
             f'<tspan class="it" fill="{VIOLET}">thoughtful.</tspan></text>')
    b.append(f'<text x="42" y="108" class="mono rise" font-size="12" fill="{MUTED}"{d(0.25)}>'
             f'Design-minded engineer · GenAI &amp; full-stack · Bengaluru, India</text>')
    b.append(f'<text x="42" y="130" class="mono rise" font-size="11" fill="{FAINT}"{d(0.35)}>'
             f'in/sourish-sri-vignesh-s  ·  github.com/{escape(USER)}</text>')
    bx, by, bw, bh = W - 40 - 220, 56, 220, 48
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="none" stroke="{VIOLET}" '
             f'stroke-width="2" class="ring halo"/>')
    b.append(f'<g class="pop fb"{d(0.5)}>'
             f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{INK}"/>'
             f'<text x="{bx + 24}" y="{by + 29}" class="mm" font-size="12.5" fill="{CREAM}">Connect on LinkedIn</text>'
             f'<g class="nudge" style="animation-delay:1.4s"><path d="M{bx + bw - 40} {by + 30}l10-10M{bx + bw - 37} {by + 20}h7v7" '
             f'stroke="{CREAM}" stroke-width="1.7" stroke-linecap="round"/></g></g>')
    css = ("@keyframes halo{0%{opacity:.6;transform:scale(1)}100%{opacity:0;transform:scale(1.12,1.5)}}"
           ".halo{animation:halo 2.8s ease-out 1.2s infinite}")
    return svg(W, H, "\n".join(b), fonts=("serif", "serif-i", "mono", "mono-m"), css=css)


# ------------------------------------------------------------------ main
def main():
    contrib = load_json("contributions.json", {"days": []})
    days = contrib.get("days", [])
    repos = load_json("repos.json", {"repos": []}).get("repos", [])
    portrait_file = ROOT / "data" / "portrait.txt"
    portrait = portrait_file.read_text(encoding="utf-8").splitlines() if portrait_file.exists() else []
    stats = contribution_stats(days)
    by_name = {r["name"]: r for r in repos}

    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(stats, repos, portrait),
        "numbers.svg": numbers(),
        "graph.svg": graph(days, stats),
        "activity.svg": activity(stats),
        "timeline.svg": timeline(),
        "stack.svg": stack(),
        "connect.svg": connect(),
    }
    for i, t in enumerate(TILES):
        files[f"tile-{t['key']}.svg"] = tile(t, i)
    for i, p in enumerate(PROJECTS):
        files[f"project-{i + 1}.svg"] = project_card(p, by_name.get(p["repo"]) if p["repo"] else None, i)

    for stale in OUT.glob("*.svg"):
        if stale.name not in files:
            stale.unlink()
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
    print(f"rendered {len(files)} cards into cards/{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()
