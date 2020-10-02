import 'bootstrap/dist/js/bootstrap.bundle';
import './css/cigionline.scss';


// MAIN NAVIGATION SCROLL
$(document).ready(function(){
  var scrollTop = 0;
  $(window).scroll(function(){
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
$(document).ready(function(){
  $("#open-search-btn").click(function(){
    $(this).toggleClass("open");
    $('#popup-search').toggleClass('opened-popup');
    $('body').toggleClass('disable-scroll');
  });
});