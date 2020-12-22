import './css/multimedia_page.scss';
import createStickyHeaderScrollListener from '../../js/create_sticky_header_scroll_listener';

const mmHero = document.querySelector('.mm-hero');
const mmVideoContainer = document.querySelector('.mm-video-container');
const mmVideoHeader = document.querySelector('.mm-video-header');

if (mmHero && mmVideoContainer && mmVideoHeader) {
  createStickyHeaderScrollListener({
    scrollTriggerEl: mmHero,
    stickyHeaderContainerEl: mmVideoContainer,
    stickyHeaderEl: mmVideoHeader,
  });
}
