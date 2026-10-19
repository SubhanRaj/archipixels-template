#!/usr/bin/env python3
"""Builds the Archipixels brand guidelines: brand/brand-guidelines.html, then brand/Archipixels-Brand-Guidelines.pdf.

The PDF is landscape at 1440 x 810 px, the same shape as the studio's portfolio. Colours, fonts and rules come from
assets/css/theme-a.css, theme-d.css and portfolio/css/portfolio.css, and the project colours from data/portfolio.json.
Fonts load from Google Fonts while Chrome renders, so run this with a network connection.

    python3 tools/build_brand_guide.py            # HTML and PDF
    python3 tools/build_brand_guide.py --html     # HTML only
"""
import json
import os
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'brand'
HTML = OUT / 'brand-guidelines.html'
PDF = OUT / 'Archipixels-Brand-Guidelines.pdf'

CORE = [
    ('Night Velvet', '#14090C', 'The page background of the site. Almost black, with a trace of wine.'),
    ('Wine Band', '#2A0F16', 'Bands and panels that sit on Night Velvet.'),
    ('Antique Gold', '#C9A24B', 'Eyebrows, rules, rings, links and the gold button on the website.'),
    ('Portfolio Gold', '#D8A93A', 'The brighter gold of the one-page portfolio and the swatch rings.'),
    ('Panel Tan', '#C3A17E', 'The panel on every project page. It holds the name, palette and design language.'),
    ('Warm Ivory', '#F3E9DC', 'Headlines and body text on dark pages. Never pure white.'),
]
SUPPORT = [
    ('Surface', '#1E1115'), ('Muted Text', '#BBA99C'), ('Burgundy', '#591524'), ('Deep Burgundy', '#2A0B13'),
    ('Portfolio Brown', '#5C3D28'), ('Closing Blush', '#E1CCBA'), ('Closing Ink', '#5A1220'), ('Panel Ink', '#1B100A'),
]
PHOTOS = [
    ('helios-maximus-1.jpg', 'Helios Maximus'), ('chat-house-dubai-1.jpg', 'Chat House, India Club'),
    ('mio-marito-gelato-1.jpg', 'Mio Marito Gelato'), ('the-deco-grand-1.jpg', 'The Deco Grand'),
    ('pixel-pop-1.jpg', 'Pixel Pop'), ('chihiro-1.jpg', 'Chihiro'), ('mr-singhs-dwelling-1.jpg', "Mr. Singh's Dwelling"),
    ('danzeria-by-danbro-1.jpg', 'Danzeria by Danbro'),
]
FONTS = ('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,600;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,500;1,500'
         '&family=Herr+Von+Muellerhoff&family=Jost:wght@300;400;500&family=Playfair+Display:ital,wght@0,500;0,700;1,500&display=swap')


def rgb(hex_):
    h = hex_.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ink_for(hex_):
    r, g, b = rgb(hex_)
    return '#1B100A' if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else '#F3E9DC'


def photo(name):
    return f'../portfolio/img/{name}' if (ROOT / 'portfolio' / 'img' / name).exists() else None


def page(n, eyebrow, body, cls=''):
    return (f'<section class="pg {cls}"><p class="foot"><span>Archipixels</span><span>Brand guidelines</span><span>@@N@@</span></p>'
            f'<p class="eyebrow">{eyebrow}</p>{body}</section>')


def dot(hex_, size=96):
    return f'<span class="dot" style="--c:{hex_};width:{size}px;height:{size}px"></span>'


