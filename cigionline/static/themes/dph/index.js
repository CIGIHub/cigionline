import './css/dph.scss';

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
        if (i === 0) opt.selected = true; // default = first in DOM order
        select.appendChild(opt);
      });

      toolbar.appendChild(label);
      toolbar.appendChild(select);
      pane.appendChild(toolbar);

      const content = document.createElement('div');
      content.className = 'variants';
      content.dataset.cohortTitleSlug = slug;

      deduped.forEach((it, i) => {
        const variant = document.createElement('div');
        variant.className = `variant${i === 0 ? '' : ' is-hidden'}`;
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

function pubTabs() {
  const scope = document.querySelector('[data-filter-scope]');
  if (!scope) return;

  const sel = scope.querySelector('#termFilter');
  const items = Array.from(
    scope.querySelectorAll('.publications-list__publication'),
  );
  if (!items.length) return;

  // Build unique terms from DOM
  const termsMap = new Map(); // slug -> label
  items.forEach((el) => {
    const slug = (el.getAttribute('data-term') || '').trim();
    const label = (el.getAttribute('data-term-label') || '').trim();
    if (slug && label && !termsMap.has(slug)) termsMap.set(slug, label);
  });

  // Sort terms by label (customize as needed)
  const sorted = Array.from(termsMap.entries()).sort((a, b) =>
    a[1].localeCompare(b[1], undefined, { numeric: true }),
  );

  // Populate dropdown (after default "All terms")
  sorted.forEach(([slug, label]) => {
    const opt = document.createElement('option');
    opt.value = slug;
    opt.textContent = label;
    sel.appendChild(opt);
  });

  const qs = new URLSearchParams(location.search);
  const initial = qs.get('term') || '';
  if (initial && termsMap.has(initial)) sel.value = initial;

  const apply = (slug) => {
    items.forEach((el) => {
      const match = !slug || el.getAttribute('data-term') === slug;
      el.style.display = match ? '' : 'none';
    });

    // Update query string (no reload)
    const params = new URLSearchParams(location.search);
    if (slug) params.set('term', slug);
    else params.delete('term');
    const newUrl = `${location.pathname}${
      params.toString() ? '?' + params.toString() : ''
    }${location.hash}`;
    history.replaceState(null, '', newUrl);
  };

  sel.addEventListener('change', () => apply(sel.value));
  apply(initial);
}

cohortTabs();
pubTabs();
