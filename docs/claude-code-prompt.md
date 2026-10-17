# Prompt for Claude Code in this repository

Paste the text below as the first message of a Claude Code session opened on this repository.

---

You are working in the `archipixels-template` repository, the static design templates for the Archipixels website (an architecture and interior design studio in Lucknow). The live site will be built later in Laravel, in a different folder and a different repository (`archipixels`). This repository is the design reference only.

Your job in this session has two stages.

## Stage 1: understand the repository

Read these files fully before you do anything else:

1. `CONTEXT.md`, `README.md`, `CLAUDE.md` and `LARAVEL.md`. `CONTEXT.md` has the design intent, so read it first.
2. `tools/build.py`, `tools/build_d.py` and `tools/build_portfolio.py`.
3. `data/site.json`, `data/projects.json`, `data/portfolio.json` and `data/legacy-projects.json`.
4. `assets/css/core.css`, `assets/css/theme-a.css`, `theme-b.css`, `theme-c.css`, `theme-d.css`, `assets/js/core.js` and `assets/js/theme-*.js`.
5. `portfolio/css/portfolio.css` and `portfolio/js/` for the one-page portfolio.

Then confirm in your own words, in a short summary:

- the five versions: A Velvet Night, B Gallery Noir, C Midnight Bazaar, D Velvet Portfolio and the one-page portfolio, and which folder each one lives in
- which files are sources (the Python generators, the JSON data, the CSS and JS) and which are generated output (every HTML file in `a/`, `b/`, `c/`, `d/` and `portfolio/`)
- which command rebuilds each version
- the rules in `CLAUDE.md`, including the motion rules, the writing rules for docs and UI text, and the iOS 15 fallback pattern for `color-mix()` and `backdrop-filter`

After the summary, stop and wait. Do not change any file, run any build or start any task until I give an instruction.

## Stage 2: work only on what I ask

When I send a request, follow these rules.

- Make the smallest change that does what I asked. Do not refactor, restyle or tidy anything I did not mention.
- Never hand-edit a generated HTML file. Change the generator, the data or the stylesheet, then rebuild only the builders whose output the change touches: `python3 tools/build.py` for A, B and C, `python3 tools/build_d.py` for D and `python3 tools/build_portfolio.py` for the portfolio. A change to `build.py` also needs `build_d.py`, which imports it. A change to a stylesheet or script needs no rebuild.
- A change to `core.css`, `core.js` or `tools/build.py` reaches every version. State the files you will edit and the versions each edit reaches before you make the change. If I ask for a fix in one version, keep the others unchanged.
- Keep the design tokens, the markup structure and the animation rules. Content is hidden by JavaScript only right before it animates, and `prefers-reduced-motion` stays respected.
- Add a plain fallback before any new `color-mix()`, `svh` or `dvh` value, and add `-webkit-backdrop-filter` beside `backdrop-filter`.
- Write docs, comments, UI text and commit messages in plain present tense. Use no em dashes, no "X, not Y" contrasts, no flourish adjectives, no bold lead-in bullets and no emoji. Leave no placeholders unless they stand for content the client still owes.
- Check only the pages the change touches: one page per version, at 1440 and 390 px. Look for horizontal scroll, broken images and console errors. Run the full link and console check on all pages only when I ask for it.
- The design of A, B and C is final. Do not change their layout, styling or content. You may fix mistakes in them: broken links, stale text in docs and comments, markup errors, bugs, and accessibility or contrast defects. A new site-wide change (a link, a button, a feature) goes into every version where it suits. Build it once in the shared source and style it with each version's existing classes. Add a rule to a theme file only when the existing classes do not cover it. C is not the current pick, and it still receives every site-wide change.
- Update `README.md`, `CLAUDE.md` or `LARAVEL.md` when a change alters what they describe.
- Do not commit or push unless I ask. When I ask, write one commit message in plain English and end with a short list of the files changed.
- Do not add a build step, a framework or a new dependency. The templates stay plain HTML, CSS and JavaScript with Python generators that use only the standard library.
- Do not start the Laravel site here. If I say the live-version work is starting, tell me to open the new folder and repository, and stop.

When a request is unclear or could change more than one version, ask one short question first. When you finish a request, reply with what changed, the files touched and the command you ran to rebuild. Then wait for the next instruction.
