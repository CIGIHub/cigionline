// =============================================================================
// Design System — Events-router Date calendar (1253:39873)
// Enhances the Date facet's Month/Year selects with a Monday-first month grid:
// day cells are cloned from the <template data-router-day-template> (markup
// lives in the page template, not here), a click writes the hidden `day` input
// and fires a change so router.js refetches. "Today" jumps the calendar (and
// the filter) to today. No-JS: the selects still filter by month/year.
// =============================================================================

export default function initRouterCalendars(root = document) {
  root.querySelectorAll('[data-router-calendar]').forEach((cal) => {
    if (cal.dataset.dsInit) return;
    cal.dataset.dsInit = '1';

    // Bound by data hooks, not field names — the faceted-listing block
    // namespaces its field names with the per-instance prefix (BugHerd #135).
    const form = cal.closest('form');
    const monthSel = form.querySelector('select[data-router-month]');
    const yearSel = form.querySelector('select[data-router-year]');
    const dayInput = cal.querySelector('[data-router-day-input]');
    const grid = cal.querySelector('[data-router-calendar-grid]');
    const template = cal.querySelector('template[data-router-day-template]');
    if (!monthSel || !yearSel || !dayInput || !grid || !template) return;

    const today = new Date();

    const shownMonth = () => ({
      year: parseInt(yearSel.value, 10) || today.getFullYear(),
      month: parseInt(monthSel.value, 10) || today.getMonth() + 1,
    });

    const render = () => {
      const { year, month } = shownMonth();
      grid.textContent = '';
      const first = new Date(year, month - 1, 1);
      const lead = (first.getDay() + 6) % 7; // Monday-first offset
      const start = new Date(year, month - 1, 1 - lead);
      const daysInMonth = new Date(year, month, 0).getDate();
      const rows = Math.ceil((lead + daysInMonth) / 7);
      for (let i = 0; i < rows * 7; i += 1) {
        const date = new Date(start);
        date.setDate(start.getDate() + i);
        const cell = template.content.cloneNode(true);
        const btn = cell.querySelector('[data-router-day]');
        btn.textContent = date.getDate();
        const inMonth = date.getMonth() === month - 1;
        if (!inMonth) {
          btn.classList.add('is-outside');
          btn.disabled = true;
        } else {
          btn.dataset.day = String(date.getDate());
          if (String(date.getDate()) === dayInput.value) btn.classList.add('is-selected');
          if (date.toDateString() === today.toDateString()) btn.classList.add('is-today');
        }
        grid.appendChild(cell);
      }
    };

    const applyAndReload = () => {
      render();
      // router.js listens for form change; a bubbled change refetches in place.
      monthSel.dispatchEvent(new window.Event('change', { bubbles: true }));
    };

    grid.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-router-day]');
      if (!btn || !btn.dataset.day) return;
      // Toggle: clicking the selected day clears the day filter.
      dayInput.value = dayInput.value === btn.dataset.day ? '' : btn.dataset.day;
      // A day filter is only meaningful with a concrete month + year.
      if (dayInput.value) {
        const { year, month } = shownMonth();
        monthSel.value = String(month);
        yearSel.value = String(year);
      }
      applyAndReload();
    });

    // User-driven month/year change: the old day no longer applies.
    [monthSel, yearSel].forEach((sel) => {
      sel.addEventListener('change', (e) => {
        if (e.isTrusted) dayInput.value = '';
        render();
      });
    });

    const todayBtn = form.querySelector('[data-router-today]');
    if (todayBtn) {
      todayBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation(); // don't toggle the <details>
        monthSel.value = String(today.getMonth() + 1);
        yearSel.value = String(today.getFullYear());
        dayInput.value = String(today.getDate());
        applyAndReload();
      });
    }

    render();
  });
}
