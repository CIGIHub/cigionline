// =============================================================================
// Design System — newsletter submit feedback
//
// Guide (Newsletter + Forms): the submit button swaps its label for a rotating
// spinner on submit. The newsletter forms navigate to /subscribe/, so the
// spinner covers the hand-off; markup (`.ds-spinner`) ships in the template and
// CSS (components/_spinner.scss) does the swap — this just flags the state.
// =============================================================================

let pageshowBound = false;

function clearSubmitting() {
  document.querySelectorAll('form[data-ds-subscribe].is-submitting').forEach((form) => {
    form.classList.remove('is-submitting');
    const button = form.querySelector('button[type="submit"]');
    if (button) button.removeAttribute('aria-busy');
  });
}

export default function initSubscribeForms(root = document) {
  // bfcache: browser Back restores the page with the submitting state still
  // applied — every subscribe button would spin forever. pageshow clears it.
  if (!pageshowBound) {
    pageshowBound = true;
    window.addEventListener('pageshow', clearSubmitting);
  }

  root.querySelectorAll('form[data-ds-subscribe]').forEach((form) => {
    if (form.dataset.dsInit) return;
    form.dataset.dsInit = '1';

    form.addEventListener('submit', () => {
      form.classList.add('is-submitting');
      const button = form.querySelector('button[type="submit"]');
      if (button) button.setAttribute('aria-busy', 'true');
    });
  });
}
