"""Generate animated orange/black SVGs for the leeyseo GitHub profile README."""
import html
import os

OUT = "assets"
os.makedirs(OUT, exist_ok=True)

ORANGE = "#FF6B1A"
BG = "#0B0B0B"
PANEL = "#101010"
LINE = "#242424"
TXT = "#EDEDED"
MUTED = "#8C8C8C"
MONO = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,'D2Coding','Noto Sans Mono CJK KR',monospace"
SANS = "'Pretendard','Helvetica Neue',Arial,'Apple SD Gothic Neo','Noto Sans KR',sans-serif"


def esc(s):
    return html.escape(s, quote=False)


class Anim:
    """Collects looping keyframe animations; times are in seconds within one cycle."""

    def __init__(self, T):
        self.T = T
        self.css = []
        self.n = 0

    def add(self, frames, dur=None, extra=""):
        dur = dur or self.T
        name = f"k{self.n}"
        self.n += 1
        frames = sorted(frames, key=lambda f: f[0])
        if frames[0][0] > 0:
            frames.insert(0, (0, frames[0][1], None))
        if frames[-1][0] < dur:
            frames.append((dur, frames[-1][1], None))
        body = []
        for t, props, timing in frames:
            p = round(min(max(t / dur * 100, 0), 100), 3)
            tf = f"animation-timing-function:{timing};" if timing else ""
            body.append(f"{p}%{{{props};{tf}}}")
        self.css.append(f"@keyframes {name}{{{''.join(body)}}}")
        self.css.append(f".{name}{{animation:{name} {dur}s linear infinite;{extra}}}")
        return name

    def style(self):
        base = (
            "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
            ".blink{animation:blink 1s steps(1,end) infinite}"
        )
        return "<style>" + base + "".join(self.css) + "</style>"


