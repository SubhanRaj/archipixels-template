# CLAUDE.md

This repository holds static HTML, CSS and JS templates (four dark directions: A, B, C and D) for Archipixels, an architecture and interior studio in Lucknow. The website will be built in Laravel (Blade). These templates are the design reference for that build. The developer continues the work in his own local Laravel environment and in the style of his existing Laravel projects.

Read `CONTEXT.md` first. It holds the brief, the design language of each direction and the decisions made so far. This file holds the working rules.

The Laravel site is built on Direction D. A, B and C stay in the repository as references and are not built into the app.

The templates use no JS framework and no bundler. GSAP, Swiper and GLightbox are vendored in `assets/vendor/`.

## Working rules

- Pages are generated. Edit `tools/build.py` and `data/*.json`, then run `python3 tools/build.py`. Do not edit the HTML in `a/`, `b/`, `c/` or `d/` by hand. `d/` is built by `tools/build_d.py`.
- Colours, fonts and shadows are tokens (`--bg --surface --band --line --text --muted --accent --accent-ink --font-display --font-body --radius --shadow-card --lit`) set per direction in `assets/css/theme-*.css`. `core.css` has no theme colours.
- Social profiles (Instagram, LinkedIn, Facebook) come from `data/site.json` through `social_links()` in `build.py`. The footer, the contact pages and the structured data use it, and the portfolio page has its own icon markup in `build_portfolio.py`. Linktree is not used anywhere. In the footer the Instagram entry reads "Instagram" with no username. The footer's WhatsApp line and address are links that open in a new tab. Link labels say "Contact us", never "Contact page".
- The header menu is shared. On screens up to 1100 px wide the About submenu starts closed and opens with the `.sub-toggle` button (`core.css`, `core.js`). On wider screens it opens on hover or focus.
- Hero and slider markup is shared across directions. Each theme's JS picks the effect (fade, creative, cards or coverflow).
- JavaScript hides content before an animation (`gsap.set`). CSS never does. Keep it that way, and keep the `prefers-reduced-motion` handling.
- Project text comes from the portfolio. Missing facts stay as bracket placeholders such as `[YEAR]` and `[PROJECT STORY]`.
- The site covers every kind of client. Dubai appears in the About story and on the Warehouse Studio and Chat House project pages only.
- Project walls (the D home and Works walls, the Works grid in A, B and C, and the portfolio's wall) are flex rows: four columns on desktop, three on tablet and two on phones (A, B and C: three, two and one). On tablet and desktop an incomplete last row is centred, so there is no empty cell at the end whatever the number of projects. Do not turn them back into CSS grids.
- The home page and Works headings do not state a project count ("Our projects.", not "All 23 projects."), and the earlier work is called "Our earlier works" with no place name. Each earlier work has a detail page, `earlier/<slug>.html` (`page_earlier` in `build.py`, shared by all four directions), built from `data/legacy-projects.json`. Photos are in `assets/img/earlier/` and the page leaves out any fact or paragraph that is empty in the data.
- Project photos are cropped at their native pixels from the slide collages in the client's PDF or PowerPoint (`assets/portfolio/`, ignored by git) and saved as JPEG quality 90 with no chroma subsampling. The PDF has no larger originals for the collage slides, so a photo cannot be larger than its crop. After adding or re-cropping photos, run `python3 tools/check_images.py`: it fails on a photo that decodes but is blank, such as a soft mask pulled out of the PDF instead of the picture.
- A palette entry in `data/projects.json` is `[name, hex]` or `[name, hex, "swatches/<file>.jpg"]`. The third item is a photo of the material (marble, slate, bronze), cut from the swatch images in the PowerPoint, and `swatch_bg` in `build.py` (also used by `build_d.py` and `build_portfolio.py`) puts it on the circle. The four newest projects have them. B shows the photo in its rectangle.
- Logos are in `assets/img/brand/` (white, transparent, for the dark themes). Originals are in `assets/brand-originals/`.

Frozen designs
- The home page of every version (A, B, C and D) is final and locked. Do not change it, and do not let a shared-code change reach it, unless the developer asks. After a build, check that each `index.html` is unchanged in git.
- The design of A, B and C is final. Do not change their layout, styling or content.
- You may fix mistakes in them: broken links, stale text in docs and comments, markup errors, bugs, and accessibility or contrast defects.
- A new site-wide change (a link, a button, a feature) goes into every version where it suits. Build it once in the shared source and style it with each version's existing classes. Add a rule to a theme file only when the existing classes do not cover it.
- C is not the current pick because its pop style did not suit the client, and the design is sound. It receives every site-wide change like A and B, and its elements can be reused elsewhere.

Effort
- Rebuild only the builders whose output the change touches.
- Check only the pages the change touches: one page per version, at 1440 and 390 px.
- Run the full link and console check only when the developer asks for it.
- State the files you will edit and the versions each edit reaches before you make the change.

## Pages

Home, About, Studio, Team, Services, Works, Contact, one page per project (23), one detail page per earlier work (`earlier/<slug>.html`, from `data/legacy-projects.json`) and one profile page per team member (`team/<slug>.html`, from `data/team.json`). Each direction builds all of them, plus a `404.html` with root-relative paths, because Cloudflare Pages serves it at the missing URL. `build.py` also writes the root `404.html` from `tools/root-404.tpl`.

## Laravel build

The Laravel app lives in its own repository, `SubhanRaj/archipixels`, at `~/Sites/archipixels`. Read `LARAVEL.md` for the mapping from these files to that app. The rules for the build:

- The Laravel app already carries Direction D. Design changes are made here, then carried over: the developer runs `scripts/sync-template.sh` in the Laravel repository for the CSS, JS, photos and PDF, and edits the matching Blade component for markup. `docs/design-sync.md` in that repository maps each `build.py` and `build_d.py` function to its Blade file. When a change touches D's markup or classes, say which components need the same edit.
- The Laravel project is where the site lives. Before writing Laravel code, read that project's own `CLAUDE.md`, `composer.json`, routes and existing folder layout, and follow its conventions for structure, naming, formatting, testing and front-end tooling. Where the project has no convention for something, ask the developer before choosing.
- Do not assume PHP, Laravel, database or Livewire versions. Take them from the project.
- The Python generators (`tools/build*.py`) exist only to produce the templates. Blade views and partials replace them. Do not port the generators.
- `data/*.json` is seed data. `site.json` holds the studio details, `projects.json` the 23 projects, `portfolio.json` the Direction D and portfolio colours, swatches and photo lists, and `legacy-projects.json` the earlier works (a project, its local photos in `assets/img/earlier/` and its text).
- Keep the design tokens, the markup structure and the motion rules when moving a direction. Copy the CSS and JS into the app's `public/assets/`. The app has no build step.
- Remove the `theme-switcher` block, the unused directions and `index.html` (the chooser) from the app.
- The forms need a POST route, validation, CSRF protection, spam protection and a notification before launch.

## Blade conversion plan

- `layouts/app.blade.php` holds the head, header, footer and scripts. Keep the chosen direction's CSS and JS (for D, `theme-a` and `theme-d` together) and drop the rest and the `theme-switcher`.
- The `<!-- component: name -->` comments in the generated HTML mark the partials. A, B and C use `site-header`, `site-footer`, `team-carousel`, `team-member`, `hero-slideshow`, `featured-works`, `intro`, `services`, `range-band`, `homes-and-experiences`, `studio-teaser`, `cta-band`, `page-hero`, `filter-bar`, `palette`, `project-gallery` and `enquiry-form`. Direction D uses `site-header`, `site-footer`, `hero-slideshow`, `services`, `homes-and-experiences`, `cta-band`, `page-hero`, `filter-bar`, `project-gallery`, `enquiry-form`, `studio-teaser` (A's, with the team photo strip), `team-carousel` and `team-member`, and adds `approach`, `works-wall` and `closing-line`. The footer also carries a `theme-switcher` comment.
- Some markup has no comment but is a partial in the same way: the work card (`.card-work` in A, B and C, `.d-tile` in D), which appears on Works and in the related-projects row, and the project hero and story block. Direction D's project page is described under Direction D below.
- Projects become an Eloquent model with slug, name, by, tagline, kind, cats, place, lit (hex), language[], details[], palette[], card image, gallery[], story, year and area. `data/projects.json` seeds it.
- The works filter runs as a Livewire component with the same categories (`/works?category=...`). The static templates keep the `data-cats` filter and `works.html#category` deep links in `core.js`.
- Project pages take the body class `page-project` and set `--lit` from `$project->lit`.
- The contact form needs a POST route, validation, CSRF, spam protection and a notification.
- Team members and services can move to database tables once the client supplies the content.

## Open items

The Before launch section of `LARAVEL.md` lists what to confirm or fill before launch.

## Portfolio version

`portfolio/` is a one-page version of the PDF portfolio. It is separate from directions A, B and C and does not use `build.py`.

- Generate it with `python3 tools/build_portfolio.py`. The sources are the generator, `data/portfolio.json` and `portfolio/css|js`. Do not edit the HTML.
- Each project section takes its colour from `data/portfolio.json` (`bg`). Text colour is picked by contrast in the generator. The tan panel stays the same on every project.
- Photos live in `portfolio/img/`. Add a project by adding it to `data/projects.json` and `data/portfolio.json`, then rebuild.
- Motion follows the same rule as the directions: JavaScript hides content right before animating it, and `prefers-reduced-motion` turns the motion off.
- Studio and team come after the projects on purpose, as the client asked.
- The page opens with an arrival veil: `.veil` in `portfolio.css`, written by `header()` in `build_portfolio.py`. The logo and a gold line show on the cover colour, then the veil wipes upward (CSS keyframes, about 2 seconds in all, removed by `prefers-reduced-motion`). It is CSS only so it never waits for a script and cannot get stuck, and it plays on every load, whether the visitor comes from the site, another address or opens the page directly. `portfolio.js` delays the cover timeline by 1.1 seconds to follow it. The page has no skip link. In Direction D, `theme-d.js` fades the screen to the same colour (`.leave-veil` in `theme-d.css`) when a visitor clicks a link to the portfolio, so the move between the two looks has no flash. A page restored by the back button removes the fade.
- The top bar has a Back to site link. `portfolio.js` points it at the version the visitor came from (read from the referrer) and otherwise at `../index.html`, which is the chooser in the templates.

## Direction D

`d/` merges the one-page portfolio with the multi-page approach of Direction A. It has 45 pages plus the 404 and the same nested menu as the other directions (About holds About us and Team).

- Generate it with `python3 tools/build_d.py`. The sources are the generator, `assets/css/theme-d.css`, `assets/js/theme-d.js` and `data/*.json`. Do not edit the HTML.
- `build_d.py` imports `build.py` and `build_portfolio.py` and reuses their functions. It replaces `b.write` at runtime and registers `b.THEMES['d']`, so `python3 tools/build.py` does not build D. The preview switcher in every footer lists `SWITCH` from `build.py` (A, B, C and D).
- The body class is `theme-a theme-d`. D loads `theme-a.css` and `theme-a.js` first, then adds its own files. The A tokens apply, and D adds the colour-section components (`.d-pj`, `.d-panel`, `.d-swatches`, `.d-next`, `.d-wall`, `.d-closing`).
- A Direction D project page is A's page with the gallery moved up. `page_project` in `build_d.py` calls `project_hero_a`, `project_gallery` (with `inline=True`), `project_story` and `project_palette` from `build.py`, in that order, so the black background, palette and slider follow A's classes. The gallery lists the project's photos from `data/portfolio.json`, which are single shots where A's list has collages. With `inline`, the "Gallery" heading is visually hidden (`sr-only`, kept for screen readers and search engines) and the arrows sit on the slider's left and right edges (`.gallery--inline`, `.gallery__stage` in `theme-d.css`). `theme-d.css` also trims the padding above the gallery and above the story. The page has no colour wrapper. A next-project band (`.d-next`, in the next project's colour from `data/portfolio.json`) and three related tiles (`.d-tile` in `.d-wall--three`) follow the palette, then the call to action. The related row is three across and one per row at 640 px and below. None of these has a component comment.
- The home hero is A's (`hero_a` in `build.py`), called with D's marquee names. `hero--d` in `theme-d.css` keeps the headline on two lines from 760 px up.
- The home page spotlights (`pj_block`) are three colour blocks, each a photo beside a tan panel (`.d-pj`, `.d-panel`). They have no component comment either. From 1001 px up, `theme-d.css` trims the panel's spacing and makes the photo fill the row height (cropped, not stretched), so neither column has empty space.
- The compressed portfolio PDF is `assets/downloads/Archipixels-Portfolio.pdf` (10.6 MB, 31 pages). Replace the file with the same name to update every download button. The full-size PDF and PowerPoint from the client sit in `assets/portfolio/`, which git ignores; compress a new PDF with Ghostscript at 100 dpi (`-dPassThroughJPEGImages=false -dColorImageResolution=100`, JPEG `QFactor` 0.76, 2x2 chroma sampling), and take project photos from the slide collages (crop each photo from the slide image in the PowerPoint's `ppt/media`). The links read "Get our portfolio", open the PDF in a new tab and do not state a file size or format. The one-page portfolio's own buttons read "Download portfolio".
- Browser support: the header and veil rules keep a plain `rgba()` fallback before each `color-mix()`, and `-webkit-backdrop-filter` sits beside `backdrop-filter`, for iOS 15 Safari. Keep this pattern in new rules. `--bg-rgb` and `--text-rgb` in each theme feed the fallbacks.
- Photos come from `portfolio/img/` and the closing logo from `assets/brand-originals/logo-stacked-light.png`. Keep both when moving D.
- The Contact page layout (facts row, pen drawing, form) is shared with A. Its rules are `.contact-facts`, `.contact-split`, `.contact-art` and `.contact-wa` in `theme-a.css`, built by `contact_split` in `build.py`. D adds the portfolio link under the form.
- About, Studio, Services and Team are A's pages with D's header and footer, and the home page's founders block is A's `studio` teaser with the team photo strip. The Team page and the member profile pages are shared by all four directions (`page_team`, `page_member`, `team_carousel` in `build.py`). Members come from `data/team.json`, whose text is placeholder until the client supplies it. The carousel is Swiper (`.team-swiper`, started in `core.js`), and each card links to the member's page. In D the cards rise in one after another when the row comes into view (`theme-d.js`).
- The Studio page (shared by all four directions) has a photo mosaic, an "Inside the studio" gallery slider (`gallery_slider` in `build.py`, the same slider as a project gallery) and a Visit the studio section with a map card (`map_card`). The map is a Google embed that loads only after a click on "Show the map" (`.map-card`, started in `core.js`), so the page sets no Google cookies until then, which fits the no-cookie-banner decision. Its dark look is a CSS filter on the iframe. The embed and place addresses are `maps_embed` and `maps_url` in `data/site.json`. The Contact page stays minimal: its address links to `maps_url`. The Studio page has one placeholder, `[STUDIO HOURS AND HOW TO BOOK A VISIT]`.
- In the Blade conversion, D's gallery reuses the `project-gallery` partial. The other D components are listed under the Blade conversion plan.
