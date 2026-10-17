/* Archipixels portfolio, one-page version.
   JavaScript hides content only right before it animates in.
   With scripts off, or with reduced motion on, everything stays visible. */
(function () {
  'use strict';

  var doc = document;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGsap = !!(window.gsap && window.ScrollTrigger);

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }

  if (hasGsap) { gsap.registerPlugin(ScrollTrigger); }

  /* header state and reading progress */
  var top = $('.top');
  var bar = $('.progress span');
  function onScroll() {
    var y = window.scrollY || 0;
    var max = doc.documentElement.scrollHeight - window.innerHeight;
    top.classList.toggle('is-solid', y > 60);
    bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* index overlay */
  var ix = $('#index');
  var ixBtn = $('.top__index');
  var ixTimer;
  function openIndex() {
    clearTimeout(ixTimer);
    ix.hidden = false;
    void ix.offsetWidth;
    ix.classList.add('is-open');
    doc.body.classList.add('has-index');
    ixBtn.setAttribute('aria-expanded', 'true');
    $('.ix__list a', ix).focus({ preventScroll: true });
  }
  function closeIndex() {
    ix.classList.remove('is-open');
    doc.body.classList.remove('has-index');
    ixBtn.setAttribute('aria-expanded', 'false');
    ixTimer = setTimeout(function () { ix.hidden = true; }, 850);
  }
  ixBtn.addEventListener('click', function () {
    if (ix.classList.contains('is-open')) { closeIndex(); } else { openIndex(); }
  });
  ix.addEventListener('click', function (ev) {
    if (ev.target.closest('a')) { closeIndex(); }
  });
  $('.ix__close', ix).addEventListener('click', function () { closeIndex(); ixBtn.focus(); });
  doc.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && ix.classList.contains('is-open')) { closeIndex(); ixBtn.focus(); }
  });

  /* cover slideshow */
  var coverEl = $('.cover__swiper');
  var nowName = $('.cover__now-name');
  if (window.Swiper && coverEl) {
    var setNow = function (sw) {
      var slide = sw.slides[sw.activeIndex];
      if (slide && nowName) { nowName.textContent = slide.getAttribute('data-label') || ''; }
    };
    new Swiper(coverEl, {
      effect: 'fade',
      fadeEffect: { crossFade: true },
      speed: 1500,
      rewind: true,
      autoplay: reduce ? false : { delay: 6500, disableOnInteraction: false },
      on: { init: setNow, slideChange: setNow }
    });
  }

  /* lightbox */
  if (window.GLightbox) {
    GLightbox({ selector: '.glightbox', loop: true, touchNavigation: true });
  }

  /* enquiry form: shows a thank-you message and sends nothing yet */
  var form = $('.enquiry');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var note = $('.enquiry__note', form);
      if (!form.checkValidity()) {
        note.textContent = 'Please fill in your name, e-mail and a few words about the project.';
        return;
      }
      note.textContent = 'Thank you. We will be in touch soon.';
      form.reset();
    });
  }

  if (!hasGsap || reduce) { return; }

  /* ---- motion ---- */

  /* cover entrance and exit */
  var intro = gsap.timeline({ defaults: { ease: 'power4.out' } });
  intro
    .from('.cover__title', { yPercent: 18, opacity: 0, duration: 1.6 }, 0.2)
    .from('.cover__rule', { scaleX: 0, duration: 1.4 }, 0.7)
    .from('.cover__sub, .cover__kinds', { y: 16, opacity: 0, duration: 1, stagger: 0.15 }, 1)
    .from('.cover__now', { opacity: 0, duration: 1 }, 1.4);
  gsap.to('.cover__text', {
    yPercent: -28, opacity: 0, ease: 'none',
    scrollTrigger: { trigger: '.cover', start: 'top top', end: 'bottom 20%', scrub: true }
  });

  /* headings: words rise out of a mask */
  $$('[data-split]').forEach(function (h) {
    var text = h.textContent.trim();
    h.setAttribute('aria-label', text);
    h.innerHTML = text.split(/\s+/).map(function (w) {
      return '<span class="w" aria-hidden="true"><span>' + w + '</span></span>';
    }).join(' ');
    var words = $$('.w > span', h);
    gsap.set(words, { yPercent: 118 });
    ScrollTrigger.create({
      trigger: h, start: 'top 90%', once: true,
      onEnter: function () { gsap.to(words, { yPercent: 0, duration: 1.2, ease: 'power4.out', stagger: 0.07 }); }
    });
  });

  /* text blocks fade up */
  $$('[data-reveal]').forEach(function (el) {
    gsap.set(el, { y: 28, opacity: 0 });
    ScrollTrigger.create({
      trigger: el, start: 'top 92%', once: true,
      onEnter: function () { gsap.to(el, { y: 0, opacity: 1, duration: 1.1, ease: 'power3.out' }); }
    });
  });

  /* gold rules draw in */
  $$('.rule').forEach(function (r) {
    gsap.set(r, { scaleX: 0 });
    ScrollTrigger.create({
      trigger: r, start: 'top 92%', once: true,
      onEnter: function () { gsap.to(r, { scaleX: 1, duration: 1.4, ease: 'power3.inOut' }); }
    });
  });

  /* photos: wipe open, settle, then drift slowly while scrolling */
  $$('.frame').forEach(function (fr) {
    var inner = $('.frame__in', fr);
    var pic = $('img', fr);
    gsap.set(fr, { clipPath: 'inset(0% 0% 100% 0%)' });
    gsap.set(pic, { scale: 1.22 });
    ScrollTrigger.create({
      trigger: fr, start: 'top 92%', once: true,
      onEnter: function () {
        gsap.to(fr, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'expo.out' });
        gsap.to(pic, { scale: 1, duration: 2, ease: 'expo.out' });
      }
    });
    gsap.fromTo(inner, { yPercent: -5 }, {
      yPercent: 5, ease: 'none',
      scrollTrigger: { trigger: fr, start: 'top bottom', end: 'bottom top', scrub: 0.6 }
    });
  });

  /* project panels: text lines, then the swatches pop in */
  $$('.panel').forEach(function (panel) {
    var kids = $$(':scope > *:not(.swatches)', panel);
    var dots = $$('.dot', panel);
    gsap.set(kids, { y: 24, opacity: 0 });
    gsap.set(dots, { scale: 0, rotate: -25 });
    gsap.set($$('.swatch__name', panel), { opacity: 0 });
    ScrollTrigger.create({
      trigger: panel, start: 'top 82%', once: true,
      onEnter: function () {
        var tl = gsap.timeline();
        tl.to(kids, { y: 0, opacity: 1, duration: 0.9, ease: 'power3.out', stagger: 0.08 }, 0)
          .to(dots, { scale: 1, rotate: 0, duration: 0.9, ease: 'back.out(1.8)', stagger: 0.09 }, 0.35)
          .to($$('.swatch__name', panel), { opacity: 1, duration: 0.6, stagger: 0.09 }, 0.6);
      }
    });
  });

  /* works wall */
  var tiles = $$('.wall__tile');
  gsap.set(tiles, { y: 44, opacity: 0 });
  ScrollTrigger.batch(tiles, {
    start: 'top 94%', once: true,
    onEnter: function (batch) { gsap.to(batch, { y: 0, opacity: 1, duration: 0.9, ease: 'power3.out', stagger: 0.06 }); }
  });

  /* project counter */
  var counter = $('.counter');
  var counterNo = $('.counter__no', counter);
  var counterName = $('.counter__name', counter);
  var projects = $$('.project');
  projects.forEach(function (p) {
    ScrollTrigger.create({
      trigger: p, start: 'top 55%', end: 'bottom 55%',
      onToggle: function (self) {
        if (self.isActive) {
          counterNo.textContent = p.getAttribute('data-no');
          counterName.textContent = p.getAttribute('data-name');
        }
      }
    });
  });
  ScrollTrigger.create({
    trigger: projects[0], endTrigger: projects[projects.length - 1],
    start: 'top 60%', end: 'bottom 40%',
    onToggle: function (self) { counter.classList.toggle('is-on', self.isActive); }
  });

  /* contact rows */
  var rows = $$('.contact__list > div');
  gsap.set(rows, { y: 22, opacity: 0 });
  ScrollTrigger.create({
    trigger: '.contact__list', start: 'top 88%', once: true,
    onEnter: function () { gsap.to(rows, { y: 0, opacity: 1, duration: 0.9, ease: 'power3.out', stagger: 0.1 }); }
  });

  /* closing line is written out from left to right */
  var line = $('[data-closing]');
  if (line) {
    gsap.set(line, { clipPath: 'inset(-10% 100% -10% 0%)' });
    ScrollTrigger.create({
      trigger: line, start: 'top 80%', once: true,
      onEnter: function () { gsap.to(line, { clipPath: 'inset(-10% 0% -10% 0%)', duration: 3, ease: 'power2.inOut' }); }
    });
  }

  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
