// =============================================================================
// Design System — reading rail height (BugHerd #523)
//
// Publishes each reading aside's height as --ds-rail-h so _reading.scss can let
// a rail taller than the screen scroll with the page and pin by its bottom
// edge, instead of clipping it in an inner scroll box (#460). Re-measured only
// when the rail's size changes — images and fonts loading, an author group
// collapsed or expanded, a resize — never on scroll. Browsers without
// ResizeObserver fall back to load / resize / group toggle.
//
// Also wires the long-group "Show N more" toggles (#523 revision): the folded
// state is server-rendered and CSS-hidden under html.js, so this only flips
// it. Focus stays on the button either way; the button never hides, and a
// collapse moves any focus left inside the folded rows back to it.
// =============================================================================

const publishRailHeight = (rail) => rail.style.setProperty('--ds-rail-h', `${rail.offsetHeight}px`);

// Height of the event hero pin-bar while it shows (fixed under the header once
// the title scrolls away — hero-pinbar.js). html's scroll-padding-top clears
// the header but not this bar.
function pinbarHeight() {
  const bar = document.querySelector('[data-ds-hero-pinbar].ds-hero__pinbar--visible');
  return bar ? bar.offsetHeight : 0;
}

// Collapse: bring the button fully into view with the least scroll (no-op
// when it already is), clear of the header and the pin-bar (WCAG 2.4.11 —
// audit F2). Collapsing a long list can pull it far above the viewport.
function revealButton(btn) {
  btn.style.scrollMarginTop = `${pinbarHeight()}px`;
  btn.scrollIntoView({ block: 'nearest' });
}

// Expand: a rail that grows past the screen can jump up (it was pinned, or
// the shell's end is pushing it), so the first revealed row can land above
// the viewport (audit F1). Scroll back just far enough to show its top, but
// only as far as the rail moves with the scroll. In flow (or filling its
// shell) it moves freely. Pinned or pushed above its in-flow spot, it moves
// only until it reaches its sticky offset, then holds still, so scrolling
// further would only move the article. No-op when the row's top is in view.
function revealFirstRow(rail, row) {
  const band = (parseFloat(window.getComputedStyle(document.documentElement).scrollPaddingTop) || 0)
    + pinbarHeight();
  const shortBy = band - row.getBoundingClientRect().top;
  if (shortBy <= 0) return;
  let by = shortBy;
  const cs = window.getComputedStyle(rail);
  if (cs.position === 'sticky') {
    const offset = parseFloat(cs.top) || 0;
    const railTop = rail.getBoundingClientRect().top;
    const shell = rail.parentElement;
    const flowTop = shell.getBoundingClientRect().top
      + (parseFloat(window.getComputedStyle(shell).paddingTop) || 0);
    if (flowTop < offset && railTop - flowTop > 1) by = Math.min(by, Math.max(0, offset - railTop));
  }
  if (by > 0) window.scrollBy({ top: -by });
}

function toggleGroup(btn) {
  const rows = document.getElementById(btn.getAttribute('aria-controls'));
  const label = btn.querySelector('.ds-button__label');
  if (!rows || !label) return;
  if (!btn.dataset.dsLabelMore) btn.dataset.dsLabelMore = label.textContent;

  const open = btn.getAttribute('aria-expanded') !== 'true';
  btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  // A mouse click doesn't move focus to a button in Safari, so focus
  // could still sit on a link inside the rows about to hide.
  if (!open && rows.contains(document.activeElement)) btn.focus({ preventScroll: true });
  rows.toggleAttribute('data-ds-open', open);
  label.textContent = open ? (btn.dataset.dsLabelLess || btn.dataset.dsLabelMore) : btn.dataset.dsLabelMore;
  // Re-measure now (not on the next observer tick) so the sticky offset is
  // current before anything reads layout below.
  const rail = btn.closest('.ds-reading__aside');
  if (rail) publishRailHeight(rail);
  if (!open) revealButton(btn);
  else if (rail && rows.firstElementChild) revealFirstRow(rail, rows.firstElementChild);
}

// One delegated listener, bound when the bundle evaluates — not inside the
// per-page init chain — so the folded rows can always be revealed even if
// an earlier initialiser throws (audit F4). Wiring needs no per-button setup.
// Bound once per document: a second copy would toggle twice and cancel out.
// (The flag's name must not match the [data-ds-aside-toggle] selector.)
if (!document.documentElement.dataset.dsAsideToggleBound) {
  document.documentElement.dataset.dsAsideToggleBound = '1';
  document.addEventListener('click', (event) => {
    const btn = event.target.closest && event.target.closest('[data-ds-aside-toggle]');
    if (btn) toggleGroup(btn);
  });
}

export default function initReadingRails(root = document) {
  root.querySelectorAll('.ds-reading__aside').forEach((rail) => {
    if (rail.dataset.dsInit) return;
    rail.dataset.dsInit = '1';

    const publish = () => publishRailHeight(rail);

    if ('ResizeObserver' in window) {
      new window.ResizeObserver(publish).observe(rail);
    } else {
      window.addEventListener('load', publish);
      window.addEventListener('resize', publish);
      // <details> toggle doesn't bubble; capture catches the author groups.
      rail.addEventListener('toggle', publish, true);
    }
    publish();
  });
}
