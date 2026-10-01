#!/usr/bin/env python3
"""Build Kullangal Vaarte from data files.

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
KN_MONTHS = ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"]

PAGE_COLOURS = dict(front=("#c4361f", "#fff"), desk=("#6b6f76", "#fff"), classifieds=("#8a5a00", "#fff"), local=("#0b7a75", "#fff"),
                    feature=("#e0a100", "#15171c"), kadambari=("#8e2c6b", "#fff"), serial=("#2f4fb0", "#fff"),
                    puz1=("#1f7a3a", "#fff"), puz2=("#d2571a", "#fff"), garden=("#4d7a1b", "#fff"),
                    tales=("#c72a66", "#fff"), sports=("#0f5fa8", "#fff"))
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
    return f"{KN_DAYS[d.weekday()]}, {str(d.day).translate(KN_DIGITS)} {KN_MONTHS[d.month - 1]} {str(d.year).translate(KN_DIGITS)}"


def en_date(d):
    return d.strftime("%A, %-d %B %Y")


def sources(items):
    if not items:
        return ""
    return '<p class="src">' + "".join(f'<a href="{E(u, quote=True)}" target="_blank" rel="noopener">{E(n)}</a>' for n, u in items) + "</p>"


# ------------------------------------------------------------------ page shell
class Paper:
    def __init__(self, day, private):
        self.day, self.private, self.pages = day, private, []

    def add(self, key, en, kn, body, blurb=""):
        self.pages.append(dict(key=key, en=en, kn=kn, body=body, blurb=blurb))

    def render_pages(self):
        out = []
        n = len(self.pages)
        for i, p in enumerate(self.pages):
            col, fg = PAGE_COLOURS[p["key"]]
            nxt = self.pages[i + 1] if i + 1 < n else None
            foot = (f'<a href="#p-{nxt["key"]}">Turn to page {i + 2}: {E(nxt["en"])} &rarr;</a>' if nxt else '<a href="#top">Back to the front page &uarr;</a>')
            out.append(
                f'<section class="page{" gold" if p["key"] == "feature" else ""}" id="p-{p["key"]}" style="--pc:{col};--pcfg:{fg}" aria-labelledby="h-{p["key"]}">'
                f'<header class="ph"><span class="pn" aria-hidden="true">{i + 1}</span>'
                f'<div class="pt"><span class="pk">Page {i + 1} of {n}</span><h2 id="h-{p["key"]}">{E(p["en"])}</h2><span class="pkn" lang="kn">{p["kn"]}</span></div>'
                f'<span class="pd">{E(en_date(self.day))}</span></header>'
                f'<div class="wrap"><div class="pb">{p["body"]}</div>'
                f'<footer class="pf">{foot}<span class="pg">Kullangal Vaarte &middot; {i + 1}/{n}</span></footer></div></section>'
                + self.joke_after.get(p["key"], ""))
        return "".join(out)

    joke_after = {}

    def pills(self):
        o = []
        for i, p in enumerate(self.pages):
            col, fg = PAGE_COLOURS[p["key"]]
            short = {"Coast & Local": "Local", "Coast Feature": "Feature", "Kannada Kadambari": "ಕಾದಂಬರಿ", "English Serial": "Serial"}.get(p["en"], p["en"])
            o.append(f'<a class="pill" href="#p-{p["key"]}" style="--c:{col};--cf:{fg}"><b>{i + 1}</b>{E(short)}</a>')
        return "".join(o)


# ------------------------------------------------------------------ jokes
def joke_break(day, k, jokes):
    idx = (day - LAUNCH).days * 3 + k
    en, kn = jokes["en"][idx % len(jokes["en"])], jokes["kn"][idx % len(jokes["kn"])]
    return ('<div class="wrap"><aside class="joke" aria-label="A joke to break the pages">'
            '<h3>Take a break <span class="kn" lang="kn">ನಗು</span></h3><div class="jj">'
            f'<div><span class="jl">In English</span><p>{E(en)}</p></div>'
            f'<div><span class="jl">ಕನ್ನಡದಲ್ಲಿ</span><p class="kn" lang="kn">{E(kn)}</p></div></div></aside></div>')


# ------------------------------------------------------------------ pages
def front_page(P, news, wx, sun, moon, priv):
    lead = news["lead"]
    day = P.day
    tiles = []
    if wx:
        t = wx[0]
        tiles.append(f'<div><span class="lab">Weather today</span><div class="v">{t["hi"]}&deg; / {t["lo"]}&deg;</div><div class="n">{E(t["sky"])}, rain chance {t["pop"]}%</div></div>')
        tiles.append(f'<div><span class="lab">Wind</span><div class="v">{t["wind"]} km/h</div><div class="n">Highest gust of the day, 10 m up</div></div>')
    else:
        tiles.append('<div><span class="lab">Weather today</span><div class="v">Not fetched</div><div class="n">Forecast unavailable this morning</div></div>')
        tiles.append('<div><span class="lab">Wind</span><div class="v">&ndash;</div><div class="n">&nbsp;</div></div>')
    tiles.append(f'<div><span class="lab">Sunrise</span><div class="v">{sun[0]}</div><div class="n">Mangaluru, calculated</div></div>')
    tiles.append(f'<div><span class="lab">Sunset</span><div class="v">{sun[1]}</div><div class="n">Day length {int(sun[2] // 60)} h {int(sun[2] % 60)} min</div></div>')
    tiles.append(f'<div><span class="lab">Moon</span><div class="v">{moon[1]}%</div><div class="n">{E(moon[0])}, calculated</div></div>')
    idx = []
    for i, p in enumerate(P.pages):
        col, fg = PAGE_COLOURS[p["key"]]
        idx.append(f'<li><span class="num" style="--c:{col};--cf:{fg}">{i + 1}</span><div><a href="#p-{p["key"]}">{E(p["en"])}</a><span class="d">{E(p["blurb"])}</span></div></li>')
    alert = ""
    if priv:
        alert = (f'<div class="alert"><span class="kicker">Notice to the reader</span><p><b>{E(priv["notice"]["title"])}.</b> {E(priv["notice"]["text"])} '
                 f'<a href="#p-desk">Read on the Desk page</a></p></div>')
    body = "".join(f"<p>{E(x)}</p>" for x in lead["body"])
    briefs = "".join(f"<li>{E(b)}</li>" for b in news["briefly"])
    return (alert + f'<div class="glance">{"".join(tiles)}</div>'
            '<div class="cols2" style="margin-top:26px"><div>'
            f'<span class="kicker">{E(lead["kicker"])}</span><h3 class="hl1" style="margin-top:8px">{E(lead["headline"])}</h3>'
            f'<p class="deck">{E(lead["deck"])}</p><div class="body drop rule">{body}</div>{sources(lead["sources"])}</div>'
            f'<aside><h3 class="sub">Inside today</h3><ul class="index">{"".join(idx)}</ul>'
            f'<div class="rule"><h3 class="sub">Briefly</h3><ul class="brief">{briefs}</ul></div></aside></div>')


def local_page(P, news, wx, sun, moon, cfg, notices_items):
    stories = []
    for s in news["stories"]:
        link = f' &middot; <a href="{E(s["url"], quote=True)}" target="_blank" rel="noopener">{E(s["source"])}</a>' if s.get("url") else f' &middot; {E(s["source"])}'
        stories.append(f'<li class="story" data-place="{E(s["place"], quote=True)}"><span class="place">{E(s["place"])}</span><h3>{E(s["title"])}</h3>'
                       f'<p>{E(s["text"])}</p><p class="meta">{E(s["age"])}{link}</p></li>')
    if wx:
        rows = "".join(
            f'<tr><td class="dd">{"Today" if i == 0 else E(d["date"].strftime("%a %-d %b"))}</td><td class="tt">{d["hi"]}&deg;<small> / {d["lo"]}&deg;</small></td>'
            f'<td class="cc"><b>{E(d["sky"])}</b><br>Rain chance {d["pop"]}%, {d["mm"]:g} mm</td></tr>' for i, d in enumerate(wx))
        wxbox = (f'<table class="wx">{rows}</table><p class="wxsrc">High / low in &deg;C. Model forecast from <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo.com</a> '
                 f'for 12.91&deg;N 74.86&deg;E, fetched {E(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%-d %B %Y, %H:%M"))} India time. A forecast, not an observation.</p>')
    else:
        wxbox = '<p class="empty">The five-day forecast could not be fetched this morning. Source: <a href="https://open-meteo.com/">Open-Meteo.com</a>.</p>'
    up = "".join(f'<li><b>{E(u["when"])}</b><span>{E(u["what"])}</span></li>' for u in news["coming_up"])
    nums = "".join(f'<div><b>{E(n)}</b><span>{E(t)}</span></div>' for n, t in news["helplines"])
    by8 = " Send it by 8 pm and it can go in tomorrow's paper." if bn.is_open(cfg) else ""
    notes = (f'<div class="notes"><div><span class="kicker">Kullangal &amp; nearby &middot; notices for the day</span>{bn.notices_html(notices_items)}</div>'
             f'<aside class="sendbox"><h3 class="hl3">Send us your news</h3><p>Events, lost and found, road works, temple and school notices, shop openings, club and school sports results.{by8}</p>{bn.send_html(cfg)}</aside></div>')
    return ('<div class="cols2"><div>'
            f'<h3 class="sub">More stories from the coast</h3><ul id="story-list">{"".join(stories)}</ul></div>'
            f'<aside><h3 class="sub">Five days ahead in Mangaluru</h3>{wxbox}'
            f'<p class="wxsrc" style="margin-top:6px">Sunrise {sun[0]}, sunset {sun[1]} (calculated). Moon: {E(moon[0])}, {moon[1]}% lit (calculated).</p>'
            f'<div class="rule"><h3 class="sub">Coming up</h3><ul class="up">{up}</ul>{sources(news.get("coming_up_sources"))}</div>'
            f'<div class="rule"><h3 class="sub">Numbers worth keeping</h3><div class="nums">{nums}</div></div></aside></div>{notes}')


def feature_page(P, feats, cache_ok=True):
    day = P.day
    f = next((x for x in feats if x["weekday"] == day.weekday()), feats[0])
    img = os.path.join(HERE, "content", f"feature-{day.isoformat()}.jpg")
    fig = ""
    if os.path.exists(img):
        uri = "data:image/jpeg;base64," + base64.b64encode(open(img, "rb").read()).decode()
        fig = f'<figure class="fig"><img src="{uri}" alt="Illustration for {E(f["title"], quote=True)}" width="800" height="600"><figcaption>Illustration made with Canva AI. It is a picture, not a photograph.</figcaption></figure>'
    else:
        ph = photos.photo_for("feature-" + f["theme"], f["terms"], day, f.get("files")) if cache_ok else None
        if ph:
            fig = (f'<figure class="fig"><img src="{ph["uri"]}" alt="{E(f["title"], quote=True)}, photograph" width="800" height="600" loading="lazy">'
                   f'<figcaption>{photos.credit_html(ph)}</figcaption></figure>')
    body = "".join(f"<p>{E(x)}</p>" for x in f["body"])
    return (f'<div class="feat">{fig}<div><span class="kicker">{E(f["theme"])} &middot; a coast feature</span><h3 class="hl1" style="margin-top:8px">{E(f["title"])}</h3>'
            f'<div class="body drop rule">{body}</div>{sources(f["sources"])}</div></div>'
            '<p class="wxsrc" style="margin-top:20px">One feature every day, on a different subject each weekday: food, art, places, tradition, the sea, nature and temples.</p>')


def render_paras(texts):
    """Paragraphs of a serial; a paragraph that is just *** becomes a scene break."""
    return "".join('<p class="sb" aria-hidden="true">* * *</p>' if t.strip() == "***" else "<p>" + E(t) + "</p>" for t in texts)


def serial_page(P, name, lang):
    s = load(f"serial_{name}.json")
    eps = s["episodes"]
    idx = (P.day - LAUNCH).days + 1
    latest = max(1, min(idx, len(eps)))
    e = eps[latest - 1]
    kn = lang == "kn"
    paras = render_paras(e["text"])
    recap_lab = "ಹಿಂದಿನ ಸಂಚಿಕೆಯಲ್ಲಿ" if kn else "Previously"
    recap = f'<div class="recap"><b>{recap_lab}</b>{E(e["recap"])}</div>' if latest > 1 else ""
    ep_lab = f"ಸಂಚಿಕೆ {str(e['n']).translate(KN_DIGITS)}" if kn else f"Episode {e['n']}"
    nxt = ("ಮುಂದಿನ ಸಂಚಿಕೆ ನಾಳೆ ಇದೇ ಪುಟದಲ್ಲಿ." if idx <= len(eps) else "ಹೊಸ ಸಂಚಿಕೆ ಶೀಘ್ರದಲ್ಲೇ ಬರಲಿದೆ.") if kn else \
          ("The next episode arrives tomorrow on this page." if idx <= len(eps) else "The next episode is on its way.")
    arch = ""
    if latest > 1:
        items = "".join(
            f'<details><summary>{"ಸಂಚಿಕೆ " + str(x["n"]).translate(KN_DIGITS) if kn else "Episode " + str(x["n"])}: {E(x["title"])}</summary>'
            f'<div class="story-text {"kn" if kn else "en"}"{" lang=kn" if kn else ""}>{render_paras(x["text"])}</div></details>'
            for x in reversed(eps[:latest - 1]))
        arch = f'<details class="arch"><summary>{"ಹಿಂದಿನ ಸಂಚಿಕೆಗಳು" if kn else "Earlier episodes"} ({latest - 1})</summary>{items}</details>'
    return (f'<div class="ser"><span class="epi">{ep_lab} &middot; {E(s["title"])}</span>'
            f'<h3 class="ser-title"{" lang=kn" if kn else ""}>{E(e["title"])}</h3>{recap}'
            f'<div class="story-text {"kn" if kn else "en"}"{" lang=kn" if kn else ""}>{paras}</div>'
            f'<p class="next"{" lang=kn" if kn else ""}>{nxt}</p><p class="blurb"{" lang=kn" if kn else ""}>{E(s["blurb"])}</p>{arch}</div>')


def pz_json(pid, obj):
    body = json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/json" id="{pid}">{body}</script>'


def yesterday_block(day):
    """Yesterday's answers, printed at the end of the puzzle pages. Answers appear only the day after."""
    y = day - datetime.timedelta(days=1)
    if y < LAUNCH:
        return ('<section class="yest"><h3>Yesterday\'s answers</h3><p class="muted">This is the first edition, so there are no answers to print yet. '
                'Tomorrow\'s paper carries the answers to today\'s puzzles.</p></section>')
    pz = puzzles.get(y, save=False)
    su, cw, ws, cr = pz["sudoku"], pz["crossword"], pz["wordsearch"], pz["cryptogram"]
    sg = "".join("<tr>" + "".join("<td>" + su["solution"][r * 9 + c] + "</td>" for c in range(9)) + "</tr>" for r in range(9))
    cg = "".join("<tr>" + "".join('<td class="b"></td>' if ch == "." else "<td>" + ch + "</td>" for ch in row) + "</tr>" for row in cw["grid"])
    hit = set()
    for w in ws["words"]:
        for k in range(len(w["w"])):
            hit.add((w["r"] + w["dr"] * k, w["c"] + w["dc"] * k))
    wg = "".join("<tr>" + "".join(('<td class="h">' if (r, c) in hit else "<td>") + ch + "</td>" for c, ch in enumerate(row)) + "</tr>" for r, row in enumerate(ws["grid"]))
    acr = "".join(f'<li><b>{w["n"]}.</b> {E(w["ans"])}</li>' for w in cw["across"])
    dwn = "".join(f'<li><b>{w["n"]}.</b> {E(w["ans"])}</li>' for w in cw["down"])
    who = f' <span class="muted">Attributed to {E(cr["who"])}.</span>' if cr["who"] else ""
    return (f'<section class="yest"><h3>Yesterday\'s answers</h3><p class="muted">{E(y.strftime("%A, %-d %B"))}. Check your work against these.</p>'
            f'<p class="sub2">Sudoku</p><table class="grid9">{sg}</table>'
            f'<p class="sub2">Crossword, across</p><ul class="ans">{acr}</ul><p class="sub2">Crossword, down</p><ul class="ans">{dwn}</ul>'
            f'<table class="grid9 cwg">{cg}</table>'
            f'<p class="sub2">Word search: {E(ws["title"])}</p><table class="grid9 wsg">{wg}</table>'
            f'<p class="sub2">Cryptogram</p><p class="quote">{E(cr["plain"].capitalize())}</p>{who}</section>')


