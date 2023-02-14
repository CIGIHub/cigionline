/* eslint-disable no-unused-vars */

import 'swiper/swiper-bundle.css';
import './css/_home_page.scss';

import Swiper, { Navigation, Pagination } from 'swiper';

Swiper.use([Navigation, Pagination]);

const swiperSocialRowContainer = document.querySelector('.swiper-container-social');
if (swiperSocialRowContainer) {
  const socialSwiper = new Swiper('.swiper-container-social', {
    autoHeight: true,
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,

    navigation: {
      nextEl: '.swiper-button-next-social',
      prevEl: '.swiper-button-prev-social',
    },

    pagination: {
      el: '.swiper-pagination-social',
      clickable: true,
    },

    breakpoints: {
      480: {
        slidesPerView: 2,
        slidesPerGroup: 2,
      },
      768: {
        slidesPerView: 2,
        slidesPerGroup: 2,
      },
      992: {
        slidesPerView: 3,
        slidesPerGroup: 3,
        allowTouchMove: false,
        grabCursor: false,
      },
    },
  });
}
