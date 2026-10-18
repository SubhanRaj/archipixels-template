/* Direction D, Velvet Portfolio: motion for the portfolio components.
   theme-a.js loads first and handles the hero, headings, reveals and parallax.
   This file adds the photo wipes, the panel and swatch entrance, and the closing line.
   Content is only hidden here, right before it animates. */
(function () {
  'use strict';
  var AP = window.AP, $ = AP.$, $$ = AP.$$;
  AP.run(function () {
    if (AP.reduce || !(window.gsap && window.ScrollTrigger)) return;

    /* photos wipe open, settle, then drift while scrolling */
    $$('.d-frame').forEach(function (fr) {
      var inner = $('.d-frame__in', fr), pic = $('img', fr);
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
        scrollTrigger: { trigger: fr, start: 'top bottom', end: 'bottom top', scrub: .6 }
      });
    });

    /* panels: text first, then the swatches pop in */
    $$('.d-panel').forEach(function (panel) {
      var kids = $$(':scope > *:not(.d-swatches)', panel);
      var dots = $$('.d-dot', panel);
      var names = $$('.d-swatches li span:last-child', panel);
      gsap.set(kids, { y: 24, opacity: 0 });
      gsap.set(dots, { scale: 0, rotate: -25 });
      gsap.set(names, { opacity: 0 });
      ScrollTrigger.create({
        trigger: panel, start: 'top 85%', once: true,
        onEnter: function () {
          var tl = gsap.timeline();
          tl.to(kids, { y: 0, opacity: 1, duration: .9, ease: 'power3.out', stagger: .08 }, 0)
            .to(dots, { scale: 1, rotate: 0, duration: .9, ease: 'back.out(1.8)', stagger: .09 }, .35)
            .to(names, { opacity: 1, duration: .6, stagger: .09 }, .6);
        }
      });
    });

    /* team cards rise one after another when the row comes into view */
    $$('.team-swiper').forEach(function (row) {
      var cards = $$('.member', row);
      if (!cards.length) return;
      gsap.set(cards, { y: 44, opacity: 0 });
      ScrollTrigger.create({
        trigger: row, start: 'top 90%', once: true,
        onEnter: function () { gsap.to(cards, { y: 0, opacity: 1, duration: 1, ease: 'power3.out', stagger: .1 }); }
      });
    });

    /* the closing line is written out from left to right */
    var line = $('[data-closing]');
    if (line) {
      gsap.set(line, { clipPath: 'inset(-10% 100% -10% 0%)' });
      ScrollTrigger.create({
        trigger: line, start: 'top 80%', once: true,
        onEnter: function () { gsap.to(line, { clipPath: 'inset(-10% 0% -10% 0%)', duration: 3, ease: 'power2.inOut' }); }
      });
    }
  });

  /* The portfolio is a separate page with its own look, so a link to it is a normal page load. The screen fades to the
     portfolio's colour first, and the portfolio's own opening (the veil in portfolio.css) starts from that same colour. */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || a.target === '_blank' || a.hasAttribute('download')) return;
    if (AP.reduce) return;
    var url;
    try { url = new URL(a.href, window.location.href); } catch (err) { return; }
    if (url.origin !== window.location.origin || !/\/portfolio(\/index\.html)?\/?$/.test(url.pathname)) return;
    e.preventDefault();
    var veil = document.createElement('div');
    veil.className = 'leave-veil';
    document.body.appendChild(veil);
    window.setTimeout(function () { window.location.href = a.href; }, 340);
  });
  /* A page restored by the back button must not stay covered. */
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) $$('.leave-veil').forEach(function (v) { v.remove(); });
  });
})();
