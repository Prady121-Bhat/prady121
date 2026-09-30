#!/usr/bin/env python3
"""One-off: add reader tools, the Kullangal notices block, the quiz slot and the page script."""
import re, sys

CSS = """/* Reader tools, notices, quiz */
.tools { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; padding-block: 8px; border-bottom: 1px solid var(--hair); }
.tools .lab { color: var(--ink-2); margin-right: 4px; }
.btn { font: 600 13px/1 var(--label); letter-spacing: .12em; text-transform: uppercase; padding: 10px 13px; border: 1px solid var(--ink); background: transparent; color: var(--ink); cursor: pointer; text-decoration: none; display: inline-block; }
.btn:hover { background: var(--ink); color: var(--paper); }
.btn:focus-visible { outline: 3px solid var(--red); outline-offset: 2px; }
.btn.pri { background: var(--red); border-color: var(--red); color: #fff; }
.btn.pri:hover { filter: brightness(.9); }
.chips { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.chips .btn[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.kn { margin-top: 30px; border-top: 4px solid var(--rule); padding-top: 12px; display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 0; }
.kn > * { padding-inline: 22px; min-width: 0; }
.kn > *:first-child { padding-left: 0; }
.kn > *:last-child { padding-right: 0; border-left: 1px solid var(--rule); }
.kn .note { border-left: 4px solid var(--red); padding: 8px 12px; margin-top: 10px; }
.kn .note h4 { font: 700 19px/1.2 var(--head); }
.kn .note p { font-size: 15.5px; margin-top: 4px; }
.kn .empty { color: var(--ink-2); font-style: italic; }
.send-box { display: flex; flex-direction: column; gap: 10px; }
.send-box pre { white-space: pre-wrap; margin: 0; font: 400 14px/1.45 var(--text); background: var(--paper-2); padding: 10px 12px; }
.quiz { margin-top: 30px; border-top: 4px solid var(--rule); padding-top: 12px; }
.q { padding-block: 14px; border-top: 1px solid var(--hair); }
.q:first-of-type { border-top: 0; }
.q h4 { font: 700 19px/1.25 var(--head); margin-bottom: 8px; }
.q .opts { display: flex; flex-wrap: wrap; gap: 8px; }
.q .opts .btn { text-transform: none; letter-spacing: 0; font: 500 15px/1.3 var(--text); text-align: left; }
.q .opts .btn.right { background: var(--green); border-color: var(--green); color: var(--paper); }
.q .opts .btn.wrong { background: var(--red); border-color: var(--red); color: #fff; }
.q .why { margin-top: 8px; font-size: 15px; color: var(--ink-2); }
.score { font: 800 22px/1.2 var(--head); margin-top: 10px; }
.check-li { display: grid; grid-template-columns: 24px minmax(0, 1fr); gap: 10px; }
.check-li input { width: 20px; height: 20px; margin-top: 3px; accent-color: var(--green); }
.check-li.done span { text-decoration: line-through; color: var(--ink-2); }
.prog { font: 600 13px/1 var(--label); letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2); margin-bottom: 6px; }
body { zoom: var(--zoom, 1); }
@media (max-width: 960px) { .kn { grid-template-columns: minmax(0, 1fr); } .kn > * { padding-inline: 0; } .kn > *:last-child { border-left: 0; border-top: 1px solid var(--rule); padding-top: 16px; margin-top: 16px; } }

"""

TOOLS = """<div class="sheet"><div class="tools" role="toolbar" aria-label="Reader tools">
    <span class="lab">Reader tools</span>
    <button class="btn" type="button" id="zoom-out" aria-label="Smaller text">A&minus;</button>
    <button class="btn" type="button" id="zoom-in" aria-label="Larger text">A+</button>
    <button class="btn" type="button" id="theme-toggle">Light / dark</button>
    <a class="btn pri" id="wa-share" href="#" target="_blank" rel="noopener">Share on WhatsApp</a>
  </div></div>

"""

KN = """
    <div class="kn" id="kullangal">
      <div>
        <span class="kicker">Kullangal &amp; nearby &middot; notices for the day</span>
        <!--notices:start--><!--notices:end-->
      </div>
      <aside class="send-box" aria-label="Send your news">
        <h3 class="hl-3">Send us your news</h3>
        <p>Events, lost and found, road works, temple and school notices, shop openings. Send it by 8 pm and it can go in tomorrow's paper.</p>
        <!--send:start--><!--send:end-->
      </aside>
    </div>
"""

QUIZ_SLOT = """<!--quiz:start--><!--quiz:end-->
    """

