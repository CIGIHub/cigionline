import './css/space_series.scss';
import Swiper, { Navigation } from 'swiper';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation]);
const breakpoint = window.matchMedia('(max-width:992px)');
let spaceSeriesPageSwiper;

const enableSwiper = function () {
  spaceSeriesPageSwiper = new Swiper('.swiper-container', {
    spaceBetween: 0,
    speed: 800,
    autoHeight: true,
    grabCursor: true,
    disabled: true,

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
      hiddenClass: 'swiper-button-hidden',
    },

    breakpoints: {
      992: {
        slidesPerView: 8,
      },
    },
  });
};

const breakpointChecker = function () {
  // if larger viewport and multi-row layout needed
  console.log('breakpoint', breakpoint.matches);
  if (breakpoint.matches === true) {
    // clean up old instances and inline styles when available
    if (spaceSeriesPageSwiper !== undefined) spaceSeriesPageSwiper.destroy(true, true);
    // else if a small viewport and single column layout needed
  } else if (breakpoint.matches === false) {
    // fire small viewport version of swiper
    return enableSwiper();
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();