def puzzle_pages(P, pz):
    day = P.day.isoformat()
    su, cw, ws, cr = pz["sudoku"], pz["crossword"], pz["wordsearch"], pz["cryptogram"]
    # Only what a printed puzzle shows goes into the page: no solutions, no answers, no word positions.
    mask = ["".join("." if ch == "." else "#" for ch in row) for row in cw["grid"]]
    strip = lambda items: [{k: v for k, v in w.items() if k != "ans"} for w in items]
    p1 = (
        f'<section class="puz"><h3>Sudoku <span class="lvl">{su["level"]}</span></h3>'
        '<p class="how">Fill every row, column and 3 by 3 box with the digits 1 to 9, once each. Tap a square, then write a number. '
        'Like a printed puzzle, it will not check your work or give hints. Your pencil marks stay on this device. The answer is in tomorrow\'s paper.</p>'
        '<div id="sudoku"></div>'
        + pz_json("pz-sudoku", dict(puzzle=su["puzzle"], day=day)) + '</section>'
        '<section class="puz"><h3>Cryptogram <span class="lvl">Decode</span></h3>'
        '<p class="how">Every letter of a well-known saying has been swapped for another letter, always the same swap, and no letter stands for itself. '
        'Write your guess above each coded letter. The answer is in tomorrow\'s paper.</p>'
        '<div id="cryptogram"></div>'
        + pz_json("pz-cryptogram", dict(cipher=cr["cipher"], day=day)) + '</section>')
    across = "".join(f'<li data-w="A,{w["r"]},{w["c"]}"><b>{w["n"]}</b><span>{E(w["clue"])} ({w["len"]})</span></li>' for w in cw["across"])
    down = "".join(f'<li data-w="D,{w["r"]},{w["c"]}"><b>{w["n"]}</b><span>{E(w["clue"])} ({w["len"]})</span></li>' for w in cw["down"])
    p2 = (
        '<section class="puz"><h3>Mini crossword <span class="lvl">Coast &amp; India</span></h3>'
        '<p class="how">Tap a square and type. Tap the same square again to turn the direction from across to down. The answers are in tomorrow\'s paper.</p>'
        '<div id="crossword"></div><div class="pbtns" id="cw-btns"></div>'
        f'<div class="clues"><div><h4>Across</h4><ul>{across}</ul></div><div><h4>Down</h4><ul>{down}</ul></div></div>'
        + pz_json("pz-crossword", dict(rows=cw["rows"], cols=cw["cols"], grid=mask, across=strip(cw["across"]), down=strip(cw["down"]), day=day)) + '</section>'
        f'<section class="puz"><h3>Word search <span class="lvl">{E(ws["title"])}</span></h3>'
        f'<p class="how">Find these {len(ws["words"])} words in the grid. Words run across, down or diagonally{", and this weekend some run backwards too" if ws["hard"] else ""}. '
        'Tap letters to mark them with a highlighter, and tap a word in the list to cross it off. Nothing is checked for you.</p>'
        '<div id="wordsearch"></div>'
        + pz_json("pz-wordsearch", dict(size=ws["size"], grid=ws["grid"], words=[{"w": w["w"]} for w in ws["words"]], day=day)) + '</section>'
        + yesterday_block(P.day))
    return p1, p2


