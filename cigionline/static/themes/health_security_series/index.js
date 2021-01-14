import './css/health_security_series.scss';

$(function() {
  const authorImages = $('.author-images').filter(function() {
    return $(this).children('a').length > 1;
  });

  authorImages.each(function() {
    $(this).children('a:not(:first-of-type)').addClass('inactive');
  });

  window.setInterval(function() {
    authorImages.each(function() {
      let nextImage = $(this).find('.inactive');
      let activeImage = nextImage.siblings('a');

      nextImage.removeClass('inactive');
      activeImage.addClass('inactive');

      nextImage = [activeImage, activeImage = nextImage][0];
    });
  }, 3000);
});
