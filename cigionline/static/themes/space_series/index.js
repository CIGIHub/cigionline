import './css/space_series.scss';
import Swiper, { Navigation } from 'swiper';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation]);
const breakpoint = window.matchMedia('(max-width:992px)');
let spaceSeriesPageSwiper;
let pageType;
if (document.querySelector('.space-series-article')) {
  pageType = 'article';
} else if (document.querySelector('.space-series-article-series')) {
  pageType = 'article series';
}

const enableSwiper = function(articleType) {
  const slidesPerView = articleType === 'article series' ? 8 : 6;
  spaceSeriesPageSwiper = new Swiper('.swiper-container', {
    spaceBetween: 0,
    speed: 800,
    autoHeight: pageType === 'article series',
    grabCursor: true,
    effect: 'slide',

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
      hiddenClass: 'swiper-button-hidden',
    },

    breakpoints: {
      992: {
        slidesPerView,
      },
    },
  });
};

const breakpointChecker = function() {
  if (breakpoint.matches === true) {
    if (spaceSeriesPageSwiper !== undefined) spaceSeriesPageSwiper.destroy(true, true);
  } else if (breakpoint.matches === false) {
    enableSwiper(pageType);
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();

if (pageType === 'article') {
  let sticky;
  const stickyHeader = document.getElementById('sticky-in-the-series');
  const observer = new IntersectionObserver(
    ([e]) => {
      setTimeout(() => {
        e.target.classList.toggle('sticky', e.intersectionRatio < 1);
        if (e.intersectionRatio < 1) {
          sticky = true;
        } else {
          sticky = false;
        }
      }, 50);
    },
    { rootMargin: '-51px 0px 0px 0px', threshold: [1] },
  );

  observer.observe(stickyHeader);

  stickyHeader.addEventListener('mouseenter', () => {
    if (sticky) {
      stickyHeader.classList.remove('sticky');
    }
  });
  stickyHeader.addEventListener('mouseleave', () => {
    if (sticky) {
      stickyHeader.classList.add('sticky');
    }
  });
}
