// =============================================================================
// Design System — event countdown chip
//
// The date-proximity chip's number ticks into place on load — counting up from
// 0 to the rendered value with an ease-out settle (guide: Events Module). The
// server renders the final number, so no-JS and reduced-motion simply show it.
// Duration comes from the motion tokens (single source of truth).
// =============================================================================

export default function initCountdowns(root = document) {
  const nums = Array.from(root.querySelectorAll('[data-ds-countdown-num]')).filter(
    (el) => !el.dataset.dsInit,
  );
  if (!nums.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const rootStyle = window.getComputedStyle(document.documentElement);
  const duration = parseFloat(rootStyle.getPropertyValue('--motion-duration-media-fade')) || 400;

  nums.forEach((el) => {
    el.dataset.dsInit = '1';
    const target = parseInt(el.textContent, 10);
    if (!Number.isFinite(target) || target <= 0) return;

    const start = window.performance.now();
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - (1 - t) ** 3; // decelerate into place — no overshoot
      el.textContent = String(Math.round(target * eased));
      if (t < 1) window.requestAnimationFrame(tick);
    };
    el.textContent = '0';
    window.requestAnimationFrame(tick);
  });
}
