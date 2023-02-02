/* eslint-disable no-unused-vars */

import 'swiper/swiper-bundle.css';
import './css/_home_page.scss';

import Swiper, { Navigation, Pagination } from 'swiper';

// Homepage Highlights
Swiper.use([Navigation, Pagination]);
const swiperContainer = document.querySelector('.swiper-container');

if (swiperContainer) {
  const swiperControls = swiperContainer.querySelector('.swiper-controls');
  const homepageSwiper = new Swiper('.swiper-container', {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },

    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },

    breakpoints: {
      480: {
        slidesPerView: 2,
        slidesPerGroup: 2,
      },
      768: {
        slidesPerView: 3,
        slidesPerGroup: 3,
      },
    },
  });
}

const swiperSocialRowContainer = document.querySelector('.swiper-container-social');
if (swiperSocialRowContainer) {
  const socialSwiper = new Swiper('.swiper-container-social', {
    autoHeight: true,
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    grabCursor: true,

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
      },
    },
  });
}
