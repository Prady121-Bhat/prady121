"""Pages for the daily Bhagavad Gita verse and the Sanskrit course.

Sanskrit is authored in Devanagari (the standard text of the verses) and printed in Kannada script,
which maps one to one onto Devanagari, so the whole paper stays in Kannada script.
In lesson text, Sanskrit is marked {{like this}}.
"""
import datetime, html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
START = datetime.date(2026, 10, 5)  # day one of the Gita cycle and of the Sanskrit course
E = html.escape
KN_DIGITS = str.maketrans("0123456789", "೦೧೨೩೪೫೬೭೮೯")


def kd(x):
    return str(x).translate(KN_DIGITS)


def to_kn(text):
    """Devanagari to Kannada script. The two blocks line up at an offset of 0x380."""
    out = []
    for ch in text:
        c = ord(ch)
        if ch == "ँ":      # candrabindu: Kannada has none, an anusvara is the usual choice
            out.append("ಂ")
        elif 0x0902 <= c <= 0x094d or 0x0960 <= c <= 0x0963:
            out.append(chr(c + 0x380))
        elif ch == "ऽ":
            out.append("ಽ")
        elif ch == "॥":
            out.append("||")
        elif ch == "।":
            out.append("|")
        else:
            out.append(ch)
    return "".join(out)


def inline(text):
    """Escape text; Sanskrit spans {{...}} are converted to Kannada script and styled."""
    parts = re.split(r"\{\{(.*?)\}\}", text)
    res = []
    for i, p in enumerate(parts):
        res.append(f'<span class="sa" lang="sa">{E(to_kn(p))}</span>' if i % 2 else E(p).replace("\n", "<br>"))
    return "".join(res)


def _load(name):
    with open(os.path.join(HERE, "content", name), encoding="utf-8") as f:
        return json.load(f)


CHAPTERS = ["ಅರ್ಜುನವಿಷಾದಯೋಗ", "ಸಾಂಖ್ಯಯೋಗ", "ಕರ್ಮಯೋಗ", "ಜ್ಞಾನಕರ್ಮಸಂನ್ಯಾಸಯೋಗ", "ಕರ್ಮಸಂನ್ಯಾಸಯೋಗ", "ಧ್ಯಾನಯೋಗ", "ಜ್ಞಾನವಿಜ್ಞಾನಯೋಗ",
            "ಅಕ್ಷರಬ್ರಹ್ಮಯೋಗ", "ರಾಜವಿದ್ಯಾರಾಜಗುಹ್ಯಯೋಗ", "ವಿಭೂತಿಯೋಗ", "ವಿಶ್ವರೂಪದರ್ಶನಯೋಗ", "ಭಕ್ತಿಯೋಗ", "ಕ್ಷೇತ್ರಕ್ಷೇತ್ರಜ್ಞವಿಭಾಗಯೋಗ",
            "ಗುಣತ್ರಯವಿಭಾಗಯೋಗ", "ಪುರುಷೋತ್ತಮಯೋಗ", "ದೈವಾಸುರಸಂಪದ್ವಿಭಾಗಯೋಗ", "ಶ್ರದ್ಧಾತ್ರಯವಿಭಾಗಯೋಗ", "ಮೋಕ್ಷಸಂನ್ಯಾಸಯೋಗ"]


def verse_text():
    """All 701 verses in order, as {ch, v, speaker, sa}: the Sanskrit text of the Gita (Devanagari)."""
    return _load("gita_text.json")


def study():
    """Kannada study notes keyed 'ch.v' (content/gita/chNN.json), written a few days ahead of the paper."""
    out = {}
    d = os.path.join(HERE, "content", "gita")
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            ch = int(f[2:4])
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                for v, e in json.load(fh).items():
                    out[f"{ch}.{v}"] = e
    return out


def verse_for(day):
    vs = verse_text()
    n = (day - START).days % len(vs)
    return vs[n], vs[(n + 1) % len(vs)], n + 1


def missing_study(day):
    v, _, _ = verse_for(day)
    return f"{v['ch']}.{v['v']}" not in study()


def lessons():
    return _load("sanskrit_1.json") + _load("sanskrit_2.json")


def lesson_for(day):
    ls = lessons()
    d = (day - START).days
    return ls[d % len(ls)], ls[(d - 1) % len(ls)] if d >= 1 else None


def gita_title(day):
    v, _, n = verse_for(day)
    return f"ಅಧ್ಯಾಯ {kd(v['ch'])}, ಶ್ಲೋಕ {kd(v['v'])}"


def lesson_title(day):
    le, _ = lesson_for(day)
    return f"ಪಾಠ {kd(le['n'])}: {le['title']}"


