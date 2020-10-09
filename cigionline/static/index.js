import 'bootstrap/dist/js/bootstrap.bundle';
import './css/cigionline.scss';

// MAIN NAVIGATION SCROLL
$(document).ready(function() {
  let scrollTop = 0;
  $(window).scroll(function() {
    scrollTop = $(window).scrollTop();
    $('.counter').html(scrollTop);

    if (scrollTop >= 66) {
      $('#global-nav').addClass('scrolled-nav');
    } else if (scrollTop < 66) {
      $('#global-nav').removeClass('scrolled-nav');
    }
  });
});
// SEARCH BAR OPEN

$(document).ready(function() {
  let popup_open_class = 'opened-popup';
  let $open_search_btn = $('#open-search-btn');

  $open_search_btn.click(function() {
    $(this).toggleClass('open');
    $('#popup-search').toggleClass(popup_open_class);
    $('body').toggleClass('disable-scroll');
  });

  $(document).on('click', '.' + popup_open_class, function() {
    $('.' + popup_open_class).removeClass(popup_open_class);
    $open_search_btn.removeClass('open');
    $('body').toggleClass('disable-scroll');
  });

  $('.custom-popup-inner').click(function(e) {
    e.stopPropagation();
  });
});
