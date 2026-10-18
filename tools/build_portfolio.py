#!/usr/bin/env python3
"""Builds portfolio/index.html, the one-page portfolio version of the site.

Reads data/site.json, data/projects.json and data/portfolio.json.
It does not touch the a/, b/ or c/ directions.

Run from the package root:  python3 tools/build_portfolio.py
"""
import datetime
import html
import json
import os
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "portfolio", "index.html")


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


SITE = load("site.json")
PROJECTS = load("projects.json")
PF = load("portfolio.json")

e = html.escape


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


LIGHT_INK = "#F6EFE6"
DARK_INK = "#1B100A"


def ink_for(bg):
    return LIGHT_INK if contrast(bg, LIGHT_INK) >= contrast(bg, DARK_INK) else DARK_INK


def img(file, w, h, alt, lazy=True, cls=""):
    loading = ' loading="lazy" decoding="async"' if lazy else ""
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="img/{e(file)}" width="{w}" height="{h}" alt="{e(alt)}"{loading}>'


def frame(file, w, h, alt, lazy=True, gallery=None, title="", caption=""):
    inner = f'<div class="frame__in">{img(file, w, h, alt, lazy)}</div>'
    box = f'<div class="frame" style="aspect-ratio:{w}/{h}">{inner}</div>'
    if gallery:
        box = (
            f'<a class="glightbox" href="img/{e(file)}" data-gallery="{e(gallery)}" '
            f'data-title="{e(title)}" aria-label="Open photo: {e(title)}">{box}</a>'
        )
    if caption:
        return f'<figure class="shot">{box}<figcaption>{e(caption)}</figcaption></figure>'
    return f'<figure class="shot">{box}</figure>'


def fixed(key):
    return PF["fixed"][key]


# ---------------------------------------------------------------- head

def head():
    desc = (
        "Archipixels is an architecture and interior design studio in Lucknow, India. "
        "Selected works across homes, hotels, restaurants, offices, salons and townships."
    )
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Archipixels",
        "slogan": SITE["sign_off"],
        "foundingDate": str(SITE["founded"]),
        "email": SITE["email"],
        "telephone": SITE["phone_tel"],
        "url": "https://archipixels.com/",
        "sameAs": [SITE["instagram"], SITE["linkedin"], SITE["facebook"]],
        "address": {"@type": "PostalAddress", "streetAddress": "1/146, Gomti Nagar", "addressLocality": "Lucknow", "addressCountry": "IN"},
    }
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Archipixels | Selected Works</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="Archipixels | Selected Works">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="img/cover.jpg">
<meta name="theme-color" content="#591524">
<link rel="icon" type="image/png" href="../assets/img/brand/favicon.png">
<link rel="apple-touch-icon" href="../assets/img/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Herr+Von+Muellerhoff&family=Jost:wght@300;400;500&family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,500&display=swap">
<link rel="stylesheet" href="../assets/vendor/swiper-bundle.min.css">
<link rel="stylesheet" href="../assets/vendor/glightbox.min.css">
<link rel="stylesheet" href="css/portfolio.css">
<script type="application/ld+json">{json.dumps(org, ensure_ascii=False)}</script>
</head>
"""


# ---------------------------------------------------------------- chrome

ICON_LI = (
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="3" y="3" width="18" height="18" rx="3.500"/><path d="M8 10.500V16M8 7.800v.01M11.500 16v-5.500M11.500 13c0-1.600 1-2.600 2.400-2.600 1.500 0 2.100 1 2.100 2.500V16"/></svg>'
)
ICON_FB = (
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/><path d="M13.200 20.900v-6.700h2.200l.4-2.600h-2.600V9.900c0-.8.400-1.300 1.400-1.300h1.300V6.400c-.5-.1-1.200-.2-2-.2-2 0-3.300 1.200-3.300 3.400v2h-2.200v2.600h2.200v6.700"/></svg>'
)
ICON_IG = (
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
    '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.3" cy="6.7" r="1" fill="currentColor" stroke="none"/></svg>'
)


def header():
    return f"""<div class="veil" aria-hidden="true"><img src="../assets/img/brand/logo-horizontal-white.png" width="184" height="38" alt=""><span class="veil__rule"></span></div>
