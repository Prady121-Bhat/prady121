#!/usr/bin/env python3
"""Notices for the Local page and the "Send us your news" box (used by build_paper.py).

Notices come from kullangal_notices.json and, if kullangal_config.json has a sheet_csv_url, from
that published Google Sheet (CSV columns: title, text, place, date_from, date_to, approved).
Only notices with approved = true/yes whose dates include today are shown. Everything typed by
readers is HTML-escaped and length-limited. With none, an empty-state line is shown.
"""
import csv, datetime, html, io, json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape
EMPTY = "No notices for today. If something is happening in Kullangal or nearby, send it in."
TEMPLATE = ("Kullangal Vaarte notice\nWhat:\nWhere:\nWhen (date and time):\nContact for questions (optional):")


def load_json(name):
    try:
        return json.load(open(os.path.join(HERE, name), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "approved")


def day(v):
    try:
        return datetime.date.fromisoformat(str(v).strip())
    except ValueError:
        return None


def sheet_rows(url):
    if not url:
        return []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KullangalVaarte/1.0"})
        text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8-sig")
        return [{(k or "").strip().lower(): (v or "") for k, v in r.items()} for r in csv.DictReader(io.StringIO(text))]
    except Exception as e:  # sheet unreachable: use the JSON file only and say so
        print("Sheet not read:", e, file=sys.stderr)
        return []


def todays(rows, d):
    out = []
    for r in rows:
        if not truthy(r.get("approved")):
            continue
        a, b = day(r.get("date_from")), day(r.get("date_to") or r.get("date_from"))
        if not a or not b or not (a <= d <= b):
            continue
        title, text = (r.get("title") or "").strip()[:120], (r.get("text") or "").strip()[:500]
        if title and text:
            out.append(dict(title=title, text=text, place=(r.get("place") or "").strip()[:60]))
    return out


def notices_html(items):
    if not items:
        return f'<p class="empty">{E(EMPTY)}</p>'
    return "".join(f'<div class="note"><h4>{E(n["title"])}</h4>'
                   + (f'<span class="place">{E(n["place"])}</span>' if n["place"] else "")
                   + f'<p>{E(n["text"])}</p></div>' for n in items)


def send_html(cfg):
    btns = []
    if str(cfg.get("form_url", "")).startswith("https://"):
        btns.append(f'<a class="btn pri" href="{E(cfg["form_url"], quote=True)}" target="_blank" rel="noopener">Fill the form</a>')
    num = re.sub(r"\D", "", cfg.get("whatsapp_number") or "")
    if num:
        btns.append(f'<a class="btn" href="https://wa.me/{num}?text={urllib.parse.quote(TEMPLATE)}" target="_blank" rel="noopener">Send on WhatsApp</a>')
    if not btns:
        return '<p class="empty">The submission form is being set up. Until it opens, the editor cannot take notices.</p>'
    return ('<pre id="tpl-text">' + E(TEMPLATE) + '</pre><div class="btns">' + "".join(btns)
            + '<button class="btn" type="button" id="copy-tpl">Copy the template</button></div>'
            '<p class="prog">Every notice is read by the editor before it is printed.</p>')
