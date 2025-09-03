import './css/dph.scss';

const mailingListButton = document.getElementById('mailing-list-button');
mailingListButton.addEventListener('click', () => {
  const input = document.getElementById('subscribe-email');
  input.scrollIntoView({
    behavior: 'smooth',
  });

  setTimeout(() => {
    input.focus();
  }, 600);
});

function initVariantContainerHeight(contentEl) {
  const active =
    contentEl.querySelector('.variant.is-active') ||
    contentEl.querySelector('.variant');
  if (active) {
    active.classList.add('is-active');
    requestAnimationFrame(() => {
      contentEl.style.height = `${active.offsetHeight}px`;
    });
  }
}

function wireCohortSelect(selectEl, contentEl) {
  selectEl.addEventListener('change', () => {
    const boxes = Array.from(contentEl.children);
    const nextIndex = Number(selectEl.value);
    const current =
      boxes.find((b) => b.classList.contains('is-active')) || boxes[0];
    const next = boxes[nextIndex] || boxes[0];
    if (current === next) return;

    contentEl.style.height = `${current.offsetHeight}px`;

    requestAnimationFrame(() => {
      current.classList.remove('is-active');
      next.classList.add('is-active');

      const nextHeight = next.offsetHeight;
      contentEl.style.height = `${nextHeight}px`;
    });

    const onEnd = (e) => {
      if (e.propertyName !== 'height') return;
      contentEl.style.height = `${next.offsetHeight}px`;
      contentEl.removeEventListener('transitionend', onEnd);
    };
    contentEl.addEventListener('transitionend', onEnd);
  });
}