def build_pages():
    projects = {p['slug']: p for p in json.load(open(ROOT / 'data/projects.json'))}
    colours = json.load(open(ROOT / 'data/portfolio.json'))['projects']
    pages = []

    # 1 Cover
    pages.append(
        '<section class="pg cover"><img class="cover__logo" src="../assets/img/brand/logo-stacked-white.png" alt="Archipixels, design that works">'
        '<p class="cover__title">Brand guidelines</p><p class="script">Spaces with stories of their own.</p>'
        '<p class="cover__meta">Logo · Colour · Type · Photography · Voice<br>Version 1.0 · October 2026</p></section>')

    # 2 Brand
    pages.append(page(2, 'The brand', '''
<div class="two"><div>
<h1 class="display">Spaces with stories of their own.</h1>
<p class="lead">Archipixels is an architecture and interior design studio in Gomti Nagar, Lucknow, founded in 2018 by Shivika and Abhinav.
The work is layered, expressive and sometimes unexpected, and always careful in its details. Every project begins with a different story, and no design is repeated.</p>
</div><div class="facts">
<dl><dt>Descriptor</dt><dd>Architecture · Interiors · Experiences</dd>
<dt>Sign-off</dt><dd>Design that works.</dd>
<dt>Closing line</dt><dd class="script small">Let's create something the world hasn't seen yet!</dd>
<dt>Services</dt><dd>Architecture, interior design, space planning and turnkey projects.</dd>
<dt>Clients</dt><dd>Homes, hotels, restaurants, offices, salons and townships. The studio works for every kind of client.</dd></dl>
</div></div>'''))

    # Moodboard
    pages.append(page(0, 'The look', """
<div class="mb"><img class="mb__img" src="img/moodboard-velvet-portfolio.jpg" alt="Moodboard: Velvet Portfolio">
<div><h2 class="h2">Velvet Portfolio.</h2>
<p class="lead small">The site is a gallery to walk through. Night Velvet carries the page, gold draws the lines, a tan panel holds each project's story and the colour of every project fills its own section.</p>
<ul class="list"><li>Colour per project, so each work keeps its own atmosphere.</li><li>Tan panels, one for every project, always the same.</li><li>Gold rings around the swatches, and gold hairlines for rules and frames.</li><li>Large Bodoni headlines, quiet Jost text, and a script signature for the closing line.</li></ul></div></div>"""))

    # 3 Logo
    mis = [('Do not stretch', 'transform:scaleX(1.55)'), ('Do not recolour', 'filter:hue-rotate(150deg) saturate(4)'),
           ('Do not rotate', 'transform:rotate(-11deg)'), ('Do not place on busy photos', '')]
    mis_html = ''.join(
        f'<figure class="mis"><div class="mis__box{" mis__box--photo" if not st else ""}"><img src="../assets/img/brand/logo-horizontal-white.png" style="{st}" alt=""></div>'
        f'<figcaption>{t}</figcaption></figure>' for t, st in mis)
    pages.append(page(3, 'Logo', f'''
<h2 class="h2">The mark, the wordmark and the line.</h2>
<div class="logos">
<figure><div class="tile dark"><img src="../assets/img/brand/logo-horizontal-white.png" alt=""></div><figcaption>Horizontal. The default, used in the website header.</figcaption></figure>
<figure><div class="tile dark"><img src="../assets/img/brand/logo-stacked-white.png" alt=""></div><figcaption>Stacked. For the footer, the closing page and square spaces.</figcaption></figure>
<figure><div class="tile dark"><img src="../assets/img/brand/logo-mark-white.png" alt=""></div><figcaption>Mark. For icons and very small sizes.</figcaption></figure>
<figure><div class="tile light"><img src="../assets/brand-originals/logo-horizontal-light.png" alt=""></div><figcaption>Dark ink version for ivory and tan backgrounds.</figcaption></figure>
</div>
<div class="rules"><p><b>Clear space.</b> Keep a margin around the logo equal to the height of the letter A in the wordmark.</p>
<p><b>Minimum size.</b> The horizontal logo is never narrower than 120 px on screen or 30 mm in print. The mark alone is never narrower than 28 px.</p>
<p><b>Backgrounds.</b> The white logo goes on Night Velvet, Wine Band, burgundy and project colours. The dark logo goes on Warm Ivory and Panel Tan.</p></div>'''))
    pages.append(page(4, 'Logo, what to avoid', f'''
<h2 class="h2">Keep the logo as it was drawn.</h2>
<div class="mis-row">{mis_html}</div>
<p class="lead small">Use the supplied files only. Do not redraw the mark, change the spacing between the mark, the wordmark and the line, or set the wordmark in another typeface.</p>'''))

    # 5 Core colours
    cards = ''.join(f'<div class="col">{dot(h)}<h3>{n}</h3><p class="mono">{h} · RGB {", ".join(map(str, rgb(h)))}</p><p>{u}</p></div>' for n, h, u in CORE)
    sup = ''.join(f'<div class="chip"><span style="background:{h}"></span><b>{n}</b><i>{h}</i></div>' for n, h in SUPPORT)
    pages.append(page(5, 'Colour', f'''
<h2 class="h2">Gold on velvet.</h2>
<div class="cols">{cards}</div>
<p class="eyebrow sub">Supporting colours</p><div class="chips">{sup}</div>'''))

    # 6 Project colours
    tiles = []
    for slug, data in colours.items():
        name = projects.get(slug, {}).get('name', slug)
        tiles.append(f'<div class="pc" style="background:{data["bg"]};color:{ink_for(data["bg"])}"><b>{escape(name)}</b><i>{data["bg"]}</i></div>')
    pages.append(page(6, 'Colour, projects', f'''
<h2 class="h2">Each project takes its own colour.</h2>
<p class="lead small">On the website and in the portfolio, a project section uses the page colour taken from that project's palette. The text colour is chosen for contrast. The tan panel stays the same on every project, so the studio's frame holds the colours together.</p>
<div class="pcs">{"".join(tiles)}</div>'''))

    # 7 Typography families
    pages.append(page(7, 'Typography', '''
<h2 class="h2">Three voices.</h2>
<div class="fam">
<div><p class="tag">Display · Bodoni Moda</p><p class="spec bodoni">Aa Bb Cc</p><p class="bodoni sm">Headlines and project names. Regular weight, large, with room around it. Italic carries the emphasis and takes the gold.</p><p class="mono">Regular 400 · Italic 400 · SemiBold 600</p></div>
<div><p class="tag">Body · Jost</p><p class="spec jost">Aa Bb Cc</p><p class="jost sm">Paragraphs, navigation, buttons and labels. Light 300 for text on dark, Regular 400 and Medium 500 for labels in capitals.</p><p class="mono">Light 300 · Regular 400 · Medium 500</p></div>
<div><p class="tag">Script · Herr Von Muellerhoff</p><p class="spec script">Aa Bb Cc</p><p class="sm jost">The signature face. It sets the closing line and nothing else. It always appears large, in gold or ink, and never for body text.</p><p class="mono">One weight · closing line only</p></div>
</div>
<p class="eyebrow sub">One-page portfolio</p>
<div class="fam two-fam"><div><p class="spec playfair">PROJECT NAME</p><p class="mono">Playfair Display 700, capitals, on the tan panel</p></div><div><p class="spec corm">A colourful slice of India</p><p class="mono">Cormorant Garamond Italic 500, taglines and swatch names</p></div></div>'''))

    # 8 Type hierarchy
    pages.append(page(8, 'Typography, in use', '''
<div class="hier">
<div class="row"><span class="meta">Eyebrow<br>Jost 500 · 0.74 rem · capitals · 0.3 em spacing · gold, with a 38 px rule</span><p class="eyebrow inline"><i class="rl"></i>The studio</p></div>
<div class="row"><span class="meta">Display<br>Bodoni Moda 400 · 2.4 to 5.6 rem · line height 1.02</span><p class="display">Artful, maximalist and unafraid to experiment.</p></div>
<div class="row"><span class="meta">Lead<br>Jost 300 · 1.35 to 1.6 rem · line height 1.55</span><p class="lead">Our studio is an expression of who we are. It reflects the freedom we find in design.</p></div>
<div class="row"><span class="meta">Body<br>Jost 300 · 1.06 rem · line height 1.65</span><p class="body">We create artful, expressive spaces, each with its own identity. Every project begins with a different story, and we never repeat a design.</p></div>
<div class="row"><span class="meta">Button<br>Jost 500 · 0.76 rem · capitals · 0.22 em spacing</span><p><span class="btn">Chat on WhatsApp</span> <span class="btn line">View selected works</span></p></div>
</div>'''))

    # 9 Components
    pages.append(page(9, 'Components', f'''
<h2 class="h2">The details that repeat.</h2>
<div class="comp">
<div><p class="tag">Swatch</p><div class="sw">{dot("#C8283C", 70)}{dot("#00343D", 70)}{dot("#B48731", 70)}{dot("#3C0D36", 70)}</div><p class="sm jost">A round dot with a gold ring and the colour's name beneath. Four to six swatches per project.</p></div>
<div><p class="tag">Tan panel</p><div class="mini-panel"><p class="mp-no">NO. 01 · THEMED RENTAL HOME</p><p class="mp-title">HELIOS MAXIMUS</p><p class="mp-tag">A maximalist escape</p></div><p class="sm jost">Panel Tan, a thin inner outline, a soft shadow. Name, tagline, palette, design language and signature details.</p></div>
<div><p class="tag">Buttons and links</p><p><span class="btn">Chat on WhatsApp</span></p><p><span class="btn line">View selected works</span></p><p><span class="lnk">View project &rarr;</span></p><p class="sm jost">One gold button for the main action. An outlined button and an underlined arrow link for the rest.</p></div>
<div><p class="tag">Gold rules</p><p class="rule-demo"></p><p class="sm jost">Hairlines in Antique Gold draw out under headings and frame photographs. Corners stay square and shadows stay warm.</p></div>
</div>'''))

    # 10 Photography
    shots = [(photo(f), c) for f, c in PHOTOS if photo(f)][:8]
    grid = ''.join(f'<figure><img src="{src}" alt=""><figcaption>{escape(c)}</figcaption></figure>' for src, c in shots)
    pages.append(page(10, 'Photography', f'''
<div class="two ph"><div><h2 class="h2">The photograph carries the page.</h2>
<ul class="list"><li>Photographs are the largest element on any screen and sit close against the colour.</li>
<li>Show the whole room or the one detail that makes it. Crop tightly and keep the colour true.</li>
<li>Frame a photograph with a thin gold line and a warm shadow, never a white border.</li>
<li>Use the studio's own project photographs. Keep people in shot natural and unposed.</li>
<li>Photos are saved as JPEG at quality 90, and no photo is shown larger than its file.</li></ul></div>
<div class="grid8">{grid}</div></div>'''))

    # Website
    pages.append(page(0, 'In use', """
<h2 class="h2">On the website.</h2>
<div class="shots"><figure><img src="img/site-home.jpg" alt=""><figcaption>Home. The slideshow, the headline and the gold button.</figcaption></figure>
<figure><img src="img/site-portfolio.jpg" alt=""><figcaption>Portfolio cover. A photograph under the veil, the name in capitals.</figcaption></figure>
<figure><img src="img/site-panel.jpg" alt=""><figcaption>Project section. Its own colour, photographs and the tan panel.</figcaption></figure></div>"""))

    # 11 Layout and motion
    pages.append(page(11, 'Layout and motion', '''
<h2 class="h2">A gallery to walk through.</h2>
<div class="three big">
<div><p class="tag">Layout</p><p class="sm jost">Wide pages with generous space. Content sits in a column up to 1280 px, with side gutters of 18 to 48 px. A section has 72 to 144 px of space above and below on the home page and half of that on inner pages. Work walls are four across on desktop, three on tablet and two on phones.</p></div>
<div><p class="tag">Motion</p><p class="sm jost">Soft and slow. Photographs fade up from the page colour, headings reveal word by word, and cards rise in one after another. A page fades softly into the colour of the next. Motion never hides content from someone who cannot see it, and it stops for visitors who ask their device to reduce motion.</p></div>
<div><p class="tag">Accessibility</p><p class="sm jost">Text keeps strong contrast against its background. Every photograph has a description, links are underlined or ringed on focus, and the site works from the keyboard and on a phone.</p></div>
</div>'''))

    # 12 Voice
    pages.append(page(12, 'Voice', '''
<div class="two"><div><h2 class="h2">Short, specific, warm.</h2>
<p class="lead small">The studio talks about stories, curiosity and details. Sentences are short and name the thing. The tone invites a conversation with someone who has an ambitious space in mind.</p>
<p class="tag">Words we use</p><p class="chips-words">story · curiosity · layered · expressive · artful · details · identity · collaborators · extraordinary ambitions</p></div>
<div class="dd"><div class="do"><p class="tag">Write</p><p class="q">"Every project begins with a different story, and we never repeat a design."</p><p class="q">"Have something wild in mind? Let's make it happen together."</p></div>
<div class="dont"><p class="tag">Avoid</p><p class="q">"We deliver world-class, cutting-edge design solutions."</p><p class="q">"Contact page"</p><p class="sm jost">Link labels say "Contact us". Headings do not state a project count or a place name for earlier work.</p></div></div></div>'''))

    # 13 Details
    pages.append(page(13, 'Details', '''
<div class="two"><div><h2 class="h2">Find us.</h2>
<dl class="det"><dt>Studio</dt><dd>1/146, Gomti Nagar, Lucknow, India</dd><dt>E-mail</dt><dd>hello@archipixels.com</dd><dt>Phone and WhatsApp</dt><dd>+91 99996 60533</dd>
<dt>Instagram</dt><dd>@archipixels</dd><dt>LinkedIn</dt><dd>linkedin.com/company/archipixels</dd><dt>Facebook</dt><dd>facebook.com/archipixels</dd><dt>Website</dt><dd>archipixels.com</dd></dl></div>
<div><p class="tag">Files</p><ul class="list"><li>Logo files: white versions in <span class="mono">assets/img/brand/</span>, dark ink and original versions in <span class="mono">assets/brand-originals/</span>.</li>
<li>Website tokens: <span class="mono">--bg --surface --band --accent --text --muted</span> and the display and body fonts, set in <span class="mono">theme-a.css</span>.</li>
<li>Portfolio colours: <span class="mono">portfolio.css</span> and <span class="mono">data/portfolio.json</span>.</li>
<li>Fonts: Bodoni Moda, Jost, Herr Von Muellerhoff, Playfair Display and Cormorant Garamond, all free on Google Fonts.</li></ul>
<p class="script small closing">Let's create something the world hasn't seen yet!</p></div></div>'''))
    return pages


