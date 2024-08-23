import './css/space_series.scss';
import Swiper from 'swiper';
import { Navigation } from 'swiper/modules'; // eslint-disable-line import/no-unresolved
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
  const slidesPerViewLg = articleType === 'article series' ? 1 : 5;
  const slidesPerViewXl = articleType === 'article series' ? 1 : 6;
  let swiperIds;
  if (articleType === 'article series') {
    swiperIds = ['.swiper-container-series-content'];
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
        nextEl: `.swiper-button-next-${id.replace('.swiper-container-', '')}`,
        prevEl: `.swiper-button-prev-${id.replace('.swiper-container-', '')}`,
        hiddenClass: 'swiper-button-hidden',
      },

      pagination: {
        horizontalClass: 'swiper-pagination-horizontal-styles-disabled',
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
    if (pageType !== 'article series') {
      enableSwiper(pageType);
    }
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();

if (pageType === 'article' || pageType === 'multimedia') {
  const heroInTheSeries = document.getElementById('hero-in-the-series');
  const hero = document.querySelector('.space-series-article-hero')
    || document.querySelector('.mm-hero');
  const heroHeight = hero.offsetHeight;

  const body = document.querySelector('body');
  const header = document.querySelector('header');

  const stickyInTheSeries = document.getElementById('sticky-in-the-series');
  const $expandButtons = $('.in-the-series-expand');
  const dropdown = document.getElementById('dropdown-in-the-series');

  $expandButtons.on('click', function() {
    $expandButtons.toggleClass('expanded');
    dropdown.classList.toggle('open');
    if (dropdown.classList.contains('open')) {
      body.classList.add('disable-scroll');
      header.classList.add('dark');
    } else {
      body.classList.remove('disable-scroll');
      if (!stickyInTheSeries.classList.contains('sticky') && window.scrollY < heroHeight - 50) {
        header.classList.remove('dark');
      }
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 767) {
      $expandButtons.removeClass('expanded');
      dropdown.classList.remove('open');
      body.classList.remove('disable-scroll');
      header.classList.remove('dark');
    }
  });

  header.addEventListener('mouseenter', () => {
    if (!stickyInTheSeries.classList.contains('hidden')) {
      stickyInTheSeries.classList.remove('sticky');
    }
  });
  header.addEventListener('mouseleave', () => {
    if (!stickyInTheSeries.classList.contains('hidden')) {
      stickyInTheSeries.classList.add('sticky');
    }
  });
  if (pageType === 'article') {
    document.addEventListener('scroll', () => {
      if (window.scrollY > heroHeight - 50) {
        stickyInTheSeries.classList.remove('hidden');
        stickyInTheSeries.classList.add('sticky');
        heroInTheSeries.classList.add('hidden');
        heroInTheSeries.style.display = 'none';
        body.style.marginTop = '80px';
        header.classList.add('dark');
      } else {
        stickyInTheSeries.classList.add('hidden');
        heroInTheSeries.classList.remove('hidden');
        heroInTheSeries.style.display = 'block';
        body.style.marginTop = '0';
        header.classList.remove('dark');
      }
    });
  }
} else {
  const swiperSlides = document.querySelectorAll('article.series-item');
  swiperSlides.forEach((slide) => {
    // change src of image to data-src-gif on hover and change back on mouseleave
    const image = slide.querySelector('img');
    if (image != null) {
      const gif = image.getAttribute('data-src-gif');
      const still = image.getAttribute('data-src-static');
      if (gif !== '' && gif != null) {
        slide.addEventListener('mouseenter', () => {
          image.setAttribute('src', gif);
        });
        slide.addEventListener('mouseleave', () => {
          image.setAttribute('src', still);
        });
      }
    }
  });
}
