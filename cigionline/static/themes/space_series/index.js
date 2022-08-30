import './css/space_series.scss';
import Swiper, { Navigation } from 'swiper';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation]);
let pageType;
if (document.querySelector('.space-series-article')) {
  pageType = 'article';
} else if (document.querySelector('.space-series-article-series')) {
  pageType = 'article series';
}
const breakpoint = pageType === 'article series'
  ? window.matchMedia('(max-width:992px)')
  : window.matchMedia('(max-width:768px)');
const swipers = {};

const enableSwiper = function(articleType) {
  const slidesPerViewLg = articleType === 'article series' ? 8 : 6;
  const slidesPerViewMd = articleType === 'article series' ? 8 : 4;
  const swiperIds = articleType === 'article series' ? ['.swiper-container-series'] : ['.swiper-container-sticky', '.swiper-container-hero'];
  swiperIds.forEach((id) => {
    swipers[id] = new Swiper(id, {
      spaceBetween: 0,
      speed: 800,
      autoHeight: false,
      grabCursor: true,
      effect: 'slide',
      watchSlidesProgress: true,
      watchSlidesVisibility: true,

      navigation: {
        nextEl: `.swiper-button-next-${id.replace('.swiper-container-', '')}`,
        prevEl: `.swiper-button-prev-${id.replace('.swiper-container-', '')}`,
        hiddenClass: 'swiper-button-hidden',
      },

      breakpoints: {
        768: {
          slidesPerView: slidesPerViewMd,
        },
        992: {
          slidesPerView: slidesPerViewLg,
        },
      },
    });
  });
};

const breakpointChecker = function() {
  if (breakpoint.matches === true) {
    for (const swiper in swipers) {
      if (swipers[swiper] !== undefined) swipers[swiper].destroy(true, true);
    }
  } else if (breakpoint.matches === false) {
    enableSwiper(pageType);
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();

if (pageType === 'article') {
  const stickyInTheSeries = document.getElementById('sticky-in-the-series');
  const heroInTheSeries = document.getElementById('hero-in-the-series');
  const hero = document.querySelector('.space-series-article-hero');
  const heroHeight = hero.offsetHeight;

  stickyInTheSeries.addEventListener('mouseenter', () => {
    stickyInTheSeries.classList.remove('sticky');
  });
  stickyInTheSeries.addEventListener('mouseleave', () => {
    stickyInTheSeries.classList.add('sticky');
  });

  const expandButtons = document.querySelectorAll('.in-the-series-expand');
  const body = document.querySelector('body');
  const header = document.querySelector('header');
  expandButtons.forEach((button) => {
    button.addEventListener('click', () => {
      heroInTheSeries.classList.toggle('expanded');
      button.classList.toggle('expanded');
      body.classList.toggle('no-scroll');

      if (button.id === 'in-the-series-expand-sticky') {
        heroInTheSeries.classList.toggle('hidden');
      }
    });
  });
  document.addEventListener('scroll', () => {
    if (window.scrollY > (heroHeight - 50)) {
      stickyInTheSeries.classList.remove('hidden');
      stickyInTheSeries.classList.add('sticky');
      heroInTheSeries.classList.add('hidden');
      body.style.marginTop = '200px';
      header.classList.add('dark');
    } else {
      stickyInTheSeries.classList.add('hidden');
      heroInTheSeries.classList.remove('hidden');
      body.style.marginTop = '0';
      header.classList.remove('dark');
    }
  });
}
