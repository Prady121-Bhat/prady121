#!/usr/bin/env python3
"""One-off: remove the anime (Screen) section and re-letter the remaining sections."""
import re, sys


def edit(s):
    s = re.sub(r'<section class="sec" id="screen".*?</section>\s*', '', s, flags=re.S)
    s = re.sub(r'\s*<a href="#screen">.*?</a>', '', s)
    s = re.sub(r'\s*<li><b>C</b><div><a href="#screen">.*?</li>', '', s)
    for a, b in [
        ('<a href="#desk"><b>D</b>', '<a href="#desk"><b>C</b>'),
        ('<a href="#classifieds"><b>E</b>', '<a href="#classifieds"><b>D</b>'),
        ('<a href="#garden"><b>F</b>', '<a href="#garden"><b>E</b>'),
        ('<span class="letter">D</span><h2 id="h-desk">', '<span class="letter">C</span><h2 id="h-desk">'),
        ('<span class="letter">E</span><h2 id="h-class">', '<span class="letter">D</span><h2 id="h-class">'),
        ('<span class="letter">F</span><h2 id="h-garden">', '<span class="letter">E</span><h2 id="h-garden">'),
        ('<li><b>D</b><div><a href="#desk">', '<li><b>C</b><div><a href="#desk">'),
        ('<li><b>E</b><div><a href="#classifieds">', '<li><b>D</b><div><a href="#classifieds">'),
        ('<li><b>F</b><div><a href="#garden">', '<li><b>E</b><div><a href="#garden">'),
        ('Read in section D', 'Read in section C'),
        ('Care notes in section F', 'Care notes in section E'),
        ('Anime, the inbox, the coast and the garden, edited into one morning read',
         'The coast, your inbox and the garden, edited into one morning read'),
        ('Six sections, about ten minutes', 'Five sections, about ten minutes'),
    ]:
        assert a in s, a
        s = s.replace(a, b)
    mid = '''<article class="mid stack">
        <div>
          <span class="kicker">Coast &middot; Udupi</span>
          <h3 class="hl-1" style="margin-top:8px">Two members of a Uttar Pradesh gang arrested in Udupi burglary case</h3>
          <p class="deck">Two members of a gang from Uttar Pradesh were arrested in a house burglary case.</p>
        </div>
        <div class="body drop rule-t">
          <p>Two members of a gang from Uttar Pradesh were arrested in a house burglary case in Udupi, reported one day ago.</p>
          <p><a href="#coast" class="by">More stories in section B</a></p>
        </div>
        <div class="rule-t">
          <span class="kicker">Culture &middot; Palimar</span>
          <h3 class="hl-2" style="margin-top:6px">A Konkani film comes to Palimar on 5 October</h3>
          <p class="body" style="margin-top:8px">'Bapache Putache Navim' is scheduled to screen in Palimar. If you want a quiet weekend plan, this is the one on the calendar.</p>
        </div>
      </article>'''
    s = re.sub(r'<article class="mid stack">.*?</article>', lambda m: mid, s, count=1, flags=re.S)
    brief = '''<ul class="brief-list">
            <li><h4>Four cars damaged at Katapady</h4><p>Four cars were damaged in a serial accident at Katapady, Udupi, four days ago.</p></li>
            <li><h4>Youth drug awareness campaign</h4><p>Srinivas University and IPSLM ran a 'Nasha Mukta Yuva' campaign in Mangaluru.</p></li>
          </ul>'''
    s = re.sub(r'<ul class="brief-list">.*?</ul>', lambda m: brief, s, count=1, flags=re.S)
    s = s.replace('<li><p><span class="place">Palimar</span>Konkani film \'Bapache Putache Navim\' screens on 5 October.</p></li>', '')
    s = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com/css2\?family=Noto\+Sans\+JP[^>]*>\s*', '', s)
    return s


if __name__ == "__main__":
    for f in sys.argv[1:]:
        text = edit(open(f, encoding="utf-8").read())
        open(f, "w", encoding="utf-8").write(text)
