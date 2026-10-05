#!/usr/bin/env python3
"""Comic panels for the Tales page: original SVG drawings of Panchatantra and Jataka episodes.

Each panel is a layered scene (sky, hills, ground, trees, characters). A shared set of SVG filters gives the
flat shapes soft lighting, a ground shadow, slightly hand-inked edges and paper grain.
Stories are traditional (public domain) and retold in original words.
"""
import html, json

E = html.escape
# ---------------------------------------------------------------- drawing
def g(x, y, s, flip, inner):
    sx = -s if flip else s
    return f'<g transform="translate({x} {y}) scale({sx} {s})" stroke="#2b2118" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">{inner}</g>'

def eye(x, y, r=2.6):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke-width="1"/><circle cx="{x+.7}" cy="{y}" r="{r/2}" fill="#111" stroke="none"/>'

def lion(c="#8A4B12", face="#E3AE55", body="#C98A3B"):
    return (f'<path d="M-34 -36 q-18 -6 -20 -26" fill="none" stroke-width="3"/><circle cx="-54" cy="-64" r="5" fill="{c}"/>'
            f'<rect x="-28" y="-20" width="9" height="20" fill="{body}"/><rect x="14" y="-20" width="9" height="20" fill="{body}"/>'
            f'<ellipse cx="-2" cy="-36" rx="38" ry="24" fill="{body}"/>'
            f'<circle cx="34" cy="-58" r="31" fill="{c}"/><circle cx="34" cy="-56" r="20" fill="{face}"/>'
            f'<circle cx="22" cy="-76" r="6" fill="{face}"/><circle cx="46" cy="-76" r="6" fill="{face}"/>'
            f'{eye(28,-60)}{eye(42,-60)}<path d="M31 -52 l6 0 l-3 5z" fill="#5a2d0c"/><path d="M28 -44 q6 6 12 0" fill="none"/>')

def hare(body="#F4F1EA"):
    return (f'<circle cx="-24" cy="-26" r="8" fill="#fff"/><ellipse cx="0" cy="-24" rx="24" ry="17" fill="{body}"/>'
            f'<rect x="8" y="-14" width="8" height="14" rx="4" fill="{body}"/><rect x="-14" y="-10" width="16" height="10" rx="5" fill="{body}"/>'
            f'<ellipse cx="17" cy="-58" rx="4.5" ry="17" fill="{body}"/><ellipse cx="27" cy="-57" rx="4.5" ry="16" fill="{body}"/>'
            f'<circle cx="24" cy="-38" r="12" fill="{body}"/>{eye(28,-40,2.4)}<circle cx="35" cy="-37" r="2.2" fill="#e88"/>')

def monkey(body="#8B5A2B", face="#E8C39A"):
    return (f'<path d="M-12 -30 q-30 6 -26 -30 q2 -10 10 -8" fill="none" stroke-width="4"/>'
            f'<rect x="-10" y="-16" width="8" height="16" fill="{body}"/><rect x="4" y="-16" width="8" height="16" fill="{body}"/>'
            f'<ellipse cx="0" cy="-42" rx="16" ry="26" fill="{body}"/><ellipse cx="2" cy="-38" rx="9" ry="16" fill="{face}"/>'
            f'<path d="M12 -50 q16 6 18 -8" fill="none" stroke-width="5"/>'
            f'<circle cx="0" cy="-78" r="14" fill="{body}"/><circle cx="-14" cy="-80" r="5" fill="{face}"/><circle cx="14" cy="-80" r="5" fill="{face}"/>'
            f'<ellipse cx="1" cy="-75" rx="9" ry="8" fill="{face}"/>{eye(-3,-80,2.2)}{eye(6,-80,2.2)}<path d="M-3 -71 q4 3 8 0" fill="none"/>')

def croc():
    return ('<path d="M-70 -10 q-20 4 -40 12 q30 -2 42 -2z" fill="#4E8B3A"/>'
            '<ellipse cx="-10" cy="-12" rx="58" ry="14" fill="#4E8B3A"/>'
            '<rect x="30" y="-20" width="58" height="13" rx="6" fill="#4E8B3A"/><path d="M34 -7 h52 l-4 6 l-6 -5 l-6 5 l-6 -5 l-6 5 l-6 -5 l-6 5 l-6 -5z" fill="#fff" stroke-width="1"/>'
            '<circle cx="34" cy="-28" r="7" fill="#4E8B3A"/>' + eye(35,-29,3) +
            '<path d="M-40 -24 l4 -8 l4 8 M-20 -25 l4 -8 l4 8 M0 -25 l4 -8 l4 8" fill="#3B6E2B"/>')

def crow():
    return ('<path d="M-14 -34 l-16 -8 l6 12z" fill="#222"/><path d="M-4 -12 v12 M6 -12 v12" fill="none"/>'
            '<ellipse cx="0" cy="-30" rx="15" ry="19" fill="#262626"/><ellipse cx="-4" cy="-28" rx="8" ry="13" fill="#3a3a3a"/>'
            '<circle cx="10" cy="-52" r="9" fill="#262626"/><path d="M17 -54 l14 3 l-14 5z" fill="#F0A020"/>' + eye(12,-54,2.4))

def cobra():
    return ('<ellipse cx="0" cy="-8" rx="30" ry="9" fill="#6B8E23"/><ellipse cx="0" cy="-22" rx="24" ry="8" fill="#7BA02D"/>'
            '<ellipse cx="0" cy="-34" rx="17" ry="7" fill="#6B8E23"/><path d="M-6 -36 q-6 -30 6 -50" fill="none" stroke="#2b2118" stroke-width="20"/>'
            '<path d="M-6 -36 q-6 -30 6 -50" fill="none" stroke="#7BA02D" stroke-width="17"/>'
            '<ellipse cx="4" cy="-78" rx="18" ry="16" fill="#7BA02D"/><path d="M-4 -74 q8 8 16 0" fill="none" stroke="#E7D7A1" stroke-width="4"/>'
            + eye(0,-82,2.6) + eye(10,-82,2.6) + '<path d="M20 -72 l12 0 m-4 -3 l4 3 l-4 3" stroke="#c00" fill="none" stroke-width="1.4"/>')

