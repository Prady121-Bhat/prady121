# Kullangal Vaarte: handoff for a new session

Paste the "Start prompt" at the bottom of this file into a new Claude Code session in the same Default environment.

## State (30 Sep 2026, end of second session)

- Repo `Prady121-Bhat/prady121`, branch `claude/zen-cerf-ve6pjo`, folder `magazine/`.
- Two published editions (Artifact tool, update in place, read the artifact first):
  - Private (inbox and jobs, never share): https://claude.ai/artifact/4jg9ZRexvuGqbmXzrsmt2d , file `kullangal-vaarte.html`
  - Shareable: https://claude.ai/artifact/7voAxG4qkUxsec11FZmraw , file `public-edition.html`, built with `make_public.py`. Both artifacts are private until the owner uses the Share menu.
- No anime anywhere.
- Done this session: `add_interactive.py` applied to `template.html` and `kullangal-vaarte.html` (reader tools, coast place filter, garden checklist, quiz slot, notices block, send box). Do not run it again.
- `build_tales.py` also builds the quiz (moral of each of today's two tales, plus one plant or coast fact from the page; grim headlines are skipped; wrong morals come from other themes). Still 7 + 6 episodes with SVG panels.
- `build_notices.py` + `kullangal_config.json` + `kullangal_notices.json`: only approved notices dated for today; empty-state text otherwise. The config values `form_url`, `whatsapp_number`, `sheet_csv_url` are still EMPTY (the owner has to supply them); until then the send box says the form is being set up.
- `build_weather.py`: five-day Mangaluru forecast from Open-Meteo, dated, with retries. Says so if it cannot fetch.
- Daily routine `trig_01AgENKKUZBgSk64iAKogS8M` (06:29 India time) updated for all of the above. No Gmail connector, so Desk, Classifieds and email still do not work.

## Painted panels: tried and rejected

Pollinations (`image.pollinations.ai`) is reachable but returned watermarked 886x665 images from the Sana model (the `flux` and size parameters are ignored), with wrong animals (two monkeys for "monkey and crocodile", tortoise-goose hybrids) and 500/402 errors. The owner also judged them bad. Nothing was generated. `tales_data.py` (33 episodes with captions and prompts) is unused; only an image source that gets characters right would justify using it.

## Decisions and limits

- Reader posts: the `db` capability cannot be written by people who open a public link (read-only). News from readers comes in through a free Google Form or a WhatsApp message to the editor. Approved items go in `kullangal_notices.json` (or a published Sheet CSV).
- Canva image credits ran out earlier ("quota_exceeded").
- Allowed domains: upload.wikimedia.org, commons.wikimedia.org, export-download.canva.com, api.open-meteo.com, image.pollinations.ai (reachable, rejected). docs.google.com is needed for a Sheet CSV.
- Wikimedia rate-limits (429): retries and a User-Agent. Open-Meteo through the proxy sometimes times out: `build_weather.py` retries.
- Shell commands sometimes fail with a transient classifier error: retry.
- WhatsApp cannot be automated for free. The owner posts the shareable link or PDF to a WhatsApp Channel by hand.
- Do not send email or messages to anyone without asking the owner.
