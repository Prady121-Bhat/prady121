#!/usr/bin/env python3
"""Make the shareable edition: drops the personal Desk and Classifieds sections from the private page."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
s = re.sub(r'<div class="notice">.*?</div>\s*(?=<div class="front">)', '', s, flags=re.S)
s = re.sub(r'<section class="sec" id="desk".*?</section>\s*', '', s, flags=re.S)
s = re.sub(r'<section class="sec" id="classifieds".*?</section>\s*', '', s, flags=re.S)
s = re.sub(r'\s*<li><b>[CD]</b><div><a href="#(desk|classifieds)">.*?</li>', '', s)
s = re.sub(r'\s*<a href="#desk">.*?</a>', '', s)
s = re.sub(r'\s*<a href="#classifieds">.*?</a>', '', s)
s = s.replace('<a href="#garden"><b>E</b>', '<a href="#garden"><b>C</b>')
s = s.replace('<li><b>E</b><div><a href="#garden">', '<li><b>C</b><div><a href="#garden">')
s = s.replace('<span class="letter">E</span>', '<span class="letter">C</span>')
s = s.replace('section E', 'section C').replace('Six sections', 'Four sections')
s = s.replace('<a href="#tales"><b>F</b>', '<a href="#tales"><b>D</b>')
s = s.replace('<li><b>F</b><div><a href="#tales">', '<li><b>D</b><div><a href="#tales">')
s = s.replace('<span class="letter">F</span>', '<span class="letter">D</span>')
s = s.replace('The coast, your inbox and the garden', 'The coast and the garden')
s = s.replace('from your Gmail and the sources', 'from the sources')
open(dst, "w", encoding="utf-8").write(s)
