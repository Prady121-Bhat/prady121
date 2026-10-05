#!/usr/bin/env python3
"""Daily puzzles for the Puzzle pages: Sudoku, mini crossword, word search and cryptogram.

Everything is generated from the date, so the same date always gives the same puzzles.
Sudoku puzzles have exactly one solution (checked). Crosswords use the clue bank in
content/crossword_words_kn.json: Kannada answers and clues, one akshara per square.
"""
import re, datetime, json, os, random, string

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, "content", name), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- sudoku
def _peers():
    P = []
    for i in range(81):
        r, c = divmod(i, 9)
        s = {j for j in range(81) if j // 9 == r or j % 9 == c or (j // 9 // 3 == r // 3 and j % 9 // 3 == c // 3)}
        s.discard(i)
        P.append(sorted(s))
    return P


PEERS = _peers()


def _cands(grid, i):
    used = {grid[j] for j in PEERS[i]}
    return [v for v in range(1, 10) if v not in used]


def _solve(grid, rng=None, limit=1):
    """Backtracking with fewest-candidates-first. Returns number of solutions found (up to limit)."""
    best, opts = None, None
    for i in range(81):
        if grid[i] == 0:
            c = _cands(grid, i)
            if not c:
                return 0
            if opts is None or len(c) < len(opts):
                best, opts = i, c
                if len(c) == 1:
                    break
    if best is None:
        return 1
    if rng:
        rng.shuffle(opts)
    n = 0
    for v in opts:
        grid[best] = v
        n += _solve(grid, rng, limit - n)
        if n >= limit:
            return n  # leave grid filled: caller copies before use
        grid[best] = 0
    return n


def make_sudoku(day, level):
    rng = random.Random(day.toordinal() * 7919 + 13)
    full = [0] * 81
    _solve(full, rng)
    solution = full[:]
    clues = {"Easy": 40, "Medium": 34, "Hard": 28}[level]
    puzzle = solution[:]
    order = list(range(81))
    rng.shuffle(order)
    remaining = 81
    for i in order:
        if remaining <= clues:
            break
        keep = puzzle[i]
        puzzle[i] = 0
        test = puzzle[:]
        if _solve(test, None, 2) != 1:
            puzzle[i] = keep
        else:
            remaining -= 1
    return dict(level=level, puzzle="".join(map(str, puzzle)), solution="".join(map(str, solution)))


# ---------------------------------------------------------------- crossword
N = 13
# one crossword square holds one akshara (a consonant with its vowel sign, or a conjunct such as ಲ್ಲು or ಕ್ಷ)
_AKS = re.compile("(?:[\u0C95-\u0CB9](?:\u0CCD[\u0C95-\u0CB9])*[\u0CBE-\u0CCC]?[\u0C82\u0C83]?|[\u0C85-\u0C94][\u0C82\u0C83]?)")


def aksharas(word):
    return tuple(_AKS.findall(word))


def _fits(grid, word, r, c, dr, dc):
    """Crossing count if the word can be placed (word = tuple of aksharas); -1 or -2 if not."""
    er, ec = r + dr * (len(word) - 1), c + dc * (len(word) - 1)
    if r < 0 or c < 0 or er >= N or ec >= N:
        return -1
    pr, pc = r - dr, c - dc
    if 0 <= pr < N and 0 <= pc < N and grid[pr][pc]:
        return -1
    nr, nc = er + dr, ec + dc
    if 0 <= nr < N and 0 <= nc < N and grid[nr][nc]:
        return -1
    cross = 0
    for k, ch in enumerate(word):
        rr, cc = r + dr * k, c + dc * k
        cur = grid[rr][cc]
        if cur:
            if cur != ch:
                return -1
            cross += 1
        else:
            # a new akshara must not touch another sideways (perpendicular neighbours must be empty)
            for ar, ac in ((rr + dc, cc + dr), (rr - dc, cc - dr)):
                if 0 <= ar < N and 0 <= ac < N and grid[ar][ac]:
                    return -1
    return cross if cross > 0 else -2  # -2: no crossing (only valid for the first word)


def _build_cross(words, rng):
    grid = [[""] * N for _ in range(N)]
    placed = []
    first = words[0]
    r0 = rng.randrange(2, N - 2)
    c0 = (N - len(first)) // 2
    for k, ch in enumerate(first):
        grid[r0][c0 + k] = ch
    placed.append((first, r0, c0, 0, 1))
    left = list(words[1:])
    for _ in range(3):  # a word that found no crossing early may fit once more words are down
        again = []
        for w in left:
            best = []
            for dr, dc in ((0, 1), (1, 0)):
                for r in range(N):
                    for c in range(N):
                        x = _fits(grid, w, r, c, dr, dc)
                        if x > 0:
                            best.append((x, r, c, dr, dc))
            if best:
                rng.shuffle(best)
                best.sort(key=lambda t: -t[0])
                x, r, c, dr, dc = best[0]
                for k, ch in enumerate(w):
                    grid[r + dr * k][c + dc * k] = ch
                placed.append((w, r, c, dr, dc))
            else:
                again.append(w)
        left = again
    return grid, placed


def make_crossword(day):
    """Kannada crossword: words and clues in Kannada from content/crossword_words_kn.json."""
    bank = {}
    for a, clue in load("crossword_words_kn.json"):
        t = aksharas(a)
        if "".join(t) == a and 2 <= len(t) <= 8:
            bank.setdefault(t, (a, clue))
    answers = sorted(bank)
    rng = random.Random(day.toordinal() * 104729 + 5)
    best = None
    for attempt in range(70):
        pool = answers[:]
        rng.shuffle(pool)
        seeds = [a for a in pool[:60] if 5 <= len(a) <= 8] or [a for a in pool if len(a) >= 4]
        seed = rng.choice(seeds)
        rest = [a for a in pool if a != seed]
        grid, placed = _build_cross([seed] + rest, rng)
        score = len(placed) * 10 + sum(1 for r in grid for ch in r if ch) // 3 + sum(1 for p in placed if len(p[0]) >= 4) * 3
        if best is None or score > best[0]:
            best = (score, grid, placed)
    _, grid, placed = best
    rows = [i for i in range(N) if any(grid[i])]
    cols = [j for j in range(N) if any(grid[i][j] for i in range(N))]
    r0, r1, c0, c1 = rows[0], rows[-1], cols[0], cols[-1]
    g = [[grid[i][j] for j in range(c0, c1 + 1)] for i in range(r0, r1 + 1)]
    H, W = len(g), len(g[0])
    n = 0
    across, down = [], []
    for i in range(H):
        for j in range(W):
            if not g[i][j]:
                continue
            sa = (j == 0 or not g[i][j - 1]) and j + 1 < W and g[i][j + 1]
            sd = (i == 0 or not g[i - 1][j]) and i + 1 < H and g[i + 1][j]
            if sa or sd:
                n += 1
                if sa:
                    t = []
                    k = j
                    while k < W and g[i][k]:
                        t.append(g[i][k]); k += 1
                    t = tuple(t)
                    across.append(dict(n=n, r=i, c=j, len=len(t), ans="".join(t), clue=bank.get(t, ("", ""))[1]))
                if sd:
                    t = []
                    k = i
                    while k < H and g[k][j]:
                        t.append(g[k][j]); k += 1
                    t = tuple(t)
                    down.append(dict(n=n, r=i, c=j, len=len(t), ans="".join(t), clue=bank.get(t, ("", ""))[1]))
    ok = all(x["clue"] for x in across + down)
    return dict(lang="kn", rows=H, cols=W, grid=[[ch or "" for ch in row] for row in g], across=across, down=down, clean=ok)


# ---------------------------------------------------------------- word search
DIRS_EASY = [(0, 1), (1, 0), (1, 1)]
DIRS_HARD = DIRS_EASY + [(0, -1), (-1, 0), (-1, -1), (1, -1)]


def make_wordsearch(day):
    """Kannada word search: every square holds one akshara; words are placed across, down or diagonally (and backwards at weekends)."""
    sets = load("wordsearch_sets_kn.json")
    s = sets[day.toordinal() % len(sets)]
    rng = random.Random(day.toordinal() * 31337 + 1)
    size = 12
    hard = day.weekday() >= 4
    dirs = DIRS_HARD if hard else DIRS_EASY
    words = [(w, aksharas(w)) for w in s["words"]]
    words = [(w, t) for w, t in words if "".join(t) == w and len(t) <= size]
    rng.shuffle(words)
    words = sorted(words[:10], key=lambda p: -len(p[1]))
    pool = sorted({a for st in sets for w in st["words"] for a in aksharas(w)})
    for attempt in range(200):
        grid = [[""] * size for _ in range(size)]
        placed, ok = [], True
        for w, t in words:
            done = False
            for _ in range(300):
                dr, dc = rng.choice(dirs)
                r, c = rng.randrange(size), rng.randrange(size)
                er, ec = r + dr * (len(t) - 1), c + dc * (len(t) - 1)
                if not (0 <= er < size and 0 <= ec < size):
                    continue
                if all(grid[r + dr * k][c + dc * k] in ("", t[k]) for k in range(len(t))):
                    for k in range(len(t)):
                        grid[r + dr * k][c + dc * k] = t[k]
                    placed.append(dict(w=w, r=r, c=c, dr=dr, dc=dc, n=len(t)))
                    done = True
                    break
            if not done:
                ok = False
                break
        if ok:
            break
    for i in range(size):
        for j in range(size):
            if not grid[i][j]:
                grid[i][j] = rng.choice(pool)
    return dict(lang="kn", title=s["title"], size=size, grid=grid, words=placed, hard=hard)


# ---------------------------------------------------------------- codeword (Kannada saying)
def make_cryptogram(day):
    """A Kannada saying with every akshara replaced by a number (the same akshara always gets the same number).
    A few aksharas are given as a start. The solver writes the aksharas under the numbers."""
    items = [it for it in load("proverbs_kn.json") if len(aksharas(it[0].replace(" ", ""))) >= 10]
    text, who = items[day.toordinal() % len(items)]
    rng = random.Random(day.toordinal() * 65537 + 3)
    words = [aksharas(w) for w in text.split(" ")]
    distinct = sorted({a for w in words for a in w})
    codes = list(range(1, len(distinct) + 1))
    rng.shuffle(codes)
    m = dict(zip(distinct, codes))
    given_n = max(2, len(distinct) // 5)
    given = {str(m[a]): a for a in rng.sample(distinct, given_n)}
    return dict(lang="kn", plain=text, who=who, words=[[m[a] for a in w] for w in words], given=given)


def level_for(day):
    return ["Easy", "Easy", "Medium", "Medium", "Hard", "Hard", "Medium"][day.weekday()]


def make_all(day):
    return dict(sudoku=make_sudoku(day, level_for(day)), crossword=make_crossword(day),
                wordsearch=make_wordsearch(day), cryptogram=make_cryptogram(day))


def exists(day):
    return os.path.exists(os.path.join(HERE, "content", "puzzles", day.isoformat() + ".json"))


def get(day, save=True):
    """Today's puzzles, stored in content/puzzles/<date>.json so tomorrow's answers match exactly what was printed,
    even if the word banks change in between."""
    folder = os.path.join(HERE, "content", "puzzles")
    path = os.path.join(folder, day.isoformat() + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    data = make_all(day)
    if save:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        for name in sorted(os.listdir(folder)):  # keep two weeks
            try:
                if (day - datetime.date.fromisoformat(name[:10])).days > 14:
                    os.remove(os.path.join(folder, name))
            except ValueError:
                pass
    return data


if __name__ == "__main__":
    import sys, time
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    t = time.time()
    p = make_all(d)
    print("time", round(time.time() - t, 1))
    s = p["sudoku"]
    print(s["level"], sum(1 for ch in s["puzzle"] if ch != "0"), "clues")
    cw = p["crossword"]
    print("crossword", cw["rows"], "x", cw["cols"], "across", len(cw["across"]), "down", len(cw["down"]), "clean", cw["clean"])
    print("\n".join(" ".join(c or "·" for c in row) for row in cw["grid"]))
    print(p["wordsearch"]["title"], [w["w"] for w in p["wordsearch"]["words"]])
    print(p["cryptogram"])