<div class="progress" aria-hidden="true"><span></span></div>
<header class="top" id="top">
  <a class="top__brand" href="#cover" aria-label="Archipixels, back to the start">
    <img src="../assets/img/brand/logo-horizontal-white.png" width="184" height="38" alt="Archipixels, design that works">
  </a>
  <nav class="top__nav" aria-label="Sections">
    <a href="#works">Works</a>
    <a href="#studio">Studio</a>
    <a href="#team">Team</a>
    <a href="#contact">Contact</a>
  </nav>
  <div class="top__tools">
    <a class="top__site" href="../index.html" aria-label="Back to site"><span aria-hidden="true">&larr;</span><span class="top__site-label">Back to site</span></a>
    <span class="top__social">
      <a class="top__ig" href="{e(SITE['instagram'])}" target="_blank" rel="noopener" aria-label="Archipixels on Instagram">{ICON_IG}</a>
      <a class="top__ig top__ig--more" href="{e(SITE['linkedin'])}" target="_blank" rel="noopener" aria-label="Archipixels on LinkedIn">{ICON_LI}</a>
      <a class="top__ig top__ig--more" href="{e(SITE['facebook'])}" target="_blank" rel="noopener" aria-label="Archipixels on Facebook">{ICON_FB}</a>
    </span>
    <button class="top__index" type="button" aria-expanded="false" aria-controls="index">
      <span class="top__index-label">Index</span><i aria-hidden="true"></i>
    </button>
  </div>
</header>
"""


def index_overlay():
    rows = []
    for n, p in enumerate(PROJECTS, 1):
        rows.append(
            f'<li style="--i:{n}"><a href="#{e(p["slug"])}"><span class="ix__no">{n:02d}</span>'
            f'<span class="ix__name">{e(p["name"])}</span><span class="ix__kind">{e(p["kind"])}</span>'
            f'<i style="background:{PF["projects"][p["slug"]]["bg"]}" aria-hidden="true"></i></a></li>'
        )
    return f"""<div class="ix" id="index" role="dialog" aria-modal="true" aria-label="Project index" hidden>
  <button class="ix__close" type="button">Close</button>
  <div class="ix__inner">
    <p class="eyebrow">Selected works</p>
    <ol class="ix__list">{''.join(rows)}</ol>
    <ul class="ix__more">
      <li><a href="#studio">Studio</a></li><li><a href="#team">Team</a></li><li><a href="#contact">Contact</a></li><li><a href="../assets/downloads/Archipixels-Portfolio.pdf" download>Download portfolio</a></li>
    </ul>
  </div>
</div>
<div class="counter" aria-hidden="true"><span class="counter__no">01</span><span class="counter__of">/ {len(PROJECTS):02d}</span><span class="counter__name"></span></div>
"""


# ---------------------------------------------------------------- opening sections

def cover():
    slides = []
    for i, s in enumerate(PF["cover_slides"]):
        if "file" in s:
            f = fixed("cover") if s["file"] == "cover.jpg" else None
            file, w, h = f["file"], f["w"], f["h"]
        else:
            im = PF["projects"][s["project"]]["images"][s["i"]]
            file, w, h = im["file"], im["w"], im["h"]
        slides.append(
            f'<div class="swiper-slide" data-label="{e(s["label"])}">{img(file, w, h, s["label"] + ", an Archipixels project", lazy=i > 0)}</div>'
        )
    return f"""<section class="cover" id="cover" aria-label="Archipixels, selected works">
  <div class="swiper cover__swiper"><div class="swiper-wrapper">{''.join(slides)}</div></div>
  <div class="cover__veil" aria-hidden="true"></div>
  <div class="cover__text">
    <h1 class="cover__title">Archipixels</h1>
    <hr class="cover__rule">
    <p class="cover__sub">Selected works</p>
    <p class="cover__kinds">Architecture · Interiors · Experiences</p>
  </div>
  <p class="cover__now"><span>Now showing</span><b class="cover__now-name"></b></p>
  <a class="cover__cue" href="#story" aria-label="Scroll to the introduction"><span></span></a>
