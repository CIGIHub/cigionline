import './css/four_domains_series.scss';

const backgroundImages = document.getElementById('background-images');
const topImage = backgroundImages.querySelector('.top');
const midImage = backgroundImages.querySelector('.mid');
const topImageInitialTop = parseInt(topImage.offsetTop, 10);
const midImageInitialTop = parseInt(midImage.offsetTop, 10);
console.log(topImageInitialTop);

let lastKnownScrollPosition = 0;
let ticking = false;

function animateImage(scrollPos) {
  if (lastKnownScrollPosition < 800) {
    topImage.style.top = `${topImageInitialTop - scrollPos * 0.4}px`;
    midImage.style.top = `${midImageInitialTop - scrollPos * 0.2}px`;

    // topImage.style.transform = `scale(${1 + scrollPos * 0.0002})`;
    // midImage.style.transform = `scale(${1 + scrollPos * 0.0002})`;
  } else {

  }
  // leftImage.style.transform = `scale(${1 + scrollPos * 0.001})`;
  // rightImage.style.transform = `scale(${1 + scrollPos * 0.001})`;
}

document.addEventListener('scroll', function (e) {
  lastKnownScrollPosition = window.scrollY;
  console.log(lastKnownScrollPosition);

  if (!ticking) {
    window.requestAnimationFrame(function () {
      animateImage(lastKnownScrollPosition);
      ticking = false;
    });

    ticking = true;
  }
});
