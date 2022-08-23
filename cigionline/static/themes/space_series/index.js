import './css/space_series.scss';
import Swiper, { Navigation } from 'swiper';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation]);
const swiperContainer = document.querySelector('.swiper-container');

if (swiperContainer) {
  const spaceSeriesPageSwiper = new Swiper('.swiper-container', {
    slidesPerView: 1,
    spaceBetween: 0,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
      hiddenClass: 'swiper-button-hidden',
    },

    breakpoints: {
      480: {
        slidesPerView: 3,
      },
      768: {
        slidesPerView: 4,
      },
      992: {
        slidesPerView: 6,
      },
    },
  });
}
