import './css/think7.scss';

$(function () {
  document.getElementById('open-menu-btn').addEventListener('click', function (e) {
    e.stopPropagation();
    this.classList.toggle('open');

    const dropdownMenu = document.getElementById('dropdown-menu');
    dropdownMenu.classList.toggle('show');

    // Optionally update the aria-expanded attribute for accessibility
    const isExpanded = this.getAttribute('aria-expanded') === 'true';
    this.setAttribute('aria-expanded', !isExpanded);
  });
});
