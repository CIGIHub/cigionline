/* eslint-disable no-unused-vars */

import 'swiper/swiper-bundle.css';
import Swiper from 'swiper';
import { Navigation, Pagination, EffectCoverflow, A11y } from 'swiper/modules'; // eslint-disable-line import/no-unresolved
import './css/slider_gallery_block.scss';

Swiper.use([Navigation, Pagination]);

document.addEventListener('DOMContentLoaded', () => {
  const blocks = document.querySelectorAll('.slider-gallery-block');

  blocks.forEach((block) => {
    const container = block.querySelector('.swiper-container');
    if (!container) return;

    const slides = container.querySelectorAll('.swiper-slide');
    const slideCount = slides.length;

    const isDesktop = window.matchMedia('(min-width: 992px)').matches;
    const desiredSPV = isDesktop ? 3 : 1;

    const enableLoop = slideCount >= desiredSPV + 1;

    const swiper = new Swiper(container, {
      modules: [Navigation, Pagination, EffectCoverflow, A11y],
      a11y: {
        prevSlideMessage: 'Previous slide',
        nextSlideMessage: 'Next slide',
      },
      slidesPerView: 1,
      centeredSlides: true,
      spaceBetween: 0,
      speed: 800,
      loop: true,

      effect: 'coverflow',
      coverflowEffect: {
        rotate: 0,
        stretch: 200,
        depth: 400,
        slideShadows: false,
        scale: 0.7,
      },
      watchSlidesProgress: true,

      breakpoints: {
        992: {
          slidesPerView: 3,
          slidesPerGroup: 1,
        },
      },

      navigation: {
        nextEl: block.querySelector('.swiper-button-next'),
        prevEl: block.querySelector('.swiper-button-prev'),
      },
      pagination: {
        el: block.querySelector('.swiper-pagination'),
        clickable: true,
      },
    });
  });
});
