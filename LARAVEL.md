# Laravel build notes

The static templates in this repository are the design reference for the Archipixels website. The site is built in Laravel 13 in a separate repository, `SubhanRaj/archipixels`, checked out at `~/Sites/archipixels`. That repository's own `CLAUDE.md`, `ROADMAP.md` and `ARCHITECTURE.md` hold the build rules. This file maps the templates to that app.

## Status

The direction is D, and the Laravel app has it built: every page, the one-page portfolio and the error pages, with `data/*.json` loaded by seeders. Design changes continue in this repository. The app's `docs/design-sync.md` describes how a change is carried over, and its `scripts/sync-template.sh` copies the CSS, JS, vendor files, photos and PDF.

## Starting point (for a new direction or a rebuild)

1. Read the Laravel project's `CLAUDE.md`, `composer.json` and existing routes. Follow what is there.
2. Move the direction's markup into Blade, its CSS and JS into `public/assets/` (the app has no build step), and `data/*.json` into migrations and seeders.

## Target app

| Item | Value |
|---|---|
| Repository | `SubhanRaj/archipixels`, local path `~/Sites/archipixels` |
| Runtime | PHP ^8.5, Laravel 13, Livewire 4 |
| Database | MariaDB locally, MySQL on Hostinger. Migrations use only features both support. |
| Public site | Blade layout plus the chosen direction's CSS and JS from this repository, served from `public/assets/`. The templates are token-driven custom CSS, so the public side uses neither Tailwind nor Bootstrap. |
| Admin panel (later phase) | Livewire 4 with Tailwind from the Play CDN, in the style of the Excise Livewire apps (`upexcise-stats-dashboard`, `excise-budget-tracker`). Tables, filters and confirm dialogs are reused from them. |
| Front-end build | None. Hostinger shared hosting has no Node, so the public assets are vendored and the admin panel loads Tailwind from the CDN. The CDN is allowed in the admin CSP only. The public pages keep the strict CSP. |
| Testing and style | Pest 4, Laravel Pint |
| Local database setup | `php artisan db:provision` from `subhanraj/laravel-db-provisioner` (dev only) |
| Hosting | Hostinger shared hosting, deployed as in `~/Sites/infra-notes/hostinger-laravel-deploy.md` |

Build rules that apply from the first migration:

