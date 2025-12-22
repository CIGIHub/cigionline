import './css/facility_rentals_page.scss';

document.addEventListener('DOMContentLoaded', function () {
  const firstError = document.querySelector(
    '.field-errors, .invalid-feedback, .form-errors, .errorlist',
  );
  if (firstError) {
    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    firstError.classList.add('highlight-error');
    setTimeout(() => firstError.classList.remove('highlight-error'), 2000);
  }

  const otherWrapper = document.getElementById('space-other-wrapper');
  if (!otherWrapper) return;

  const otherCheckbox = document.querySelector(
    'input[name="space"][value="other"]',
  );
  if (!otherCheckbox) return;

  const toggleOther = () => {
    if (otherCheckbox.checked) {
      otherWrapper.style.display = '';
    } else {
      otherWrapper.style.display = 'none';
    }
  };

  toggleOther();

  otherCheckbox.addEventListener('change', toggleOther);
});
