/* Direction A, Velvet Night: theatrical motion.
   Fade slideshow + Ken Burns, word-by-word headlines, gold hairlines that draw,
   parallax, cursor spotlight, creative-effect works slider. */
(function () {
  'use strict';
  var AP = window.AP, $ = AP.$, $$ = AP.$$;
  var hasGsap = !!(window.gsap && window.ScrollTrigger);
  AP.run(function () {

    /* hero slideshow */
    var hero = $('.hero--a');
    if (hero && window.Swiper) {
      var hs = AP.swiper($('.hero-swiper', hero), {
        effect: 'fade', fadeEffect: { crossFade: true }, speed: 1600, rewind: true,
        autoplay: AP.reduce ? false : { delay: 6500, disableOnInteraction: false },
        pagination: { el: '.hero__pagination', clickable: true },
        navigation: { prevEl: '.hero-prev', nextEl: '.hero-next' }, keyboard: { enabled: true }
      });
      AP.now(hs, hero);
      if (AP.fine && !AP.reduce) {
        var spot = $('.hero__spot', hero);
        hero.addEventListener('pointermove', function (e) {
          var r = hero.getBoundingClientRect();
          spot.style.setProperty('--mx', (e.clientX - r.left) + 'px'); spot.style.setProperty('--my', (e.clientY - r.top) + 'px');
        });
      }
    }

    /* featured works: creative-effect slider */
    var fs = $('.featured--a .feature-swiper');
    if (fs && window.Swiper) {
      var fsw = AP.swiper(fs, {
        effect: 'creative', speed: 1000, grabCursor: true, keyboard: { enabled: true },
        creativeEffect: { prev: { shadow: true, translate: ['-24%', 0, -300], opacity: 0 }, next: { translate: ['100%', 0, 0] } },
        navigation: { prevEl: '.feature-prev', nextEl: '.feature-next' }
      });
      AP.fraction(fsw, $('.featured--a'));
    }

    /* section heads get a gold rule that draws in on scroll */
    $$('.section-head').forEach(function (h) {
      if (h.querySelector('.rule')) return;
      var r = document.createElement('span'); r.className = 'rule'; r.setAttribute('aria-hidden', 'true'); h.appendChild(r);
    });

    if (AP.reduce || !hasGsap) return;

    AP.splitReveal({ dur: 1.3, stagger: .09, ease: 'expo.out' });
    AP.reveals({ y: 44, dur: 1.1, ease: 'expo.out' });
    AP.parallax();
    AP.tilt(4, 0);

    $$('.rule').forEach(function (r) {
      gsap.set(r, { scaleX: 0 });
      ScrollTrigger.create({ trigger: r, start: 'top 92%', once: true, onEnter: function () { gsap.to(r, { scaleX: 1, duration: 1.6, ease: 'power3.inOut' }); } });
    });

    /* hero intro: veil lifts, content rises */
    if (hero) {
      gsap.from('.hero__veil', { opacity: 0, duration: 1.6, ease: 'power2.out' });
      gsap.from('.hero__ui', { opacity: 0, y: 20, duration: 1, delay: .9, ease: 'power3.out' });
      gsap.to('.hero__content', { yPercent: -12, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
      gsap.to('.hero-swiper', { yPercent: 8, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
    }

    /* project hero: the title fades as the hero scrolls away */
    var ph = $('.phero--a');
    if (ph) gsap.to($('.phero__content', ph), { yPercent: -10, opacity: .2, ease: 'none', scrollTrigger: { trigger: ph, start: 'center top', end: 'bottom top', scrub: true } });

    /* homes tiles drift against the scroll */
    $$('.home-tile').forEach(function (t, i) {
      gsap.to(t, { y: (i % 2 ? 1 : -1) * 28, ease: 'none', scrollTrigger: { trigger: t, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
  });
})();
