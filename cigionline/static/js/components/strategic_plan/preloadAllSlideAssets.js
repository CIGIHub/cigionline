const loadedAssets = new Set();

const preloadImageAsPromise = (src) =>
  new Promise((resolve) => {
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

const preloadAllSlideAssets = async (slides) => {
  if (!slides?.length) return;

  const allImagePromises = [];

  slides.forEach((slide) => {
    allImagePromises.push(preloadImageAsPromise(slide.background_image));
    allImagePromises.push(
      preloadImageAsPromise(slide.background_image_thumbnail),
    );

    slide.background_images?.forEach((src) => {
      allImagePromises.push(preloadImageAsPromise(src));
    });
  });

  await Promise.all(allImagePromises);
};

export default preloadAllSlideAssets;
