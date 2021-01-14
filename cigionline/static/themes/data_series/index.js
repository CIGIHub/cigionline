import './css/data_series.scss';

const headerEl = document.querySelector('header');
const stickyHeader = document.querySelector('.article-header-sticky');
let headerHeight = null;
let docHeight = null;
let scrolled = null;

window.addEventListener('load', function() {
  headerHeight = headerEl.offsetHeight;
  docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
});

window.addEventListener('scroll', function() {
  const scrollTop = document.querySelector('html').scrollTop;

  scrolled = (scrollTop / docHeight) * 100;
  document.querySelector('progress').setAttribute('value', scrolled);

  if (scrollTop > headerHeight) {
    stickyHeader.classList.add('scrolled');
  } else {
    stickyHeader.classList.remove('scrolled');
  }
});
