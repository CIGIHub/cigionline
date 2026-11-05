// =============================================================================
// Design System — Tabs behaviour (ARIA tablist)
//
// Progressive enhancement for [data-ds-tabs]: one panel visible at a time, the
// rest hidden. WAI-ARIA tabs pattern — select, roving tabindex, Left/Right/Home/
// End keys. Without JS all panels are visible (accessible fallback).
//
// Composable Tabs ([data-ds-tabs-url], tab controls are <a href="?tab=slug">) add:
//  - URL tab state (decision D1): read ?tab= on load, replaceState ?tab=slug on
//    select, handle back/forward.
//  - Lazy router panels (decision D3): a panel whose faceted-listing rendered a
//    placeholder (.ds-router[data-router-lazy]) fetches its results on first show.
//  - A `ds:panel-shown` event on activation so the host re-runs DS inits scoped to
//    the panel (carousels re-measure now that it's visible, lazy-injected modules
//    wire up). See init-all.js.
// =============================================================================

function emitShown(panel) {
  panel.dispatchEvent(new CustomEvent('ds:panel-shown', { bubbles: true, detail: { panel } }));
}

// Fetch + inject the results for any lazy faceted-listing in a just-shown panel.
function loadLazyRouters(panel) {
  panel.querySelectorAll('.ds-router[data-router-lazy]').forEach((routerEl) => {
    const prefix = routerEl.dataset.routerPrefix;
    const results = routerEl.querySelector('[data-router-results]');
    if (!prefix || !results) { routerEl.removeAttribute('data-router-lazy'); return; }

    const params = new URLSearchParams(window.location.search);
    params.set('router', prefix);
    fetch(`${window.location.pathname}?${params.toString()}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then((r) => r.json())
      .then((data) => {
        results.innerHTML = data.html;
        const countEl = routerEl.querySelector('[data-router-count]');
        if (countEl && typeof data.total === 'number') {
          const label = data.rangeStart === data.rangeEnd
            ? `${data.rangeStart}` : `${data.rangeStart}–${data.rangeEnd}`;
          countEl.textContent = data.total ? `Showing ${label} of ${data.total}` : 'No results';
        }
        routerEl.removeAttribute('data-router-lazy');
        emitShown(panel); // results now in the DOM → wire router.js etc.
      })
      .catch(() => { routerEl.removeAttribute('data-router-lazy'); });
  });
}

function activate(group, tabs, panels, index, { focus = true, push = false } = {}) {
  tabs.forEach((tab, i) => {
    const selected = i === index;
    tab.setAttribute('aria-selected', selected ? 'true' : 'false');
    tab.setAttribute('tabindex', selected ? '0' : '-1');
    tab.classList.toggle('ds-tabs__tab--active', selected);
    panels[i].hidden = !selected;
  });
  const panel = panels[index];

  // The tab strip scrolls horizontally on mobile, so the active tab could sit
  // off-screen — on load from ?tab=, and after arrow-key navigation. Scroll the
  // STRIP (not scrollIntoView, which would also scroll the page) so the active
  // tab is centred in it, clamped to the ends (BugHerd #216).
  const strip = tabs[index].parentElement;
  if (strip && strip.scrollWidth > strip.clientWidth) {
    const tab = tabs[index];
    const target = tab.offsetLeft - (strip.clientWidth - tab.offsetWidth) / 2;
    const max = strip.scrollWidth - strip.clientWidth;
    strip.scrollTo({
      left: Math.max(0, Math.min(target, max)),
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    });
  }

  if (group.dataset.dsTabsUrl !== undefined && push) {
    const slug = tabs[index].dataset.tabSlug;
    if (slug) {
      // History contract (2026-07-03): tab switches keep the page as ONE
      // history entry (replaceState); merge into existing params so router
      // filter state in the URL survives a tab change.
      const params = new URLSearchParams(window.location.search);
      params.set('tab', slug);
      window.history.replaceState({ tab: slug }, '', `${window.location.pathname}?${params.toString()}`);
    }
  }

  if (group.dataset.dsTabsUrl !== undefined) {
    loadLazyRouters(panel);
  }
  emitShown(panel);
  if (focus) tabs[index].focus();

  // A tab chosen from deep in the previous panel would otherwise open partway
  // down the new one, because the strip is sticky and the swap keeps the
  // scroll offset (Tim, BugHerd #513). Bring the group's top back under the
  // header — only when the reader has scrolled past it, so a click near the
  // top of the page does not jump. Same offset rule as the ?tab= landing below.
  if (push) {
    const header = document.querySelector('[data-ds-header]');
    const top = group.getBoundingClientRect().top + window.scrollY
      - (header ? header.offsetHeight : 0);
    if (window.scrollY > top) {
      window.scrollTo({
        top,
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      });
    }
  }
}

function initTabGroup(group) {
  if (group.dataset.dsInit) return;
  group.dataset.dsInit = '1';

  const tabs = Array.from(group.querySelectorAll('[role="tab"]'));
  const panels = tabs.map((tab) =>
    group.querySelector(`#${CSS.escape(tab.getAttribute('aria-controls'))}`),
  );
  if (!tabs.length || panels.some((p) => !p)) return;

  // Initial tab: from ?tab= for URL-enabled groups, else the server-marked one.
  let initial = Math.max(0, tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true'));
  let landedOnTab = false;
  if (group.dataset.dsTabsUrl !== undefined) {
    const wanted = new URLSearchParams(window.location.search).get('tab');
    if (wanted) {
      const idx = tabs.findIndex((t) => t.dataset.tabSlug === wanted);
      if (idx !== -1) { initial = idx; landedOnTab = true; }
    }
  }
  activate(group, tabs, panels, initial === -1 ? 0 : initial, { focus: false });

  // Arriving on a ?tab= URL expresses intent to view that tab, so land at the
  // strip rather than the top of the page (BugHerd #287 — the DPH header
  // submenu links bypass the hero). The scroll waits for window load — at
  // DOMContentLoaded the hero media hasn't sized the layout yet — and yields
  // if the user scrolled first. Eased, per Evan: one smooth scroll to a
  // precomputed target. The offset is the header ELEMENT's height (constant
  // in both chrome states), not the pinned-height var — the var shrinks when
  // the page enters its scrolled state, and scrollIntoView is unreliable on
  // sticky elements.
  if (landedOnTab) {
    const bar = group.querySelector('.ds-tabs__bar');
    const land = () => {
      if (!bar || window.scrollY !== 0) return;
      const header = document.querySelector('[data-ds-header]');
      const top = bar.getBoundingClientRect().top + window.scrollY
        - (header ? header.offsetHeight : 0);
      window.scrollTo({ top, behavior: 'smooth' });
    };
    if (document.readyState === 'complete') land();
    else window.addEventListener('load', land, { once: true });
  }

  tabs.forEach((tab, i) => {
    tab.addEventListener('click', (event) => {
      event.preventDefault(); // tab controls may be <a href="?tab=slug">
      activate(group, tabs, panels, i, { focus: false, push: true });
    });

    tab.addEventListener('keydown', (event) => {
      let next = null;
      switch (event.key) {
        case 'ArrowRight': next = (i + 1) % tabs.length; break;
        case 'ArrowLeft': next = (i - 1 + tabs.length) % tabs.length; break;
        case 'Home': next = 0; break;
        case 'End': next = tabs.length - 1; break;
        default: return;
      }
      event.preventDefault();
      activate(group, tabs, panels, next, { push: true });
    });
  });

  // Back/forward through tab history (URL-enabled groups only).
  if (group.dataset.dsTabsUrl !== undefined) {
    window.addEventListener('popstate', () => {
      const wanted = new URLSearchParams(window.location.search).get('tab');
      const idx = wanted ? tabs.findIndex((t) => t.dataset.tabSlug === wanted) : 0;
      activate(group, tabs, panels, idx === -1 ? 0 : idx, { focus: false });
    });
  }
}

export default function initTabs(root = document) {
  root.querySelectorAll('[data-ds-tabs]').forEach(initTabGroup);
}
