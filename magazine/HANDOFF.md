# Kullangal Vaarte: how it works now

A daily paper for the Mangaluru and Udupi coast, built from data files by `build_paper.py`. White paper only (no dark mode). Numbered pages, mobile first.

## Editions

- Private (inbox and jobs, never share): https://claude.ai/artifact/4jg9ZRexvuGqbmXzrsmt2d , file `kullangal-vaarte.html`
- Shareable: https://claude.ai/artifact/7voAxG4qkUxsec11FZmraw , file `public-edition.html`
- Both are built together by `python3 build_paper.py [YYYY-MM-DD]`. The build refuses to write the shareable file if any private text leaked into it.
- Publish with the Artifact tool to the same URLs (read the artifact first).

## Pages

Public: 1 Front page, 2 Coast & Local, 3 Coast Feature, 4 Kannada Kadambari, 5 English Serial, 6 Puzzles I (Sudoku, cryptogram), 7 Puzzles II (crossword, word search), 8 Garden (3 plants), 9 Tales (comics), 10 Sports (last page).
Private adds Desk and Classifieds as pages 2 and 3. Jokes (English and Kannada) sit between pages.

## Files

- `build_paper.py` builds everything. `paper.css` and `paper.js` are inlined into the page.
- `content/news.json`: the day's lead story, local stories, briefly, coming up, sports, helplines. **Refreshed daily from web-search results with a source for every item.**
- `content/serial_kn.json` (Kannada novel 'ಸಮುದ್ರ ನಿಲಯ') and `content/serial_en.json` (English mystery 'The Tide Ledger'): original fiction, one episode a day (episode 1 on 2026-09-30). Each file has a `bible` with cast, setting and the plan for the next episodes. **Append the next episode each day** (`n`, `title`, `recap` of the previous episode, `text` paragraphs). 14 episodes are written for each.
- `content/features.json`: seven feature articles, one per weekday, each with Commons photo search terms.
- `content/garden.json`: seven plants (3 shown a day, rotating) and monthly tips.
- `content/jokes.json`, `content/crossword_words.json`, `content/wordsearch_sets.json`, `content/proverbs.json`: banks used by the puzzles and joke breaks. Add more over time.
- `content/private.json`: Desk and Classifieds (private edition only). Refresh from Gmail when the connector is available.
- `puzzles.py` (Sudoku with a unique solution, crossword, word search, cryptogram; all seeded by date), `comics.py` (SVG comic panels with lighting filters, 7 Panchatantra + 6 Jataka episodes), `astro.py` (sunrise, sunset, moon phase, calculated), `weather.py` (Open-Meteo), `photos.py` (Wikimedia Commons photos with cache and fallback), `build_notices.py` (approved reader notices, config).
- `kullangal_config.json` (form_url, whatsapp_number, sheet_csv_url: **still empty**, the owner supplies them) and `kullangal_notices.json` (approved notices).
- `content/cache/`: today's downloaded photos. The `*-seed.json` files are the last good real photos and are used if Commons refuses (HTTP 429).

## Decisions and limits

- Canva image credits are tiny (about three images a day) and the Canva connector only returns thumbnails; full size needs a design plus export. So Canva is used for **one illustration a day at most, for the feature article only** (never news, sports or the comic panels): if `content/feature-<date>.jpg` exists it is shown with the label "Illustration made with Canva AI"; otherwise a Commons photo is used. The daily routine has no Canva connector yet, so it uses Commons photos.
- Painted comic panels were tested (Pollinations and Canva) and rejected: Pollinations gave wrong animals and watermarks; Canva quality is good but the quota is far too small for 52 panels. Comics stay SVG, with shading filters added.
- Only web search reaches the news sites (direct fetches of daijiworld, mangaloretoday, deccanherald and others are blocked). News facts therefore come from search result summaries: state only what is clear, cite the source, drop anything contradictory or unclear, and never put a number in the paper that is not in a source.
- Reader posts: the artifact `db` capability cannot be written by people who open a public link. News from readers comes through a Google Form or WhatsApp message to the editor; approved items go into `kullangal_notices.json` (or a published Sheet CSV, which needs docs.google.com allowed).
- No Gmail connector in the routine, so Desk, Classifieds and email do not refresh. Do not send email or messages to anyone without asking the owner.
- WhatsApp cannot be automated for free; the owner posts the shareable link or the PDF by hand.
- Wikimedia rate-limits (HTTP 429). `photos.py` retries and falls back to cached photos.
- Shell: `pip install pillow` if `PIL` is missing (needed by `photos.py`).