</section>
"""


def story():
    im = fixed("intro")
    return f"""<section class="band band--burg story" id="story">
  <div class="wrap split">
    <div class="split__media">{frame(im['file'], im['w'], im['h'], 'A layered, colourful Archipixels interior with hanging lamps and patterned floors')}</div>
    <div class="split__text">
      <p class="eyebrow" data-reveal>Our approach</p>
      <h2 class="display" data-split>Spaces with stories of their own.</h2>
      <hr class="rule">
      <p class="lead" data-reveal>We believe every space has a story waiting to be told. At Archipixels, design begins with curiosity. A curiosity about people, places, cultures and the little things that often go unnoticed.</p>
      <p data-reveal>Spaces that are layered, expressive, sometimes unexpected, but always thoughtful in their details.</p>
      <p data-reveal>We create artful, expressive spaces, each with its own identity. Every project begins with a different story, and we never repeat a design.</p>
      <p data-reveal>We don't believe every space should look a certain way. We believe it should feel a certain way and make you feel something, too.</p>
      <p class="signoff" data-reveal>Archipixels. Design that works.</p>
    </div>
  </div>
</section>
"""


def founders():
    im = fixed("founders")
    return f"""<section class="band band--burg founders" id="founders">
  <div class="wrap split split--flip">
    <div class="split__media">{frame(im['file'], im['w'], im['h'], 'Shivika and Abhinav, the founders of Archipixels, seated on a velvet sofa')}</div>
    <div class="split__text">
      <p class="eyebrow" data-reveal>The founders</p>
      <h2 class="display" data-split>Two minds. A thousand ideas.</h2>
      <hr class="rule">
      <p class="lead" data-reveal>We're <strong>Shivika</strong> and <strong>Abhinav</strong>, partners in life, work and a shared curiosity for everything around us. Our love for design, travel, art and the unexpected has shaped the journey of Archipixels. We find inspiration in the places we visit, the people we meet and the smallest details that often go unnoticed.</p>
      <p data-reveal>We started Archipixels in {SITE['founded']}. Since then, that curiosity has grown into bold spaces and unexpected ideas. Our journey began in Dubai, where we gained international experience before founding Archipixels in India.</p>
      <p data-reveal>Now, we're ready to take that energy worldwide. We're looking for collaborators who share our curiosity and clients with extraordinary ambitions.</p>
      <p class="signoff" data-reveal>Have something wild in mind? Let's make it happen together.</p>
    </div>
  </div>
</section>
"""


def works_intro():
    tiles = []
    for n, p in enumerate(PROJECTS, 1):
        d = PF["projects"][p["slug"]]
        pic = d["images"][0]
        tiles.append(
            f'<li class="wall__tile" style="--c:{d["bg"]}"><a href="#{e(p["slug"])}">'
            f'<span class="wall__img">{img(pic["file"], pic["w"], pic["h"], p["name"] + ", an Archipixels project")}</span>'
            f'<span class="wall__meta"><b>{n:02d}</b><span>{e(p["name"])}</span></span></a></li>'
        )
    return f"""<section class="band band--wall" id="works">
  <div class="wrap">
    <header class="wall__head">
      <p class="eyebrow" data-reveal>Selected works</p>
      <h2 class="display" data-split>Our projects.</h2>
      <p class="lead" data-reveal>Homes, hotels, restaurants, offices, salons and a township. Scroll on to walk through them in order, or pick one below.</p>
    </header>
    <ul class="wall">{''.join(tiles)}</ul>
  </div>
