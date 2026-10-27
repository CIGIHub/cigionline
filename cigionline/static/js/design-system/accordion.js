// =============================================================================
// Design System — Accordion Module behaviour
//
// Native <details>/<summary> gives us accessible, no-JS-functional markup, but
// it snaps open/closed with no animation, and its single-open `name` grouping
// closes siblings instantly. This progressive enhancement animates the
// expand/collapse (and sibling close) with the Web Animations API.
//
// We animate the <details> element's OWN height (locking it before reveal) so
// the summary never moves and the content is never painted at full height for
// a frame — that frame-flash is the usual "hitch" in naive details animations.
// Height-only (no opacity crossfade) keeps the motion crisp and serious.
//
// First principles honoured here:
//   - Motion timings come from the design-system tokens (single source of
//     truth) — never hardcoded here.
//   - prefers-reduced-motion fully disables animation (instant toggle).
//   - No-JS / pre-init: native <details name> still works (accessible default).
// =============================================================================

const ITEM = '.ds-accordion-module__item';
const TRIGGER = '.ds-accordion-module__trigger';
const PANEL = '.ds-accordion-module__panel';
const COLLAPSING = 'ds-accordion-module__item--collapsing';

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Read motion tokens from :root so CSS remains the single source of truth.
function motion() {
  const root = getComputedStyle(document.documentElement);
  const duration = parseFloat(root.getPropertyValue('--motion-duration-base')) || 250;
  const easing = root.getPropertyValue('--motion-ease-standard').trim() || 'ease';
  return { duration, easing };
}

function finish(item, panel) {
  item.style.height = '';
  item.style.overflow = '';
  panel.style.removeProperty('display');
  item.classList.remove(COLLAPSING);
  delete item.dataset.dsAnimating;
}

function setExpanded(item, expanded) {
  const trigger = item.querySelector(TRIGGER);
  if (trigger) trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
}

function openItem(item, panel) {
  setExpanded(item, true);
  if (prefersReducedMotion()) {
    item.open = true;
    return;
  }

  const { duration, easing } = motion();
  const collapsed = item.offsetHeight; // summary + item borders only

  item.dataset.dsAnimating = '1';
  item.style.overflow = 'hidden';
  item.style.height = `${collapsed}px`; // lock before reveal — no full-height flash
  item.open = true;
  const expanded = collapsed + panel.offsetHeight;

  const anim = item.animate(
    [{ height: `${collapsed}px` }, { height: `${expanded}px` }],
    { duration, easing },
  );
  anim.onfinish = () => finish(item, panel);
}

function closeItem(item, panel) {
  setExpanded(item, false);
  if (prefersReducedMotion()) {
    item.open = false;
    return;
  }

  const { duration, easing } = motion();
  const expanded = item.offsetHeight;
  const collapsed = expanded - panel.offsetHeight;

  item.dataset.dsAnimating = '1';
  item.classList.add(COLLAPSING); // CSS rotates the chevron back in sync
  item.style.overflow = 'hidden';

  const anim = item.animate(
    [{ height: `${expanded}px` }, { height: `${collapsed}px` }],
    { duration, easing },
  );
  anim.onfinish = () => {
    item.open = false; // collapse natively only once the height animation is done
    finish(item, panel);
  };
}

function closeGroupSiblings(item) {
  const group = item.dataset.dsGroup;
  if (!group) return;
  document
    .querySelectorAll(`${ITEM}[data-ds-group="${group}"]`)
    .forEach((sibling) => {
      if (sibling !== item && sibling.open && !sibling.dataset.dsAnimating) {
        closeItem(sibling, sibling.querySelector(PANEL));
      }
    });
}

function initAccordionItem(item) {
  if (item.dataset.dsInit) return;
  item.dataset.dsInit = '1';

  // Take exclusivity over from the native `name` grouping so we can animate
  // sibling closes instead of the browser snapping them shut.
  const name = item.getAttribute('name');
  if (name) {
    item.dataset.dsGroup = name;
    item.removeAttribute('name');
  }

  const trigger = item.querySelector(TRIGGER);
  const panel = item.querySelector(PANEL);
  if (!trigger || !panel) return;

  setExpanded(item, item.open); // sync initial state (handles server-rendered open)

  trigger.addEventListener('click', (event) => {
    event.preventDefault(); // we manage open state ourselves
    if (item.dataset.dsAnimating) return;

    if (item.open) {
      closeItem(item, panel);
    } else {
      closeGroupSiblings(item);
      openItem(item, panel);
    }
  });
}

export default function initAccordions(root = document) {
  root.querySelectorAll(ITEM).forEach(initAccordionItem);
}
