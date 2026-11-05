// =============================================================================
// Design System — reading progress bar
//
// Thin brand-red line fixed to the top of the viewport that grows 0→100% as the
// reader moves through the article (guide: Publication + Long-form Reading —
// "confirms reading context quietly"). The bar element ships in
// reading_body.html and tracks the .ds-reading column; 100% lands as its end
// scrolls into view. Width follows the scroll position directly (scaleX per
// frame), so it stays useful under reduced motion — it's a position indicator,
// not decoration.
// =============================================================================

export default function initReadingProgress(root = document) {
  const bar = (root === document ? document : root).querySelector('[data-ds-reading-progress]');
  if (!bar || bar.dataset.dsInit) return;
  bar.dataset.dsInit = '1';

  const article =
    bar.closest('.ds-surface')?.querySelector('.ds-reading') ||
    document.querySelector('.ds-reading');
  if (!article) return;

  let ticking = false;

  const update = () => {
    ticking = false;
    const rect = article.getBoundingClientRect();
    const total = rect.height - window.innerHeight;
    const progress = total > 0 ? Math.min(Math.max(-rect.top / total, 0), 1) : rect.top < 0 ? 1 : 0;
    bar.style.transform = `scaleX(${progress})`;
  };

  window.addEventListener(
    'scroll',
    () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    },
    { passive: true },
  );
  window.addEventListener('resize', update);

  update();
}
