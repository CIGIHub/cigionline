/* eslint-disable no-unused-vars */

import 'swiper/swiper-bundle.css';
import './css/_home_page.scss';

import Swiper, { Navigation, Pagination } from 'swiper';

Swiper.use([Navigation, Pagination]);

const swiperSocialRowContainer = document.querySelector(
  '.swiper-container-social',
);
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

const liveEvent = document.getElementById('live-event');
const liveEventButtonContainer = document.getElementById('live-event-button-container');
const liveEventButton = document.getElementById('live-event-button');
if (liveEvent) {
  const eventTime = Number(liveEvent.dataset.eventTime) * 1000;

  setInterval(function () {
    const currentTimestamp = Date.now();
    const timeDiff = eventTime - currentTimestamp;
    let eventStatus;

    if (timeDiff <= 0 && timeDiff >= -3600000) {
      eventStatus = 'live';
    } else if (timeDiff > 0 && timeDiff <= 3600000) {
      eventStatus = 'upcoming';
    } else {
      eventStatus = 'hidden';
    }

    switch (eventStatus) {
    case 'live':
      if (!liveEvent.classList.contains('live')) {
        liveEvent.classList.remove('hidden');
        liveEvent.classList.remove('upcoming');
        liveEvent.classList.add('live');
        liveEventButton.innerHTML = 'Watch live';
        liveEventButtonContainer.classList.remove('hidden');
      }
      break;
    case 'upcoming':
      if (!liveEvent.classList.contains('upcoming')) {
        liveEvent.classList.remove('hidden');
        liveEvent.classList.add('upcoming');
        liveEventButton.innerHTML = 'Watch live soon';
        liveEventButtonContainer.classList.remove('hidden');
      }
      break;
    case 'hidden':
      if (!liveEvent.classList.contains('hidden')) {
        liveEvent.classList.add('hidden');
        liveEventButtonContainer.classList.add('hidden');
      }
      break;
    default:
      if (!liveEvent.classList.contains('hidden')) {
        liveEvent.classList.add('hidden');
        liveEventButtonContainer.classList.add('hidden');
      }
      break;
    }
  }, 1000);
}
