// =============================================================================
// Design System — Program Spotlight behaviour
//
// Progressive enhancement for [data-ds-program-spotlight]: the program list is
// a vertical ARIA tablist — one panel visible at a time, Up/Down/Home/End
// keyboard navigation — and the "Explore <program>" link tracks the selection
// (label + href from the active tab's data attributes). Without JS all panels
// are visible (accessible fallback).
// =============================================================================

let uid = 0;

// Theme filter (BugHerd #150, every width since #381). The active tile fills
// with the theme accent and the program list shows only that theme's programs.
// Desktop: nothing is active on load (every program listed); clicking a tile
// selects it, clicking it again clears the filter (Evan — never locked on).
// Mobile: the themes render as a swipeable carousel and the ACTIVE SLIDE
// drives the list; tapping a tile navigates to the theme page (Learn More
// carries the tap).
// The filter replaces the earlier desktop hover dim/lit (BugHerd #119, #487):
// the hovered theme's programs are the whole list now.
const MOBILE_QUERY = '(max-width: 768px)';
const THEME_ACTIVE = 'ds-program-spotlight__theme--active';

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function isMobile() {
  return window.matchMedia(MOBILE_QUERY).matches;
}

// Read motion tokens from :root so CSS stays the single source of truth (same
// contract as accordion.js — the list resize is the accordion's height tier).
function motion() {
  const root = window.getComputedStyle(document.documentElement);
  const duration = parseFloat(root.getPropertyValue('--motion-duration-base')) || 300;
  const easing = root.getPropertyValue('--motion-ease-standard').trim() || 'ease';
  return { duration, easing };
}

function activate(root, tabs, panels, index, animate) {
  tabs.forEach((tab, i) => {
    const selected = i === index;
    tab.setAttribute('aria-selected', selected ? 'true' : 'false');
    tab.setAttribute('tabindex', selected ? '0' : '-1');
    tab.classList.toggle('ds-program-spotlight__item--active', selected);
    panels[i].hidden = !selected;
    panels[i].classList.remove('ds-program-spotlight__panel--enter');
  });

  // User-driven switch: cross-fade the panel + stagger its cards (CSS handles
  // the keyframes + reduced-motion). The reflow restarts the animation each time.
  if (animate) {
    const panel = panels[index];
    void panel.offsetWidth;
    panel.classList.add('ds-program-spotlight__panel--enter');
  }

  const explore = root.querySelector('[data-ds-spotlight-explore]');
  if (explore) {
    explore.href = tabs[index].dataset.dsSpotlightUrl;
    const label = explore.querySelector('[data-ds-spotlight-explore-label]');
    if (label) label.textContent = tabs[index].dataset.dsSpotlightTitle;
  }

  // Mobile dropdown: keep the trigger label in sync, and close on selection.
  const dropdownLabel = root.querySelector('[data-ds-spotlight-dropdown-label]');
  if (dropdownLabel) dropdownLabel.textContent = tabs[index].dataset.dsSpotlightTitle;
  if (animate && root._dsSpotlightCloseDropdown) root._dsSpotlightCloseDropdown();
}

// Wire the themes row to the program list. Returns nothing; all state lives on
// the DOM so a resize can clear it.
function initThemeFilter(root, tabs, panels) {
  const list = root.querySelector('[data-ds-spotlight-list]');
  const cards = Array.from(root.querySelectorAll('[data-ds-spotlight-theme]'));
  if (!list || !cards.length) return;

  let activeThemeId = null;

  const apply = (themeId, animate) => {
    const before = list.offsetHeight;

    // A tab with no theme id belongs to no theme and stays visible.
    tabs.forEach((tab) => {
      const id = tab.dataset.dsSpotlightThemeId;
      tab.hidden = Boolean(themeId) && Boolean(id) && id !== themeId;
    });

    cards.forEach((card) => {
      const on = Boolean(themeId) && card.dataset.dsSpotlightThemeId === themeId;
      card.classList.toggle(THEME_ACTIVE, on);
      const toggle = card.querySelector('[data-ds-spotlight-theme-toggle]');
      if (toggle) toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    });

    activeThemeId = themeId;

    // Keep the visible panel in step with the filter.
    const firstVisible = tabs.findIndex((tab) => !tab.hidden);
    if (firstVisible !== -1) activate(root, tabs, panels, firstVisible, animate);

    if (!animate || prefersReducedMotion()) return;
    const after = list.offsetHeight;
    if (before === after) return;
    const { duration, easing } = motion();
    list.style.overflow = 'hidden';
    const anim = list.animate(
      [{ height: `${before}px` }, { height: `${after}px` }],
      { duration, easing },
    );
    anim.onfinish = () => { list.style.overflow = ''; };
  };

  // Swiping the themes carousel IS the filter (Evan, BugHerd #150 follow-up):
  // gallery-init's mobile rail re-emits Swiper's slideChange as a DOM event;
  // the active slide's theme drives the list. Tiles stay plain links — tapping
  // one navigates to the theme page, as on desktop.
  const rail = root.querySelector('[data-ds-spotlight-themes-rail]');
  const slides = rail ? Array.from(rail.querySelectorAll('[data-ds-spotlight-theme]')) : [];

  const railThemeId = () => {
    const active = rail && rail.querySelector('.swiper-slide-active[data-ds-spotlight-theme]');
    return (active || slides[0] || cards[0]).dataset.dsSpotlightThemeId;
  };

  if (rail) {
    rail.addEventListener('ds-carousel-slidechange', (event) => {
      const slide = slides[event.detail.index];
      if (!slide) return;
      const id = slide.dataset.dsSpotlightThemeId;
      if (id && id !== activeThemeId) apply(id, true);
    });
  }

  // Desktop: the tile's title button selects its theme (BugHerd #381). In the
  // rail the swipe is the filter, so the same button (keyboard-reachable only —
  // Learn More's stretched target covers the tap) slides the rail instead and
  // the slidechange event applies the filter.
  cards.forEach((card) => {
    const toggle = card.querySelector('[data-ds-spotlight-theme-toggle]');
    if (!toggle) return;
    toggle.addEventListener('click', () => {
      const id = card.dataset.dsSpotlightThemeId;
      if (!id) return;
      const slideIndex = slides.indexOf(card);
      const swiper = rail && rail.querySelector('.swiper') && rail.querySelector('.swiper').swiper;
      if (isMobile() && swiper && slideIndex !== -1) {
        swiper.slideTo(slideIndex);
        return;
      }
      apply(id === activeThemeId ? null : id, true);
    });
  });

  const syncBreakpoint = () => {
    if (isMobile()) {
      // Follow the rail's current slide (first theme on a fresh load).
      apply(railThemeId(), false);
    } else if (activeThemeId) {
      // Desktop starts unfiltered; the rail's slide must not carry across.
      apply(null, false);
    }
  };
  window.matchMedia(MOBILE_QUERY).addEventListener('change', syncBreakpoint);
  syncBreakpoint();
}

