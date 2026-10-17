/* Direction C, Midnight Bazaar: playful motion.
   Stacked-card hero deck, coverflow works slider, wobbling stickers, velocity-skewed
   marquee, 3D tilt cards, springy headline pops. */
(function () {
  'use strict';
  var AP = window.AP, $ = AP.$, $$ = AP.$$;
  var hasGsap = !!(window.gsap && window.ScrollTrigger);

  /* hero deck of stacked cards */
  var hero = $('.hero--c');
  if (hero && window.Swiper) {
    var hs = new Swiper($('.hero-swiper', hero), {
      effect: 'cards', grabCursor: true, rewind: true, speed: 650, keyboard: { enabled: true },
      cardsEffect: { perSlideOffset: 9, perSlideRotate: 3, rotate: true, slideShadows: false },
      autoplay: AP.reduce ? false : { delay: 4200, disableOnInteraction: true, pauseOnMouseEnter: true },
      navigation: { prevEl: '.hero-prev', nextEl: '.hero-next' }
    });
    AP.now(hs, hero);
  }

  /* works slider: coverflow */
  var fs = $('.featured--c .feature-swiper');
  if (fs && window.Swiper) {
    new Swiper(fs, {
      effect: 'coverflow', centeredSlides: true, slidesPerView: 'auto', grabCursor: true, initialSlide: 2, speed: 700, keyboard: { enabled: true },
      coverflowEffect: { rotate: 16, stretch: 0, depth: 180, modifier: 1, slideShadows: false },
      navigation: { prevEl: '.feature-prev', nextEl: '.feature-next' }
    });
  }

  if (AP.reduce || !hasGsap) return;

  AP.splitReveal({ dur: .9, stagger: .06, ease: 'back.out(1.8)', rot: 5 });
  AP.reveals({ y: 50, rot: -2, dur: .8, ease: 'back.out(1.4)' });
  AP.tilt(10, 20);

  /* stickers: pop in, then keep wobbling */
  $$('.sticker').forEach(function (s, i) {
    var r = parseFloat(getComputedStyle(s).getPropertyValue('--r')) || (i % 2 ? 2 : -3);
    gsap.fromTo(s, { scale: 0, rotation: r * 4 }, { scale: 1, rotation: r, duration: .7, delay: .2 + i * .08, ease: 'back.out(3)', clearProps: 'transform,scale' });
  });
  $$('.sticker-row').forEach(function (row) {
    $$('.sticker', row).forEach(function (s, i) {
      gsap.to(s, { rotation: '+=' + (i % 2 ? 4 : -4), y: i % 2 ? -4 : 4, duration: 1.4 + i * .25, ease: 'sine.inOut', yoyo: true, repeat: -1, delay: 1 });
    });
  });
  $$('.feature-card__tag').forEach(function (s, i) {
    gsap.to(s, { rotation: i % 2 ? 5 : -5, duration: 1.2 + (i % 3) * .3, ease: 'sine.inOut', yoyo: true, repeat: -1 });
  });

  /* marquee skews with scroll velocity */
  var skews = $$('.marquee__skew');
  if (skews.length) {
    var setSkew = gsap.quickTo(skews, 'skewX', { duration: .4, ease: 'power3' });
    var last = 0;
    ScrollTrigger.create({ onUpdate: function (self) {
      var v = gsap.utils.clamp(-18, 18, self.getVelocity() / -90);
      if (Math.abs(v - last) > .1) setSkew(v); last = v;
    } });
    gsap.ticker.add(function () { if (Math.abs(last) > .1) { last *= .92; setSkew(last); } });
  }

  /* hero entrance */
  if (hero) {
    gsap.from('.hero--c .hero-swiper', { scale: .6, rotation: -14, opacity: 0, duration: 1.1, ease: 'back.out(1.6)', delay: .3 });
    gsap.from('.hero--c .actions .btn', { y: 30, opacity: 0, stagger: .12, duration: .7, ease: 'back.out(2)', delay: .9 });
  }

  /* parallax on frames + a little float on tiles */
  AP.parallax();
  $$('.home-tile').forEach(function (t, i) {
    gsap.to(t, { y: (i % 2 ? 1 : -1) * 22, rotation: (i - 1) * 1.5, ease: 'none', scrollTrigger: { trigger: t, start: 'top bottom', end: 'bottom top', scrub: true } });
  });
  var pf = $('.phero__frame');
  if (pf) gsap.from(pf, { rotation: 6, scale: .85, duration: 1.1, ease: 'back.out(1.5)' });
})();
