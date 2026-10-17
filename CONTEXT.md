# CONTEXT.md

Project context for the Archipixels website templates. Read this file at the start of a new session. It holds the brief, the design language of each direction and the decisions made so far. `CLAUDE.md` holds the working rules, `README.md` the overview and `LARAVEL.md` the Laravel mapping and the list to settle before launch.

## 1. Project

- Client: Archipixels, an architecture and interior design studio in Gomti Nagar, Lucknow. Founded in 2018 by Shivika and Abhinav, who started in Dubai before founding the studio in India. The studio now wants to take its work abroad.
- Developer: Subhan, who leads the agency and IT side. He reviews the templates with the client, then builds the live site in Laravel (Blade) in his own local environment and style.
- Deliverable in this repository: four complete multi-page directions (A, B, C, D), a one-page portfolio and a chooser page. All of them use the same 19 projects and the same copy.
- Live preview: https://archipixels-template.pages.dev (Cloudflare Pages, no build step, a Pages Functions middleware blocks the dev files, `_headers` sets `X-Robots-Tag: noindex, nofollow`). The repository is `SubhanRaj/archipixels-template`.
- The live site goes in a different folder and a different repository (`archipixels`). This repository stays the design reference.

## 2. Source material

The content comes from the studio's PDF portfolio (`Archipixels_Portfolio_1.pdf`, 26 landscape pages at 1440 x 810, 101 MB). Photos were cut from the PDF, so they are 600 to 1,600 px wide.

What the PDF looks like, which drives the whole design:

- Burgundy pages for the intro, founders and team.
- A tan panel (`#C3A17E`) on each project page, holding the name, tagline, a set of gold-ringed colour swatches, the design language and the signature details.
- A different full-page background colour for each project, taken from that project's palette.
- Large serif headlines in capitals, a script signature face for the closing line, and photographs cropped tightly against the colour.

Studio facts (in `data/site.json`):

- Tagline: "Spaces with stories of their own."
- Descriptor: "Architecture · Interiors · Experiences"
- Sign-off: "Design that works."
- Closing line: "Let's create something the world hasn't seen yet!"
- Services: Architecture, Interior design, Space planning, Turnkey projects.
- Contact (from the portfolio): `hello@archipixels.com`, `+91 99996 60533` (WhatsApp), `1/146, Gomti Nagar, Lucknow`. The old Wix site gave a different address and `info@archipixels.com`. The client confirms both.
- Instagram `@archipixels`, Linktree `linktr.ee/archipixels`.
- The Homes collection is Jamboree, Ghar-Aana and Mandala Maasai (themed rental homes).

Voice: short, specific sentences. The studio says it never repeats a design and that each project starts from a different story. The site covers every kind of client. Dubai appears in the About story and on the Warehouse Studio and Chat House project pages only.

### The 19 projects

| Project | Kind | Accent (`lit`, used by A, B and C) | Page colour (`bg`, used by D and the portfolio) |
|---|---|---|---|
| Helios Maximus | Themed rental home | `#C8283C` | `#3C0C36` |
| Archipixels Homes | Themed rental homes | `#2D6BD1` | `#A34927` |
| Chihiro | Bakehouse | `#A5C27B` | `#93954C` |
| Warehouse Studio | Workplace, Al Quoz, Dubai | `#2F8F5B` | `#0D1F1A` |
| The Deco Grand | Hotel | `#C9A24B` | `#373321` |
| The Heritage Mosaic | Hotel | `#D2673E` | `#6C5242` |
| Hons, Grey Opera | Lounge | `#3F6FD8` | `#423931` |
| Bajpayee Kachori Bhandar | Eatery | `#F2B01E` | `#38627E` |
| Buttercup Bungalow | Residence | `#C9A24B` | `#3E2109` |
| Danzeria by Danbro | Restaurant | `#C23A55` | `#580007` |
| KSMB Marketing Office | Marketing office | `#4A9BC9` | `#3B3737` |
| Mio Marito Gelato | Gelateria | `#D9744F` | `#AD2C03` |
| Pixel Pop | Salon | `#F6C21E` | `#120F12` |
| Chat House, India Club | Restaurant, Dubai | `#2BA9D6` | `#0B2A38` |
| Jewellery Spaces | Jewellery stores | `#C9A24B` | `#96A4AA` |
| Shreeya Vista Homes | Residential township | `#E8B9A0` | `#5C3D28` |
| House of Narula | Residence | `#7FA8D6` | `#515036` |
| Kesarwani Residence | Residence | `#C25C3A` | `#5C3D28` |
| The Quiet Abode | Residence | `#C99B5B` | `#E1D0C5` |

