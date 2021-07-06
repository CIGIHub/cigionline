import './css/twentieth_page_singleton.scss';
import 'swiper/swiper.scss';
import Swiper, { Navigation, Pagination } from 'swiper';

Swiper.use([Navigation, Pagination]);

const swiperContainer = document.querySelector('.swiper-container');
if (swiperContainer) {
  const swiper = new Swiper('.swiper-container', {
    slidesPerView: 1,
    spaceBetween: 0,
    centeredSlides: true,

    breakpoints: {
      992: {
        slidesPerView: 3,
      },
    },

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },

    scrollbar: {
      el: '.swiper-scrollbar',
    },
  });

  const timelineNavArrows = document.querySelectorAll('.swiper-button');
  const swiperWrapper = document.querySelector('.swiper-wrapper');

  const setSwiperPadding = (slideIndex) => {
    const windowWidth = window.innerWidth;
    const offset = windowWidth / 175 + 60;
    if (windowWidth >= 992) {
      swiperContainer.style.paddingBottom = `${
        offset
        + swiper.slides[slideIndex].querySelector('.gallery-text').offsetHeight
      }px`;
    } else {
      swiperContainer.style.paddingBottom = '0px';
    }
  };

  const centreNavArrows = () => {
    const swiperHeight = parseFloat(swiperWrapper.clientHeight)
      - parseFloat(swiper.slides[swiper.activeIndex].querySelector('.gallery-text')
        .offsetHeight);
    if (window.innerWidth >= 992) {
      timelineNavArrows.forEach((elem) => {
        elem.style.top = `${parseFloat(swiperWrapper.clientHeight) / 2}px`;
      });
    } else {
      timelineNavArrows.forEach((elem) => {
        elem.style.top = `${swiperHeight / 2}px`;
      });
    }
  };

  const timelineNavButtons = document.querySelectorAll(
    '#timeline-nav li button',
  );
  const years = JSON.parse(document.getElementById('years').textContent);

  const toggleYear = function() {
    [].map.call(timelineNavButtons, function(elem) {
      elem.classList.remove('active');
    });
    this.classList.add('active');
    swiper.slideTo(years.indexOf(this.dataset.year));
  };
  [].map.call(timelineNavButtons, function(elem) {
    elem.addEventListener('click', toggleYear, false);
  });

  swiper.on('activeIndexChange', function(e) {
    for (let i = 0; i < timelineNavButtons.length; i += 1) {
      if (timelineNavButtons[i].dataset.year === years[e.activeIndex]) {
        [].map.call(timelineNavButtons, function(elem) {
          elem.classList.remove('active');
        });
        timelineNavButtons[i].classList.add('active');
      }
    }

    setSwiperPadding(e.activeIndex);
  });

  centreNavArrows();
  setSwiperPadding(0);
  window.addEventListener('resize', function() {
    setSwiperPadding(swiper.activeIndex);
    centreNavArrows();
  });
}
