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
const closeAnniversaryToggles = (focusButton = null) => {
  anniversaryToggleButtons.forEach((button) => {
    const target = document.getElementById(button.dataset.anniversaryToggle);
    button.setAttribute('aria-expanded', 'false');
    if (target) {
      target.hidden = true;
    }
  });

  if (focusButton) {
    focusButton.focus();
  }
};

anniversaryToggleButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.getElementById(button.dataset.anniversaryToggle);
    if (!target) return;

    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    closeAnniversaryToggles();

    button.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
    target.hidden = isExpanded;
  });
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('[data-anniversary-toggle], .anniversary-share-panel')) {
    closeAnniversaryToggles();
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;

  const openButton = [...anniversaryToggleButtons].find(
    (button) => button.getAttribute('aria-expanded') === 'true',
  );
  closeAnniversaryToggles(openButton);
});

document.querySelectorAll('.anniversary-share-panel a').forEach((link) => {
  link.addEventListener('click', () => {
    closeAnniversaryToggles();
  });
});

const anniversaryMenuButton = document.querySelector('[data-anniversary-menu-toggle]');
const anniversaryMenuOverlay = document.getElementById('anniversary-menu-overlay');
const anniversaryMenuAccordions = document.querySelectorAll('.anniversary-menu-accordion');
const anniversaryPageNavLinks = document.querySelectorAll('.anniversary-site-links a');

const setAnniversaryPageNavEnabled = (isEnabled) => {
  anniversaryPageNavLinks.forEach((link) => {
    link.setAttribute('aria-hidden', isEnabled ? 'false' : 'true');
    if (isEnabled) {
      link.removeAttribute('tabindex');
    } else {
      link.setAttribute('tabindex', '-1');
    }
  });
};

const closeAnniversaryMenu = (focusButton = null) => {
  if (!anniversaryMenuButton || !anniversaryMenuOverlay) return;

  anniversaryMenuButton.classList.remove('open');
  anniversaryMenuButton.setAttribute('aria-expanded', 'false');
  anniversaryMenuButton.setAttribute('aria-label', 'Open menu');
  anniversaryMenuOverlay.hidden = true;
  if (anniversaryStickyHeader) {
    anniversaryStickyHeader.classList.remove('menu-open');
  }
  setAnniversaryPageNavEnabled(true);
  document.body.classList.remove('disable-scroll');

  if (focusButton) {
    focusButton.focus();
  }
};

const openAnniversaryMenu = () => {
  if (!anniversaryMenuButton || !anniversaryMenuOverlay) return;

  closeAnniversaryToggles();
  anniversaryMenuButton.classList.add('open');
  anniversaryMenuButton.setAttribute('aria-expanded', 'true');
  anniversaryMenuButton.setAttribute('aria-label', 'Close menu');
  anniversaryMenuOverlay.hidden = false;
  if (anniversaryStickyHeader) {
    anniversaryStickyHeader.classList.add('menu-open');
  }
  setAnniversaryPageNavEnabled(false);
  document.body.classList.add('disable-scroll');
};

if (anniversaryMenuButton && anniversaryMenuOverlay) {
  anniversaryMenuButton.addEventListener('click', () => {
    const isOpen = anniversaryMenuButton.getAttribute('aria-expanded') === 'true';

    if (isOpen) {
      closeAnniversaryMenu();
    } else {
      openAnniversaryMenu();
    }
  });

  anniversaryMenuOverlay.addEventListener('click', (event) => {
    if (event.target === anniversaryMenuOverlay) {
      closeAnniversaryMenu();
    }
  });
}

document.addEventListener('keydown', (event) => {
  if (
    event.key === 'Escape'
    && anniversaryMenuButton
    && anniversaryMenuButton.getAttribute('aria-expanded') === 'true'
  ) {
    closeAnniversaryMenu(anniversaryMenuButton);
  }
});

anniversaryMenuAccordions.forEach((accordion) => {
  accordion.addEventListener('click', () => {
    const panel = accordion.nextElementSibling;
    if (!panel) return;

    const isExpanded = accordion.getAttribute('aria-expanded') === 'true';
    accordion.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
    panel.style.maxHeight = isExpanded ? null : `${panel.scrollHeight}px`;
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

const eventsBlock = document.querySelector('[data-anniversary-events]');
if (eventsBlock) {
  const swiperContainer = eventsBlock.querySelector('.anniversary-events-swiper');
  const prevButton = eventsBlock.querySelector('.anniversary-events-button-prev');
  const nextButton = eventsBlock.querySelector('.anniversary-events-button-next');
  const pagination = eventsBlock.querySelector('.anniversary-events-pagination');

  if (
    swiperContainer
    && prevButton
    && nextButton
    && pagination
    && swiperContainer.querySelector('.swiper-slide')
  ) {
    swiperContainer.classList.add('swiper');

    new Swiper(swiperContainer, {
      slidesPerView: 1,
      spaceBetween: 0,
      breakpoints: {
        768: {
          slidesPerView: 2,
        },
        992: {
          slidesPerView: 3,
        },
      },
      navigation: {
        nextEl: nextButton,
        prevEl: prevButton,
      },
      pagination: {
        el: pagination,
        clickable: true,
        renderBullet(index, className) {
          return [
            `<button class="${className}" type="button"`,
            ` aria-label="Go to events slide ${index + 1}">`,
            `<span>${index + 1}</span></button>`,
          ].join('');
        },
      },
    });
  }
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
