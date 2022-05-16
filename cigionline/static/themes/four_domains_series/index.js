import './css/four_domains_series.scss';

const backgroundImages = Array.from(
  document.getElementById('background-images').querySelectorAll('img')
).map((img) => {
  const image = {
    img,
    classes: Array.from(img.classList),
    animation: img.dataset.animation,
    position: img.dataset.position,
    initialTop: parseInt(img.offsetTop, 10),
  };
  return image;
});

let lastKnownScrollPosition = 0;
let ticking = false;

function animateVertically(scrollPos, img) {
  const speedFast = window.innerWidth / (1980 * 0.4);
  const speedSlow = window.innerWidth / (1980 * 0.2);
  switch (img.position) {
  case 'top':
    img.img.style.top = `${img.initialTop - scrollPos * speedFast}px`;
    break;
  case 'mid':
    img.img.style.top = `${img.initialTop - scrollPos * speedSlow}px`;
    break;
  default:
    break;
  }
}

function animateImage(scrollPos) {
  backgroundImages.forEach((image) => {
    if (lastKnownScrollPosition < 800) {
      switch (image.animation) {
      case 'vertical':
        animateVertically(scrollPos, image);
        break;
      default:
        break;
      }
    }
  });
}

document.addEventListener('scroll', function () {
  lastKnownScrollPosition = window.scrollY;

  if (!ticking) {
    window.requestAnimationFrame(function () {
      animateImage(lastKnownScrollPosition);
      ticking = false;
    });

    ticking = true;
  }
});
