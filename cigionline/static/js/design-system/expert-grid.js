// =============================================================================
// Design System — Experts Grid pagination
// Pages the [data-ds-expert-grid-item] cards in groups of data-ds-per-page and
// builds a numbered pager (prev / 1 2 3 … / next) into [data-ds-expert-grid-pager].
// Under 769px the numbered pager gives way to a cumulative "Load More" button
// (BugHerd #147) — the button is authored in the template, so this only reveals
// and wires it. Graceful: with no JS (or a single page) both controls stay
// hidden and every card shows. Pairs with .ds-pager in components/_pagination.scss.
// =============================================================================

import { icon } from './templates';

const MOBILE_QUERY = '(max-width: 768px)';

function arrow(dir, label) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = `ds-slider-arrow ds-pager__${dir}`;
  btn.setAttribute('aria-label', label);
  const glyph = icon(dir === 'prev' ? 'chevron-left' : 'chevron-right');
  const svg = glyph.querySelector('svg');
  if (svg) svg.classList.add('ds-carousel-nav__icon');
  btn.appendChild(glyph);
  return btn;
}

export default function initExpertGrids(root = document) {
  root.querySelectorAll('[data-ds-expert-grid]').forEach((grid) => {
    if (grid.dataset.dsInit) return;
    grid.dataset.dsInit = '1';

    const items = Array.from(grid.querySelectorAll('[data-ds-expert-grid-item]'));
    const perPage = parseInt(grid.dataset.dsPerPage, 10) || 9;
    const pager = grid.parentElement.querySelector('[data-ds-expert-grid-pager]');
    const more = grid.parentElement.querySelector('[data-ds-expert-grid-more]');
    const pageCount = Math.ceil(items.length / perPage);
    if (!pager || pageCount <= 1) return; // leave all cards shown; both controls stay hidden

    const prev = arrow('prev', 'Previous page');
    const next = arrow('next', 'Next page');
    const pages = document.createElement('div');
    pages.className = 'ds-pager__pages';

    let current = 1;
    const numbers = [];
    const section = grid.closest('.ds-experts-grid') || grid;
    const show = (page, scroll) => {
      current = Math.min(Math.max(page, 1), pageCount);
      items.forEach((el, i) => { el.hidden = Math.floor(i / perPage) !== current - 1; });
      numbers.forEach((b, i) => {
        const active = i === current - 1;
        b.classList.toggle('ds-pager__page--active', active);
        if (active) b.setAttribute('aria-current', 'page');
        else b.removeAttribute('aria-current');
      });
      prev.disabled = current === 1;
      next.disabled = current === pageCount;
      // Paging jumps the reader back to the section top (BugHerd #85) — but not
      // on the initial render. Instant under prefers-reduced-motion.
      if (scroll) {
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        section.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      }
    };

    for (let i = 1; i <= pageCount; i += 1) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'ds-pager__page';
      b.textContent = i;
      b.setAttribute('aria-label', `Page ${i}`);
      b.addEventListener('click', () => show(i, true));
      pages.appendChild(b);
      numbers.push(b);
    }

    prev.addEventListener('click', () => show(current - 1, true));
    next.addEventListener('click', () => show(current + 1, true));

    pager.append(prev, pages, next);

    // --- Mobile: cumulative "Load More" instead of numbered pages (#147) -----
    // `shown` counts revealed cards, so the list only ever grows. No scroll jump
    // here: the reader stays where they are and the new cards appear below.
    let shown = perPage;
    const reveal = () => {
      items.forEach((el, i) => { el.hidden = i >= shown; });
      if (more) more.hidden = shown >= items.length;
    };

    if (more) {
      more.addEventListener('click', () => {
        shown = Math.min(shown + perPage, items.length);
        reveal();
      });
    }

    const mq = window.matchMedia(MOBILE_QUERY);
    const sync = () => {
      if (mq.matches) {
        pager.hidden = true;
        shown = Math.max(shown, perPage); // keep whatever the reader already opened
        reveal();
      } else {
        if (more) more.hidden = true;
        pager.hidden = false;
        show(current); // back to the page the numbered pager was on
      }
    };
    mq.addEventListener('change', sync);
    sync();
  });
}
