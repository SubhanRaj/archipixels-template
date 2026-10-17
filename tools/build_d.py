#!/usr/bin/env python3
"""Builds direction D (d/): the multi-page approach and look of direction A,
with the presentation of the one-page portfolio version.

Run from the package root:  python3 tools/build_d.py

It reuses the page functions of tools/build.py for About, Studio and Services,
and replaces Home, Works, Project, Team and Contact. It writes only to d/.
It never rewrites a/, b/, c/ or portfolio/.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as b          # noqa: E402  (shared helpers, data and page functions)
import build_portfolio as bp  # noqa: E402  (colour helpers and portfolio data)

e = b.e
ROOT = b.ROOT
SITE = b.SITE
PROJECTS = b.PROJECTS
PF = bp.PF
OUT = ROOT / 'd'

b.THEMES['d'] = dict(
    name='Velvet Portfolio', color='#14090C',
    fonts='https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,600;0,700;1,400&family=Herr+Von+Muellerhoff&family=Jost:wght@300;400;500&display=swap')

SPOTLIGHT = ['helios-maximus', 'chihiro', 'mio-marito-gelato']
HERO = [('cover.jpg', 'Helios Maximus', 'helios-maximus'), ('the-deco-grand-1.jpg', 'The Deco Grand', 'the-deco-grand'),
        ('hons-grey-opera-2.jpg', 'Hons, Grey Opera', 'hons-grey-opera'), ('warehouse-studio-1.jpg', 'Warehouse Studio', 'warehouse-studio')]
DARK = '#14090C'


def pimg(c, name):
    return f'{c.base}portfolio/img/{name}'


def write_d(c, title, desc, og, page_cls, active, body, extra=''):
    """Same as build.write, but D loads the A stylesheet and script as its base."""
    out = OUT / c.rel
    out.parent.mkdir(parents=True, exist_ok=True)
    html = b.head(c, title, desc, og, page_cls, extra) + b.header(c, active) + body + b.footer(c)
    html = html.replace('<body class="theme-d ', '<body class="theme-a theme-d ')
    html = html.replace('</a></li></ul>\n    </div>\n  </div>\n  <div class="container site-footer__base">',
                        f'</a></li><li><a href="{c.base}{PDF_NAME}" download>Portfolio PDF</a></li></ul>\n    </div>\n  </div>\n  <div class="container site-footer__base">')
    css = f'<link rel="stylesheet" href="{c.base}assets/css/theme-d.css">'
    html = html.replace(css, f'<link rel="stylesheet" href="{c.base}assets/css/theme-a.css">\n{css}')
    js = f'<script src="{c.base}assets/js/theme-d.js"></script>'
    html = html.replace(js, f'<script src="{c.base}assets/js/theme-a.js"></script>\n{js}')
    out.write_text(html)


PDF_NAME = 'assets/downloads/Archipixels-Portfolio.pdf'
PDF_LABEL = 'Download portfolio (PDF, 5 MB)'


def pdf_link(c, cls='btn btn--outline', label=PDF_LABEL):
    return f'<a class="{cls}" href="{c.base}{PDF_NAME}" download>{label}</a>'


b.write = write_d   # About, Studio and Services call build.write


# ------------------------------------------------------------ components ----

def project_meta(p):
    return b.meta_line(p)


def swatches(p):
    d = PF['projects'][p['slug']]
    cols = d.get('swatches') or [x[1] for x in p['palette']]
    if not p['palette']:
        return ''
    items = ''.join(f'<li><span class="d-dot" style="--c:{col}"></span><span>{e(n)}</span></li>'
                    for col, (n, _) in zip(cols, p['palette']))
    return f'<ul class="d-swatches" aria-label="Colour palette">{items}</ul>'


def frame(c, im, alt, lazy=True, gallery=None, title='', href=None, caption=''):
    inner = (f'<div class="d-frame" style="aspect-ratio:{im["w"]}/{im["h"]}"><div class="d-frame__in">'
             f'<img src="{pimg(c, im["file"])}" width="{im["w"]}" height="{im["h"]}" alt="{e(alt)}"'
             f'{" loading=lazy" if lazy else ""} decoding="async"></div></div>')
    if gallery:
        inner = (f'<a class="glightbox" href="{pimg(c, im["file"])}" data-gallery="{e(gallery)}" '
                 f'data-title="{e(title)}" aria-label="Open photo: {e(title)}">{inner}</a>')
    elif href:
        inner = f'<a href="{href}" aria-label="{e(title)}">{inner}</a>'
    cap = f'<figcaption>{e(caption)}</figcaption>' if caption else ''
    return f'<figure class="d-shot">{inner}{cap}</figure>'


def tile(c, p, n):
    d = PF['projects'][p['slug']]
    im = d['images'][0]
    cats = ' '.join(p['cats'])
    return f'''<li class="d-tile" data-cats="{cats}" style="--c:{d['bg']}" data-reveal>
  <a href="{c.loc}projects/{p['slug']}.html">
    <span class="d-tile__img"><img src="{pimg(c, im['file'])}" width="{im['w']}" height="{im['h']}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="lazy"></span>
    <span class="d-tile__meta"><b>{n:02d}</b><span>{e(p['name'])}</span><em>{e(p['kind'])}</em></span>
  </a>
</li>'''


def pj_block(c, p, n, prev_bg, full):
    """The project block: photos on the left, tan panel on the right."""
    d = PF['projects'][p['slug']]
    bg = d['bg']
    ink = bp.ink_for(bg)
    imgs = d['images']
    layout = d.get('layout') or {1: 'single', 2: 'duo', 3: 'trio', 4: 'quad'}[len(imgs)]
    if full:
        shots = ''.join(frame(c, im, f'{p["name"]}, photograph {i + 1} of {len(imgs)}', i > 0, p['slug'] + '-photos',
                              p['name'] + (f': {im["caption"]}' if im.get('caption') else ''), caption=im.get('caption', ''))
                        for i, im in enumerate(imgs))
        media_cls = f'd-media d-media--{layout}'
    else:
        shots = frame(c, imgs[0], f'{p["name"]}, an Archipixels project', True, None, p['name'],
                      href=f'{c.loc}projects/{p["slug"]}.html')
        media_cls = 'd-media d-media--single'
    by = f'<p class="d-panel__by">{e(p["by"])}</p>' if p['by'] else ''
    title_tag = 'h1' if full else 'h2'
    tail = ''
    if full:
        tail = (f'<h3>The design language</h3><p>{" | ".join(e(x) for x in p["language"])}</p>'
                f'<h3>Signature details</h3><p>{" · ".join(e(x) for x in p["details"])}</p>')
        if p.get('story'):
            tail += f'<h3>The story</h3><p>{e(p["story"])}</p>'
        tail += f'<p class="d-panel__cta"><a class="btn btn--primary" href="{c.loc}contact.html">Discuss a space like this</a></p>'
    else:
        tail = (f'<h3>The design language</h3><p>{" | ".join(e(x) for x in p["language"])}</p>'
                f'<p class="d-panel__cta"><a class="link-arrow" href="{c.loc}projects/{p["slug"]}.html">View project{b.arrow_svg()}</a></p>')
    return f'''<section class="d-pj{'' if full else ' d-pj--spot'}" style="--bg:{bg};--prev:{prev_bg};--ink:{ink}">
  <div class="container d-pj__inner">
    <div class="{media_cls}">{shots}</div>
    <article class="d-panel">
      <p class="d-panel__no">No. {n:02d} <span>{e(project_meta(p))}</span></p>
      <{title_tag} class="d-panel__title">{e(p['name'])}</{title_tag}>
      {by}
      <p class="d-panel__tagline">{e(p['tagline'])}</p>
      {swatches(p)}
      {tail}
    </article>
  </div>
</section>'''


def hero_d(c):
    slides = ''.join(f'''<div class="swiper-slide" data-title="{e(name)}" data-meta="{e(project_meta(b.BY_SLUG[slug]))}" data-href="{c.loc}projects/{slug}.html">
  <img class="hero__img" src="{pimg(c, f)}" alt="" {'loading="eager"' if i == 0 else 'loading="lazy"'}>
</div>''' for i, (f, name, slug) in enumerate(HERO))
    return f'''<!-- component: hero-slideshow (D, same behaviour as A) -->
<section class="hero hero--a hero--d" aria-label="Introduction">
  <div class="swiper hero-swiper"><div class="swiper-wrapper">{slides}</div></div>
  <div class="hero__veil"></div>
  <div class="hero__spot" aria-hidden="true"></div>
  <div class="container hero__content">
    <p class="eyebrow" data-reveal>{e(SITE['descriptor'])}</p>
    <h1 class="hero__title" data-split>Archipixels. Selected works.</h1>
    <p class="lead" data-reveal>{e(SITE['tagline'])} An architecture and interior design studio in Lucknow, for clients with extraordinary ambitions.</p>
    <div class="actions" data-reveal>
      <a class="btn btn--primary" href="{c.loc}works.html">See selected works</a>
      <a class="link-arrow" href="{c.loc}about.html">About the studio{b.arrow_svg()}</a>
    </div>
  </div>
  <div class="container hero__ui">
    <div class="hero__now"><span class="hero__now-meta"></span><a class="hero__now-title" href="#"></a></div>
    <div class="hero__pagination" aria-hidden="true"></div>
    {b.ui_arrows('hero-prev', 'hero-next')}
  </div>
</section>
{b.marquee([p['name'] for p in PROJECTS[:12]])}'''


def approach(c):
    im = PF['fixed']['intro']
    return f'''<!-- component: approach -->
<section class="section d-approach">
  <div class="container d-split">
    <figure class="d-split__media parallax"><img src="{pimg(c, im['file'])}" width="{im['w']}" height="{im['h']}" alt="A layered, colourful Archipixels interior with hanging lamps and patterned floors" loading="lazy"></figure>
    <div class="d-split__text">
      <p class="eyebrow" data-reveal>Our approach</p>
      <h2 class="h2" data-split>Spaces with stories of their own.</h2>
      <p class="lead" data-reveal>We believe every space has a story waiting to be told. At Archipixels, design begins with curiosity. A curiosity about people, places, cultures and the little things that often go unnoticed.</p>
      <p data-reveal>Spaces that are layered, expressive, sometimes unexpected, but always thoughtful in their details. We create artful, expressive spaces, each with its own identity. Every project begins with a different story, and we never repeat a design.</p>
      <p class="d-quote" data-reveal>We don’t believe every space should look a certain way. We believe it should feel a certain way and make you feel something, too.</p>
    </div>
  </div>
</section>'''


def founders(c):
    im = PF['fixed']['founders']
    return f'''<!-- component: founders -->
<section class="section surface d-founders">
  <div class="container d-split d-split--flip">
    <div class="d-split__text">
      <p class="eyebrow" data-reveal>The founders</p>
      <h2 class="h2" data-split>Two minds. A thousand ideas.</h2>
      <p class="lead" data-reveal>We’re <strong>{SITE['founders'][0]}</strong> and <strong>{SITE['founders'][1]}</strong>, partners in life, work and a shared curiosity for everything around us. Our love for design, travel, art and the unexpected has shaped the journey of Archipixels.</p>
      <p data-reveal>We started Archipixels in {SITE['founded']}. Our journey began in Dubai, where we gained international experience before founding Archipixels in India. Now we’re ready to take that energy worldwide.</p>
      <div class="actions" data-reveal><a class="link-arrow" href="{c.loc}about.html">About us{b.arrow_svg()}</a><a class="link-arrow" href="{c.loc}team.html">The team{b.arrow_svg()}</a></div>
    </div>
    <figure class="d-split__media parallax"><img src="{pimg(c, im['file'])}" width="{im['w']}" height="{im['h']}" alt="Shivika and Abhinav, the founders of Archipixels, seated on a velvet sofa" loading="lazy"></figure>
  </div>
</section>'''


def wall(c, projects=None, link=True):
    items = projects or PROJECTS
    lis = ''.join(tile(c, p, PROJECTS.index(p) + 1) for p in items)
    head = b.section_head('Selected works', f'{len(PROJECTS)} projects, each with its own colours.',
                          (c.loc + 'works.html', 'View all works') if link else None)
    return f'''<!-- component: works-wall -->
<section class="section d-wallsec">
  <div class="container">{head}<ul class="d-wall">{lis}</ul></div>
</section>'''


def closing(c):
    im = PF['fixed']['closing']
    line = SITE['closing_line'].replace("'", '’')
    return f'''<!-- component: closing-line -->
<section class="d-closing" id="contact">
  <div class="d-closing__bg"><img src="{pimg(c, im['file'])}" width="{im['w']}" height="{im['h']}" alt="" loading="lazy"></div>
  <div class="container d-closing__body">
    <p class="d-closing__line" data-closing>{e(line)}</p>
    <img class="d-closing__logo" src="{c.base}assets/brand-originals/logo-stacked-light.png" width="260" height="160" alt="Archipixels, design that works" loading="lazy">
    <div class="actions"><a class="btn btn--primary" href="{b.wa()}" target="_blank" rel="noopener">Chat on WhatsApp</a><a class="btn btn--dark" href="{c.loc}contact.html">Contact page</a>{pdf_link(c)}</div>
  </div>
</section>'''


# ----------------------------------------------------------------- pages ----

def page_home():
    c = b.Ctx('d', 'index.html')
    spots = ''
    prev = DARK
    for slug in SPOTLIGHT:
        p = b.BY_SLUG[slug]
        spots += pj_block(c, p, PROJECTS.index(p) + 1, prev, False)
        prev = PF['projects'][slug]['bg']
    intro = f'''<section class="section d-spotintro"><div class="container">{b.section_head('', 'A few stories, in their own colours', (c.loc + 'works.html', 'View all works'))}</div></section>'''
    ld = bp.json.dumps({
        '@context': 'https://schema.org', '@type': 'Organization', 'name': SITE['brand'],
        'description': 'Architecture, interior design and experience design studio in Lucknow, India.',
        'telephone': SITE['phone_tel'], 'email': SITE['email'], 'sameAs': [SITE['instagram']],
        'address': {'@type': 'PostalAddress', 'streetAddress': '1/146, Gomti Nagar', 'addressLocality': 'Lucknow', 'addressCountry': 'IN'}}, indent=2)
    body = hero_d(c) + approach(c) + founders(c) + intro + spots + wall(c) + b.services(c) + closing(c)
    write_d(c, 'Archipixels | Architecture and interiors, Lucknow',
            'Archipixels is an architecture and interior design studio in Lucknow. Hotels, cafés, residences, workplaces and themed stays.',
            'helios.jpg', 'home', '', body, f'<script type="application/ld+json">\n{ld}\n</script>\n')


def page_works():
    c = b.Ctx('d', 'works.html')
    chips = ''.join(f'<button class="chip{" is-active" if k == "all" else ""}" type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{e(l)}</button>' for k, l in b.FILTERS)
    lis = ''.join(tile(c, p, i + 1) for i, p in enumerate(PROJECTS))
    legacy = ''.join(f'<li><span class="legacy__name">{e(x["name"])}</span><span class="legacy__meta">{e(x["type"])} · {e(x["location"])}</span><span class="legacy__year">{e(x["year"])}</span></li>' for x in b.LEGACY)
    body = f'''<section class="page-hero page-hero--simple">
  <div class="container">
    <p class="eyebrow" data-reveal>Selected works</p>
    <h1 class="display" data-split>Spaces that make you feel something.</h1>
    <p class="lead" data-reveal>Every project begins with a different story, and we never repeat a design.</p>
  </div>
</section>
<section class="section works">
  <div class="container">
    <!-- component: filter-bar -->
    <div class="filters" role="group" aria-label="Filter projects">{chips}<span class="filters__count" data-count aria-live="polite">{len(PROJECTS)} projects</span></div>
    <ul class="d-wall d-wall--works">{lis}</ul>
  </div>
</section>
<section class="section surface legacy">
  <div class="container">{b.section_head('', 'Earlier work in Lucknow')}
    <ul class="legacy__list" data-reveal>{legacy}</ul>
  </div>
</section>
{b.cta(c)}'''
    write_d(c, 'Selected works | Archipixels', 'Hotels, cafés, residences, workplaces and themed stays by Archipixels.', 'deco-facade.jpg', 'works', 'works.html', body)


def gallery_d(c, p):
    """Swiper + GLightbox gallery with every photo of the project, as on A's project pages."""
    imgs = PF['projects'][p['slug']]['images']
    slides = ''.join(
        f'<div class="swiper-slide"><a class="glightbox" href="{pimg(c, im["file"])}" data-gallery="{e(p["slug"])}-gallery" '
        f'data-title="{e(p["name"] + (": " + im["caption"] if im.get("caption") else ""))}">'
        f'<img src="{pimg(c, im["file"])}" width="{im["w"]}" height="{im["h"]}" alt="{e(p["name"])}, view {i + 1} of {len(imgs)}" loading="lazy"></a></div>'
        for i, im in enumerate(imgs))
    ui = f'<div class="container gallery__ui">{b.ui_arrows("gallery-prev", "gallery-next")}</div>' if len(imgs) > 1 else ''
    return f'''<!-- component: project-gallery (Swiper + GLightbox) -->
<section class="section gallery d-gallery">
  <div class="container">{b.section_head('', 'Gallery', None)}</div>
  <div class="swiper gallery-swiper"><div class="swiper-wrapper">{slides}</div></div>
  {ui}
</section>'''


