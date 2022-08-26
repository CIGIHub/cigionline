import './css/space_series.scss';
import Swiper, { Navigation } from 'swiper';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation]);
let spaceSeriesPageSwiper;
let pageType;
if (document.querySelector('.space-series-article')) {
  pageType = 'article';
} else if (document.querySelector('.space-series-article-series')) {
  pageType = 'article series';
}
const breakpoint = pageType === 'article series'
  ? window.matchMedia('(max-width:992px)')
  : window.matchMedia('(max-width:768px)');
const swipers = {};

const enableSwiper = function(articleType) {
  const slidesPerViewLg = articleType === 'article series' ? 8 : 6;
  const slidesPerViewMd = articleType === 'article series' ? 8 : 4;
  const swiperIds = articleType === 'article series' ? ['.swiper-container'] : ['.swiper-container-sticky', '.swiper-container-hero'];
  swiperIds.forEach((id) => {
    swipers[id] = new Swiper(id, {
      spaceBetween: 0,
      speed: 800,
      autoHeight: pageType === 'article series',
      grabCursor: true,
      effect: 'slide',

      navigation: {
        nextEl: `.swiper-button-next-${id.replace('.swiper-container-', '')}`,
        prevEl: `.swiper-button-prev-${id.replace('.swiper-container-', '')}`,
        hiddenClass: 'swiper-button-hidden',
      },

      breakpoints: {
        768: {
          slidesPerView: slidesPerViewMd,
        },
        992: {
          slidesPerView: slidesPerViewLg,
        },
      },
    });
  });
  console.log(swipers)
};

const breakpointChecker = function() {
  if (breakpoint.matches === true) {
    if (spaceSeriesPageSwiper !== undefined) spaceSeriesPageSwiper.destroy(true, true);
  } else if (breakpoint.matches === false) {
    enableSwiper(pageType);
  }
};

breakpoint.addEventListener('change', breakpointChecker);

breakpointChecker();

function getOffset(el) {
  const rect = el.getBoundingClientRect();
  return {
    left: rect.left,
    top: rect.top
  };
}

if (pageType === 'article') {
  let sticky;
  const stickyInTheSeries = document.getElementById('sticky-in-the-series');
  const heroInTheSeries = document.getElementById('hero-in-the-series');
  const hero = document.querySelector('.space-series-article-hero');
  let heroHeight = hero.offsetHeight;
  

  // const observer = new IntersectionObserver(
  //   ([e]) => {
  //     if (window.innerWidth > 768) {
  //       e.target.classList.toggle('sticky', e.intersectionRatio < 1);
  //       if (e.intersectionRatio < 1) {
  //         sticky = true;
  //       } else {
  //         sticky = false;
  //       }
  //     }
  //   },
  //   { rootMargin: '-50px 0px 0px 0px', threshold: [0.5, 1] },
  // );

  // observer.observe(stickyHeader);

  stickyInTheSeries.addEventListener('mouseenter', () => {
    stickyInTheSeries.classList.remove('sticky');
  });
  stickyInTheSeries.addEventListener('mouseleave', () => {
    stickyInTheSeries.classList.add('sticky');
  });

  const expandButtons = document.querySelectorAll('.in-the-series-expand');
  const body = document.querySelector('body');
  expandButtons.forEach((button) => {
    button.addEventListener('click', () => {
      heroInTheSeries.classList.toggle('expanded');
      button.classList.toggle('expanded');
      body.classList.toggle('no-scroll');

      if (button.id === 'in-the-series-expand-sticky') {
        heroInTheSeries.classList.toggle('hidden');
      }
    });
  });
  document.addEventListener('scroll', () => {
    if (window.scrollY > (heroHeight - 50)) {
      stickyInTheSeries.classList.remove('hidden');
      stickyInTheSeries.classList.add('sticky');
      heroInTheSeries.classList.add('hidden');
      document.querySelector('.body').style.marginTop = '200px';
    } else {
      stickyInTheSeries.classList.add('hidden');
      heroInTheSeries.classList.remove('hidden');
      document.querySelector('.body').style.marginTop = '1em';
    }
  });
}
