import './css/four_domains_series.scss';

function animateVertically(scrollPos, img, windowSizeConstant) {
  const speed = (0.25 * windowSizeConstant + 0.75) * 0.05 * img.speed;
  img.img.style.top = `${img.initialTop - scrollPos * speed}px`;
}

function animateHorizontally(scrollPos, img, windowSizeConstant) {
  const speed = (0.25 * windowSizeConstant + 0.75) * 0.05 * img.speed;
  img.img.style.left = `${img.initialLeft + scrollPos * speed}px`;
}

function animateZoom(scrollPos, img) {
  const speed = img.speed;
  const zoom = 1 + scrollPos * 0.0001 * speed;
  img.img.style.transform = `scale(${zoom})`;
  img.img.style.top = `${img.initialTop + scrollPos * 0.03 * speed}px`;
}

function animateMouse(mouseX, mouseY, img) {
  const screenWidth = window.innerWidth;
  const screenHeight = window.innerHeight;
  const middleX = screenWidth / 2;
  const middleY = screenHeight / 2;

  const x = mouseX - middleX;
  const y = mouseY - middleY;

  const speed = (1 / img.position) * img.speed * 0.1;

  img.img.style.top = `${-y * speed}px`;
  img.img.style.left = `${-x * speed}px`;
}

function animateImage(
  scrollPos,
  backgroundImages,
  windowSizeConstant,
  lastKnownScrollPosition,
) {
  backgroundImages.forEach((image) => {
    if (lastKnownScrollPosition < 800) {
      switch (image.animation) {
      case 'vertical':
        animateVertically(scrollPos, image, windowSizeConstant);
        break;
      case 'horizontal':
        animateHorizontally(scrollPos, image, windowSizeConstant);
        break;
      case 'zoom':
        animateZoom(scrollPos, image, windowSizeConstant);
        break;
      default:
        break;
      }
    }
  });
}

if (document.querySelector('.four-domains-series-article')) {
  let windowSizeConstant = window.innerWidth / 1980;

  const backgroundImages = Array.from(
    document.getElementById('background-images').querySelectorAll('img'),
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

  window.addEventListener('resize', () => {
    windowSizeConstant = window.innerWidth / 1980;
    backgroundImages.forEach((image) => {
      image.initialTop = Number(image.img.dataset.initialTop) * windowSizeConstant;
      image.initialLeft = Number(image.img.dataset.initialLeft) * windowSizeConstant;
    });

    lastKnownScrollPosition = window.scrollY;

    window.requestAnimationFrame(function() {
      animateImage(
        lastKnownScrollPosition,
        backgroundImages,
        windowSizeConstant,
        lastKnownScrollPosition,
      );
    });
  });

  document.addEventListener('scroll', function() {
    lastKnownScrollPosition = window.scrollY;

    if (!ticking) {
      window.requestAnimationFrame(function() {
        animateImage(
          lastKnownScrollPosition,
          backgroundImages,
          windowSizeConstant,
          lastKnownScrollPosition,
        );
        ticking = false;
      });

      ticking = true;
    }
  });

  document.addEventListener('mousemove', function(e) {
    backgroundImages.forEach((image) => {
      if (image.animation === 'mouse') {
        window.requestAnimationFrame(function() {
          animateMouse(e.clientX, e.clientY, image);
        });
      }
    });
  });
}
