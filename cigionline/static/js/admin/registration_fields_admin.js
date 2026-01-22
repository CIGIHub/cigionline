function init() {
  document
    .querySelectorAll('.js-registration-fields-inline')
    .forEach((root) => {
      const items = root.querySelectorAll(
        '.w-inline-panel__item, .c-inline-panel__item, .sequence-member, .w-panel',
      );

      items.forEach((item) => {
        const labelInput = item.querySelector('input[name$="-label"]');
        const typeSelect = item.querySelector('select[name$="-field_type"]');

        if (!labelInput && !typeSelect) return;

        const update = () => {
          const label =
            labelInput && labelInput.value.trim()
              ? labelInput.value.trim()
              : 'Untitled field';
          const type =
            typeSelect && typeSelect.selectedOptions.length
              ? typeSelect.selectedOptions[0].textContent.trim()
              : '';
          const text = type ? `${label} — ${type}` : label;

          const heading =
            item.querySelector('.c-sf-panel__title') ||
            item.querySelector('.sequence-member__title') ||
            item.querySelector('summary') ||
            item.querySelector('h2, h3');

          if (!heading) return;

          let prevSpan = heading.querySelector('span');
          if (
            prevSpan &&
            prevSpan !== heading.querySelector('.js-inline-title')
          ) {
            prevSpan.remove();
          }

          let span = heading.querySelector('.js-inline-title');
          if (!span) {
            span = document.createElement('span');
            span.className = 'js-inline-title';
            heading.prepend(span);
            span.style.marginRight = '0.5rem';
          }
          span.textContent = text;
        };

        update();
        if (labelInput) labelInput.addEventListener('input', update);
        if (typeSelect) typeSelect.addEventListener('change', update);
      });
    });
}

document.addEventListener('DOMContentLoaded', init);

function toggleConditionalSettingsForItem(item) {
  const typeSelect = item.querySelector('select[name$="-field_type"]');
  if (!typeSelect) return;

  const val = (typeSelect.value || '').trim();

  const showFields = (suffixes, shouldShow) => {
    suffixes.forEach((suffix) => {
      const input =
        item.querySelector(`input[name$="-${suffix}"]`) ||
        item.querySelector(`select[name$="-${suffix}"]`) ||
        item.querySelector(`textarea[name$="-${suffix}"]`);

      if (!input) return;

      const container =
        input.closest('.w-panel__wrapper') ||
        input.closest('.w-field__wrapper') ||
        input.closest('.w-field') ||
        input.parentElement;

      if (!container) return;

      container.style.display = shouldShow ? '' : 'none';
    });
  };

  const showGroupHeading = (headingText, shouldShow) => {
    const h = Array.from(item.querySelectorAll('h3.w-field__label')).find(
      (el) => (el.textContent || '').trim() === headingText,
    );
    if (!h) return;
    const section = h.closest('.w-panel__wrapper');
    if (!section) return;
    section.style.display = shouldShow ? '' : 'none';
  };

  // ---- Conditional groups
  const isConditionalText = val === 'conditional_text';
  const isConditionalOther = val === 'conditional_dropdown_other';

  // Show/hide the "group" wrappers if present
  showGroupHeading('Conditional form settings', isConditionalText);
  showGroupHeading("Conditional 'Other' settings", isConditionalOther);

  // Show/hide underlying fields too (in case the group wrapper isn't there)
  showFields(
    [
      'conditional_label',
      'conditional_details_label',
      'conditional_details_help_text',
      'conditional_details_required',
    ],
    isConditionalText,
  );

  showFields(
    [
      'conditional_other_value',
      'conditional_other_label',
      'conditional_other_help_text',
      'conditional_other_required',
    ],
    isConditionalOther,
  );

  // ---- Choices: only for choice-y types
  const needsChoices = new Set([
    'dropdown',
    'radio',
    'checkboxes',
    'multiselect',
    'conditional_dropdown_other',
  ]).has(val);

  showFields(['choices'], needsChoices);

  // ---- Default value: show only where it makes sense
  const needsDefaultValue = new Set([
    'singleline',
    'multiline',
    'email',
    'number',
    'url',
    'date',
    'datetime',
    'dropdown',
    'radio',
    'hidden',
  ]).has(val);

  showFields(['default_value'], needsDefaultValue);
}

function initConditionalAdminUI() {
  document
    .querySelectorAll('.js-registration-fields-inline')
    .forEach((root) => {
      const items = root.querySelectorAll(
        '.w-inline-panel__item, .c-inline-panel__item, .sequence-member, .w-panel',
      );

      items.forEach((item) => {
        const typeSelect = item.querySelector('select[name$="-field_type"]');
        if (!typeSelect) return;

        // initial
        toggleConditionalSettingsForItem(item);

        // on change
        typeSelect.addEventListener('change', () => {
          toggleConditionalSettingsForItem(item);
        });
      });
    });
}

document.addEventListener('DOMContentLoaded', initConditionalAdminUI);

// Re-run after adding a new inline row
document.addEventListener('click', (e) => {
  const addBtn = e.target.closest(
    '.chooser__choose-button',
  );
  console.log(addBtn);
  if (!addBtn) return;

  setTimeout(() => {
    initConditionalAdminUI();
  }, 150);
});
