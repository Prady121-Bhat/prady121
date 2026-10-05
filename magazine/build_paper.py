#!/usr/bin/env python3
"""ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ (Kullangal Vaarte): the whole paper is printed in Kannada. Built from data files.

Usage: build_paper.py [YYYY-MM-DD] [--private FILE] [--public FILE]

Writes two editions from the same data: the private one (adds the Desk and Classifieds pages from
content/private.json) and the shareable one. Defaults: kullangal-vaarte.html and public-edition.html.
The shareable edition never contains anything from content/private.json (checked before writing).
"""
import datetime, html, json, os, re, sys, base64

import astro, comics, photos, puzzles, weather
import build_notices as bn

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCH = datetime.date(2026, 9, 30)
PUBLIC_URL = "https://claude.ai/artifact/7voAxG4qkUxsec11FZmraw"
E = html.escape


def load(name):
    with open(os.path.join(HERE, "content", name), encoding="utf-8") as f:
        return json.load(f)


def rd(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


KN_DIGITS = str.maketrans("0123456789", "೦೧೨೩೪೫೬೭೮೯")
KN_DAYS = ["ಸೋಮವಾರ", "ಮಂಗಳವಾರ", "ಬುಧವಾರ", "ಗುರುವಾರ", "ಶುಕ್ರವಾರ", "ಶನಿವಾರ", "ಭಾನುವಾರ"]
KN_DAYS_SHORT = ["ಸೋಮ", "ಮಂಗಳ", "ಬುಧ", "ಗುರು", "ಶುಕ್ರ", "ಶನಿ", "ಭಾನು"]
KN_MONTHS = ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"]
LEVELS = {"Easy": "ಸುಲಭ", "Medium": "ಮಧ್ಯಮ", "Hard": "ಕಠಿಣ"}


def kd(x):
    """Kannada digits."""
    return str(x).translate(KN_DIGITS)


PAGE_COLOURS = dict(front=("#c4361f", "#fff"), desk=("#6b6f76", "#fff"), classifieds=("#8a5a00", "#fff"), local=("#0b7a75", "#fff"),
                    feature=("#e0a100", "#15171c"), kadambari=("#8e2c6b", "#fff"),
                    world=("#5b3fa8", "#fff"), puz1=("#1f7a3a", "#fff"), puz2=("#d2571a", "#fff"), garden=("#4d7a1b", "#fff"),
                    tales=("#c72a66", "#fff"), sports=("#0f5fa8", "#fff"), kitchen=("#a0522d", "#fff"))
SHORT = dict(front="ಮುಖಪುಟ", desk="ಡೆಸ್ಕ್", classifieds="ಪ್ರಕಟಣೆ", local="ಸ್ಥಳೀಯ", world="ಜಗತ್ತು", feature="ವಿಶೇಷ", kadambari="ಕಾದಂಬರಿ",
             puz1="ಒಗಟು ೧", puz2="ಒಗಟು ೨", garden="ತೋಟ", kitchen="ಅಡುಗೆ", tales="ಕತೆ", sports="ಕ್ರೀಡೆ")
# English names are used only to search Wikimedia Commons for a photograph of each plant
PLANT_TERMS = {
    "Udupi Mallige": ["Jasminum sambac flower", "Jasminum sambac"],
    "Aboli": ["Crossandra infundibuliformis flower", "Crossandra infundibuliformis"],
    "Hibiscus": ["Hibiscus rosa-sinensis flower", "Hibiscus rosa-sinensis"],
    "Tulsi": ["Ocimum tenuiflorum", "Holy basil Ocimum tenuiflorum plant"],
    "Curry leaf": ["Murraya koenigii leaves", "Murraya koenigii"],
    "Monstera": ["Monstera deliciosa leaf", "Monstera deliciosa plant"],
    "Canna lily": ["Canna indica flower", "Canna indica"],
}


def kn_date(d):
    return f"{KN_DAYS[d.weekday()]}, {kd(d.day)} {KN_MONTHS[d.month - 1]} {kd(d.year)}"


def kn_date_short(d):
    return f"{kd(d.day)} {KN_MONTHS[d.month - 1]}"


def sources(items):
    if not items:
        return ""
    return '<p class="src">' + "".join(f'<a href="{E(u, quote=True)}" target="_blank" rel="noopener">{E(n)}</a>' for n, u in items) + "</p>"


# ------------------------------------------------------------------ page shell
class Paper:
    def __init__(self, day, private):
        self.day, self.private, self.pages = day, private, []

    def add(self, key, title, body, blurb=""):
        self.pages.append(dict(key=key, title=title, body=body, blurb=blurb))

    def render_pages(self):
        out = []
        n = len(self.pages)
        for i, p in enumerate(self.pages):
            col, fg = PAGE_COLOURS[p["key"]]
            nxt = self.pages[i + 1] if i + 1 < n else None
            foot = (f'<a href="#p-{nxt["key"]}">ಪುಟ {kd(i + 2)}ಕ್ಕೆ ತಿರುಗಿಸಿ: {E(nxt["title"])} &rarr;</a>' if nxt else '<a href="#top">ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ &uarr;</a>')
            out.append(
                f'<section class="page{" gold" if p["key"] == "feature" else ""}" id="p-{p["key"]}" style="--pc:{col};--pcfg:{fg}" aria-labelledby="h-{p["key"]}">'
                f'<header class="ph"><span class="pn" aria-hidden="true">{i + 1}</span>'
                f'<div class="pt"><span class="pk">ಪುಟ {kd(i + 1)} / {kd(n)}</span><h2 id="h-{p["key"]}">{E(p["title"])}</h2></div>'
                f'<span class="pd">{E(kn_date(self.day))}</span></header>'
                f'<div class="wrap"><div class="pb">{p["body"]}</div>'
                f'<footer class="pf">{foot}<span class="pg">ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ &middot; {kd(i + 1)}/{kd(n)}</span></footer></div></section>'
                + self.joke_after.get(p["key"], ""))
        return "".join(out)

    joke_after = {}

    def pills(self):
        o = []
        for i, p in enumerate(self.pages):
            col, fg = PAGE_COLOURS[p["key"]]
            o.append(f'<a class="pill" href="#p-{p["key"]}" style="--c:{col};--cf:{fg}"><b>{kd(i + 1)}</b>{E(SHORT[p["key"]])}</a>')
        return "".join(o)


# ------------------------------------------------------------------ jokes
def joke_break(day, k, jokes):
    idx = (day - LAUNCH).days * 4 + k
    kn = jokes["kn"][idx % len(jokes["kn"])]
    return ('<div class="wrap"><aside class="joke" aria-label="ಪುಟಗಳ ನಡುವೆ ಒಂದು ಹಾಸ್ಯ">'
            f'<h3>ಸ್ವಲ್ಪ ನಗೋಣ</h3><div class="jj"><div><p class="kn" lang="kn">{E(kn)}</p></div></div></aside></div>')


# ------------------------------------------------------------------ pages
def front_page(P, news, wx, sun, moon, priv):
    lead = news["lead"]
    tiles = []
    if wx:
        t = wx[0]
        tiles.append(f'<div><span class="lab">ಇಂದಿನ ಹವಾಮಾನ</span><div class="v">{t["hi"]}&deg; / {t["lo"]}&deg;</div><div class="n">{E(t["sky"])}, ಮಳೆಯ ಸಾಧ್ಯತೆ {t["pop"]}%</div></div>')
        tiles.append(f'<div><span class="lab">ಗಾಳಿ</span><div class="v">{t["wind"]} ಕಿ.ಮೀ./ಗಂ</div><div class="n">ದಿನದ ಗರಿಷ್ಠ ವೇಗ</div></div>')
    else:
        tiles.append('<div><span class="lab">ಇಂದಿನ ಹವಾಮಾನ</span><div class="v">ಸಿಕ್ಕಿಲ್ಲ</div><div class="n">ಇಂದು ಬೆಳಗ್ಗೆ ಮುನ್ಸೂಚನೆ ಲಭ್ಯವಾಗಲಿಲ್ಲ</div></div>')
        tiles.append('<div><span class="lab">ಗಾಳಿ</span><div class="v">&ndash;</div><div class="n">&nbsp;</div></div>')
    tiles.append(f'<div><span class="lab">ಸೂರ್ಯೋದಯ</span><div class="v">{sun[0]}</div><div class="n">ಮಂಗಳೂರು, ಲೆಕ್ಕಾಚಾರದ್ದು</div></div>')
    tiles.append(f'<div><span class="lab">ಸೂರ್ಯಾಸ್ತ</span><div class="v">{sun[1]}</div><div class="n">ಹಗಲು {int(sun[2] // 60)} ಗಂಟೆ {int(sun[2] % 60)} ನಿಮಿಷ</div></div>')
    tiles.append(f'<div><span class="lab">ಚಂದ್ರ</span><div class="v">{moon[1]}%</div><div class="n">{E(moon[0])}, ಲೆಕ್ಕಾಚಾರದ್ದು</div></div>')
    idx = []
    for i, p in enumerate(P.pages):
        col, fg = PAGE_COLOURS[p["key"]]
        idx.append(f'<li><span class="num" style="--c:{col};--cf:{fg}">{kd(i + 1)}</span><div><a href="#p-{p["key"]}">{E(p["title"])}</a><span class="d">{E(p["blurb"])}</span></div></li>')
    alert = ""
    if priv:
        alert = (f'<div class="alert"><span class="kicker">ಓದುಗರ ಗಮನಕ್ಕೆ</span><p><b>{E(priv["notice"]["title"])}.</b> {E(priv["notice"]["text"])} '
                 f'<a href="#p-desk">ಡೆಸ್ಕ್ ಪುಟದಲ್ಲಿ ಓದಿ</a></p></div>')
    body = "".join(f"<p>{E(x)}</p>" for x in lead["body"])
    briefs = "".join(f"<li>{E(b)}</li>" for b in news["briefly"])
    return (alert + f'<div class="glance">{"".join(tiles)}</div>'
            '<div class="cols2" style="margin-top:26px"><div>'
            f'<span class="kicker">{E(lead["kicker"])}</span><h3 class="hl1" style="margin-top:8px">{E(lead["headline"])}</h3>'
            f'<p class="deck">{E(lead["deck"])}</p><div class="body drop rule">{body}</div>{sources(lead["sources"])}</div>'
            f'<aside><h3 class="sub">ಇಂದಿನ ಸಂಚಿಕೆಯಲ್ಲಿ</h3><ul class="index">{"".join(idx)}</ul>'
            f'<div class="rule"><h3 class="sub">ಸಂಕ್ಷಿಪ್ತವಾಗಿ</h3><ul class="brief">{briefs}</ul></div></aside></div>')


def local_page(P, news, wx, sun, moon, cfg, notices_items):
    stories = []
    for s in news["stories"]:
        link = f' &middot; <a href="{E(s["url"], quote=True)}" target="_blank" rel="noopener">{E(s["source"])}</a>' if s.get("url") else f' &middot; {E(s["source"])}'
        stories.append(f'<li class="story" data-place="{E(s["place"], quote=True)}"><span class="place">{E(s["place"])}</span><h3>{E(s["title"])}</h3>'
                       f'<p>{E(s["text"])}</p><p class="meta">{E(s["age"])}{link}</p></li>')
    if wx:
        rows = "".join(
            f'<tr><td class="dd">{"ಇಂದು" if i == 0 else E(KN_DAYS_SHORT[d["date"].weekday()] + " " + kd(d["date"].day) + " " + KN_MONTHS[d["date"].month - 1][:3])}</td>'
            f'<td class="tt">{d["hi"]}&deg;<small> / {d["lo"]}&deg;</small></td>'
            f'<td class="cc"><b>{E(d["sky"])}</b><br>ಮಳೆಯ ಸಾಧ್ಯತೆ {d["pop"]}%, {d["mm"]:g} ಮಿ.ಮೀ.</td></tr>' for i, d in enumerate(wx))
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        wxbox = (f'<table class="wx">{rows}</table><p class="wxsrc">ಗರಿಷ್ಠ / ಕನಿಷ್ಠ ತಾಪಮಾನ &deg;ಸೆ.ನಲ್ಲಿ. <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo.com</a> ನ ಮಾದರಿ ಮುನ್ಸೂಚನೆ, '
                 f'12.91&deg;ಉ 74.86&deg;ಪೂ ಸ್ಥಳಕ್ಕೆ, {E(kd(now.day) + " " + KN_MONTHS[now.month - 1] + " " + kd(now.year) + ", " + kd(now.strftime("%H:%M")))} (ಭಾರತೀಯ ಕಾಲಮಾನ) ಪಡೆದದ್ದು. ಇದು ಮುನ್ಸೂಚನೆ, ವೀಕ್ಷಣೆಯಲ್ಲ.</p>')
    else:
        wxbox = '<p class="empty">ಐದು ದಿನದ ಮುನ್ಸೂಚನೆ ಇಂದು ಬೆಳಗ್ಗೆ ಲಭ್ಯವಾಗಲಿಲ್ಲ. ಮೂಲ: <a href="https://open-meteo.com/">Open-Meteo.com</a>.</p>'
    up = "".join(f'<li><b>{E(u["when"])}</b><span>{E(u["what"])}</span></li>' for u in news["coming_up"])
    nums = "".join(f'<div><b>{E(n)}</b><span>{E(t)}</span></div>' for n, t in news["helplines"])
    by8 = " ರಾತ್ರಿ 8ರ ಒಳಗೆ ಕಳುಹಿಸಿದರೆ ನಾಳೆಯ ಪತ್ರಿಕೆಯಲ್ಲಿ ಬರಬಹುದು." if bn.is_open(cfg) else ""
    notes = (f'<div class="notes"><div><span class="kicker">ಕುಲ್ಲಂಗಾಲ್ ಮತ್ತು ಸುತ್ತಮುತ್ತ &middot; ಇಂದಿನ ಪ್ರಕಟಣೆಗಳು</span>{bn.notices_html(notices_items)}</div>'
             f'<aside class="sendbox"><h3 class="hl3">ನಿಮ್ಮ ಸುದ್ದಿ ನಮಗೆ ಕಳುಹಿಸಿ</h3><p>ಕಾರ್ಯಕ್ರಮಗಳು, ಕಳೆದುಹೋದ-ಸಿಕ್ಕಿದ ವಸ್ತುಗಳು, ರಸ್ತೆ ಕಾಮಗಾರಿ, ದೇವಸ್ಥಾನ ಮತ್ತು ಶಾಲೆಯ ಪ್ರಕಟಣೆಗಳು, ಅಂಗಡಿ ಉದ್ಘಾಟನೆ, ಕ್ಲಬ್ ಮತ್ತು ಶಾಲಾ ಕ್ರೀಡಾ ಫಲಿತಾಂಶಗಳು.{by8}</p>{bn.send_html(cfg)}</aside></div>')
    return ('<div class="cols2"><div>'
            f'<h3 class="sub">ಕರಾವಳಿಯ ಇನ್ನಷ್ಟು ಸುದ್ದಿ</h3><ul id="story-list">{"".join(stories)}</ul></div>'
            f'<aside><h3 class="sub">ಮಂಗಳೂರಿನಲ್ಲಿ ಮುಂದಿನ ಐದು ದಿನ</h3>{wxbox}'
            f'<p class="wxsrc" style="margin-top:6px">ಸೂರ್ಯೋದಯ {sun[0]}, ಸೂರ್ಯಾಸ್ತ {sun[1]} (ಲೆಕ್ಕಾಚಾರ). ಚಂದ್ರ: {E(moon[0])}, {moon[1]}% ಬೆಳಗಿದೆ (ಲೆಕ್ಕಾಚಾರ).</p>'
            f'<div class="rule"><h3 class="sub">ಮುಂದಿನ ದಿನಗಳಲ್ಲಿ</h3><ul class="up">{up}</ul>{sources(news.get("coming_up_sources"))}</div>'
            f'<div class="rule"><h3 class="sub">ನೆನಪಿಟ್ಟುಕೊಳ್ಳಬೇಕಾದ ಸಂಖ್ಯೆಗಳು</h3><div class="nums">{nums}</div></div></aside></div>{notes}')


def feature_page(P, feats, cache_ok=True):
    day = P.day
    f = next((x for x in feats if x["weekday"] == day.weekday()), feats[0])
    img = os.path.join(HERE, "content", f"feature-{day.isoformat()}.jpg")
    fig = ""
    if os.path.exists(img):
        uri = "data:image/jpeg;base64," + base64.b64encode(open(img, "rb").read()).decode()
        fig = f'<figure class="fig"><img src="{uri}" alt="{E(f["title"], quote=True)} ಲೇಖನದ ಚಿತ್ರ" width="800" height="600"><figcaption>ಕ್ಯಾನ್ವಾ ಎಐ ಬಳಸಿ ರಚಿಸಿದ ಚಿತ್ರ. ಇದು ಛಾಯಾಚಿತ್ರವಲ್ಲ, ಚಿತ್ರ.</figcaption></figure>'
    else:
        ph = photos.photo_for("feature-" + f["theme"], f["terms"], day, f.get("files")) if cache_ok else None
        if ph:
            fig = (f'<figure class="fig"><img src="{ph["uri"]}" alt="{E(f["title"], quote=True)}, ಛಾಯಾಚಿತ್ರ" width="800" height="600" loading="lazy">'
                   f'<figcaption>{photos.credit_html(ph)}</figcaption></figure>')
    body = "".join(f"<p>{E(x)}</p>" for x in f["body"])
    return (f'<div class="feat">{fig}<div><span class="kicker">{E(f["theme_kn"])} &middot; ಕರಾವಳಿ ವಿಶೇಷ</span><h3 class="hl1" style="margin-top:8px">{E(f["title"])}</h3>'
            f'<div class="body drop rule">{body}</div>{sources(f["sources"])}</div></div>'
            '<p class="wxsrc" style="margin-top:20px">ಪ್ರತಿದಿನ ಒಂದು ವಿಶೇಷ ಲೇಖನ; ವಾರದ ಪ್ರತಿ ದಿನ ಬೇರೆ ವಿಷಯ: ಆಹಾರ, ಕಲೆ, ಸ್ಥಳ, ಸಂಪ್ರದಾಯ, ಕಡಲು, ಪ್ರಕೃತಿ ಮತ್ತು ದೇವಾಲಯ.</p>')


def render_paras(texts):
    """Paragraphs of a serial; a paragraph that is just *** becomes a scene break."""
    return "".join('<p class="sb" aria-hidden="true">* * *</p>' if t.strip() == "***" else "<p>" + E(t) + "</p>" for t in texts)


def serial_page(P):
    s = load("serial_kn.json")
    eps = s["episodes"]
    idx = (P.day - LAUNCH).days + 1
    latest = max(1, min(idx, len(eps)))
    e = eps[latest - 1]
    recap = f'<div class="recap"><b>ಹಿಂದಿನ ಸಂಚಿಕೆಯಲ್ಲಿ</b>{E(e["recap"])}</div>' if latest > 1 else ""
    nxt = "ಮುಂದಿನ ಸಂಚಿಕೆ ನಾಳೆ ಇದೇ ಪುಟದಲ್ಲಿ." if idx <= len(eps) else "ಹೊಸ ಸಂಚಿಕೆ ಶೀಘ್ರದಲ್ಲೇ ಬರಲಿದೆ."
    arch = ""
    if latest > 1:
        items = "".join(
            f'<details><summary>ಸಂಚಿಕೆ {kd(x["n"])}: {E(x["title"])}</summary><div class="story-text kn" lang="kn">{render_paras(x["text"])}</div></details>'
            for x in reversed(eps[:latest - 1]))
        arch = f'<details class="arch"><summary>ಹಿಂದಿನ ಸಂಚಿಕೆಗಳು ({kd(latest - 1)})</summary>{items}</details>'
    return (f'<div class="ser" lang="kn"><span class="epi">ಸಂಚಿಕೆ {kd(e["n"])} &middot; {E(s["title"])}</span>'
            f'<h3 class="ser-title">{E(e["title"])}</h3>{recap}'
            f'<div class="story-text kn">{render_paras(e["text"])}</div>'
            f'<p class="next">{nxt}</p><p class="blurb">{E(s["blurb"])}</p>{arch}</div>')


def pz_json(pid, obj):
    body = json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/json" id="{pid}">{body}</script>'


def cw_cells(cw):
    """Crossword cells as a list of rows of strings, "" for a black square. Older saved days used a string per row with '.'."""
    return [[("" if ch == "." else ch) for ch in row] if isinstance(row, str) else list(row) for row in cw["grid"]]


def yesterday_block(day):
    """Yesterday's answers, printed at the end of the puzzle pages. Answers appear only the day after."""
    y = day - datetime.timedelta(days=1)
    head = '<section class="yest"><h3>ನಿನ್ನೆಯ ಉತ್ತರಗಳು</h3>'
    if y < LAUNCH:
        return head + '<p class="muted">ಇದು ಮೊದಲ ಸಂಚಿಕೆ, ಆದ್ದರಿಂದ ಮುದ್ರಿಸಲು ಉತ್ತರಗಳಿಲ್ಲ. ಇಂದಿನ ಒಗಟುಗಳ ಉತ್ತರ ನಾಳೆಯ ಪತ್ರಿಕೆಯಲ್ಲಿ ಬರುತ್ತದೆ.</p></section>'
    if not puzzles.exists(y):
        return head + (f'<p class="muted">{E(kn_date(y))}ರಂದು ಪತ್ರಿಕೆ ಪ್ರಕಟವಾಗಿರಲಿಲ್ಲ, ಆದ್ದರಿಂದ ಮುದ್ರಿಸಲು ಉತ್ತರಗಳಿಲ್ಲ. '
                       'ಇಂದಿನ ಒಗಟುಗಳ ಉತ್ತರ ನಾಳೆಯ ಪತ್ರಿಕೆಯಲ್ಲಿ ಬರುತ್ತದೆ.</p></section>')
    pz = puzzles.get(y, save=False)
    su, cw, ws, cr = pz["sudoku"], pz["crossword"], pz["wordsearch"], pz["cryptogram"]
    out = head + f'<p class="muted">{E(kn_date(y))}. ನಿಮ್ಮ ಉತ್ತರಗಳನ್ನು ಇವುಗಳೊಂದಿಗೆ ಹೋಲಿಸಿ ನೋಡಿ.</p>'
    sg = "".join("<tr>" + "".join("<td>" + su["solution"][r * 9 + c] + "</td>" for c in range(9)) + "</tr>" for r in range(9))
    out += f'<p class="sub2">ಸುಡೋಕು</p><table class="grid9">{sg}</table>'
    cg = "".join("<tr>" + "".join("<td>" + E(ch) + "</td>" if ch else '<td class="b"></td>' for ch in row) + "</tr>" for row in cw_cells(cw))
    acr = "".join(f'<li><b>{w["n"]}.</b> {E(w["ans"])}</li>' for w in cw["across"])
    dwn = "".join(f'<li><b>{w["n"]}.</b> {E(w["ans"])}</li>' for w in cw["down"])
    out += (f'<p class="sub2">ಪದಬಂಧ: ಎಡದಿಂದ ಬಲಕ್ಕೆ</p><ul class="ans">{acr}</ul><p class="sub2">ಪದಬಂಧ: ಮೇಲಿನಿಂದ ಕೆಳಕ್ಕೆ</p><ul class="ans">{dwn}</ul>'
            f'<table class="grid9 cwg">{cg}</table>')
    if ws.get("lang") == "kn":
        hit = set()
        for w in ws["words"]:
            for k in range(w["n"]):
                hit.add((w["r"] + w["dr"] * k, w["c"] + w["dc"] * k))
        wg = "".join("<tr>" + "".join(('<td class="h">' if (r, c) in hit else "<td>") + E(ch) + "</td>" for c, ch in enumerate(row)) + "</tr>" for r, row in enumerate(ws["grid"]))
        out += f'<p class="sub2">ಪದ ಹುಡುಕಾಟ: {E(ws["title"])}</p><table class="grid9 wsg">{wg}</table>'
    if cr.get("lang") == "kn":
        who = f' <span class="muted">— {E(cr["who"])}</span>' if cr.get("who") else ""
        out += f'<p class="sub2">ಗಾದೆ ಸಂಕೇತ</p><p class="quote">{E(cr["plain"])}</p>{who}'
    return out + "</section>"


def puzzle_pages(P, pz):
    day = P.day.isoformat()
    su, cw, ws, cr = pz["sudoku"], pz["crossword"], pz["wordsearch"], pz["cryptogram"]
    # Only what a printed puzzle shows goes into the page: no solutions, no answers, no word positions.
    mask = ["".join("#" if ch else "." for ch in row) for row in cw_cells(cw)]
    strip = lambda items: [{k: v for k, v in w.items() if k != "ans"} for w in items]
    p1 = (
        f'<section class="puz"><h3>ಸುಡೋಕು <span class="lvl">{E(LEVELS.get(su["level"], su["level"]))}</span></h3>'
        '<p class="how">ಪ್ರತಿ ಸಾಲು, ಕಂಬ ಮತ್ತು 3×3 ಪೆಟ್ಟಿಗೆಯಲ್ಲಿ 1ರಿಂದ 9ರ ಅಂಕೆಗಳು ಒಮ್ಮೆಯೇ ಬರುವಂತೆ ತುಂಬಿ. ಚೌಕದ ಮೇಲೆ ಒತ್ತಿ, ಸಂಖ್ಯೆ ಬರೆಯಿರಿ. '
        'ಮುದ್ರಿತ ಒಗಟಿನಂತೆ ಇದು ನಿಮ್ಮ ಉತ್ತರ ಪರಿಶೀಲಿಸುವುದಿಲ್ಲ, ಸುಳಿವೂ ಕೊಡುವುದಿಲ್ಲ. ನಿಮ್ಮ ಪೆನ್ಸಿಲ್ ಗುರುತುಗಳು ಈ ಸಾಧನದಲ್ಲೇ ಉಳಿಯುತ್ತವೆ. ಉತ್ತರ ನಾಳೆಯ ಪತ್ರಿಕೆಯಲ್ಲಿ.</p>'
        '<div id="sudoku"></div>'
        + pz_json("pz-sudoku", dict(puzzle=su["puzzle"], day=day)) + '</section>'
        '<section class="puz"><h3>ಗಾದೆ ಸಂಕೇತ <span class="lvl">ಬಿಡಿಸಿ</span></h3>'
        '<p class="how">ಒಂದು ಪ್ರಸಿದ್ಧ ಗಾದೆಯ ಪ್ರತಿ ಅಕ್ಷರದ ಬದಲು ಒಂದು ಸಂಖ್ಯೆ ಇದೆ; ಒಂದೇ ಅಕ್ಷರಕ್ಕೆ ಯಾವಾಗಲೂ ಒಂದೇ ಸಂಖ್ಯೆ. ಕೆಲವು ಅಕ್ಷರಗಳನ್ನು ಕೊಟ್ಟಿದೆ. '
        'ಉಳಿದವನ್ನು ಸಂಖ್ಯೆಯ ಮೇಲಿರುವ ಖಾಲಿ ಚೌಕದಲ್ಲಿ ಬರೆಯಿರಿ (ಒಂದು ಚೌಕಕ್ಕೆ ಒಂದು ಅಕ್ಷರ, ಉದಾಹರಣೆಗೆ ಮಾ, ಲ್ಲಿ, ಕ್ಷ). ಉತ್ತರ ನಾಳೆಯ ಪತ್ರಿಕೆಯಲ್ಲಿ.</p>'
        '<div id="cryptogram"></div>'
        + pz_json("pz-cryptogram", dict(words=cr["words"], given=cr["given"], day=day)) + '</section>')
    unit = "ಅಕ್ಷರ"
    across = "".join(f'<li data-w="A,{w["r"]},{w["c"]}"><b>{w["n"]}</b><span>{E(w["clue"])} ({w["len"]} {unit})</span></li>' for w in cw["across"])
    down = "".join(f'<li data-w="D,{w["r"]},{w["c"]}"><b>{w["n"]}</b><span>{E(w["clue"])} ({w["len"]} {unit})</span></li>' for w in cw["down"])
    back = ", ಈ ವಾರಾಂತ್ಯ ಕೆಲವು ಹಿಂದಕ್ಕೂ ಇರುತ್ತವೆ" if ws["hard"] else ""
    p2 = (
        '<section class="puz"><h3>ಪದಬಂಧ <span class="lvl">ಕಠಿಣ</span></h3>'
        '<p class="how" lang="kn">ಚೌಕದ ಮೇಲೆ ಒತ್ತಿ, ನಿಮ್ಮ ಫೋನಿನ ಕನ್ನಡ ಕೀಬೋರ್ಡ್‌ನಲ್ಲಿ ಉತ್ತರ ಬರೆಯಿರಿ. ಒಂದು ಚೌಕಕ್ಕೆ ಒಂದು ಅಕ್ಷರ (ಉದಾಹರಣೆಗೆ ಮೀ, ಲ್ಲು, ಕ್ಷ). ಅದೇ ಚೌಕವನ್ನು ಮತ್ತೆ ಒತ್ತಿದರೆ ದಿಕ್ಕು ಅಡ್ಡದಿಂದ ಕೆಳಕ್ಕೆ ಬದಲಾಗುತ್ತದೆ. ಉತ್ತರಗಳು ನಾಳೆಯ ಪತ್ರಿಕೆಯಲ್ಲಿ.</p>'
        '<div id="crossword"></div><div class="pbtns" id="cw-btns"></div>'
        f'<div class="clues" lang="kn"><div><h4>ಎಡದಿಂದ ಬಲಕ್ಕೆ</h4><ul>{across}</ul></div><div><h4>ಮೇಲಿನಿಂದ ಕೆಳಕ್ಕೆ</h4><ul>{down}</ul></div></div>'
        + pz_json("pz-crossword", dict(rows=cw["rows"], cols=cw["cols"], grid=mask, across=strip(cw["across"]), down=strip(cw["down"]), day=day)) + '</section>'
        f'<section class="puz"><h3>ಪದ ಹುಡುಕಾಟ <span class="lvl">{E(ws["title"])}</span></h3>'
        f'<p class="how">ಈ {kd(len(ws["words"]))} ಪದಗಳನ್ನು ಜಾಲದಲ್ಲಿ ಹುಡುಕಿ. ಪದಗಳು ಅಡ್ಡ, ಕೆಳಕ್ಕೆ ಅಥವಾ ಓರೆಯಾಗಿ ಇರುತ್ತವೆ{back}. ಒಂದು ಚೌಕದಲ್ಲಿ ಒಂದು ಅಕ್ಷರ ಇದೆ. '
        'ಅಕ್ಷರಗಳ ಮೇಲೆ ಒತ್ತಿ ಹೈಲೈಟರ್‌ನಂತೆ ಗುರುತಿಸಿ; ಪಟ್ಟಿಯಲ್ಲಿನ ಪದದ ಮೇಲೆ ಒತ್ತಿ ಕಾಟು ಹಾಕಿ. ಏನನ್ನೂ ಪರಿಶೀಲಿಸುವುದಿಲ್ಲ.</p>'
        '<div id="wordsearch"></div>'
        + pz_json("pz-wordsearch", dict(size=ws["size"], grid=ws["grid"], words=[{"w": w["w"]} for w in ws["words"]], day=day)) + '</section>'
        + yesterday_block(P.day))
    return p1, p2


GARDEN_KINDS = (("herb", "ಇಂದಿನ ಗಿಡಮೂಲಿಕೆ", 0), ("flower", "ಇಂದಿನ ಹೂವು", 3), ("indoor", "ಒಳಾಂಗಣ ಮತ್ತು ತೋಟದ ಗಿಡ", 5))


def garden_page(P, garden):
    """One herb, one flower and one indoor or garden plant (sometimes a bonsai) a day, rotating inside each group."""
    d = (P.day - LAUNCH).days
    picks = []
    for cat, label, off in GARDEN_KINDS:
        grp = [p for p in garden["plants"] if p.get("category") == cat]
        p = grp[(d + off) % len(grp)]
        picks.append(("ಇಂದಿನ ಬೋನ್ಸಾಯ್" if p.get("bonsai") else label, p))
    cards = []
    for k, (label, p) in enumerate(picks):
        ph = photos.photo_for(p["key"], PLANT_TERMS.get(p["key"], [p["latin"]]), P.day)
        fig = (f'<figure class="fig"><img src="{ph["uri"]}" alt="{E(p["name"], quote=True)}, ಛಾಯಾಚಿತ್ರ" width="800" height="600" loading="lazy"><figcaption>{photos.credit_html(ph)}</figcaption></figure>' if ph else "")
        tags = "".join(f"<span>{E(t)}</span>" for t in p["tags"])
        spec = "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in p["spec"])
        cards.append(f'<article class="plant{" first" if k == 0 else ""}">{fig}<div><span class="kicker">{E(label)}</span><h3>{E(p["name"])}</h3><div class="names"><span class="lat">{E(p["latin"])}</span></div>'
                     f'<div class="tags">{tags}</div><p class="about">{E(p["about"])}</p><dl class="spec">{spec}</dl></div></article>')
    month = "".join(f"<li>{E(x)}</li>" for x in garden["month"])
    return (f'<p class="deck" style="margin-bottom:22px">ಪ್ರತಿದಿನ ಒಂದು ಗಿಡಮೂಲಿಕೆ, ಒಂದು ಹೂವು ಮತ್ತು ಒಂದು ಒಳಾಂಗಣ ಅಥವಾ ತೋಟದ ಗಿಡ (ಆಗಾಗ ಬೋನ್ಸಾಯ್): ಜಂಬಿಟ್ಟಿಗೆ ಮಣ್ಣು, ಉಪ್ಪುಗಾಳಿ ಮತ್ತು ತಿಂಗಳುಗಟ್ಟಲೆ ಮಳೆಯ ಕರಾವಳಿ ಮನೆಗೆ ಹೊಂದುವಂತೆ ಆಯ್ದದ್ದು.</p><div class="plants">{"".join(cards)}</div>'
            f'<div class="month"><h3 class="sub">ಈ ತಿಂಗಳು ತೋಟದಲ್ಲಿ</h3><p class="prog" id="garden-prog"></p><ul id="garden-list">{month}</ul></div>')


def recipe_page(P, rec):
    """One vegetarian recipe a day without onion or garlic, in the order of the list."""
    items = rec["recipes"]
    r = items[(P.day - LAUNCH).days % len(items)]
    nxt = items[((P.day - LAUNCH).days + 1) % len(items)]
    ing = "".join(f"<li>{E(x)}</li>" for x in r["ingredients"])
    steps = "".join(f"<li>{E(x)}</li>" for x in r["steps"])
    return (f'<article class="recipe" lang="kn"><p class="deck" style="margin-bottom:14px">ಶುದ್ಧ ಸಸ್ಯಾಹಾರ, ಈರುಳ್ಳಿ ಮತ್ತು ಬೆಳ್ಳುಳ್ಳಿ ಇಲ್ಲದ ಅಡುಗೆ: ಪ್ರತಿದಿನ ಒಂದು.</p>'
            f'<span class="kicker">{E(r["kind"])} &middot; ಇಂದಿನ ಅಡುಗೆ</span><h3 class="hl1" style="margin-top:8px">{E(r["name"])}</h3>'
            f'<p class="deck">{E(r["intro"])}</p>'
            f'<div class="rmeta"><span><b>ಪ್ರಮಾಣ</b>{E(r["serves"])}</span><span><b>ಸಮಯ</b>{E(r["time"])}</span><span class="nog"><b>ಈರುಳ್ಳಿ-ಬೆಳ್ಳುಳ್ಳಿ</b>ಇಲ್ಲ</span></div>'
            f'<h4 class="sub" style="margin-top:20px">ಬೇಕಾದ ಸಾಮಗ್ರಿ</h4><ul class="ingr">{ing}</ul>'
            f'<h4 class="sub" style="margin-top:20px">ಮಾಡುವ ವಿಧಾನ</h4><ol class="steps">{steps}</ol>'
            f'<p class="moral"><span class="lab">ಸಲಹೆ</span> {E(r["tip"])}</p>'
            f'<p class="wxsrc" style="margin-top:14px">ನಾಳೆಯ ಅಡುಗೆ: {E(nxt["name"])}. ಇಂಗು ಇಷ್ಟವಿಲ್ಲದಿದ್ದರೆ ಬಿಡಬಹುದು; ಇಂಗಿನ ಪುಡಿಯಲ್ಲಿ ಕೆಲವೊಮ್ಮೆ ಗೋಧಿ ಹಿಟ್ಟು ಬೆರೆತಿರುತ್ತದೆ, ಲೇಬಲ್ ನೋಡಿ. ಅಡುಗೆಗಳು ಸಾಂಪ್ರದಾಯಿಕ ವಿಧಾನಗಳನ್ನು ಆಧರಿಸಿ ನಮ್ಮದೇ ಮಾತುಗಳಲ್ಲಿ ಬರೆದವು; ಅಳತೆಗಳನ್ನು ನಿಮ್ಮ ರುಚಿಗೆ ತಕ್ಕಂತೆ ಹೊಂದಿಸಿ.</p></article>')


def plate_html(key):
    meta = json.load(open(os.path.join(HERE, "tales_assets", "meta.json")))
    keys = ["tortoise1", "tortoise2"] if key == "tortoise" else ["camel"]
    figs = []
    for k in keys:
        m = meta[k]
        data = base64.b64encode(open(os.path.join(HERE, "tales_assets", k + ".jpg"), "rb").read()).decode()
        who = m["artist"] or ("ದಿ ಮೆಟ್ರೋಪಾಲಿಟನ್ ಮ್ಯೂಸಿಯಂ ಆಫ್ ಆರ್ಟ್" if k == "camel" else "ಅಜ್ಞಾತ")
        if k.startswith("tortoise"):
            who = "ಎಲ್ಸ್‌ವರ್ತ್ ಯಂಗ್, 1912"
        figs.append(f'<figure class="plate"><img src="data:image/jpeg;base64,{data}" alt="ಈ ಕತೆಯ ಹಳೆಯ ಚಿತ್ರ" loading="lazy" width="{m["size"][0]}" height="{m["size"][1]}">'
                    f'<figcaption>ಹಳೆಯ ಚಿತ್ರ: {E(who)}, <a href="{m["page"]}" target="_blank" rel="noopener">ವಿಕಿಮೀಡಿಯಾ ಕಾಮನ್ಸ್</a>, {E(m["lic"])}</figcaption></figure>')
    return "".join(figs)


def tales_page(P):
    """One tale a day, Panchatantra and Jataka on alternate days."""
    day = (P.day - LAUNCH).days
    series = comics.PANCHATANTRA if day % 2 == 0 else comics.JATAKA
    label = "ಪಂಚತಂತ್ರ" if day % 2 == 0 else "ಜಾತಕ ಕತೆಗಳು"
    ep = series[(day // 2) % len(series)]
    panels = "".join(f'<figure class="panel">{comics.panel(p)}<figcaption><b>{kd(i)}</b>{E(p["cap"])}</figcaption></figure>' for i, p in enumerate(ep["panels"], 1))
    plate = plate_html(ep["plate"]) if ep["plate"] else ""
    art = (f'<article class="tale"><span class="kicker">{E(label)} &middot; ಇಂದಿನ ಕತೆ</span><h3 class="hl2" style="margin-top:6px">{E(ep["title"])}</h3>'
           f'<div class="panels">{panels}</div><p class="moral"><span class="lab">ನೀತಿ</span> {E(ep["moral"])}</p>{plate}</article>')
    other = "ಜಾತಕ" if day % 2 == 0 else "ಪಂಚತಂತ್ರದ"
    return (comics.COMIC_DEFS + f'<p class="deck" style="margin-bottom:20px">ಪ್ರತಿದಿನ ಒಂದು ಹಳೆಯ ಭಾರತೀಯ ಕತೆ, ನಾಲ್ಕು ಚಿತ್ರಗಳಲ್ಲಿ, ಕೊನೆಯಲ್ಲಿ ನೀತಿಯೊಂದಿಗೆ. ನಾಳೆ: {other} ಕತೆ. '
            'ಕತೆಗಳು ಸಾಂಪ್ರದಾಯಿಕವಾದವು, ಇಲ್ಲಿ ನಮ್ಮದೇ ಮಾತುಗಳಲ್ಲಿ ಮರುಹೇಳಲಾಗಿದೆ; ಚಿತ್ರಗಳು ಮೂಲ ರಚನೆ.</p>'
            f'<div class="tales">{art}</div>'), ep["title"], None


def world_page(world):
    ld = world["lead"]
    body = "".join(f"<p>{E(t)}</p>" for t in ld["body"])
    cards = "".join(f'<article><span class="sport">{E(i["region"])}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p>'
                    f'<p class="src"><a href="{E(i["url"], quote=True)}" target="_blank" rel="noopener">{E(i["source"])}</a></p></article>' for i in world["items"])
    brief = "".join(f"<li>{E(x)}</li>" for x in world.get("briefly", []))
    return (f'<span class="kicker">{E(ld["region"])}</span><h3 class="hl1" style="margin:8px 0 0">{E(ld["headline"])}</h3><p class="deck">{E(ld["deck"])}</p>'
            f'<div class="body drop rule">{body}</div>{sources(ld["sources"])}'
            f'<div class="rule"><h3 class="sub">ಜಗತ್ತಿನ ಸುತ್ತ</h3><div class="sp">{cards}</div></div>'
            + (f'<div class="rule"><h3 class="sub">ಸಂಕ್ಷಿಪ್ತವಾಗಿ</h3><ul class="brief">{brief}</ul></div>' if brief else "")
            + '<p class="wxsrc" style="margin-top:18px">ವಿಶ್ವ ಸುದ್ದಿಯನ್ನು ಪ್ರತಿ ಸುದ್ದಿಯ ಕೆಳಗೆ ಹೆಸರಿಸಿದ ಮೂಲಗಳಿಂದ ವೆಬ್ ಹುಡುಕಾಟದ ಮೂಲಕ ಸಂಗ್ರಹಿಸಿ ನಮ್ಮದೇ ಮಾತುಗಳಲ್ಲಿ ಬರೆಯಲಾಗಿದೆ. ವರದಿಗಳು ಭಿನ್ನವಾಗಿದ್ದರೆ ಅಥವಾ ದ್ವಿತೀಯ ಮೂಲದ್ದಾದರೆ ಪಠ್ಯದಲ್ಲೇ ಹೇಳಲಾಗಿದೆ.</p>')


def sports_page(news):
    sp = news["sports"]
    cards = "".join(f'<article><span class="sport">{E(i["sport"])}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p>'
                    f'<p class="src"><a href="{E(i["url"], quote=True)}" target="_blank" rel="noopener">{E(i["source"])}</a></p></article>' for i in sp["items"])
    return (f'<h3 class="hl1" style="margin-bottom:22px">{E(sp["headline"])}</h3><div class="sp">{cards}</div>'
            f'<div class="rule"><h3 class="sub">ಸ್ಥಳೀಯ ಕ್ರೀಡೆ</h3><p>{E(sp["local"])}</p></div>')


def desk_pages(priv):
    notices = "".join(
        f'<article><span class="tag{" act" if n["act"] else ""}">{E(n["tag"])}</span><h3 class="hl2">{E(n["title"])}</h3><p>{E(n["text"])}</p>'
        f'<a class="more" href="{E(n["url"], quote=True)}" target="_blank" rel="noopener">{E(n["link"])}</a></article>' for n in priv["desk"])
    also = "".join(f'<li><b>{E(a["title"])}</b><small>{E(a["tag"])}</small><p>{E(a["text"])}</p></li>' for a in priv["also"])
    desk = (f'<div class="desk">{notices}</div><div class="cols2" style="margin-top:26px"><div><h3 class="sub">ಇವೂ ಬಂದಿವೆ</h3><ul class="rows">{also}</ul></div>'
            f'<aside><h3 class="sub">ಮನೆಗೆಲಸ</h3><p><b class="hl2">{E(priv["cleanup"]["n"])}</b> {E(priv["cleanup"]["text"])}</p></aside></div>'
            '<p class="wxsrc">ಖಾಸಗಿ ಪುಟ: ಈ ಆವೃತ್ತಿಯನ್ನು ಹಂಚಿಕೊಳ್ಳಬಾರದು. ಜಿಮೇಲ್ ಸಂಪರ್ಕ ಕೊನೆಯ ಬಾರಿ ಲಭ್ಯವಿದ್ದಾಗಿನ ನಿಮ್ಮ ಇನ್‌ಬಾಕ್ಸ್‌ನಿಂದ ಇದನ್ನು ತಯಾರಿಸಲಾಗಿದೆ.</p>')
    ads = "".join(f'<div class="ad"><span class="lab">ಬೇಕಾಗಿದ್ದಾರೆ</span><h3>{E(a["title"])}</h3><p>{E(a["text"])}</p><span class="lab" style="color:#565b63">{E(a["from"])}</span></div>' for a in priv["classifieds"])
    return desk, f'<div class="ads">{ads}</div>'


# ------------------------------------------------------------------ assemble
def assemble(day, private, ctx):
    P = Paper(day, private)
    P.joke_after = {}
    news, garden, jokes, feats, pz, wx, sun, moon, cfg, notices_items, priv = (ctx[k] for k in
        ("news", "garden", "jokes", "feats", "pz", "wx", "sun", "moon", "cfg", "notices", "priv"))
    tales_html, t1, t2 = ctx["tales"]
    p1, p2 = ctx["pz_pages"]
    n_days = (day - LAUNCH).days
    # page order; front page needs the index, so add pages first with placeholders
    P.add("front", "ಮುಖಪುಟ", "", "ದಿನದ ಮುಖ್ಯ ಸುದ್ದಿ, ಹವಾಮಾನ, ಸೂರ್ಯ ಮತ್ತು ಚಂದ್ರ")
    if private:
        desk, ads = desk_pages(priv)
        P.add("desk", "ಡೆಸ್ಕ್", desk, "ನಿಮ್ಮ ಇನ್‌ಬಾಕ್ಸ್, ಸಂಪಾದಿತ (ಖಾಸಗಿ)")
        P.add("classifieds", "ಪ್ರಕಟಣೆಗಳು", ads, "ನಿಮಗೆ ಹೊಂದುವ ಉದ್ಯೋಗಗಳು (ಖಾಸಗಿ)")
    P.add("local", "ಕರಾವಳಿ ಮತ್ತು ಸ್ಥಳೀಯ", local_page(P, news, wx, sun, moon, cfg, notices_items), "ಇನ್ನಷ್ಟು ಸುದ್ದಿ, ಐದು ದಿನದ ಹವಾಮಾನ, ಪ್ರಕಟಣೆಗಳು, ಬೇಕಾದ ಸಂಖ್ಯೆಗಳು")
    P.add("world", "ಜಗತ್ತು", world_page(ctx["world"]), "ದಿನದ ವಿಶ್ವ ಸುದ್ದಿ: ಮುಖ್ಯ ಸುದ್ದಿ, ಪ್ರದೇಶಗಳು, ಅರ್ಥವ್ಯವಸ್ಥೆ, ಬಾಹ್ಯಾಕಾಶ ಮತ್ತು ವಿಜ್ಞಾನ")
    P.add("feature", "ಕರಾವಳಿ ವಿಶೇಷ", ctx["feature"], "ಪ್ರತಿದಿನ ಒಂದು ವಿಶೇಷ: ಆಹಾರ, ಕಲೆ, ಸ್ಥಳ, ಸಂಪ್ರದಾಯ, ಕಡಲು, ಪ್ರಕೃತಿ, ದೇವಾಲಯ")
    P.add("kadambari", "ಕನ್ನಡ ಕಾದಂಬರಿ", serial_page(P), "ಸಮುದ್ರ ನಿಲಯ: ಧಾರಾವಾಹಿ ಕಾದಂಬರಿ, ಪ್ರತಿದಿನ ಒಂದು ಸಂಚಿಕೆ")
    P.add("puz1", "ಒಗಟುಗಳು ೧", p1, "ಸುಡೋಕು ಮತ್ತು ಗಾದೆ ಸಂಕೇತ")
    P.add("puz2", "ಒಗಟುಗಳು ೨", p2, "ಕನ್ನಡ ಪದಬಂಧ ಮತ್ತು ಪದ ಹುಡುಕಾಟ")
    P.add("garden", "ತೋಟ", garden_page(P, garden), "ಪ್ರತಿದಿನ ಒಂದು ಗಿಡಮೂಲಿಕೆ, ಒಂದು ಹೂವು, ಒಂದು ಒಳಾಂಗಣ ಅಥವಾ ಬೋನ್ಸಾಯ್ ಗಿಡ")
    P.add("kitchen", "ಅಡುಗೆಮನೆ", recipe_page(P, ctx["recipes"]), f"ಇಂದಿನ ಅಡುಗೆ: {ctx['recipe_name']} (ಈರುಳ್ಳಿ-ಬೆಳ್ಳುಳ್ಳಿ ಇಲ್ಲದ ಸಸ್ಯಾಹಾರ)")
    P.add("tales", "ಕತೆಗಳು", tales_html, f"ಇಂದು: {t1}")
    P.add("sports", "ಕ್ರೀಡೆ", sports_page(news), "ಕ್ರಿಕೆಟ್, ದೊಡ್ಡ ಕ್ರೀಡಾಕೂಟಗಳು ಮತ್ತು ಸ್ಥಳೀಯ ಕ್ರೀಡೆ")
    P.pages[0]["body"] = front_page(P, news, wx, sun, moon, priv if private else None)
    P.joke_after = {"local": joke_break(day, 0, jokes), "kadambari": joke_break(day, 1, jokes), "puz2": joke_break(day, 2, jokes), "garden": joke_break(day, 3, jokes)}
    n = len(P.pages)
    css, js = rd("paper.css"), rd("paper.js")
    edno = n_days + 1
    doc = (
        '<title>ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=Noto+Serif+Kannada:wght@400;600;800&family=Noto+Sans+Kannada:wght@400;700;900&display=swap">\n'
        f'<style>{css}</style>\n'
        f'<div id="top"></div><header class="wrap mast" lang="kn"><div class="top lab"><span>ಸಂಪುಟ ೧ &middot; ಸಂಚಿಕೆ {kd(edno)}</span><span>ಮಂಗಳೂರು &middot; ಉಡುಪಿ &middot; ಕುಂದಾಪುರ</span><span>ದಿನಪತ್ರಿಕೆ</span></div>'
        '<div class="knname" lang="kn">ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ</div>'
        '<p class="slogan">ಕರಾವಳಿಯ ಸುದ್ದಿ, ಕತೆ, ಒಗಟು ಮತ್ತು ತೋಟ: ಬೆಳಗಿನ ಓದಿಗೆ ಪುಟಗಳ ಪತ್ರಿಕೆ</p>'
        f'<div class="dateline lab"><span lang="kn">{kn_date(day)}</span><span>{kd(n)} ಪುಟಗಳು, ಸುಮಾರು ಇಪ್ಪತ್ತು ನಿಮಿಷದ ಓದು</span></div></header>\n'
        f'<nav class="nav" aria-label="ಪುಟಗಳು" lang="kn"><div class="wrap nav-in"><div class="pills">{P.pills()}</div>'
        '<div class="tools"><button class="tbtn" id="size-down" type="button" aria-label="ಅಕ್ಷರ ಚಿಕ್ಕದು">ಅ&minus;</button><button class="tbtn" id="size-up" type="button" aria-label="ಅಕ್ಷರ ದೊಡ್ಡದು">ಅ+</button>'
        f'<a class="btn share" id="wa-share" href="#" target="_blank" rel="noopener" data-url="{PUBLIC_URL}">ವಾಟ್ಸ್‌ಆ್ಯಪ್</a></div></div></nav>\n'
        f'<main lang="kn">{P.render_pages()}</main>\n'
        '<footer class="wrap colo" lang="kn"><b>ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ</b>'
        f'<p>ಸಂಚಿಕೆ {kd(edno)}, {E(kn_date(day))}ರಂದು ತಯಾರಿಸಿದ್ದು. ಸುದ್ದಿ ಮತ್ತು ಕ್ರೀಡೆಯ ವಿವರಗಳು ಪ್ರತಿ ಸುದ್ದಿಯ ಕೆಳಗೆ ಹೆಸರಿಸಿದ ಮೂಲಗಳಿಂದ ವೆಬ್ ಹುಡುಕಾಟದ ಮೂಲಕ ಸಂಗ್ರಹಿಸಿ ನಮ್ಮದೇ ಮಾತುಗಳಲ್ಲಿ ಬರೆದವು. ಹವಾಮಾನ Open-Meteo.com ನಿಂದ (CC BY 4.0). ಸೂರ್ಯೋದಯ, ಸೂರ್ಯಾಸ್ತ ಮತ್ತು ಚಂದ್ರನ ಕಲೆ ಲೆಕ್ಕಾಚಾರದ್ದು. ಗಿಡ ಮತ್ತು ವಿಶೇಷ ಲೇಖನದ ಛಾಯಾಚಿತ್ರಗಳು ವಿಕಿಮೀಡಿಯಾ ಕಾಮನ್ಸ್‌ನಿಂದ, ಶ್ರೇಯಸ್ಸು ಪ್ರತಿ ಚಿತ್ರದ ಕೆಳಗಿದೆ. ಕಾದಂಬರಿ, ಒಗಟುಗಳು, ಕತೆಗಳ ರೇಖಾಚಿತ್ರಗಳು ಮತ್ತು ಹಾಸ್ಯಗಳನ್ನು ಈ ಪತ್ರಿಕೆಗಾಗಿಯೇ ಬರೆದು ರಚಿಸಲಾಗಿದೆ; ಕಾದಂಬರಿಯ ಎಲ್ಲ ವ್ಯಕ್ತಿಗಳು ಮತ್ತು ಸಂಸ್ಥೆಗಳು ಕಾಲ್ಪನಿಕ. ಕತೆಗಳ ಪುಟದ ಹಳೆಯ ಚಿತ್ರಗಳ ಶ್ರೇಯಸ್ಸು ಅವುಗಳ ಕೆಳಗಿದೆ.</p>'
        '<p>ಪ್ರತಿದಿನ ಬೆಳಗ್ಗೆ ಹೊಸ ಸಂಚಿಕೆ ಈ ಸಂಚಿಕೆಯ ಸ್ಥಾನ ಪಡೆಯುತ್ತದೆ.</p></footer>\n'
        f'<script>{js}</script>')
    doc = doc.replace("<main", '<main data-month="' + day.strftime("%Y-%m") + '"', 1)
    return doc, t1, t2


def main():
    args = [a for a in sys.argv[1:]]
    day = datetime.date.today()
    outs = dict(private=os.path.join(HERE, "kullangal-vaarte.html"), public=os.path.join(HERE, "public-edition.html"))
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--private":
            outs["private"] = args[i + 1]; i += 2
        elif a == "--public":
            outs["public"] = args[i + 1]; i += 2
        else:
            day = datetime.date.fromisoformat(a); i += 1
    ctx = dict(news=load("news.json"), garden=load("garden.json"), jokes=load("jokes.json"), feats=load("features.json"), priv=load("private.json"), world=load("world.json"), recipes=load("recipes.json"))
    ctx["pz"] = puzzles.get(day)
    ctx["pz_pages"] = puzzle_pages(Paper(day, False), ctx["pz"])
    ctx["wx"] = weather.forecast()
    ctx["sun"], ctx["moon"] = astro.sun_times(day), astro.moon(day)
    cfg = bn.load_json("kullangal_config.json")
    ctx["cfg"] = cfg
    rows = list(bn.load_json("kullangal_notices.json").get("notices", [])) + bn.sheet_rows(cfg.get("sheet_csv_url"))
    ctx["notices"] = bn.todays(rows, day)
    if ctx["news"]["date"] != day.isoformat():
        print(f"WARNING: content/news.json is dated {ctx['news']['date']}, not {day}. Refresh the news first.", file=sys.stderr)
    if ctx["world"]["date"] != day.isoformat():
        print(f"WARNING: content/world.json is dated {ctx['world']['date']}, not {day}. Refresh the world news first.", file=sys.stderr)
    ctx["recipe_name"] = ctx["recipes"]["recipes"][(day - LAUNCH).days % len(ctx["recipes"]["recipes"])]["name"]
    tp = Paper(day, False)
    ctx["tales"] = tales_page(tp)
    ctx["feature"] = feature_page(tp, ctx["feats"])
    for private in (True, False):
        doc, t1, t2 = assemble(day, private, ctx)
        path = outs["private" if private else "public"]
        if not private:
            words = ("mail.google", "gmail", "@gmail", "miniTV", "Payment declined", "Outskill", "pradyumna", "ಮಿನಿಟಿವಿ", "ಔಟ್‌ಸ್ಕಿಲ್", "ಜಿಮೇಲ್", "ಜಿಪೇ", "ಲಿಬೆರಾ", "ವೆನ್ಹ್")
            bad = [w for w in words if w.lower() in doc.lower()]
            assert not bad, f"private content leaked into the shareable edition: {bad}"
        open(path, "w", encoding="utf-8").write(doc)
        print(("private" if private else "public"), path, round(len(doc) / 1e6, 2), "MB")
    print("Tale:", t1)


if __name__ == "__main__":
    main()
