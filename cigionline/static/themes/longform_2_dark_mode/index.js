import './css/longform_2_dark_mode.scss';

$(window).on('load', function() {
  const headerHeight = $('header').height();
  const scrollTop = $(window).scrollTop();
  const docHeight = $(document).height();
  const winHeight = $(window).height();

  const maxHeight = docHeight - winHeight;
  const scrolled = (scrollTop / maxHeight) * 100;

  console.log('here');
  console.log(headerHeight);

  $('progress').attr('value', scrolled);

  if (scrollTop > headerHeight) {
    $('body').addClass('scrolled');
  } else {
    $('body').removeClass('scrolled');
  }
});