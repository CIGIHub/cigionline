import 'bootstrap/dist/js/bootstrap.bundle';
import './css/cigionline.scss';

import addInlineVideoActions from './js/inline_video_block';

// MAIN NAVIGATION SCROLL
$(function () {
  let scrollTop = 0;

  $(window).on('scroll', function () {
    scrollTop = $(window).scrollTop();
    if (scrollTop >= 66) {
      $('#global-nav').addClass('scrolled-nav');
    } else {
      $('#global-nav').removeClass('scrolled-nav');
    }
  });

  const accordions = document.getElementsByClassName('accordion');
  for (let i = 0; i < accordions.length; i += 1) {
    accordions[i].addEventListener('click', function () {
      this.classList.toggle('active');
      const panel = this.nextElementSibling;
      if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
      } else {
        panel.style.maxHeight = `${panel.scrollHeight}px`;
      }
    });
  }
});

// SEARCH BAR OPEN
$(function () {
  const $openSearchBtn = $('#open-search-btn');
  const $openMenuBtn = $('#open-menu-btn');
  const openMenuClass = 'opened-popup';

  $openSearchBtn.on('click', function () {
    $(this).toggleClass('open');
    $('#popup-search').toggleClass(openMenuClass);
    $('body').toggleClass('disable-scroll');
  });

  $openMenuBtn.on('click', function () {
    $(this).toggleClass('open');
    $('#popup-menu').toggleClass(openMenuClass);
    $('body').toggleClass('disable-scroll');
  });

  $(document).on('click', `.${openMenuClass}`, function (e) {
    $(this).removeClass(openMenuClass);
    $openSearchBtn.removeClass('open');
    $('body').toggleClass('disable-scroll');
  });

  $('.custom-popup-inner').on('click', function (e) {
    e.stopPropagation();
  });
});

addInlineVideoActions();