def jackal(col="#B87B3D", belly="#EBD3A7"):
    return (f'<path d="M-30 -38 q-24 4 -28 -18 q10 6 26 6z" fill="{col}"/>'
            f'<rect x="-22" y="-20" width="7" height="20" fill="{col}"/><rect x="16" y="-20" width="7" height="20" fill="{col}"/>'
            f'<ellipse cx="0" cy="-36" rx="30" ry="15" fill="{col}"/><ellipse cx="4" cy="-30" rx="18" ry="7" fill="{belly}"/>'
            f'<path d="M22 -46 l10 -22 l8 14z" fill="{col}"/><path d="M34 -46 l10 -20 l4 16z" fill="{col}"/>'
            f'<circle cx="34" cy="-44" r="12" fill="{col}"/><path d="M40 -42 l22 6 l-20 8z" fill="{belly}"/><circle cx="62" cy="-36" r="2.6" fill="#222"/>'
            + eye(36,-48,2.4))

def tortoise():
    return ('<rect x="-22" y="-10" width="10" height="10" rx="3" fill="#8DAA55"/><rect x="12" y="-10" width="10" height="10" rx="3" fill="#8DAA55"/>'
            '<path d="M-32 -8 q0 -40 32 -40 q32 0 32 40z" fill="#6B7A3A"/><path d="M-14 -8 l-6 -22 M6 -8 l0 -30 M22 -8 l8 -20 M-22 -26 h44" fill="none" stroke-width="1.2"/>'
            '<path d="M32 -16 q10 -2 14 -12 q4 -8 -4 -10 q-8 -2 -12 8z" fill="#8DAA55"/>' + eye(42,-32,2.2))

def swan(col="#FFFFFF", beak="#F08A24"):
    return (f'<path d="M-26 -22 q-14 -10 -12 -20 q14 6 24 8z" fill="{col}"/><ellipse cx="0" cy="-22" rx="28" ry="16" fill="{col}"/>'
            f'<path d="M18 -30 q16 -6 8 -30" fill="none" stroke="#2b2118" stroke-width="10"/><path d="M18 -30 q16 -6 8 -30" fill="none" stroke="{col}" stroke-width="7"/>'
            f'<circle cx="28" cy="-64" r="8" fill="{col}"/><path d="M34 -64 l14 3 l-14 4z" fill="{beak}"/>' + eye(29,-66,2)
            + '<path d="M-8 -8 v10 M6 -8 v10" stroke="#F08A24" fill="none"/>')

def deer(col="#C99A5B", horn="#6B4A2A"):
    return (f'<rect x="-26" y="-32" width="6" height="32" fill="{col}"/><rect x="-14" y="-32" width="6" height="32" fill="{col}"/>'
            f'<rect x="12" y="-32" width="6" height="32" fill="{col}"/><rect x="24" y="-32" width="6" height="32" fill="{col}"/>'
            f'<ellipse cx="0" cy="-46" rx="34" ry="16" fill="{col}"/><path d="M26 -52 l14 -30 l14 6 l-12 34z" fill="{col}"/>'
            f'<ellipse cx="52" cy="-82" rx="14" ry="10" fill="{col}"/><path d="M40 -90 q-6 -18 4 -26 M50 -90 q2 -16 12 -22" fill="none" stroke="{horn}" stroke-width="3"/>'
            + eye(54,-84,2.2) + '<circle cx="-10" cy="-50" r="2" fill="#fff" stroke="none"/><circle cx="6" cy="-42" r="2" fill="#fff" stroke="none"/><circle cx="-20" cy="-42" r="2" fill="#fff" stroke="none"/>')

def man(robe="#C0392B", cap="turban", skin="#C68E5E"):
    top = {"turban": '<ellipse cx="0" cy="-92" rx="15" ry="9" fill="#F3EAD2"/>',
           "crown": '<path d="M-13 -92 l4 -12 l5 8 l4 -12 l4 12 l5 -8 l4 12z" fill="#F2C230"/>',
           "hair": '<path d="M-13 -88 q13 -20 26 0z" fill="#2b2118"/>'}[cap]
    return (f'<path d="M-18 0 l6 -70 h24 l6 70z" fill="{robe}"/><path d="M-14 -66 l-16 26 M14 -66 l16 26" fill="none" stroke-width="6" stroke="{skin}"/>'
            f'<circle cx="0" cy="-82" r="13" fill="{skin}"/>{top}{eye(-4,-84,2)}{eye(6,-84,2)}<path d="M-3 -76 q4 3 8 0" fill="none" stroke-width="1.2"/>')

def mongoose():
    return ('<path d="M-30 -18 q-22 -4 -26 -20" fill="none" stroke-width="8" stroke="#8A6D4B"/><ellipse cx="0" cy="-16" rx="32" ry="12" fill="#8A6D4B"/>'
            '<rect x="-16" y="-8" width="6" height="8" fill="#8A6D4B"/><rect x="16" y="-8" width="6" height="8" fill="#8A6D4B"/>'
            '<circle cx="32" cy="-22" r="10" fill="#8A6D4B"/><path d="M40 -22 l12 4 l-12 4z" fill="#D8B48A"/>' + eye(34,-26,2))

def crab():
    return ('<ellipse cx="0" cy="-16" rx="26" ry="14" fill="#D9482B"/><path d="M-22 -12 l-14 6 M-20 -6 l-14 8 M22 -12 l14 6 M20 -6 l14 8" fill="none"/>'
            '<path d="M-20 -24 q-14 -12 -6 -26 q10 4 6 12z M20 -24 q14 -12 6 -26 q-10 4 -6 12z" fill="#D9482B"/>'
            '<path d="M-8 -28 v-8 M8 -28 v-8" fill="none"/><circle cx="-8" cy="-38" r="3" fill="#fff"/><circle cx="8" cy="-38" r="3" fill="#fff"/>')

