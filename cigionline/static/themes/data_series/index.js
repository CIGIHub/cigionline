import './css/data_series.scss';

const headerEl = document.querySelector('header');
const stickyHeader = document.querySelector('.article-header-sticky');
var headerHeight, docHeight = null;

window.addEventListener('load', function() {
  headerHeight = headerEl.offsetHeight;
  docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
});

window.addEventListener('scroll', function(){
  var scrollTop = document.querySelector('html').scrollTop;

  var scrolled = (scrollTop/docHeight) * 100;
  document.querySelector('progress').style.width = scrolled + "%";

  if (scrollTop > headerHeight){
    stickyHeader.classList.add('scrolled');
  }
  else {
    stickyHeader.classList.remove('scrolled');
  }

});