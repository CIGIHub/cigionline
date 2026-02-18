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
  // --- Registration page UX: smooth-scroll to the main interactive section ---
  // This nudges the user past the hero/banner so it's obvious the page changed.
  // Only runs on the registration subpages (types/form/manage/etc).
  const scrollTarget = document.querySelector(
    '.event-registration-type-select-section, .event-registration-form-section, .event-registration-result-section, .event-registration-no-types-section',
  );

  const shouldAutoscroll = () => {
    // Avoid fighting user intent (e.g., back/forward restoring scroll position).
    // Also avoid scrolling when a modal is open.
    if (!scrollTarget) return false;
    if (document.documentElement.classList.contains('has-open-modal')) return false;

    const navEntries = performance.getEntriesByType?.('navigation');
    const navType = navEntries && navEntries.length ? navEntries[0].type : null;
    if (navType === 'back_forward') return false;

    // If URL has a hash, let the browser handle that.
    if (window.location.hash) return false;

    // If we're already at/near the target, do nothing.
    const rect = scrollTarget.getBoundingClientRect();
    if (rect.top >= -8 && rect.top <= 120) return false;

    return true;
  };

  if (shouldAutoscroll()) {
    // Defer one tick so layout/images settle a bit before measuring.
    window.setTimeout(() => {
      scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }

  // --- Modal helpers (used for cancel confirmation on manage pages) ---
  let activeModal = null;
  let lastActiveElement = null;

  const getModalById = (id) => (id ? document.getElementById(id) : null);

  const getFocusable = (root) => {
    if (!root) return [];
    return Array.from(
      root.querySelectorAll(
        'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])',
      ),
    ).filter((el) => el.offsetParent !== null);
  };

  const closeModal = (modal) => {
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.documentElement.classList.remove('has-open-modal');

    if (activeModal === modal) activeModal = null;

    // Restore focus to the element that opened the modal.
    if (lastActiveElement && typeof lastActiveElement.focus === 'function') {
      lastActiveElement.focus();
    }
    lastActiveElement = null;
  };

  const openModal = (modal) => {
    if (!modal) return;

    // Close any existing modal first.
    if (activeModal && activeModal !== modal) closeModal(activeModal);

    lastActiveElement = document.activeElement;
    activeModal = modal;

    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.documentElement.classList.add('has-open-modal');

    // Focus first focusable element in dialog.
    const dialog = modal.querySelector('.cigi-modal__dialog') || modal;
    const focusables = getFocusable(dialog);
    (focusables[0] || dialog).focus?.();
  };

  // Open modal
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-modal-open]');
    if (!btn) return;
    const id = btn.getAttribute('data-modal-open');
    const modal = getModalById(id);
    if (!modal) return;
    e.preventDefault();
    openModal(modal);
  });

  // Close modal
  document.addEventListener('click', (e) => {
    const closeBtn = e.target.closest('[data-modal-close]');
    if (!closeBtn) return;
    const modal = e.target.closest('.cigi-modal');
    if (!modal) return;
    e.preventDefault();
    closeModal(modal);
  });

  // Confirm action: submit the first form that contains the opener for this modal
  document.addEventListener('click', (e) => {
    const submitBtn = e.target.closest('[data-modal-submit]');
    if (!submitBtn) return;
    const id = submitBtn.getAttribute('data-modal-submit');
    const modal = getModalById(id);
    if (!modal) return;
    e.preventDefault();
    // The templates place the modal right after the form.
    const form = modal.previousElementSibling?.tagName === 'FORM' ? modal.previousElementSibling : null;
    if (form) form.submit();
    else closeModal(modal);
  });

  // ESC to close + basic focus trap
  document.addEventListener('keydown', (e) => {
    if (!activeModal) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      closeModal(activeModal);
      return;
    }

    if (e.key !== 'Tab') return;
    const dialog = activeModal.querySelector('.cigi-modal__dialog') || activeModal;
    const focusables = getFocusable(dialog);
    if (!focusables.length) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

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

  const findTargetInput = (scope, rawName) => {
    if (!rawName) return null;
    // Prefer ID produced by non-formset fields.
    let el = scope.querySelector(`#id_${CSS.escape(rawName)}`);
    // Formsets: id includes prefix (e.g., id_guests-0-<rawName>).
    if (!el) el = scope.querySelector(`[id$='-${CSS.escape(rawName)}']`);
    return el;
  };

  const getFieldWrapper = (input) => (
    input?.closest('.cigi-field')
    || input?.closest('.w-field')
    || input?.closest('.field')
    || input?.parentElement
  );

  const syncConditionalToggle = (toggleEl, opts = {}) => {
    const { clearOnHide = false } = opts;
    const detailsName = toggleEl.getAttribute('data-conditional-target');
    const scope = toggleEl.closest('[data-guest-block]') || toggleEl.closest('form') || document;
    const detailsInput = findTargetInput(scope, detailsName);
    if (!detailsInput) return;
    const wrapper = getFieldWrapper(detailsInput);
    const show = !!toggleEl.checked;
    if (wrapper) wrapper.style.display = show ? '' : 'none';
    if (!show && clearOnHide) detailsInput.value = '';
  };

  const syncConditionalSelectOther = (selectEl, opts = {}) => {
    const { clearOnHide = false } = opts;
    const targetName = selectEl.getAttribute('data-conditional-target');
    const triggerValue = selectEl.getAttribute('data-conditional-trigger-value') || 'Other';
    const scope = selectEl.closest('[data-guest-block]') || selectEl.closest('form') || document;
    const otherInput = findTargetInput(scope, targetName);
    if (!otherInput) return;
    const wrapper = getFieldWrapper(otherInput);
    const show = (selectEl.value || '').trim() === triggerValue;
    if (wrapper) wrapper.style.display = show ? '' : 'none';
    if (!show && clearOnHide) otherInput.value = '';
  };

  const initConditionalsIn = (root) => {
    root.querySelectorAll('[data-conditional-target]').forEach((t) => syncConditionalToggle(t));
    root.querySelectorAll("[data-conditional-select='1']").forEach((s) => syncConditionalSelectOther(s));
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
    // Sync conditionals only within the newly added block.
    initConditionalsIn(wrapper);
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
    initConditionalsIn(guestContainer);
  }

  // Delegated conditional handling so dynamically-added guest blocks Just Work.
  const formEl = document.querySelector('form.cigi-form') || document.querySelector('form');
  if (formEl) {
    formEl.addEventListener('change', (e) => {
      const t = e.target;
      if (!t) return;
      if (t.matches('[data-conditional-target]')) {
        syncConditionalToggle(t, { clearOnHide: true });
      }
      if (t.matches("[data-conditional-select='1']")) {
        syncConditionalSelectOther(t, { clearOnHide: true });
      }
    });

    // Initial sync for primary + any server-rendered guests.
    initConditionalsIn(formEl);
  }
});
