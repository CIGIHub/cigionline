// =============================================================================
// Design System — Router in-place filtering
// Faceted router forms ([data-ds-router-form]) filter without a full reload: on a
// facet/search/page change, refetch with an X-Requested-With header; the server
// returns just the results partial (JSON {html,total,…}), which we swap into
// [data-router-results] and push to the URL. No framework.
//
// Two modes:
//  - Page-level router (Events/Experts/Annual/SERP): one router per page, params
//    un-prefixed; we replace the querystring.
//  - Block-level faceted listing (.ds-router[data-router-prefix]): MANY listings
//    can share a page (e.g. the DPH hub's Cohort + Working Papers tabs). Each
//    owns a `<prefix>-*` param namespace; we MERGE its params into the current
//    querystring (preserving sibling routers' params + the active `tab`), read its
//    page cursor as `<prefix>-page`, and send `router=<prefix>` on the fetch so
//    the server dispatches to the right block (decisions D2/D4).
//
// Progressive enhancement: with no JS the GET form full-reloads and the pager
// links / Clear All are real <a href>s. The facet groups are native <details>.
// =============================================================================

// Deep link landing (Evan): a topic pill links to `?<prefix>-topic=<id>#router-<prefix>`
// (core/router_links.py). Land on that router, not the page top. Same contract
// as tabs.js's ?tab= landing: wait for window load (the hero media hasn't sized
// the layout at DOMContentLoaded), offset by the header element's height, one
// smooth scroll. The native fragment jump may already have moved the page, so
// this does not yield on scrollY — it corrects to the precise target.
let landed = false;
function landOnRouter(root) {
  if (landed) return;
  const hash = window.location.hash || '';
  if (!hash.startsWith('#router-')) return;
  const target = root.querySelector(`[id="${hash.slice(1)}"]`);
  if (!target) return;
  landed = true;
  const land = () => {
    const header = document.querySelector('[data-ds-header]');
    const top = target.getBoundingClientRect().top + window.scrollY
      - (header ? header.offsetHeight : 0);
    window.scrollTo({
      top,
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    });
  };
  if (document.readyState === 'complete') land();
  else window.addEventListener('load', land, { once: true });
}

// Page change → back to the top of the listing (Tim, BugHerd #537). The old
// results.scrollIntoView leaned on html's scroll-padding, which only clears the
// header: inside a Tabs block the sticky strip parks under the header and hid
// the first card row, and the heading + "Showing x–y" count sat above the grid
// out of view. Land the listing root just below ALL pinned chrome — the header
// and, in a Tabs panel, its strip — measured now, not hard-coded: a sticky
// element's pinned bottom is its `top` + its height (the strip sizes up on
// mobile; the header keeps one height in both chrome states).
//
// Only ever scrolls UP. "Already visible" = the listing's content box (the root
// below its section padding: heading, else count/grid) starts at or below the
// chrome; then the reader can already see where the new page begins, and a
// jump down would only yank them. When it starts behind or above the chrome,
// correct to the root's top so the section padding is restored above the
// heading. Instant under reduced motion, like every other DS scroll.
function scrollToListing(target) {
  const pinned = [document.querySelector('[data-ds-header]')];
  const tabs = target.closest('.ds-tabs');
  if (tabs) pinned.push(tabs.querySelector(':scope > .ds-tabs__bar'));
  const chrome = pinned.reduce((bottom, el) => {
    if (!el) return bottom;
    const style = window.getComputedStyle(el);
    if (style.position !== 'sticky' && style.position !== 'fixed') return bottom;
    return Math.max(bottom, (parseFloat(style.top) || 0) + el.offsetHeight);
  }, 0);
  const rootTop = target.getBoundingClientRect().top;
  const contentTop = rootTop + (parseFloat(window.getComputedStyle(target).paddingTop) || 0);
  if (contentTop >= chrome - 1) return; // 1px: sub-pixel layout rounding
  window.scrollTo({
    top: Math.max(0, window.scrollY + rootTop - chrome),
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
  });
}

