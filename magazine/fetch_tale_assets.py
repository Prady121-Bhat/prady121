#!/usr/bin/env python3
"""One-off: download the public-domain / CC0 illustrations used in the Tales section into tales_assets/."""
import html, io, json, os, re, sys, urllib.parse
from PIL import Image
from update_plant_photos import fetch, API

FILES = {
    "tortoise1": "Contes de Jataka, La tortue bavarde - 1.jpg",
    "tortoise2": "Contes de Jataka, La tortue bavarde - 2.jpg",
    "camel": '"The Attack on the Camel by the Lion, Crow, Wolf, and Jackal", Folio from a Kalila wa Dimna MET DP300742.jpg',
}
os.makedirs("tales_assets", exist_ok=True)
meta = {}
for k, f in FILES.items():
    q = dict(action="query", titles="File:" + f, prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=1000, format="json")
    d = json.loads(fetch(API + "?" + urllib.parse.urlencode(q)))
    i = list(d["query"]["pages"].values())[0]["imageinfo"][0]
    m = i["extmetadata"]
    url = i["thumburl"].replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/").split("?")[0]
    im = Image.open(io.BytesIO(fetch(url))).convert("RGB")
    w = 640 if k == "camel" else 900
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    im.save(f"tales_assets/{k}.jpg", quality=76, optimize=True)
    artist = html.unescape(re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip())
    meta[k] = dict(file=f, artist=artist or None, lic=m["LicenseShortName"]["value"],
                   page="https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(f.replace(" ", "_")), size=im.size)
    print(k, meta[k])
json.dump(meta, open("tales_assets/meta.json", "w"), indent=1)