def garden_page(P, garden):
    pl = garden["plants"]
    start = ((P.day - LAUNCH).days * 3) % len(pl)
    picks = [pl[(start + k) % len(pl)] for k in range(3)]
    cards = []
    for k, p in enumerate(picks):
        ph = photos.photo_for(p["name"], PLANT_TERMS.get(p["name"], [p["latin"]]), P.day)
        fig = (f'<figure class="fig"><img src="{ph["uri"]}" alt="{E(p["name"], quote=True)}, photograph" width="800" height="600" loading="lazy"><figcaption>{photos.credit_html(ph)}</figcaption></figure>' if ph else "")
        kn = f'<span class="knn" lang="kn">{E(p["kn"])}</span>' if p["kn"] else ""
        tags = "".join(f"<span>{E(t)}</span>" for t in p["tags"])
        spec = "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in p["spec"])
        cards.append(f'<article class="plant{" first" if k == 0 else ""}">{fig}<div><h3>{E(p["name"])}</h3><div class="names">{kn}<span class="lat">{E(p["latin"])}</span></div>'
                     f'<div class="tags">{tags}</div><p class="about">{E(p["about"])}</p><dl class="spec">{spec}</dl></div></article>')
    month = "".join(f"<li>{E(x)}</li>" for x in garden["month"])
    return (f'<p class="deck" style="margin-bottom:22px">Three plants a day for a home on the coast: laterite soil, salty air and months of rain.</p><div class="plants">{"".join(cards)}</div>'
            f'<div class="month"><h3 class="sub">This month in the garden</h3><p class="prog" id="garden-prog"></p><ul id="garden-list">{month}</ul></div>')


