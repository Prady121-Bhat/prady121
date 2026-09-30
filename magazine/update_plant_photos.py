#!/usr/bin/env python3
"""Pick a fresh real photo per plant from Wikimedia Commons and embed it in the magazine HTML.

Usage: update_plant_photos.py PAGE.html [YYYY-MM-DD]

The photo for each plant is chosen from Commons search results by date, so it changes daily.
Only photographs are used: JPEG files with a CC / public-domain licence, and anything that
looks like a drawing, plate, herbarium sheet or painting is skipped.
Images are embedded as data: URIs because the artifact page cannot load remote images.
"""
import base64, datetime, html, io, json, re, sys, time, urllib.parse, urllib.request
from PIL import Image

UA = "KullangalVaarteMagazine/1.0 (anivaletest@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
PLANTS = {  # heading in the page -> Commons search terms
    "Udupi Mallige": ["Jasminum sambac flower", "Jasminum sambac"],
    "Aboli": ["Crossandra infundibuliformis flower", "Crossandra infundibuliformis"],
    "Hibiscus": ["Hibiscus rosa-sinensis flower", "Hibiscus rosa-sinensis"],
    "Tulsi": ["Ocimum tenuiflorum", "Holy basil Ocimum tenuiflorum plant"],
    "Curry leaf": ["Murraya koenigii leaves", "Murraya koenigii"],
    "Monstera": ["Monstera deliciosa leaf", "Monstera deliciosa plant"],
    "Canna lily": ["Canna indica flower", "Canna indica"],
}
BAD = re.compile(r"drawing|illustration|plate|herbarium|specimen|painting|lithograph|engraving|"
                 r"botanical|sketch|diagram|map|logo|icon|stamp|seed|fruit\b|book|scan|pressed", re.I)
OKLIC = re.compile(r"^(CC0|CC BY|CC BY-SA|Public domain|PD)", re.I)


def fetch(url, tries=6):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40).read()
        except Exception as e:
            print("retry:", e, file=sys.stderr)
            time.sleep(4 * (i + 1))
    raise RuntimeError("could not fetch " + url)


def candidates(terms):
    seen, out = set(), []
    for term in terms:
        q = dict(action="query", generator="search", gsrsearch=term + " filetype:bitmap", gsrnamespace=6,
                 gsrlimit=30, prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=960, format="json")
        data = json.loads(fetch(API + "?" + urllib.parse.urlencode(q)))
        for p in data.get("query", {}).get("pages", {}).values():
            i = p["imageinfo"][0]
            m = i["extmetadata"]
            lic = m.get("LicenseShortName", {}).get("value", "")
            title = p["title"]
            if title in seen or i["mime"] != "image/jpeg" or i["width"] < 1200 or i["height"] < 900:
                continue
            cats = m.get("Categories", {}).get("value", "")
            if BAD.search(title) or BAD.search(cats) or not OKLIC.match(lic):
                continue
            seen.add(title)
            artist = html.unescape(re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()) or "Unknown author"
            out.append(dict(title=title, thumb=i["thumburl"], lic=lic, artist=artist[:60],
                            page="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))))
        time.sleep(2)
    out.sort(key=lambda c: c["title"])  # stable order so the daily index is repeatable
    return out


def photo(c):
    # thumb.wikimedia.org is not reachable from every network; upload.wikimedia.org serves the same path.
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


def figure(name, c, uri):
    credit = (f'Photo: {html.escape(c["artist"])}, <a href="{c["page"]}" target="_blank" rel="noopener">'
              f'Wikimedia Commons</a>, {html.escape(c["lic"])}')
    return (f'<figure class="photo"><img src="{uri}" alt="{html.escape(name)}, photograph" width="800" height="600" '
            f'loading="lazy"><figcaption>{credit}</figcaption></figure>')


def main():
    page = sys.argv[1]
    day = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    src = open(page, encoding="utf-8").read()
    src = re.sub(r'<figure class="photo">.*?</figure>', "", src, flags=re.S)
    for name, terms in PLANTS.items():
        cands = candidates(terms)
        if not cands:
            print("no photo for", name); continue
        c = cands[day.toordinal() % len(cands)]
        print(f"{name}: {c['title']} ({c['lic']}, {c['artist']}) [{len(cands)} candidates]")
        fig = figure(name, c, photo(c))
        marker = f'<h3>{name}</h3>'
        head = re.search(r'<article class="plant[^"]*"><div class="plant-body">' + re.escape(marker), src)
        if not head:
            print("card not found for", name); continue
        pos = head.start() + len('<article class="plant')
        pos = src.index('>', pos) + 1
        src = src[:pos] + fig + src[pos:]
    open(page, "w", encoding="utf-8").write(src)


if __name__ == "__main__":
    main()