function cohortTabs() {
  const stash = document.getElementById('cohort-variants');
  if (!stash) return;

  const variants = Array.from(stash.querySelectorAll('.cohort-variant'));
  if (!variants.length) return;

  const groups = new Map();
  for (const v of variants) {
    const title = v.dataset.title || 'People';
    const titleSlug = v.dataset.titleSlug || 'people';
    const cohort = v.dataset.cohort || '(Default)';
    const tmpl = v.querySelector('template');

    if (!groups.has(titleSlug)) {
      groups.set(titleSlug, { title, items: [] });
    }
    groups.get(titleSlug).items.push({ cohort, tmpl });
  }

  const tablist = document.getElementById('cohorts-tablist');
  const panels = document.getElementById('cohorts-panels');
  if (!tablist || !panels) return;

  let idx = 0;

  for (const [slug, group] of groups.entries()) {
    const btn = document.createElement('button');
    btn.className = `nav-link${idx === 0 ? ' active' : ''}`;
    btn.id = `${slug}-tab`;
    btn.type = 'button';
    btn.setAttribute('role', 'tab');
    btn.setAttribute('aria-selected', idx === 0 ? 'true' : 'false');
    btn.setAttribute('aria-controls', `${slug}-panel`);
    btn.dataset.cohortTitleSlug = slug;
    btn.textContent = group.title;
    tablist.appendChild(btn);

    const pane = document.createElement('div');
    pane.className = `tab-pane fade cohort-panel${
      idx === 0 ? ' show active' : ''
    }`;
    pane.id = `${slug}-panel`;
    pane.setAttribute('role', 'tabpanel');
    pane.setAttribute('aria-labelledby', `${slug}-tab`);
    pane.dataset.cohortTitleSlug = slug;

    const items = group.items;

    if (items.length > 1) {
      const seen = new Set();
      const deduped = [];
      for (const it of items) {
        if (!seen.has(it.cohort)) {
          seen.add(it.cohort);
          deduped.push(it);
        }
      }

      const toolbar = document.createElement('div');
      toolbar.className = 'toolbar';

      const label = document.createElement('label');
      label.className = 'sr-only';
      label.setAttribute('for', `${slug}-cohort`);
      label.textContent = `Select cohort for ${group.title}`;

      const select = document.createElement('select');
      select.id = `${slug}-cohort`;
      select.className = 'form-control form-select';
      select.dataset.cohortTitleSlug = slug;

      deduped.forEach((it, i) => {
        const opt = document.createElement('option');
        opt.value = String(i);
        opt.textContent = it.cohort;
        if (i === 0) opt.selected = true;
        select.appendChild(opt);
      });

      toolbar.appendChild(label);
      toolbar.appendChild(select);
      pane.appendChild(toolbar);

      const content = document.createElement('div');
      content.className = 'variants';
      initVariantContainerHeight(content);
      wireCohortSelect(select, content);
      content.dataset.cohortTitleSlug = slug;

      deduped.forEach((it, i) => {
        const variant = document.createElement('div');
        variant.className = `variant${i === 0 ? ' is-active' : ' is-hidden'}`;
        variant.dataset.cohort = it.cohort;
        variant.appendChild(it.tmpl.content.cloneNode(true));
        content.appendChild(variant);
      });

      pane.appendChild(content);

      select.addEventListener('change', () => {
        const selIndex = Number(select.value);
        const boxes = Array.from(content.children);
        boxes.forEach((box, i) => {
          box.classList.toggle('is-hidden', i !== selIndex);
        });
      });
    } else {
      const only = items[0];
      const content = document.createElement('div');
      content.className = 'variant';
      content.dataset.cohort = only.cohort;
      content.appendChild(only.tmpl.content.cloneNode(true));
      pane.appendChild(content);
    }

    panels.appendChild(pane);
    idx += 1;
  }

  tablist.addEventListener('click', (e) => {
    const btn = e.target.closest('button.nav-link');
    if (!btn) return;
    const slug = btn.dataset.cohortTitleSlug;

    tablist.querySelectorAll('.nav-link').forEach((b) => {
      const active = b === btn;
      b.classList.toggle('active', active);
      b.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    panels.querySelectorAll('.tab-pane').forEach((p) => {
      const show = p.dataset.cohortTitleSlug === slug;
      p.classList.toggle('show', show);
      p.classList.toggle('active', show);
    });
  });
}

function xfadeTo(container, nextPane) {
  const panes = Array.from(container.children);
  const current =
    panes.find((p) => p.classList.contains('is-active')) || panes[0];
  if (!nextPane || current === nextPane) return;
  const currentH = current.offsetHeight;
  container.style.height = currentH + 'px';
  current.classList.remove('is-active');
  current.classList.add('is-hidden');
  nextPane.classList.add('is-active');
  nextPane.classList.remove('is-hidden');
  const nextH = nextPane.offsetHeight;
  container.style.height = nextH + 'px';
  const onEnd = (e) => {
    if (e.propertyName !== 'height') return;
    container.style.height = 'auto';
    container.removeEventListener('transitionend', onEnd);
  };
  container.addEventListener('transitionend', onEnd);
}
function initXfade(container) {
  const panes = Array.from(container.children);
  if (!panes.length) return;
  const active =
    panes.find((p) => p.classList.contains('is-active')) || panes[0];
  panes.forEach((p) => {
    const isActive = p === active;
    p.classList.toggle('is-active', isActive);
    p.classList.toggle('is-hidden', !isActive);
  });
  requestAnimationFrame(() => {
    container.style.height = active.offsetHeight + 'px';
    setTimeout(() => {
      container.style.height = 'auto';
    }, 320);
  });
  container.querySelectorAll('img').forEach((img) => {
    img.addEventListener(
      'load',
      () => {
        const pane = container.querySelector('.xfade-pane.is-active');
        if (pane) container.style.height = pane.offsetHeight + 'px';
      },
      { once: true },
    );
  });
}

function pubsList() {
  // --- Build selects (keeps "All ..." as default) ---
  function populateTerms(select) {
    if (!select) return;
    const seen = new Set();
    const keepFirst =
      select.querySelector('option[value=""]') || new Option('All terms', '');
    select.innerHTML = '';
    select.appendChild(keepFirst);
    for (const el of items) {
      const slug = (el.dataset.term || '').trim();
      const label = (el.dataset.termLabel || slug || 'Uncategorized').trim();
      if (!slug || seen.has(slug)) continue;
      seen.add(slug);
      select.appendChild(new Option(label, slug));
    }
    select.value = '';
  }
  function populateTopics(select) {
    if (!select) return;
    const seen = new Set();
    const keepFirst =
      select.querySelector('option[value=""]') || new Option('All topics', '');
    select.innerHTML = '';
    select.appendChild(keepFirst);
    for (const el of items) {
      const topics = (el.dataset.topics || '')
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      for (const slug of topics) {
        if (seen.has(slug)) continue;
        seen.add(slug);
        const label = slug
          .replace(/-/g, ' ')
          .replace(/\b\w/g, (c) => c.toUpperCase());
        select.appendChild(new Option(label, slug));
      }
    }
    select.value = '';
  }

  const root = document.getElementById('publist');
  if (!root) return;

  const termSel = root.querySelector('#termFilter');
  const topicSel = root.querySelector('#topicFilter');
  const spinner = root.querySelector('.publist-spinner');
  const items = Array.from(
    root.querySelectorAll('.publications-list__publication'),
  );
  if (!items.length) return;

  populateTerms(termSel);
  populateTopics(topicSel);
  // Keep your existing population (or leave as is if server-filled):
  // populateTerms(termSel); populateTopics(topicSel);

  // Matching logic
  function matches(el, term, topic) {
    const elTerm = el.dataset.term || '';
    const elTopics = (el.dataset.topics || '').split(/\s+/).filter(Boolean);
    const termOk = !term || elTerm === term;
    const topicOk = !topic || elTopics.includes(topic);
    return termOk && topicOk;
  }

  let pendingTimer = null;

  function showSpinner() {
    spinner?.classList.add('is-visible');
  }
  function hideSpinner() {
    spinner?.classList.remove('is-visible');
  }

  function applyFilterWithLoading() {
    const term = termSel ? termSel.value.trim() : '';
    const topic = topicSel ? topicSel.value.trim() : '';

    // Cancel any in-flight reveal
    if (pendingTimer) {
      clearTimeout(pendingTimer);
      pendingTimer = null;
    }

    // Classify items once
    const toShow = [];
    const toHide = [];
    for (const el of items) {
      if (matches(el, term, topic)) toShow.push(el);
      else toHide.push(el);
    }

    const noResultsEl = root.querySelector('.publist-noresults');
    if (noResultsEl) {
      if (toShow.length === 0) noResultsEl.classList.remove('d-none');
      else noResultsEl.classList.add('d-none');
    }

    // Immediately hide non-matches (remove from flow)
    toHide.forEach((el) => {
      el.classList.add('is-hidden');
      el.classList.remove('will-fade');
      el.setAttribute('aria-hidden', 'true');
      el.style.transitionDelay = '';
    });

    // Prepare matches to reveal: ensure in flow but invisible (opacity 0)
    toShow.forEach((el) => {
      el.classList.remove('is-hidden');
      el.classList.add('will-fade');
      el.setAttribute('aria-hidden', 'false');
      el.style.transitionDelay = ''; // reset any old delay
    });

    // Show loading overlay for 1s
    showSpinner();
    const DELAY = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 0
      : 1000;

    pendingTimer = setTimeout(() => {
      hideSpinner();

      // Next frame: drop the "will-fade" class to animate to visible
      requestAnimationFrame(() => {
        // optional: deterministic tiny stagger
        toShow.forEach((el, i) => {
          const delay = Math.min(i * 20, 120); // cap at 120ms
          el.style.transitionDelay = delay ? `${delay}ms` : '';
        });

        toShow.forEach((el) => el.classList.remove('will-fade'));

        // clean up delays after transition
        const CLEANUP_AFTER = 240 + 130; // css duration + max stagger
        setTimeout(() => {
          toShow.forEach((el) => {
            el.style.transitionDelay = '';
          });
        }, CLEANUP_AFTER);
      });

      pendingTimer = null;
    }, DELAY);
  }

  // Defaults: "All terms" + "All topics"
  if (termSel) termSel.value = '';
  if (topicSel) topicSel.value = '';
  // Start with everything visible (no flicker)
  items.forEach((el) => {
    el.classList.remove('is-hidden', 'will-fade');
    el.setAttribute('aria-hidden', 'false');
  });

  termSel?.addEventListener('change', applyFilterWithLoading);
  topicSel?.addEventListener('change', applyFilterWithLoading);
}

pubsList();
cohortTabs();
