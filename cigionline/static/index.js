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
  const $openSearchBtn = $('#open-search-btn');
  const open_menu_class = 'opened-popup';

  $openSearchBtn.click(function() {
    $(this).toggleClass('open');
    $('#popup-search').toggleClass(open_menu_class);
    $('body').toggleClass('disable-scroll');
  });

  $(document).on('click', `.${open_menu_class}`, function() {
    $(this).removeClass(open_menu_class);
    $openSearchBtn.removeClass('open');
    $('body').toggleClass('disable-scroll');
  });

  $('.custom-popup-inner').click(function(e) {
    e.stopPropagation();
  });
});
