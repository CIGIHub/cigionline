// Swiper-backed gallery init. Loaded as a lazy chunk by gallery.js so Swiper +
// its CSS only download on pages that actually have a gallery.
import Swiper from 'swiper';
import { Navigation, Pagination, A11y, Autoplay } from 'swiper/modules'; // eslint-disable-line import/no-unresolved
import 'swiper/swiper-bundle.css';
import { paginationBullet } from './carousel';

// Author-set carousel controls, read from data-* on the carousel root. Shared by
// every DS carousel (gallery, supporting materials, video). `minLoopSlides`
// guards loop so a centred/fractional peek doesn't leave blank gaps; autoplay is
// disabled under prefers-reduced-motion (accessibility) and pauses on hover.
function carouselOptions(el, count, minLoopSlides) {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const delay = (parseInt(el.dataset.dsAutoplayDelay, 10) || 5) * 1000;
  return {
    loop: el.dataset.dsLoop === '1' && count > minLoopSlides,
    autoplay:
      el.dataset.dsAutoplay === '1' && !reduceMotion
        ? { delay, disableOnInteraction: false, pauseOnMouseEnter: true }
        : false,
    pagination:
      el.dataset.dsPagination !== '0'
        ? { el: el.querySelector('.ds-pagination'), clickable: true, renderBullet: paginationBullet }
        : false,
  };
}

// Wire the autoplay pause/resume toggle (rendered in the shared nav only when
// autoplay is on). Hidden when autoplay isn't actually active (e.g. under
// prefers-reduced-motion), so it never sits inert.
function wirePause(rootEl, swiper, autoplayOn) {
  const btn = rootEl.querySelector('[data-ds-pause]');
  if (!btn) return;
  if (!autoplayOn || !swiper.autoplay) {
    btn.hidden = true;
    return;
  }
  btn.addEventListener('click', () => {
    const paused = btn.getAttribute('aria-pressed') === 'true';
    if (paused) {
      swiper.autoplay.start();
      btn.setAttribute('aria-pressed', 'false');
    } else {
      swiper.autoplay.stop();
      btn.setAttribute('aria-pressed', 'true');
    }
  });
}

