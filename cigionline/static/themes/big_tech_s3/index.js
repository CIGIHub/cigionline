import './css/big_tech_s3.scss';
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

const dropdown = $('#season-select');
const seasonContainers = $('.season-episodes');
const seasonSelectBtn = $('#season-select-btn');

dropdown.find('li').on('click', function(e) {
  seasonContainers.removeClass('active');
  $(`#${e.currentTarget.dataset.season}`).addClass('active');
  seasonSelectBtn.text(e.currentTarget.textContent);
});
