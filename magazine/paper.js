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
  if (wa) wa.href = 'https://wa.me/?text=' + encodeURIComponent('ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ, ಮಂಗಳೂರು-ಉಡುಪಿ ಕರಾವಳಿಯ ದಿನಪತ್ರಿಕೆ: ' + wa.getAttribute('data-url'));

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
      var bar = el('div', 'chips'); bar.setAttribute('role', 'group'); bar.setAttribute('aria-label', 'ಊರಿನ ಪ್ರಕಾರ ಸುದ್ದಿ ಆಯ್ಕೆ');
      ['ಎಲ್ಲ'].concat(places).forEach(function (name, i) {
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
    var upd = function () { var n = 0; gl.forEach(function (li, i) { if (gdone[i]) n++; }); if (prog) prog.textContent = 'ಈ ತಿಂಗಳು ' + n + ' / ' + gl.length + ' ಕೆಲಸ ಮುಗಿದಿದೆ'; };
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
    try { navigator.clipboard.writeText(t).then(function () { cp.textContent = 'ನಕಲಾಯಿತು'; }, function () { cp.textContent = 'ಪಠ್ಯ ಆಯ್ದು ನಕಲಿಸಿ'; }); }
    catch (e) { cp.textContent = 'ಪಠ್ಯ ಆಯ್ದು ನಕಲಿಸಿ'; }
  };

  /* ---- button helper ---- */
  function btn(label, fn, cls) { var b = el('button', 'btn' + (cls ? ' ' + cls : ''), label); b.type = 'button'; b.onclick = fn; return b; }
  /* "Rub out all": two taps, like deciding to scrub the whole page. Nothing else is offered: no hints, no checking. */
  function rubber(fn) {
    var b = btn('ಎಲ್ಲ ಅಳಿಸಿ', function () {
      if (b.getAttribute('data-arm') === '1') { fn(); b.textContent = 'ಎಲ್ಲ ಅಳಿಸಿ'; b.setAttribute('data-arm', '0'); return; }
      b.setAttribute('data-arm', '1'); b.textContent = 'ಅಳಿಸಲು ಮತ್ತೆ ಒತ್ತಿ';
      setTimeout(function () { b.setAttribute('data-arm', '0'); b.textContent = 'ಎಲ್ಲ ಅಳಿಸಿ'; }, 3500);
    });
    return b;
  }

  /* The puzzles work like pencil and paper. You fill them in yourself; the page never checks, hints or completes
     anything. Yesterday's answers are printed at the end of the second puzzle page. */

  /* ================= SUDOKU ================= */
  (function () {
    var host = $('#sudoku'), d = data('pz-sudoku'); if (!host || !d) return;
    var giv = d.puzzle.split('').map(Number), key = 'kv-sudoku-' + d.day, val = giv.slice(), sel = -1, cells = [];
    try { var sv = JSON.parse(store(key) || 'null'); if (sv && sv.length === 81) val = sv.map(function (v, i) { return giv[i] ? giv[i] : v; }); } catch (e) {}
    var grid = el('div', 'sud'); grid.setAttribute('role', 'grid'); grid.setAttribute('aria-label', 'ಸುಡೋಕು ಜಾಲ');
    for (var i = 0; i < 81; i++) (function (i) {
      var c = el('button', 'sc'); c.type = 'button'; c.onclick = function () { sel = i; paint(); }; cells.push(c); grid.appendChild(c);
    })(i);
    host.appendChild(grid);
    var pad = el('div', 'pad');
    for (var n = 1; n <= 9; n++) (function (n) { var b = el('button', '', String(n)); b.type = 'button'; b.setAttribute('aria-label', n + ' ಬರೆಯಿರಿ'); b.onclick = function () { put(n); }; pad.appendChild(b); })(n);
    var er = el('button', 'w', 'ಅಳಿಸಿ'); er.type = 'button'; er.onclick = function () { put(0); }; pad.appendChild(er);
    host.appendChild(pad);
    var pb = el('div', 'pbtns'); pb.appendChild(rubber(function () { val = giv.slice(); sel = -1; save(); paint(); })); host.appendChild(pb);
    function save() { store(key, JSON.stringify(val)); }
    function put(n) { if (sel < 0 || giv[sel]) return; val[sel] = n; save(); paint(); }
    function paint() {
      cells.forEach(function (c, i) {
        var v = val[i]; c.textContent = v || '';
        c.className = 'sc' + (giv[i] ? ' g' : (v ? ' u' : '')) + (i === sel ? ' sel' : '');
        c.setAttribute('aria-label', 'ಸಾಲು ' + (Math.floor(i / 9) + 1) + ' ಕಂಬ ' + (i % 9 + 1) + (v ? ', ' + v : ', ಖಾಲಿ'));
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
    paint();
  })();

  /* ================= CROSSWORD ================= */
  (function () {
    var host = $('#crossword'), d = data('pz-crossword'); if (!host || !d) return;
    var R = d.rows, C = d.cols, g = d.grid, key = 'kv-cwk-' + d.day;
    /* one square holds one Kannada akshara; a trailing virama is kept while a conjunct is being typed */
    var AKI = /[\u0C95-\u0CB9](?:\u0CCD[\u0C95-\u0CB9])*[\u0CBE-\u0CCC\u0CCD]?[\u0C82\u0C83]?|[\u0C85-\u0C94][\u0C82\u0C83]?/g, pushing = false;
    var saved = []; try { saved = JSON.parse(store(key) || '[]') || []; } catch (e) { saved = []; }
    var num = {}; d.across.concat(d.down).forEach(function (w) { num[w.r + ',' + w.c] = w.n; });
    var isBlock = function (r, c) { return r < 0 || c < 0 || r >= R || c >= C || g[r][c] === '.'; };
    var grid = el('div', 'cw'); grid.style.gridTemplateColumns = 'repeat(' + C + ', minmax(0, 1fr))';
    var cells = {}, inputs = {}, act = { r: -1, c: -1, dir: 'A' };
    for (var r = 0; r < R; r++) for (var c = 0; c < C; c++) {
      var cell = el('div', 'cwc' + (isBlock(r, c) ? ' blk' : ''));
      if (!isBlock(r, c)) {
        var inp = el('input'); inp.type = 'text'; inp.lang = 'kn'; inp.autocomplete = 'off'; inp.autocapitalize = 'none'; inp.setAttribute('autocorrect', 'off'); inp.spellcheck = false;
        inp.setAttribute('aria-label', 'ಸಾಲು ' + (r + 1) + ' ಕಂಬ ' + (c + 1)); inp.setAttribute('data-r', r); inp.setAttribute('data-c', c);
        inp.value = saved[r * C + c] || ''; cell.appendChild(inp); inputs[r + ',' + c] = inp;
        if (num[r + ',' + c]) cell.appendChild(el('i', '', String(num[r + ',' + c])));
      }
      cells[r + ',' + c] = cell; grid.appendChild(cell);
    }
    host.appendChild(grid);
    function nextCell(r, c, k) {
      var dr = act.dir === 'D' ? k : 0, dc = act.dir === 'A' ? k : 0, rr = r + dr, cc = c + dc;
      return isBlock(rr, cc) ? null : [rr, cc];
    }
    function mark(r, c) {
      Object.keys(cells).forEach(function (k) { cells[k].classList.remove('sel', 'dA', 'dD'); });
      if (r >= 0) cells[r + ',' + c].classList.add('sel', act.dir === 'A' ? 'dA' : 'dD');
    }
    function save() { var arr = []; for (var r = 0; r < R; r++) for (var c = 0; c < C; c++) arr.push(inputs[r + ',' + c] ? inputs[r + ',' + c].value : ''); store(key, JSON.stringify(arr)); }
    Object.keys(inputs).forEach(function (k) {
      var inp = inputs[k], r = +inp.getAttribute('data-r'), c = +inp.getAttribute('data-c');
      inp.addEventListener('focus', function () { act.r = r; act.c = c; mark(r, c); if (!pushing) inp.select(); });
      inp.addEventListener('click', function () { if (inp.getAttribute('data-was') === '1') { act.dir = act.dir === 'A' ? 'D' : 'A'; mark(r, c); } inp.setAttribute('data-was', '1'); });
      inp.addEventListener('blur', function () { inp.setAttribute('data-was', '0'); });
      inp.addEventListener('input', function () {
        var parts = (inp.value || '').replace(/[^\u0C80-\u0CFF]/g, '').match(AKI) || [];
        inp.value = parts[0] || '';
        if (parts.length > 1) {   /* typing carries on into the next square, like writing a word along the boxes */
          var n = nextCell(r, c, 1);
          if (n) { var t = inputs[n[0] + ',' + n[1]]; t.value = parts[1]; pushing = true; t.focus(); pushing = false; try { t.setSelectionRange(t.value.length, t.value.length); } catch (x) { } t.dispatchEvent(new Event('input')); }
        }
        save();
      });
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !inp.value) { var p = nextCell(r, c, -1); if (p) inputs[p[0] + ',' + p[1]].focus(); e.preventDefault(); }
        else if (e.key.indexOf('Arrow') === 0) {
          var dr = e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0, dc = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0, rr = r + dr, cc = c + dc;
          while (rr >= 0 && cc >= 0 && rr < R && cc < C && isBlock(rr, cc)) { rr += dr; cc += dc; }
          if (inputs[rr + ',' + cc]) inputs[rr + ',' + cc].focus();
          e.preventDefault();
        } else if (e.key === ' ') { act.dir = act.dir === 'A' ? 'D' : 'A'; mark(r, c); e.preventDefault(); }
      });
    });
    $$('.clues li').forEach(function (li) {
      li.onclick = function () { var w = li.getAttribute('data-w').split(','); act.dir = w[0]; var i = inputs[w[1] + ',' + w[2]]; if (i) i.focus(); mark(+w[1], +w[2]); };
    });
    var pb = $('#cw-btns'); if (pb) pb.appendChild(rubber(function () { Object.keys(inputs).forEach(function (k) { inputs[k].value = ''; }); save(); }));
  })();

  /* ================= WORD SEARCH ================= */
  (function () {
    var host = $('#wordsearch'), d = data('pz-wordsearch'); if (!host || !d) return;
    var n = d.size, key = 'kv-ws-' + d.day, marks = {}, cut = {}, cells = [];
    try { var sv = JSON.parse(store(key) || '{}') || {}; marks = sv.m || {}; cut = sv.c || {}; } catch (e) {}
    var grid = el('div', 'ws'); grid.style.gridTemplateColumns = 'repeat(' + n + ', 1fr)';
    for (var i = 0; i < n * n; i++) (function (i) {
      var b = el('button', 'wc', d.grid[Math.floor(i / n)][i % n]); b.type = 'button';
      b.setAttribute('aria-label', 'ಸಾಲು ' + (Math.floor(i / n) + 1) + ' ಕಂಬ ' + (i % n + 1) + ' ' + b.textContent);
      b.onclick = function () { marks[i] = marks[i] ? 0 : 1; b.classList.toggle('mk', !!marks[i]); save(); };
      b.classList.toggle('mk', !!marks[i]); cells.push(b); grid.appendChild(b);
    })(i);
    host.appendChild(grid);
    var wl = el('div', 'wlist'); host.appendChild(wl);
    d.words.forEach(function (w) {
      var s = el('button', 'wd' + (cut[w.w] ? ' cut' : ''), w.w); s.type = 'button';
      s.onclick = function () { cut[w.w] = cut[w.w] ? 0 : 1; s.classList.toggle('cut', !!cut[w.w]); save(); }; wl.appendChild(s);
    });
    function save() { store(key, JSON.stringify({ m: marks, c: cut })); }
    var pb = el('div', 'pbtns'); host.appendChild(pb);
    pb.appendChild(rubber(function () { marks = {}; cut = {}; save(); cells.forEach(function (c) { c.classList.remove('mk'); }); $$('.wd', wl).forEach(function (s) { s.classList.remove('cut'); }); }));
  })();

  /* ================= CODEWORD (Kannada saying) ================= */
  (function () {
    var host = $('#cryptogram'), d = data('pz-cryptogram'); if (!host || !d) return;
    var AKI = /[\u0C95-\u0CB9](?:\u0CCD[\u0C95-\u0CB9])*[\u0CBE-\u0CCC\u0CCD]?[\u0C82\u0C83]?|[\u0C85-\u0C94][\u0C82\u0C83]?/g;
    var key = 'kv-code-' + d.day, guess = {}, boxes = [], pushing = false;
    try { guess = JSON.parse(store(key) || '{}') || {}; } catch (e) { guess = {}; }
    var wrap = el('div', 'cry');
    d.words.forEach(function (word) {
      var w = el('div', 'cw-word');
      word.forEach(function (code) {
        var c = el('div', 'cl'), given = d.given[String(code)];
        if (given) { c.className = 'cl gv'; c.appendChild(el('span', 'gl', given)); }
        else {
          var my = boxes.length, inp = el('input'); inp.type = 'text'; inp.lang = 'kn'; inp.autocomplete = 'off'; inp.autocapitalize = 'none'; inp.spellcheck = false;
          inp.setAttribute('aria-label', 'ಸಂಖ್ಯೆ ' + code + 'ಕ್ಕೆ ಅಕ್ಷರ'); inp.value = guess[my] || '';
          boxes.push(inp); c.appendChild(inp);
          inp.addEventListener('focus', function () { if (!pushing) inp.select(); });
          inp.addEventListener('input', function () {
            var parts = (inp.value || '').replace(/[^\u0C80-\u0CFF]/g, '').match(AKI) || [];
            inp.value = parts[0] || ''; guess[my] = inp.value;
            if (parts.length > 1 && boxes[my + 1]) { var t = boxes[my + 1]; t.value = parts[1]; guess[my + 1] = parts[1]; pushing = true; t.focus(); pushing = false; try { t.setSelectionRange(t.value.length, t.value.length); } catch (x) { } }
            store(key, JSON.stringify(guess));
          });
          inp.addEventListener('keydown', function (e) { if (e.key === 'Backspace' && !inp.value && boxes[my - 1]) { boxes[my - 1].focus(); e.preventDefault(); } });
        }
        c.appendChild(el('small', '', String(code))); w.appendChild(c);
      });
      wrap.appendChild(w);
    });
    host.appendChild(wrap);
    var pb = el('div', 'pbtns'); host.appendChild(pb);
    pb.appendChild(rubber(function () { guess = {}; store(key, '{}'); boxes.forEach(function (b) { b.value = ''; }); }));
  })();
})();
