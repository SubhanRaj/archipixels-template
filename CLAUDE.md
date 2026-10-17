# CLAUDE.md

This repository holds static HTML, CSS and JS templates (four dark directions: A, B, C and D) for Archipixels, an architecture and interior studio in Lucknow. The website will be built in Laravel (Blade). These templates are the design reference for that build. The developer continues the work in his own local Laravel environment and in the style of his existing Laravel projects.

The chosen direction is not decided yet. Update this paragraph when it is.

The templates use no JS framework and no bundler. GSAP, Swiper and GLightbox are vendored in `assets/vendor/`.

## Working rules

- Pages are generated. Edit `tools/build.py` and `data/*.json`, then run `python3 tools/build.py`. Do not edit the HTML in `a/`, `b/`, `c/` or `d/` by hand. `d/` is built by `tools/build_d.py`.
- Colours, fonts and shadows are tokens (`--bg --surface --band --line --text --muted --accent --accent-ink --font-display --font-body --radius --shadow-card --lit`) set per direction in `assets/css/theme-*.css`. `core.css` has no theme colours.
- The header menu is shared. On screens up to 1100 px wide the About submenu starts closed and opens with the `.sub-toggle` button (`core.css`, `core.js`). On wider screens it opens on hover or focus.
- Hero and slider markup is shared across directions. Each theme's JS picks the effect (fade, creative, cards or coverflow).
- JavaScript hides content before an animation (`gsap.set`). CSS never does. Keep it that way, and keep the `prefers-reduced-motion` handling.
- Project text comes from the portfolio. Missing facts stay as bracket placeholders such as `[YEAR]` and `[PROJECT STORY]`.
- The site covers every kind of client. Dubai appears in the About story and on the Warehouse Studio and Chat House project pages only.
- Logos are in `assets/img/brand/` (white, transparent, for the dark themes). Originals are in `assets/brand-originals/`.

## Pages

Home, About, Studio, Team, Services, Works, Contact, and one page per project (19). Each direction builds all of them.

## Laravel build

Read `LARAVEL.md` for the mapping from these files to a Laravel app. The rules for the build:

- The Laravel project is where the site lives. Before writing Laravel code, read that project's own `CLAUDE.md`, `composer.json`, routes and existing folder layout, and follow its conventions for structure, naming, formatting, testing and front-end tooling. Where the project has no convention for something, ask the developer before choosing.
- Do not assume PHP, Laravel, database or Livewire versions. Take them from the project.
- The Python generators (`tools/build*.py`) exist only to produce the templates. Blade views and partials replace them. Do not port the generators.
- `data/*.json` is seed data. `site.json` holds the studio details, `projects.json` the 19 projects, `portfolio.json` the Direction D and portfolio colours, swatches and photo lists, and `legacy-projects.json` the earlier Lucknow work.
- Keep the design tokens, the markup structure and the motion rules when moving a direction. Move the CSS and JS into the project's asset pipeline.
- Remove the `theme-switcher` block, the unused directions and `index.html` (the chooser) from the app.
- The forms need a POST route, validation, CSRF protection, spam protection and a notification before launch.

## Blade conversion plan

- `layouts/app.blade.php` holds the head, header, footer and scripts. Keep the chosen direction's CSS and JS (for D, `theme-a` and `theme-d` together) and drop the rest and the `theme-switcher`.
- The `<!-- component: name -->` comments in the generated HTML mark the partials: `site-header`, `site-footer`, `hero-slideshow`, `featured-works`, `intro`, `services`, `range-band`, `homes-and-experiences`, `studio-teaser`, `cta-band`, `page-hero`, `filter-bar`, `card-work`, `palette`, `project-gallery`, `enquiry-form`. Direction D adds `project-colour-section`, `project-panel`, `next-project` and `works-wall`.
- Projects become an Eloquent model with slug, name, by, tagline, kind, cats, place, lit (hex), language[], details[], palette[], card image, gallery[], story, year and area. `data/projects.json` seeds it.
- The works filter can run on Alpine.js or Livewire using the same `data-cats` logic. `works.html#category` deep links already work in `core.js`.
- Project pages take the body class `page-project` and set `--lit` from `$project->lit`.
- The contact form needs a POST route, validation, CSRF, spam protection and a notification.
- Team members and services can move to database tables once the client supplies the content.

## Open items

The README lists what to confirm or fill before launch.

## Portfolio version

`portfolio/` is a one-page version of the PDF portfolio. It is separate from directions A, B and C and does not use `build.py`.

- Generate it with `python3 tools/build_portfolio.py`. The sources are the generator, `data/portfolio.json` and `portfolio/css|js`. Do not edit the HTML.
- Each project section takes its colour from `data/portfolio.json` (`bg`). Text colour is picked by contrast in the generator. The tan panel stays the same on every project.
- Photos live in `portfolio/img/`. Add a project by adding it to `data/projects.json` and `data/portfolio.json`, then rebuild.
- Motion follows the same rule as the directions: JavaScript hides content right before animating it, and `prefers-reduced-motion` turns the motion off.
- Studio and team come after the projects on purpose, as the client asked.

## Direction D

`d/` merges the one-page portfolio with the multi-page approach of Direction A. It has 26 pages and the same nested menu as the other directions (About holds About us and Team).

- Generate it with `python3 tools/build_d.py`. The sources are the generator, `assets/css/theme-d.css`, `assets/js/theme-d.js` and `data/*.json`. Do not edit the HTML.
- `build_d.py` imports `build.py` and `build_portfolio.py` and reuses their functions. It replaces `b.write` at runtime and registers `b.THEMES['d']`, so `python3 tools/build.py` does not build D. The preview switcher in every footer lists `SWITCH` from `build.py` (A, B, C and D).
- The body class is `theme-a theme-d`. D loads `theme-a.css` and `theme-a.js` first, then adds its own files. The A tokens apply, and D adds the colour-section components (`.d-pj`, `.d-panel`, `.d-swatches`, `.d-next`, `.d-wall`, `.d-closing`, `.d-contact*`).
- Each project page has a gallery (`gallery_d` in `build_d.py`). It uses A's `.gallery-swiper` markup, which `core.js` starts, and lists the project's photos from `data/portfolio.json`. `theme-d.css` sizes the slides by photo height.
- Each project block takes its colour from `data/portfolio.json` (`bg`). The generator picks text colour by contrast with `ink_for`.
- Photos come from `portfolio/img/` and the closing logo from `assets/brand-originals/logo-stacked-light.png`. Keep both when moving D.
- About, Studio and Services are A's pages with D's header and footer. The Studio page has one placeholder, `[STUDIO HOURS AND HOW TO BOOK A VISIT]`.
- In the Blade conversion, D's gallery reuses the `project-gallery` partial. The other D components are listed under the Blade conversion plan.
