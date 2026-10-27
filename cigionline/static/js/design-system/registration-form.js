// =============================================================================
// Design System — Event registration form (Event Form 1705:20332)
//
// Progressive enhancement for [data-ds-registration] (templates/events/
// registration_form.html). Three behaviours, ported from the legacy
// static/pages/event_page bundle (which the manage pages still load):
//   1. conditional fields — a yes/no toggle or a select's "Other" choice
//      reveals its "Please specify" detail field (server enforces the rule);
//   2. guests — add / remove / renumber guest blocks cloned from the server-
//      rendered <template data-guest-prototype>, keeping the formset's
//      TOTAL_FORMS in step;
//   3. file inputs — the chosen file name(s) in the field's meta span.
// No markup is authored here: blocks come from the template, the field
// wrapper is the ds-form contract's [data-ds-field].
// =============================================================================

const fieldWrapper = (input) => input && input.closest('[data-ds-field]');

// Formset inputs carry a prefix (guests-0-<name>); primary fields do not.
function findTargetInput(scope, rawName) {
  if (!rawName) return null;
  return (
    scope.querySelector(`#id_${CSS.escape(rawName)}`) ||
    scope.querySelector(`[id$='-${CSS.escape(rawName)}']`)
  );
}

function scopeOf(el) {
  return el.closest('[data-guest-block]') || el.closest('form') || document;
}

function reveal(input, show, clearOnHide) {
  const wrapper = fieldWrapper(input);
  if (wrapper) wrapper.hidden = !show;
  if (!show && clearOnHide) input.value = '';
}

function syncToggle(toggle, clearOnHide = false) {
  const details = findTargetInput(scopeOf(toggle), toggle.getAttribute('data-conditional-target'));
  if (details) reveal(details, toggle.checked, clearOnHide);
}

function syncSelectOther(select, clearOnHide = false) {
  const other = findTargetInput(scopeOf(select), select.getAttribute('data-conditional-target'));
  if (!other) return;
  const trigger = (select.getAttribute('data-conditional-trigger-value') || 'Other').trim();
  const show = select.multiple
    ? Array.from(select.selectedOptions).some((o) => (o.value || '').trim() === trigger)
    : (select.value || '').trim() === trigger;
  reveal(other, show, clearOnHide);
}

function syncConditionals(root) {
  root.querySelectorAll("[data-conditional-toggle='1']").forEach((t) => syncToggle(t));
  root.querySelectorAll("[data-conditional-select='1']").forEach((s) => syncSelectOther(s));
}

function initGuests(form) {
  const addBtn = form.querySelector('[data-guest-add]');
  const container = form.querySelector('[data-guest-container]');
  const proto = form.querySelector('[data-guest-prototype]');
  const total = form.querySelector('input[name="guests-TOTAL_FORMS"]');
  if (!addBtn || !container || !proto || !total) return;

  const max = Number(addBtn.getAttribute('data-guest-max') || '0');
  const blocks = () => container.querySelectorAll('[data-guest-block]');

  // Rewrite every formset reference in a block (name / id / for / aria-*) so
  // the block is guest `index`. Django's empty_form renders the __prefix__
  // placeholder; an existing block carries a real index that goes stale
  // once an earlier block is removed — the formset needs 0..N-1 contiguous
  // or it drops and merges submissions.
  const renumber = (block, index) => {
    const re = /guests-(?:__prefix__|\d+)-/g;
    const to = `guests-${index}-`;
    block.querySelectorAll('[name]').forEach((el) => { el.name = el.name.replace(re, to); });
    block.querySelectorAll('[id]').forEach((el) => { el.id = el.id.replace(re, to); });
    block.querySelectorAll('[for]').forEach((el) => { el.htmlFor = el.htmlFor.replace(re, to); });
    ['aria-labelledby', 'aria-describedby'].forEach((attr) => {
      block.querySelectorAll(`[${attr}]`).forEach((el) => {
        el.setAttribute(attr, el.getAttribute(attr).replace(re, to));
      });
    });
    const title = block.querySelector('[data-guest-title]');
    if (title) title.textContent = `Guest ${index + 1}`;
  };

  const sync = () => {
    blocks().forEach((block, i) => renumber(block, i));
    total.value = String(blocks().length);
    addBtn.hidden = max > 0 && blocks().length >= max;
  };

  const addGuest = () => {
    const index = blocks().length;
    if (max > 0 && index >= max) return;
    const fragment = proto.content.cloneNode(true);
    const block = fragment.querySelector('[data-guest-block]');
    if (!block) return;
    renumber(block, index);
    container.appendChild(block);
    sync();
    syncConditionals(block);
    const first = block.querySelector('input, select, textarea');
    if (first) first.focus();
  };

  addBtn.addEventListener('click', addGuest);
  container.addEventListener('click', (event) => {
    const remove = event.target.closest('[data-guest-remove]');
    if (!remove) return;
    event.preventDefault();
    const block = remove.closest('[data-guest-block]');
    if (block) block.remove();
    sync();
  });
  sync();
}

function initFileMeta(form) {
  form.addEventListener('change', (event) => {
    const input = event.target;
    if (!input.matches('input[type="file"]')) return;
    const holder = input.closest('.ds-form__file');
    const meta = holder && holder.querySelector('[data-ds-file-meta]');
    if (!meta) return;
    meta.textContent = Array.from(input.files || []).map((f) => f.name).join(', ');
  });
}

function initRegistration(root) {
  if (root.dataset.dsInit) return;
  root.dataset.dsInit = '1';
  const form = root.querySelector('form');
  if (!form) return;

  // Delegated, so guest blocks added later just work.
  form.addEventListener('change', (event) => {
    const t = event.target;
    if (t.matches("[data-conditional-toggle='1']")) syncToggle(t, true);
    if (t.matches("[data-conditional-select='1']")) syncSelectOther(t, true);
  });
  syncConditionals(form);
  initGuests(form);
  initFileMeta(form);

  // A failed POST re-renders at the top of the page with the first error a
  // screen or more below the hero — bring it into view and focus its control.
  const firstError = form.querySelector('.ds-form__field--error');
  if (firstError) {
    firstError.scrollIntoView({ block: 'center' });
    const control = firstError.querySelector('input, select, textarea');
    if (control) control.focus({ preventScroll: true });
  }
}

export default function initRegistrationForms(root = document) {
  root.querySelectorAll('[data-ds-registration]').forEach(initRegistration);
}
