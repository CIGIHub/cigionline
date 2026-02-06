import './css/event_page.scss';

document.addEventListener('change', function (e) {
  if (e.target.matches('.cigi-form input[type="file"]')) {
    const meta = e.target.closest('.cigi-file')?.querySelector('.file-meta');
    if (!meta) return;
    if (e.target.files && e.target.files.length) {
      const names = Array.from(e.target.files).map((f) => f.name);
      meta.textContent = names.join(', ');
    } else {
      meta.textContent = '';
    }
  }
});

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-conditional-target]').forEach((toggle) => {
    const detailsName = toggle.getAttribute('data-conditional-target');
    const detailsInput = document.getElementById(`id_${detailsName}`);
    if (!detailsInput) return;

    // Prefer a wrapper if you have one; fallback to parent
    const wrapper = detailsInput.closest('.cigi-field')
      || detailsInput.closest('.w-field')
      || detailsInput.parentElement;

    const sync = (opts = {}) => {
      const { clearOnHide = false } = opts;
      const show = toggle.checked;
      if (wrapper) wrapper.style.display = show ? '' : 'none';
      // Don't clear on initial load or we can wipe server-provided initial values
      // (notably on the manage-registration page).
      if (!show && clearOnHide) detailsInput.value = '';
    };

    sync({ clearOnHide: false });
    toggle.addEventListener('change', () => sync({ clearOnHide: true }));
  });

  document
    .querySelectorAll("[data-conditional-select='1']")
    .forEach((select) => {
      const targetName = select.getAttribute('data-conditional-target');
      const triggerValue = select.getAttribute('data-conditional-trigger-value') || 'Other';
      const otherInput = document.getElementById(`id_${targetName}`);
      if (!otherInput) return;

      const wrapper = otherInput.closest('.cigi-field')
        || otherInput.closest('.field')
        || otherInput.parentElement;

      const sync = (opts = {}) => {
        const { clearOnHide = false } = opts;
        const show = (select.value || '').trim() === triggerValue;
        if (wrapper) wrapper.style.display = show ? '' : 'none';
        // Same idea: keep any server-rendered initial value on load.
        if (!show && clearOnHide) otherInput.value = '';
      };

      sync({ clearOnHide: false });
      select.addEventListener('change', () => sync({ clearOnHide: true }));
    });
});
