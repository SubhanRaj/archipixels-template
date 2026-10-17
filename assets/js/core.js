/* ==========================================================================
   Archipixels core behaviour (theme-agnostic) + small helpers used by theme-*.js.
   Plain browser JS, no build step. Blade: include once in the layout, before the
   theme script. Content is only hidden by JS, so the page stays readable without it.
   ========================================================================== */
(function () {
  'use strict';
  var d = document;
  var AP = window.AP = {
    reduce: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    fine: window.matchMedia('(hover: hover) and (pointer: fine)').matches,
    $: function (s, r) { return (r || d).querySelector(s); },
    $$: function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
  };
  var hasGsap = !!(window.gsap && window.ScrollTrigger);
  if (hasGsap) gsap.registerPlugin(ScrollTrigger);

  /* ---- header: scrolled state + mobile nav ---- */
  var header = AP.$('[data-header]');
  function onScroll() { if (header) header.classList.toggle('is-scrolled', window.scrollY > 40); }
  window.addEventListener('scroll', onScroll, { passive: true });
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
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') setNav(false); });
    window.addEventListener('resize', function () { if (window.innerWidth > 1100) setNav(false); });
  }

  /* ---- works filter (chips + count; reads #hash like works.html#dubai) ---- */
  var chips = AP.$$('.chip[data-filter]');
  if (chips.length) {
    var items = AP.$$('.works [data-cats]');
    var count = AP.$('[data-count]');
    var apply = function (key) {
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
    chips.forEach(function (c) { c.addEventListener('click', function () { apply(c.getAttribute('data-filter')); }); });
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
    new Swiper(el, { slidesPerView: 'auto', spaceBetween: 16, grabCursor: true, keyboard: { enabled: true }, navigation: { prevEl: '.gallery-prev', nextEl: '.gallery-next' } });
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
