// =============================================================================
// Primary header — mega-menu open/close, sticky scroll state, search expand.
// Panel triggers are links to their section landing page (BugHerd #282): the
// panel opens on hover and on keyboard focus; click navigates. A trigger with
// no authored destination (href "#") keeps click-to-toggle. One panel open at
// a time. Escape / click-outside / focus-leaving the header all close it.
// Compact panels are anchored under their trigger via a --panel-left var.
// The header pins at top 0 and holds the brand/nav row; the utility band above
// it scrolls away in normal flow. Once the band is gone the header gains
// `ds-header--scrolled`. The pinned height is published as
// --ds-header-pinned-height on :root so other sticky elements can clear it.
// The utility search rests collapsed and expands from the icon (guide:
// Primary Navigation).
// =============================================================================

export default function initHeader() {
  const header = document.querySelector('[data-ds-header]');
  if (!header) return;

  initScrollState(header);
  initSearchExpand();
  initDrawerSearchGuard(header);
  initMobileDrawer(header);

  const entries = Array.from(header.querySelectorAll('[data-ds-header-item]'))
    .map((li) => {
      const trigger = li.querySelector('.ds-header__link--has-panel');
      const panel = li.querySelector('[data-ds-header-panel]');
      return trigger && panel ? { li, trigger, panel } : null;
    })
    .filter(Boolean);
  if (!entries.length) return;

  const desktop = window.matchMedia('(min-width: 1255px)'); // matches the CSS burger breakpoint (BugHerd #53)
  let open = null;
  let hoverTimer = null;

  const positionCompact = (entry) => {
    if (!entry.panel.classList.contains('ds-header__panel--compact')) return;
    // Left-align under the trigger, but clamp so the fixed-width panel never
    // overflows the container's right gutter — a right-most panel shifts left
    // (BugHerd #46). Panel must be visible (unhidden) to measure its width.
    const sectionX =
      parseFloat(getComputedStyle(header).getPropertyValue('--space-section-x')) || 0;
    const maxLeft = Math.max(0, header.clientWidth - sectionX - entry.panel.offsetWidth);
    const left = Math.min(entry.li.offsetLeft, maxLeft);
    entry.panel.style.setProperty('--panel-left', `${left}px`);
  };

  const openPanel = (entry) => {
    if (open && open !== entry) closePanel(open);
    entry.trigger.setAttribute('aria-expanded', 'true');
    entry.panel.hidden = false;
    positionCompact(entry);
    open = entry;
  };

  const closePanel = (entry) => {
    entry.trigger.setAttribute('aria-expanded', 'false');
    entry.panel.hidden = true;
    if (open === entry) open = null;
  };

  entries.forEach((entry) => {
    // A click navigates (the trigger is a link). Only the "#" fallback —
    // a trigger with no authored landing page — keeps the old toggle.
    entry.trigger.addEventListener('click', (e) => {
      if (entry.trigger.getAttribute('href') !== '#') return;
      e.preventDefault();
      if (entry.panel.hidden) openPanel(entry);
      else closePanel(entry);
    });

    // Keyboard path: Enter now navigates, so the panel opens on focus to keep
    // its links reachable by Tab. focusout on the header closes it again.
    entry.trigger.addEventListener('focus', () => {
      if (!desktop.matches) return;
      clearTimeout(hoverTimer);
      openPanel(entry);
    });

    entry.li.addEventListener('mouseenter', () => {
      if (!desktop.matches) return;
      clearTimeout(hoverTimer);
      openPanel(entry);
    });
    entry.li.addEventListener('mouseleave', () => {
      if (!desktop.matches) return;
      clearTimeout(hoverTimer);
      hoverTimer = setTimeout(() => closePanel(entry), 120);
    });
  });

  header.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && open) {
      const { trigger } = open;
      closePanel(open);
      trigger.focus();
    }
  });

  header.addEventListener('focusout', () => {
    window.requestAnimationFrame(() => {
      if (open && !header.contains(document.activeElement)) closePanel(open);
    });
  });

  document.addEventListener('click', (e) => {
    if (open && !open.li.contains(e.target)) closePanel(open);
  });

  window.addEventListener('resize', () => {
    if (open) positionCompact(open);
  });

}

