import './css/four_domains_series.scss';

let windowSizeConstant = window.innerWidth / 1980;

const backgroundImages = Array.from(
  document.getElementById('background-images').querySelectorAll('img')
).map((img) => {
  const image = {
    img,
    classes: Array.from(img.classList),
    animation: img.dataset.animation,
    position: img.dataset.position,
    speed: Number(img.dataset.speed),
    initialTop: Number(img.dataset.initialTop) * windowSizeConstant,
    initialLeft: Number(img.dataset.initialLeft) * windowSizeConstant,
  };
  image.img.style.left = `${image.initialLeft}px`;
  image.img.style.top = `${image.initialTop}px`;
  image.img.style.opacity = 1;
  return image;
});

let lastKnownScrollPosition = 0;
let ticking = false;

document.addEventListener('resize', () => {
  windowSizeConstant = window.innerWidth / 1980;
});

function animateVertically(scrollPos, img) {
  const speed = windowSizeConstant * 0.05 * img.speed;
  img.img.style.top = `${img.initialTop - scrollPos * speed}px`;
}

function animateHorizontally(scrollPos, img) {
  const speed = windowSizeConstant * 0.05 * img.speed;
  img.img.style.left = `${img.initialLeft + scrollPos * speed}px`;
}

function animateZoom(scrollPos, img) {
  const speed = windowSizeConstant * img.speed;
  const zoom = 1 + scrollPos * 0.0001 * speed;
  img.img.style.transform = `scale(${zoom})`;
  img.img.style.top = `${img.initialTop + scrollPos * 0.05 * speed}px`;
}

function animateImage(scrollPos) {
  backgroundImages.forEach((image) => {
    if (lastKnownScrollPosition < 800) {
      switch (image.animation) {
      case 'vertical':
        animateVertically(scrollPos, image);
        break;
      case 'horizontal':
        animateHorizontally(scrollPos, image);
        break;
      case 'zoom':
        animateZoom(scrollPos, image);
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