def _rgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _mix(a, z, t):
    """Blend colour a towards z by t (0 to 1), as a hex string."""
    ra, rz = _rgb(a), _rgb(z)
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(ra, rz))


def tone_style(bg):
    """Tokens that recolour A's project sections in the project's own colour."""
    ink = bp.ink_for(bg)
    accent = next((x for x in ('#D8A93A', '#8A5A12', '#7A1F2E', '#F3E9DC', '#14090C') if bp.contrast(bg, x) >= 4.5), ink)
    r, g, bl = _rgb(ink)
    return (f'--bg:{bg};--text:{ink};--muted:{_mix(ink, bg, .32)};--surface:{_mix(bg, ink, .07)};'
            f'--band:{_mix(bg, ink, .12)};--line:rgba({r},{g},{bl},.28);--accent:{accent};'
            f'--accent-ink:{bp.ink_for(accent)};--prev:{DARK}')


def page_project(p, idx):
    """A's project page (full-background hero), with the body recoloured to the project's colour."""
    c = b.Ctx('d', f"projects/{p['slug']}.html")
    d = PF['projects'][p['slug']]
    nxt = PROJECTS[(idx + 1) % len(PROJECTS)]
    nbg = PF['projects'][nxt['slug']]['bg']
    nim = PF['projects'][nxt['slug']]['images'][0]
    by = f'<p class="phero__by">by {e(p["by"])}</p>' if p['by'] else ''
    hero = f'''<section class="phero phero--a">
  <div class="phero__media parallax"><img src="{b.img(c, p['card'])}" alt="{e(p['name'])}, {e(p['kind'].lower())}" loading="eager"></div>
  <div class="phero__veil"></div>
  <div class="container phero__content">
    <a class="back" href="{c.loc}works.html">All selected works</a>
    <p class="eyebrow">{e(b.meta_line(p))}</p>
    <h1 class="phero__title" data-split>{e(p['name'])}</h1>{by}
    <p class="phero__tag">{e(p['tagline'])}</p>
  </div>
</section>'''
    story = p.get('story') or f"{p['tagline'][0].upper() + p['tagline'][1:]}."
    langs = ''.join(f'<li>{e(x)}</li>' for x in p['language'])
    details = ''.join(f'<li data-reveal>{e(x)}</li>' for x in p['details'])
    det = f'<h3 class="mini-title">Signature details</h3><ul class="details">{details}</ul>' if p['details'] else ''
    pal = ''
    if p['palette']:
        pal = f'''<section class="section d-tone__pal"><div class="container"><div class="d-tone__panel">
    <h2 class="h3">Colour palette</h2>{swatches(p)}</div></div></section>'''
    tone = f'''<div class="d-tone" style="{tone_style(d['bg'])}">
<div class="container facts-wrap">{b.facts_html(p)}</div>
<section class="section pstory">
  <div class="container pstory__grid">
    <div><p class="eyebrow" data-reveal>The design language</p><ul class="chips-static" data-reveal>{langs}</ul></div>
    <div class="prose" data-reveal><p class="lead">{e(story)}</p><p class="placeholder">[PROJECT STORY: the brief, the idea behind the space and how it is used.]</p>{det}
      <p class="d-tone__cta"><a class="btn btn--primary" href="{c.loc}contact.html">Discuss a space like this</a></p></div>
  </div>
</section>
{pal}
{gallery_d(c, p)}
</div>'''
    nxt_html = f'''<a class="d-next" href="{c.loc}projects/{nxt['slug']}.html" style="--bg:{nbg};--ink:{bp.ink_for(nbg)}">
  <img src="{pimg(c, nim['file'])}" width="{nim['w']}" height="{nim['h']}" alt="" loading="lazy">
  <span class="container d-next__body"><small>Next project · No. {(idx + 1) % len(PROJECTS) + 1:02d}</small><b>{e(nxt['name'])}</b><i>{b.arrow_svg()}</i></span>
</a>'''
    rel = [PROJECTS[(idx + k) % len(PROJECTS)] for k in (2, 3, 4)]
    related = f'''<section class="section d-related"><div class="container">{b.section_head('', 'More projects', (c.loc + 'works.html', 'All works'))}<ul class="d-wall d-wall--three">{''.join(tile(c, r, PROJECTS.index(r) + 1) for r in rel)}</ul></div></section>'''
    body = hero + tone + nxt_html + related + b.cta(c, 'Have a space in mind? Tell us its story.')
    write_d(c, f"{p['name']} | Archipixels", f"{p['name']}: {p['tagline']}. {p['kind']} by Archipixels.",
            p['card'], 'project', 'works.html', body)


