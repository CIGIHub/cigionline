import './css/multimedia_page.scss';

const mmHero = document.querySelector('.mm-hero');
const mmVideoContainer = document.querySelector('.mm-video-container');
const mmVideoHeader = document.querySelector('.mm-video-header');

if (mmHero && mmVideoContainer && mmVideoHeader) {
  window.addEventListener('scroll', function() {
    const windowWidth = parseFloat(getComputedStyle(document.querySelector('html'), null).width.replace('px', ''));
    const windowHeight = parseFloat(getComputedStyle(document.querySelector('html'), null).height.replace('px', ''));

    const scrollTop = document.querySelector('html').scrollTop;
    const multimediaHeroVideoHeight = parseFloat(getComputedStyle(mmVideoHeader, null).height.replace('px', ''));

    const mmHeroHeight = parseFloat(getComputedStyle(mmHero, null).height.replace('px', ''));
    const mmHeroTop = mmHero.offsetTop;
    const mmHeroBottom = mmHeroTop + mmHeroHeight;

    if (windowWidth > 768
        && windowHeight > 600
        && scrollTop > mmHeroBottom) {
      if (!mmVideoContainer.classList.contains('sticky-video')) {
        mmVideoContainer.style.height = `${multimediaHeroVideoHeight}px`;
        mmVideoContainer.classList.add('sticky-video');
      }
    } else if (mmVideoContainer.classList.contains('sticky-video')) {
      mmVideoContainer.style.height = '';
      mmVideoContainer.classList.remove('sticky-video');
    }
  });
}