def plate_html(key):
    meta = json.load(open(os.path.join(HERE, "tales_assets", "meta.json")))
    keys = ["tortoise1", "tortoise2"] if key == "tortoise" else ["camel"]
    figs = []
    for k in keys:
        m = meta[k]
        data = base64.b64encode(open(os.path.join(HERE, "tales_assets", k + ".jpg"), "rb").read()).decode()
        who = m["artist"] or ("The Metropolitan Museum of Art" if k == "camel" else "Unknown")
        if k.startswith("tortoise"):
            who = "Ellsworth Young, 1912"
        figs.append(f'<figure class="plate"><img src="data:image/jpeg;base64,{data}" alt="Historic illustration for this tale" loading="lazy" width="{m["size"][0]}" height="{m["size"][1]}">'
                    f'<figcaption>Old illustration: {E(who)}, <a href="{m["page"]}" target="_blank" rel="noopener">Wikimedia Commons</a>, {E(m["lic"])}</figcaption></figure>')
    return "".join(figs)


def tales_page(P):
    """One tale a day, Panchatantra and Jataka on alternate days."""
    day = (P.day - LAUNCH).days
    series = comics.PANCHATANTRA if day % 2 == 0 else comics.JATAKA
    label = "Panchatantra" if day % 2 == 0 else "Jataka tales"
    ep = series[(day // 2) % len(series)]
    panels = "".join(f'<figure class="panel">{comics.panel(p)}<figcaption><b>{i}</b>{E(p["cap"])}</figcaption></figure>' for i, p in enumerate(ep["panels"], 1))
    plate = plate_html(ep["plate"]) if ep["plate"] else ""
    art = (f'<article class="tale"><span class="kicker">{E(label)} &middot; today\'s tale</span><h3 class="hl2" style="margin-top:6px">{E(ep["title"])}</h3>'
           f'<div class="panels">{panels}</div><p class="moral"><span class="lab">Moral</span> {E(ep["moral"])}</p>{plate}</article>')
    other = "Jataka" if day % 2 == 0 else "Panchatantra"
    return (comics.COMIC_DEFS + f'<p class="deck" style="margin-bottom:20px">One old Indian tale a day, drawn as four panels with the moral at the end. Tomorrow: a {other} tale. '
            'The stories are traditional and retold here in original words; the drawings are original.</p>'
            f'<div class="tales">{art}</div>'), ep["title"], None


def sports_page(news):
    sp = news["sports"]
    cards = "".join(f'<article><span class="sport">{E(i["sport"])}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p>'
                    f'<p class="src"><a href="{E(i["url"], quote=True)}" target="_blank" rel="noopener">{E(i["source"])}</a></p></article>' for i in sp["items"])
    return (f'<h3 class="hl1" style="margin-bottom:22px">{E(sp["headline"])}</h3><div class="sp">{cards}</div>'
            f'<div class="rule"><h3 class="sub">Local sports</h3><p>{E(sp["local"])}</p></div>')


def desk_pages(priv):
    notices = "".join(
        f'<article><span class="tag{" act" if n["act"] else ""}">{E(n["tag"])}</span><h3 class="hl2">{E(n["title"])}</h3><p>{E(n["text"])}</p>'
        f'<a class="more" href="{E(n["url"], quote=True)}" target="_blank" rel="noopener">{E(n["link"])}</a></article>' for n in priv["desk"])
    also = "".join(f'<li><b>{E(a["title"])}</b><small>{E(a["tag"])}</small><p>{E(a["text"])}</p></li>' for a in priv["also"])
    desk = (f'<div class="desk">{notices}</div><div class="cols2" style="margin-top:26px"><div><h3 class="sub">Also received</h3><ul class="rows">{also}</ul></div>'
            f'<aside><h3 class="sub">Housekeeping</h3><p><b class="hl2">{E(priv["cleanup"]["n"])}</b> {E(priv["cleanup"]["text"])}</p></aside></div>'
            '<p class="wxsrc">Private page: this edition is not for sharing. It is built from your inbox as of the last time the Gmail connector was available.</p>')
    ads = "".join(f'<div class="ad"><span class="lab">Wanted</span><h3>{E(a["title"])}</h3><p>{E(a["text"])}</p><span class="lab" style="color:#565b63">{E(a["from"])}</span></div>' for a in priv["classifieds"])
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
    P.add("front", "Front page", "ಮುಖಪುಟ", "", "The day's lead story, weather, sun and moon")
    if private:
        desk, ads = desk_pages(priv)
        P.add("desk", "Desk", "ಡೆಸ್ಕ್", desk, "Your inbox, edited (private)")
        P.add("classifieds", "Classifieds", "ಪ್ರಕಟಣೆಗಳು", ads, "Situations vacant matched to you (private)")
    P.add("local", "Coast & Local", "ಕರಾವಳಿ ಮತ್ತು ಸ್ಥಳೀಯ", local_page(P, news, wx, sun, moon, cfg, notices_items), "More stories, five-day weather, notices, useful numbers")
    P.add("feature", "Coast Feature", "ವಿಶೇಷ ಲೇಖನ", ctx["feature"], "One feature a day: food, art, places, tradition, sea, nature, temples")
    P.add("kadambari", "Kannada Kadambari", "ಕನ್ನಡ ಕಾದಂಬರಿ", serial_page(P, "kn", "kn"), "ಸಮುದ್ರ ನಿಲಯ: ಧಾರಾವಾಹಿ ಕಾದಂಬರಿ, ಪ್ರತಿದಿನ ಒಂದು ಸಂಚಿಕೆ")
    P.add("serial", "English Serial", "ಇಂಗ್ಲಿಷ್ ಕಾದಂಬರಿ", serial_page(P, "en", "en"), "The Tide Ledger: a coastal mystery, one episode a day")
    P.add("puz1", "Puzzles I", "ಒಗಟುಗಳು ೧", p1, "Sudoku and a cryptogram")
    P.add("puz2", "Puzzles II", "ಒಗಟುಗಳು ೨", p2, "A mini crossword and a word search")
    P.add("garden", "Garden", "ತೋಟ", garden_page(P, garden), "Three plants for a coastal home")
    P.add("tales", "Tales", "ಕತೆಗಳು", tales_html, f"Today: {t1}")
    P.add("sports", "Sports", "ಕ್ರೀಡೆ", sports_page(news), "Cricket, the Asian Games, hockey and kabaddi")
    P.pages[0]["body"] = front_page(P, news, wx, sun, moon, priv if private else None)
    P.joke_after = {"local": joke_break(day, 0, jokes), "serial": joke_break(day, 1, jokes), "puz2": joke_break(day, 2, jokes), "garden": joke_break(day, 3, jokes)}
    n = len(P.pages)
    css, js = rd("paper.css"), rd("paper.js")
    edno = n_days + 1
    doc = (
        '<title>Kullangal Vaarte</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700;9..144,800;9..144,900&family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Archivo+Narrow:wght@500;700&family=Noto+Serif+Kannada:wght@400;600;800&family=Noto+Sans+Kannada:wght@400;700&display=swap">\n'
        f'<style>{css}</style>\n'
        f'<div id="top"></div><header class="wrap mast"><div class="top lab"><span>Vol. I &middot; No. {edno}</span><span>Mangaluru &middot; Udupi &middot; Kundapura</span><span>Daily edition</span></div>'
        '<div class="knname" lang="kn">ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ</div><div class="enname">Kullangal Vaarte</div>'
        '<p class="slogan">The coast, in Kannada and English, in a morning read of numbered pages</p>'
        f'<div class="dateline lab"><span>{E(en_date(day))}</span><span lang="kn">{kn_date(day)}</span><span>{n} pages, about twenty minutes</span></div></header>\n'
        f'<nav class="nav" aria-label="Pages"><div class="wrap nav-in"><div class="pills">{P.pills()}</div>'
        '<div class="tools"><button class="tbtn" id="size-down" type="button" aria-label="Smaller text">A&minus;</button><button class="tbtn" id="size-up" type="button" aria-label="Larger text">A+</button>'
        f'<a class="btn share" id="wa-share" href="#" target="_blank" rel="noopener" data-url="{PUBLIC_URL}">WhatsApp</a></div></div></nav>\n'
        f'<main>{P.render_pages()}</main>\n'
        '<footer class="wrap colo"><b>Kullangal Vaarte</b>'
        f'<p>Edition No. {edno}, built {E(en_date(day))}. News and sports facts come from the sources named under each item, gathered by web search and rewritten in our own words. Weather is from Open-Meteo.com (CC BY 4.0). Sunrise, sunset and moon phase are calculated. Plant and feature photographs are from Wikimedia Commons with credits under each. The two serial novels, the puzzles, the comic drawings and the jokes are written or made for this paper; all people and companies in the serials are invented. Old illustrations on the Tales page are credited under them.</p>'
        '<p>A new edition replaces this one each morning.</p></footer>\n'
        f'<script>{js}</script>')
    doc = doc.replace("<main>", '<main data-month="' + day.strftime("%Y-%m") + '">')
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
    ctx = dict(news=load("news.json"), garden=load("garden.json"), jokes=load("jokes.json"), feats=load("features.json"), priv=load("private.json"))
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
    tp = Paper(day, False)
    ctx["tales"] = tales_page(tp)
    ctx["feature"] = feature_page(tp, ctx["feats"])
    for private in (True, False):
        doc, t1, t2 = assemble(day, private, ctx)
        path = outs["private" if private else "public"]
        if not private:
            bad = [w for w in ("mail.google", "gmail", "@gmail", "miniTV", "Payment declined", "Outskill", "pradyumna") if w.lower() in doc.lower()]
            assert not bad, f"private content leaked into the shareable edition: {bad}"
        open(path, "w", encoding="utf-8").write(doc)
        print(("private" if private else "public"), path, round(len(doc) / 1e6, 2), "MB")
    print("Tale:", t1)


if __name__ == "__main__":
    main()