// --- Mobile drawer -----------------------------------------------------------
// The burger toggles the drawer (mobile/iPad primary nav). Wired separately from
// the desktop mega-menu panel setup so it runs even when the nav has no submenu
// items — the panel setup returns early in that case, which previously left the
// burger dead and the primary menu unopenable (BugHerd #52).
function initMobileDrawer(header) {
  const drawer = header.querySelector('[data-ds-drawer]');
  const openBtn = header.querySelector('[data-ds-drawer-open]');
  const closeBtn = header.querySelector('[data-ds-drawer-close]');
  if (!drawer || !openBtn) return;

  const setDrawer = (isOpen) => {
    drawer.hidden = !isOpen;
    openBtn.setAttribute('aria-expanded', String(isOpen));
    document.body.classList.toggle('ds-no-scroll', isOpen);
  };

  openBtn.addEventListener('click', () => {
    setDrawer(true);
    const firstFocusable = drawer.querySelector('input, a, button');
    if (firstFocusable) firstFocusable.focus();
  });
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      setDrawer(false);
      openBtn.focus();
    });
  }
  // Exclusive-open accordions (QA regroup, ticket #100): opening one drawer
  // section closes the others, so the list never stacks multiple open panels.
  drawer.addEventListener('toggle', (e) => {
    const opened = e.target;
    if (!(opened instanceof HTMLDetailsElement) || !opened.open) return;
    drawer.querySelectorAll('details[open]').forEach((d) => {
      if (d !== opened) d.open = false;
    });
  }, true); // toggle doesn't bubble — capture it

  drawer.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      setDrawer(false);
      openBtn.focus();
    }
    // Focus trap: the page behind is scroll-locked and inert; letting Tab
    // walk out strands keyboard users (and takes the Escape handler with
    // it). Cycle within the drawer.
    if (e.key === 'Tab') {
      const focusables = [...drawer.querySelectorAll(
        'a[href], button, input, select, textarea, summary, [tabindex="0"]',
      )].filter((el) => el.offsetParent !== null);
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
}

// --- Sticky scroll state -----------------------------------------------------
// Publishes the pinned header height and toggles `ds-header--scrolled` once the
// utility band above has scrolled away. The header pins the brand/nav row at
// `top: 0`, so its own height IS the pinned height — nothing here feeds the
// sticky offset any more (BugHerd #233).
function initScrollState(header) {
  const band = document.querySelector('[data-ds-header-band]');

  const measure = () => {
    document.documentElement.style.setProperty(
      '--ds-header-pinned-height',
      `${header.offsetHeight}px`,
    );
    return band ? band.offsetHeight : 0;
  };

  let bandHeight = measure();
  let ticking = false;

  const update = () => {
    ticking = false;
    header.classList.toggle('ds-header--scrolled', window.scrollY > bandHeight);
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

  window.addEventListener('resize', () => {
    bandHeight = measure();
    update();
  });

  update();
}

// --- Search expand -----------------------------------------------------------
// The utility search rests as its icon; clicking it expands the field (CSS
// transition) and focuses the input. A click with a query submits as normal;
// blur-empty and Escape collapse it. No-JS never gets `--collapsible`, so the
// field stays permanently open.
// The drawer's search shares the partial but not the collapsible behaviour.
// Its magnifier must not act as a link to the bare search page either: an
// empty tap focuses the field; a typed query still submits.
function initDrawerSearchGuard(header) {
  const form = header.querySelector('.ds-header__drawer-search .ds-header__search');
  if (!form) return;
  const input = form.querySelector('.ds-header__search-input');
  const button = form.querySelector('.ds-header__search-btn');
  if (!input || !button) return;

  button.addEventListener('click', (e) => {
    if (!input.value.trim()) {
      e.preventDefault();
      input.focus();
    }
  });
}

function initSearchExpand() {
  // The utility row is the band's child, not the header's (BugHerd #233).
  const form = document.querySelector('.ds-header__utility .ds-header__search');
  if (!form) return;

  const input = form.querySelector('.ds-header__search-input');
  const button = form.querySelector('.ds-header__search-btn');
  if (!input || !button) return;

  form.classList.add('ds-header__search--collapsible');

  // Collapsible is a desktop behaviour; the mobile header keeps the field
  // permanently open (BugHerd #97), so the button must submit right away there.
  const desktop = window.matchMedia('(min-width: 1255px)');

  const setOpen = (isOpen) => {
    form.classList.toggle('is-open', isOpen);
    button.setAttribute('aria-expanded', String(isOpen));
  };
  setOpen(false);

  button.addEventListener('click', (e) => {
    if (!desktop.matches) {
      // Mobile keeps the field permanently open. An empty tap on the icon
      // must not act as a link to the bare search page — it focuses the
      // field instead. A typed query still submits.
      if (!input.value.trim()) {
        e.preventDefault();
        input.focus();
      }
      return;
    }
    if (!form.classList.contains('is-open')) {
      e.preventDefault();
      setOpen(true);
      input.focus();
    } else if (!input.value.trim()) {
      e.preventDefault();
      setOpen(false);
    }
  });

  input.addEventListener('blur', () => {
    if (!input.value.trim()) setOpen(false);
  });

  form.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && form.classList.contains('is-open')) {
      input.value = '';
      setOpen(false);
      input.blur();
    }
  });
}
