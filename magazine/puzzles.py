#!/usr/bin/env python3
"""Daily puzzles for the Puzzle pages: Sudoku, mini crossword, word search and cryptogram.

Everything is generated from the date, so the same date always gives the same puzzles.
Sudoku puzzles have exactly one solution (checked). Crosswords use the clue bank in
content/crossword_words.json and only English answers of A to Z.
"""
import datetime, json, os, random, string

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
N = 11


def _fits(grid, word, r, c, dr, dc):
    """True if the word can be placed; returns crossing count or -1."""
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
            # a new letter must not touch a letter sideways (perpendicular neighbours must be empty)
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
    for w in words[1:]:
        best = []
        for dr, dc in ((0, 1), (1, 0)):
            for r in range(N):
                for c in range(N):
                    x = _fits(grid, w, r, c, dr, dc)
                    if x > 0:
                        # do not extend an existing word in the same direction
                        best.append((x, r, c, dr, dc))
        if best:
            rng.shuffle(best)
            best.sort(key=lambda t: -t[0])
            x, r, c, dr, dc = best[0]
            for k, ch in enumerate(w):
                grid[r + dr * k][c + dc * k] = ch
            placed.append((w, r, c, dr, dc))
    return grid, placed


def make_crossword(day):
    bank = {}
    for a, clue in load("crossword_words.json"):
        if 3 <= len(a) <= 9:
            bank.setdefault(a, clue)
    answers = sorted(bank)
    rng = random.Random(day.toordinal() * 104729 + 5)
    best = None
    for attempt in range(220):
        pool = answers[:]
        rng.shuffle(pool)
        long_first = sorted(pool[:60], key=lambda a: -len(a))
        seed = rng.choice([a for a in long_first if 6 <= len(a) <= 9])
        rest = [a for a in pool if a != seed][:60]
        grid, placed = _build_cross([seed] + rest, rng)
        score = len(placed) * 10 + sum(1 for r in grid for ch in r if ch) // 3
        rows = [i for i in range(N) if any(grid[i])]
        cols = [j for j in range(N) if any(grid[i][j] for i in range(N))]
        if not rows or not cols:
            continue
        if best is None or score > best[0]:
            best = (score, grid, placed)
    _, grid, placed = best
    rows = [i for i in range(N) if any(grid[i])]
    cols = [j for j in range(N) if any(grid[i][j] for i in range(N))]
    r0, r1, c0, c1 = rows[0], rows[-1], cols[0], cols[-1]
    g = [[grid[i][j] for j in range(c0, c1 + 1)] for i in range(r0, r1 + 1)]
    H, W = len(g), len(g[0])
    starts = {}
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
                starts[(i, j)] = n
                if sa:
                    w = ""
                    k = j
                    while k < W and g[i][k]:
                        w += g[i][k]; k += 1
                    across.append(dict(n=n, r=i, c=j, len=len(w), ans=w, clue=bank.get(w, "")))
                if sd:
                    w = ""
                    k = i
                    while k < H and g[k][j]:
                        w += g[k][j]; k += 1
                    down.append(dict(n=n, r=i, c=j, len=len(w), ans=w, clue=bank.get(w, "")))
    # incidental runs of letters that are not in the bank would have no clue; drop such words from the clue list check
    ok = all(x["clue"] for x in across + down)
    return dict(rows=H, cols=W, grid=["".join(ch or "." for ch in row) for row in g], across=across, down=down, clean=ok)


# ---------------------------------------------------------------- word search
DIRS_EASY = [(0, 1), (1, 0), (1, 1)]
DIRS_HARD = DIRS_EASY + [(0, -1), (-1, 0), (-1, -1), (1, -1)]


def make_wordsearch(day):
    sets = load("wordsearch_sets.json")
    s = sets[day.toordinal() % len(sets)]
    rng = random.Random(day.toordinal() * 31337 + 1)
    size = 12
    hard = day.weekday() >= 4
    dirs = DIRS_HARD if hard else DIRS_EASY
    words = [w for w in s["words"] if len(w) <= size]
    rng.shuffle(words)
    words = sorted(words[:10], key=lambda w: -len(w))
    for attempt in range(200):
        grid = [[""] * size for _ in range(size)]
        placed, ok = [], True
        for w in words:
            done = False
            for _ in range(300):
                dr, dc = rng.choice(dirs)
                r, c = rng.randrange(size), rng.randrange(size)
                er, ec = r + dr * (len(w) - 1), c + dc * (len(w) - 1)
                if not (0 <= er < size and 0 <= ec < size):
                    continue
                if all(grid[r + dr * k][c + dc * k] in ("", w[k]) for k in range(len(w))):
                    for k in range(len(w)):
                        grid[r + dr * k][c + dc * k] = w[k]
                    placed.append(dict(w=w, r=r, c=c, dr=dr, dc=dc))
                    done = True
                    break
            if not done:
                ok = False
                break
        if ok:
            break
    letters = string.ascii_uppercase
    for i in range(size):
        for j in range(size):
            if not grid[i][j]:
                grid[i][j] = rng.choice(letters)
    return dict(title=s["title"], size=size, grid=["".join(r) for r in grid], words=placed, hard=hard)


# ---------------------------------------------------------------- cryptogram
def make_cryptogram(day):
    items = load("proverbs.json")
    text, who = items[day.toordinal() % len(items)]
    rng = random.Random(day.toordinal() * 65537 + 3)
    letters = list(string.ascii_uppercase)
    while True:
        perm = letters[:]
        rng.shuffle(perm)
        if all(a != b for a, b in zip(letters, perm)):
            break
    m = dict(zip(letters, perm))
    plain = text.upper()
    cipher = "".join(m.get(ch, ch) for ch in plain)
    return dict(plain=plain, cipher=cipher, who=who)


def level_for(day):
    return ["Easy", "Easy", "Medium", "Medium", "Hard", "Hard", "Medium"][day.weekday()]


def make_all(day):
    return dict(sudoku=make_sudoku(day, level_for(day)), crossword=make_crossword(day),
                wordsearch=make_wordsearch(day), cryptogram=make_cryptogram(day))


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
    print("\n".join(cw["grid"]))
    print(p["wordsearch"]["title"], [w["w"] for w in p["wordsearch"]["words"]])
    print(p["cryptogram"])
