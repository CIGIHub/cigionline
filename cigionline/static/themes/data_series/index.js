import './css/data_series.scss';
//import createStickyHeaderScrollListener from '../../js/create_sticky_header_scroll_listener';

const headerEl = document.querySelector('header');
const stickyHeader = document.querySelector('.article-header-sticky');
var headerHeight = null;

window.addEventListener('load', function() {
  headerHeight = headerEl.offsetHeight
  
});

window.addEventListener('scroll', function(){
  var scrollTop = document.querySelector('html').scrollTop;
  if (scrollTop > headerHeight){
    stickyHeader.classList.add('scrolled');
  }
  else {
    stickyHeader.classList.remove('scrolled');
  }
});