CSS = '''
@page { size: 1440px 810px; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #14090C; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Jost", sans-serif; font-weight: 300; color: #F3E9DC; font-size: 17px; line-height: 1.6; }
:root { --gold: #C9A24B; --gold2: #D8A93A; --tan: #C3A17E; --ivory: #F3E9DC; --muted: #BBA99C; --line: rgba(201,162,75,.32); }
.pg { width: 1440px; height: 810px; position: relative; overflow: hidden; page-break-after: always; break-after: page; padding: 70px 76px 64px; background: #14090C; }
.pg:nth-child(even) { background: #190C10; }
.foot { position: absolute; left: 76px; right: 76px; bottom: 26px; margin: 0; display: flex; justify-content: space-between; font-size: 11px; letter-spacing: .26em; text-transform: uppercase; color: var(--muted); }
.eyebrow { font-weight: 500; font-size: 12px; letter-spacing: .3em; text-transform: uppercase; color: var(--gold); margin: 0 0 22px; display: flex; align-items: center; gap: 14px; }
.eyebrow::before { content: ""; width: 38px; height: 1px; background: var(--gold); }
.eyebrow.sub { margin-top: 26px; } .eyebrow.inline { margin: 0; }
.display { font: 400 58px/1.04 "Bodoni Moda", serif; margin: 0 0 26px; letter-spacing: -.01em; }
.h2 { font: 400 44px/1.08 "Bodoni Moda", serif; margin: 0 0 24px; }
.lead { font-size: 22px; line-height: 1.55; margin: 0 0 18px; } .lead.small { font-size: 18px; max-width: 900px; }
.sm { font-size: 17px; line-height: 1.65; } .jost { font-family: "Jost", sans-serif; } .bodoni { font-family: "Bodoni Moda", serif; }
.mono { font: 400 13px/1.5 "Jost", sans-serif; letter-spacing: .06em; color: var(--muted); }
.script { font: 400 52px/1.1 "Herr Von Muellerhoff", cursive; color: var(--gold); } .script.small { font-size: 34px; }
.tag { font-weight: 500; font-size: 12px; letter-spacing: .24em; text-transform: uppercase; color: var(--gold); margin: 0 0 12px; }
.two { display: grid; grid-template-columns: 1.1fr 1fr; gap: 64px; align-items: start; } .three { display: grid; grid-template-columns: repeat(3, 1fr); gap: 56px; margin-top: 30px; } .three.big .sm { font-size: 19px; line-height: 1.75; }
.facts dl, .det { margin: 0; } dt { font-weight: 500; font-size: 12px; letter-spacing: .24em; text-transform: uppercase; color: var(--gold); margin-top: 18px; } dd { margin: 4px 0 0; font-size: 18px; }
.cover { background: radial-gradient(ellipse at 50% 38%, #2A0F16, #14090C 70%); display: grid; place-content: center; justify-items: center; text-align: center; gap: 8px; }
.cover__logo { width: 360px; margin-bottom: 18px; } .cover__title { font: 400 64px/1.1 "Bodoni Moda", serif; margin: 6px 0 0; }
.cover__meta { font-size: 13px; letter-spacing: .26em; text-transform: uppercase; color: var(--muted); margin-top: 28px; line-height: 2; }
.logos { display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px; margin: 6px 0 22px; } figure { margin: 0; } figcaption { font-size: 13px; color: var(--muted); margin-top: 10px; line-height: 1.5; }
.tile { height: 215px; display: grid; place-items: center; border: 1px solid var(--line); } .tile img { max-width: 78%; max-height: 110px; } .tile.dark { background: #14090C; } .tile.light { background: #F3E9DC; }
.rules { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; font-size: 17px; line-height: 1.7; margin-top: 28px; } .rules p { margin: 0; } .rules b { color: var(--gold); font-weight: 500; }
.mis-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin: 18px 0 30px; }
.mis__box { height: 215px; display: grid; place-items: center; background: #14090C; border: 1px solid var(--line); overflow: hidden; } .mis__box img { width: 62%; }
.mis__box--photo { background: url(../portfolio/img/helios-maximus-1.jpg) center/cover; } .mis figcaption::before { content: "\\2715\\00a0"; color: #C8283C; }
.cols { display: grid; grid-template-columns: repeat(6, 1fr); gap: 24px; margin-top: 14px; } .col h3 { font: 400 24px/1.2 "Bodoni Moda", serif; margin: 14px 0 6px; } .col p { margin: 0 0 8px; font-size: 15.5px; line-height: 1.5; color: var(--ivory); } .col .mono { color: var(--muted); }
.dot { display: block; border-radius: 50%; background: radial-gradient(circle at 32% 28%, rgba(255,255,255,.3), transparent 52%) center/cover, var(--c); box-shadow: 0 0 0 3px var(--gold2), 0 0 0 4px rgba(27,16,10,.35), 0 12px 24px -10px rgba(0,0,0,.6); margin: 4px 0 8px 4px; }
.chips { display: grid; grid-template-columns: repeat(8, 1fr); gap: 14px; } .chip span { display: block; height: 72px; border: 1px solid var(--line); } .chip b { display: block; font-weight: 400; font-size: 13px; margin-top: 8px; } .chip i { font-style: normal; font-size: 12px; color: var(--muted); }
.pcs { display: grid; grid-template-columns: repeat(8, 1fr); gap: 10px; margin-top: 18px; } .pc { height: 108px; padding: 10px 11px; display: flex; flex-direction: column; justify-content: flex-end; font-size: 12.5px; line-height: 1.25; } .pc b { font-weight: 500; } .pc i { font-style: normal; opacity: .8; font-size: 11px; }
.fam { display: grid; grid-template-columns: repeat(3, 1fr); gap: 44px; } .fam.two-fam { grid-template-columns: 1fr 1fr; margin-top: 4px; }
.spec { font-size: 84px; white-space: nowrap; line-height: 1.05; margin: 0 0 10px; } .spec.bodoni { font-family: "Bodoni Moda", serif; } .spec.jost { font-weight: 300; } .spec.script { font: 400 100px/1 "Herr Von Muellerhoff", cursive; color: var(--gold); } .spec.playfair { font: 700 52px/1.1 "Playfair Display", serif; color: var(--tan); } .spec.corm { font: italic 500 52px/1.1 "Cormorant Garamond", serif; color: var(--tan); }
.hier .row { display: grid; grid-template-columns: 330px 1fr; gap: 36px; align-items: center; padding: 26px 0; border-top: 1px solid var(--line); } .hier .row:first-child { border-top: 0; } .hier .row p { margin: 0; } .hier .display { font-size: 58px; margin: 0; } .hier .lead { margin: 0; font-size: 21px; } .hier .body { font-size: 17px; max-width: 760px; }
.meta { font-size: 12px; line-height: 1.5; color: var(--muted); letter-spacing: .04em; } .rl { display: block; width: 38px; height: 1px; background: var(--gold); }
.btn { display: inline-block; font: 500 12px/1 "Jost", sans-serif; letter-spacing: .22em; text-transform: uppercase; padding: 16px 24px; background: #CFAA55; color: #1A0C0F; margin: 4px 8px 4px 0; } .btn.line { background: transparent; color: var(--ivory); border: 1px solid rgba(243,233,220,.5); }
.lnk { font: 500 12px/1 "Jost", sans-serif; letter-spacing: .22em; text-transform: uppercase; color: var(--ivory); border-bottom: 1px solid var(--gold); padding-bottom: 6px; }
.comp { display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; margin-top: 34px; } .sw { display: flex; gap: 16px; margin: 6px 0 16px; }
.mini-panel { background: var(--tan); color: #1B100A; text-align: center; padding: 42px 20px; outline: 1px solid rgba(27,16,10,.28); outline-offset: -9px; box-shadow: 0 30px 50px -26px rgba(0,0,0,.8); margin-bottom: 14px; }
.mp-no { font: 500 10px/1.5 "Jost", sans-serif; letter-spacing: .26em; margin: 0 0 8px; } .mp-title { font: 700 26px/1.1 "Playfair Display", serif; margin: 0 0 6px; } .mp-tag { font: italic 500 19px/1.3 "Cormorant Garamond", serif; margin: 0; }
.rule-demo { height: 1px; background: linear-gradient(90deg, var(--gold), transparent); margin: 70px 0 70px; }
.ph { grid-template-columns: .8fr 1.3fr; } .list { margin: 0; padding-left: 20px; font-size: 18px; line-height: 1.7; } .list li { margin-bottom: 10px; }
.grid8 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; } .grid8 img { width: 100%; height: 250px; object-fit: cover; display: block; box-shadow: 0 0 0 1px rgba(201,162,75,.28), 0 20px 40px -20px rgba(0,0,0,.8); } .grid8 figcaption { font-size: 12px; letter-spacing: .08em; }
.mb { display: grid; grid-template-columns: 470px 1fr; gap: 64px; align-items: center; margin-top: 0; } .mb__img { height: 612px; width: auto; display: block; box-shadow: 0 0 0 1px rgba(201,162,75,.3), 0 30px 60px -24px rgba(0,0,0,.9); }
.shots { display: grid; grid-template-columns: repeat(3, 1fr); gap: 26px; margin-top: 8px; } .shots img { width: 100%; display: block; box-shadow: 0 0 0 1px rgba(201,162,75,.3), 0 26px 50px -22px rgba(0,0,0,.9); } .shots figcaption { font-size: 15px; margin-top: 14px; }
.dd { display: grid; gap: 22px; } .do, .dont { padding: 24px 28px; border: 1px solid var(--line); } .do { border-left: 3px solid var(--gold); } .dont { border-left: 3px solid #C8283C; } .q { font: italic 400 24px/1.4 "Bodoni Moda", serif; margin: 0 0 12px; }
.chips-words { font: 400 28px/1.55 "Bodoni Moda", serif; color: var(--ivory); } .det dd { font-size: 20px; } .closing { margin-top: 30px; }
'''


def main():
    pages = build_pages()
    OUT.mkdir(exist_ok=True)
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Archipixels brand guidelines</title>'
            f'<link rel="stylesheet" href="{FONTS}"><style>{CSS}</style></head><body>'
            f'{"".join(p.replace("@@N@@", f"{i:02d}") for i, p in enumerate(pages, 1))}</body></html>')
    HTML.write_text(html, encoding='utf-8')
    print(f'wrote {HTML.relative_to(ROOT)} ({len(pages)} pages)')
    if '--html' in sys.argv:
        return
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    if not chrome:
        sys.exit('Chrome is needed to write the PDF')
    subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-sandbox', '--no-pdf-header-footer', '--virtual-time-budget=20000',
                    f'--print-to-pdf={PDF}', f'file://{HTML}'], check=True, stderr=subprocess.DEVNULL)
    print(f'wrote {PDF.relative_to(ROOT)} ({PDF.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
