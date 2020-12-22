import './css/big_tech_s3.scss';

const simplecastContainer = document.querySelector('.simplecast-container');
const simplecastHeader = document.querySelector('.simplecast-header');

if (simplecastContainer && simplecastHeader) {
  window.addEventListener('scroll', function() {
    const windowWidth = parseFloat(getComputedStyle(document.querySelector('html'), null).width.replace('px', ''));
    const windowHeight = parseFloat(getComputedStyle(document.querySelector('html'), null).height.replace('px', ''));

    const scrollTop = document.querySelector('html').scrollTop;

    const containerHeight = parseFloat(getComputedStyle(simplecastContainer, null).height.replace('px', ''));
    const containerTop = simplecastContainer.offsetTop;
    const containerBottom = containerTop + containerHeight;

    if (windowWidth > 768
        && windowHeight > 600
        && scrollTop > containerBottom) {
      if (!simplecastHeader.classList.contains('sticky-video')) {
        simplecastHeader.classList.add('sticky-video');
      }
    } else if (simplecastHeader.classList.contains('sticky-video')) {
      simplecastHeader.classList.remove('sticky-video');
    }
  });
}
