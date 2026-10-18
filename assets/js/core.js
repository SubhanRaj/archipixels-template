/* ==========================================================================
   Archipixels core behaviour (theme-agnostic) + small helpers used by theme-*.js.
   Plain browser JS, no build step. Blade: include once in the layout, before the
   theme script. Content is only hidden by JS, so the page stays readable without it.
   ========================================================================== */
(function () {
  'use strict';
  var d = document;
  var AP = window.AP = {
    osReduce: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    reduce: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    fine: window.matchMedia('(hover: hover) and (pointer: fine)').matches,
    $: function (s, r) { return (r || d).querySelector(s); },
    $$: function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
  };
  var hasGsap = !!(window.gsap && window.ScrollTrigger);
  if (hasGsap) gsap.registerPlugin(ScrollTrigger);

  /* ---- page lifecycle ----
     Everything that binds to the page runs in start(). A Livewire wire:navigate swaps the body, so core.js
     (loaded once) calls stop(), start() and every AP.run() function again on livewire:navigated. On a plain
     page this runs once, as before. Theme scripts wrap their setup in AP.run(). */
  var life = null, swipers = [], hooks = [];
  AP.swiper = function (el, opts) { var s = new Swiper(el, opts); swipers.push(s); return s; };
  AP.run = function (fn) { hooks.push(fn); fn(); };
  AP.stop = function () {
    if (life) life.abort();
    swipers.forEach(function (s) { if (s && !s.destroyed) s.destroy(true, true); });
    swipers = [];
    if (AP.lightbox) { AP.lightbox.destroy(); AP.lightbox = null; }
    if (hasGsap) ScrollTrigger.getAll().forEach(function (t) { t.kill(); });
  };

  /* ---- works filter motion ----
     The tiles fade out when a chip is pressed and drift back in, one after another, with the new set. Shared by the static
     filter below and by the Livewire filter on the Laravel Works page. JS hides the tiles right before it shows them. */
  function wallTiles() { return AP.$$('.works [data-cats]').filter(function (t) { return !t.hidden; }); }
  function wallCount() { return AP.$('.works [data-count], .works .filters__count'); }
  AP.wallOut = function (done) {
    var t = wallTiles();
    if (AP.reduce || !AP.filterFx || !hasGsap || !t.length) { if (done) done(); return; }
    gsap.to(t, { opacity: 0, duration: .5, stagger: { amount: .2 }, ease: 'power1.inOut', overwrite: true, onComplete: done });
  };
  AP.wallIn = function (wait) {
    var t = wallTiles(), n = wallCount();
    if (AP.reduce || !AP.filterFx || !hasGsap) return;
    if (t.length) gsap.fromTo(t, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 1.2, delay: wait || 0, stagger: { amount: Math.min(.7, t.length * .06) }, ease: 'power2.out', overwrite: true, clearProps: 'opacity,transform' });
    if (n) gsap.fromTo(n, { opacity: 0 }, { opacity: 1, duration: .7, delay: wait || 0, ease: 'power1.out', clearProps: 'opacity,transform' });
  };
  AP.wallBack = function () { if (hasGsap) gsap.to(wallTiles(), { opacity: 1, y: 0, duration: .25, overwrite: true, clearProps: 'opacity,transform' }); };
  AP.chipPop = function (chip) { if (!AP.reduce && AP.filterFx && hasGsap && chip) gsap.fromTo(chip, { scale: .96 }, { scale: 1, duration: .6, ease: 'power2.out', clearProps: 'transform' }); };

  /* The Livewire filter (Laravel): a chip press starts the fade at once, and the new tiles rise when the page has been updated. */
  var filtering = false, fadedAt = 0; /* fadedAt: when the old tiles have finished fading, so the new ones never cut in */
  d.addEventListener('click', function (e) {
    var chip = e.target.closest('.works .filters .chip, .filters .chip');
    if (!chip || chip.hasAttribute('data-filter') || chip.classList.contains('is-active') || !AP.$('.works')) return;
    filtering = true; fadedAt = Date.now() + 700; AP.wallOut(); AP.chipPop(chip);
  });
  function hookLivewire() {
    if (hookLivewire.done || !window.Livewire || !Livewire.hook) return;
    hookLivewire.done = true;
    Livewire.hook('morphed', function () { if (filtering) { filtering = false; AP.wallIn(Math.max(0, (fadedAt - Date.now()) / 1000)); } });
    Livewire.hook('commit', function (c) { c.fail(function () { if (filtering) { filtering = false; AP.wallBack(); } }); });
  }
  hookLivewire();
  d.addEventListener('livewire:init', hookLivewire);

  /* ---- project page transition ----
     A link to a project (or an earlier work) from the Works wall, a related tile or the "Next project" band fades the page
     softly into the page colour before it opens. The project page then plays its own entrance, so nothing runs twice.
     It works the same on a Livewire page swap and on a plain page load, and it is skipped for reduced motion. */
  var PROJECT = /(^|\/)(works|projects|earlier)\/[^\/?#]+$/;
  function isProject(url) { return url.origin === window.location.origin && PROJECT.test(url.pathname); }
  function fadeOut(done) {
    var el = d.createElement('div');
    el.className = 'page-fade'; el.setAttribute('aria-hidden', 'true');
    el.style.background = window.getComputedStyle(d.body).backgroundColor;
    d.body.appendChild(el);
    gsap.fromTo(el, { opacity: 0 }, { opacity: 1, duration: .38, ease: 'power1.inOut', onComplete: done });
    return el;
  }
  function fadeTo(url, viaLivewire) {
    AP.leaving = true;
    var el = fadeOut(function () {
      if (viaLivewire) { AP.passing = url.href; Livewire.navigate(url.href); } else window.location.href = url.href;
      /* A swap replaces the body and takes the fade with it. If the page is still here, the move failed, so clear the fade. */
      window.setTimeout(function () { if (el.isConnected) { AP.leaving = false; gsap.to(el, { opacity: 0, duration: .3, onComplete: function () { el.remove(); } }); } }, 6000);
    });
  }
  function fadeOn() { return !AP.reduce && AP.pageFade && hasGsap && !AP.leaving && !d.body.classList.contains('page-home'); } /* the home pages keep their own motion */
  /* A plain link: the page loads after the fade. */
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || (a.target && a.target !== '_self') || a.hasAttribute('download')) return;
    if (Array.prototype.some.call(a.attributes, function (at) { return at.name.indexOf('wire:navigate') === 0; })) return;
    var url = new URL(a.href, window.location.href);
    if (!fadeOn() || !isProject(url)) return;
    e.preventDefault(); e.stopPropagation();
    fadeTo(url, false);
  }, true);
  /* A wire:navigate link opens on mouse release, so the fade hooks into the navigation itself. */
  d.addEventListener('livewire:navigate', function (e) {
    var url = e.detail && e.detail.url ? new URL(String(e.detail.url), window.location.href) : null;
    if (!url || e.detail.history || e.defaultPrevented) return;
    if (AP.passing === url.href) { AP.passing = null; return; }
    if (!fadeOn() || !isProject(url)) return;
    e.preventDefault();
    fadeTo(url, true);
  });
  window.addEventListener('pageshow', function (e) { if (e.persisted) { AP.leaving = false; AP.$$('.page-fade').forEach(function (c) { c.remove(); }); } });

  /* The admin's Motion settings reach the page as data attributes on the body (the Laravel layout writes them). A page
     without them, such as the static templates, keeps the defaults. "off" works like the visitor's reduced-motion setting. */
  function readMotion() {
    var b = d.body, mode = b.getAttribute('data-motion') || 'full';
    AP.reduce = AP.osReduce || mode === 'off';
    AP.soft = mode === 'soft';
    AP.heroDelay = parseFloat(b.getAttribute('data-hero-delay')) || 6.5;
    AP.heroFade = parseFloat(b.getAttribute('data-hero-fade')) || 1.6;
    AP.pageFade = b.getAttribute('data-page-fade') !== '0';
    AP.filterFx = b.getAttribute('data-filter-motion') !== '0';
  }
  readMotion();

  function start() {
    AP.leaving = false;
    readMotion();
    life = window.AbortController ? new AbortController() : { signal: undefined, abort: function () {} };
    var sig = life.signal;
    /* ---- header: scrolled state + mobile nav ---- */
    var header = AP.$('[data-header]');
    function onScroll() { if (header) header.classList.toggle('is-scrolled', window.scrollY > 40); }
    window.addEventListener('scroll', onScroll, { passive: true, signal: sig });
    onScroll();

    var toggle = AP.$('.nav-toggle');
    function setNav(open) {
      d.body.classList.toggle('nav-open', open);
      if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open) {
        AP.$$('.has-sub.is-open').forEach(function (li) {
          li.classList.remove('is-open');
          li.querySelector('.sub-toggle').setAttribute('aria-expanded', 'false');
        });
      }
    }
    if (toggle) {
      toggle.addEventListener('click', function () { setNav(!d.body.classList.contains('nav-open')); });
      AP.$$('.site-nav a').forEach(function (a) { a.addEventListener('click', function () { setNav(false); }); });
      AP.$$('.sub-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var li = btn.parentNode;
          var open = !li.classList.contains('is-open');
          li.classList.toggle('is-open', open);
          btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
      });
      d.addEventListener('keydown', function (e) { if (e.key === 'Escape') setNav(false); }, { signal: sig });
      window.addEventListener('resize', function () { if (window.innerWidth > 1100) setNav(false); }, { signal: sig });
    }

    /* ---- works filter (chips + count; reads #hash like works.html#dubai) ---- */
    var chips = AP.$$('.chip[data-filter]');
    if (chips.length) {
      var items = AP.$$('.works [data-cats]');
      var count = AP.$('[data-count]');
      var swap = function (key) {
        var n = 0;
        items.forEach(function (it) {
          var show = key === 'all' || it.getAttribute('data-cats').split(' ').indexOf(key) > -1;
          it.hidden = !show;
          if (show) n++;
        });
        chips.forEach(function (c) {
          var on = c.getAttribute('data-filter') === key;
          c.classList.toggle('is-active', on);
          c.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        if (count) count.textContent = n + (n === 1 ? ' project' : ' projects');
        if (hasGsap) ScrollTrigger.refresh();
        d.dispatchEvent(new CustomEvent('ap:filtered', { detail: { key: key } }));
      };
      var apply = function (key, animate) {
        if (!animate) { swap(key); return; }
        AP.wallOut(function () { swap(key); AP.wallIn(); });
      };

      chips.forEach(function (c) { c.addEventListener('click', function () { if (c.classList.contains('is-active')) return; apply(c.getAttribute('data-filter'), true); AP.chipPop(c); }); });
      var h = (location.hash || '').replace('#', '');
      if (h && chips.some(function (c) { return c.getAttribute('data-filter') === h; })) apply(h);
    }

    /* ---- demo forms: no backend, show the thank-you message ---- */
    AP.$$('[data-demo-form]').forEach(function (f) {
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var ok = f.querySelector('[required]') ? Array.prototype.every.call(f.querySelectorAll('[required]'), function (i) { return i.value.trim(); }) : true;
        var msg = f.querySelector('.form__thanks');
        if (!ok) { f.querySelector('[required]:invalid, [required]').focus(); return; }
        if (msg) msg.hidden = false;
        f.reset();
      });
    });

    /* ---- lightbox + project gallery slider ---- */
    if (window.GLightbox && AP.$('.glightbox')) AP.lightbox = GLightbox({ selector: '.glightbox', touchNavigation: true, loop: true });
    AP.$$('.gallery-swiper').forEach(function (el) {
      AP.swiper(el, { slidesPerView: 'auto', spaceBetween: 16, grabCursor: true, keyboard: { enabled: true }, navigation: { prevEl: '.gallery-prev', nextEl: '.gallery-next' } });
    });

    /* ---- team carousel (cards link to the member pages) ---- */
    AP.$$('.team-swiper').forEach(function (el) {
      AP.swiper(el, { slidesPerView: 'auto', spaceBetween: 24, grabCursor: true, keyboard: { enabled: true }, navigation: { prevEl: '.team-prev', nextEl: '.team-next' } });
    });

    /* ---- map card: the Google map loads on click, so the page sets no Google cookies until then ---- */
    AP.$$('.map-card__stage').forEach(function (stage) {
      var btn = AP.$('.map-card__load', stage);
      if (!btn) return;
      btn.addEventListener('click', function () {
        var f = d.createElement('iframe');
        f.src = stage.getAttribute('data-map-src');
        f.title = 'Map showing the Archipixels studio in Gomti Nagar, Lucknow';
        f.loading = 'lazy'; f.allowFullscreen = true; f.referrerPolicy = 'strict-origin-when-cross-origin';
        stage.appendChild(f);
        stage.classList.add('is-loaded');
        AP.$('.map-card__veil', stage).hidden = true;
      });
    });

  }

  start();

  var booted = d.body;
  d.addEventListener('livewire:navigated', function () {
    if (d.body === booted) return; /* Livewire fires this on the first load too */
    booted = d.body;
    AP.stop(); start();
    hooks.forEach(function (fn) { fn(); });
    if (hasGsap) ScrollTrigger.refresh();
  });

  /* ---- helpers for theme scripts ---- */

  /* wraps each word of [data-split] elements in .word > span */
  AP.split = function (scope) {
    var out = [];
    AP.$$('[data-split]', scope).forEach(function (el) {
      var words = el.textContent.trim().split(/\s+/);
      el.textContent = '';
      var spans = words.map(function (w, i) {
        var wrap = d.createElement('span'); wrap.className = 'word';
        var inner = d.createElement('span'); inner.textContent = w; wrap.appendChild(inner);
        el.appendChild(wrap);
        if (i < words.length - 1) el.appendChild(d.createTextNode(' '));
        return inner;
      });
      out.push({ el: el, spans: spans });
    });
    return out;
  };

  /* "now showing" caption for a hero Swiper */
  AP.now = function (sw, root) {
    var meta = AP.$('.hero__now-meta', root), link = AP.$('.hero__now-title', root);
    if (!meta || !link) return;
    var set = function () {
      var s = sw.slides[sw.activeIndex]; if (!s) return;
      meta.textContent = s.getAttribute('data-meta'); link.textContent = s.getAttribute('data-title'); link.setAttribute('href', s.getAttribute('data-href'));
    };
    set(); sw.on('slideChange', set);
  };

  /* fraction counter "01 / 07" */
  AP.fraction = function (sw, root) {
    var cur = AP.$('[data-current]', root), tot = AP.$('[data-total]', root);
    if (!cur) return;
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var set = function () { cur.textContent = pad(sw.activeIndex + 1); if (tot) tot.textContent = pad(sw.slides.length); };
    set(); sw.on('slideChange', set);
  };

  /* fades up [data-reveal] elements in batches as they enter the viewport */
  AP.reveals = function (o) {
    if (!hasGsap) return;
    o = o || {};
    var els = AP.$$('[data-reveal]');
    if (!els.length) return;
    gsap.set(els, { opacity: 0, y: o.y || 36, rotation: o.rot || 0 });
    ScrollTrigger.batch(els, {
      start: 'top 90%', once: true,
      onEnter: function (b) { gsap.to(b, { opacity: 1, y: 0, rotation: 0, duration: o.dur || .9, stagger: .09, ease: o.ease || 'power3.out', overwrite: true }); }
    });
  };

  /* slides the words of [data-split] headings into view */
  AP.splitReveal = function (o) {
    if (!hasGsap) return;
    o = o || {};
    AP.split().forEach(function (s) {
      gsap.set(s.spans, { yPercent: 115, rotation: o.rot || 0 });
      ScrollTrigger.create({
        trigger: s.el, start: 'top 90%', once: true,
        onEnter: function () { gsap.to(s.spans, { yPercent: 0, rotation: 0, duration: o.dur || 1.1, stagger: o.stagger || .07, ease: o.ease || 'power4.out' }); }
      });
    });
  };

  /* parallax for images inside .parallax frames (the CSS makes the image 118% tall) */
  AP.parallax = function () {
    if (!hasGsap) return;
    AP.$$('.parallax').forEach(function (box) {
      var im = AP.$('img', box); if (!im) return;
      gsap.fromTo(im, { yPercent: 0 }, { yPercent: -15, ease: 'none', scrollTrigger: { trigger: box, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
  };

  /* 3D tilt that follows the pointer on .tilt elements */
  AP.tilt = function (max, lift) {
    if (!hasGsap || !AP.fine) return;
    AP.$$('.tilt').forEach(function (el) {
      el.style.transformStyle = 'preserve-3d';
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
        gsap.to(el, { rotationY: px * max, rotationX: -py * max, z: lift || 0, transformPerspective: 900, duration: .45, ease: 'power2.out', overwrite: 'auto' });
      });
      el.addEventListener('pointerleave', function () { gsap.to(el, { rotationY: 0, rotationX: 0, z: 0, duration: .7, ease: 'power3.out', overwrite: 'auto' }); });
    });
  };

  window.addEventListener('load', function () { if (hasGsap) ScrollTrigger.refresh(); });
})();