def text(x, y, s, size=15, fill=TXT, family=MONO, weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" {extra}>{s}</text>')


def typed(a, x, y, s, start, size=15, cover=PANEL, fill=TXT, cps=0.07, cursor=True):
    """Command text revealed char-by-char by sliding a cover rect to the right."""
    cw = size * 0.6
    n = len(s)
    dur = n * cps
    w = n * cw
    T = a.T
    k = a.add([
        (0, "transform:translateX(0px)", None),
        (start, "transform:translateX(0px)", f"steps({n},end)"),
        (start + dur, f"transform:translateX({w:.1f}px)", None),
        (T * 0.985, f"transform:translateX({w:.1f}px)", "steps(1,end)"),
        (T * 0.99, "transform:translateX(0px)", None),
    ])
    out = text(x, y, esc(s), size, fill, extra=f'textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs"')
    out += f'<rect class="{k}" x="{x - 1}" y="{y - size}" width="{w + cw + 2:.1f}" height="{size + 7}" fill="{cover}"/>'
    if cursor:
        kc = a.add([
            (0, "opacity:0;transform:translateX(0px)", None),
            (start - 0.01, "opacity:0;transform:translateX(0px)", "steps(1,end)"),
            (start, "opacity:1;transform:translateX(0px)", f"steps({n},end)"),
            (start + dur, f"opacity:1;transform:translateX({w:.1f}px)", "steps(1,end)"),
            (start + dur + 0.25, f"opacity:0;transform:translateX({w:.1f}px)", None),
        ])
        out += f'<rect class="{kc}" x="{x}" y="{y - size + 2}" width="{cw:.1f}" height="{size + 2}" fill="{ORANGE}"/>'
    return out, start + dur


def appear(a, inner, t, dx=0, dy=6, fade=0.35):
    k = a.add([
        (0, f"opacity:0;transform:translate({dx}px,{dy}px)", None),
        (t, f"opacity:0;transform:translate({dx}px,{dy}px)", "cubic-bezier(.2,.8,.2,1)"),
        (t + fade, "opacity:1;transform:translate(0px,0px)", None),
    ])
    return f'<g class="{k}">{inner}</g>'


def content_group(a, inner):
    T = a.T
    k = a.add([(0, "opacity:1", None), (T * 0.95, "opacity:1", None), (T * 0.98, "opacity:0", None)])
    return f'<g class="{k}">{inner}</g>'


def window(W, H, title):
    dots = "".join(
        f'<circle cx="{22 + i * 18}" cy="18" r="5.5" fill="{c}"/>'
        for i, c in enumerate([ORANGE, "#7A3A14", "#3A3A3A"])
    )
    return (
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
        f'<path d="M0.5 36 H{W - 0.5}" stroke="{LINE}"/>'
        + dots
        + text(W / 2, 23, esc(title), 12, MUTED, extra='text-anchor="middle"')
    )


def prompt_line(a, x, y, cmd, start, size=15):
    t, end = typed(a, x + size * 1.2, y, cmd, start, size)
    return appear(a, text(x, y, "$", size, ORANGE, weight=700) + t, start - 0.25, dy=0, fade=0.05), end


def final_prompt(a, x, y, t, size=15):
    cur = (f'<rect class="blink" x="{x + size * 1.2}" y="{y - size + 2}" '
           f'width="{size * 0.6:.1f}" height="{size + 2}" fill="{ORANGE}"/>')
    return appear(a, text(x, y, "$", size, ORANGE, weight=700) + cur, t, dy=0, fade=0.1)


def svg(W, H, a, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f"{a.style()}<defs>{defs}</defs>{body}</svg>")


# ---------------------------------------------------------------- hero.svg
def hero():
    W, H, T = 860, 250, 11
    a = Anim(T)
    defs = (
        f'<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1" fill="#1C1C1C"/></pattern>'
        f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{ORANGE}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{ORANGE}" stop-opacity="0.10"/></linearGradient>'
        f'<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="#fff" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="heroclip"><rect width="{W}" height="{H}" rx="12"/></clipPath>'
    )
    scan = a.add([(0, "transform:translateY(-90px)", None), (6, f"transform:translateY({H}px)", None)], dur=6)
    bg = (f'<g clip-path="url(#heroclip)"><rect width="{W}" height="{H}" fill="{BG}"/>'
          f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
          f'<rect class="{scan}" width="{W}" height="90" fill="url(#scan)"/></g>'
          f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{LINE}"/>')

    top = appear(a,
                 text(40, 42, "FOCUS — Agent System · Machine Learning", 12, MUTED, extra='letter-spacing="1.5"')
                 + text(W - 40, 42, "SEOUL, KST", 12, MUTED, extra='letter-spacing="1.5" text-anchor="end"'),
                 0.2, dy=-6)
    pulse = a.add([(0, "opacity:1", None), (0.6, "opacity:0.25", None), (1.2, "opacity:1", None)], dur=1.2)
    live = appear(a, f'<circle class="{pulse}" cx="{W / 2 - 52}" cy="38" r="4" fill="{ORANGE}"/>'
                     + text(W / 2 - 42, 42, "AVAILABLE FOR RESEARCH", 11, ORANGE, extra='letter-spacing="1.2"'),
                  0.4, dy=-6)

    name_anim = a.add([
        (0, "stroke-dashoffset:900;fill-opacity:0;stroke-opacity:1", None),
        (0.5, "stroke-dashoffset:900;fill-opacity:0;stroke-opacity:1", "ease-in-out"),
        (2.6, "stroke-dashoffset:0;fill-opacity:0;stroke-opacity:1", None),
        (3.3, "stroke-dashoffset:0;fill-opacity:1;stroke-opacity:0", None),
    ])
    dot_anim = a.add([(0, "opacity:0", None), (3.2, "opacity:0", None), (3.4, "opacity:1", None),
                      (4.0, "opacity:1", None), (4.5, "opacity:0.2", None), (5.0, "opacity:1", None),
                      (5.5, "opacity:0.2", None), (6.0, "opacity:1", None)])
    name = (f'<text x="38" y="150" font-family="{SANS}" font-size="94" font-weight="800" '
            f'letter-spacing="-3" fill="{TXT}" stroke="{ORANGE}" stroke-width="1.6" '
            f'stroke-dasharray="900" class="{name_anim}">LeeYoonseo'
            f'<tspan class="{dot_anim}" fill="{ORANGE}" stroke="none">.</tspan></text>')

    sub, _ = typed(a, 42, 192, "> AI Engineer @ Unnest  ·  Incoming M.S. @ Yonsei SIL", 3.4, 16,
                   cover=BG, fill=TXT, cps=0.045)
    sub = appear(a, sub, 3.3, dy=0, fade=0.05)

    bar_grow = a.add([(0, "transform:scaleX(0)", None), (0.3, "transform:scaleX(0)", "cubic-bezier(.7,0,.2,1)"),
                      (2.3, "transform:scaleX(1)", None)], extra="transform-box:fill-box;transform-origin:left")
    shine = a.add([(0, "transform:translateX(-140px)", None), (2.6, f"transform:translateX({W}px)", None)], dur=2.6)
    bar = (f'<rect class="{bar_grow}" x="40" y="218" width="{W - 80}" height="3" fill="{ORANGE}"/>'
           f'<g clip-path="url(#heroclip)"><rect class="{shine}" x="0" y="217" width="140" height="5" '
           f'fill="url(#shine)" opacity="0.6"/></g>')
    body = bg + content_group(a, top + live + name + sub + bar)
    return svg(W, H, a, body, defs)


# ---------------------------------------------------------------- terminal.svg
def terminal():
    W, H, T = 860, 392, 17
    a = Anim(T)
    x = 32
    parts = []
    l, e = prompt_line(a, x, 76, "whoami", 0.5)
    parts.append(l)
    parts.append(appear(a, text(x, 106, "Lee Yoonseo · 이윤서", 21, ORANGE, weight=700), e + 0.3))

    l, e = prompt_line(a, x, 142, "cat role.txt", e + 1.0)
    parts.append(l)
    parts.append(appear(a, text(x, 168, f'AI Engineer / Backend &amp; Architecture <tspan fill="{ORANGE}">@ Unnest</tspan>'), e + 0.3))
    parts.append(appear(a, text(x, 192, f'Incoming M.S. · Industrial Engineering <tspan fill="{ORANGE}">@ Yonsei SIL</tspan> <tspan fill="{MUTED}">(2027.03)</tspan>'), e + 0.45))

    l, e = prompt_line(a, x, 228, "echo $FOCUS", e + 1.0)
    parts.append(l)
    parts.append(appear(a, text(x, 254, "Agent System · Machine Learning"), e + 0.3))

    l, e = prompt_line(a, x, 290, "echo $MOTTO", e + 1.0)
    parts.append(l)
    parts.append(appear(a, text(x, 316, esc('"I don\'t avoid problems — I dig until I find the answer."')), e + 0.3))
    parts.append(appear(a, text(x, 340, "문제를 피하지 않고, 답을 찾을 때까지 파고듭니다.", 15, MUTED, family=SANS), e + 0.5))

    parts.append(final_prompt(a, x, 372, e + 1.0))
    body = window(W, H, "leeyseo@unnest: ~") + content_group(a, "".join(parts))
    return svg(W, H, a, body)


# ---------------------------------------------------------------- career.svg
ENTRIES = [
    ("2027.03 · NEXT", False, "Incoming M.S. · Industrial Engineering, Yonsei University",
     "연세대학교 산업공학과 석사과정 입학 예정 · System Intelligence Lab (SIL)"),
    ("2026.07 · NOW", True, "AI Engineer / Backend &amp; Architecture @ Unnest",
     "언네스트 AI 엔지니어 · Agent Platform (Minerva) 백엔드·아키텍처"),
    ("NAVER PAY", False, "Industry–Academia R&amp;D @ Naver Financial (Naver Pay)",
     "네이버페이 스코어 모델 고도화 · 테이블+세션 로그 결합 대출 전환 예측"),
    ("PATENT", False, "Inventor · ML-based STT system patent",
     "머신러닝 기반 STT 시스템 특허 발명자"),
    ("AWARD", False, "Winner of multiple AI competitions",
     "AI 관련 대회 다수 수상"),
    ("SCHOLAR", False, "Innovation Scholarship · University Innovation Support Project",
     "대학혁신지원사업 혁신인재 장학생"),
]


def career():
    W, T = 860, 15
    gap = 56
    y0 = 116
    H = y0 + gap * len(ENTRIES) + 22
    a = Anim(T)
    parts = []
    l, e = prompt_line(a, 32, 72, f"tail -n {len(ENTRIES)} career.log", 0.4)
    parts.append(l)

    first = e + 0.4
    gx = 34
    rail = a.add([(0, "transform:scaleY(0)", None), (first, "transform:scaleY(0)", "ease-out"),
                  (first + 0.9 * len(ENTRIES), "transform:scaleY(1)", None)],
                 extra="transform-box:fill-box;transform-origin:top")
    parts.append(f'<rect class="{rail}" x="{gx - 1}" y="{y0 - 18}" width="2" '
                 f'height="{gap * (len(ENTRIES) - 1) + 8}" fill="{ORANGE}" opacity="0.45"/>')

    pulse = a.add([(0, "transform:scale(1);opacity:1", None), (0.8, "transform:scale(2.2);opacity:0", None)],
                  dur=1.6, extra="transform-box:fill-box;transform-origin:center")
    for i, (tag, live, en, kr) in enumerate(ENTRIES):
        y = y0 + i * gap
        t = first + i * 0.9
        tx, tw = 54, 136
        node = f'<circle cx="{gx}" cy="{y - 5}" r="5" fill="{PANEL}" stroke="{ORANGE}" stroke-width="2"/>'
        if live:
            node += f'<circle class="{pulse}" cx="{gx}" cy="{y - 5}" r="5" fill="{ORANGE}"/>'
            node += f'<circle cx="{gx}" cy="{y - 5}" r="3" fill="{ORANGE}"/>'
            box = f'<rect x="{tx}" y="{y - 17}" width="{tw}" height="24" rx="5" fill="{ORANGE}"/>'
            tcol = BG
        else:
            box = f'<rect x="{tx + 0.5}" y="{y - 16.5}" width="{tw - 1}" height="23" rx="5" fill="none" stroke="{ORANGE}"/>'
            tcol = ORANGE
        tagtxt = text(tx + tw / 2, y, tag, 12, tcol, weight=700, extra='text-anchor="middle" letter-spacing="0.5"')
        lines = text(206, y, en, 15, TXT) + text(206, y + 21, kr, 13, MUTED, family=SANS)
        parts.append(appear(a, node, t, dy=0, fade=0.2))
        parts.append(appear(a, box + tagtxt + lines, t, dx=-14, dy=0, fade=0.45))

    parts.append(final_prompt(a, 32, H - 18, first + 0.9 * len(ENTRIES) + 0.4))
    body = window(W, H, "~/career.log") + content_group(a, "".join(parts))
    return svg(W, H, a, body)


# ---------------------------------------------------------------- divider.svg
def divider():
    W, H = 860, 14
    a = Anim(3.6)
    k = a.add([(0, "transform:translateX(-200px)", None), (3.6, f"transform:translateX({W}px)", None)])
    defs = (f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0"/>'
            f'<stop offset="0.8" stop-color="{ORANGE}"/><stop offset="1" stop-color="#FFD1B3"/></linearGradient>')
    body = (f'<rect y="6" width="{W}" height="2" fill="{LINE}"/>'
            f'<rect class="{k}" y="5" width="200" height="4" rx="2" fill="url(#g)"/>')
    return svg(W, H, a, body, defs)


for fname, fn in [("hero.svg", hero), ("terminal.svg", terminal), ("career.svg", career), ("divider.svg", divider)]:
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(fn())
    print("wrote", fname)
