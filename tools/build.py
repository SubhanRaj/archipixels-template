#!/usr/bin/env python3
"""Generates the three static template sets (a/, b/, c/) from data/*.json.

Run from the package root:  python3 tools/build.py

Markup is plain and component-shaped (see the `<!-- component: ... -->`
comments) so each block maps to a Blade partial or <x-component>.
"""
import html
import json
import re
import shutil
import struct
from pathlib import Path
from urllib.parse import quote

from build_portfolio import PF, contrast, ICON_IG, ICON_LI, ICON_FB

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / 'data/site.json').read_text())
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
LEGACY = json.loads((ROOT / 'data/legacy-projects.json').read_text())['projects']
BY_SLUG = {p['slug']: p for p in PROJECTS}
TEAM = json.loads((ROOT / 'data/team.json').read_text())['members']
e = html.escape

THEMES = {
    'a': dict(name='Velvet Night', color='#14090C',
              fonts='https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400;500&display=swap'),
    'b': dict(name='Gallery Noir', color='#0D0D0C',
              fonts='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Hanken+Grotesk:wght@300;400;500&display=swap'),
    'c': dict(name='Midnight Bazaar', color='#0A1A1F',
              fonts='https://fonts.googleapis.com/css2?family=Rozha+One&family=Karla:wght@400;500;700&display=swap'),
}

# (href, label, children). Children render as a submenu under their parent.
PORTFOLIO = '../portfolio/index.html'   # the one-page portfolio, relative to the theme folder like the other hrefs
PDF_FILE = 'assets/downloads/Archipixels-Portfolio.pdf'   # relative to the package root
NAV = [('works.html', 'Works', []),
       ('about.html', 'About', [('about.html', 'About us'), ('team.html', 'Team')]),
       ('studio.html', 'Studio', []),
       ('services.html', 'Services', []),
       (PORTFOLIO, 'Portfolio', []),
       ('contact.html', 'Contact', [])]


def nav_flat():
    out = []
    for h, l, kids in NAV:
        out.append((h, l))
        out.extend((kh, kl) for kh, kl in kids if kh != h)
    return out
HERO_SLIDES = ['helios-maximus', 'the-deco-grand', 'hons-grey-opera', 'the-heritage-mosaic', 'house-of-narula']
FEATURED = ['the-deco-grand', 'chihiro', 'hons-grey-opera', 'house-of-narula', 'warehouse-studio', 'mio-marito-gelato', 'kesarwani-residence']
FILTERS = [('all', 'All'), ('hospitality', 'Hospitality'), ('cafes', 'Cafés'), ('retail', 'Retail'),
           ('residential', 'Residential'), ('workplace', 'Workplace'), ('homes', 'Homes')]


class Ctx:
    def __init__(self, t, rel):
        self.t = t
        self.rel = rel
        self.depth = rel.count('/')
        self.loc = '../' * self.depth          # from this page to the theme folder root
        self.base = '../' * (self.depth + 1)   # from this page to the package root


class Ctx404(Ctx):
    """Context for 404.html. Cloudflare Pages serves it at whatever URL was missing, so every link and asset is root-relative."""
    def __init__(self, t):
        super().__init__(t, '404.html')
        self.loc = f'/{t}/'
        self.base = '/'


def wa(msg_key='whatsapp_message_general'):
    return f"https://wa.me/{SITE['whatsapp_number']}?text={quote(SITE[msg_key], safe='')}"


def img(c, name):
    return f'{c.base}assets/img/{name}'


