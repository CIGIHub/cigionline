import './css/big_tech.scss';
import createStickyHeaderScrollListener from '../../js/create_sticky_header_scroll_listener';

const simplecastContainer = document.querySelector('.simplecast-container');
const simplecastHeader = document.querySelector('.simplecast-header');

if (simplecastContainer && simplecastHeader) {
  createStickyHeaderScrollListener({
    scrollTriggerEl: simplecastContainer,
    stickyHeaderContainerEl: simplecastContainer,
    stickyHeaderEl: simplecastHeader,
  });
}
