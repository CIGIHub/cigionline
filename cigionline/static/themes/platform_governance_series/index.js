import './css/platform_governance_series.scss';

const displayGridButton = document.querySelector('.platform-governance-display-grid');
const displayListButton = document.querySelector('.platform-governance-display-list');
const listingContainer = document.querySelector('.platform-governance-listing');

if (displayGridButton && displayListButton && listingContainer) {
  displayGridButton.addEventListener('click', function() {
    if (!displayGridButton.classList.contains('active')) {
      displayGridButton.classList.add('active');
      displayListButton.classList.remove('active');
      listingContainer.classList.remove('display-list');
    }
  });
  displayListButton.addEventListener('click', function() {
    if (!displayListButton.classList.contains('active')) {
      displayListButton.classList.add('active');
      displayGridButton.classList.remove('active');
      listingContainer.classList.add('display-list');
    }
  });
}
