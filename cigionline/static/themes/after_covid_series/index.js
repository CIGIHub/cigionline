import './css/after_covid_series.scss';

$(function() {
  const authorImages = $('.author-images').filter(function() {
    return $(this).children().length > 1;
  });
  let activeImage;
  let nextImage;

  authorImages.each(function() {
    $(this).children(':not(:first)').addClass('inactive');
    activeImage = $(this).children().first();
    nextImage = activeImage.next();
  });

  window.setInterval(function() {
    authorImages.each(function() {
      activeImage.addClass('inactive');
      nextImage.removeClass('inactive');

      activeImage = nextImage;
      nextImage = activeImage.next();
      if (!nextImage.length) {
        nextImage = activeImage.siblings().first();
      }
    });
  }, 3000);
});
