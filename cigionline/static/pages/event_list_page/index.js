import React from 'react';
import ReactDOM from 'react-dom';
import Swiper, { Navigation, Pagination } from 'swiper';
import EventSearchResultCard from '../../js/components/EventSearchResultCard';
import EventListing from '../../js/components/EventListing';
import FeaturedEventListing from '../../js/components/FeaturedEventListing';
import SearchTable from '../../js/components/SearchTable';
import EventCalendar from '../../js/components/EventCalendar';
import './css/_event_list_page.scss';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation, Pagination]);

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={['Event']}
    fields={[
      'authors',
      'contentsubtype',
      'image_hero_url',
      'publishing_date',
      'title',
      'topics',
      'url',
      'event_access',
      'event_end',
      'event_type',
      'event_format_string',
      'time_zone_label',
      'event_start_time_utc_ts',
      'event_end_time_utc_ts',
    ]}
    filterTypes={[
      {
        name: 'CIGI Sponsored',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'CIGI Sponsored',
          },
        ],
      },
      {
        name: 'Cinema Series',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Cinema Series',
          },
        ],
      },
      {
        name: 'Community Event',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Community Event',
          },
        ],
      },
      {
        name: 'Conference',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Conference',
          },
        ],
      },
      {
        name: 'Global Policy Forum',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Global Policy Forum',
          },
        ],
      },
      {
        name: 'Noon Lecture Series',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Noon Lecture Series',
          },
        ],
      },
      {
        name: 'Panel Discussion',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Panel Discussion',
          },
        ],
      },
      {
        name: 'Publication Launch',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Publication Launch',
          },
        ],
      },
      {
        name: 'Round Table',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Round Table',
          },
        ],
      },
      {
        name: 'Seminar',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Seminar',
          },
        ],
      },
      {
        name: 'Signature Lecture',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Signature Lecture',
          },
        ],
      },
      {
        name: 'Virtual Event',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Virtual Event',
          },
        ],
      },
      {
        name: 'Workshop',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Workshop',
          },
        ],
      },
    ]}
    containerClass={['custom-theme-table', 'table-events']}
    RowComponent={EventSearchResultCard}
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
        colClass: 'title',
      },
      {
        colSpan: 3,
        colTitle: 'Type',
        colClass: 'type',
      },
      {
        colSpan: 3,
        colTitle: 'Speaker',
        colClass: 'authors',
      },
      {
        colSpan: 2,
        colTitle: 'Topic',
        colClass: 'topics',
      },
    ]}
  />,
  document.getElementById('events-search-table'),
);

ReactDOM.render(
  <EventCalendar />,
  document.getElementById('event-list-calendar'),
);

ReactDOM.render(
  <EventListing />,
  document.getElementById('event-list'),
);

const featuredEvents = JSON.parse(
  document.getElementById('events-page__featured-events-slider').dataset
    .eventsPageFeaturedEventsSlider,
);

ReactDOM.render(
  <FeaturedEventListing
    meta={featuredEvents.meta}
    items={featuredEvents.items}
  />,
  document.getElementById('featured-events'),
);

if (featuredEvents) {
  const eventsPageFeaturedEventsSlider = new Swiper('.swiper-container', {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },

    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
  });
}

const navItems = document.querySelectorAll('.nav-link');
const pageLabel = document.getElementById('page-label');
navItems.forEach((item) => {
  item.addEventListener('click', () => {
    pageLabel.innerHTML = item.innerHTML;
  });
});
