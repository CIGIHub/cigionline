import { useEffect } from 'react';

const loadedAssets = new Set();

const preloadImage = (src) => {
  if (!src || loadedAssets.has(src)) return;
  const img = new Image();
  img.src = src;
  loadedAssets.add(src);
};

const preloadVideo = (src) => {
  if (!src || loadedAssets.has(src)) return;
  const video = document.createElement('video');
  video.src = src;
  video.preload = 'auto';
  video.muted = true;
  video.playsInline = true;
  video.load();
  loadedAssets.add(src);
};

const usePreloadSlideAssets = (slides) => {
  useEffect(() => {
    if (!slides?.length) return;

    slides.forEach((slide) => {
      preloadImage(slide.background_image);
      preloadImage(slide.background_image_thumbnail);

      slide.background_images?.forEach(preloadImage);

      if (slide.background_video) {
        preloadVideo(slide.background_video);
      }
    });
  }, []);
};

export default usePreloadSlideAssets;
