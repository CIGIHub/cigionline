/* eslint-disable no-unused-vars */

import 'swiper/swiper-bundle.css';
import './css/_home_page.scss';

import Swiper from 'swiper';
import { Navigation, Pagination } from 'swiper/modules';

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
      horizontalClass: 'swiper-pagination-horizontal-styles-disabled',
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
      992: {
        slidesPerView: 4,
        slidesPerGroup: 4,
      },
    },
  });
}
