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
  // --- Guest registration (optional per event) ---
  const guestAddBtn = document.querySelector('[data-guest-add]');
  const guestContainer = document.querySelector('[data-guest-container]');
  const guestProto = document.querySelector('[data-guest-prototype]');
  const totalFormsInput = document.querySelector('input[name="guests-TOTAL_FORMS"]');

  const maxGuests = guestAddBtn ? Number(guestAddBtn.getAttribute('data-guest-max') || '0') : 0;

  const updateTotalForms = () => {
    if (!totalFormsInput || !guestContainer) return;
    const count = guestContainer.querySelectorAll('[data-guest-block]').length;
    totalFormsInput.value = String(count);
  };

  const renumberGuests = () => {
    if (!guestContainer) return;
    guestContainer.querySelectorAll('[data-guest-block]').forEach((block, i) => {
      const h = block.querySelector('h4');
      if (h) h.textContent = `Guest ${i + 1}`;
    });
  };

  const initConditionalWithin = (root) => {
    // Re-run conditional sync hooks for newly inserted guest blocks.
    root.querySelectorAll('[data-conditional-target]').forEach((toggle) => {
      const detailsName = toggle.getAttribute('data-conditional-target');
      // In guest formsets there may be multiple fields with the same suffix
      // (e.g. id_guests-0-foo__details, id_guests-1-foo__details).
      // Resolve relative to the same guest block to avoid finding the first one.
      const scope = toggle.closest('[data-guest-block]') || root;
      const detailsInput = scope.querySelector(`#id_${CSS.escape(detailsName)}`);
      if (!detailsInput) return;
      const wrapper = detailsInput.closest('.cigi-field')
        || detailsInput.closest('.w-field')
        || detailsInput.parentElement;
      const sync = (opts = {}) => {
        const { clearOnHide = false } = opts;
        const show = toggle.checked;
        if (wrapper) wrapper.style.display = show ? '' : 'none';
        if (!show && clearOnHide) detailsInput.value = '';
      };
      sync({ clearOnHide: false });
      toggle.addEventListener('change', () => sync({ clearOnHide: true }));
    });

    root.querySelectorAll("[data-conditional-select='1']").forEach((select) => {
      const targetName = select.getAttribute('data-conditional-target');
      const triggerValue = select.getAttribute('data-conditional-trigger-value') || 'Other';
      const scope = select.closest('[data-guest-block]') || root;
      const otherInput = scope.querySelector(`#id_${CSS.escape(targetName)}`);
      if (!otherInput) return;

      const wrapper = otherInput.closest('.cigi-field')
        || otherInput.closest('.field')
        || otherInput.parentElement;

      const sync = (opts = {}) => {
        const { clearOnHide = false } = opts;
        const show = (select.value || '').trim() === triggerValue;
        if (wrapper) wrapper.style.display = show ? '' : 'none';
        if (!show && clearOnHide) otherInput.value = '';
      };

      sync({ clearOnHide: false });
      select.addEventListener('change', () => sync({ clearOnHide: true }));
    });
  };

  const addGuest = () => {
    if (!guestAddBtn || !guestContainer || !guestProto || !totalFormsInput) return;

    const current = guestContainer.querySelectorAll('[data-guest-block]').length;
    if (Number.isFinite(maxGuests) && maxGuests > 0 && current >= maxGuests) return;

    const index = current;
    const tpl = guestProto.content.cloneNode(true);
    const wrapper = tpl.querySelector('[data-guest-block]');
    if (!wrapper) return;

    // Replace __prefix__ and ids to match Django formset naming.
    wrapper.querySelectorAll('[name]').forEach((el) => {
      el.name = el.name.replace(/guests-__prefix__/g, `guests-${index}`);
    });
    wrapper.querySelectorAll('[id]').forEach((el) => {
      el.id = el.id.replace(/id_guests-__prefix__/g, `id_guests-${index}`);
    });
    wrapper.querySelectorAll('label[for]').forEach((el) => {
      el.htmlFor = el.htmlFor.replace(/id_guests-__prefix__/g, `id_guests-${index}`);
    });

    // Update header
    const h = wrapper.querySelector('h4');
    if (h) h.textContent = `Guest ${index + 1}`;

    guestContainer.appendChild(wrapper);
    updateTotalForms();
    renumberGuests();
    // Initialize conditionals only within the newly added block.
    initConditionalWithin(wrapper);
  };

  const removeGuest = (btn) => {
    const block = btn.closest('[data-guest-block]');
    if (!block || !guestContainer) return;
    block.remove();
    updateTotalForms();
    renumberGuests();
  };

  if (guestAddBtn) {
    guestAddBtn.addEventListener('click', addGuest);
  }

  if (guestContainer) {
    guestContainer.addEventListener('click', (e) => {
      const t = e.target;
      if (t && t.matches('[data-guest-remove]')) {
        e.preventDefault();
        removeGuest(t);
      }
    });
    // Ensure TOTAL_FORMS is correct on initial load.
    updateTotalForms();
    initConditionalWithin(guestContainer);
  }

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
