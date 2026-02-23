import './css/policy_popup_group_page.scss';

document.addEventListener('DOMContentLoaded', () => {
  const bodyContent = document.querySelector('.body-content');
  const navList = document.querySelector('.section-nav-list');
  const docsBtn = document.querySelector('.section-nav-btn-docs');

  if (!bodyContent || !navList || !docsBtn) return;

  const h2s = Array.from(bodyContent.querySelectorAll('h2'));
  if (!h2s.length) return;

  const slugify = (text) =>
    text
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');

  // Assign IDs to all h2s that don't already have one
  h2s.forEach((h2) => {
    if (!h2.id) {
      h2.id = slugify(h2.textContent.trim());
    }
  });

  const docsH2 = h2s.find((h2) => /documents\s+and\s+research/i.test(h2.textContent.trim()));
  const navH2s = h2s.filter((h2) => h2 !== docsH2);

  // Update the docs button href and click behaviour
  if (docsH2) {
    docsBtn.setAttribute('href', `#${docsH2.id}`);
  }
  docsBtn.addEventListener('click', (e) => {
    if (docsH2) {
      e.preventDefault();
      docsH2.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  // Populate the nav list with the remaining h2s
  navH2s.forEach((h2) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `#${h2.id}`;
    // Use data-nav-label if set by SectionHeadingBlock, otherwise fall back to heading text
    a.textContent = h2.dataset.navLabel || h2.textContent.trim();
    a.addEventListener('click', (e) => {
      e.preventDefault();
      h2.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    li.appendChild(a);
    navList.appendChild(li);
  });

  const allH2s = docsH2 ? [docsH2, ...navH2s] : navH2s;
  const navItems = Array.from(navList.querySelectorAll('li'));

  const setActive = (activeH2) => {
    if (docsH2) {
      docsBtn.classList.toggle('active', activeH2 === docsH2);
    }
    navItems.forEach((li, i) => {
      li.classList.toggle('active', navH2s[i] === activeH2);
    });
  };

  // The active section is the last h2 whose top edge has passed 40% down the viewport
  const getActiveH2 = () => {
    const threshold = window.innerHeight * 0.4;
    let active = null;
    for (const h2 of allH2s) {
      if (h2.getBoundingClientRect().top <= threshold) {
        active = h2;
      }
    }
    return active;
  };

  window.addEventListener('scroll', () => setActive(getActiveH2()), {
    passive: true,
  });

  setActive(getActiveH2());

  // Inject an inline "[more +] / [more −]" toggle at the end of the last
  // paragraph in each collapsible block, instead of the default chevron button.
  const collapsibleBlocks = Array.from(
    bodyContent.querySelectorAll('.collapsible-paragraph-block'),
  );

  collapsibleBlocks.forEach((block) => {
    const headerP = block.querySelector('.collapsible-header p');
    if (!headerP) return;

    const span = document.createElement('span');
    span.className = 'collapsible-inline-toggle';
    span.textContent = block.classList.contains('collapsed') ? ' [more +]' : ' [more −]';

    span.addEventListener('click', (e) => {
      e.stopPropagation();
      block.classList.toggle('collapsed');
    });

    // Keep text in sync when the heading is also clicked (shared bundle toggles class)
    const observer = new MutationObserver(() => {
      span.textContent = block.classList.contains('collapsed') ? ' [more +]' : ' [more −]';
    });
    observer.observe(block, { attributes: true, attributeFilter: ['class'] });

    headerP.appendChild(span);
  });
});
