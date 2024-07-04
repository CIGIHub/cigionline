import 'swiper/swiper-bundle.css';
import Swiper from 'swiper';
import { Navigation, Pagination, EffectCoverflow, A11y } from 'swiper/modules';
import './css/slider_gallery_block.scss';

Swiper.use([Navigation, Pagination]);

document.addEventListener('DOMContentLoaded', function () {
  const swiperContainer = document.querySelector('.swiper-container');
  if (swiperContainer) {
    const swiper = new Swiper('.swiper-container', {
      a11y: {
        prevSlideMessage: 'Previous slide',
        nextSlideMessage: 'Next slide',
      },
      slidesPerView: 1,
      spaceBetween: 0,
      loop: true,
      speed: 1000,
      centeredSlides: true,
      followFinger: false,
      modules: [Navigation, Pagination, EffectCoverflow, A11y],
      effect: 'coverflow',
      coverflowEffect: {
        rotate: 0,
        stretch: 200,
        depth: 400,
        modifier: 1,
        slideShadows: false,
        scale: 0.7,
      },
      breakpoints: {
        992: {
          slidesPerView: 3,
        },
      },

      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },

      pagination: {
        el: '.swiper-pagination',
        clickable: true,
        horizontalClass: 'swiper-pagination-horizontal-styles-disabled',
      },

      scrollbar: {
        el: '.swiper-scrollbar',
      },
    });
  }
});
