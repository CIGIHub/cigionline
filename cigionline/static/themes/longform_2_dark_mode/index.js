import './css/longform_2_dark_mode.scss';
import ScrollReveal from 'scrollreveal';

let scrolled = null;
let headerHeight = null;
let maxHeight = null;
let scrollTop = 0;

function setScrollPosition() {
  scrollTop = $(window).scrollTop();
  scrolled = (scrollTop / maxHeight) * 100;
  $('progress').attr('value', scrolled);

  if (scrollTop > headerHeight) {
    $('body').addClass('scrolled');
  } else {
    $('body').removeClass('scrolled');
  }
}

$(window).on('load', function() {
  const docHeight = $(document).height();
  const winHeight = $(window).height();
  headerHeight = $('header').height();

  maxHeight = docHeight - winHeight;
  setScrollPosition();
});

$(window).on('scroll', function() {
  setScrollPosition();
});

const sr = ScrollReveal();

sr.reveal('.stream-block-blockquote', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'left',
  scale: 1,
});
