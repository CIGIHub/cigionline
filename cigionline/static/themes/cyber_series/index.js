import ScrollReveal from 'scrollreveal';
import './css/cyber_series.scss';

// window hide title after scrolling 25%

$(window).on('scroll', function () {
  const documentPercent = $(document).height() * 0.25;
  if ($(window).scrollTop() >= documentPercent) {
    $('.cyber-series-article-series-hero-content').fadeOut('slow');
  }
  if ($(window).scrollTop() < documentPercent) {
    $('.cyber-series-article-series-hero-content').fadeIn('slow');
  }
});

// add icon to exand/collapse about the series description

const firstBlock = $('.cyber-series-article-series-body .body .container').first();
const lastBlock = $('.cyber-series-article-series-body .body .container').last();

lastBlock.hide();

firstBlock.find('p').last().append('<span class="read-more"><i class="fa fa-chevron-down"></i></span>');
lastBlock.find('p').last().append('<span class="read-more"><i class="fa fa-chevron-up"></i></span>');

firstBlock.find('.read-more').on('click', function() {
  firstBlock.find('.read-more').hide();
  lastBlock.show();
});

lastBlock.find('.read-more').on('click', function() {
  firstBlock.find('.read-more').show();
  lastBlock.hide();
});

// fade in article elements

const sr = ScrollReveal();

sr.reveal('.stream-block-blockquote', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'left',
  scale: 1,
});

sr.reveal('.stream-image-block img', {
  delay: 250,
  distance: '0',
  duration: 750,
  scale: 1,
});
