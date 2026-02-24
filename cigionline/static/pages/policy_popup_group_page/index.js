import './css/policy_popup_group_page.scss';

document.addEventListener('DOMContentLoaded', () => {
  const bodyContent = document.querySelector('.body-content');
  const navList = document.querySelector('.section-nav-list');
  const docsBtn = document.querySelector('.section-nav-btn-docs');

  if (!bodyContent || !navList || !docsBtn) return;

  const h2s = Array.from(bodyContent.querySelectorAll('.section-heading-block h2'));
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

  // Footnote link tooltips — hover on pointer devices, tap-to-toggle on touch.
  // Finds all anchor links in .body-blocks that point to an element inside
  // .footnotes.
  const footnotesEl = document.querySelector('.footnotes');
  if (footnotesEl) {
    const tooltip = document.createElement('div');
    tooltip.className = 'footnote-tooltip';
    tooltip.setAttribute('role', 'tooltip');
    document.body.appendChild(tooltip);

    const positionTooltip = (anchorEl) => {
      const gap = 6;
      const rect = anchorEl.getBoundingClientRect();
      const tooltipWidth = tooltip.offsetWidth;
      const viewportWidth = window.innerWidth;
      let left = rect.left;
      if (left + tooltipWidth + gap > viewportWidth) {
        left = viewportWidth - tooltipWidth - gap;
      }
      tooltip.style.left = `${left}px`;
      // fixed uses viewport coords; absolute needs scrollY offset
      const scrollOffset = tooltip.style.position === 'absolute' ? window.scrollY : 0;
      tooltip.style.top = `${rect.bottom + scrollOffset + gap}px`;
    };

    const showTooltip = (anchorEl, displayEl) => {
      tooltip.innerHTML = '';
      const closeBtn = document.createElement('button');
      closeBtn.className = 'footnote-tooltip-close';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.textContent = '\u00d7';
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        hideTooltip();
      });
      tooltip.appendChild(closeBtn);
      tooltip.appendChild(displayEl.cloneNode(true));
      tooltip.classList.add('visible');
      positionTooltip(anchorEl);
    };

    const hideTooltip = () => tooltip.classList.remove('visible');

    const isTouch = window.matchMedia('(hover: none)').matches;

    if (!isTouch) {
      // --- Pointer/hover devices ---
      let hideTimer = null;
      const scheduleHide = () => {
        hideTimer = setTimeout(hideTooltip, 150);
      };
      const cancelHide = () => {
        if (hideTimer) {
          clearTimeout(hideTimer);
          hideTimer = null;
        }
      };
      tooltip.addEventListener('mouseenter', cancelHide);
      tooltip.addEventListener('mouseleave', scheduleHide);
      // Hide close button on hover devices
      tooltip.classList.add('no-close-btn');

      const footnoteLinks = Array.from(bodyContent.querySelectorAll('a[href^="#"]'));
      footnoteLinks.forEach((link) => {
        const targetId = link.getAttribute('href').slice(1);
        const target = footnotesEl.querySelector(`[name="${targetId}"]`);
        if (!target) return;
        let displayEl = target;
        while (displayEl.parentElement && displayEl.parentElement !== footnotesEl) {
          displayEl = displayEl.parentElement;
        }
        link.addEventListener('mouseenter', () => {
          cancelHide();
          showTooltip(link, displayEl);
        });
        link.addEventListener('mouseleave', scheduleHide);
      });
    } else {
      // --- Touch devices ---
      // Use position: absolute instead of fixed so positionTooltip can use scrollY offset.
      tooltip.style.position = 'absolute';

      let activeLink = null;

      // Tap outside to dismiss
      document.addEventListener('touchstart', (e) => {
        if (
          tooltip.classList.contains('visible') &&
          !tooltip.contains(e.target) &&
          e.target !== activeLink
        ) {
          hideTooltip();
          activeLink = null;
        }
      });

      const footnoteLinks = Array.from(bodyContent.querySelectorAll('a[href^="#"]'));
      footnoteLinks.forEach((link) => {
        const targetId = link.getAttribute('href').slice(1);
        const target = footnotesEl.querySelector(`[name="${targetId}"]`);
        if (!target) return;
        let displayEl = target;
        while (displayEl.parentElement && displayEl.parentElement !== footnotesEl) {
          displayEl = displayEl.parentElement;
        }
        link.addEventListener('click', (e) => {
          // If already open for this link, close it
          if (activeLink === link && tooltip.classList.contains('visible')) {
            hideTooltip();
            activeLink = null;
            return;
          }
          e.preventDefault();
          activeLink = link;
          showTooltip(link, displayEl);
        });
      });
    }
  }
});
