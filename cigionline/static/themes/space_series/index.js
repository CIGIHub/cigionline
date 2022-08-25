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

const enableSwiper = function (articleType) {
  const slidesPerView = articleType === 'article series' ? 8 : 6;
  spaceSeriesPageSwiper = new Swiper('.swiper-container', {
    spaceBetween: 0,
    speed: 800,
    autoHeight: true,
    grabCursor: true,
    disabled: true,
    grid: {
      rows: 1,
    },

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

    on: {
      navigationNext() {
        console.log(this);
      },
    },
  });
};

const breakpointChecker = function () {
  if (breakpoint.matches === true) {
    if (spaceSeriesPageSwiper !== undefined)
      spaceSeriesPageSwiper.destroy(true, true);
  } else if (breakpoint.matches === false) {
    return enableSwiper(pageType);
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();

document.addEventListener('scroll', function () {
  console.log(window.scrollY);
});