- Public detail pages bind on `slug`, never on the row id.
- Every create, update, delete and restore is a POST. Livewire actions and `fetch()` forms return without a page reload. Query strings carry navigation state only (filters, pagination).
- A write that touches more than one row runs inside `DB::transaction()`. A single `create()`, `update()` or `delete()` is already atomic and is not wrapped.
- Content models use `SoftDeletes` and an explicit `$fillable`.
- A global `SecurityHeaders` middleware sets the CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` and `Permissions-Policy`, and HSTS over HTTPS. The public CSP lists only the origins the pages load. Admin routes add the Tailwind CDN origin and inline styles. Livewire runs with `csp_safe` on.
- The enquiry form has a honeypot field, a per-IP rate limit and server-side validation.
- The public site and its CRUD actions are built before the admin panel. The admin panel is a later phase that adds screens over the same actions.

## Files to carry over

| Source | Use in Laravel |
|---|---|
| `a/` to `d/` HTML | Reference for views. Pick one direction. |
| `assets/css/core.css` | Layout and components shared by every direction. |
| `assets/css/theme-*.css` | Tokens and styling for the chosen direction. D loads `theme-a.css` and then `theme-d.css`. |
| `assets/js/core.js` | Nav, works filter, forms, lightbox and the `window.AP` helpers. |
| `assets/js/theme-*.js` | Motion for the chosen direction. D loads `theme-a.js` and then `theme-d.js`. |
| `assets/vendor/` | GSAP 3.12.5 with ScrollTrigger, Swiper 11.1.4 and GLightbox 3.3.0. Copy them to `public/assets/vendor/`. |
| `assets/img/`, `portfolio/img/` | Photos. D reads `portfolio/img/`. |
| `assets/img/brand/`, `assets/brand-originals/` | Logos, favicon and touch icon. |
| `data/*.json` | Seed data. |

## Changes still to carry into the app

These changes are in the templates and not yet in the Laravel app.

- Run `scripts/sync-template.sh` (CSS, JS, photos, `assets/img/earlier/`, the new `portfolio/img/` files and the PDF). The centred last row of the project walls is CSS only (`.d-wall` in `theme-d.css`, `.wall` in the portfolio CSS, `.grid-works` in `core.css`) and needs no markup change. `.legacy__list` also changed in `core.css`: each row is now a link.
- Four projects: poddar-mansion, mr-singhs-dwelling, house-of-mishras, house-of-agarwals, appended to `projects.json` and `portfolio.json` (the projects seeder, with colours and photo lists). Jewellery Spaces has no signature details now, and the project story and portfolio panel leave the heading out when the list is empty.
- Palette photos: a `palette` entry in `projects.json` can have a third item, a file in `assets/img/swatches/` (a photo of the material, cut from the PowerPoint). The four new projects use them. In the palette partial and D's panel swatches the photo goes on the circle (`background-image` on `.swatch__dot` and `.d-dot`, inline), and the hex stays as the fallback colour. Add a nullable image column to the palette items, and `core.css` gets `background: var(--sw) center / cover` on `.swatch__dot`.
- Headings: the home wall reads "Our projects." with the "Selected works" eyebrow (`works-wall`), the portfolio wall reads "Our projects.", and the Works page block is "Our earlier works" (no place name).
- Earlier works: `legacy-projects.json` now carries `slug`, `story` (paragraphs), local `images` (files in `assets/img/earlier/`) and `wix_images`. They need a model and table (`earlier_works`: slug, name, category, type, location, year, summary, story, images, sort), a seeder, a `/earlier/{slug}` route, a view built like `page_earlier` in `tools/build.py`, rows linking to it in the Works page, and sitemap entries. Leave out the year, location and story when they are empty.
- Download button: `assets/downloads/Archipixels-Portfolio.pdf` is the new 31-page file.

## Layout and partials

`layouts/app.blade.php` holds the head, skip link, header, footer and scripts. The generated HTML marks each partial with a `<!-- component: name -->` comment:

- A, B and C: `site-header`, `site-footer`, `hero-slideshow`, `featured-works`, `intro`, `services`, `range-band`, `homes-and-experiences`, `studio-teaser`, `cta-band`, `page-hero`, `filter-bar`, `palette`, `project-gallery`, `enquiry-form`.
- Direction D: `site-header`, `site-footer`, `hero-slideshow`, `services`, `homes-and-experiences`, `cta-band`, `page-hero`, `filter-bar`, `project-gallery` and `enquiry-form`, plus `approach`, `studio-teaser`, `team-carousel`, `team-member`, `works-wall` and `closing-line`.
- The work card has no comment. It is `.card-work` in A, B and C and `.d-tile` in D, and it appears on Works and in the related-projects row. The project hero and the story block (design language, story, signature details) have no comment either.
- A Direction D project page has these parts in order, none with a comment: A's hero and facts row, the gallery (no visible heading, arrows on the slider's edges), the story block, the palette, a next-project band, three related tiles and the call to action. The home page spotlights are three colour blocks, each a photo beside a tan panel.
- The portfolio PDF in `assets/downloads/` goes in `public/` or a storage disk, and the download buttons link to it.
- `theme-switcher` is for client preview only. Leave it out.

## Routes

| Route | Page |
|---|---|
| `/` | Home |
| `/about` | About |
| `/team` | Team: founders, then a swipeable member carousel (listed under About in the menu) |
| `/team/{slug}` | A team member's profile page. `data/team.json` is the placeholder content, and each person becomes a `team_members` row |
| `/studio` | Studio |
| `/services` | Services |
| `/works` | Works, filterable, with `#category` deep links |
| `/works/{slug}` | Project page (23 projects) |
| `/earlier/{slug}` | Earlier work detail page (`data/legacy-projects.json`, photos in `assets/img/earlier/`): header, facts, photo slider (`gallery-slider`), paragraphs and three more earlier works. The `legacy_section`, `legacy_list` and `page_earlier` functions in `build.py` map to a `legacy-list` component and an `earlier` view |
| `/contact` | Contact facts, pen drawing and enquiry form (A and D layout) |
| `/portfolio` | The one-page portfolio: the PDF as a web page that reads the same on every platform, with a button for the PDF download |

The 404 design in `404.html` of the chosen direction maps to `resources/views/errors/404.blade.php` in the live site. Keep the numeral, the two buttons, the three recent works and the call to action band.

## Data

Project fields: slug, name, by, tagline, kind, cats[], place, lit (hex), language[], details[], palette[] (name, hex and an optional photo file), card image, gallery[], story, year and area. Direction D also uses a background colour (`bg`), a layout name and a photo list with captions per project, from `data/portfolio.json`.

Studio details, founders, contact details, services and the closing line are in `data/site.json`. The menu (Works, About with About us and Team, Studio, Services, Portfolio, Contact) is the `NAV` list in `tools/build.py`. Seven earlier Lucknow projects are in `data/legacy-projects.json` with Wix image ids.

Team members and services can move to database tables once the client supplies the content.

## Rules that carry over

- Colours, fonts and shadows are tokens. Components never hold literal theme colours.
- JavaScript hides content right before it animates. CSS never hides content. `prefers-reduced-motion` turns the motion off.
- Project pages set `--lit` from the project's `lit` value and use the body class `page-project`.
- The works filter uses `data-cats`. The Laravel app runs the template's `core.js` filter. A Livewire component with the same category logic is optional.

## Before launch

This is the one list of what to decide, confirm or fill before launch. `README.md` and `CONTEXT.md` link here.

Decisions and content from the client:

- The client picks a direction, or a mix. Update `CLAUDE.md` when that happens.
- Confirm the contact details. The portfolio gives `1/146, Gomti Nagar, Lucknow` and `hello@archipixels.com`. The old Wix site gave `B-2, 1222, DLF MyPad, Vibhuti Khand, Gomtinagar` and `info@archipixels.com`. The templates use the portfolio values.
- The Studio page's map card loads the Google embed after a click, so the cookie policy should mention Google Maps as a service that sets cookies once the visitor loads the map. `maps_url` and `maps_embed` in `data/site.json` become `site_settings` keys, and the components are `map-card` and the existing `project-gallery` (used for the studio slider too).
- Social profiles are `instagram`, `linkedin` and `facebook` in `data/site.json`, and become `site_settings` keys. The seeded `linktree` key and the Linktree link in the footer are removed. The footer's Follow column, the Contact page's Social hover icons and the structured data `sameAs` use all three.
- Fill the placeholders (they show with a dashed underline): `[YEAR]`, `[AREA IN SQ FT]`, `[LOCATION]` and `[PROJECT STORY]` on each project page, `[ROLE]` and `[SHORT BIO]` for each founder, the team member cards, `[STUDIO HOURS AND HOW TO BOOK A VISIT]` on the studio page and `[TURNKEY EXAMPLES]` on the services page.
- Write the real project stories. The text on each project page comes only from the portfolio facts.
- Replace the placeholder team in `data/team.json` (6 members and the founders' roles, intros and bios) when the client supplies it. Each person's profile page needs a photo, role, intro, bio, year joined and focus areas.
- Check the colour swatches. The names come from the portfolio and the hex values were estimated by eye.
- Confirm the Dubai mentions in D's About page, which repeats A's story.

Images:

- Replace the PDF crops with original photos. The crops are about 1000 px wide in A, B and C and 600 to 1,600 px wide in D and the portfolio.
- Check the earlier-works text with the client. `data/legacy-projects.json` holds seven earlier works with their photos downloaded and compressed into `assets/img/earlier/`. The paragraphs are paraphrased from the old Wix pages, and three of the seven have no description at all.

Direction D and the portfolio version:

- The PDF backgrounds for Warehouse Studio, Pixel Pop and Chat House are black. The pages use a deep green, a near-black and a deep blue taken from their palettes.
- Check the closing script line and the photo captions on a device with web fonts loaded.
- Open the chosen direction on a real iPhone, iPad and Mac in Safari. The WebKit test on Linux cannot show the iOS toolbar height or the iOS 15 fallbacks.

Build:

- Wire the enquiry forms to a POST route with validation, CSRF, spam protection and a notification. They show a thank-you message and send nothing yet.
- Remove the `theme-switcher` block from the footer markup, the chooser page (`index.html`) and the directions that are not used.
- Point the Back to site link on the portfolio page (`../index.html` in the templates) at the home route.
- Use absolute URLs for `og:image` and the JSON-LD `logo`, which are relative paths in the templates. Add `canonical`, `og:url` and `twitter:card` tags with the live domain.
