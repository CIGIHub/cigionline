import './css/four_domains_series.scss';
import ScrollMagic from 'scrollmagic';

const backgroundImages = document.getElementById('background-images');
const leftImage = backgroundImages.querySelector('.left');
const rightImage = backgroundImages.querySelector('.right');

let leftOriginalWidth = parseInt(leftImage.offsetWidth, 10);
let rightOriginalWidth = parseInt(rightImage.offsetWidth, 10);
let lastKnownScrollPosition = 0;
let ticking = false;

function animateImage(scrollPos) {
  leftImage.style.width = `${leftOriginalWidth + scrollPos * 0.2}px`;
  rightImage.style.width = `${rightOriginalWidth + scrollPos * 0.2}px`;
  console.log('width: ', Number(scrollPos) * 0.5);
}

document.addEventListener('scroll', function (e) {
  lastKnownScrollPosition = window.scrollY;
  console.log('scrollY: ', lastKnownScrollPosition);

  if (!ticking) {
    window.requestAnimationFrame(function () {
      animateImage(lastKnownScrollPosition);
      ticking = false;
    });

    ticking = true;
  }
});
