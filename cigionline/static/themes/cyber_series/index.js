import './css/cyber_series.scss';

const firstBlock = $('.cyber-series-article-series-body .block-paragraph').first();
const lastBlock = $('.cyber-series-article-series-body .block-paragraph').last();

lastBlock.hide();

let readMore = firstBlock.find('p').last().append('<span class="read-more"><i class="fa fa-chevron-down"></i></span>');
let readLess = lastBlock.find('p').last().append('<span class="read-more"><i class="fa fa-chevron-up"></i></span>');

readMore.on('click', function(){
  firstBlock.find('.read-more').hide();
  lastBlock.show();
});

readLess.on('click', function(){
  firstBlock.find('.read-more').show();
  lastBlock.hide();
});