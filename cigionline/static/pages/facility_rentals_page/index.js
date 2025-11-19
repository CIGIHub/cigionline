import './css/facility_rentals_page.scss';

document.addEventListener('DOMContentLoaded', function () {
  const firstError = document.querySelector(
    '.field-errors, .invalid-feedback, .form-errors, .errorlist',
  );
  if (firstError) {
    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    // optional highlight
    firstError.classList.add('highlight-error');
    setTimeout(() => firstError.classList.remove('highlight-error'), 2000);
  }
});
