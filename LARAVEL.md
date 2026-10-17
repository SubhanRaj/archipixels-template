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

- A, B and C: `site-header`, `site-footer`, `hero-slideshow`, `featured-works`, `intro`, `services`, `range-band`, `homes-and-experiences`, `studio-teaser`, `cta-band`, `page-hero`, `filter-bar`, `palette`, `project-gallery`, `enquiry-form`.
- Direction D: `site-header`, `site-footer`, `hero-slideshow`, `services`, `homes-and-experiences`, `cta-band`, `page-hero`, `filter-bar`, `project-gallery` and `enquiry-form`, plus `approach`, `founders`, `works-wall` and `closing-line`.
- The work card has no comment. It is `.card-work` in A, B and C and `.d-tile` in D, and it appears on Works and in the related-projects row. The project hero and the story block (design language, story, signature details) have no comment either.
- A Direction D project page has these parts in order, none with a comment: A's hero, a wrapper (`.d-tone`) coloured with the project's `bg` that holds the facts row, the story block, the palette on a tan panel and the gallery, a next-project band, three related tiles and the call to action. The home page spotlights are three colour blocks, each a photo beside a tan panel.
- The portfolio PDF in `assets/downloads/` goes in `public/` or a storage disk, and the download buttons link to it.
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
| `/portfolio` | The one-page portfolio: the PDF as a web page that reads the same on every platform, with a button for the PDF download |

## Data

Project fields: slug, name, by, tagline, kind, cats[], place, lit (hex), language[], details[], palette[] (name and hex), card image, gallery[], story, year and area. Direction D also uses a background colour (`bg`), a layout name and a photo list with captions per project, from `data/portfolio.json`.

Studio details, founders, contact details, services and the closing line are in `data/site.json`. The menu (Works, About with About us and Team, Studio, Services, Portfolio, Contact) is the `NAV` list in `tools/build.py`. Seven earlier Lucknow projects are in `data/legacy-projects.json` with Wix image ids.

Team members and services can move to database tables once the client supplies the content.

## Rules that carry over

- Colours, fonts and shadows are tokens. Components never hold literal theme colours.
- JavaScript hides content right before it animates. CSS never hides content. `prefers-reduced-motion` turns the motion off.
- Project pages set `--lit` from the project's `lit` value and use the body class `page-project`.
- The works filter uses `data-cats`. It can run on Alpine.js or Livewire if the Laravel project already uses one of them.

## Before launch

This is the one list of what to decide, confirm or fill before launch. `README.md` and `CONTEXT.md` link here.

Decisions and content from the client:

- The client picks a direction, or a mix. Update `CLAUDE.md` when that happens.
- Confirm the contact details. The portfolio gives `1/146, Gomti Nagar, Lucknow` and `hello@archipixels.com`. The old Wix site gave `B-2, 1222, DLF MyPad, Vibhuti Khand, Gomtinagar` and `info@archipixels.com`. The templates use the portfolio values.
- Fill the placeholders (they show with a dashed underline): `[YEAR]`, `[AREA IN SQ FT]`, `[LOCATION]` and `[PROJECT STORY]` on each project page, `[ROLE]` and `[SHORT BIO]` for each founder, the team member cards, `[STUDIO HOURS AND HOW TO BOOK A VISIT]` on the studio page and `[TURNKEY EXAMPLES]` on the services page.
- Write the real project stories. The text on each project page comes only from the portfolio facts.
- Add individual team members when the client supplies them. The studio and team sections use the PDF photos only.
- Check the colour swatches. The names come from the portfolio and the hex values were estimated by eye.
- Confirm the Dubai mentions in D's About page, which repeats A's story.

Images:

- Replace the PDF crops with original photos. The crops are about 1000 px wide in A, B and C and 600 to 1,600 px wide in D and the portfolio.
- Download the old-site photos. `data/legacy-projects.json` lists seven earlier Lucknow projects with Wix image ids (`https://static.wixstatic.com/media/<id>`). They appear as a text list on the works page.

Direction D and the portfolio version:

- The PDF backgrounds for Warehouse Studio, Pixel Pop and Chat House are black. The pages use a deep green, a near-black and a deep blue taken from their palettes.
- Check the closing script line and the photo captions on a device with web fonts loaded.
- Open the chosen direction on a real iPhone, iPad and Mac in Safari. The WebKit test on Linux cannot show the iOS toolbar height or the iOS 15 fallbacks.

Build:

- Wire the enquiry forms to a POST route with validation, CSRF, spam protection and a notification. They show a thank-you message and send nothing yet.
- Remove the `theme-switcher` block from the footer markup, the chooser page (`index.html`) and the directions that are not used.
- Point the Back to site link on the portfolio page (`../index.html` in the templates) at the home route.
- Use absolute URLs for `og:image` and the JSON-LD `logo`, which are relative paths in the templates. Add `canonical`, `og:url` and `twitter:card` tags with the live domain.