def crane():
    return ('<path d="M-6 -30 v-40 M6 -30 v-40" fill="none" stroke="#E7A93B" stroke-width="3"/><ellipse cx="0" cy="-30" rx="24" ry="14" fill="#F2F2EE"/>'
            '<path d="M-20 -32 l-18 -6 l8 12z" fill="#F2F2EE"/><path d="M16 -36 q14 -4 8 -34" fill="none" stroke="#2b2118" stroke-width="8"/><path d="M16 -36 q14 -4 8 -34" fill="none" stroke="#F2F2EE" stroke-width="5.5"/>'
            '<circle cx="26" cy="-72" r="7" fill="#F2F2EE"/><path d="M32 -72 l22 2 l-22 4z" fill="#F0A020"/>' + eye(27,-74,1.8))

def fish():
    return ('<ellipse cx="0" cy="-8" rx="16" ry="8" fill="#5DA9E9"/><path d="M-14 -8 l-12 -8 v16z" fill="#5DA9E9"/>' + eye(8,-10,2))

def drum(torn=False):
    hole = ('<path d="M-16 -48 l7 -8 l6 7 l7 -9 l6 9 l7 -5 l-2 9 l-10 5 l-9 -3 l-8 5z" fill="#2b1a0a" stroke-width="1"/>' if torn else '')
    return ('<ellipse cx="0" cy="-8" rx="26" ry="9" fill="#7A4A25"/><path d="M-26 -8 v-40 a26 9 0 0 0 52 0 v40 a26 9 0 0 1 -52 0z" fill="#A9652F"/>'
            '<ellipse cx="0" cy="-48" rx="26" ry="9" fill="#F2DDB0"/><path d="M-26 -30 h52" fill="none" stroke="#7A4A25"/>' + hole)

def camel(body="#C99B5C", dark="#A67B3F"):
    return (f'<rect x="-28" y="-46" width="8" height="46" rx="3" fill="{dark}"/><rect x="-16" y="-46" width="8" height="46" rx="3" fill="{body}"/>'
            f'<rect x="10" y="-46" width="8" height="46" rx="3" fill="{dark}"/><rect x="22" y="-46" width="8" height="46" rx="3" fill="{body}"/>'
            f'<path d="M-34 -62 q-14 4 -12 24" fill="none" stroke-width="3"/>'
            f'<ellipse cx="-2" cy="-62" rx="38" ry="21" fill="{body}"/><ellipse cx="-8" cy="-88" rx="15" ry="17" fill="{body}"/>'
            f'<path d="M26 -70 q22 -6 24 -40" fill="none" stroke-width="15"/><path d="M26 -70 q22 -6 24 -40" fill="none" stroke="{body}" stroke-width="12"/>'
            f'<ellipse cx="58" cy="-118" rx="15" ry="9" fill="{body}"/><path d="M68 -116 q10 4 6 10 q-8 2 -12 -4z" fill="{dark}"/>'
            f'<path d="M52 -128 l-3 -9 l8 6z" fill="{body}"/>{eye(58,-121,2.4)}<path d="M66 -113 q4 2 8 0" fill="none" stroke-width="1.2"/>')

def baby():
    return ('<rect x="-22" y="-14" width="44" height="14" rx="7" fill="#7FB3D5"/><circle cx="-8" cy="-22" r="10" fill="#E9B98C"/>' + eye(-11,-23,1.8) + eye(-4,-23,1.8))

def blood(): return '<circle cx="0" cy="0" r="1" fill="none"/>'

def flame():
    return ('<path d="M-20 0 q-4 -30 8 -44 q2 14 10 18 q0 -20 12 -30 q10 20 4 56z" fill="#F57C00"/><path d="M-8 0 q0 -20 6 -28 q10 14 6 28z" fill="#FFD54F" stroke="none"/>')

def stick():
    return '<path d="M-60 -60 h120" stroke="#7A4A25" stroke-width="5" fill="none"/>'

def necklace():
    return '<path d="M-14 -14 q14 22 28 0" fill="none" stroke="#F2C230" stroke-width="3"/><circle cx="0" cy="0" r="4" fill="#E53935"/>'

def feather():
    return '<path d="M0 0 q-14 -6 -6 -22 q14 8 6 22z" fill="#F2C230"/>'

def tree(x, y, s=1, fruit=False):
    f = ''.join(f'<circle cx="{x+dx*s}" cy="{y-100*s+dy*s}" r="{3.6*s}" fill="#7B3F9E" stroke="#3b1d4d" stroke-width=".8"/>' for dx, dy in ((-16, 4), (14, -6), (2, 16), (-4, -14))) if fruit else ''
    return (f'<g filter="url(#lit)" stroke="#2b2118" stroke-width="1.3" stroke-linejoin="round">'
            f'<path d="M{x-8*s} {y} q2 -40 -1 -72 h{16*s} q-3 32 1 72z" fill="url(#trunk)"/>'
            f'<circle cx="{x}" cy="{y-100*s}" r="{40*s}" fill="#2F7A36"/><circle cx="{x-26*s}" cy="{y-82*s}" r="{27*s}" fill="#3B8F3F"/>'
            f'<circle cx="{x+28*s}" cy="{y-84*s}" r="{27*s}" fill="#3B8F3F"/><circle cx="{x-8*s}" cy="{y-116*s}" r="{26*s}" fill="#4DA84B"/>'
            f'<circle cx="{x+16*s}" cy="{y-108*s}" r="{18*s}" fill="#5DB859"/>{f}</g>')

CHARS = dict(camel=camel, lion=lion, hare=hare, monkey=monkey, croc=croc, crow=crow, cobra=cobra, jackal=jackal, tortoise=tortoise, swan=swan,
             deer=deer, man=man, mongoose=mongoose, crab=crab, crane=crane, fish=fish, drum=drum, baby=baby, flame=flame,
             stick=stick, necklace=necklace, feather=feather)