function initSpotlight(root) {
  if (root.dataset.dsInit) return;
  root.dataset.dsInit = '1';

  const tabs = Array.from(root.querySelectorAll('[data-ds-spotlight-tab]'));
  const panels = Array.from(root.querySelectorAll('[data-ds-spotlight-panel]'));
  if (!tabs.length || tabs.length !== panels.length) return;

  const initial = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
  activate(root, tabs, panels, initial === -1 ? 0 : initial, false);

  // Slider arrow: scrolls the program list to its bottom, then back to the top
  // once scrolled. The chevron flips to point up in the scrolled state. Shown
  // only when the list actually overflows.
  const list = root.querySelector('[data-ds-spotlight-list]');
  const scrollBtn = root.querySelector('[data-ds-spotlight-scroll]');
  if (list && scrollBtn && list.scrollHeight > list.clientHeight) {
    scrollBtn.hidden = false;

    const atBottom = () => list.scrollTop + list.clientHeight >= list.scrollHeight - 1;
    const sync = () => {
      const up = atBottom();
      scrollBtn.classList.toggle('ds-slider-arrow--up', up);
      scrollBtn.setAttribute('aria-label', up ? 'Scroll to top of program list' : 'Scroll to bottom of program list');
    };

    scrollBtn.addEventListener('click', () => {
      list.scrollTo({ top: atBottom() ? 0 : list.scrollHeight, behavior: 'smooth' });
    });
    list.addEventListener('scroll', sync);
    sync();
  }

  // Mobile dropdown: a disclosure that toggles the program list (which becomes a
  // popup in the mobile breakpoint). The tablist stays the no-JS / desktop UI, so
  // this only adds behaviour — visibility is the CSS media query's job.
  const trigger = root.querySelector('[data-ds-spotlight-dropdown]');
  const wrap = root.querySelector('[data-ds-spotlight-list-wrap]');
  if (trigger && list && wrap) {
    if (!list.id) { uid += 1; list.id = `ds-spotlight-list-${uid}`; }
    trigger.setAttribute('aria-controls', list.id);
    trigger.hidden = false;

    const setOpen = (open) => {
      wrap.toggleAttribute('data-ds-open', open);
      trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    root._dsSpotlightCloseDropdown = () => setOpen(false);

    trigger.addEventListener('click', (event) => {
      event.stopPropagation();
      setOpen(!wrap.hasAttribute('data-ds-open'));
    });
    document.addEventListener('click', (event) => {
      if (!wrap.contains(event.target)) setOpen(false);
    });
    root.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') { setOpen(false); trigger.focus(); }
    });
  }

  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => activate(root, tabs, panels, i, true));

    tab.addEventListener('keydown', (event) => {
      // Step over the visible tabs only — the mobile theme filter hides the
      // rest, and arrowing onto a hidden tab would move focus nowhere.
      const shown = tabs.filter((t) => !t.hidden);
      if (!shown.length) return;
      const pos = shown.indexOf(tab);
      let target = null;
      switch (event.key) {
        case 'ArrowDown': target = shown[(pos + 1) % shown.length]; break;
        case 'ArrowUp': target = shown[(pos - 1 + shown.length) % shown.length]; break;
        case 'Home': target = shown[0]; break;
        case 'End': target = shown[shown.length - 1]; break;
        default: return;
      }
      const next = tabs.indexOf(target);
      event.preventDefault();
      activate(root, tabs, panels, next, true);
      tabs[next].focus();
    });
  });

  initThemeFilter(root, tabs, panels);
}

export default function initProgramSpotlights(root = document) {
  // Scope to `root` so a spotlight inside a lazily-shown tab panel initialises;
  // initSpotlight's dataset.dsInit guard keeps re-runs idempotent.
  root.querySelectorAll('[data-ds-program-spotlight]').forEach(initSpotlight);
}