def gita_page(day):
    v, nxt, n = verse_for(day)
    total = len(verse_text())
    key = f"{v['ch']}.{v['v']}"
    st = study().get(key)
    spk = f'<span class="gspk">{E(to_kn(v["speaker"]))}</span>' if v["speaker"] else ""
    lines = "".join(f'<span class="gl">{E(to_kn(l))}{" |" if i == 0 else " ||"}</span>' for i, l in enumerate(v["sa"]))
    head = (f'<p class="deck" style="margin-bottom:14px">ಭಗವದ್ಗೀತೆ ಮೊದಲಿನಿಂದ ಕೊನೆಯವರೆಗೆ, ಪ್ರತಿದಿನ ಒಂದು ಶ್ಲೋಕ: ಮೂಲ ಪಾಠ, ಪದಾರ್ಥ, ಅನುವಾದ ಮತ್ತು ವಿವರಣೆ. '
            f'ಇಂದು {kd(n)}ನೆಯ ಶ್ಲೋಕ ({kd(total)} ರಲ್ಲಿ). ಕುರುಕ್ಷೇತ್ರದ ಯುದ್ಧಭೂಮಿಯಲ್ಲಿ ಕೃಷ್ಣ ಮತ್ತು ಅರ್ಜುನರ ಸಂವಾದ ಇದು.</p>'
            f'<span class="kicker">ಅಧ್ಯಾಯ {kd(v["ch"])} &middot; ಶ್ಲೋಕ {kd(v["v"])} &middot; {E(CHAPTERS[v["ch"] - 1])}</span>'
            f'<div class="shloka" lang="sa">{spk}{lines}</div>')
    if st:
        words = "".join(f'<tr><td class="sa" lang="sa">{E(to_kn(a))}</td><td>{E(b)}</td></tr>' for a, b in st["words"])
        exp = "".join(f"<p>{E(t)}</p>" for t in st["exp"])
        body = (f'<h4 class="sub">ಪದಾರ್ಥ</h4><table class="wtab"><tbody>{words}</tbody></table>'
                f'<h4 class="sub">ಅನುವಾದ</h4><p class="tr">{E(st["tr"])}</p>'
                f'<h4 class="sub">ವಿವರಣೆ</h4><div class="exp">{exp}</div>'
                f'<p class="moral"><span class="lab">ಇಂದಿನ ಚಿಂತನೆ</span> {E(st["think"])}</p>')
    else:
        body = '<p class="tr">ಈ ಶ್ಲೋಕದ ಪದಾರ್ಥ ಮತ್ತು ವಿವರಣೆ ಇನ್ನೂ ಸಿದ್ಧವಾಗಿಲ್ಲ; ಅವು ಮುಂದಿನ ಸಂಚಿಕೆಗಳಲ್ಲಿ ಸೇರುತ್ತವೆ. ಮೂಲ ಶ್ಲೋಕವನ್ನು ಪಠಿಸಿ.</p>'
    foot = (f'<p class="wxsrc" style="margin-top:14px">ನಾಳೆಯ ಶ್ಲೋಕ: ಅಧ್ಯಾಯ {kd(nxt["ch"])}, ಶ್ಲೋಕ {kd(nxt["v"])}. ಮೂಲ ಪಾಠ ಪ್ರಚಲಿತ ಪಾಠದಂತೆ (ಈ ಸಂಖ್ಯಾಕ್ರಮದಲ್ಲಿ ಒಟ್ಟು {kd(total)} ಶ್ಲೋಕಗಳು); ಪದಾರ್ಥ, ಅನುವಾದ ಮತ್ತು ವಿವರಣೆ ನಮ್ಮದೇ ಮಾತುಗಳಲ್ಲಿ. '
            'ವ್ಯಾಖ್ಯಾನಕಾರರ ನಡುವೆ ಅರ್ಥಭೇದಗಳು ಇರಬಹುದು; ಹೆಚ್ಚಿನ ಅಧ್ಯಯನಕ್ಕೆ ಗುರುಗಳನ್ನು ಅಥವಾ ಮಾನ್ಯ ವ್ಯಾಖ್ಯಾನ ಗ್ರಂಥಗಳನ್ನು ನೋಡಿ.</p>')
    return f'<article class="gita" lang="kn">{head}{body}{foot}</article>'


def _table(t):
    head = "".join(f"<th>{E(h)}</th>" for h in t["head"])
    rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in t["rows"])
    return f'<div class="stab-wrap"><table class="stab"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def sanskrit_page(day):
    le, prev = lesson_for(day)
    intro = "".join('<p class="%s">%s</p>' % ("sloka" if ("{{" in t and "\n" in t) else "", inline(t)) for t in le["intro"])
    qs = "".join(f"<li>{inline(p['q'])}</li>" for p in le["practice"])
    ans = ""
    if prev:
        a = "".join(f"<li>{inline(p['a'])}</li>" for p in prev["practice"])
        ans = (f'<div class="yest" lang="kn"><h3 class="sub">ನಿನ್ನೆಯ ಅಭ್ಯಾಸದ ಉತ್ತರಗಳು (ಪಾಠ {kd(prev["n"])})</h3>'
               f'<ol class="sans">{a}</ol></div>')
    return (f'<article class="sanskrit" lang="kn"><p class="deck" style="margin-bottom:14px">ಸಂಸ್ಕೃತ ಕಲಿಕೆ: ಪ್ರತಿದಿನ ಒಂದು ಸಣ್ಣ ಪಾಠ, ಮೂವತ್ತು ದಿನಗಳ ಕ್ರಮದಲ್ಲಿ. '
            'ಸಂಸ್ಕೃತವನ್ನು ಕನ್ನಡ ಲಿಪಿಯಲ್ಲೇ ಬರೆದಿದೆ. ಅಭ್ಯಾಸಗಳನ್ನು ಕಾಗದ-ಪೆನ್ಸಿಲ್‌ನಲ್ಲಿ ಮಾಡಿ; ಉತ್ತರಗಳು ನಾಳೆಯ ಸಂಚಿಕೆಯಲ್ಲಿ.</p>'
            f'<span class="kicker">ಪಾಠ {kd(le["n"])} / {kd(len(lessons()))}</span><h3 class="hl2" style="margin-top:6px">{E(le["title"])}</h3>'
            f'<div class="lesson">{intro}</div>{_table(le["table"])}'
            f'<h4 class="sub">ಇಂದಿನ ಅಭ್ಯಾಸ</h4><ol class="sans">{qs}</ol>'
            f'{ans}</article>')
