// =============================================================================
// Design System — Scroll reveal (shared)
//
// Trigger-once scroll-entry animation via IntersectionObserver. Mark a container
// with [data-ds-reveal]; its [data-ds-reveal-item] children animate in, staggered
// (default 80ms, override with data-ds-reveal-stagger). If there are no item
// children, the container itself animates. The CSS lives in components/_reveal.
//
// Graceful by design: with no JS, no IntersectionObserver, or prefers-reduced-
// motion, nothing is hidden — content shows immediately. Spec: animation-guide.md
// (fade + 16px rise, 600ms entry).
// =============================================================================

const STEP_DEFAULT = 80;

function targetsOf(container) {
  const items = container.querySelectorAll('[data-ds-reveal-item]');
  return items.length ? Array.from(items) : [container];
}

function reveal(container, onLoad = false) {
  const step = parseInt(container.dataset.dsRevealStagger || STEP_DEFAULT, 10);
  targetsOf(container).forEach((el, i) => {
    // The on-load pass halves the stagger and runs the shorter fade
    // (_reveal.scss) — the landing view must not sit empty (BugHerd #260).
    el.style.transitionDelay = `${i * (onLoad ? step / 2 : step)}ms`;
    if (onLoad) el.classList.add('ds-reveal-load');
    el.classList.add('ds-reveal-in');
  });
}

// Inside a [data-ds-reveal-media] body (rich text — no per-node attributes),
// figures and pull quotes fade in place as each one enters the viewport —
// opacity only, no rise, so the reading experience stays physically still
// (guide: Publication + Long-form Reading). Nested matches defer to their
// outermost ancestor so a quote inside a figure doesn't double-fade.
const MEDIA_SELECTOR = 'figure, blockquote';

function mediaTargetsOf(host) {
  return Array.from(host.querySelectorAll(MEDIA_SELECTOR)).filter(
    (el) =>
      !el.parentElement.closest(MEDIA_SELECTOR) &&
      // DS modules embedded in the body run their own [data-ds-reveal]
      // entrance — their figures must not double-fade with the prose media.
      !el.closest('.ds-prose__module'),
  );
}

export default function initScrollReveal(root = document) {
  // Scope to `root` so reveals inside a lazily-shown tab panel initialise too;
  // dataset.dsInit makes re-running over already-wired containers a no-op.
  const containers = Array.from(root.querySelectorAll('[data-ds-reveal]')).filter(
    (c) => !c.dataset.dsInit,
  );
  const mediaHosts = Array.from(root.querySelectorAll('[data-ds-reveal-media]')).filter(
    (c) => !c.dataset.dsInit,
  );
  if (!containers.length && !mediaHosts.length) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return; // leave content visible

  // Hide just-before-reveal, only now that we know motion is allowed.
  containers.forEach((c) => {
    c.dataset.dsInit = '1';
    targetsOf(c).forEach((el) => el.classList.add('ds-reveal-pending'));
  });

  const io = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        reveal(entry.target);
        obs.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -10% 0px' },
  );

  // Anything already inside the first viewport reveals on load (Tim, BugHerd
  // #260 — a straddling container never met the 0.15 threshold, so the fold
  // sat empty). Everything below keeps the scroll-entry trigger.
  containers.forEach((c) => {
    if (c.getBoundingClientRect().top < window.innerHeight) {
      reveal(c, true);
    } else {
      io.observe(c);
    }
  });

  // Reading media fade — each element observed individually (they're spread
  // down a long article; a container-level trigger would fade them all at once).
  const mediaEls = [];
  mediaHosts.forEach((host) => {
    host.dataset.dsInit = '1';
    mediaTargetsOf(host).forEach((el) => {
      el.classList.add('ds-reveal-media-pending');
      mediaEls.push(el);
    });
  });
  if (!mediaEls.length) return;

  const ioMedia = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('ds-reveal-media-in');
        obs.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -10% 0px' },
  );

  mediaEls.forEach((el) => ioMedia.observe(el));
}
