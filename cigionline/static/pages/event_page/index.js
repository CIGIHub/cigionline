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
    const wrapper =
      detailsInput.closest('.cigi-field') ||
      detailsInput.closest('.w-field') ||
      detailsInput.parentElement;

    const sync = () => {
      const show = toggle.checked;
      if (wrapper) wrapper.style.display = show ? '' : 'none';
      if (!show) detailsInput.value = '';
    };

    sync();
    toggle.addEventListener('change', sync);
  });
});