</section>
"""


# ---------------------------------------------------------------- projects

def bg(x):
    # a palette entry may carry a photo of the material as its third item
    return f"background-image:url(../assets/img/{x[2]})" if len(x) > 2 else ""


def swatches(p, d):
    cols = d.get("swatches") or [c[1] for c in p["palette"]]
    if not p["palette"]:
        return ""
    items = "".join(
        f'<li><span class="dot" style="--c:{c};{bg(x)}"></span><span class="swatch__name">{e(x[0])}</span></li>'
        for c, x in zip(cols, p["palette"])
    )
    return f'<ul class="swatches" aria-label="Colour palette">{items}</ul>'


def project(n, p, prev_bg):
    d = PF["projects"][p["slug"]]
    bg = d["bg"]
    ink = ink_for(bg)
    imgs = d["images"]
    total = len(imgs)
    layout = d.get("layout") or {1: "single", 2: "duo", 3: "trio", 4: "quad"}[total]
    shots = []
    for i, im in enumerate(imgs):
        alt = f'{p["name"]}, photograph {i + 1} of {total}'
        title = p["name"] + (f': {im["caption"]}' if im.get("caption") else "")
        shots.append(
            frame(im["file"], im["w"], im["h"], alt, True, p["slug"], title, im.get("caption", ""))
        )
    tag = " · ".join(x for x in (p["kind"], p["place"]) if x)
    by = f'<p class="panel__by">{e(p["by"])}</p>' if p.get("by") else ""
    place = ""
    details = " · ".join(e(x) for x in p["details"])
    language = " | ".join(e(x) for x in p["language"])
    return f"""<section class="project project--{layout}" id="{e(p['slug'])}" data-no="{n:02d}" data-name="{e(p['name'])}" style="--bg:{bg};--prev:{prev_bg};--ink:{ink}">
  <div class="project__inner">
    <div class="project__media">{''.join(shots)}</div>
    <article class="panel">
      <p class="panel__no">No. {n:02d} <span>{e(tag)}</span></p>
      <h2 class="panel__title">{e(p['name'])}</h2>
      {by}
      <p class="panel__tagline">{e(p['tagline'])}</p>
      {swatches(p, d)}
      <h3>The design language</h3>
      <p>{language}</p>
      {f"<h3>Signature details</h3><p>{details}</p>" if details else ""}
    </article>
  </div>
</section>
"""


# ---------------------------------------------------------------- closing sections

def studio():
    a, b, c = fixed("studio1"), fixed("studio2"), fixed("studio3")
    return f"""<section class="band band--burg studio" id="studio">
  <div class="wrap">
    <div class="split split--wide">
      <div class="split__text">
        <p class="eyebrow" data-reveal>The studio</p>
        <h2 class="display" data-split>Our studio</h2>
        <hr class="rule">
        <p class="lead" data-reveal>Our studio is an expression of who we are: artful, maximalist and unafraid to experiment. It reflects the freedom we find in design, the joy of creating beyond convention and our belief that thoughtful maximalism can be as welcoming as it is memorable.</p>
      </div>
    </div>
    <div class="studio__grid">
      <div class="studio__a">{frame(a['file'], a['w'], a['h'], 'The Archipixels studio: a lounge with a green glass pendant, coral sofa and patterned rugs', True, 'studio', 'Our studio')}</div>
      <div class="studio__b">{frame(b['file'], b['w'], b['h'], 'A studio corner with a red curtain, shelves of curios and a pair of crystal lamps', True, 'studio', 'Our studio')}</div>
      <div class="studio__c">{frame(c['file'], c['w'], c['h'], 'A chandelier with red shades against a gilded ceiling', True, 'studio', 'Our studio')}</div>
    </div>
  </div>
</section>
"""


def team():
    im = fixed("team")
    return f"""<section class="band band--burg team" id="team">
  <div class="wrap">
    <div class="team__media">{frame(im['file'], im['w'], im['h'], 'The Archipixels team gathered on sofas around a coffee table in the studio lounge', True, 'team', 'Our team')}</div>
    <div class="team__text">
      <p class="eyebrow" data-reveal>The team</p>
      <h2 class="display" data-split>Our team</h2>
      <hr class="rule">
      <p class="lead" data-reveal>At Archipixels, we believe that when people are valued, supported and given love, they create their best work. We are more than a team; we are the Archipixels family, growing together, celebrating every milestone and standing by one another through every challenge.</p>
      <p class="signoff" data-reveal>Because the best ideas rarely happen in isolation.</p>
    </div>
  </div>
