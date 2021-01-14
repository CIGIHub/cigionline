import './css/platform_governance_series.scss';

console.log('hello world');

const displayGridButton = document.querySelector('.platform-governance-display-grid');
const displayListButton = document.querySelector('.platform-governance-display-list');
const listingContainer = document.querySelector('.platform-governance-listing');

if (displayGridButton && displayListButton && listingContainer) {
  displayGridButton.addEventListener('click', function() {
    console.log('displayGridButton click');
    console.log(displayGridButton.classList);
    console.log(displayGridButton.classList.contains('active'));
    if (!displayGridButton.classList.contains('active')) {
      displayGridButton.classList.add('active');
      displayListButton.classList.remove('active');
      listingContainer.classList.remove('display-list');
    }
  });
  displayListButton.addEventListener('click', function() {
    console.log('displayListButton click');
    console.log(displayListButton.classList);
    console.log(displayListButton.classList.contains('active'));
    if (!displayListButton.classList.contains('active')) {
      displayListButton.classList.add('active');
      displayGridButton.classList.remove('active');
      listingContainer.classList.add('display-list');
    }
  });
} else {
  console.log('fail');
}
