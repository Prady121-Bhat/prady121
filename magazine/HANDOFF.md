# ಕುಲ್ಲಂಗಾಲ್ ವಾರ್ತೆ (Kullangal Vaarte): how it works now

A daily paper for the Mangaluru and Udupi coast, **printed entirely in Kannada** (no English text on the pages, except photo credits, Latin plant names, licence names and the Open-Meteo name). Built from data files by `build_paper.py`. White paper only (no dark mode). Numbered pages, mobile first. Everything the editor writes into `content/` must be in Kannada.

## Editions

- Private (inbox and jobs, never share): https://claude.ai/artifact/4jg9ZRexvuGqbmXzrsmt2d , file `kullangal-vaarte.html`
- Shareable: https://claude.ai/artifact/7voAxG4qkUxsec11FZmraw , file `public-edition.html`
- Both are built together by `python3 build_paper.py [YYYY-MM-DD]`. The build refuses to write the shareable file if any private text (English or Kannada) leaked into it.
- Publish with the Artifact tool to the same URLs (read the artifact first).

## Pages

Public: 1 ಮುಖಪುಟ (front), 2 ಕರಾವಳಿ ಮತ್ತು ಸ್ಥಳೀಯ (coast and local), 3 ಜಗತ್ತು (world), 4 ಕರಾವಳಿ ವಿಶೇಷ (feature), 5 ಕನ್ನಡ ಕಾದಂಬರಿ (serial), 6 ಒಗಟುಗಳು ೧ (Sudoku, codeword), 7 ಒಗಟುಗಳು ೨ (Kannada crossword, Kannada word search), 8 ತೋಟ (a herb, a flower and an indoor or bonsai plant), 9 ಅಡುಗೆಮನೆ (one vegetarian recipe a day, NO onion or garlic), 10 ಭಗವದ್ಗೀತೆ (one Gita verse a day with word meanings, translation, explanation), 11 ಸಂಸ್ಕೃತ ಕಲಿಕೆ (one Sanskrit lesson a day; yesterday's practice answers), 12 ಕತೆಗಳು (ONE comic tale a day, Panchatantra and Jataka alternately), 13 ಕ್ರೀಡೆ (sports, last page).
Private adds ಡೆಸ್ಕ್ and ಪ್ರಕಟಣೆಗಳು (classifieds) as pages 2 and 3. A Kannada joke sits between some pages. The English serial was removed.

## Files

- `build_paper.py` builds everything (all page labels are Kannada strings in this file). `paper.css` and `paper.js` are inlined into the page. `comics_kn.py` holds the Kannada text of the 13 comic tales (`comics.py` keeps the drawings and calls it).
- `content/news.json` (coast news, sports, helplines, coming up) and `content/world.json` (World page): **refreshed daily from web-search results, written in Kannada, with a source name and URL for every item; set `date`.** Never state a number or fact that is not in a source; say 'ವರದಿಗಳ ಪ್ರಕಾರ' for secondary sources.
- `content/serial_kn.json`: Kannada novel 'ಸಮುದ್ರ ನಿಲಯ', one episode a day (episode 1 on 2026-09-30), 14 written (new ones needed from 14 Oct). Episodes are long (about 2,800 to 3,800 characters, 8 to 14 paragraphs, `***` paragraph = scene break). Each file has a `bible` with cast, setting and the plan. Append `{n, title, recap, text}`.
- `content/recipes.json`: 15 Kannada vegetarian recipes (name, kind, serves, time, intro, ingredients, steps, tip), one shown per day in list order (day number modulo 15). Rules: pure vegetarian, never onion or garlic (asafoetida is fine), simple reliable measures, no health claims. Add more over time.
- **Bhagavad Gita page runs from the first verse, in order, one verse a day.** `content/gita_text.json` holds the Sanskrit text of all 701 numbered verses (ch, v, speaker, two lines, Devanagari), taken from the open `gita/gita` dataset on GitHub (raw.githubusercontent.com is reachable from the sandbox) and cleaned; day one is 2026-10-05 = verse 1.1, and day N shows verse N (it wraps after 701). The Kannada study notes live in `content/gita/chNN.json`, keyed by verse number: `{words: [[Devanagari word, Kannada meaning],...], tr, exp: [paragraphs], think}`. **Chapter 1 (47 verses) is written; chapter 2 has 10 verses (2.13, 2.14, 2.20, 2.22, 2.23, 2.47, 2.48, 2.62, 2.63, 2.70) and a few later ones exist; all the rest still has to be written, always at least 14 days ahead of the paper.** The build prints a WARNING and shows only the verse if a day's notes are missing. Write in your own words (do not copy English commentaries), give the translation faithfully, say where commentators differ, and keep sensitive verses (for example 1.41) in context. The Sanskrit is displayed through `gita_sanskrit.py`, which converts Devanagari to Kannada script.
- `content/sanskrit_1.json` + `sanskrit_2.json`: a 30-lesson Sanskrit course (alphabet and sounds, nouns and cases, verbs and tenses, numbers, sandhi, greetings, vocabulary, kridanta forms, three subhashitas), same cycle; each has `intro`, `table`, `practice` (q, a). Sanskrit is authored in Devanagari (inside `{{ }}` in lesson text) and `gita_sanskrit.py` converts it to Kannada script (same Unicode layout, offset 0x380; danda printed as |). Practice answers appear only in the next day's lesson. Verse texts were written from the standard Gita text; have a Sanskrit teacher check them and the lessons before relying on them. Never alter a verse from uncertain memory.
- `content/features.json`: seven Kannada feature articles, one per weekday (`theme` is the English key for photo search, `theme_kn` is shown), with Commons photo search terms.
- `content/garden.json`: 26 plants in three categories (`category`: herb 8, flower 8, indoor 10 including 3 bonsai with `bonsai: true`). `key` is the English name (used for photo search and the photo cache), `name` the Kannada name. One of each category is shown daily (index = day number, +3 for flowers, +5 for indoor).
- `content/jokes.json` (Kannada only, rotates 4 a day), `content/crossword_words_kn.json` (word, Kannada clue), `content/wordsearch_sets_kn.json`, `content/proverbs_kn.json` (sayings for the codeword puzzle): banks used by the puzzles and joke breaks. Add more over time.
- `content/private.json`: Desk and Classifieds (private edition only, written in Kannada). Refresh from Gmail when the connector is available.
- `puzzles.py` (Sudoku with a unique solution, Kannada crossword, Kannada word search, codeword; seeded by date and SAVED to `content/puzzles/<date>.json`), `comics.py`, `astro.py` (sunrise, sunset, moon phase, calculated), `weather.py` (Open-Meteo, descriptions in Kannada), `photos.py` (Wikimedia Commons photos with cache and fallback), `build_notices.py` (approved reader notices).
- `kullangal_config.json` (form_url, whatsapp_number, sheet_csv_url: **still empty**, the owner supplies them) and `kullangal_notices.json` (approved notices).
- `content/cache/`: downloaded photos. The `*-seed.json` files are the last good real photos and are used if Commons refuses (HTTP 429).

## Kannada puzzles

- One crossword square, word-search square or codeword box holds one **akshara** (consonant with its vowel sign, or a conjunct such as ಲ್ಲು, ಕ್ಷ). `puzzles.aksharas(word)` splits a word; always check new bank words with it.
- Crossword: 13 x 13 search, about 20 entries, indirect clues (general knowledge). Word search: 12 x 12 of aksharas, weekends add reversed words. Codeword ("ಗಾದೆ ಸಂಕೇತ"): a Kannada saying with every akshara replaced by a number; a few aksharas are given.
- Typing in the boxes uses the phone's Kannada keyboard; typing carries on into the next box.

## Pencil-and-paper rule (answers next day only)

- Today's page has no check, hint, solve or auto-fill. Readers pencil in squares (progress is kept on their own device) and can rub out ("ಎಲ್ಲ ಅಳಿಸಿ"). The page JSON holds only the puzzle, never the solution.
- The page shows **yesterday's** answers from `content/puzzles/<yesterday>.json`. If there was no edition yesterday, the page says so. Always commit `content/puzzles/`; never edit an earlier day's file.

## Reader notices (events, lost and found, road works, temple/school notices, shop openings, club and school results)

Readers fill the owner's free **Google Form** (or send a WhatsApp message with the template). The Form's response Sheet gets a column `approved` (or `ಅನುಮೋದನೆ`); the editor types `yes` (or `ಹೌದು`) for notices that may print. The sheet is published to the web as CSV and the link goes in `kullangal_config.json` as `sheet_csv_url` (and `form_url`, `whatsapp_number`). The 06:29 IST build reads approved rows whose date includes today, understands English or Kannada question headings and ISO or d/m/yyyy dates, so a notice sent by 8 pm the evening before is in the next morning's paper. Nothing unapproved is ever printed. The routine's environment must allow `docs.google.com`. Step-by-step owner checklist: `NOTICES-SETUP.md`. Until the form exists, the box on the local page says the section is not open yet.

## Decisions and limits

- **A purely vegetarian paper (owner's rule).** Never print non-vegetarian food, recipes, fish or meat markets, or jokes about them. Recipes never use onion or garlic. The Food feature is about Udupi vegetarian cuisine, the Sea feature about Maravanthe, the crane-and-fish Jataka tale is left out of the rotation, and puzzle word banks avoid fish and meat words. The serial's village is a fishing village (boats, nets, fishermen as livelihood); the owner has been told and may ask to change that.

- Canva image credits are tiny. Canva is used for **one illustration a day at most, for the feature article only**: if `content/feature-<date>.jpg` exists it is shown with a Kannada label; otherwise a Commons photo is used. The daily routine has no Canva connector yet.
- Comics are original SVG drawings (painted panels were tested and rejected).
- Only web search reaches the news sites (direct fetches are blocked). Facts come from search-result summaries: state only what is clear, cite the source, drop anything contradictory or unclear.
- Reader posts: the artifact `db` capability cannot be written by people who open a public link, so notices come through the Form or WhatsApp.
- No Gmail connector in the routine, so Desk, Classifieds and email do not refresh. Do not send email or messages to anyone without asking the owner. WhatsApp cannot be automated; the owner posts the shareable link or the PDF by hand.
- Wikimedia rate-limits (HTTP 429). `photos.py` retries and falls back to cached photos; a plant with no photo simply shows without one.
- The routine run on 2026-10-01 06:29 IST did nothing because the routine has no repository attached (`sources: []`); the owner must add `Prady121-Bhat/prady121` as its source in the routine's settings.
- Shell: `pip install pillow` if `PIL` is missing (needed by `photos.py`).
