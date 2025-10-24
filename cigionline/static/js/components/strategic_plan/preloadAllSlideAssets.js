const loadedAssets = new Set();

const preloadImageAsPromise = (src) => new Promise((resolve) => {
  if (!src || loadedAssets.has(src)) {
    resolve();
    return;
  }

  const img = new Image();
  img.onload = () => {
    loadedAssets.add(src);
    resolve();
  };
  img.onerror = () => resolve();
  img.src = src;
});

const preloadVideoAsPromise = (src) => new Promise((resolve) => {
  if (!src || loadedAssets.has(src)) {
    resolve();
    return;
  }

  const video = document.createElement('video');
  video.onloadeddata = () => {
    loadedAssets.add(src);
    resolve();
  };
  video.onerror = () => resolve();
  video.src = src;
  video.load();
});

const preloadAllSlideAssets = async (slides) => {
  if (!slides?.length) return;

  const criticalAssets = [];

  slides.forEach((slide) => {
    if (slide.background_image_thumbnail) {
      criticalAssets.push(
        preloadImageAsPromise(slide.background_image_thumbnail),
      );
    }
    if (slide.background_video) {
      criticalAssets.push(preloadVideoAsPromise(slide.background_video));
    }
  });

  await Promise.all(criticalAssets);
};

export default preloadAllSlideAssets;