# Shared filters and gradients. Put COMIC_DEFS once in the page; every panel refers to it by id.
COMIC_DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<filter id="lit" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G" result="w"/>
  <feGaussianBlur in="w" stdDeviation="2.4" result="b"/>
  <feDiffuseLighting in="b" surfaceScale="3.2" diffuseConstant="1.05" lighting-color="#fff8ec" result="d"><feDistantLight azimuth="235" elevation="52"/></feDiffuseLighting>
  <feComposite in="w" in2="d" operator="arithmetic" k1="1.32" k2="0" k3="0" k4="0" result="m"/>
  <feComposite in="m" in2="w" operator="in"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .2  0 0 0 .55 0"/></filter>
<linearGradient id="trunk" x1="0" x2="1"><stop offset="0" stop-color="#5A3A1E"/><stop offset=".5" stop-color="#8A5A31"/><stop offset="1" stop-color="#5A3A1E"/></linearGradient>
<linearGradient id="sky-day" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6FB6E3"/><stop offset=".7" stop-color="#CDEBF6"/><stop offset="1" stop-color="#F6F1D3"/></linearGradient>
<linearGradient id="sky-warm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0A86A"/><stop offset=".65" stop-color="#F8D9A0"/><stop offset="1" stop-color="#FCEFC8"/></linearGradient>
<linearGradient id="sky-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B1230"/><stop offset=".7" stop-color="#1B2C57"/><stop offset="1" stop-color="#2B3F6E"/></linearGradient>
<linearGradient id="ground-grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#86BF5C"/><stop offset="1" stop-color="#4C8534"/></linearGradient>
<linearGradient id="ground-dust" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E2C494"/><stop offset="1" stop-color="#B8925C"/></linearGradient>
<linearGradient id="ground-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C5238"/><stop offset="1" stop-color="#16301F"/></linearGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6CC0E8"/><stop offset="1" stop-color="#2F7DB5"/></linearGradient>
<radialGradient id="sun"><stop offset="0" stop-color="#FFF6C2"/><stop offset=".35" stop-color="#FFD54F"/><stop offset="1" stop-color="#FFD54F" stop-opacity="0"/></radialGradient>
<radialGradient id="moonglow"><stop offset="0" stop-color="#FFF8DC"/><stop offset=".4" stop-color="#F7EFC2"/><stop offset="1" stop-color="#F7EFC2" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#2b1a0a" stop-opacity="0"/><stop offset="1" stop-color="#2b1a0a" stop-opacity=".38"/></radialGradient>
<linearGradient id="rays" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3B0" stop-opacity=".55"/><stop offset="1" stop-color="#FFF3B0" stop-opacity="0"/></linearGradient>
</defs></svg>"""

def hills(kind):
    col1, col2 = ("#1D2D4A", "#16243C") if kind in ("night", "moon") else (("#A9C79A", "#8DB37D") if kind != "palace" else ("#D7B679", "#C4A05F"))
    return (f'<path d="M0 205 C40 170 80 178 120 192 C170 208 210 165 260 175 C310 185 350 168 400 190 V240 H0z" fill="{col1}"/>'
            f'<path d="M0 220 C50 200 100 210 150 214 C220 222 280 196 340 206 C370 212 390 208 400 210 V250 H0z" fill="{col2}"/>')

def grass(kind, ground_y=225):
    if kind in ("river", "pond", "palace"):
        return ''
    col = "#3F7A2C" if kind not in ("night", "moon") else "#22422C"
    o = []
    for i in range(0, 400, 19):
        h = 7 + (i * 7) % 6
        o.append(f'<path d="M{i} {ground_y+2+(i*3)%9} q2 -{h} 4 0 q2 -{h+2} 4 0 q2 -{h} 4 0" fill="none" stroke="{col}" stroke-width="1.6" stroke-linecap="round"/>')
    return ''.join(o)

def bg(kind):
    night = kind in ("night", "moon")
    sky = "url(#sky-night)" if night else ("url(#sky-warm)" if kind in ("fire", "village") else "url(#sky-day)")
    if kind == "palace":
        sky = "#F3E2B4"
    o = [f'<rect width="400" height="300" fill="{sky}"/>']
    if night:
        o.append('<g fill="#fff">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" opacity=".9"/>' for x, y, r in ((30,30,1.6),(90,60,1.2),(160,24,1.8),(240,50,1.3),(310,28,1.6),(360,70,1.2),(60,100,1.4),(210,90,1.1),(340,120,1.5),(120,120,1.1))) + '</g>')
        r = 44 if kind == "moon" else 28
        o.append(f'<circle cx="330" cy="52" r="{r*1.8:.0f}" fill="url(#moonglow)" opacity=".7"/><circle cx="330" cy="52" r="{r}" fill="#F7EFC2"/>')
        if kind == "moon":
            o.append('<g fill="#E1D59E" opacity=".8"><circle cx="318" cy="44" r="7"/><circle cx="342" cy="66" r="9"/><circle cx="336" cy="38" r="4"/></g>')
    elif kind != "palace":
        o.append('<circle cx="350" cy="44" r="66" fill="url(#sun)"/><circle cx="350" cy="44" r="19" fill="#FFE47A"/>')
        o.append('<path d="M350 44 L60 300 L170 300z M350 44 L210 300 L300 300z" fill="url(#rays)" opacity=".5"/>')
        o.append('<g fill="#fff" opacity=".85"><ellipse cx="70" cy="50" rx="34" ry="9"/><ellipse cx="94" cy="44" rx="24" ry="9"/><ellipse cx="260" cy="30" rx="28" ry="7"/></g>')
    if kind == "palace":
        o.append('<rect y="210" width="400" height="90" fill="#B5651D"/><rect y="210" width="400" height="14" fill="#C97A32"/>' + ''.join(f'<g stroke="#2b2118" stroke-width="1.5"><rect x="{x}" y="20" width="24" height="200" fill="#F5E8C1"/><rect x="{x-4}" y="14" width="32" height="10" fill="#E2CD98"/><rect x="{x-4}" y="208" width="32" height="10" fill="#E2CD98"/></g>' for x in (20, 356)))
        o.append('<g stroke="#2b2118" stroke-width="1.5"><rect x="150" y="70" width="100" height="80" fill="#7FB3D5"/><path d="M150 70 q50 -40 100 0" fill="#E2CD98"/></g>')
        return ''.join(o)
    o.append(hills(kind))
    ground = "url(#ground-night)" if night else ("url(#ground-dust)" if kind in ("village", "fire") else "url(#ground-grass)")
    o.append(f'<rect y="225" width="400" height="75" fill="{ground}"/>')
    o.append(grass(kind))
    if kind in ("river", "pond"):
        o.append('<rect y="200" width="400" height="60" fill="url(#water)"/>' + ''.join(f'<path d="M{x} {y} q12 -5 24 0 t24 0" fill="none" stroke="#fff" stroke-width="1.8" opacity=".6" stroke-linecap="round"/>' for x, y in ((10,214),(150,222),(270,212),(60,240),(200,246),(330,236))))
    if kind == "village":
        o.append('<g filter="url(#lit)" stroke="#2b2118" stroke-width="1.5" stroke-linejoin="round"><rect x="40" y="150" width="90" height="75" fill="#E9C9A0"/><path d="M28 152 l57 -44 l57 44z" fill="#B5651D"/><rect x="72" y="182" width="26" height="43" fill="#7A4E2A"/><rect x="52" y="164" width="14" height="14" fill="#7FB3D5"/><rect x="104" y="164" width="14" height="14" fill="#7FB3D5"/></g>')
    if kind == "well":
        o.append('<g stroke="#2b2118" stroke-width="1.5"><ellipse cx="200" cy="232" rx="46" ry="14" fill="#8A8A88"/><ellipse cx="200" cy="230" rx="34" ry="9" fill="#2B4B63"/><path d="M168 232 v14 q32 10 64 0 v-14" fill="#9C9A96"/></g>')
    if kind in ("forest", "night", "moon", "well", "fire"):
        o.append(tree(30, 235, 1.0) + tree(372, 240, 0.9))
    return ''.join(o)

def panel(scene, uid=""):
    parts = [bg(scene["bg"])]
    for item in scene.get("items", []):
        if item[0] == "tree":
            _, x, y, s, fruit = item
            parts.append(tree(x, y, s, fruit)); continue
        if item[0] == "text":
            _, x, y, t = item
            parts.append(f'<text x="{x}" y="{y}" font-family="Noto Sans Kannada, Arial Black, sans-serif" font-weight="900" font-size="28" fill="#D32F2F" stroke="#fff" stroke-width="3" paint-order="stroke" transform="rotate(-6 {x} {y})">{E(t)}</text>'); continue
        if item[0] == "water":
            _, y = item
            parts.append(f'<rect y="{y}" width="400" height="{300-y}" fill="url(#water)" opacity=".94"/>' + ''.join(f'<path d="M{x} {y+10+k*9} q12 -5 24 0 t24 0" fill="none" stroke="#fff" stroke-width="1.8" opacity=".55" stroke-linecap="round"/>' for k, x in enumerate((10, 120, 250, 60, 190, 320)))); continue
        name, x, y, s, flip = item[:5]
        kw = item[5] if len(item) > 5 else {}
        parts.append(f'<ellipse cx="{x}" cy="{y+2}" rx="{34*s:.0f}" ry="{7*s:.0f}" fill="#1b2a10" opacity=".28"/>')
        parts.append(f'<g filter="url(#lit)">{g(x, y, s, flip, CHARS[name](**kw))}</g>')
    parts.append('<rect width="400" height="300" fill="url(#vig)"/><rect width="400" height="300" filter="url(#grain)" opacity=".22" style="mix-blend-mode:multiply"/>')
    return f'<svg viewBox="0 0 400 300" role="img" aria-label="{E(scene["alt"])}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'

# ---------------------------------------------------------------- stories
# Each panel: dict(bg, items, alt, cap). Items: (char, x, ground_y, scale, flip[, kwargs]).
PANCHATANTRA = [
 dict(title="The Lion and the Clever Hare", moral="Cleverness can do what strength cannot.", plate=None, panels=[
  dict(bg="forest", alt="A big lion roars while animals hide", cap="A greedy lion hunted every animal in the forest, day after day. The animals feared they would all be gone.",
       items=[("lion", 150, 245, 1.5, False), ("hare", 320, 250, .8, True), ("text", 40, 60, "ROAR!")]),
  dict(bg="forest", alt="Animals bow before the lion", cap="They made a deal. One animal would go to the lion each day, so he would not have to hunt.",
       items=[("lion", 120, 245, 1.4, False), ("deer", 290, 250, .8, True), ("hare", 360, 250, .6, True)]),
  dict(bg="well", alt="The hare points into a well", cap="One day it was the little hare's turn. He walked slowly, then told the hungry lion that another lion had stopped him on the way.",
       items=[("hare", 150, 250, 1.2, False), ("lion", 340, 245, 1.2, True)]),
  dict(bg="well", alt="The lion looks down at his reflection in the well", cap="The hare led him to a deep well. The lion saw his own reflection, roared at the 'rival', and leapt in. The forest was safe again.",
       items=[("lion", 120, 240, 1.4, False), ("hare", 310, 250, 1.0, True), ("text", 220, 70, "SPLASH!")]),
 ]),
 dict(title="The Monkey and the Crocodile", moral="Keep a calm mind in danger. A quick thought can save you.", plate=None, panels=[
  dict(bg="river", alt="A monkey on a tree drops fruit to a crocodile", cap="A monkey lived in a jamun tree by the river. He shared his sweet fruit with a crocodile, and they became friends.",
       items=[("tree", 90, 235, 1.3, True), ("monkey", 150, 190, .9, False), ("croc", 290, 246, .9, True)]),
  dict(bg="river", alt="The crocodile with the monkey on his back in the river", cap="The crocodile's wife wanted to eat the monkey's heart. So the crocodile offered the monkey a ride across the river.",
       items=[("water", 190), ("croc", 200, 240, 1.1, False), ("monkey", 195, 180, .7, False)]),
  dict(bg="river", alt="The monkey speaks while the crocodile listens", cap="In the middle of the river, the crocodile told the truth. The monkey stayed calm. 'My heart is on the tree! Take me back for it.'",
       items=[("water", 190), ("croc", 200, 240, 1.1, False), ("monkey", 195, 180, .7, False), ("text", 250, 70, "OH!")]),
  dict(bg="river", alt="The monkey back on the tree", cap="The crocodile swam back. The monkey leapt into the branches and called down, 'A heart never stays outside the body. Go home, foolish friend.'",
       items=[("tree", 100, 235, 1.3, True), ("monkey", 140, 178, 1.0, False), ("croc", 290, 246, .9, True)]),
 ]),
 dict(title="The Blue Jackal", moral="Borrowed glory does not last. Be yourself.", plate=None, panels=[
  dict(bg="village", alt="A jackal near a village", cap="A hungry jackal wandered into a village and was chased by dogs. He ran, and fell into a huge vat of blue dye.",
       items=[("jackal", 250, 245, 1.2, True), ("text", 220, 70, "SPLASH!")]),
  dict(bg="forest", alt="A blue jackal stands proudly", cap="He climbed out blue from nose to tail. Back in the forest, the animals had never seen such a creature.",
       items=[("jackal", 210, 245, 1.5, False, dict(col="#3B62C9", belly="#9FB6F0")), ("deer", 340, 250, .7, True), ("hare", 60, 250, .6, False)]),
  dict(bg="forest", alt="Animals bow before the blue jackal", cap="'I am a king sent by the gods,' he said. Lions, deer and hares bowed. He stopped speaking to the other jackals, who felt ashamed.",
       items=[("jackal", 210, 245, 1.5, False, dict(col="#3B62C9", belly="#9FB6F0")), ("lion", 340, 245, .8, True), ("hare", 70, 250, .7, False)]),
  dict(bg="night", alt="The blue jackal howls with other jackals", cap="One night a pack of jackals howled far away. Without thinking, the 'king' howled back. The animals knew him at once, and he ran for his life.",
       items=[("jackal", 210, 245, 1.5, False, dict(col="#3B62C9", belly="#9FB6F0")), ("text", 230, 70, "AWOO!")]),
 ]),
 dict(title="The Crows and the Cobra", moral="Where force fails, a clever plan works.", plate=None, panels=[
  dict(bg="forest", alt="A cobra near a tree with a crow's nest", cap="A pair of crows lived in a tree. A cobra in its roots ate their eggs, year after year.",
       items=[("tree", 100, 235, 1.4, False), ("cobra", 190, 245, 1.0, False), ("crow", 100, 120, .6, False)]),
  dict(bg="palace", alt="A crow takes a necklace", cap="The sad crows flew to a palace garden. One crow picked up a queen's shining necklace in her beak.",
       items=[("crow", 150, 245, 1.3, False), ("necklace", 200, 230, 1.0, False), ("man", 320, 250, .9, True, dict(robe="#8E44AD", cap="crown"))]),
  dict(bg="forest", alt="A crow drops a necklace near the snake's hole", cap="Guards followed the crow. She dropped the necklace right beside the cobra's hole in the roots.",
       items=[("tree", 100, 235, 1.4, False), ("necklace", 130, 245, 1.1, False), ("crow", 190, 150, .7, False), ("man", 320, 250, .9, True, dict(robe="#2E86C1", cap="turban"))]),
  dict(bg="forest", alt="Guards stand near the empty hole", cap="When the cobra came out, the guards struck it down and took the necklace. The crows lived safely, and hatched their eggs in peace.",
       items=[("tree", 100, 235, 1.4, False), ("crow", 130, 150, .7, False), ("crow", 175, 150, .6, True), ("man", 320, 250, .9, True, dict(robe="#2E86C1", cap="turban"))]),
 ]),
 dict(title="The Brahmin and the Mongoose", moral="Never act in anger before you know the truth.", plate=None, panels=[
  dict(bg="village", alt="A pet mongoose beside a baby", cap="A family kept a pet mongoose, who loved the baby of the house like a brother.",
       items=[("baby", 250, 245, 1.2, False), ("mongoose", 170, 246, 1.1, False)]),
  dict(bg="village", alt="A man leaves for the market", cap="One day the mother went to fetch water and the father to the market. The mongoose was left to watch the baby.",
       items=[("man", 110, 245, 1.2, False, dict(robe="#D68910", cap="turban")), ("baby", 290, 245, 1.1, False), ("mongoose", 230, 246, 1.0, False)]),
  dict(bg="village", alt="The mongoose with blood on its mouth meets the father", cap="A snake crept toward the baby, and the mongoose killed it. When the mother came back she saw blood on his mouth, and struck out in fear.",
       items=[("cobra", 300, 245, .8, True), ("mongoose", 190, 246, 1.1, False), ("man", 100, 245, 1.2, False, dict(robe="#D68910", cap="turban"))]),
  dict(bg="village", alt="A sad family and the dead snake", cap="Then she saw the dead snake, and the baby, safe and asleep. She wept for the loyal mongoose. Too late, she understood.",
       items=[("man", 120, 245, 1.2, False, dict(robe="#D68910", cap="turban")), ("baby", 280, 245, 1.1, False), ("cobra", 340, 245, .5, True)]),
 ]),
 dict(title="The Jackal and the Drum", moral="A loud sound does not mean there is much inside.", plate=None, panels=[
  dict(bg="night", alt="A hungry jackal listens", cap="A hungry jackal wandered near an old battlefield and heard a great booming sound. 'Something huge is here,' he thought.",
       items=[("jackal", 150, 245, 1.2, False), ("text", 240, 80, "BOOM!")]),
  dict(bg="forest", alt="A jackal hears a drum among trees", cap="He crept closer, trembling. The sound came again and again, louder than thunder.",
       items=[("jackal", 110, 246, 1.0, False), ("tree", 350, 240, 1.1, False), ("drum", 262, 246, .8, False), ("text", 200, 62, "BOOM!")]),
  dict(bg="forest", alt="A jackal tears open the drum", cap="It was a drum. Branches blew against its skin each time the wind rose. The jackal tore it open, hoping to find meat.",
       items=[("drum", 250, 246, 1.5, False, dict(torn=True)), ("jackal", 120, 246, 1.5, False), ("text", 150, 66, "RIP!")]),
  dict(bg="forest", alt="A jackal looks inside an empty drum", cap="The drum was hollow. 'So much noise, and nothing inside,' he sighed. And he learned to look before he ran.",
       items=[("drum", 290, 246, 1.4, False, dict(torn=True)), ("jackal", 130, 246, 1.3, False), ("text", 60, 62, "Nothing!")]),
 ]),
 dict(title="The Lion's Courtiers and the Camel", moral="Beware of those who flatter you into harming others.", plate="camel", panels=[
  dict(bg="forest", alt="A camel meets a lion", cap="A camel lost his caravan and wandered into the forest. The lion took him in as a friend.",
       items=[("lion", 110, 246, 1.3, False), ("camel", 300, 246, 1.05, True)]),
  dict(bg="forest", alt="A hungry lion and his courtiers", cap="One hard season, the lion could not hunt. His courtiers, a crow, a jackal and a wolf, were hungry too.",
       items=[("lion", 100, 246, 1.25, False), ("jackal", 225, 246, .7, True), ("jackal", 280, 246, .75, True, dict(col="#7F848B", belly="#D5D8DC")), ("crow", 345, 246, .8, True)]),
  dict(bg="forest", alt="The courtiers plot while the camel bows", cap="They plotted. Each offered himself as a meal, and the lion refused each in turn. Then the camel, trusting, offered too.",
       items=[("lion", 95, 246, 1.2, False), ("camel", 250, 246, .95, True), ("jackal", 350, 246, .7, True), ("text", 190, 62, "PLEASE!")]),
  dict(bg="forest", alt="The courtiers turn on the camel", cap="'Yes!' cried the courtiers, and the trap closed. The camel learned too late: never trust those who agree only to please.",
       items=[("camel", 110, 246, 1.0, False), ("lion", 250, 246, 1.05, True), ("jackal", 320, 246, .65, True, dict(col="#7F848B", belly="#D5D8DC")), ("crow", 365, 246, .7, True)]),
 ]),
]

JATAKA = [
 dict(title="The Monkey King's Bridge", moral="A true leader thinks of others before himself.", plate=None, panels=[
  dict(bg="river", alt="Monkeys eat mangoes beside a river", cap="A monkey king led eighty thousand monkeys in a great mango tree beside the river. Everyone ate happily.",
       items=[("tree", 90, 235, 1.4, True), ("monkey", 150, 190, .9, False), ("monkey", 230, 245, .8, True)]),
  dict(bg="river", alt="Soldiers shoot arrows at monkeys", cap="A king of men heard about the tree and sent his archers. Monkeys leapt in terror. The only way out was across the river.",
       items=[("man", 330, 245, 1.0, True, dict(robe="#8E44AD", cap="crown")), ("monkey", 150, 245, .9, False)]),
  dict(bg="river", alt="The monkey king stretches across the river", cap="The monkey king stretched his body from the tree to the far bank and made a living bridge. The monkeys crossed over his back.",
       items=[("water", 200), ("monkey", 120, 190, 1.2, False), ("monkey", 260, 190, .6, True)]),
  dict(bg="river", alt="The king of men bows to the monkey king", cap="The king of men watched, moved. He put down his bow and cared for the monkey king. He said, 'You are the true king of this forest.'",
       items=[("monkey", 130, 245, 1.2, False), ("man", 290, 245, 1.2, True, dict(robe="#8E44AD", cap="crown"))]),
 ]),
 dict(title="The Banyan Deer", moral="Kindness can open even a hard heart.", plate=None, panels=[
  dict(bg="forest", alt="A golden deer among trees", cap="Two herds of deer lived in a forest, each with a king. The Banyan Deer was golden, like the sun on the leaves.",
       items=[("deer", 200, 246, 1.3, False, dict(col="#E4B93A", horn="#8A5A2B")), ("deer", 320, 250, .8, True)]),
  dict(bg="forest", alt="A king with a bow", cap="The king of the land loved hunting deer, and the deer were dying in great numbers. The two deer kings made a plan.",
       items=[("man", 330, 245, 1.1, True, dict(robe="#8E44AD", cap="crown")), ("deer", 130, 246, 1.0, False, dict(col="#E4B93A", horn="#8A5A2B"))]),
  dict(bg="forest", alt="A golden deer stands before the king", cap="One deer would go to the king each day. One day the lot fell on a mother deer with a fawn. The Banyan Deer said, 'I will go in her place.'",
       items=[("deer", 150, 246, 1.3, False, dict(col="#E4B93A", horn="#8A5A2B")), ("man", 320, 245, 1.1, True, dict(robe="#8E44AD", cap="crown"))]),
  dict(bg="palace", alt="The king lowers his bow", cap="The king was astonished that a deer would die for another. He lowered his bow, and spared every deer in the land.",
       items=[("deer", 130, 246, 1.2, False, dict(col="#E4B93A", horn="#8A5A2B")), ("man", 300, 245, 1.2, True, dict(robe="#8E44AD", cap="crown"))]),
 ]),
 dict(title="The Hare in the Moon", moral="The greatest gift is the one you give freely.", plate=None, panels=[
  dict(bg="night", alt="A hare, a monkey and a jackal under a tree", cap="A hare, a monkey and a jackal lived in a forest and kept a fast on the full moon night. They promised to give food to any visitor.",
       items=[("tree", 60, 235, 1.0, False), ("hare", 150, 250, 1.0, False), ("monkey", 230, 245, .8, False), ("jackal", 320, 246, .8, True)]),
  dict(bg="night", alt="A beggar visits", cap="A hungry beggar came. The monkey brought fruit, the jackal brought fish. The hare had only grass, which no traveller could eat.",
       items=[("man", 330, 245, 1.1, True, dict(robe="#D68910", cap="hair")), ("hare", 150, 250, 1.1, False), ("monkey", 230, 245, .7, False)]),
  dict(bg="fire", alt="The hare stands before a fire", cap="'I have nothing to give but myself,' said the hare. 'Light a fire.' The beggar lit a fire and the hare, without a moment's fear, leapt in.",
       items=[("flame", 260, 245, 1.5, False), ("hare", 130, 250, 1.1, False), ("text", 220, 60, "WHOOSH!")]),
  dict(bg="moon", alt="A hare on the face of the moon", cap="The flames did not burn him. The beggar was the king of the gods in disguise. To honour the hare, he drew the hare's shape on the moon, for all time.",
       items=[("hare", 200, 250, 1.1, False)]),
 ]),
 dict(title="The Golden Swan", moral="Greed loses everything.", plate=None, panels=[
  dict(bg="pond", alt="A golden swan by a pond", cap="A poor woman's husband died and was reborn as a golden swan. He remembered his family, and flew to their home.",
       items=[("water", 205), ("swan", 210, 232, 1.5, False, dict(col="#F2C230"))]),
  dict(bg="village", alt="A swan gives a feather to a family", cap="'I will give you one golden feather now and then,' he said. The family sold the feathers and lived in comfort.",
       items=[("swan", 240, 246, 1.5, False, dict(col="#F2C230")), ("man", 110, 245, 1.1, False, dict(robe="#C0392B", cap="hair")), ("feather", 175, 210, 1.5, False)]),
  dict(bg="village", alt="The mother grabs the swan", cap="But the mother grew greedy. 'Next time he comes, I will take all the feathers at once,' she said. And she did.",
       items=[("swan", 230, 246, 1.5, False, dict(col="#F2C230")), ("man", 110, 245, 1.2, False, dict(robe="#C0392B", cap="hair")), ("text", 180, 60, "GRAB!")]),
  dict(bg="village", alt="A plain white swan and plain feathers", cap="The feathers turned plain white in her hands. The swan grew back only white feathers and flew away, never to return.",
       items=[("swan", 240, 246, 1.5, False, dict(col="#FFFFFF")), ("man", 110, 245, 1.2, False, dict(robe="#C0392B", cap="hair"))]),
 ]),
 dict(title="The Talkative Tortoise", moral="Think before you speak.", plate="tortoise", panels=[
  dict(bg="pond", alt="A tortoise talks to two geese by a lake", cap="A tortoise lived in a pond with two geese friends. He talked and talked, and rarely listened.",
       items=[("water", 205), ("tortoise", 130, 232, 1.5, False), ("swan", 290, 246, 1.0, True)]),
  dict(bg="forest", alt="Geese hold a stick with a tortoise", cap="When the pond began to dry, the geese made a plan. They held a stick in their beaks, the tortoise bit the middle. 'Do not open your mouth.'",
       items=[("stick", 200, 180, 1.0, False), ("swan", 130, 246, 1.0, False), ("swan", 280, 246, 1.0, True), ("tortoise", 200, 176, .6, False)]),
  dict(bg="village", alt="Children point up at the flying tortoise", cap="Over a village, children pointed and laughed at the strange sight. The tortoise grew angry, and wanted to answer them.",
       items=[("stick", 200, 100, 1.0, False), ("tortoise", 200, 96, .6, False), ("man", 100, 245, .9, False, dict(robe="#2E86C1", cap="hair")), ("man", 300, 245, .9, True, dict(robe="#27AE60", cap="hair"))]),
  dict(bg="village", alt="The tortoise falls", cap="He opened his mouth to speak, and fell from the sky. A wise tortoise would have kept quiet.",
       items=[("tortoise", 200, 245, 1.3, False), ("text", 130, 70, "OOPS!")]),
 ]),
 dict(title="The Crane and the Crab", moral="Cheats are caught by their own cunning.", plate=None, panels=[
  dict(bg="pond", alt="A crane by a pond with fish", cap="An old crane could no longer catch fish, and thought of a trick. He stood at the pond looking sad.",
       items=[("water", 205), ("crane", 110, 235, 1.4, False), ("fish", 250, 250, 1.4, False), ("crab", 320, 250, .9, True)]),
  dict(bg="pond", alt="A crane talks to a fish", cap="'A great drought is coming,' he said to the fish. 'I know a deep lake. I will carry you there, one by one.'",
       items=[("water", 205), ("crane", 110, 235, 1.4, False), ("fish", 250, 250, 1.4, False)]),
  dict(bg="forest", alt="A crane eats a fish under a tree", cap="But he carried each fish to a rock and ate it. The bones piled up. The last one to ask was a crab.",
       items=[("crane", 130, 245, 1.4, False), ("crab", 310, 250, 1.0, True)]),
  dict(bg="forest", alt="The crab holds the crane by the neck", cap="The crab saw the fish bones and understood. He gripped the crane's neck with his claws until the cheat could do no more harm.",
       items=[("crane", 170, 245, 1.4, False), ("crab", 240, 200, .9, False)]),
 ]),
]


# the paper is printed in Kannada: swap in the Kannada text (comics_kn.py keeps the translations)
import comics_kn
comics_kn.localise(PANCHATANTRA, JATAKA)
