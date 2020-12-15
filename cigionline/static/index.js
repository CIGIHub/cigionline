import 'bootstrap/dist/js/bootstrap.bundle';
import './css/cigionline.scss';

// MAIN NAVIGATION SCROLL
$(function() {
  let scrollTop = 0;

  $(window).on('scroll', function() {
    scrollTop = $(window).scrollTop();
    if (scrollTop >= 66) {
      $('#global-nav').addClass('scrolled-nav');
    } else {
      $('#global-nav').removeClass('scrolled-nav');
    }
  });
});
// SEARCH BAR OPEN

$(document).ready(function() {
  const $openSearchBtn = $('#open-search-btn');
  const openMenuClass = 'opened-popup';

  $openSearchBtn.on('click', function() {
    $(this).toggleClass('open');
    $('#popup-search').toggleClass(openMenuClass);
    $('body').toggleClass('disable-scroll');
  });

  $(document).on('click', `.${openMenuClass}`, function() {
    $(this).removeClass(openMenuClass);
    $openSearchBtn.removeClass('open');
    $('body').toggleClass('disable-scroll');
  });

  $('.custom-popup-inner').on('click', function(e) {
    e.stopPropagation();
  });
});
