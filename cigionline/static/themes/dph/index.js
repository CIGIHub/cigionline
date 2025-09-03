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
  const active = contentEl.querySelector('.variant.is-active')
    || contentEl.querySelector('.variant');
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
    const current = boxes.find((b) => b.classList.contains('is-active')) || boxes[0];
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

function pubsList() {
  const root = document.getElementById('publist');
  if (!root) return;

  const termDD = document.getElementById('termDropdown');
  const topicDD = document.getElementById('topicDropdown');
  const termBtn = termDD?.querySelector('.dropdown-toggle');
  const topicBtn = topicDD?.querySelector('.dropdown-toggle');
  const termList = termDD?.querySelector('.dropdown-menu ul');
  const topicList = topicDD?.querySelector('.dropdown-menu ul');
  const spinner = root.querySelector('.publist-spinner');
  const items = Array.from(
    root.querySelectorAll('.publications-list__publication'),
  );
  const noResultsEl = root.querySelector('.publist-noresults');
  if (!items.length) return;

  const terms = [];
  const seenTerms = new Set();
  items.forEach((el) => {
    const slug = (el.dataset.term || '').trim();
    const label = (el.dataset.termLabel || slug || '').trim();
    if (!slug) return;
    if (seenTerms.has(slug)) return;
    seenTerms.add(slug);
    terms.push({ value: slug, label: label || 'Uncategorized' });
  });

  const topics = [];
  const seenTopics = new Set();
  items.forEach((el) => {
    (el.dataset.topics || '')
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .forEach((slug) => {
        if (seenTopics.has(slug)) return;
        seenTopics.add(slug);
        const label = slug
          .replace(/-/g, ' ')
          .replace(/\b\w/g, (c) => c.toUpperCase());
        topics.push({ value: slug, label });
      });
  });

  function makeChoice(label, value) {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'dropdown-choice';
    btn.textContent = label;
    btn.setAttribute('role', 'menuitemradio');
    btn.setAttribute('aria-checked', 'false');
    btn.dataset.value = value;
    li.appendChild(btn);
    return li;
  }

  function populateMenu(listEl, itemsArr, allText) {
    if (!listEl) return;
    listEl.innerHTML = '';

    listEl.appendChild(makeChoice(allText, ''));
    itemsArr.forEach(({ label, value }) => listEl.appendChild(makeChoice(label, value)));
  }

  function openMenu(dd, btn) {
    const menu = dd.querySelector('.dropdown-menu');
    menu.classList.add('show');
    btn.setAttribute('aria-expanded', 'true');
  }
  function closeMenu(dd, btn) {
    const menu = dd.querySelector('.dropdown-menu');
    menu.classList.remove('show');
    btn.setAttribute('aria-expanded', 'false');
  }
  function setSelection(dd, btn, value, label) {
    btn.dataset.current = value;
    btn.textContent = label || btn.textContent;
    dd.querySelectorAll('.dropdown-choice').forEach((ch) => {
      const isSel = ch.dataset.value === value;
      ch.setAttribute('aria-selected', isSel ? 'true' : 'false');
      ch.setAttribute('aria-checked', isSel ? 'true' : 'false');
    });
  }

  function matches(el, term, topic) {
    const elTerm = el.dataset.term || '';
    const elTopics = (el.dataset.topics || '').split(/\s+/).filter(Boolean);
    const termOk = !term || elTerm === term;
    const topicOk = !topic || elTopics.includes(topic);
    return termOk && topicOk;
  }

  function showSpinner() {
    spinner?.classList.add('is-visible');
  }
  function hideSpinner() {
    spinner?.classList.remove('is-visible');
  }

  let pendingTimer = null;
  function applyFilterWithLoading() {
    const term = termBtn?.dataset.current || '';
    const topic = topicBtn?.dataset.current || '';

    if (pendingTimer) {
      clearTimeout(pendingTimer);
      pendingTimer = null;
    }

    const toShow = [];
    const toHide = [];
    items.forEach((el) => (matches(el, term, topic) ? toShow : toHide).push(el));

    if (noResultsEl) noResultsEl.classList.toggle('d-none', toShow.length > 0);

    toHide.forEach((el) => {
      el.classList.add('is-hidden');
      el.classList.remove('will-fade');
      el.setAttribute('aria-hidden', 'true');
      el.style.transitionDelay = '';
    });

    toShow.forEach((el) => {
      el.classList.remove('is-hidden');
      el.classList.add('will-fade');
      el.setAttribute('aria-hidden', 'false');
      el.style.transitionDelay = '';
    });

    if (toShow.length > 0) {
      showSpinner();
    }
    const DELAY = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 0
      : 500;

    pendingTimer = setTimeout(() => {
      hideSpinner();
      requestAnimationFrame(() => {
        toShow.forEach((el, i) => {
          const delay = Math.min(i * 20, 120);
          el.style.transitionDelay = delay ? `${delay}ms` : '';
        });
        toShow.forEach((el) => el.classList.remove('will-fade'));
        setTimeout(() => {
          toShow.forEach((el) => { el.style.transitionDelay = ''; });
        }, 240 + 130);
      });
      pendingTimer = null;
    }, DELAY);
  }
  populateMenu(termList, terms, 'All Terms');
  populateMenu(topicList, topics, 'All Topics');

  setSelection(termDD, termBtn, '', 'All Terms');
  setSelection(topicDD, topicBtn, '', 'All Topics');

  termBtn?.addEventListener('click', () => {
    const expanded = termBtn.getAttribute('aria-expanded') === 'true';
    closeMenu(topicDD, topicBtn);
    expanded ? closeMenu(termDD, termBtn) : openMenu(termDD, termBtn);
  });
  topicBtn?.addEventListener('click', () => {
    const expanded = topicBtn.getAttribute('aria-expanded') === 'true';
    closeMenu(termDD, termBtn);
    expanded ? closeMenu(topicDD, topicBtn) : openMenu(topicDD, topicBtn);
  });

  document.addEventListener('click', (e) => {
    if (!termDD.contains(e.target)) closeMenu(termDD, termBtn);
    if (!topicDD.contains(e.target)) closeMenu(topicDD, topicBtn);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeMenu(termDD, termBtn);
      closeMenu(topicDD, topicBtn);
    }
  });

  termList?.addEventListener('click', (e) => {
    const btn = e.target.closest('.dropdown-choice');
    if (!btn) return;
    const value = btn.dataset.value || '';
    const label = btn.textContent.trim();
    setSelection(termDD, termBtn, value, label);
    closeMenu(termDD, termBtn);
    applyFilterWithLoading();
  });
  topicList?.addEventListener('click', (e) => {
    const btn = e.target.closest('.dropdown-choice');
    if (!btn) return;
    const value = btn.dataset.value || '';
    const label = btn.textContent.trim();
    setSelection(topicDD, topicBtn, value, label);
    closeMenu(topicDD, topicBtn);
    applyFilterWithLoading();
  });

  items.forEach((el) => {
    el.classList.remove('is-hidden', 'will-fade');
    el.setAttribute('aria-hidden', 'false');
  });
  applyFilterWithLoading();
}

pubsList();
cohortTabs();
