# Archipixels website templates

Static HTML, CSS and JavaScript templates for four dark design directions (A, B, C and D). The client picks one, and it is then built in Laravel (Blade). The developer continues that build in his own local Laravel environment. `LARAVEL.md` describes how these files map to a Laravel app.

| Folder | Direction | Look |
|---|---|---|
| `a/` | Velvet Night | Oxblood-black, antique gold. Bodoni Moda and Jost. |
| `b/` | Gallery Noir | Near-black with bone-coloured type and one accent colour per project. Cormorant Garamond and Hanken Grotesk. |
| `c/` | Midnight Bazaar | Deep teal, marigold, stickers and hard shadows. Rozha One and Karla. |
| `d/` | Velvet Portfolio | The one-page portfolio laid out as a multi-page site in the style of A. Bodoni Moda, Jost and Herr Von Muellerhoff. |

Open `index.html` to pick a direction. A small A · B · C · D switcher at the bottom left of every page opens the same page in another direction. The list comes from `SWITCH` in `tools/build.py`.

## Portfolio version (one page)

`portfolio/index.html` is a separate version. It is the PDF portfolio as one scrolling page, and it does not use the `a/`, `b/` or `c/` templates.

Order: cover slideshow, approach, founders, a wall of all 19 projects, the 19 project sections (each in the background colour of its PDF page, with a tan panel, colour swatches, design language and signature details), studio, team, contact with an enquiry form and a WhatsApp button, and the closing line.

- `portfolio/css/portfolio.css` and `portfolio/js/portfolio.js` hold the styling and motion.
- `portfolio/img/` holds the photos cut from the PDF.
- `tools/build_portfolio.py` generates the page from `data/site.json`, `data/projects.json` and `data/portfolio.json`. `data/portfolio.json` holds each project's background colour, photo list, captions and sampled swatch colours.
- It reuses the logos in `assets/img/brand/` and the libraries in `assets/vendor/`.
- Fonts: Playfair Display, Cormorant Garamond, Jost and Herr Von Muellerhoff (the closing script line), all from Google Fonts.

Regenerate it with `python3 tools/build_portfolio.py`. The command does not touch the other directions.

## Direction D (Velvet Portfolio)

`d/` merges the one-page portfolio with the multi-page structure and style of Direction A. It has 26 pages: Home, About, Team, Studio, Services, Works, Contact and 19 project pages. The header menu is Works, About (with About us and Team below it), Studio, Services and Contact.

