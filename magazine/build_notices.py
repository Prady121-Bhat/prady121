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
EMPTY = "No reader notices today. If something is happening in Kullangal or nearby, send it in."
NOT_OPEN = ("Reader notices are not open yet. Until the form is ready the editor cannot take notices, "
            "so please do not send them anywhere for now.")
# Google Form columns carry the question text; these aliases map them to our fields
ALIASES = dict(
    title=("title", "heading", "what", "notice", "headline"),
    text=("text", "details", "description", "more details", "notice details"),
    place=("place", "where", "location", "village", "town"),
    date_from=("date_from", "date", "when", "from", "event date", "date of event"),
    date_to=("date_to", "to", "until", "last date", "last day", "show until"),
    approved=("approved", "ok", "editor", "editor approval"),
)
TEMPLATE = ("Kullangal Vaarte notice\nWhat:\nWhere:\nWhen (date and time):\nContact for questions (optional):")


def load_json(name):
    try:
        return json.load(open(os.path.join(HERE, name), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "approved")


def day(v):
    """ISO (2026-10-05) or day/month/year (5/10/2026, 05-10-2026, 5 Oct 2026); None otherwise."""
    v = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y", "%d/%m/%y"):
        try:
            return datetime.datetime.strptime(v[:20] if fmt != "%Y-%m-%d" else v[:10], fmt).date()
        except ValueError:
            continue
    return None


def pick(row, field):
    """First non-empty cell whose header (lower-cased, question text allowed) starts with an alias."""
    for head, val in row.items():
        h = head.strip().lower()
        if val and any(h == a or h.startswith(a + " ") or h.startswith(a + ":") or h.startswith(a + "(") for a in ALIASES[field]):
            return val
    return ""


def sheet_rows(url):
    if not url:
        return []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KullangalVaarte/1.0"})
        text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8-sig")
        return [dict(r) for r in csv.DictReader(io.StringIO(text))]
    except Exception as e:  # sheet unreachable: use the JSON file only and say so
        print("Sheet not read:", e, file=sys.stderr)
        return []


def todays(rows, d):
    out = []
    for r in rows:
        r = {(k or ""): (v or "") for k, v in r.items()}
        if not truthy(pick(r, "approved")):
            continue
        a = day(pick(r, "date_from"))
        b = day(pick(r, "date_to")) or a
        if not a or not b or not (a <= d <= b):
            continue
        title, text = pick(r, "title").strip()[:120], pick(r, "text").strip()[:500]
        if title and not text:
            title, text = title[:60], title
        if title and text:
            out.append(dict(title=title, text=text, place=pick(r, "place").strip()[:60]))
    return out


def notices_html(items):
    if not items:
        return f'<p class="empty">{E(EMPTY)}</p>'
    return "".join(f'<div class="note"><h4>{E(n["title"])}</h4>'
                   + (f'<span class="place">{E(n["place"])}</span>' if n["place"] else "")
                   + f'<p>{E(n["text"])}</p></div>' for n in items)


def is_open(cfg):
    return str(cfg.get("form_url", "")).startswith("https://") or bool(re.sub(r"\D", "", cfg.get("whatsapp_number") or ""))


def send_html(cfg):
    btns = []
    if str(cfg.get("form_url", "")).startswith("https://"):
        btns.append(f'<a class="btn pri" href="{E(cfg["form_url"], quote=True)}" target="_blank" rel="noopener">Fill the form</a>')
    num = re.sub(r"\D", "", cfg.get("whatsapp_number") or "")
    if num:
        btns.append(f'<a class="btn" href="https://wa.me/{num}?text={urllib.parse.quote(TEMPLATE)}" target="_blank" rel="noopener">Send on WhatsApp</a>')
    if not btns:
        return f'<p class="empty">{E(NOT_OPEN)}</p>'
    return ('<pre id="tpl-text">' + E(TEMPLATE) + '</pre><div class="btns">' + "".join(btns)
            + '<button class="btn" type="button" id="copy-tpl">Copy the template</button></div>'
            '<p class="prog">Every notice is read by the editor before it is printed.</p>')
