import './css/space_series.scss';
import Swiper, { Navigation } from 'swiper';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation]);
let pageType;
if (document.querySelector('.space-series-article')) {
  pageType = 'article';
} else if (document.querySelector('.space-series-article-series')) {
  pageType = 'article series';
} else if (document.querySelector('.space-series-multimedia')) {
  pageType = 'multimedia';
}
const breakpoint = pageType === 'article series'
  ? window.matchMedia('(max-width:992px)')
  : window.matchMedia('(max-width:767px)');
const swipers = {};

const enableSwiper = function(articleType) {
  const slidesPerViewMd = 4;
  const slidesPerViewLg = articleType === 'article series' ? 5 : 6;
  const slidesPerViewXl = 6;
  let swiperIds;
  if (articleType === 'article series') {
    swiperIds = ['.swiper-wrapper-container'];
  } else if (articleType === 'article') {
    swiperIds = ['.swiper-container-sticky', '.swiper-container-hero'];
  } else if (articleType === 'multimedia') {
    swiperIds = ['.swiper-container-hero'];
  }
  swiperIds.forEach((id) => {
    swipers[id] = new Swiper(id, {
      spaceBetween: 0,
      speed: 800,
      autoHeight: false,
      grabCursor: true,
      effect: 'slide',
      watchSlidesProgress: true,
      watchSlidesVisibility: true,

      navigation: {
        nextEl: `.swiper-button-next-${id.replace('.swiper-wrapper-container', 'series')}`,
        prevEl: `.swiper-button-prev-${id.replace('.swiper-wrapper-container', 'series')}`,
        hiddenClass: 'swiper-button-hidden',
      },

      breakpoints: {
        767: {
          slidesPerGroup: slidesPerViewMd,
          slidesPerView: slidesPerViewMd,
        },
        992: {
          slidesPerGroup: slidesPerViewLg,
          slidesPerView: slidesPerViewLg,
        },
        1200: {
          slidesPerGroup: slidesPerViewXl,
          slidesPerView: slidesPerViewXl,
        },
      },
    });
  });
};

const breakpointChecker = function() {
  if (breakpoint.matches === true) {
    for (const swiper in swipers) {
      if (swipers[swiper] !== undefined) swipers[swiper].destroy(true, true);
    }
  } else if (breakpoint.matches === false) {
    enableSwiper(pageType);
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();

if (pageType === 'article' || pageType === 'multimedia') {
  const heroInTheSeries = document.getElementById('hero-in-the-series');
  const hero = document.querySelector('.space-series-article-hero') || document.querySelector('.mm-hero');
  const heroHeight = hero.offsetHeight;

  const expandButtons = document.querySelectorAll('.in-the-series-expand');
  const body = document.querySelector('body');
  const header = document.querySelector('header');
  expandButtons.forEach((button) => {
    button.addEventListener('click', () => {
      heroInTheSeries.classList.toggle('expanded');
      button.classList.toggle('expanded');
      body.classList.toggle('no-scroll');
      if (heroInTheSeries.classList.contains('expanded') && !header.classList.contains('dark')) {
        header.classList.add('dark');
      } else if (window.scrollY < (heroHeight - 50)) {
        header.classList.remove('dark');
      }

      if (button.id === 'in-the-series-expand-sticky') {
        heroInTheSeries.classList.toggle('hidden');
      }
    });
  });

  if (pageType === 'article') {
    const stickyInTheSeries = document.getElementById('sticky-in-the-series');
    stickyInTheSeries.addEventListener('mouseenter', () => {
      stickyInTheSeries.classList.remove('sticky');
    });
    stickyInTheSeries.addEventListener('mouseleave', () => {
      stickyInTheSeries.classList.add('sticky');
    });
    document.addEventListener('scroll', () => {
      if (window.scrollY > (heroHeight - 50)) {
        stickyInTheSeries.classList.remove('hidden');
        stickyInTheSeries.classList.add('sticky');
        heroInTheSeries.classList.add('hidden');
        body.style.marginTop = '200px';
        header.classList.add('dark');
      } else {
        stickyInTheSeries.classList.add('hidden');
        heroInTheSeries.classList.remove('hidden');
        body.style.marginTop = '0';
        header.classList.remove('dark');
      }
    });
  }
} else {
  const swiperSlides = document.querySelectorAll('article.swiper-slide');
  swiperSlides.forEach((slide) => {
    // change src of image to data-src-gif on hover and change back on mouseleave
    const image = slide.querySelector('img');
    const gif = image.getAttribute('data-src-gif');
    const still = image.getAttribute('data-src-static');
    slide.addEventListener('mouseenter', () => {
      image.setAttribute('src', gif);
    });
    slide.addEventListener('mouseleave', () => {
      image.setAttribute('src', still);
    });
  });
}