- Home: hero slideshow, approach, founders, three spotlight projects in their own colours, the works wall and the closing line.
- Works: a filterable wall of all 19 projects.
- Project pages: a full-colour section for the project (photos, tan panel, swatches, design language, signature details, story), a Gallery slider with lightbox (Swiper and GLightbox, as on A's project pages, with every photo of the project), a next-project band, related projects and an enquiry call to action. Warehouse Studio has one photo, so its gallery has one slide and no arrows.
- About, Studio and Services come from Direction A's templates and use A's styling. The Studio page keeps one placeholder, `[STUDIO HOURS AND HOW TO BOOK A VISIT]`.
- `tools/build_d.py` generates `d/`. It imports `tools/build.py` for the shared header, footer and pages and `tools/build_portfolio.py` for the colour helpers. `build.py` has one addition for D, the `SWITCH` list.
- `assets/css/theme-d.css` and `assets/js/theme-d.js` hold the D components and motion. D also loads `theme-a.css` and `theme-a.js`, so the body class is `theme-a theme-d`.
- D reads its photos from `portfolio/img/` and the closing logo from `assets/brand-originals/logo-stacked-light.png`, so keep both in the package.
- Project text, colours and swatches come from `data/portfolio.json`, `data/projects.json` and `data/site.json`.

Regenerate it with `python3 tools/build_d.py`. The command does not touch `a/`, `b/`, `c/` or `portfolio/`.

## Pages

Directions A, B and C have the same pages (D is described above):

- `index.html` (home)
- `about.html`, `studio.html`, `team.html`, `services.html`
- `works.html` (filterable list of 19 projects, plus a text list of earlier Lucknow work)
- `projects/<slug>.html` (19 project pages)
- `contact.html`

## Folder layout

```
index.html              direction chooser (client preview only)
portfolio/              one-page portfolio version (own css, js and img)
a/ b/ c/ d/            one complete site per direction
assets/css/core.css     layout and components, shared by all directions
assets/css/theme-*.css  tokens and styling for each direction (theme-d.css adds to theme-a.css)
assets/js/core.js       nav, header, works filter, forms, lightbox, shared helpers (window.AP)
assets/js/theme-*.js    motion for each direction
assets/vendor/          GSAP 3.12.5 with ScrollTrigger, Swiper 11.1.4, GLightbox 3.3.0
assets/img/             photos cropped from the portfolio PDF
assets/img/brand/       logo variants for the dark themes, favicon, touch icon
assets/brand-originals/ logo files as supplied
moodboards/             one mood board PNG each for A, B, C, D and the one-page portfolio, plus moodboards-overview.png with all five
data/                   site.json, projects.json, legacy-projects.json
tools/build.py          generates every page of a/, b/ and c/ from data/
tools/build_portfolio.py generates portfolio/index.html from data/
tools/build_d.py        generates d/ from data/ and the shared build.py helpers
```

Regenerate the pages after changing data or markup:

```
python3 tools/build.py
python3 tools/build_d.py
```

The first command builds `a/`, `b/` and `c/`. The second builds `d/`.

## Laravel build

The templates are the design reference for the Laravel site. The Laravel project follows the developer's own conventions, so read its `CLAUDE.md` and `composer.json` before adding code to it. `LARAVEL.md` lists the layout, partials, routes, models and seed data that the templates imply. `CLAUDE.md` holds the rules for Claude Code.

## Libraries and motion

There is no JS framework and no build step. GSAP and ScrollTrigger handle parallax, reveals and the pinned horizontal scroll. Swiper handles the slideshows and GLightbox the gallery lightbox. Fonts load from Google Fonts.

Motion respects `prefers-reduced-motion`. Only JavaScript hides content before an animation, so the pages stay readable when scripts fail.

## Mood boards

`moodboards/` holds a 1620 x 2340 px board for each direction (A, B, C and D) and for the one-page portfolio. Each board shows the palette, type, components and photos of that version. `moodboards-overview.png` puts all five side by side. The boards are images only and are not used by the site.

## Logo

The supplied logos have a transparent white version for each dark theme in `assets/img/brand/`: horizontal in the header, stacked in the footer. The favicon and touch icon are built from the mark. The white versions were derived from the supplied files, so replace them if the studio has a native white or reversed logo.

## To do before launch

- Confirm the contact details. The portfolio gives `1/146, Gomti Nagar, Lucknow` and `hello@archipixels.com`. The old Wix site gave `B-2, 1222, DLF MyPad, Vibhuti Khand, Gomtinagar` and `info@archipixels.com`. The templates use the portfolio values.
- Fill the placeholders, which show with a dashed underline: `[YEAR]`, `[AREA IN SQ FT]`, `[LOCATION]` and `[PROJECT STORY]` on each project page, `[ROLE]` and `[SHORT BIO]` for each founder, the team member cards, `[STUDIO HOURS AND HOW TO BOOK A VISIT]` on the studio page and `[TURNKEY EXAMPLES]` on the services page.
- Write the real project stories. The text on each project page comes only from the portfolio facts.
- Check the colour swatches. The names come from the portfolio and the hex values were estimated by eye.
- Delete the `theme-switcher` block from the footer markup.
- Wire the forms to a Laravel route with validation, CSRF and a mail notification. They currently show a thank-you message and send nothing.
- Download the old-site photos. `data/legacy-projects.json` lists seven earlier Lucknow projects with Wix image ids (`https://static.wixstatic.com/media/<id>`). They appear as a text list on the works page.
- Replace the PDF crops, which are about 1000 px wide, with original photos.

Direction D only:

- D uses the PDF crops in `portfolio/img/`. Replace them with the original renders for large screens.
- The Studio placeholder above is the only open text. The Team page lists the two founders and no placeholders.
- A's hero caption and pagination share a flex row that squeezes the caption on narrow screens. D has its own fix in `theme-d.css`. The same fix is not applied in `theme-a.css`.
- The About page repeats the A story, which still mentions Dubai. Check it with the client.

Portfolio version only:

- The photos are cut from the PDF and are 600 to 1,600 px wide. Replace them with the original renders for large screens.
- Project backgrounds for Warehouse Studio, Pixel Pop and Chat House are black in the PDF. The page uses a deep green, near-black and deep blue taken from their palettes.
- The enquiry form shows a thank-you message and sends nothing. Wire it to a mail route.
- The studio and team sections use the PDF photos only. Add individual team members when the client supplies them.
- The closing script line and the photo captions need a check on a device with web fonts loaded.
