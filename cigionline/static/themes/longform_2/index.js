/* eslint-disable no-unused-vars */

import ScrollReveal from 'scrollreveal';
import Panzoom from '@panzoom/panzoom';
import './css/longform_2.scss';

const panzoomContainers = Array.from(document.getElementsByClassName('stream-image-scroll-block'));
const panzoomImg = [];
const panzoomScrollbar = [];
const panzoomArrow = [];
const panzoomScrollbarWrapper = [];

function setScrollBarWidth(index) {
  panzoomScrollbar[index].style.width = `${Math.min((panzoomContainers[index].offsetWidth / panzoomImg[index].offsetWidth) * 100, 100)}%`;
}

function moveScrollBar(x, index) {
  panzoomScrollbar[index].style.transform = `matrix(1,0,0,1,${x},0)`;
}

function moveImage(x, index) {
  panzoomImg[index].style.transform = `matrix(1,0,0,1,${x},0)`;
}

function resizeUpdate() {
  panzoomContainers.forEach(function(panzoomContainer, index) {
    setScrollBarWidth(index);
    if (panzoomImg[index].offsetWidth <= panzoomContainer.offsetWidth) {
      panzoomScrollbarWrapper[index].style.display = 'none';
      panzoomArrow[index].style.display = 'none';
    } else {
      panzoomScrollbarWrapper[index].style.display = 'block';
      panzoomArrow[index].style.display = 'block';
    }
  });
}

panzoomContainers.forEach(function(panzoomContainer, index) {
  panzoomImg[index] = panzoomContainer.querySelector('img');
  panzoomScrollbar[index] = panzoomContainer.querySelector('.panzoom-scrollbar-inner');
  panzoomScrollbarWrapper[index] = panzoomContainer.querySelector('.panzoom-scrollbar-outer');
  panzoomArrow[index] = panzoomContainer.querySelector('.panzoom-arrow');
  const panzoomImgInstance = Panzoom(panzoomImg[index], { contain: 'outside', disableYAxis: true });
  const panzoomScrollbarInstance = Panzoom(panzoomScrollbar[index], { contain: 'inside', disableYAxis: true });

  setScrollBarWidth(index);

  panzoomImg[index].addEventListener('panzoompan', function(event) {
    const x = Math.abs(
      (panzoomScrollbar[index].offsetWidth / panzoomContainers[index].offsetWidth) * event.detail.x,
    );
    moveScrollBar(x, index);
  });

  panzoomScrollbar[index].addEventListener('panzoompan', function(event) {
    const x = Math.abs(
      (panzoomContainers[index].offsetWidth / panzoomScrollbar[index].offsetWidth) * event.detail.x,
    ) * -1;
    moveImage(x, index);
  });
});

window.addEventListener('resize', resizeUpdate);

/* sticky header */

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
  delay: 100,
  distance: '0',
  duration: 750,
  scale: 1,
});

sr.reveal('.stream-block-pull-quote.right', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'right',
  scale: 1,
});

sr.reveal('.stream-block-pull-quote.left', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'left',
  scale: 1,
});