def page_team():
    c = b.Ctx('d', 'team.html')
    team = PF['fixed']['team']
    fo = PF['fixed']['founders']
    names = ''.join(f'<li class="founder" data-reveal><h3>{e(n)}</h3><p class="founder__role">Founder</p></li>' for n in SITE['founders'])
    body = f'''<section class="page-hero">
  <div class="container page-hero__grid">
    <div><p class="eyebrow" data-reveal>Our team</p><h1 class="display" data-split>The Archipixels family.</h1>
    <p class="lead" data-reveal>We believe that when people are valued, supported and given love, they create their best work. We are more than a team; we are the Archipixels family, growing together, celebrating every milestone and standing by one another through every challenge.</p></div>
    <figure class="page-hero__media parallax"><img src="{pimg(c, team['file'])}" alt="The Archipixels team gathered on sofas around a coffee table" loading="eager"></figure>
  </div>
</section>
<section class="section surface">
  <div class="container founders">
    <figure class="founders__media parallax"><img src="{pimg(c, fo['file'])}" alt="Shivika and Abhinav, founders of Archipixels" loading="lazy"></figure>
    <div class="founders__copy">
      <h2 class="h2" data-split>The founders</h2>
      <ul class="founders__list">{names}</ul>
      <p class="lead" data-reveal>Partners in life, work and a shared curiosity for everything around us. Our love for design, travel, art and the unexpected has shaped the journey of Archipixels.</p>
    </div>
  </div>
</section>
<section class="section band">
  <div class="container story__grid">
    <blockquote class="pullquote" data-reveal>The best ideas rarely happen in isolation.</blockquote>
    <div class="prose" data-reveal><p>We are looking for collaborators who share our curiosity, and clients with extraordinary ambitions.</p><div class="actions"><a class="btn btn--light" href="{c.loc}contact.html">Get in touch</a></div></div>
  </div>
</section>'''
    write_d(c, 'The team | Archipixels', 'Meet the Archipixels team, led by founders Shivika and Abhinav in Lucknow.', 'team.jpg', 'team', 'team.html', body)