Seven earlier Lucknow projects are in `data/legacy-projects.json` (Wix image ids) and appear as a text list on the works page in A, B and C.

## 3. The design idea

Every direction treats the studio's site as a gallery that the visitor walks through. The photographs carry the page, the type is a large high-contrast serif and the colour comes from the projects. All directions are dark because the studio's work is saturated and lit, and it looks best against a dark ground.

What holds across directions:

- Each direction has one idea, used everywhere: gold on oxblood (A), one lit colour per project (B), street-poster colour (C), the project's own page colour (D).
- Display type is large, with space around it. Headlines reveal word by word or line by line.
- Photographs are the largest element on any screen. They sit in frames, wipe open on scroll and drift slightly as the page moves.
- Colour swatches are round dots ringed in gold, with the colour's name below.
- Pages stay readable without the animation.
- Each project has its own identity inside the shared layout. The studio says it never repeats a design.

## 4. Shared system

### Tokens

`core.css` holds layout and components and no theme colours. Each theme sets these tokens on its body class in `assets/css/theme-*.css`:

`--bg --surface --band --line --text --muted --accent --accent-ink --font-display --font-body --radius --shadow-card --lit`, plus `--bg-rgb` and `--text-rgb` (comma-separated channels used by the Safari 15 fallbacks).

### Components (marked by `<!-- component: name -->` comments)

A, B and C use `site-header`, `site-footer`, `hero-slideshow`, `featured-works`, `intro`, `services`, `range-band`, `homes-and-experiences`, `studio-teaser`, `cta-band`, `page-hero`, `filter-bar`, `palette`, `project-gallery` and `enquiry-form`. D uses `site-header`, `site-footer`, `hero-slideshow`, `services`, `homes-and-experiences`, `cta-band`, `page-hero`, `filter-bar`, `project-gallery` and `enquiry-form`, and adds `approach`, `founders`, `works-wall` and `closing-line`. The footer also carries a `theme-switcher` comment.

The work card (`.card-work` in A, B and C, `.d-tile` in D), the project hero and the project story block have no comment. D's project page is A's hero followed by a wrapper (`.d-tone`) in the project's colour that holds the facts row, the story, the palette on a tan panel and the gallery, then a next-project band, three related tiles and the call to action. D's home page spotlights are three colour blocks, each a photo beside a tan panel.

### Header and navigation

- Menu: Works, About (About us, Team), Studio, Services, Portfolio, Contact. Portfolio opens the one-page portfolio, which shows the PDF as a web page that reads the same on every platform. The PDF opens from one "Get our portfolio" link in every footer. The list is `NAV` in `tools/build.py`.
- Desktop: the About submenu opens on hover or focus.
- Up to 1100 px: the menu is a full-width drawer. The About submenu starts closed and opens with the chevron `.sub-toggle` button.
- The header is transparent over the hero with a soft top scrim, and turns solid with a blur once the page scrolls.
- A preview-only switcher at the bottom left of every page lists A, B, C and D (`SWITCH` in `build.py`). It goes before launch.

### Motion rules

- GSAP and ScrollTrigger drive parallax, reveals and pinned scrolling. Swiper runs slideshows and the gallery. GLightbox runs the lightbox. All three are vendored in `assets/vendor/`.
- JavaScript hides content right before it animates (`gsap.set`). CSS never hides content. If scripts fail, the page stays readable.
- `prefers-reduced-motion` turns the motion off.
- Hero and slider markup is shared. Each theme's JS picks the effect.

### Responsive and browser support

