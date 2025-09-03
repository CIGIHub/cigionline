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

function pubTabs() {
  const root = document.getElementById('publist');
  if (!root) return;

  const select = root.querySelector('#termFilter');
  const articles = Array.from(
    root.querySelectorAll('.publications-list__publication'),
  );

  if (!articles.length || !select) return;

  // Collect unique terms (preserve DOM order)
  const termMap = new Map(); // slug -> { label, nodes: [] }
  for (const art of articles) {
    const slug = (art.dataset.term || 'all').trim();
    const label = (art.dataset.termLabel || 'All terms').trim();
    if (!termMap.has(slug)) termMap.set(slug, { label, nodes: [] });
    termMap.get(slug).nodes.push(art);
  }

  // Populate the select (keep your existing "All terms" option on top)
  // (If you already populate server-side, you can skip this loop.)
  const existingValues = new Set(
    Array.from(select.options).map((o) => o.value),
  );
  for (const [slug, info] of termMap.entries()) {
    if (slug === 'all') continue; // avoid duplicate of default
    if (existingValues.has(slug)) continue;
    const opt = document.createElement('option');
    opt.value = slug;
    opt.textContent = info.label;
    select.appendChild(opt);
  }

  // Build panes wrapper
  const panes = document.createElement('div');
  panes.id = 'pub-panes';
  panes.className = 'xfade-container';

  // Pane: "All terms" (clone nodes so other panes can keep originals)
  const allPane = document.createElement('div');
  allPane.className = 'xfade-pane is-active'; // default active matches default select=""
  allPane.dataset.pane = 'all';
  const allFrag = document.createDocumentFragment();
  for (const art of articles) allFrag.appendChild(art.cloneNode(true));
  allPane.appendChild(allFrag);
  panes.appendChild(allPane);

  // Panes: one per term (move originals to save memory)
  for (const [slug, info] of termMap.entries()) {
    if (slug === 'all') continue;
    const pane = document.createElement('div');
    pane.className = 'xfade-pane';
    pane.dataset.pane = slug;

    const frag = document.createDocumentFragment();
    info.nodes.forEach((node) => frag.appendChild(node)); // move original nodes into this pane
    pane.appendChild(frag);

    panes.appendChild(pane);
  }

  // Insert panes and remove any leftover article shells
  // Keep the toolbar row (already inside #publist)
  // Remove any stray article wrappers still under #publist (we moved them)
  root
    .querySelectorAll('.publications-list__publication')
    .forEach((n) => n.remove());
  root.appendChild(panes);

  // Init animator
  initXfade(panes);

  // Wire filter -> cross-fade
  select.addEventListener('change', () => {
    const value = select.value.trim();
    const target = value ? value : 'all';
    const next = panes.querySelector(`.xfade-pane[data-pane="${target}"]`);
    if (next) xfadeTo(panes, next);
  });
}

cohortTabs();
pubTabs();
