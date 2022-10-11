export default ({
  scrollTriggerEl,
  stickyHeaderContainerEl,
  stickyHeaderEl,
}) => {
  window.addEventListener('scroll', function() {
    const windowWidth = parseFloat(getComputedStyle(document.querySelector('html'), null).width.replace('px', ''));
    const windowHeight = parseFloat(getComputedStyle(document.querySelector('html'), null).height.replace('px', ''));

    const scrollTop = document.querySelector('html').scrollTop;
    const multimediaHeroVideoHeight = parseFloat(getComputedStyle(stickyHeaderEl, null).height.replace('px', ''));

    const mmHeroHeight = parseFloat(getComputedStyle(scrollTriggerEl, null).height.replace('px', ''));
    const mmHeroTop = scrollTriggerEl.offsetTop;
    const mmHeroBottom = mmHeroTop + mmHeroHeight;

    const mmHero = document.querySelector('.big-tech-mm-hero') || document.querySelector('.mm-hero');

    if (windowWidth > 768
        && windowHeight > 600
        && scrollTop > mmHeroBottom) {
      if (!stickyHeaderContainerEl.classList.contains('sticky-video')) {
        stickyHeaderContainerEl.style.height = `${multimediaHeroVideoHeight}px`;
        stickyHeaderContainerEl.classList.add('sticky-video');
        mmHero.classList.add('z-index-1');
      }
    } else if (stickyHeaderContainerEl.classList.contains('sticky-video')) {
      stickyHeaderContainerEl.style.height = '';
      stickyHeaderContainerEl.classList.remove('sticky-video');
      mmHero.classList.remove('z-index-1');
    }
  });
};
