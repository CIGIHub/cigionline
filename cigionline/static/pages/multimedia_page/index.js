import './css/multimedia_page.scss';

const multimediaHeroVideo = document.querySelector('.multimedia-hero-video');

if (multimediaHeroVideo) {
  window.addEventListener('scroll', function() {
    const windowWidth = parseFloat(getComputedStyle(document.querySelector('html'), null).width.replace('px', ''));
    const windowHeight = parseFloat(getComputedStyle(document.querySelector('html'), null).height.replace('px', ''));

    const scrollTop = document.querySelector('html').scrollTop;
    const multimediaHeroVideoHeight = parseFloat(getComputedStyle(multimediaHeroVideo, null).height.replace('px', ''));
    const multimediaHeroVideoTop = multimediaHeroVideo.offsetTop;
    const multimediaHeroVideoBottom = multimediaHeroVideoTop + multimediaHeroVideoHeight;

    if (windowWidth > 768
        && windowHeight > 600
        && scrollTop > multimediaHeroVideoBottom) {
      if (!multimediaHeroVideo.classList.contains('sticky-video')) {
        multimediaHeroVideo.classList.add('sticky-video');
      }
    } else if (multimediaHeroVideo.classList.contains('sticky-video')) {
      multimediaHeroVideo.classList.remove('sticky-video');
    }
  });
}