- Pages do not scroll horizontally at 1440, 820 or 390 px wide.
- iOS 15 Safari lacks `color-mix()`, `svh` and unprefixed `backdrop-filter`. Each rule that uses one of them has a plain fallback before it (`rgba(var(--bg-rgb), .9)`, `vh`, `-webkit-backdrop-filter`). New rules follow the same pattern. The mobile menu height in `core.css` follows it too (`100vh`, then `100svh`).
- WebKit (Playwright's build, version 26.6) renders A, B, C, D and the portfolio without console errors or sideways scroll at 1440 and 390 px. Real iPhone, iPad and Mac Safari checks are still to do.

## 5. The directions

### A, Velvet Night (`a/`)

- Idea: a theatre at night, in the spirit of the studio's most dramatic interiors. Gold on oxblood-black, with warm lighting and ornament.
- Palette: Night Velvet `#14090C`, surface `#1E1115`, band `#2A0F16`, Oxblood `#7A1F2E`, Antique Gold `#C9A24B`, Emerald `#1F5E4B`, Midnight Teal `#1D4F5A`, Warm Ivory `#F3EADB`. Text `#F3E9DC`, muted `#BBA99C`.
- Type: Bodoni Moda for display (400, with italics for emphasis), Jost 300 for body. Uppercase labels with wide letter spacing.
- Features: gold hairlines that draw across the page, a fan (Art Deco) motif above the band sections, gilded frames with warm drop shadows, frames that gain a gold inset line on hover, a marquee in gold italics, a cursor-following spotlight on the hero.
- Motion: fade slideshow with a Ken Burns zoom, word-by-word headlines, parallax, a creative-effect works slider.
- Project page: a full-background hero (the project's card photo, with a veil that fades to the page colour), a facts row (type, location, year, area), the design language as chips, the story, signature details, the palette as large gold-ringed dots, a gallery slider with a lightbox, related projects and a call to action.

### B, Gallery Noir (`b/`)

- Idea: a darkened gallery with one light on at a time. Each project carries one accent colour (`--lit`) that tints its page.
- Palette: `#0D0D0C` ground, surface `#141413`, band `#1A1917`, bone text `#ECE6DC`, muted `#A39E94`, default accent marigold `#E0A526`.
- Type: Cormorant Garamond in weight 300 at very large sizes, Hanken Grotesk for body. The eyebrow label starts with a dash.
- Features: film grain over the page, a letterboxed hero stage with giant type, italic accent words, project pages with a sticky side column and a long stack of photographs.
- Motion: creative-effect hero with a progress line, clip-path image reveals, a pinned horizontal scroll of featured works, a cursor-following preview on the works index.

### C, Midnight Bazaar (`c/`)

- Idea: a night market with poster colour. The studio's playful projects (a salon, a gelateria, a kachori shop) set the tone.
- Palette: `#0A1A1F` deep teal ground, surface `#112A31`, band `#0F3A44`, cream text `#FFF4D6`, marigold `#F2B01E`, pop red `#D9252C`, blue `#1F9BC4`, terracotta `#D9702E`.
- Type: Rozha One for display, Karla for body. Weight is heavier than A and B.
- Features: stickers that wobble, hard black offset shadows (`8px 8px 0 #000`), pill buttons with a black outline that press down on click, rounded 14 px corners, tilted photo frames on project pages.
- Motion: cards-effect hero and coverflow works slider.
- Status: the client is not pursuing C. Subhan may reuse single elements from it. Leave it untouched.

### D, Velvet Portfolio (`d/`)

- Idea: the PDF portfolio as a website. A's multi-page structure and look, with the portfolio's colour-block way of showing each project.
- Palette: A's tokens, plus tan `#C3A17E` with tan ink `#1B100A` (the panels) and gold `#D8A93A`. Each project adds its own page colour.
- Type: Bodoni Moda and Jost (as A), plus Herr Von Muellerhoff, a script face used for the closing line.
- Home: hero slideshow (same behaviour as A), the approach, the founders, three spotlight projects in their own colours (Helios Maximus, Chihiro, Mio Marito Gelato), the works wall, services and the closing line with the studio logo.
- Works: a filterable wall of all 19 projects, each tile with its colour as a bottom edge.
- Project page: A's layout and hero, then everything below the hero is recoloured to the project's own colour. `tone_style()` in `tools/build_d.py` derives the surface, band, line, muted and accent tokens from the project's `bg`, and picks light or dark text by contrast. The palette sits on a tan panel with gold-ringed dots. The gallery shows every photo of the project. A next-project band and three related tiles follow.
- Motion: photos wipe open and drift on scroll, tan panels and swatches enter in sequence, the closing line writes itself out.
- Portfolio links: the footer of every version has one link, "Get our portfolio", in the place of the menu's Portfolio entry. It opens the PDF in a new tab, in the browser viewer on desktop and the phone's own PDF handling on mobile. D repeats it in the closing band and on the contact page. The one-page portfolio has a Back to site link in its top bar. It returns to the version the visitor came from. The file is `assets/downloads/Archipixels-Portfolio.pdf`.
- Technical: `tools/build_d.py` builds it. Body class `theme-a theme-d`.

### One-page portfolio (`portfolio/`)

- Idea: the PDF as one scroll, in its original order. Cover slideshow, approach, founders, a wall of the 19 projects, then 19 project sections, then studio, team, contact with a form and WhatsApp button, and the closing line. Studio and team come after the projects because the client asked for that order.
- Palette: burgundy `#591524` and deep burgundy `#2A0B13`, brown `#5C3D28`, cover brown `#321B13`, tan `#C3A17E`, cream `#F6EFE6`, gold `#D8A93A`.
- Type: Playfair Display for display, Cormorant Garamond for body serif, Jost for labels and Herr Von Muellerhoff for the script.
- Navigation: a small top bar with Works, Studio, Team, Contact and an Index button that opens a full-screen project list. A counter shows the current project number.
- Each project section takes its background from the PDF page. The tan panel stays the same on every project.
- Technical: `tools/build_portfolio.py` builds it. It has its own CSS and JS and does not use `build.py`.

## 6. Decisions so far

- The design of A, B and C is final. Only fixes are allowed (see Frozen designs in `CLAUDE.md`).
- C is dropped. Leave it as is, or take elements from it if one is wanted.
- D merges the one-page portfolio with A's multi-page structure and nested menu.
- D's project page uses A's full-background hero, with the page body in the project's colour. The photo-and-tan-panel block appears only in D's home page spotlights.
- Every project page in D has a gallery slider with a lightbox. Warehouse Studio has one photo, so it has no arrows.
- The preview switcher lists A, B, C and D on every page.
- The About submenu starts closed on mobile in every direction.
- The chooser page (`index.html`) lists five versions and shows the mood boards below them, with a lightbox. It has a favicon and share tags that assume `archipixels-template.pages.dev`.
- The README follows the layout of Subhan's other repositories (centred logo, badges, preview image).
- `functions/_middleware.js` and `_routes.json` stay in the root. They return 404 on the preview for `tools/`, `data/` and every `.md`, `.py` and `.pyc` file. A page that needs a new file of one of those types has to move it out of the blocked set.
- `_headers` stays in the root. It blocks search engines on the preview, which an HTTP header does for every file type, including images and PDFs.
- The portfolio PDF is compressed to 5 MB. Every version links it from the footer, and the one-page portfolio and D link it in more places.
- Writing rules for docs, comments and UI text: plain present tense, no em dashes, no "X, not Y" contrasts, no flourish adjectives, no bold lead-ins on bullets, no emoji in headings, no leftover placeholders unless they stand for content the client still owes.

## 7. Open items

The list of what to decide, confirm or fill before launch is in the Before launch section of [LARAVEL.md](./LARAVEL.md#before-launch).

## 8. How to work in this repository

- Pages are generated. Change the generator, the data or the stylesheet, then rebuild: `python3 tools/build.py` (A, B, C), `python3 tools/build_d.py` (D), `python3 tools/build_portfolio.py` (portfolio). The generators use only the Python standard library.
- A change to `core.css`, `core.js`, the header, the footer or `build.py` reaches every direction.
- Serve locally with `python3 -m http.server 8000`.
- Rebuild only the builders whose output the change touches. A change to `build.py` also needs `build_d.py`, which imports it. A change to a stylesheet or script needs no rebuild.
- Check only the pages a change touches: one page per version, at 1440 and 390 px. Look for horizontal scroll, broken images and console errors. When a change touches project pages, use a light-coloured project (The Quiet Abode, Jewellery Spaces), a portrait-photo project (Archipixels Homes) or Warehouse Studio. Run the full link and console check on all pages only when the developer asks for it.
- A, B and C are frozen. Fix mistakes in them and leave their design alone. A new site-wide change goes into every version where it suits, built once in the shared source and styled with each version's existing classes.
- The live Laravel site is a separate project. Read that project's own `CLAUDE.md` and follow its conventions. Do not port the Python generators.

## 9. Starting a new session

Paste this as the first message:

> Read `CONTEXT.md`, `README.md`, `CLAUDE.md` and `LARAVEL.md` in this repository, then summarise the project, the five versions and the rules in a few lines. Wait for my instructions.