</section>
"""


def contact():
    v = fixed("villa")
    wa = "https://wa.me/{}?text={}".format(SITE["whatsapp_number"], urllib.parse.quote(SITE["whatsapp_message_general"]))
    maps = SITE["maps_url"]
    return f"""<section class="band band--brown contact" id="contact">
  <div class="wrap">
    <div class="contact__head">
      <p class="eyebrow" data-reveal>Get in touch</p>
      <h2 class="display display--xl" data-split>Contact</h2>
    </div>
    <dl class="contact__list">
        <div><dt>E-mail</dt><dd><a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></dd></div>
        <div><dt>Phone</dt><dd><a href="tel:{e(SITE['phone_tel'])}">{e(SITE['phone_display'])}</a> <span>{e(SITE['phone_note'])}</span></dd></div>
        <div><dt>Address</dt><dd><a href="{e(maps)}" target="_blank" rel="noopener">{e(SITE['address'])}</a></dd></div>
        <div><dt>Social</dt><dd class="social-reveal"><a href="{e(SITE['instagram'])}" target="_blank" rel="noopener">{e(SITE['instagram_handle'])}</a>
        <div class="social-row"><a href="{e(SITE['instagram'])}" target="_blank" rel="noopener" aria-label="Archipixels on Instagram">{ICON_IG}</a><a href="{e(SITE['linkedin'])}" target="_blank" rel="noopener" aria-label="Archipixels on LinkedIn">{ICON_LI}</a><a href="{e(SITE['facebook'])}" target="_blank" rel="noopener" aria-label="Archipixels on Facebook">{ICON_FB}</a></div></dd></div>
      </dl>
    <div class="contact__split">
      <div class="contact__art">{img(v['file'], v['w'], v['h'], 'Pen drawing of a three-storey villa facade by Archipixels')}</div>
      <form class="enquiry" action="#" method="post" novalidate>
        <p class="enquiry__title">Tell us about your space</p>
        <label><span>Name</span><input type="text" name="name" autocomplete="name" required></label>
        <label><span>E-mail</span><input type="email" name="email" autocomplete="email" required></label>
        <label><span>Your project</span><textarea name="message" rows="4" required></textarea></label>
        <div class="enquiry__row">
          <button class="btn" type="submit">Send enquiry</button>
          <a class="btn btn--line" href="{e(wa)}" target="_blank" rel="noopener">Message on WhatsApp</a>
          <a class="btn btn--line" href="../assets/downloads/Archipixels-Portfolio.pdf" download>Download portfolio</a>
        </div>
        <p class="enquiry__note" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>
"""


def closing():
    im = fixed("closing")
    return f"""<section class="closing" id="closing">
  <div class="closing__bg">{img(im['file'], im['w'], im['h'], '')}</div>
  <div class="closing__body">
    <p class="closing__line" data-closing>{e(SITE['closing_line'])}</p>
    <img class="closing__logo" src="../assets/brand-originals/logo-stacked-light.png" width="320" height="197" alt="Archipixels, design that works" loading="lazy">
  </div>
</section>
"""


def footer():
    return f"""<footer class="foot">
  <p>© {datetime.date.today().year} Archipixels. Architecture, interiors and experiences. <a href="{e(SITE['maps_url'])}" target="_blank" rel="noopener">{e(SITE['address'])}</a>.</p>
  <p><a href="{e(SITE['instagram'])}" target="_blank" rel="noopener">Instagram</a> · <a href="{e(SITE['linkedin'])}" target="_blank" rel="noopener">LinkedIn</a> · <a href="{e(SITE['facebook'])}" target="_blank" rel="noopener">Facebook</a> · <a href="../assets/downloads/Archipixels-Portfolio.pdf" download>Download portfolio</a> · <a href="#cover">Back to top</a></p>
</footer>
"""


# ---------------------------------------------------------------- page

def main():
    parts = [head(), '<body class="page-portfolio">\n', header(), index_overlay(), "<main>\n"]
    parts += [cover(), story(), founders(), works_intro()]
    prev = "#591524"
    for n, p in enumerate(PROJECTS, 1):
        parts.append(project(n, p, prev))
        prev = PF["projects"][p["slug"]]["bg"]
    parts += [studio(), team(), contact(), closing()]
    parts += ["</main>\n", footer()]
    page = "".join(parts)
    scripts = """
<script src="../assets/vendor/gsap.min.js"></script>
<script src="../assets/vendor/ScrollTrigger.min.js"></script>
<script src="../assets/vendor/swiper-bundle.min.js"></script>
<script src="../assets/vendor/glightbox.min.js"></script>
<script src="js/portfolio.js"></script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page + scripts)
    print("wrote", os.path.relpath(OUT, ROOT), len(page) // 1024, "KB")


if __name__ == "__main__":
    main()
