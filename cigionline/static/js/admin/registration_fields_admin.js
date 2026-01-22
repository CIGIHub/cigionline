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
          if (prevSpan && prevSpan !== heading.querySelector('.js-inline-title')) {
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