def img_size(name):
    d = (ROOT / 'assets/img' / name).read_bytes()
    if d[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', d[16:24])
    i = 2
    while i < len(d):
        m = d[i + 1]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack('>HH', d[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack('>H', d[i + 2:i + 4])[0]


def add_img_dims(page):
    """Adds width and height to the photo tags so the browser reserves their space before they load."""
    def repl(m):
        if 'width=' in m['pre'] + m['post']:
            return m[0]
        w, h = img_size(m['name'])
        return f'<img {m["pre"]}src="{m["src"]}" width="{w}" height="{h}"{m["post"]}>'
    return re.sub(r'<img (?P<pre>[^>]*?)src="(?P<src>(?:\.\./)+assets/img/(?!brand/)(?P<name>[^"]+))"(?P<post>[^>]*)>', repl, page)


def lit_text(hx, bg='#0D0D0C', need=4.5):
    """Lightens a project colour until it reads as text on bg. Returns None when it already does."""
    r = [int(hx[i:i + 2], 16) for i in (1, 3, 5)]
    for step in range(21):
        c = '#' + ''.join(f'{round(x + (255 - x) * step / 20):02X}' for x in r)
        if contrast(c, bg) >= need:
            return c if step else None


def meta_line(p):
    return p['kind'] + (f" · {p['place']}" if p['place'] else '')


def dots(p):
    if not p['palette']:
        return ''
    items = ''.join(f'<li style="--sw:{hx}" title="{e(n)}"></li>' for n, hx, *_ in p['palette'])
    return f'<ul class="dots" aria-label="Colour palette">{items}</ul>'


def arrow_svg():
    return '<svg viewBox="0 0 24 12" width="24" height="12" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M0 6h22M17 1l5 5-5 5"/></svg>'


def social_links():
    """The studio's social profiles as (name, address, icon). Instagram first."""
    return [('Instagram', SITE['instagram'], ICON_IG), ('LinkedIn', SITE['linkedin'], ICON_LI), ('Facebook', SITE['facebook'], ICON_FB)]


def social_icons(cls='social-icons'):
    """A row of icon-only links to the social profiles."""
    items = ''.join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="Archipixels on {n}">{i}</a>' for n, u, i in social_links())
    return f'<div class="{cls}">{items}</div>'


def placeholder(txt):
    return f'<span class="placeholder">{e(txt)}</span>'


# ---------------------------------------------------------------- shell ----

def head(c, title, desc, og, page_cls, extra=''):
    t = THEMES[c.t]
    b = c.base
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="{t['color']}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{b}assets/img/{og}">
<link rel="icon" type="image/png" sizes="48x48" href="{b}assets/img/brand/favicon-48.png">
<link rel="icon" type="image/png" sizes="256x256" href="{b}assets/img/brand/favicon.png">
<link rel="apple-touch-icon" href="{b}assets/img/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{t['fonts']}">
<link rel="stylesheet" href="{b}assets/vendor/swiper-bundle.min.css">
<link rel="stylesheet" href="{b}assets/vendor/glightbox.min.css">
<link rel="stylesheet" href="{b}assets/css/core.css">
<link rel="stylesheet" href="{b}assets/css/theme-{c.t}.css">
{extra}</head>
<body class="theme-{c.t} page-{page_cls}">
'''


def header(c, active=''):
    # a project page is not the Works page, and a parent link is not the page itself
    def link(h, l, on, cur='page'):
        return f'<a href="{c.loc}{h}"' + (f' aria-current="{cur}"' if on else '') + f'>{e(l)}</a>'
    cur = 'true' if c.rel.startswith('projects/') else 'page'
    items = ''
    for h, l, kids in NAV:
        if kids:
            sub = ''.join(f'<li>{link(kh, kl, kh == active)}</li>' for kh, kl in kids)
            on = active in [k[0] for k in kids]
            btn = f'<button class="sub-toggle" type="button" aria-expanded="false" aria-label="Show {e(l)} pages"></button>'
            items += f'<li class="has-sub">{link(h, l, on, "true")}{btn}<ul class="submenu">{sub}</ul></li>'
        else:
            items += f'<li>{link(h, l, h == active, cur)}</li>'
    nav = f'<ul class="site-nav__list">{items}</ul>'
    return f'''<!-- component: site-header -->
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" data-header>
  <div class="container site-header__inner">
    <a class="brand" href="{c.loc}index.html"><img src="{c.base}assets/img/brand/logo-horizontal-white.png" alt="Archipixels, design that works" width="184" height="38"></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="sr-only">Menu</span><span class="nav-toggle__bars" aria-hidden="true"></span>
    </button>
    <nav id="site-nav" class="site-nav" aria-label="Primary">{nav}</nav>
    <a class="btn btn--primary site-header__cta" href="{wa()}" target="_blank" rel="noopener">Chat on WhatsApp</a>
  </div>
</header>
<main id="main">
'''


# Directions shown in the preview switcher. D is built by build_d.py.
SWITCH = ['a', 'b', 'c', 'd']


def footer(c):
    # the menu's Portfolio item shows the web page, so the footer's entry opens the PDF
    pdf = f'<li><a href="{c.base}{PDF_FILE}" target="_blank" rel="noopener">Get our portfolio</a></li>'
    links = ''.join(pdf if h == PORTFOLIO else f'<li><a href="{c.loc}{h}">{e(l)}</a></li>' for h, l in nav_flat())
    sw = ''.join(
        f'<a href="{c.base}{k}/{c.rel}"' + (' aria-current="true"' if k == c.t else '') + f'>{k.upper()}</a>'
        for k in SWITCH)
    follow = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{ic}<span>{n}</span></a></li>' for n, u, ic in social_links())
    return f'''</main>
<!-- component: site-footer -->
<footer class="site-footer">
  <div class="container site-footer__grid">
    <div class="site-footer__brand">
      <a class="brand brand--stacked" href="{c.loc}index.html"><img src="{c.base}assets/img/brand/logo-stacked-white.png" alt="Archipixels, design that works" width="190" height="117" loading="lazy"></a>
      <p>{e(SITE['descriptor'])}</p>
    </div>
    <div>
      <h2 class="footer-title">Explore</h2>
      <ul class="footer-list">{links}</ul>
    </div>
    <div>
      <h2 class="footer-title">Contact</h2>
      <address class="footer-list">
        <a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a>
        <a href="{wa()}" target="_blank" rel="noopener">{e(SITE['phone_note'])}</a>
        <a href="mailto:{SITE['email']}">{SITE['email']}</a>
        <a href="{e(SITE['maps_url'])}" target="_blank" rel="noopener">{e(SITE['address'])}</a>
      </address>
    </div>
    <div>
      <h2 class="footer-title">Follow</h2>
      <ul class="footer-list footer-list--social">{follow}</ul>
    </div>
  </div>
  <div class="container site-footer__base"><small>© 2026 Archipixels. {e(SITE['sign_off'])}</small></div>
</footer>
<!-- component: theme-switcher (client preview only, remove for production) -->
<nav class="theme-switcher" aria-label="Design direction preview"><span>Direction</span>{sw}</nav>
<script src="{c.base}assets/vendor/gsap.min.js"></script>
<script src="{c.base}assets/vendor/ScrollTrigger.min.js"></script>
<script src="{c.base}assets/vendor/swiper-bundle.min.js"></script>
<script src="{c.base}assets/vendor/glightbox.min.js"></script>
<script src="{c.base}assets/js/core.js"></script>
<script src="{c.base}assets/js/theme-{c.t}.js"></script>
</body>
</html>
'''


def write(c, title, desc, og, page_cls, active, body, extra=''):
    out = ROOT / c.t / c.rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(add_img_dims(head(c, title, desc, og, page_cls, extra) + header(c, active) + body + footer(c)))


# ------------------------------------------------------------ components ----

def section_head(eyebrow, title, link=None, split=True):
    s = ' data-split' if split else ''
    lk = f'<a class="link-arrow" href="{link[0]}">{e(link[1])}{arrow_svg()}</a>' if link else ''
    return f'''<header class="section-head">
  <div>{f'<p class="eyebrow" data-reveal>{e(eyebrow)}</p>' if eyebrow else ''}<h2 class="h2"{s}>{e(title)}</h2></div>{lk}
</header>'''


def card_work(c, p, hidden_cats=True):
    cats = ' '.join(p['cats'])
    return f'''<article class="card-work tilt" data-cats="{cats}" data-reveal>
  <a class="card-work__link" href="{c.loc}projects/{p['slug']}.html">
    <div class="card-work__media"><img src="{img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="lazy"></div>
    <div class="card-work__body">
      <p class="card-work__meta">{e(meta_line(p))}</p>
      <h3 class="card-work__title">{e(p['name'])}</h3>
      <p class="card-work__tag">{e(p['tagline'])}</p>
      {dots(p)}
    </div>
  </a>
</article>'''


def index_row(c, p):
    cats = ' '.join(p['cats'])
    return f'''<li class="index-row" data-cats="{cats}" data-img="{img(c, p['card'])}" style="--lit:{p['lit']}">
  <a href="{c.loc}projects/{p['slug']}.html">
    <img class="index-row__thumb" src="{img(c, p['card'])}" alt="" loading="lazy">
    <span class="index-row__name">{e(p['name'])}</span>
    <span class="index-row__kind">{e(p['kind'])}</span>
    <span class="index-row__place">{e(p['place'])}</span>
    {dots(p)}
  </a>
</li>'''


def marquee(items):
    one = ''.join(f'<span>{e(n)}</span><i aria-hidden="true"></i>' for n in items)
    return f'''<div class="marquee" aria-hidden="true"><div class="marquee__skew"><div class="marquee__track">{one}{one}</div></div></div>'''


def ui_arrows(prev_cls, next_cls):
    return f'''<div class="slider-arrows">
  <button class="slider-arrow {prev_cls}" type="button" aria-label="Previous"><svg viewBox="0 0 24 12" width="24" height="12" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M24 6H2M7 1L2 6l5 5"/></svg></button>
  <button class="slider-arrow {next_cls}" type="button" aria-label="Next"><svg viewBox="0 0 24 12" width="24" height="12" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M0 6h22M17 1l5 5-5 5"/></svg></button>
</div>'''


def hero_slides(c):
    out = []
    for s in HERO_SLIDES:
        p = BY_SLUG[s]
        out.append(f'''<div class="swiper-slide" data-title="{e(p['name'])}" data-meta="{e(meta_line(p))}" data-href="{c.loc}projects/{p['slug']}.html">
  <img class="hero__img" src="{img(c, p['card'])}" alt="" {'loading="eager"' if s == HERO_SLIDES[0] else 'loading="lazy"'}>
</div>''')
    return '\n'.join(out)


def hero_a(c, strip=None):
    """A's home hero. `strip` lists the names in the marquee below it, and defaults to the featured works."""
    return f'''<!-- component: hero-slideshow (A) -->
<section class="hero hero--a" aria-label="Introduction">
  <div class="swiper hero-swiper"><div class="swiper-wrapper">
{hero_slides(c)}
  </div></div>
  <div class="hero__veil"></div>
  <div class="hero__spot" aria-hidden="true"></div>
  <div class="container hero__content">
    <p class="eyebrow" data-reveal>{e(SITE['descriptor'])}</p>
    <h1 class="hero__title" data-split>{e(SITE['tagline'])}</h1>
    <p class="lead" data-reveal>An architecture and interior design studio in Lucknow, for clients with extraordinary ambitions.</p>
    <div class="actions" data-reveal>
      <a class="btn btn--primary" href="{c.loc}works.html">See selected works</a>
      <a class="link-arrow" href="{c.loc}about.html">About the studio{arrow_svg()}</a>
    </div>
  </div>
  <div class="container hero__ui">
    <div class="hero__now"><span class="hero__now-meta"></span><a class="hero__now-title" href="#"></a></div>
    <div class="hero__pagination" aria-hidden="true"></div>
    {ui_arrows('hero-prev', 'hero-next')}
  </div>
</section>
{marquee(strip or [BY_SLUG[s]['name'] for s in FEATURED])}'''


def hero_b(c):
    return f'''<!-- component: hero-slideshow (B) -->
<section class="hero hero--b" aria-label="Introduction">
  <div class="container hero__top">
    <p class="eyebrow" data-reveal>{e(SITE['descriptor'])}</p>
    <h1 class="hero__title" data-split>{e(SITE['tagline'])}</h1>
  </div>
  <div class="hero__stage">
    <div class="swiper hero-swiper"><div class="swiper-wrapper">
{hero_slides(c)}
    </div></div>
    <div class="container hero__ui">
      <div class="hero__now"><span class="hero__now-meta"></span><a class="hero__now-title" href="#"></a></div>
      <div class="hero__counter" aria-hidden="true"><b data-current>01</b><span>/</span><span data-total>05</span></div>
      <div class="hero__progress" aria-hidden="true"><i></i></div>
      {ui_arrows('hero-prev', 'hero-next')}
    </div>
  </div>
  <div class="container hero__bottom">
    <p class="lead" data-reveal>An architecture and interior design studio in Lucknow, for clients with extraordinary ambitions.</p>
    <div class="actions" data-reveal>
      <a class="btn btn--primary" href="{c.loc}works.html">See selected works</a>
      <a class="link-arrow" href="{c.loc}about.html">About the studio{arrow_svg()}</a>
    </div>
  </div>
</section>'''


def hero_c(c):
    cards = []
    for s in HERO_SLIDES:
        p = BY_SLUG[s]
        cards.append(f'''<div class="swiper-slide" data-title="{e(p['name'])}" data-meta="{e(meta_line(p))}" data-href="{c.loc}projects/{p['slug']}.html">
  <img class="hero__img" src="{img(c, p['card'])}" alt="" loading="eager"><span class="deck-label">{e(p['name'])}</span>
</div>''')
    return f'''<!-- component: hero-slideshow (C) -->
<section class="hero hero--c" aria-label="Introduction">
  <div class="container hero__grid">
    <div class="hero__copy">
      <div class="sticker-row" data-reveal>
        <span class="sticker sticker--yellow">Since {SITE['founded']}</span>
        <span class="sticker sticker--red">Lucknow, India</span>
        <span class="sticker sticker--blue">Never repeats a design</span>
      </div>
      <h1 class="hero__title" data-split>{e(SITE['tagline'])}</h1>
      <p class="lead" data-reveal>An architecture and interior design studio in Lucknow, for clients with extraordinary ambitions.</p>
      <div class="actions" data-reveal>
        <a class="btn btn--primary" href="{c.loc}works.html">See selected works</a>
        <a class="btn btn--ghost" href="{c.loc}about.html">About the studio</a>
      </div>
    </div>
    <div class="hero__deck">
      <div class="swiper hero-swiper"><div class="swiper-wrapper">
{''.join(cards)}
      </div></div>
      <div class="hero__ui">
        <div class="hero__now"><span class="hero__now-meta"></span><a class="hero__now-title" href="#"></a></div>
        {ui_arrows('hero-prev', 'hero-next')}
      </div>
    </div>
  </div>
</section>
{marquee(['Spaces with stories', 'Maximalist', 'Playful', 'Theatrical', 'Eclectic', 'Immersive', 'Never the same twice'])}'''


def featured_a(c):
    slides = []
    for s in FEATURED:
        p = BY_SLUG[s]
        slides.append(f'''<div class="swiper-slide feature-slide">
  <a class="feature-slide__media" href="{c.loc}projects/{p['slug']}.html"><img src="{img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="lazy"></a>
  <div class="feature-slide__body">
    <p class="card-work__meta">{e(meta_line(p))}</p>
    <h3 class="feature-slide__title">{e(p['name'])}</h3>
    <p class="card-work__tag">{e(p['tagline'])}</p>
    {dots(p)}
    <a class="link-arrow" href="{c.loc}projects/{p['slug']}.html">View project{arrow_svg()}</a>
  </div>
</div>''')
    return f'''<!-- component: featured-works (A, creative-effect slider) -->
<section class="section featured featured--a">
  <div class="container">{section_head('', 'Hospitality, cafés, residences, workplaces', (c.loc + 'works.html', 'View all works'))}</div>
  <div class="container">
    <div class="swiper feature-swiper"><div class="swiper-wrapper">{''.join(slides)}</div></div>
    <div class="feature-ui"><div class="feature-fraction" aria-hidden="true"><b data-current>01</b> / <span data-total>07</span></div>{ui_arrows('feature-prev', 'feature-next')}</div>
  </div>
</section>'''


def featured_b(c):
    cards = []
    for s in FEATURED:
        p = BY_SLUG[s]
        cards.append(f'''<article class="hcard">
  <a href="{c.loc}projects/{p['slug']}.html">
    <div class="hcard__media"><img src="{img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="lazy"></div>
    <p class="card-work__meta">{e(meta_line(p))}</p>
    <h3 class="hcard__title">{e(p['name'])}</h3>
  </a>
</article>''')
    return f'''<!-- component: featured-works (B, pinned horizontal scroll) -->
<section class="hscroll">
  <div class="container hscroll__head">{section_head('', 'Seven spaces, seven stories', (c.loc + 'works.html', 'View all works'))}</div>
  <div class="hscroll__track">{''.join(cards)}<a class="hcard hcard--end" href="{c.loc}works.html"><span>All works</span>{arrow_svg()}</a></div>
</section>'''


def featured_c(c):
    slides = []
    for s in FEATURED:
        p = BY_SLUG[s]
        slides.append(f'''<div class="swiper-slide feature-card">
  <a href="{c.loc}projects/{p['slug']}.html">
    <div class="feature-card__media"><img src="{img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="lazy"></div>
    <span class="sticker sticker--yellow feature-card__tag">{e(p['kind'])}</span>
    <h3 class="feature-card__title">{e(p['name'])}</h3>
  </a>
</div>''')
    return f'''<!-- component: featured-works (C, coverflow slider) -->
<section class="section featured featured--c">
  <div class="container">{section_head('', 'Pick a story', (c.loc + 'works.html', 'View all works'))}</div>
  <div class="swiper feature-swiper"><div class="swiper-wrapper">{''.join(slides)}</div></div>
  <div class="container feature-ui">{ui_arrows('feature-prev', 'feature-next')}</div>
</section>'''


FEATURED_FN = {'a': featured_a, 'b': featured_b, 'c': featured_c}
HERO_FN = {'a': hero_a, 'b': hero_b, 'c': hero_c}


def intro(c):
    return f'''<!-- component: intro -->
<section class="section intro">
  <div class="container intro__grid">
    <h2 class="h2" data-split>Design begins with curiosity.</h2>
    <div class="intro__copy" data-reveal>
      <p class="lead">A curiosity about people, places, cultures and the little things that often go unnoticed. Spaces that are layered, expressive, sometimes unexpected, but always thoughtful in their details.</p>
      <a class="link-arrow" href="{c.loc}about.html">About the studio{arrow_svg()}</a>
    </div>
  </div>
</section>'''


def services(c):
    items = ''.join(f'''<li class="service" data-reveal><h3 class="service__name">{e(s['name'])}</h3><p class="service__text">{e(s['text'])}</p></li>''' for s in SITE['services'])
    return f'''<!-- component: services -->
<section class="section services">
  <div class="container">
    {section_head('', 'What we design and build', (c.loc + 'services.html', 'All services'))}
    <ul class="services__list">{items}</ul>
  </div>
</section>'''


def range_band(c):
    cats = [('Hotels and lounges', 'hospitality'), ('Cafés and restaurants', 'cafes'), ('Residences', 'residential'), ('Offices and workplaces', 'workplace'), ('Salons and retail', 'retail'), ('Themed homes', 'homes')]
    lis = ''.join(f'<li><a class="link-arrow" href="{c.loc}works.html#{k}">{e(n)}{arrow_svg()}</a></li>' for n, k in cats)
    return f'''<!-- component: range-band (project types, links into the filtered works page) -->
<section class="section band range">
  <div class="container range__grid">
    <div class="range__copy">
      <h2 class="h2" data-split>One point of view, many different stories.</h2>
      <p class="lead" data-reveal>From hotels and lounges to homes, cafés and offices, every project begins with a different story, and we never repeat a design.</p>
      <ul class="range__list" data-reveal>{lis}</ul>
    </div>
    <figure class="range__media parallax"><img src="{img(c, 'deco-room.jpg')}" alt="A guest room at The Deco Grand with a sculpted headboard and jewel tones" loading="lazy"><figcaption>The Deco Grand · Hotel</figcaption></figure>
  </div>
</section>'''


def homes(c):
    tiles = ''.join(f'''<li class="home-tile tilt" data-reveal><img src="{img(c, h['img'])}" alt="{e(h['name'])}, an Archipixels Homes themed rental" loading="lazy"><span>{e(h['name'])}</span></li>''' for h in SITE['homes_collection'])
    return f'''<!-- component: homes-and-experiences -->
<section class="section homes">
  <div class="container homes__grid">
    <div class="homes__copy">
      <h2 class="h2" data-split>We create experiences, and run a few of our own.</h2>
      <p class="lead" data-reveal>Our café and themed rental homes bring our ideas to life, giving us firsthand insight into designing places people love to visit and stay in.</p>
      <div class="actions" data-reveal>
        <a class="link-arrow" href="{c.loc}projects/archipixels-homes.html">The homes collection{arrow_svg()}</a>
        <a class="link-arrow" href="{c.loc}projects/chihiro.html">Chihiro, our bakehouse{arrow_svg()}</a>
      </div>
    </div>
    <ul class="homes__tiles">{tiles}</ul>
  </div>
</section>'''


def studio(c):
    return f'''<!-- component: studio-teaser -->
<section class="section surface studio">
  <div class="container studio__grid">
    <figure class="studio__portrait parallax"><img src="{img(c, 'founders.jpg')}" alt="Shivika and Abhinav, founders of Archipixels, seated in a velvet lounge" loading="lazy"></figure>
    <div class="studio__copy">
      <h2 class="h2" data-split>Two minds. A thousand ideas.</h2>
      <p class="lead" data-reveal>We're {SITE['founders'][0]} and {SITE['founders'][1]}, partners in life, work and a shared curiosity for everything around us. Our love for design, travel, art and the unexpected has shaped the journey of Archipixels.</p>
      <div class="studio__team parallax"><img src="{img(c, 'team.jpg')}" alt="The Archipixels team gathered around a coffee table" loading="lazy"></div>
      <div class="actions"><a class="link-arrow" href="{c.loc}about.html">About us{arrow_svg()}</a><a class="link-arrow" href="{c.loc}team.html">The team{arrow_svg()}</a></div>
    </div>
  </div>
</section>'''


def cta(c, title=None, key='whatsapp_message_general'):
    title = title or SITE['closing_line']
    return f'''<!-- component: cta-band -->
<section class="section band cta" id="contact">
  <div class="container cta__grid">
    <h2 class="cta__title" data-split>{e(title)}</h2>
    <div class="cta__side" data-reveal>
      <a class="btn btn--light" href="{wa(key)}" target="_blank" rel="noopener">Chat on WhatsApp</a>
      <address>
        <span>{SITE['email']}</span>
        <span>{SITE['phone_display']} · {e(SITE['phone_note'])}</span>
        <span>{e(SITE['address'])}</span>
      </address>
    </div>
  </div>
</section>'''


def form(prefix, with_type=True):
    typ = ''
    if with_type:
        typ = f'''<div class="field-row">
    <div class="field"><label for="{prefix}-type">Project type</label><select id="{prefix}-type"><option>Hotel or hospitality</option><option>Café or restaurant</option><option>Villa or residence</option><option>Workplace</option><option>Retail or salon</option><option>Something else</option></select></div>
    <div class="field"><label for="{prefix}-city">City</label><input id="{prefix}-city" name="city" type="text" autocomplete="address-level2"></div>
  </div>'''
    return f'''<!-- component: enquiry-form (demo only, wire to a Laravel route) -->
<form class="form" data-demo-form action="#" method="post" novalidate>
  <div class="field-row">
    <div class="field"><label for="{prefix}-first">First name</label><input id="{prefix}-first" name="first_name" type="text" autocomplete="given-name" required></div>
    <div class="field"><label for="{prefix}-last">Last name</label><input id="{prefix}-last" name="last_name" type="text" autocomplete="family-name"></div>
  </div>
  <div class="field"><label for="{prefix}-email">Email</label><input id="{prefix}-email" name="email" type="email" autocomplete="email" required></div>
  {typ}
  <div class="field"><label for="{prefix}-msg">The story so far</label><textarea id="{prefix}-msg" name="message" rows="4" placeholder="A few lines about the space"></textarea></div>
  <button class="btn btn--primary" type="submit">Send enquiry</button>
  <p class="form__thanks" role="status" hidden>Thanks for submitting! We will reply on WhatsApp or email.</p>
</form>'''


# ----------------------------------------------------------------- pages ----

def page_home(t):
    c = Ctx(t, 'index.html')
    ld = json.dumps({
        '@context': 'https://schema.org', '@type': 'Organization', 'name': SITE['brand'],
        'description': 'Architecture, interior design and experience design studio in Lucknow, India.',
        'logo': 'assets/img/brand/logo-stacked-white.png', 'telephone': SITE['phone_tel'], 'email': SITE['email'],
        'address': {'@type': 'PostalAddress', 'streetAddress': '1/146, Gomti Nagar', 'addressLocality': 'Lucknow', 'addressCountry': 'IN'},
        'sameAs': [u for _, u, _ in social_links()]}, indent=2)
    body = HERO_FN[t](c) + intro(c) + FEATURED_FN[t](c) + services(c) + range_band(c) + homes(c) + studio(c) + cta(c)
    write(c, 'Archipixels | Architecture and interiors, Lucknow',
          'Archipixels is an architecture and interior design studio in Lucknow. Hotels, cafés, residences, workplaces and themed stays.',
          'helios.jpg', 'home', '', body, f'<script type="application/ld+json">\n{ld}\n</script>\n')


def page_about(t):
    c = Ctx(t, 'about.html')
    values = [('Every space has a story', 'We believe every space has a story waiting to be told. Design begins with curiosity about people, places and cultures.'),
              ('Every design is new', 'Every project begins with a different story, so every space gets an identity of its own.'),
              ('Feeling comes first', 'A space should feel a certain way and make you feel something, too. How it looks follows from that.')]
    vals = ''.join(f'<li class="value" data-reveal><h3>{e(a)}</h3><p>{e(b)}</p></li>' for a, b in values)
    body = f'''<!-- component: page-hero -->
<section class="page-hero">
  <div class="container page-hero__grid">
    <div><p class="eyebrow" data-reveal>About Archipixels</p><h1 class="display" data-split>Two minds. A thousand ideas.</h1>
    <p class="lead" data-reveal>Architecture, interiors and experiences from a studio in Lucknow, founded in {SITE['founded']}.</p></div>
    <figure class="page-hero__media parallax"><img src="{img(c, 'founders.jpg')}" alt="Shivika and Abhinav, founders of Archipixels, seated in a velvet lounge" loading="eager"></figure>
  </div>
</section>
<div class="container"><dl class="facts facts--three" data-reveal>
  <div><dt>Founded</dt><dd>{SITE['founded']}</dd></div>
  <div><dt>Founders</dt><dd>{SITE['founders'][0]} and {SITE['founders'][1]}</dd></div>
  <div><dt>Studio</dt><dd>Gomti Nagar, Lucknow</dd></div>
</dl></div>
<section class="section story">
  <div class="container story__grid">
    <blockquote class="pullquote" data-reveal>Every space has a story waiting to be told.</blockquote>
    <div class="prose" data-reveal>
      <p>We're {SITE['founders'][0]} and {SITE['founders'][1]}, partners in life, work and a shared curiosity for everything around us. Our love for design, travel, art and the unexpected has shaped the journey of Archipixels. We find inspiration in the places we visit, the people we meet and the smallest details that often go unnoticed.</p>
      <p>We started Archipixels in {SITE['founded']}. Our journey began in Dubai, where we gained international experience before founding Archipixels in India. Now we're ready to take that energy worldwide. We're looking for collaborators who share our curiosity and clients with extraordinary ambitions.</p>
    </div>
  </div>
</section>
<section class="section surface values">
  <div class="container">{section_head('', 'How we think')}<ul class="values__list">{vals}</ul></div>
</section>
<section class="section">
  <div class="container more-links">
    <a class="more-link" href="{c.loc}studio.html" data-reveal><span>The studio</span><b>See where we work</b>{arrow_svg()}</a>
    <a class="more-link" href="{c.loc}team.html" data-reveal><span>The team</span><b>Meet the Archipixels family</b>{arrow_svg()}</a>
    <a class="more-link" href="{c.loc}services.html" data-reveal><span>Services</span><b>What we design and build</b>{arrow_svg()}</a>
  </div>
</section>
{cta(c)}'''
    write(c, 'About us | Archipixels', 'Archipixels is an architecture and interior design studio founded in 2018 by Shivika and Abhinav in Lucknow.', 'founders.jpg', 'about', 'about.html', body)


def page_studio(t):
    c = Ctx(t, 'studio.html')
    shots = [('studio.jpg', 'The Archipixels studio lounge'), ('studio-detail.jpg', 'A velvet-draped corner of the studio'), ('team.jpg', 'The team gathered around a coffee table')]
    gal = ''.join(f'<li class="studio-mosaic__item parallax"><a class="glightbox" href="{img(c, f)}" data-gallery="studio" data-title="{e(cap)}"><img src="{img(c, f)}" alt="{e(cap)}" loading="{"eager" if i == 0 else "lazy"}"></a></li>' for i, (f, cap) in enumerate(shots))
    body = f'''<section class="page-hero page-hero--simple">
  <div class="container">
    <p class="eyebrow" data-reveal>The studio</p>
    <h1 class="display" data-split>Artful, maximalist and unafraid to experiment.</h1>
    <p class="lead" data-reveal>Our studio is an expression of who we are. It reflects the freedom we find in design, the joy of creating beyond convention and our belief that thoughtful maximalism can be as welcoming as it is memorable.</p>
  </div>
</section>
<section class="section studio-gallery">
  <div class="container"><ul class="studio-mosaic">{gal}</ul></div>
</section>
{gallery_slider(c, 'The Archipixels studio', [f'{c.base}portfolio/img/{f}' for f in ('studio-1.jpg', 'studio-2.jpg', 'studio-3.jpg')], heading='Inside the studio', group='studio-slider')}
<section class="section surface visit">
  <div class="container story__grid">
    <div class="visit__map"><h2 class="h2" data-split>Visit the studio</h2>{map_card(c)}</div>
    <div class="prose" data-reveal>
      <address class="contact-list">
        <span>{e(SITE['address'])}</span>
        <a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a>
        <a href="mailto:{SITE['email']}">{SITE['email']}</a>
      </address>
      <p>{placeholder('[STUDIO HOURS AND HOW TO BOOK A VISIT]')}</p>
      <div class="actions"><a class="btn btn--primary" href="{wa()}" target="_blank" rel="noopener">Chat on WhatsApp</a><a class="link-arrow" href="{c.loc}contact.html">Contact us{arrow_svg()}</a></div>
    </div>
  </div>
</section>
{homes(c)}{cta(c)}'''
    write(c, 'The studio | Archipixels', 'The Archipixels studio in Gomti Nagar, Lucknow: an artful, maximalist space that reflects how the team designs.', 'studio.jpg', 'studio', 'studio.html', body)


def member_name(m):
    """The name to show in a title or heading. Placeholder members read as 'Team member'."""
    return 'Team member' if m['name'].startswith('[') else m['name']


def member_card(c, m):
    return f'''<div class="swiper-slide"><a class="member" href="{c.loc}team/{m['slug']}.html">
  <div class="member__photo"><span>Photo</span></div>
  <h3>{e(m['name'])}</h3><p>{e(m['role'])}</p>
</a></div>'''


def team_carousel(c, members):
    """Swipeable row of member cards. Each card links to the member's profile page."""
    slides = ''.join(member_card(c, m) for m in members)
    return f'''<!-- component: team-carousel (Swiper) -->
<div class="swiper team-swiper"><div class="swiper-wrapper">{slides}</div></div>
<div class="gallery__ui">{ui_arrows('team-prev', 'team-next')}</div>'''


def page_team(t):
    c = Ctx(t, 'team.html')
    founders = ''.join(f'''<li class="founder" data-reveal><h3>{e(m['name'])}</h3><p class="founder__role">{e(m['role'])}</p><p>{placeholder(m['intro'])}</p><a class="link-arrow" href="{c.loc}team/{m['slug']}.html">View profile{arrow_svg()}</a></li>''' for m in TEAM if m['founder'])
    members = [m for m in TEAM if not m['founder']]
    body = f'''<section class="page-hero">
  <div class="container page-hero__grid">
    <div><p class="eyebrow" data-reveal>Our team</p><h1 class="display" data-split>The Archipixels family.</h1>
    <p class="lead" data-reveal>We believe that when people are valued, supported and given love, they create their best work. We are more than a team; we are the Archipixels family, growing together, celebrating every milestone and standing by one another through every challenge.</p></div>
    <figure class="page-hero__media parallax"><img src="{img(c, 'team.jpg')}" alt="The Archipixels team gathered around a coffee table" loading="eager"></figure>
  </div>
</section>
<section class="section surface">
  <div class="container founders">
    <figure class="founders__media parallax"><img src="{img(c, 'founders.jpg')}" alt="Shivika and Abhinav, founders of Archipixels" loading="lazy"></figure>
    <div class="founders__copy">
      <h2 class="h2" data-split>The founders</h2>
      <ul class="founders__list">{founders}</ul>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">{section_head('', 'The people behind the projects')}
    {team_carousel(c, members)}
  </div>
</section>
<section class="section band">
  <div class="container story__grid">
    <blockquote class="pullquote" data-reveal>The best ideas rarely happen in isolation.</blockquote>
    <div class="prose" data-reveal><p>We are looking for collaborators who share our curiosity, and clients with extraordinary ambitions.</p><div class="actions"><a class="btn btn--light" href="{c.loc}contact.html">Get in touch</a></div></div>
  </div>
</section>'''
    write(c, 'The team | Archipixels', 'Meet the Archipixels team, led by founders Shivika and Abhinav in Lucknow.', 'team.jpg', 'team', 'team.html', body)


def page_member(t, m):
    """A team member's profile page. The layout is the same in every direction. Text comes from data/team.json."""
    c = Ctx(t, f"team/{m['slug']}.html")
    name = member_name(m)
    if m['founder']:
        media = f'<img src="{img(c, "founders.jpg")}" alt="{e(m["name"])} and {e(" and ".join(x["name"] for x in TEAM if x["founder"] and x is not m))}, founders of Archipixels" loading="eager">'
    else:
        media = '<div class="member__photo member__photo--large"><span>Photo</span></div>'
    focus = ''.join(f'<li>{e(x)}</li>' for x in m['focus'])
    others = [x for x in TEAM if x is not m]
    body = f'''<section class="page-hero">
  <div class="container page-hero__grid">
    <div><a class="back" href="{c.loc}team.html">The team</a><p class="eyebrow" data-reveal>{e(m['role'])}</p><h1 class="display" data-split>{e(m['name'])}</h1>
    <p class="lead" data-reveal>{placeholder(m['intro'])}</p></div>
    <figure class="page-hero__media parallax">{media}</figure>
  </div>
</section>
<div class="container"><dl class="facts" data-reveal>
  <div><dt>Role</dt><dd>{e(m['role'])}</dd></div>
  <div><dt>With the studio since</dt><dd>{placeholder(m['since']) if m['since'].startswith('[') else e(m['since'])}</dd></div>
  <div><dt>Based in</dt><dd>Lucknow</dd></div>
  <div><dt>Works on</dt><dd>{placeholder('[PROJECT TYPES]')}</dd></div>
</dl></div>
<section class="section story">
  <div class="container story__grid">
    <blockquote class="pullquote" data-reveal>{placeholder(m['quote'])}</blockquote>
    <div class="prose" data-reveal>
      <p>{placeholder(m['bio'])}</p>
      <h2 class="mini-title">Focus</h2><ul class="chips-static">{focus}</ul>
    </div>
  </div>
</section>
<section class="section surface">
  <div class="container">{section_head('', 'Meet the rest of the team')}
    {team_carousel(c, others)}
  </div>
</section>
{cta(c)}'''
    write(c, f'{name} | Archipixels', f"{name}, {m['role']} at Archipixels, an architecture and interior design studio in Lucknow.", 'team.jpg', 'member', 'team.html', body)


def page_services(t):
    c = Ctx(t, 'services.html')
    rows_data = [
        ('Architecture', 'deco-facade.jpg', 'The Deco Grand, a hotel facade in Art Deco style', ['the-deco-grand', 'the-heritage-mosaic', 'shreeya-vista-homes', 'warehouse-studio']),
        ('Interior design', 'narula.jpg', 'A drawing room at House of Narula with ornate ceilings', ['house-of-narula', 'danzeria-by-danbro', 'hons-grey-opera', 'kesarwani-residence', 'pixel-pop']),
        ('Space planning', 'buttercup.jpg', 'Buttercup Bungalow, planned as distinct zones', ['buttercup-bungalow', 'shreeya-vista-homes', 'ksmb-marketing-office']),
        ('Turnkey projects', 'warehouse.jpg', 'Warehouse Studio, built from concept to completion', []),
    ]
    text = {s['name']: s['text'] for s in SITE['services']}
    rows = ''
    for name, im, alt, slugs in rows_data:
        links = ''.join(f'<li><a class="link-arrow" href="{c.loc}projects/{sl}.html">{e(BY_SLUG[sl]["name"])}{arrow_svg()}</a></li>' for sl in slugs)
        extra = f'<p class="service-row__label">Examples</p><ul class="service-row__links">{links}</ul>' if links else f'<p>{placeholder("[TURNKEY EXAMPLES: projects delivered from design to handover.]")}</p>'
        rows += f'''<article class="service-row">
  <figure class="service-row__media parallax"><img src="{img(c, im)}" alt="{e(alt)}" loading="lazy"></figure>
  <div class="service-row__copy" data-reveal><h2 class="h2">{e(name)}</h2><p class="lead">{e(text[name])}</p>{extra}</div>
</article>'''
    body = f'''<section class="page-hero page-hero--simple">
  <div class="container"><p class="eyebrow" data-reveal>Services</p><h1 class="display" data-split>What we design and build.</h1>
  <p class="lead" data-reveal>Hotels, cafés, residences, workplaces and themed stays, each with an identity of its own.</p></div>
</section>
<section class="services-rows"><div class="container">{rows}</div></section>
{cta(c)}'''
    write(c, 'Services | Archipixels', 'Architecture, interior design, space planning and turnkey projects by Archipixels in Lucknow.', 'narula.jpg', 'services', 'services.html', body)


def legacy_list(c, items):
    """Earlier works as a list of links to their detail pages (earlier/<slug>.html)."""
    def row(x):
        meta = ' · '.join(v for v in (x['type'], x['location']) if v)
        return (f'<li><a href="{c.loc}earlier/{x["slug"]}.html"><span class="legacy__name">{e(x["name"])}</span>'
                f'<span class="legacy__meta">{e(meta)}</span><span class="legacy__year">{e(x["year"])}{arrow_svg()}</span></a></li>')
    return f'<ul class="legacy__list" data-reveal>{"".join(row(x) for x in items)}</ul>'


def legacy_section(c):
    """The Our earlier works block at the foot of the Works page. Add a project in data/legacy-projects.json and it appears here."""
    return f'''<section class="section surface legacy" id="earlier">
  <div class="container">{section_head('', 'Our earlier works')}
    {legacy_list(c, LEGACY)}
  </div>
</section>'''


def page_earlier(t, x):
    """Detail page of an earlier work: header, facts, photo slider and the paragraphs from data/legacy-projects.json.
    Shared by all four directions. Facts and paragraphs that are not known yet are left out, not filled with placeholders."""
    c = Ctx(t, f"earlier/{x['slug']}.html")
    srcs = [f"{c.base}assets/img/earlier/{f}" for f in x['images']]
    facts = [('Type', x['type']), ('Location', x['location']), ('Year', x['year'])]
    facts = ''.join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k, v in facts if v)
    lead = f'<p class="lead" data-reveal>{e(x["summary"])}</p>' if x['summary'] and not x['story'] else ''
    story = ''.join(f'<p{" class=\"lead\"" if k == 0 else ""}>{e(para)}</p>' for k, para in enumerate(x['story']))
    prose = f'<section class="section"><div class="container"><div class="prose" data-reveal>{story}</div></div></section>' if story else ''
    i = LEGACY.index(x)
    more = [LEGACY[(i + k) % len(LEGACY)] for k in (1, 2, 3) if len(LEGACY) > k]
    body = f'''<section class="page-hero page-hero--simple">
  <div class="container">
    <a class="back" href="{c.loc}works.html#earlier">Our earlier works</a>
    <p class="eyebrow" data-reveal>{e(x['category'])} · {e(x['type'])}</p>
    <h1 class="display" data-split>{e(x['name'])}</h1>
    {lead}
  </div>
</section>
<div class="container">{f'<dl class="facts facts--three" data-reveal>{facts}</dl>' if facts else ''}</div>
{gallery_slider(c, x['name'], srcs, inline=(t == 'd'), group='earlier')}
{prose}
<section class="section surface legacy">
  <div class="container">{section_head('', 'More earlier works', (c.loc + 'works.html#earlier', 'All works'))}
    {legacy_list(c, more)}
  </div>
</section>
{cta(c, 'Have a space in mind? Tell us its story.')}'''
    write(c, f"{x['name']} | Archipixels", f"{x['name']}, {x['type'].lower()}{' in ' + x['location'] if x['location'] else ''}. An earlier project by Archipixels.", f"earlier/{x['images'][0]}", 'earlier', 'works.html', body)


def page_works(t):
    c = Ctx(t, 'works.html')
    chips = ''.join(f'<button class="chip{" is-active" if k == "all" else ""}" type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{e(l)}</button>' for k, l in FILTERS)
    if t == 'b':
        listing = f'<ul class="index-list">{"".join(index_row(c, p) for p in PROJECTS)}</ul>'
    else:
        listing = f'<div class="grid-works">{"".join(card_work(c, p) for p in PROJECTS)}</div>'
    body = f'''<section class="page-hero page-hero--simple">
  <div class="container">
    <p class="eyebrow" data-reveal>Selected works</p>
    <h1 class="display" data-split>Spaces that make you feel something.</h1>
    <p class="lead" data-reveal>Every project begins with a different story, and we never repeat a design.</p>
  </div>
</section>
<section class="section works">
  <div class="container">
    <h2 class="sr-only">All projects</h2>
    <!-- component: filter-bar -->
    <div class="filters" role="group" aria-label="Filter projects">{chips}<span class="filters__count" data-count aria-live="polite">{len(PROJECTS)} projects</span></div>
    {listing}
  </div>
</section>
{legacy_section(c)}
{cta(c)}'''
    write(c, 'Selected works | Archipixels', 'Hotels, cafés, residences, workplaces and themed stays by Archipixels.', 'deco-facade.jpg', 'works', 'works.html', body)


def facts_html(p):
    loc = e(p['place']) if p['place'] else placeholder('[LOCATION]')
    return f'''<dl class="facts">
  <div><dt>Type</dt><dd>{e(p['kind'])}</dd></div>
  <div><dt>Location</dt><dd>{loc}</dd></div>
  <div><dt>Year</dt><dd>{placeholder('[YEAR]')}</dd></div>
  <div><dt>Area</dt><dd>{placeholder('[AREA IN SQ FT]')}</dd></div>
</dl>'''


def project_hero_a(c, p):
    """A's project hero and facts row. Direction D uses it as well."""
    by = f'<p class="phero__by">by {e(p["by"])}</p>' if p['by'] else ''
    return f'''<section class="phero phero--a">
  <div class="phero__media parallax"><img src="{img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="eager"></div>
  <div class="phero__veil"></div>
  <div class="container phero__content">
    <a class="back" href="{c.loc}works.html">All selected works</a>
    <p class="eyebrow">{e(meta_line(p))}</p>
    <h1 class="phero__title" data-split>{e(p['name'])}</h1>{by}
    <p class="phero__tag">{e(p['tagline'])}</p>
  </div>
</section>
<div class="container facts-wrap">{facts_html(p)}</div>'''


def project_story(p):
    story = p.get('story') or f"{p['tagline'][0].upper() + p['tagline'][1:]}."
    langs = ''.join(f'<li>{e(x)}</li>' for x in p['language'])
    details = ''.join(f'<li data-reveal>{e(x)}</li>' for x in p['details'])
    det = f'<h2 class="mini-title">Signature details</h2><ul class="details">{details}</ul>' if p['details'] else ''
    return f'''<section class="section pstory">
  <div class="container pstory__grid">
    <div><p class="eyebrow" data-reveal>The design language</p><ul class="chips-static" data-reveal>{langs}</ul></div>
    <div class="prose" data-reveal><p class="lead">{e(story)}</p><p class="placeholder">[PROJECT STORY: the brief, the idea behind the space and how it is used.]</p>{det}</div>
  </div>
</section>'''


def swatch_bg(c, x):
    # a palette entry may carry a photo of the material (marble, slate, bronze) as its third item
    return f'background-image:url({img(c, x[2])})' if len(x) > 2 else ''


def project_palette(c, p):
    if not p['palette']:
        return ''
    sw = ''.join(f'<li class="swatch" style="--sw:{x[1]}" data-reveal><span class="swatch__dot" style="{swatch_bg(c, x)}"></span><span class="swatch__name">{e(x[0])}</span></li>' for x in p['palette'])
    return f'''<!-- component: palette -->
<section class="section surface palette"><div class="container">{section_head('', 'Colour palette')}<ul class="palette__list">{sw}</ul></div></section>'''


def gallery_slider(c, name, srcs, inline=False, heading='Gallery', group='project'):
    """A Swiper slider of photos that open in the lightbox. `srcs` lists image addresses and `name` is their title and alt text.
    With `inline`, the heading is visually hidden (it stays for screen readers and search engines) and the
    arrows sit on the left and right edges of the slider. Direction D's project page uses it."""
    slides = ''.join(f'<div class="swiper-slide"><a class="glightbox" href="{src}" data-gallery="{group}" data-title="{e(name)}"><img src="{src}" alt="{e(name)}, view {i + 1}" loading="lazy"></a></div>' for i, src in enumerate(srcs))
    swiper = f'<div class="swiper gallery-swiper"><div class="swiper-wrapper">{slides}</div></div>'
    if inline:
        arrows = ui_arrows("gallery-prev", "gallery-next") if len(srcs) > 1 else ''
        return f'''<!-- component: project-gallery (Swiper + GLightbox) -->
<section class="section gallery gallery--inline">
  <h2 class="sr-only">{e(name)}, {e(heading.lower())}</h2>
  <div class="gallery__stage">{swiper}{arrows}</div>
</section>'''
    return f'''<!-- component: project-gallery (Swiper + GLightbox) -->
<section class="section gallery">
  <div class="container">{section_head('', heading, None)}</div>
  {swiper}
  {f'<div class="container gallery__ui">{ui_arrows("gallery-prev", "gallery-next")}</div>' if len(srcs) > 1 else ''}
</section>'''


def project_gallery(c, p, srcs=None, inline=False):
    """A's project gallery. `srcs` lists image addresses to show instead of the card and gallery photos."""
    return gallery_slider(c, p['name'], srcs or [img(c, f) for f in [p['card']] + p['gallery']], inline)


def map_card(c):
    """The studio on a map. The Google map loads only after a click, so a visit to the page sets no Google cookies.
    Without JavaScript the link under it opens Google Maps."""
    return f'''<!-- component: map-card (the embed loads on click) -->
<div class="map-card" data-reveal>
  <div class="map-card__stage" data-map-src="{e(SITE['maps_embed'])}">
    <div class="map-card__veil">
      <svg class="map-card__pin" viewBox="0 0 24 32" width="30" height="40" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M12 31C12 31 2 19.5 2 12a10 10 0 0 1 20 0c0 7.500-10 19-10 19Z"/><circle cx="12" cy="12" r="3.600"/></svg>
      <b>Archipixels</b><span>{e(SITE['address'])}</span>
      <button class="btn btn--ghost map-card__load" type="button">Show the map</button>
    </div>
  </div>
  <a class="link-arrow" href="{e(SITE['maps_url'])}" target="_blank" rel="noopener">Open in Google Maps{arrow_svg()}</a>
</div>'''


def page_project(t, p, idx):
    c = Ctx(t, f"projects/{p['slug']}.html")
    gal_imgs = [p['card']] + p['gallery']
    by = f'<p class="phero__by">by {e(p["by"])}</p>' if p['by'] else ''
    if t == 'a':
        hero = project_hero_a(c, p)
    elif t == 'b':
        stack = ''.join(f'<figure class="reveal-img"><img src="{img(c, f)}" alt="{e(p["name"])}, view {i + 1}" loading="{"eager" if i == 0 else "lazy"}"></figure>' for i, f in enumerate(gal_imgs))
        hero = f'''<section class="phero phero--b">
  <div class="container phero__grid">
    <div class="phero__side">
      <a class="back" href="{c.loc}works.html">All selected works</a>
      <p class="eyebrow">{e(meta_line(p))}</p>
      <h1 class="phero__title" data-split>{e(p['name'])}</h1>{by}
      <p class="phero__tag">{e(p['tagline'])}</p>
      {facts_html(p)}
    </div>
    <div class="phero__stack">{stack}</div>
  </div>
</section>'''
    else:
        hero = f'''<section class="phero phero--c">
  <div class="container phero__grid">
    <div class="phero__copy">
      <a class="back" href="{c.loc}works.html">All selected works</a>
      <div class="sticker-row"><span class="sticker sticker--yellow">{e(p['kind'])}</span>{f'<span class="sticker sticker--red">{e(p["place"])}</span>' if p['place'] else ''}</div>
      <h1 class="phero__title" data-split>{e(p['name'])}</h1>{by}
      <p class="phero__tag">{e(p['tagline'])}</p>
    </div>
    <figure class="phero__frame tilt"><img src="{img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="eager"></figure>
  </div>
  <div class="container facts-wrap">{facts_html(p)}</div>
</section>'''
    body_story, pal, gallery = project_story(p), project_palette(c, p), project_gallery(c, p)
    rel = [PROJECTS[(idx + k) % len(PROJECTS)] for k in (1, 2, 3)]
    related = f'''<section class="section related"><div class="container">{section_head('', 'More projects', (c.loc + 'works.html', 'All works'))}<div class="grid-works grid-works--three">{''.join(card_work(c, r) for r in rel)}</div></div></section>'''
    body = hero + body_story + pal + gallery + related + cta(c, 'Have a space in mind? Tell us its story.')
    lt = lit_text(p['lit']) if t == 'b' else None   # B uses --lit as text colour on near-black
    style = f'<style>body.page-project{{--lit:{p["lit"]}' + (f';--lit-text:{lt}' if lt else '') + '}</style>\n'
    write(c, f"{p['name']} | Archipixels", f"{p['name']}: {p['tagline']}. {p['kind']} by Archipixels.", p['card'], 'project', 'works.html', body, style)


def contact_split(c, extra=''):
    """Facts row, pen drawing and enquiry form. Direction A and D share it. `extra` adds links under the form."""
    v = PF['fixed']['villa']
    maps = SITE['maps_url']
    return f'''<section class="section contact-page">
  <div class="container">
    <dl class="contact-facts" data-reveal>
      <div><dt>E-mail</dt><dd><a href="mailto:{SITE['email']}">{SITE['email']}</a></dd></div>
      <div><dt>Phone</dt><dd><a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a><span>{e(SITE['phone_note'])}</span></dd></div>
      <div><dt>Address</dt><dd><a href="{e(maps)}" target="_blank" rel="noopener">{e(SITE['address'])}</a></dd></div>
      <div><dt>Social</dt><dd class="social-reveal"><a href="{SITE['instagram']}" target="_blank" rel="noopener">{SITE['instagram_handle']}</a>{social_icons()}</dd></div>
    </dl>
    <div class="contact-split">
      <div class="contact-art" data-reveal><img src="{c.base}portfolio/img/{v['file']}" width="{v['w']}" height="{v['h']}" alt="Pen drawing of a three-storey villa facade by Archipixels" loading="lazy"></div>
      <div class="contact-form" data-reveal>{form('contact')}<p class="contact-wa"><a class="link-arrow" href="{wa()}" target="_blank" rel="noopener">Or message us on WhatsApp{arrow_svg()}</a></p>{extra}</div>
    </div>
  </div>
</section>'''


def page_contact(t):
    c = Ctx(t, 'contact.html')
    hero = '''<section class="page-hero page-hero--simple">
  <div class="container"><p class="eyebrow" data-reveal>Contact</p><h1 class="display" data-split>Have something wild in mind?</h1></div>
</section>'''
    if t == 'a':
        write(c, 'Contact | Archipixels', 'Contact Archipixels in Gomti Nagar, Lucknow, by WhatsApp, phone or email.', 'studio.jpg', 'contact', 'contact.html', hero + '\n' + contact_split(c))
        return
    social_items = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{ic}<span>{n}</span></a></li>' for n, u, ic in social_links())
    body = hero + f'''
<section class="section">
  <div class="container enquire__grid">
    <div class="contact-card" data-reveal>
      <h2 class="h3">Studio</h2>
      <address class="contact-list">
        <span>{e(SITE['address'])}</span>
        <a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a><span>{e(SITE['phone_note'])}</span>
        <a href="mailto:{SITE['email']}">{SITE['email']}</a>
        <ul class="footer-list footer-list--social">{social_items}</ul>
      </address>
      <a class="btn btn--primary" href="{wa()}" target="_blank" rel="noopener">Chat on WhatsApp</a>
    </div>
    <div class="panel" data-reveal>{form('contact')}</div>
  </div>
</section>'''
    write(c, 'Contact | Archipixels', 'Contact Archipixels in Gomti Nagar, Lucknow, by WhatsApp, phone or email.', 'studio.jpg', 'contact', 'contact.html', body)


def error_hero(c):
    return f'''<section class="page-hero page-hero--simple">
  <div class="container">
    <p class="eyebrow" data-reveal>Error 404</p>
    <p class="err-code" aria-hidden="true">404</p>
    <h1 class="display" data-split>This page is not here.</h1>
    <p class="lead" data-reveal>The link may be old, or the address may have a typing error.</p>
    <p class="err-actions" data-reveal><a class="btn btn--primary" href="{c.loc}index.html">Back to home</a> <a class="btn btn--ghost" href="{c.loc}works.html">Selected works</a></p>
  </div>
</section>'''


def page_404(t):
    c = Ctx404(t)
    picks = [BY_SLUG[s] for s in FEATURED[:3]]
    if t == 'b':
        listing = f'<ul class="index-list">{"".join(index_row(c, p) for p in picks)}</ul>'
    else:
        listing = f'<div class="grid-works">{"".join(card_work(c, p) for p in picks)}</div>'
    body = f'''{error_hero(c)}
<section class="section works">
  <div class="container">{section_head('', 'Recent work', (c.loc + 'works.html', 'View all works'))}
    {listing}
  </div>
</section>
{cta(c)}'''
    write(c, 'Page not found | Archipixels', 'This page does not exist. Start from the Archipixels home page or the works.', 'deco-facade.jpg', '404', '', body,
          extra='<meta name="robots" content="noindex">\n')


def page_404_root():
    """The fallback 404 for URLs outside a version folder, in the chooser's style. Its paths start at the site root."""
    tpl = (ROOT / 'tools/root-404.tpl').read_text()
    page = tpl.replace('@EMAIL@', SITE['email']).replace('@ADDRESS@', e(SITE['address'])).replace('@SIGN_OFF@', e(SITE['sign_off']))
    (ROOT / '404.html').write_text(page)


def main():
    for t in THEMES:
        out = ROOT / t
        if out.exists():
            shutil.rmtree(out)
        page_home(t)
        page_about(t)
        page_studio(t)
        page_team(t)
        for m in TEAM:
            page_member(t, m)
        page_services(t)
        page_works(t)
        page_contact(t)
        page_404(t)
        for i, p in enumerate(PROJECTS):
            page_project(t, p, i)
        for x in LEGACY:
            page_earlier(t, x)
    page_404_root()
    print('built', sum(1 for _ in ROOT.glob('[abc]/**/*.html')), 'pages')


if __name__ == '__main__':
    main()
