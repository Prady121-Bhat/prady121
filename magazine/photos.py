#!/usr/bin/env python3
"""Real photographs from Wikimedia Commons for plants and features.

photo_for(key, terms, day) picks one licensed JPEG from Commons search results (the pick changes daily),
crops it to 4:3, shrinks it to 800x600 and returns an embedded data: URI and a credit line. Results are
cached in content/cache so a rebuild on the same day does not hit Commons again.
Only photographs: drawings, plates, herbarium sheets and similar are skipped.
"""
import base64, datetime, html, io, json, os, re, sys, time, urllib.parse, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "content", "cache")
UA = "KullangalVaarteMagazine/1.0 (anivaletest@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
BAD = re.compile(r"drawing|illustration|plate|herbarium|specimen|painting|lithograph|engraving|botanical|sketch|"
                 r"diagram|map|logo|icon|stamp|seed|book|scan|pressed|poster|coat of arms|flag", re.I)
OKLIC = re.compile(r"^(CC0|CC BY|CC BY-SA|Public domain|PD)", re.I)


def fetch(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40).read()
        except Exception as e:
            print("retry:", str(e)[:80], file=sys.stderr)
            time.sleep(min(45, 4 * (i + 1)))
    raise RuntimeError("could not fetch " + url)


def candidates(terms, min_w=1200, min_h=800):
    seen, out = set(), []
    for term in terms:
        q = dict(action="query", generator="search", gsrsearch=term + " filetype:bitmap", gsrnamespace=6, gsrlimit=30,
                 prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=960, format="json")
        data = json.loads(fetch(API + "?" + urllib.parse.urlencode(q)))
        for p in data.get("query", {}).get("pages", {}).values():
            i = p["imageinfo"][0]
            m = i["extmetadata"]
            lic = m.get("LicenseShortName", {}).get("value", "")
            title = p["title"]
            if title in seen or i["mime"] != "image/jpeg" or i["width"] < min_w or i["height"] < min_h:
                continue
            cats = m.get("Categories", {}).get("value", "")
            if BAD.search(title) or BAD.search(cats) or not OKLIC.match(lic):
                continue
            seen.add(title)
            artist = html.unescape(re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()) or "Unknown author"
            out.append(dict(title=title, thumb=i["thumburl"], lic=lic, artist=artist[:60],
                            page="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))))
        time.sleep(1.5)
    # prefer files whose name matches the search words best (a basalt-column photo for a basalt search, not a beach shelter)
    def score(c):
        name = re.sub(r"[^a-z0-9 ]", " ", c["title"].lower().replace("'s", ""))
        best = 0.0
        for term in terms:
            toks = [t for t in re.sub(r"[^a-z0-9 ]", " ", term.lower().replace("'s", "")).split() if len(t) > 2 and t != "filetype"]
            if toks:
                best = max(best, sum(1 for t in toks if t in name) / len(toks))
        return best
    for c in out:
        c["score"] = score(c)
    top = max((c["score"] for c in out), default=0)
    out = [c for c in out if c["score"] >= max(0.34, top - 0.25)] or out
    out.sort(key=lambda c: c["title"])
    return out


def by_title(title):
    """One exact Commons file (a title such as 'File:Name.jpg'), or None."""
    q = dict(action="query", titles=title, prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=960, format="json")
    data = json.loads(fetch(API + "?" + urllib.parse.urlencode(q)))
    for p in data.get("query", {}).get("pages", {}).values():
        if "imageinfo" not in p:
            continue
        i = p["imageinfo"][0]
        m = i["extmetadata"]
        lic = m.get("LicenseShortName", {}).get("value", "")
        if i["mime"] != "image/jpeg" or not OKLIC.match(lic):
            continue
        artist = html.unescape(re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()) or "Unknown author"
        return dict(title=p["title"], thumb=i["thumburl"], lic=lic, artist=artist[:60],
                    page="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")))
    return None


def to_uri(c):
    url = c["thumb"].replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/").split("?")[0]
    im = Image.open(io.BytesIO(fetch(url))).convert("RGB")
    w, h = im.size
    if w / h > 4 / 3:
        nw = int(h * 4 / 3); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 3 / 4); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    buf = io.BytesIO()
    im.resize((800, 600), Image.LANCZOS).save(buf, "JPEG", quality=74, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def photo_for(key, terms, day, files=None):
    os.makedirs(CACHE, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
    path = os.path.join(CACHE, f"{slug}-{day.isoformat()}.json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    try:
        cands = []
        for t in (files or []):  # hand-picked files first
            c = by_title(t)
            if c:
                cands.append(c)
        cands = cands or candidates(terms)
    except Exception as e:  # Commons refused or timed out: reuse the newest photo we already hold
        print("Commons unavailable for", key, "-", str(e)[:60], file=sys.stderr)
        cands = []
    if not cands:
        old = sorted((f for f in os.listdir(CACHE) if f.startswith(slug + "-") and f.endswith(".json")), key=lambda f: (not f.endswith("-seed.json"), f))
        return json.load(open(os.path.join(CACHE, old[-1]), encoding="utf-8")) if old else None
    c = cands[day.toordinal() % len(cands)]
    print(f"{key}: {c['title']} ({c['lic']}, {c['artist']}) [{len(cands)} candidates]")
    out = dict(uri=to_uri(c), artist=c["artist"], lic=c["lic"], page=c["page"], title=c["title"])
    json.dump(out, open(path, "w", encoding="utf-8"))
    # keep the cache small: only the last few days
    for f in sorted(os.listdir(CACHE)):
        m = re.search(r"(\d{4}-\d{2}-\d{2})\.json$", f)  # seed files have no date and are kept
        if m and (day - datetime.date.fromisoformat(m.group(1))).days > 3:
            os.remove(os.path.join(CACHE, f))
    return out


def credit_html(p):
    return (f'Photo: {html.escape(p["artist"])}, <a href="{p["page"]}" target="_blank" rel="noopener">Wikimedia Commons</a>, {html.escape(p["lic"])}')