export default function run(root = document) {
  root.querySelectorAll('[data-ds-gallery]').forEach((gallery) => {
    if (gallery.dataset.dsInit) return;
    gallery.dataset.dsInit = '1';

    const container = gallery.querySelector('.swiper');
    if (!container) return;
    const count = container.querySelectorAll('.swiper-slide').length;
    // Swiper 11 refuses to loop unless there are ≥ 2× slidesPerView slides, i.e.
    // 6 at the 3-up desktop breakpoint; below that it disables loop itself.
    const opts = carouselOptions(gallery, count, 5);
    // The author's intent, before the slide-count guard. A gallery set to loop but
    // one slide short still gets the free ends — it just doesn't wrap.
    const loopRequested = gallery.dataset.dsLoop === '1';

    const swiper = new Swiper(container, {
      modules: [Navigation, Pagination, A11y, Autoplay],
      // observer/observeParents: re-measure when the carousel (or an ancestor tab
      // panel) goes hidden→visible, so a carousel inside a non-default tab doesn't
      // measure 0 width (audit blocker #3).
      observer: true,
      observeParents: true,
      // Mobile: one slide. Desktop: the active slide centred with exactly one
      // slide visible each side, separated by a 16px gap (no overlap/coverflow).
      slidesPerView: 1,
      centeredSlides: true,
      // Loop OFF: bounds clamp the first/last positions, so slide 1 opens flush
      // LEFT instead of centre screen (BugHerd #128). The cost of that clamp is a
      // dead end — the final snap parks the last slide at the right edge, so it
      // never becomes active.
      // Loop ON: bounds lift, so every slide centres and the last one is reachable
      // (BugHerd #159). Bounds is what pins the ends, so it has to go for the wrap
      // to work. Keyed on the author's toggle, not the guarded loop: a gallery a
      // slide short of Swiper's wrap threshold still gets free ends.
      centeredSlidesBounds: !loopRequested,
      spaceBetween: 16,
      speed: 500,
      loop: opts.loop,
      autoplay: opts.autoplay,
      a11y: { prevSlideMessage: 'Previous slide', nextSlideMessage: 'Next slide' },
      breakpoints: {
        768: { slidesPerView: 3 },
      },
      navigation: {
        prevEl: gallery.querySelector('.ds-gallery__prev'),
        nextEl: gallery.querySelector('.ds-gallery__next'),
      },
      pagination: opts.pagination,
    });

    wirePause(gallery, swiper, Boolean(opts.autoplay));
  });

  // --- Card carousels (3-up, not centred): supporting materials, video -------
  root.querySelectorAll('[data-ds-carousel]').forEach((carousel) => {
    if (carousel.dataset.dsInit) return;
    carousel.dataset.dsInit = '1';

    const container = carousel.querySelector('.swiper');
    if (!container) return;
    const count = container.querySelectorAll('.swiper-slide').length;
    // Peek mode (e.g. video carousel): active + neighbours with partial slides
    // bleeding off both sides (3 full + 2 partial). Looped so EVERY slide —
    // first/last included — reaches the centred position with no blank edge.
    // Swiper 11 only loops a 3.6-wide peek with ~2× slidesPerView slides (≈8);
    // below that it falls back to centred + bounded (ends snap to edge).
    const peek = carousel.hasAttribute('data-ds-carousel-peek');
    const opts = carouselOptions(carousel, count, peek ? 7 : 3);
    // Optional overrides (non-peek): spaceBetween and the desktop slidesPerView,
    // e.g. the Programs Carousel uses a 48px gutter (24 each side of its dividers)
    // and a fractional desktop value for a peek. Defaults keep existing carousels
    // unchanged.
    const space = parseInt(carousel.dataset.dsSpace, 10) || 24;
    const slidesLg = parseFloat(carousel.dataset.dsSlidesLg) || 3;

    const swiper = new Swiper(container, {
      modules: [Navigation, Pagination, A11y, Autoplay],
      // Re-measure on hidden→visible (carousel inside a non-default tab). #3.
      observer: true,
      observeParents: true,
      slidesPerView: peek ? 1.15 : 1,
      spaceBetween: space,
      speed: 350, // animation-guide: 350ms ease-out (timing-fn set via --swiper-wrapper-transition-timing-function in _carousel.scss)
      centeredSlides: peek,
      centeredSlidesBounds: peek && !opts.loop,
      loop: opts.loop,
      autoplay: opts.autoplay,
      a11y: { prevSlideMessage: 'Previous', nextSlideMessage: 'Next' },
      breakpoints: peek
        ? {
            768: { slidesPerView: 2.2 },
            1024: { slidesPerView: 3.6 },
          }
        : {
            768: { slidesPerView: 2 },
            992: { slidesPerView: slidesLg },
          },
      navigation: {
        prevEl: carousel.querySelector('.ds-carousel__prev'),
        nextEl: carousel.querySelector('.ds-carousel__next'),
      },
      pagination: opts.pagination,
    });

    wirePause(carousel, swiper, Boolean(opts.autoplay));
  });

  // --- Mobile-only carousels (Resource Bento): a grid/stack on desktop, a swipe
  // rail at <=768. Swiper is created ONLY while the breakpoint matches (element
  // visible) and destroyed above it — no hidden-init measurement bug, and
  // resizing across 768px is safe (BugHerd #56).
  root.querySelectorAll('[data-ds-carousel-mobile]').forEach((carousel) => {
    if (carousel.dataset.dsInit) return;
    carousel.dataset.dsInit = '1';

    const container = carousel.querySelector('.swiper');
    if (!container) return;
    const mql = window.matchMedia('(max-width: 768px)');
    let swiper = null;

    const sync = () => {
      if (mql.matches && !swiper) {
        const count = container.querySelectorAll('.swiper-slide').length;
        const opts = carouselOptions(carousel, count, 3);
        swiper = new Swiper(container, {
          modules: [Navigation, Pagination, A11y],
          // One full-width card per view — the mobile bento design has no peek
          // of the next slide (Figma 1363-124701).
          slidesPerView: 1,
          spaceBetween: parseInt(carousel.dataset.dsSpace, 10) || 16,
          speed: 350,
          loop: opts.loop,
          a11y: { prevSlideMessage: 'Previous', nextSlideMessage: 'Next' },
          navigation: {
            prevEl: carousel.querySelector('.ds-carousel__prev'),
            nextEl: carousel.querySelector('.ds-carousel__next'),
          },
          pagination: opts.pagination,
          on: {
            // Surface slide changes as a bubbling DOM event so module scripts
            // (e.g. the spotlight theme filter, BugHerd #150) can react without
            // importing Swiper into the main bundle.
            slideChange(s) {
              carousel.dispatchEvent(new window.CustomEvent('ds-carousel-slidechange', {
                bubbles: true,
                detail: { index: s.realIndex ?? s.activeIndex },
              }));
            },
          },
        });
        // Keep the shared nav's pause toggle consistent here too: shown+wired only
        // when autoplay is actually running, hidden otherwise (WCAG 2.2.2 applies
        // to auto-advancing content, so an idle rail must not expose a dead control).
        wirePause(carousel, swiper, Boolean(opts.autoplay));
      } else if (!mql.matches && swiper) {
        swiper.destroy(true, true);
        swiper = null;
      }
    };

    sync();
    mql.addEventListener('change', sync);
  });
}
