#!/usr/bin/env python3
"""One-off: add the Tales section (F) to the template and the private page."""
import sys

CSS = """/* Tales */
.tales-intro { margin-bottom: 22px; }
.tales { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 480px), 1fr)); gap: 34px 0; }
.tale { padding: 0 22px; border-left: 1px solid var(--rule); display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.tale:first-child { padding-left: 0; border-left: 0; }
.tale:last-child { padding-right: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.panel { margin: 0; border: 2px solid var(--ink); background: #fff; display: flex; flex-direction: column; min-width: 0; }
.panel svg { display: block; width: 100%; height: auto; }
.panel figcaption { padding: 6px 8px; font: 400 13.5px/1.38 var(--text); border-top: 2px solid var(--ink); background: var(--paper); flex: 1; }
.panel figcaption b { font: 900 15px/1 var(--head); color: var(--red); margin-right: 6px; }
.moral { border: 1px solid var(--rule); padding: 8px 12px; font: italic 500 17px/1.35 var(--head); }
.moral .lab { font-style: normal; color: var(--red); margin-right: 8px; }
.plate { margin: 0; }
.plate img { width: 100%; height: auto; border: 1px solid var(--rule); }
.plate figcaption { font: 500 12.5px/1.35 var(--label); letter-spacing: .06em; color: var(--ink-2); padding-top: 4px; }
.plate figcaption a { color: inherit; }
@media (max-width: 960px) { .tale { padding: 0; border-left: 0; } .tale + .tale { border-top: 4px solid var(--rule); padding-top: 20px; } }
@media (max-width: 520px) { .panels { grid-template-columns: minmax(0, 1fr); } }

"""

SECTION = """  <section class="sec" id="tales" aria-labelledby="h-tales">
    <div class="sec-head"><span class="letter">F</span><h2 id="h-tales">Tales</h2><span class="lab">One episode a day &middot; Panchatantra and Jataka</span></div>
    <p class="guide-intro">Two old Indian story books, one episode of each every morning, drawn as four panels with the moral at the end.</p>
<!--tales:start--><!--tales:end-->
    <p class="srcs" style="margin-top:22px"><span class="by">The stories are traditional and in the public domain, retold for this paper. The four-panel drawings are original. Older illustrations are credited under their episode.</span></p>
  </section>

  """

for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read()
    assert "/* Colophon */" in s and '<footer class="colophon">' in s
    s = s.replace("/* Colophon */", CSS + "/* Colophon */", 1)
    s = s.replace('<footer class="colophon">', SECTION + '<footer class="colophon">', 1)
    s = s.replace('<a href="#garden"><b>E</b>Garden</a>', '<a href="#garden"><b>E</b>Garden</a>\n    <a href="#tales"><b>F</b>Tales</a>', 1)
    idx = '<li><b>E</b><div><a href="#garden">Garden</a>'
    i = s.index(idx)
    j = s.index("</li>", i) + 5
    s = s[:j] + '\n            <li><b>F</b><div><a href="#tales">Tales</a><span>Panchatantra and Jataka, an episode a day</span></div></li>' + s[j:]
    s = s.replace("Five sections, about ten minutes", "Six sections, about ten minutes")
    open(f, "w", encoding="utf-8").write(s)