SCRIPT = r"""<script>
(function () {
  var root = document.documentElement;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  // zoom
  var z = parseFloat(store('kv-zoom')) || 1;
  function setZoom(v) { z = Math.max(.85, Math.min(1.4, v)); root.style.setProperty('--zoom', z); store('kv-zoom', String(z)); }
  setZoom(z);
  var zi = document.getElementById('zoom-in'), zo = document.getElementById('zoom-out');
  if (zi) zi.onclick = function () { setZoom(z + .1); };
  if (zo) zo.onclick = function () { setZoom(z - .1); };
  // theme
  var saved = store('kv-theme');
  if (saved === 'dark' || saved === 'light') root.setAttribute('data-theme', saved);
  var tt = document.getElementById('theme-toggle');
  if (tt) tt.onclick = function () {
    var dark = root.getAttribute('data-theme') === 'dark' || (!root.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next); store('kv-theme', next);
  };
  // share
  var wa = document.getElementById('wa-share');
  if (wa) wa.href = 'https://wa.me/?text=' + encodeURIComponent('Kullangal Vaarte, the daily paper of the Mangaluru and Udupi coast: https://claude.ai/artifact/7voAxG4qkUxsec11FZmraw');
  // coast filter
  var list = document.querySelector('#coast ul');
  if (list) {
    var items = Array.prototype.slice.call(list.querySelectorAll('.story'));
    var places = [];
    items.forEach(function (li) { var p = li.querySelector('.place'); if (p && places.indexOf(p.textContent) < 0) places.push(p.textContent); });
    if (places.length > 1) {
      var bar = document.createElement('div'); bar.className = 'chips'; bar.setAttribute('role', 'group'); bar.setAttribute('aria-label', 'Filter stories by place');
      ['All'].concat(places).forEach(function (name, i) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'btn'; b.textContent = name; b.setAttribute('aria-pressed', i === 0 ? 'true' : 'false');
        b.onclick = function () {
          Array.prototype.forEach.call(bar.children, function (c) { c.setAttribute('aria-pressed', c === b ? 'true' : 'false'); });
          items.forEach(function (li) { var p = li.querySelector('.place'); li.hidden = !(i === 0 || (p && p.textContent === name)); });
        };
        bar.appendChild(b);
      });
      list.parentNode.insertBefore(bar, list);
    }
  }
  // garden checklist
  var lis = document.querySelectorAll('#garden .month li');
  if (lis.length) {
    var box = document.querySelector('#garden .month');
    var prog = document.createElement('div'); prog.className = 'prog'; box.insertBefore(prog, box.querySelector('ul'));
    var key = 'kv-garden-' + (box.textContent.length);
    var done = {}; try { done = JSON.parse(store(key) || '{}') || {}; } catch (e) { done = {}; }
    function update() { var n = 0; lis.forEach(function (li, i) { if (done[i]) n++; }); prog.textContent = n + ' of ' + lis.length + ' done this month'; }
    lis.forEach(function (li, i) {
      var text = li.textContent; li.textContent = ''; li.className = 'check-li' + (done[i] ? ' done' : '');
      var cb = document.createElement('input'); cb.type = 'checkbox'; cb.id = 'gc' + i; cb.checked = !!done[i];
      var sp = document.createElement('span'); sp.textContent = text;
      var lab = document.createElement('label'); lab.htmlFor = cb.id; lab.appendChild(sp);
      cb.onchange = function () { done[i] = cb.checked; li.className = 'check-li' + (cb.checked ? ' done' : ''); store(key, JSON.stringify(done)); update(); };
      li.appendChild(cb); li.appendChild(lab);
    });
    update();
  }
  // quiz
  var qd = document.getElementById('quiz-data');
  var qb = document.getElementById('quiz-body');
  if (qd && qb) {
    var qs = []; try { qs = JSON.parse(qd.textContent); } catch (e) { qs = []; }
    var score = 0, answered = 0, out = document.getElementById('quiz-score');
    qs.forEach(function (q, qi) {
      var wrap = document.createElement('div'); wrap.className = 'q';
      var h = document.createElement('h4'); h.textContent = (qi + 1) + '. ' + q.q; wrap.appendChild(h);
      var opts = document.createElement('div'); opts.className = 'opts';
      var why = document.createElement('p'); why.className = 'why'; why.hidden = true; why.setAttribute('aria-live', 'polite');
      q.a.forEach(function (text, ai) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'btn'; b.textContent = text;
        b.onclick = function () {
          if (wrap.getAttribute('data-done')) return; wrap.setAttribute('data-done', '1');
          answered++; var ok = ai === q.c; if (ok) score++;
          Array.prototype.forEach.call(opts.children, function (c, ci) { c.disabled = true; if (ci === q.c) c.classList.add('right'); else if (c === b) c.classList.add('wrong'); });
          why.hidden = false; why.textContent = (ok ? 'Correct. ' : 'Not quite. ') + (q.w || '');
          if (answered === qs.length && out) out.textContent = 'You scored ' + score + ' out of ' + qs.length + '.';
        };
        opts.appendChild(b);
      });
      wrap.appendChild(opts); wrap.appendChild(why); qb.appendChild(wrap);
    });
  }
  // copy template
  var cp = document.getElementById('copy-tpl');
  if (cp) cp.onclick = function () {
    var t = document.getElementById('tpl-text').textContent;
    try { navigator.clipboard.writeText(t).then(function () { cp.textContent = 'Copied'; }, function () { cp.textContent = 'Select the text and copy'; }); } catch (e) { cp.textContent = 'Select the text and copy'; }
  };
})();
</script>
"""


def apply(s):
    assert "/* Colophon */" in s
    s = s.replace("/* Colophon */", CSS + "/* Colophon */", 1)
    s = s.replace('<nav class="nav" aria-label="Sections">', TOOLS + '<nav class="nav" aria-label="Sections">', 1)
    m = re.search(r'<section class="sec" id="coast".*?(</section>)', s, flags=re.S)
    s = s[:m.start(1)] + KN + "  " + s[m.start(1):]
    marker = '<p class="srcs" style="margin-top:22px">'
    assert marker in s
    s = s.replace(marker, QUIZ_SLOT + marker, 1)
    s = s.replace("</main>", "</main>\n" + SCRIPT, 1)
    return s


if __name__ == "__main__":
    for f in sys.argv[1:]:
        text = apply(open(f, encoding="utf-8").read())
        open(f, "w", encoding="utf-8").write(text)
