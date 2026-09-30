/* Kullangal Vaarte page script: text size, page nav, coast filter, garden checklist, share, and four puzzles.
   Everything works without storage; progress is saved in the browser when it is available. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; }
  }
  function data(id) { var e = document.getElementById(id); if (!e) return null; try { return JSON.parse(e.textContent); } catch (x) { return null; } }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }

  /* ---- text size ---- */
  var size = parseFloat(store('kv-size')) || 100;
  function setSize(v) { size = Math.max(88, Math.min(140, v)); document.documentElement.style.setProperty('--fs', size + '%'); store('kv-size', String(size)); }
  setSize(size);
  var bi = $('#size-up'), bd = $('#size-down');
  if (bi) bi.onclick = function () { setSize(size + 8); };
  if (bd) bd.onclick = function () { setSize(size - 8); };

  /* ---- share (shareable edition link only) ---- */
  var wa = $('#wa-share');
  if (wa) wa.href = 'https://wa.me/?text=' + encodeURIComponent('Kullangal Vaarte, the daily paper of the Mangaluru and Udupi coast: ' + wa.getAttribute('data-url'));

  /* ---- page nav highlight ---- */
  var pills = $$('.pill');
  if ('IntersectionObserver' in window && pills.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          pills.forEach(function (p) { p.classList.toggle('on', p.getAttribute('href') === '#' + e.target.id); });
          var on = $('.pill.on'); if (on && on.scrollIntoView) { var box = on.parentNode; box.scrollLeft = on.offsetLeft - 60; }
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    $$('.page').forEach(function (p) { io.observe(p); });
  }

  /* ---- coast place filter ---- */
  var list = $('#story-list');
  if (list) {
    var items = $$('.story', list), places = [];
    items.forEach(function (li) { var p = li.getAttribute('data-place'); if (p && places.indexOf(p) < 0) places.push(p); });
    if (places.length > 1) {
      var bar = el('div', 'chips'); bar.setAttribute('role', 'group'); bar.setAttribute('aria-label', 'Filter stories by place');
      ['All'].concat(places).forEach(function (name, i) {
        var b = el('button', 'chip', name); b.type = 'button'; b.setAttribute('aria-pressed', i === 0 ? 'true' : 'false');
        b.onclick = function () {
          $$('.chip', bar).forEach(function (c) { c.setAttribute('aria-pressed', c === b ? 'true' : 'false'); });
          items.forEach(function (li) { li.hidden = !(i === 0 || li.getAttribute('data-place') === name); });
        };
        bar.appendChild(b);
      });
      list.parentNode.insertBefore(bar, list);
    }
  }

  /* ---- garden checklist ---- */
  var gl = $$('#garden-list li');
  if (gl.length) {
    var gkey = 'kv-garden-' + (document.body.getAttribute('data-month') || 'm');
    var gdone = {}; try { gdone = JSON.parse(store(gkey) || '{}') || {}; } catch (e) { gdone = {}; }
    var prog = $('#garden-prog');
    var upd = function () { var n = 0; gl.forEach(function (li, i) { if (gdone[i]) n++; }); if (prog) prog.textContent = n + ' of ' + gl.length + ' done this month'; };
    gl.forEach(function (li, i) {
      var text = li.textContent; li.textContent = ''; li.className = 'check' + (gdone[i] ? ' done' : '');
      var cb = el('input'); cb.type = 'checkbox'; cb.id = 'gc' + i; cb.checked = !!gdone[i];
      var lab = el('label'); lab.htmlFor = cb.id; lab.appendChild(el('span', '', text));
      cb.onchange = function () { gdone[i] = cb.checked; li.className = 'check' + (cb.checked ? ' done' : ''); store(gkey, JSON.stringify(gdone)); upd(); };
      li.appendChild(cb); li.appendChild(lab);
    });
    upd();
  }

  /* ---- copy notice template ---- */
  var cp = $('#copy-tpl');
  if (cp) cp.onclick = function () {
    var t = $('#tpl-text').textContent;
    try { navigator.clipboard.writeText(t).then(function () { cp.textContent = 'Copied'; }, function () { cp.textContent = 'Select the text and copy'; }); }
    catch (e) { cp.textContent = 'Select the text and copy'; }
  };

  /* ---- button helper ---- */
  function btn(label, fn, cls) { var b = el('button', 'btn' + (cls ? ' ' + cls : ''), label); b.type = 'button'; b.onclick = fn; return b; }

  /* ================= SUDOKU ================= */
  (function () {
    var host = $('#sudoku'), d = data('pz-sudoku'); if (!host || !d) return;
    var giv = d.puzzle.split('').map(Number), sol = d.solution.split('').map(Number);
    var key = 'kv-sudoku-' + d.day, val = giv.slice(), sel = -1, cells = [], msg = $('#sudoku-msg');
    try { var sv = JSON.parse(store(key) || 'null'); if (sv && sv.length === 81) val = sv.map(function (v, i) { return giv[i] ? giv[i] : v; }); } catch (e) {}
    var grid = el('div', 'sud'); grid.setAttribute('role', 'grid'); grid.setAttribute('aria-label', 'Sudoku grid');
    for (var i = 0; i < 81; i++) {
      (function (i) {
        var c = el('button', 'sc'); c.type = 'button';
        c.onclick = function () { sel = i; paint(); };
        cells.push(c); grid.appendChild(c);
      })(i);
    }
    host.appendChild(grid);
    var pad = el('div', 'pad');
    for (var n = 1; n <= 9; n++) (function (n) { var b = el('button', '', String(n)); b.type = 'button'; b.setAttribute('aria-label', 'Enter ' + n); b.onclick = function () { put(n); }; pad.appendChild(b); })(n);
    var er = el('button', 'w', 'Erase'); er.type = 'button'; er.onclick = function () { put(0); }; pad.appendChild(er);
    host.appendChild(pad);
    var pb = el('div', 'pbtns');
    pb.appendChild(btn('Check', function () { check(true); }));
    pb.appendChild(btn('Hint', hint));
    pb.appendChild(btn('Show answer', function () { val = sol.slice(); save(); paint(); say('Here is the solution. Reset to try again.'); }));
    pb.appendChild(btn('Reset', function () { val = giv.slice(); sel = -1; save(); paint(); say(''); }));
    host.appendChild(pb);
    function say(t) { if (msg) msg.textContent = t; }
    function save() { store(key, JSON.stringify(val)); }
    function put(n) {
      if (sel < 0 || giv[sel]) { if (sel < 0) say('Tap a square first.'); return; }
      val[sel] = n; save(); paint(); check(false);
    }
    function hint() {
      var t = sel >= 0 && !giv[sel] && val[sel] !== sol[sel] ? sel : val.findIndex(function (v, i) { return v !== sol[i]; });
      if (t < 0) { say('Nothing left to hint. It is solved.'); return; }
      sel = t; val[t] = sol[t]; save(); paint(); check(false);
    }
    function check(mark) {
      var wrong = 0, empty = 0;
      val.forEach(function (v, i) { if (!v) empty++; else if (v !== sol[i]) wrong++; });
      cells.forEach(function (c, i) { c.classList.toggle('bad', mark && val[i] && val[i] !== sol[i]); });
      if (!wrong && !empty) say('Solved. Well done.');
      else if (mark) say(wrong ? wrong + ' square' + (wrong > 1 ? 's look' : ' looks') + ' wrong.' : 'No mistakes so far. ' + empty + ' to go.');
    }
    function paint() {
      cells.forEach(function (c, i) {
        var v = val[i]; c.textContent = v || '';
        c.className = 'sc' + (giv[i] ? ' g' : (v ? ' u' : ''));
        c.setAttribute('aria-label', 'Row ' + (Math.floor(i / 9) + 1) + ' column ' + (i % 9 + 1) + (v ? ', ' + v : ', empty'));
        if (sel >= 0) {
          var r = Math.floor(sel / 9), cc = sel % 9, r2 = Math.floor(i / 9), c2 = i % 9;
          if (i === sel) c.classList.add('sel');
          else if (r === r2 || cc === c2 || (Math.floor(r / 3) === Math.floor(r2 / 3) && Math.floor(cc / 3) === Math.floor(c2 / 3))) c.classList.add('pe');
          if (v && val[sel] === v && i !== sel) c.classList.add('same');
        }
      });
    }
    grid.addEventListener('keydown', function (e) {
      if (/^[1-9]$/.test(e.key)) { put(+e.key); e.preventDefault(); }
      else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') { put(0); e.preventDefault(); }
      else if (e.key.indexOf('Arrow') === 0 && sel >= 0) {
        var dr = e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0, dc = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        var r = Math.floor(sel / 9) + dr, c = sel % 9 + dc;
        if (r >= 0 && r < 9 && c >= 0 && c < 9) { sel = r * 9 + c; paint(); cells[sel].focus(); }
        e.preventDefault();
      }
    });
    paint(); check(false);
  })();

  /* ================= CROSSWORD ================= */
  (function () {
    var host = $('#crossword'), d = data('pz-crossword'); if (!host || !d) return;
    var R = d.rows, C = d.cols, g = d.grid, key = 'kv-cross-' + d.day, bar = $('#cw-bar'), msg = $('#cw-msg');
    var letters = []; for (var i = 0; i < R * C; i++) letters.push('');
    try { var sv = JSON.parse(store(key) || 'null'); if (sv && sv.length === R * C) letters = sv; } catch (e) {}
    var num = {}; d.across.concat(d.down).forEach(function (w) { num[w.r + ',' + w.c] = w.n; });
    var isBlock = function (r, c) { return r < 0 || c < 0 || r >= R || c >= C || g[r][c] === '.'; };
    var grid = el('div', 'cw'); grid.style.gridTemplateColumns = 'repeat(' + C + ', minmax(0, 1fr))';
    var cells = {}, inputs = {};
    for (var r = 0; r < R; r++) for (var c = 0; c < C; c++) {
      var cell = el('div', 'cwc' + (isBlock(r, c) ? ' blk' : ''));
      if (!isBlock(r, c)) {
        var inp = el('input'); inp.type = 'text'; inp.maxLength = 1; inp.autocomplete = 'off'; inp.autocapitalize = 'characters'; inp.spellcheck = false;
        inp.setAttribute('aria-label', 'Row ' + (r + 1) + ' column ' + (c + 1));
        inp.setAttribute('data-r', r); inp.setAttribute('data-c', c); inp.value = letters[r * C + c] || '';
        cell.appendChild(inp); inputs[r + ',' + c] = inp;
        if (num[r + ',' + c]) cell.appendChild(el('i', '', String(num[r + ',' + c])));
      }
      cells[r + ',' + c] = cell; grid.appendChild(cell);
    }
    host.appendChild(grid);
    var act = { r: -1, c: -1, dir: 'A' };
    function run(r, c, dir) {
      var dr = dir === 'D' ? 1 : 0, dc = dir === 'A' ? 1 : 0, out = [];
      var rr = r, cc = c; while (!isBlock(rr - dr, cc - dc)) { rr -= dr; cc -= dc; }
      while (!isBlock(rr, cc)) { out.push([rr, cc]); rr += dr; cc += dc; }
      return out;
    }
    function entry(r, c, dir) { var cs = run(r, c, dir); if (cs.length < 2) return null; var s = cs[0]; var list = dir === 'A' ? d.across : d.down; return list.filter(function (w) { return w.r === s[0] && w.c === s[1]; })[0] || null; }
    function paint() {
      Object.keys(cells).forEach(function (k) { cells[k].classList.remove('pe', 'sel'); });
      $$('.clues li').forEach(function (li) { li.classList.remove('on'); });
      if (act.r < 0) { if (bar) bar.innerHTML = '<b>Tap a square</b> to see its clue.'; return; }
      var w = entry(act.r, act.c, act.dir);
      run(act.r, act.c, act.dir).forEach(function (p) { cells[p[0] + ',' + p[1]].classList.add('pe'); });
      cells[act.r + ',' + act.c].classList.add('sel');
      if (w) {
        if (bar) { bar.textContent = ''; var b = el('b', '', w.n + (act.dir === 'A' ? ' ACROSS' : ' DOWN')); bar.appendChild(b); bar.appendChild(document.createTextNode(w.clue + ' (' + w.len + ')')); }
        var li = $('#cl-' + act.dir + w.n); if (li) li.classList.add('on');
      }
    }
    function select(r, c, toggle) {
      var same = act.r === r && act.c === c;
      if (same && toggle) act.dir = act.dir === 'A' ? 'D' : 'A';
      else if (!same && !entry(r, c, act.dir)) act.dir = act.dir === 'A' ? 'D' : 'A';
      act.r = r; act.c = c;
      if (!entry(r, c, act.dir)) act.dir = act.dir === 'A' ? 'D' : 'A';
      paint();
    }
    function step(r, c, k) {
      var cs = run(r, c, act.dir), i = cs.findIndex(function (p) { return p[0] === r && p[1] === c; }), n = cs[i + k];
      if (n) { act.r = n[0]; act.c = n[1]; inputs[n[0] + ',' + n[1]].focus(); paint(); }
    }
    function save() { var arr = []; for (var r = 0; r < R; r++) for (var c = 0; c < C; c++) arr.push(inputs[r + ',' + c] ? inputs[r + ',' + c].value : ''); store(key, JSON.stringify(arr)); }
    function doneClues() {
      d.across.concat(d.down).forEach(function (w) {
        var dir = d.across.indexOf(w) >= 0 ? 'A' : 'D', ok = true;
        run(w.r, w.c, dir).forEach(function (p, i) { if ((inputs[p[0] + ',' + p[1]].value || '').toUpperCase() !== w.ans[i]) ok = false; });
        var li = $('#cl-' + dir + w.n); if (li) li.classList.toggle('done', ok);
      });
      var all = true; Object.keys(inputs).forEach(function (k) { var p = k.split(','); if ((inputs[k].value || '').toUpperCase() !== g[+p[0]][+p[1]]) all = false; });
      if (all && msg) msg.textContent = 'Solved. Well done.';
    }
    Object.keys(inputs).forEach(function (k) {
      var inp = inputs[k], r = +inp.getAttribute('data-r'), c = +inp.getAttribute('data-c');
      inp.addEventListener('focus', function () { if (!(act.r === r && act.c === c)) select(r, c, false); inp.select(); });
      inp.addEventListener('click', function () { if (act.r === r && act.c === c && inp.getAttribute('data-was') === '1') select(r, c, true); inp.setAttribute('data-was', '1'); });
      inp.addEventListener('blur', function () { inp.setAttribute('data-was', '0'); });
      inp.addEventListener('input', function () {
        var v = (inp.value || '').replace(/[^a-zA-Z]/g, '').slice(-1).toUpperCase(); inp.value = v;
        cells[k].classList.remove('bad', 'ok'); save(); doneClues();
        if (v) step(r, c, 1);
      });
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !inp.value) { step(r, c, -1); e.preventDefault(); }
        else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
          var dr = e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0, dc = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0, rr = r + dr, cc = c + dc;
          while (rr >= 0 && cc >= 0 && rr < R && cc < C && isBlock(rr, cc)) { rr += dr; cc += dc; }
          if (inputs[rr + ',' + cc]) { inputs[rr + ',' + cc].focus(); }
          e.preventDefault();
        } else if (e.key === ' ') { select(r, c, true); e.preventDefault(); }
      });
    });
    $$('.clues li').forEach(function (li) {
      li.onclick = function () { var w = li.getAttribute('data-w').split(','); act.dir = w[0]; act.r = +w[1]; act.c = +w[2]; paint(); var i = inputs[w[1] + ',' + w[2]]; if (i) i.focus(); };
    });
    var pb = $('#cw-btns');
    if (pb) {
      pb.appendChild(btn('Check', function () {
        var wrong = 0; Object.keys(inputs).forEach(function (k) {
          var p = k.split(','), v = (inputs[k].value || '').toUpperCase(), ok = v === g[+p[0]][+p[1]];
          cells[k].classList.toggle('bad', !!v && !ok); if (v && !ok) wrong++;
        });
        if (msg) msg.textContent = wrong ? wrong + ' letter' + (wrong > 1 ? 's look' : ' looks') + ' wrong.' : 'No wrong letters so far.';
      }));
      pb.appendChild(btn('Reveal word', function () {
        if (act.r < 0) { if (msg) msg.textContent = 'Tap a square first.'; return; }
        run(act.r, act.c, act.dir).forEach(function (p) { inputs[p[0] + ',' + p[1]].value = g[p[0]][p[1]]; }); save(); doneClues();
      }));
      pb.appendChild(btn('Show answers', function () { Object.keys(inputs).forEach(function (k) { var p = k.split(','); inputs[k].value = g[+p[0]][+p[1]]; }); save(); doneClues(); }));
      pb.appendChild(btn('Reset', function () { Object.keys(inputs).forEach(function (k) { inputs[k].value = ''; cells[k].classList.remove('bad'); }); save(); doneClues(); if (msg) msg.textContent = ''; }));
    }
    paint(); doneClues();
  })();

  /* ================= WORD SEARCH ================= */
  (function () {
    var host = $('#wordsearch'), d = data('pz-wordsearch'); if (!host || !d) return;
    var n = d.size, key = 'kv-ws-' + d.day, cells = [], found = {}, start = -1, msg = $('#ws-msg');
    try { found = JSON.parse(store(key) || '{}') || {}; } catch (e) { found = {}; }
    var grid = el('div', 'ws'); grid.style.gridTemplateColumns = 'repeat(' + n + ', 1fr)';
    for (var i = 0; i < n * n; i++) (function (i) {
      var b = el('button', 'wc', d.grid[Math.floor(i / n)][i % n]); b.type = 'button'; b.setAttribute('aria-label', 'Row ' + (Math.floor(i / n) + 1) + ' column ' + (i % n + 1) + ' ' + b.textContent);
      b.onclick = function () { tap(i); }; cells.push(b); grid.appendChild(b);
    })(i);
    host.appendChild(grid);
    var wl = el('div', 'wlist'); host.appendChild(wl);
    var spans = {}; d.words.forEach(function (w) { var s = el('span', found[w.w] ? 'found' : '', w.w); spans[w.w] = s; wl.appendChild(s); });
    var pb = el('div', 'pbtns'); host.appendChild(pb);
    pb.appendChild(btn('Show answers', function () { d.words.forEach(function (w) { line(w).forEach(function (i) { cells[i].classList.add('rv'); }); }); }));
    pb.appendChild(btn('Reset', function () { found = {}; store(key, '{}'); start = -1; paint(); if (msg) msg.textContent = ''; cells.forEach(function (c) { c.classList.remove('rv'); }); }));
    function line(w) { var out = []; for (var k = 0; k < w.w.length; k++) out.push((w.r + w.dr * k) * n + (w.c + w.dc * k)); return out; }
    function paint() {
      cells.forEach(function (c) { c.classList.remove('fd', 'st'); });
      d.words.forEach(function (w) { spans[w.w].className = found[w.w] ? 'found' : ''; if (found[w.w]) line(w).forEach(function (i) { cells[i].classList.add('fd'); }); });
      if (start >= 0) cells[start].classList.add('st');
      var left = d.words.filter(function (w) { return !found[w.w]; }).length;
      if (msg) msg.textContent = left ? left + ' word' + (left > 1 ? 's' : '') + ' to find.' : 'Found them all. Well done.';
    }
    function tap(i) {
      if (start < 0) { start = i; paint(); return; }
      if (start === i) { start = -1; paint(); return; }
      var r1 = Math.floor(start / n), c1 = start % n, r2 = Math.floor(i / n), c2 = i % n, dr = r2 - r1, dc = c2 - c1;
      if (dr === 0 || dc === 0 || Math.abs(dr) === Math.abs(dc)) {
        var len = Math.max(Math.abs(dr), Math.abs(dc)) + 1, sr = Math.sign(dr), sc = Math.sign(dc), s = '';
        for (var k = 0; k < len; k++) s += d.grid[r1 + sr * k][c1 + sc * k];
        var rev = s.split('').reverse().join('');
        d.words.forEach(function (w) { if (w.w === s || w.w === rev) found[w.w] = 1; });
        store(key, JSON.stringify(found));
      }
      start = -1; paint();
    }
    paint();
  })();

  /* ================= CRYPTOGRAM ================= */
  (function () {
    var host = $('#cryptogram'), d = data('pz-cryptogram'); if (!host || !d) return;
    var key = 'kv-cry-' + d.day, guess = {}, msg = $('#cry-msg');
    try { guess = JSON.parse(store(key) || '{}') || {}; } catch (e) { guess = {}; }
    var map = {}; for (var i = 0; i < d.plain.length; i++) { var p = d.plain[i]; if (/[A-Z]/.test(p)) map[d.cipher[i]] = p; }
    var wrap = el('div', 'cry'), boxes = [];
    d.cipher.split(' ').forEach(function (word, wi) {
      var w = el('div', 'cw-word');
      word.split('').forEach(function (ch) {
        if (/[A-Z]/.test(ch)) {
          var c = el('div', 'cl'), inp = el('input'); inp.type = 'text'; inp.maxLength = 1; inp.autocomplete = 'off'; inp.autocapitalize = 'characters'; inp.spellcheck = false;
          inp.setAttribute('data-c', ch); inp.setAttribute('aria-label', 'Cipher letter ' + ch); inp.value = guess[ch] || '';
          c.appendChild(inp); c.appendChild(el('small', '', ch)); boxes.push({ box: c, inp: inp, ch: ch }); w.appendChild(c);
          inp.addEventListener('focus', function () { inp.select(); mark(ch); });
          inp.addEventListener('input', function () {
            var v = (inp.value || '').replace(/[^a-zA-Z]/g, '').slice(-1).toUpperCase(); inp.value = v; guess[ch] = v; store(key, JSON.stringify(guess)); sync(); if (v) next(inp);
          });
          inp.addEventListener('keydown', function (e) { if (e.key === 'Backspace' && !inp.value) { prev(inp); e.preventDefault(); } });
        } else w.appendChild(el('span', 'punct', ch));
      });
      wrap.appendChild(w);
    });
    host.appendChild(wrap);
    var pb = el('div', 'pbtns'); host.appendChild(pb);
    pb.appendChild(btn('Hint', function () {
      var t = boxes.filter(function (b) { return (guess[b.ch] || '') !== map[b.ch]; })[0];
      if (!t) return; guess[t.ch] = map[t.ch]; store(key, JSON.stringify(guess)); sync();
    }));
    pb.appendChild(btn('Check', function () { sync(true); }));
    pb.appendChild(btn('Show answer', function () { Object.keys(map).forEach(function (k) { guess[k] = map[k]; }); store(key, JSON.stringify(guess)); sync(); }));
    pb.appendChild(btn('Reset', function () { guess = {}; store(key, '{}'); sync(); if (msg) msg.textContent = ''; }));
    function mark(ch) { boxes.forEach(function (b) { b.box.classList.toggle('same', b.ch === ch); }); }
    function next(inp) { var i = boxes.findIndex(function (b) { return b.inp === inp; }); if (boxes[i + 1]) boxes[i + 1].inp.focus(); }
    function prev(inp) { var i = boxes.findIndex(function (b) { return b.inp === inp; }); if (boxes[i - 1]) boxes[i - 1].inp.focus(); }
    function sync(check) {
      var used = {}; Object.keys(guess).forEach(function (k) { if (guess[k]) used[guess[k]] = (used[guess[k]] || 0) + 1; });
      var wrong = 0, filled = 0, right = 0, total = Object.keys(map).length;
      boxes.forEach(function (b) {
        b.inp.value = guess[b.ch] || '';
        var dup = guess[b.ch] && used[guess[b.ch]] > 1, bad = check && guess[b.ch] && guess[b.ch] !== map[b.ch];
        b.box.classList.toggle('bad', !!(dup || bad));
      });
      Object.keys(map).forEach(function (k) { if (guess[k]) { filled++; if (guess[k] === map[k]) right++; else wrong++; } });
      if (msg) {
        if (right === total) msg.textContent = 'Solved. ' + (d.who ? 'Attributed to ' + d.who + '.' : 'A well-known saying.');
        else if (check) msg.textContent = wrong ? wrong + ' letter' + (wrong > 1 ? 's look' : ' looks') + ' wrong.' : 'No wrong letters so far.';
      }
    }
    sync();
  })();
})();