// After a page swap the clicked pager link is gone and focus falls to <body>,
// so keyboard and screen-reader users restart from the page top (BugHerd #537).
// Move it to the start of the new page: the "Showing x–y of N" count where the
// listing has one (it names the new range — no aria-live on the count, so this
// is the only announcement), else the results region. preventScroll leaves the
// scroll to scrollToListing. Skipped if the reader focused something else
// while the fetch was in flight.
function focusNewPage(el, results) {
  const active = document.activeElement;
  if (active && active !== document.body && !results.contains(active)) return;
  if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
  el.focus({ preventScroll: true });
}

export default function initRouters(root = document) {
  landOnRouter(root);
  root.querySelectorAll('[data-ds-router-form]').forEach((form) => {
    if (form.dataset.dsInit) return;
    form.dataset.dsInit = '1';

    const scope = form.closest('.ds-router') || root;
    const results = scope.querySelector('[data-router-results]');
    const countEl = scope.querySelector('[data-router-count]');
    const search = form.querySelector('input[type="search"]');
    if (!results) return; // no swap target → native submit (full reload) still works

    const prefix = scope.dataset && scope.dataset.routerPrefix ? scope.dataset.routerPrefix : '';
    const pageParam = prefix ? `${prefix}-page` : 'page';
    const isMine = (key) => key.startsWith(`${prefix}-`); // only meaningful when prefix set

    // --- Mobile filters drawer (BugHerd #213) --------------------------------
    // The facets live in a slide-in panel under 769px. CSS owns the layout; this
    // only toggles --open and locks the page scroll behind it (same class the
    // nav drawer uses). Facet changes apply live, so both exits — the × and the
    // footer's Apply Filters (BugHerd #213) — just dismiss the panel. Hence
    // querySelectorAll: two controls carry data-router-drawer-close.
    const drawerToggle = form.querySelector('[data-router-drawer-toggle]');
    const drawerCloses = form.querySelectorAll('[data-router-drawer-close]');
    const setDrawer = (open) => {
      form.classList.toggle('ds-router__sidebar--open', open);
      document.body.classList.toggle('ds-no-scroll', open);
      if (drawerToggle) drawerToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open && drawerCloses.length) drawerCloses[0].focus();
      else if (!open && drawerToggle) drawerToggle.focus();
    };
    // Facets ship open (desktop wants them open); collapse them on mobile so the
    // drawer opens to a scannable list of labels (BugHerd #210). Done once at
    // init — the reader's own toggling afterwards is left alone.
    if (window.matchMedia('(max-width: 768px)').matches) {
      form.querySelectorAll('details.ds-router__facet[open]').forEach((d) => {
        d.removeAttribute('open');
      });
    }

    if (drawerToggle) drawerToggle.addEventListener('click', () => setDrawer(true));
    drawerCloses.forEach((btn) => btn.addEventListener('click', () => setDrawer(false)));
    form.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && form.classList.contains('ds-router__sidebar--open')) setDrawer(false);
    });
    // Leaving the mobile breakpoint with the drawer open would strand the lock.
    window.matchMedia('(max-width: 768px)').addEventListener('change', (e) => {
      if (!e.matches) setDrawer(false);
    });

    let token = 0;
    let searchTimer;
    let page = parseInt(new URLSearchParams(window.location.search).get(pageParam), 10) || 1;

    // Applied-filter chips: one <ul data-router-chips> per multi-select facet,
    // rebuilt from the facet's checked inputs (markup cloned from the
    // <template data-router-chip-template> — no markup authored here).
    const chipTemplate = form.querySelector('[data-router-chip-template]');
    const renderChips = () => {
      if (!chipTemplate) return;
      form.querySelectorAll('[data-router-chips]').forEach((list) => {
        const name = list.dataset.routerFacet;
        list.textContent = '';
        form.querySelectorAll(`input[name="${CSS.escape(name)}"]:checked`).forEach((input) => {
          const label = input.parentElement.querySelector('span');
          const li = chipTemplate.content.cloneNode(true);
          const chip = li.querySelector('[data-router-chip]');
          chip.dataset.chipName = name;
          chip.dataset.chipValue = input.value;
          chip.insertBefore(
            document.createTextNode(`${label ? label.textContent.trim() : input.value} `),
            chip.firstChild,
          );
          list.appendChild(li);
        });
      });
    };

    // Chip click → uncheck the matching input, back to page 1, refetch.
    form.addEventListener('click', (e) => {
      const chip = e.target.closest('[data-router-chip]');
      if (!chip) return;
      const name = chip.dataset.chipName || chip.closest('[data-router-chips]').dataset.routerFacet;
      const input = form.querySelector(
        `input[name="${CSS.escape(name)}"][value="${CSS.escape(chip.dataset.chipValue)}"]`,
      );
      if (input) input.checked = false;
      renderChips();
      page = 1;
      load();
    });

    // Search-within-facet (unnamed inputs — never submitted): client-side
    // filter of the option rows by label text.
    form.querySelectorAll('[data-router-facet-filter]').forEach((filter) => {
      filter.addEventListener('input', () => {
        const q = filter.value.trim().toLowerCase();
        filter
          .closest('.ds-router__facet')
          .querySelectorAll('.ds-router__options > li')
          .forEach((li) => {
            li.hidden = q !== '' && !li.textContent.toLowerCase().includes(q);
          });
      });
    });

    // Build the clean push URL + the fetch URL (adds router=<prefix> for dispatch).
    const buildUrls = () => {
      const params = new URLSearchParams();
      if (prefix) {
        // Keep everything that isn't ours (sibling routers + tab); drop our old
        // params + the AJAX-only `router` signal, then re-add ours from the form.
        new URLSearchParams(window.location.search).forEach((value, key) => {
          // Skip our own params, the page cursor, the AJAX-only `router` signal,
          // and `tab` — the form's hidden `tab` input (re-added by FormData below)
          // is the single source, so it isn't duplicated into the querystring.
          if (!isMine(key) && key !== pageParam && key !== 'router' && key !== 'tab') {
            params.append(key, value);
          }
        });
      }
      new FormData(form).forEach((value, key) => {
        if (value !== '') params.append(key, value);
      });
      if (page > 1) params.set(pageParam, page);

      const qs = params.toString();
      const pushUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;

      const fetchParams = new URLSearchParams(params);
      if (prefix) fetchParams.set('router', prefix);
      const fetchUrl = `${window.location.pathname}?${fetchParams.toString()}`;
      return { pushUrl, fetchUrl };
    };

    // `pager`: a pager-initiated load moves focus to the new page once it is in
    // (BugHerd #537); filter/search/chip/clear loads leave focus where it is.
    const load = (push = true, { pager = false } = {}) => {
      const mine = ++token;
      const { pushUrl, fetchUrl } = buildUrls();
      results.setAttribute('aria-busy', 'true');
      results.classList.add('is-loading');
      fetch(fetchUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then((r) => r.json())
        .then((data) => {
          if (mine !== token) return; // a newer request superseded this one
          results.innerHTML = data.html;
          if (countEl && typeof data.total === 'number') {
            const fmt = (n) => n.toLocaleString('en-US');
            const label =
              data.rangeStart === data.rangeEnd
                ? fmt(data.rangeStart)
                : `${fmt(data.rangeStart)}–${fmt(data.rangeEnd)}`;
            countEl.textContent = data.total
              ? `Showing ${label} of ${fmt(data.total)}`
              : 'No results';
          }
          // History contract (2026-07-03): filter/page changes update the URL
          // in place — the page stays ONE history entry; Back leaves the page.
          if (push) window.history.replaceState({ page }, '', pushUrl);
          if (pager) focusNewPage(countEl || results, results);
        })
        .catch(() => {
          /* leave current results in place on error */
        })
        .finally(() => {
          if (mine === token) {
            results.removeAttribute('aria-busy');
            results.classList.remove('is-loading');
          }
        });
    };

    // Facet (checkbox/radio/select) change → page 1, refetch.
    form.addEventListener('change', (e) => {
      if (e.target === search) return; // search handled on input (debounced)
      if (e.target.hasAttribute('data-router-facet-filter')) return; // client-side only
      // A parent option selects/deselects all of its children (1680:96033).
      if (e.target.hasAttribute('data-router-parent')) {
        e.target
          .closest('li')
          .querySelectorAll('.ds-router__children input')
          .forEach((child) => {
            child.checked = e.target.checked;
          });
      }
      renderChips();
      page = 1;
      load();
    });

    // Debounced free-text search.
    if (search) {
      search.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
          page = 1;
          load();
        }, 350);
      });
    }

    // Enter in the search field shouldn't full-reload.
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      page = 1;
      load();
    });

    const resetForm = () => {
      form.reset();
      form.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach((c) => {
        c.checked = false;
      });
      // form.reset() restores server-rendered selections — clear the date
      // controls explicitly (the hidden `tab` input is untouched).
      form.querySelectorAll('select').forEach((s) => {
        s.value = '';
      });
      const dayInput = form.querySelector('[data-router-day-input]');
      if (dayInput) dayInput.value = '';
      renderChips();
      page = 1;
      load();
    };

    // Pager + Clear All are inside the swapped region → delegate.
    results.addEventListener('click', (e) => {
      const pageLink = e.target.closest('.ds-pager a[href]');
      if (pageLink) {
        e.preventDefault();
        const p = parseInt(new URL(pageLink.href, window.location).searchParams.get(pageParam), 10);
        if (p) {
          page = p;
          load(true, { pager: true });
          // Scroll on click (target is above the swapped region, so the swap
          // doesn't move it). Pager only — filter changes never scroll.
          scrollToListing(form.closest('.ds-router') || results);
        }
        return;
      }
      if (e.target.closest('[data-router-clear]')) {
        e.preventDefault();
        resetForm();
      }
    });

    // Clear controls outside the results region: the bar's "Clear All" and the
    // mobile panel footer's "Clear Filters" (BugHerd #213). querySelectorAll —
    // with querySelector the bar's link matched first and the panel button got
    // no handler.
    scope.querySelectorAll('[data-router-clear]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        resetForm();
      });
    });

    // Back/forward: re-sync the form to the URL (only our prefixed inputs), refetch.
    window.addEventListener('popstate', () => {
      const sp = new URLSearchParams(window.location.search);
      form.querySelectorAll('input, select').forEach((el) => {
        if (!el.name) return;
        if (el.type === 'checkbox' || el.type === 'radio')
          el.checked = sp.getAll(el.name).includes(el.value);
        else el.value = sp.get(el.name) || '';
      });
      page = parseInt(sp.get(pageParam), 10) || 1;
      renderChips();
      load(false);
    });

    // Initial chips for facets checked on page load (templates render the
    // lists empty; the block template also server-renders a first pass).
    renderChips();
  });

  // Form-less listings (no filters/search authored) still get the AJAX pager
  // (John, BugHerd #332): the DPH Program Speakers tab full-reloaded while
  // its sibling tabs swapped in place. Same fetch contract as load() above,
  // pared to the page cursor — every other param passes through untouched.
  root.querySelectorAll('.ds-router[data-router-prefix]').forEach((scope) => {
    if (scope.dataset.dsPagerInit) return;
    if (scope.querySelector('[data-ds-router-form]')) return; // full wiring above
    const results = scope.querySelector('[data-router-results]');
    if (!results) return;
    scope.dataset.dsPagerInit = '1';
    const prefix = scope.dataset.routerPrefix;
    const pageParam = `${prefix}-page`;
    let token = 0;

    results.addEventListener('click', (e) => {
      const pageLink = e.target.closest('.ds-pager a[href]');
      if (!pageLink) return;
      e.preventDefault();
      const p = parseInt(new URL(pageLink.href, window.location).searchParams.get(pageParam), 10) || 1;
      const params = new URLSearchParams(window.location.search);
      params.delete('router');
      if (p > 1) params.set(pageParam, p);
      else params.delete(pageParam);
      const pushUrl = `${window.location.pathname}${params.toString() ? `?${params}` : ''}`;
      const fetchParams = new URLSearchParams(params);
      fetchParams.set('router', prefix);

      const mine = ++token;
      results.setAttribute('aria-busy', 'true');
      results.classList.add('is-loading');
      fetch(`${window.location.pathname}?${fetchParams}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then((r) => r.json())
        .then((data) => {
          if (mine !== token) return;
          results.innerHTML = data.html;
          // Same one-history-entry contract as load().
          window.history.replaceState({}, '', pushUrl);
          scrollToListing(scope);
          focusNewPage(results, results);
        })
        .catch(() => {
          /* leave current results in place on error */
        })
        .finally(() => {
          if (mine === token) {
            results.removeAttribute('aria-busy');
            results.classList.remove('is-loading');
          }
        });
    });
  });
}
