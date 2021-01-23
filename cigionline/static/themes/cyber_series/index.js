import './css/cyber_series.scss';

const firstBlock = $('.cyber-series-article-series-body .body .container').first();
const lastBlock = $('.cyber-series-article-series-body .body .container').last();

console.log(lastBlock);
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
