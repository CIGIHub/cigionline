import './css/twentieth_page_singleton.scss';
import 'swiper/swiper.scss';
import Swiper, { Navigation, Pagination } from 'swiper';

Swiper.use([Navigation, Pagination]);
const swiperContainer = document.querySelector('.swiper-container');

if (swiperContainer) {
  const swiper = new Swiper('.swiper-container', {
    // Optional parameters
    slidesPerView: 3,
    spaceBetween: 30,
    centeredSlides: true,
    direction: 'horizontal',
    watchSlidesProgress: true,

    // If we need pagination
    pagination: {
      el: '.swiper-pagination',
    },

    // Navigation arrows
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },

    // And if we need scrollbar
    scrollbar: {
      el: '.swiper-scrollbar',
    },
  });
}
