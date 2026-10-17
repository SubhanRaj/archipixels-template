# Laravel build notes

The static templates in this repository are the design reference for the Archipixels website. The site is built in Laravel (Blade). Versions, folder conventions, front-end tooling and test setup come from the developer's Laravel project and are not fixed here.

## Starting point

1. Pick the direction (A, B, C or D). Direction D combines the portfolio look with A's multi-page structure.
2. Read the Laravel project's `CLAUDE.md`, `composer.json` and existing routes. Follow what is there.
3. Move the chosen direction's markup into Blade, its CSS and JS into the project's asset pipeline, and `data/*.json` into migrations and seeders.

## Files to carry over

| Source | Use in Laravel |
|---|---|
| `a/` to `d/` HTML | Reference for views. Pick one direction. |
| `assets/css/core.css` | Layout and components shared by every direction. |
| `assets/css/theme-*.css` | Tokens and styling for the chosen direction. D loads `theme-a.css` and then `theme-d.css`. |
| `assets/js/core.js` | Nav, works filter, forms, lightbox and the `window.AP` helpers. |
| `assets/js/theme-*.js` | Motion for the chosen direction. D loads `theme-a.js` and then `theme-d.js`. |
| `assets/vendor/` | GSAP 3.12.5 with ScrollTrigger, Swiper 11.1.4 and GLightbox 3.3.0. These can move to npm packages. |
| `assets/img/`, `portfolio/img/` | Photos. D reads `portfolio/img/`. |
| `assets/img/brand/`, `assets/brand-originals/` | Logos, favicon and touch icon. |
| `data/*.json` | Seed data. |

## Layout and partials

`layouts/app.blade.php` holds the head, skip link, header, footer and scripts. The generated HTML marks each partial with a `<!-- component: name -->` comment:

- Shared: `site-header`, `site-footer`, `hero-slideshow`, `featured-works`, `intro`, `services`, `range-band`, `homes-and-experiences`, `studio-teaser`, `cta-band`, `page-hero`, `filter-bar`, `card-work`, `palette`, `project-gallery`, `enquiry-form`.
- Direction D adds `project-colour-section`, `project-panel`, `next-project` and `works-wall`.
- `theme-switcher` is for client preview only. Leave it out.

## Routes

| Route | Page |
|---|---|
| `/` | Home |
| `/about` | About |
| `/team` | Team (listed under About in the menu) |
| `/studio` | Studio |
| `/services` | Services |
| `/works` | Works, filterable, with `#category` deep links |
| `/works/{slug}` | Project page (19 projects) |
| `/contact` | Contact and enquiry form |

## Data

Project fields: slug, name, by, tagline, kind, cats[], place, lit (hex), language[], details[], palette[] (name and hex), card image, gallery[], story, year and area. Direction D also uses a background colour (`bg`), a layout name and a photo list with captions per project, from `data/portfolio.json`.

Studio details, founders, contact details, services and the closing line are in `data/site.json`. The menu (Works, About with About us and Team, Studio, Services, Contact) is the `NAV` list in `tools/build.py`. Seven earlier Lucknow projects are in `data/legacy-projects.json` with Wix image ids.

Team members and services can move to database tables once the client supplies the content.

## Rules that carry over

- Colours, fonts and shadows are tokens. Components never hold literal theme colours.
- JavaScript hides content right before it animates. CSS never hides content. `prefers-reduced-motion` turns the motion off.
- Project pages set `--lit` from the project's `lit` value and use the body class `page-project`.
- The works filter uses `data-cats`. It can run on Alpine.js or Livewire if the Laravel project already uses one of them.

## Before launch

- Fill the placeholders (they show with a dashed underline): `[YEAR]`, `[AREA IN SQ FT]`, `[LOCATION]`, `[PROJECT STORY]`, `[ROLE]`, `[SHORT BIO]`, `[STUDIO HOURS AND HOW TO BOOK A VISIT]` and `[TURNKEY EXAMPLES]`.
- Confirm the contact details (see `README.md`).
- Wire the enquiry form to a POST route with validation, CSRF, spam protection and a notification.
- Replace the PDF crops with original photos.
- Remove the `theme-switcher`.
