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


def verses():
    return _load("gita_1.json") + _load("gita_2.json")


def lessons():
    return _load("sanskrit_1.json") + _load("sanskrit_2.json")


def verse_for(day):
    v = verses()
    return v[(day - START).days % len(v)], v[((day - START).days + 1) % len(v)]


def lesson_for(day):
    ls = lessons()
    d = (day - START).days
    return ls[d % len(ls)], ls[(d - 1) % len(ls)] if d >= 1 else None


def gita_title(day):
    v, _ = verse_for(day)
    return f"ಅಧ್ಯಾಯ {kd(v['ch'])}, ಶ್ಲೋಕ {kd(v['v'])}"


def lesson_title(day):
    le, _ = lesson_for(day)
    return f"ಪಾಠ {kd(le['n'])}: {le['title']}"


def gita_page(day):
    v, nxt = verse_for(day)
    lines = "".join(f'<span class="gl">{E(to_kn(l))}</span>' for l in v["sa"])
    words = "".join(f'<tr><td class="sa" lang="sa">{E(to_kn(a))}</td><td>{E(b)}</td></tr>' for a, b in v["words"])
    exp = "".join(f"<p>{E(t)}</p>" for t in v["exp"])
    spk = "ಶ್ರೀಕೃಷ್ಣನು ಅರ್ಜುನನಿಗೆ ಹೇಳಿದ ಮಾತು" if v["speaker"] == "ಶ್ರೀಕೃಷ್ಣ" else "ಸಂಜಯನು ಧೃತರಾಷ್ಟ್ರನಿಗೆ ಹೇಳಿದ ಮಾತು"
    return (f'<article class="gita" lang="kn"><p class="deck" style="margin-bottom:14px">ಪ್ರತಿದಿನ ಭಗವದ್ಗೀತೆಯ ಒಂದು ಶ್ಲೋಕ: ಮೂಲ ಪಾಠ, ಪದಾರ್ಥ, ಅನುವಾದ ಮತ್ತು ವಿವರಣೆ. '
            'ಗೀತೆಯಲ್ಲಿ ಹದಿನೆಂಟು ಅಧ್ಯಾಯಗಳಿವೆ; ಕುರುಕ್ಷೇತ್ರದ ಯುದ್ಧಭೂಮಿಯಲ್ಲಿ ಕೃಷ್ಣ ಮತ್ತು ಅರ್ಜುನರ ಸಂವಾದ ಇದು.</p>'
            f'<span class="kicker">ಅಧ್ಯಾಯ {kd(v["ch"])} &middot; ಶ್ಲೋಕ {kd(v["v"])} &middot; {E(v["name"])}</span>'
            f'<div class="shloka" lang="sa">{lines}</div><p class="spk">{E(spk)}</p>'
            f'<h4 class="sub">ಪದಾರ್ಥ</h4><table class="wtab"><tbody>{words}</tbody></table>'
            f'<h4 class="sub">ಅನುವಾದ</h4><p class="tr">{E(v["tr"])}</p>'
            f'<h4 class="sub">ವಿವರಣೆ</h4><div class="exp">{exp}</div>'
            f'<p class="moral"><span class="lab">ಇಂದಿನ ಚಿಂತನೆ</span> {E(v["think"])}</p>'
            f'<p class="wxsrc" style="margin-top:14px">ನಾಳೆಯ ಶ್ಲೋಕ: ಅಧ್ಯಾಯ {kd(nxt["ch"])}, ಶ್ಲೋಕ {kd(nxt["v"])}. ಮೂಲ ಪಾಠ ಪ್ರಚಲಿತ ಪಾಠದಂತೆ; ಪದಾರ್ಥ, ಅನುವಾದ ಮತ್ತು ವಿವರಣೆ ನಮ್ಮದೇ ಮಾತುಗಳಲ್ಲಿ. '
            'ವ್ಯಾಖ್ಯಾನಕಾರರ ನಡುವೆ ಅರ್ಥಭೇದಗಳು ಇರಬಹುದು; ಹೆಚ್ಚಿನ ಅಧ್ಯಯನಕ್ಕೆ ಗುರುಗಳನ್ನು ಅಥವಾ ಮಾನ್ಯ ವ್ಯಾಖ್ಯಾನ ಗ್ರಂಥಗಳನ್ನು ನೋಡಿ.</p></article>')


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
