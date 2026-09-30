#!/usr/bin/env python3
"""Make the shareable edition: drops the personal Desk and Classifieds sections from the private page."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
s = re.sub(r'<div class="notice">.*?</div>\s*(?=<div class="front">)', '', s, flags=re.S)
s = re.sub(r'<section class="sec" id="desk".*?</section>\s*', '', s, flags=re.S)
s = re.sub(r'<section class="sec" id="classifieds".*?</section>\s*', '', s, flags=re.S)
s = re.sub(r'\s*<a href="#desk">.*?</a>', '', s)
s = re.sub(r'\s*<a href="#classifieds">.*?</a>', '', s)
s = re.sub(r'\s*<li><b>[DE]</b><div>.*?</div></li>', '', s)
s = s.replace('<b>F</b>', '<b>D</b>').replace('<span class="letter">F</span>', '<span class="letter">D</span>')
s = s.replace('section F', 'section D').replace('Six sections', 'Four sections')
s = s.replace('from your Gmail and the sources', 'from the sources')
open(dst, "w", encoding="utf-8").write(s)
