// =============================================================================
// Design System — form error clearing
//
// Server-rendered field errors (.ds-form__field--error) clear as soon as the
// user starts typing in the field again (guide: Forms — error state). The
// red border / shake / message styling lives in components/_form.scss.
// =============================================================================

export default function initFormErrors(root = document) {
  root.querySelectorAll('.ds-form__field--error').forEach((field) => {
    if (field.dataset.dsErrorInit) return;
    field.dataset.dsErrorInit = '1';

    const clear = () => {
      field.classList.remove('ds-form__field--error');
      field.querySelectorAll('.ds-form__error').forEach((el) => el.remove());
    };
    field.addEventListener('input', clear, { once: true });
    field.addEventListener('change', clear, { once: true });
  });
}