def page_contact():
    c = b.Ctx('d', 'contact.html')
    v = PF['fixed']['villa']
    maps = 'https://www.google.com/maps/search/?api=1&query=' + b.quote(SITE['address'])
    body = f'''<section class="page-hero page-hero--simple">
  <div class="container"><p class="eyebrow" data-reveal>Contact</p><h1 class="display" data-split>Have something wild in mind?</h1></div>
</section>
<section class="section d-contact">
  <div class="container">
    <dl class="d-contact__list" data-reveal>
      <div><dt>E-mail</dt><dd><a href="mailto:{SITE['email']}">{SITE['email']}</a></dd></div>
      <div><dt>Phone</dt><dd><a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a><span>{e(SITE['phone_note'])}</span></dd></div>
      <div><dt>Address</dt><dd><a href="{e(maps)}" target="_blank" rel="noopener">{e(SITE['address'])}</a></dd></div>
      <div><dt>Social</dt><dd><a href="{SITE['instagram']}" target="_blank" rel="noopener">{SITE['instagram_handle']}</a></dd></div>
    </dl>
    <div class="d-contact__split">
      <div class="d-contact__art" data-reveal><img src="{pimg(c, v['file'])}" width="{v['w']}" height="{v['h']}" alt="Pen drawing of a three-storey villa facade by Archipixels" loading="lazy"></div>
      <div class="d-contact__form" data-reveal>{b.form('contact')}<p class="d-contact__wa"><a class="link-arrow" href="{b.wa()}" target="_blank" rel="noopener">Or message us on WhatsApp{b.arrow_svg()}</a></p><p class="d-contact__wa"><a class="link-arrow" href="{c.base}{PDF_NAME}" download>Download the portfolio (PDF, 5 MB){b.arrow_svg()}</a></p></div>
    </div>
  </div>
</section>'''
    write_d(c, 'Contact | Archipixels', 'Contact Archipixels in Gomti Nagar, Lucknow, by WhatsApp, phone or email.', 'studio.jpg', 'contact', 'contact.html', body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    page_home()
    b.page_about('d')
    b.page_studio('d')
    page_team()
    b.page_services('d')
    page_works()
    page_contact()
    for i, p in enumerate(PROJECTS):
        page_project(p, i)
    print('built', sum(1 for _ in OUT.glob('**/*.html')), 'pages in d/')


if __name__ == '__main__':
    main()
