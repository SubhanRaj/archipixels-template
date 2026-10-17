/* Direction B, Gallery Noir: cinematic motion.
   Creative-effect hero with progress line, huge headline reveals, pinned horizontal
   scroll of featured works, clip-path image reveals, cursor-follow preview on the
   works index, parallax. */
(function () {
  'use strict';
  var AP = window.AP, $ = AP.$, $$ = AP.$$;
  var hasGsap = !!(window.gsap && window.ScrollTrigger);

  /* hero slideshow with autoplay progress line */
  var hero = $('.hero--b');
  if (hero && window.Swiper) {
    var bar = $('.hero__progress i', hero);
    var hs = new Swiper($('.hero-swiper', hero), {
      effect: 'creative', speed: 1300, rewind: true, grabCursor: true, keyboard: { enabled: true },
      creativeEffect: { prev: { shadow: true, translate: ['-25%', 0, -1] }, next: { translate: ['100%', 0, 0] } },
      autoplay: AP.reduce ? false : { delay: 5500, disableOnInteraction: false },
      navigation: { prevEl: '.hero-prev', nextEl: '.hero-next' },
      on: { autoplayTimeLeft: function (s, time, progress) { if (bar) bar.style.transform = 'scaleX(' + (1 - progress) + ')'; } }
    });
    AP.now(hs, hero); AP.fraction(hs, hero);
  }

  /* index list: cursor-follow preview (fine pointers only) */
  var rows = $$('.index-row');
  if (rows.length && AP.fine && hasGsap && !AP.reduce) {
    var pv = document.createElement('div'); pv.className = 'index-preview'; pv.setAttribute('aria-hidden', 'true');
    pv.innerHTML = '<img alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACwAAAAAAQABAAA=">'; document.body.appendChild(pv);
    var pimg = pv.firstChild;
    var qx = gsap.quickTo(pv, 'x', { duration: .5, ease: 'power3' }), qy = gsap.quickTo(pv, 'y', { duration: .5, ease: 'power3' });
    var list = $('.index-list');
    list.addEventListener('pointermove', function (e) { qx(e.clientX + 36); qy(e.clientY - 150); });
    rows.forEach(function (r) {
      r.addEventListener('pointerenter', function () {
        pimg.src = r.getAttribute('data-img');
        gsap.to(pv, { opacity: 1, scale: 1, rotation: 0, duration: .45, ease: 'power3.out', overwrite: 'auto' });
      });
      r.addEventListener('pointerleave', function () { gsap.to(pv, { opacity: 0, scale: .9, duration: .3, overwrite: 'auto' }); });
    });
    gsap.set(pv, { scale: .9 });
  }

  /* featured works: pinned horizontal scroll on desktop, native swipe elsewhere */
  var hs2 = $('.hscroll');
  if (hs2 && hasGsap && !AP.reduce) {
    var track = $('.hscroll__track', hs2);
    ScrollTrigger.matchMedia({
      '(min-width: 900px)': function () {
        hs2.classList.add('is-pinned');
        var dist = function () { return Math.max(0, track.scrollWidth - window.innerWidth); };
        var tw = gsap.to(track, {
          x: function () { return -dist(); }, ease: 'none',
          scrollTrigger: { trigger: hs2, start: 'top top', end: function () { return '+=' + dist(); }, pin: true, scrub: .8, anticipatePin: 1, invalidateOnRefresh: true }
        });
        /* images drift against the scroll for depth */
        $$('.hcard__media img', track).forEach(function (im) {
          gsap.fromTo(im, { xPercent: -6, scale: 1.18 }, { xPercent: 6, ease: 'none', scrollTrigger: { trigger: im.parentNode, containerAnimation: tw, start: 'left right', end: 'right left', scrub: true } });
        });
        return function () { hs2.classList.remove('is-pinned'); };
      }
    });
  }

  if (AP.reduce || !hasGsap) return;

  AP.splitReveal({ dur: 1.5, stagger: .08, ease: 'expo.out' });
  AP.reveals({ y: 50, dur: 1.2, ease: 'expo.out' });
  AP.parallax();

  /* clip-path image reveals on project pages and grids */
  $$('.reveal-img').forEach(function (f) {
    var im = $('img', f);
    gsap.set(f, { clipPath: 'inset(0 0 100% 0)' }); gsap.set(im, { scale: 1.35 });
    ScrollTrigger.create({ trigger: f, start: 'top 88%', once: true, onEnter: function () {
      gsap.to(f, { clipPath: 'inset(0 0 0% 0)', duration: 1.5, ease: 'expo.inOut' });
      gsap.to(im, { scale: 1, duration: 2, ease: 'expo.out' });
    } });
  });

  /* hero: the stage opens from the centre, the headline drifts left on scroll */
  if (hero) {
    gsap.from('.hero__stage', { clipPath: 'inset(0 22% 0 22%)', duration: 1.8, ease: 'expo.out', delay: .3 });
    gsap.to('.hero--b .hero__title', { xPercent: -6, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('.hero--b .hero-swiper img', { yPercent: 8, ease: 'none', scrollTrigger: { trigger: '.hero__stage', start: 'top bottom', end: 'bottom top', scrub: true } });
  }

  /* project pages: the background darkens slightly while scrolling */
  var side = $('.phero--b');
  if (side) {
    gsap.fromTo(document.body, { backgroundColor: '#0D0D0C' }, { backgroundColor: '#14120F', ease: 'none', scrollTrigger: { trigger: side, start: 'top top', end: 'bottom bottom', scrub: true } });
  }
})();
