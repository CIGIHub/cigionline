// =============================================================================
// Design System — Gallery (carousel) loader
// Lazy-loads the Swiper-backed init only when a gallery is present, keeping
// Swiper + its CSS out of the main bundle on pages that don't use it.
// =============================================================================

export default function initGalleries(root = document) {
  if (!root.querySelector('[data-ds-gallery], [data-ds-carousel], [data-ds-carousel-mobile]')) return;
  import('./gallery-init').then(({ default: run }) => run(root));
}
