import './css/twenty_fifth_page_singleton.scss';
import 'swiper/swiper-bundle.css';
import Swiper from 'swiper';
import { Navigation, Pagination } from 'swiper/modules'; // eslint-disable-line import/no-unresolved

Swiper.use([Navigation, Pagination]);

const splashScrollButton = document.querySelector('.anniversary-splash-scroll');
const anniversaryContent = document.getElementById('anniversary-content');
const anniversaryStickyHeader = document.querySelector('.anniversary-sticky-header');
if (splashScrollButton && anniversaryContent) {
  splashScrollButton.addEventListener('click', () => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    anniversaryContent.scrollIntoView({
      behavior: reduceMotion ? 'auto' : 'smooth',
      block: 'start',
    });
  });
}

if (anniversaryContent && anniversaryStickyHeader) {
  let headerQueued = false;

  const updateAnniversaryHeader = () => {
    headerQueued = false;
    const contentTop = anniversaryContent.getBoundingClientRect().top + window.scrollY;
    anniversaryStickyHeader.classList.toggle('fixed', window.scrollY >= contentTop);
  };

  const queueHeaderUpdate = () => {
    if (headerQueued) return;
    headerQueued = true;
    window.requestAnimationFrame(updateAnniversaryHeader);
  };

  updateAnniversaryHeader();
  window.addEventListener('scroll', queueHeaderUpdate, { passive: true });
  window.addEventListener('resize', queueHeaderUpdate);
}

const anniversaryToggleButtons = document.querySelectorAll('[data-anniversary-toggle]');
anniversaryToggleButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.getElementById(button.dataset.anniversaryToggle);
    if (!target) return;

    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    anniversaryToggleButtons.forEach((otherButton) => {
      const otherTarget = document.getElementById(otherButton.dataset.anniversaryToggle);
      otherButton.setAttribute('aria-expanded', 'false');
      if (otherTarget) {
        otherTarget.hidden = true;
      }
    });

    button.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
    target.hidden = isExpanded;
  });
});

const anniversaryNavLinks = [...document.querySelectorAll('[data-anniversary-nav-link]')];
const anniversarySections = anniversaryNavLinks
  .map((link) => ({
    link,
    section: document.querySelector(link.getAttribute('href')),
  }))
  .filter(({ section }) => section);
if (anniversarySections.length) {
  let scrollSpyQueued = false;

  const setActiveAnniversarySection = () => {
    scrollSpyQueued = false;
    const headerOffset = anniversaryStickyHeader
      ? anniversaryStickyHeader.getBoundingClientRect().height
      : 0;
    const activationPoint = window.scrollY + headerOffset + 16;
    let activeItem = anniversarySections[0];

    anniversarySections.forEach((item) => {
      const sectionTop = item.section.getBoundingClientRect().top + window.scrollY;
      if (sectionTop <= activationPoint) {
        activeItem = item;
      }
    });

    anniversarySections.forEach(({ link }) => {
      const isActive = link === activeItem.link;
      link.classList.toggle('active', isActive);
      if (isActive) {
        link.setAttribute('aria-current', 'true');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  };

  const queueScrollSpy = () => {
    if (scrollSpyQueued) return;
    scrollSpyQueued = true;
    window.requestAnimationFrame(setActiveAnniversarySection);
  };

  setActiveAnniversarySection();
  window.addEventListener('scroll', queueScrollSpy, { passive: true });
  window.addEventListener('resize', queueScrollSpy);
}

const timelineGalleryBlocks = document.querySelectorAll('[data-anniversary-timeline-gallery]');
timelineGalleryBlocks.forEach((timelineGalleryBlock) => {
  const swiperContainer = timelineGalleryBlock.querySelector('.swiper-container');
  const prevButton = timelineGalleryBlock.querySelector('.anniversary-timeline-button-prev');
  const nextButton = timelineGalleryBlock.querySelector('.anniversary-timeline-button-next');
  if (!swiperContainer || !prevButton || !nextButton) return;
  if (!swiperContainer.querySelector('.swiper-slide')) return;
  swiperContainer.classList.add('swiper');

  const swiper = new Swiper(swiperContainer, {
    slidesPerView: 1,
    spaceBetween: 0,
    centeredSlides: true,

    breakpoints: {
      992: {
        slidesPerView: 2,
      },
    },

    navigation: {
      nextEl: nextButton,
      prevEl: prevButton,
    },
  });

  const timelineNavButtons = timelineGalleryBlock.querySelectorAll(
    '.anniversary-timeline-nav li button',
  );
  const years = [...timelineNavButtons].map((button) => button.dataset.year);

  const toggleYear = function () {
    [].map.call(timelineNavButtons, function (elem) {
      elem.classList.remove('active');
    });
    this.classList.add('active');
    swiper.slideTo(years.indexOf(this.dataset.year));
  };
  [].map.call(timelineNavButtons, function (elem) {
    elem.addEventListener('click', toggleYear, false);
  });

  swiper.on('activeIndexChange', function (e) {
    for (let i = 0; i < timelineNavButtons.length; i += 1) {
      if (timelineNavButtons[i].dataset.year === years[e.activeIndex]) {
        [].map.call(timelineNavButtons, function (elem) {
          elem.classList.remove('active');
        });
        timelineNavButtons[i].classList.add('active');
      }
    }
  });
});
