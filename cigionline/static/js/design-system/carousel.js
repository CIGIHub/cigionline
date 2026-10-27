// =============================================================================
// Design System — shared carousel helpers (no Swiper dependency)
// Reused by every carousel init (gallery, supporting materials, video carousel)
// so the pagination markup stays identical. Pairs with components/_pagination.scss.
// =============================================================================

import { cloneTemplate } from './templates';

// Swiper renderBullet (must return an HTML string): clone the bullet <template>,
// set the active class + number, return its markup. Markup lives in
// includes/ds_js_templates.html, not here. CSS shows the number only when active.
export function paginationBullet(index, className) {
  const frag = cloneTemplate('[data-ds-pagination-bullet]');
  const outer = frag.querySelector('span');
  if (!outer) return '';
  outer.className = className;
  const num = outer.querySelector('.ds-pagination__num');
  if (num) num.textContent = index + 1;
  return outer.outerHTML;
}
