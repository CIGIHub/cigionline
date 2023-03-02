import React from 'react';
import ReactDOM from 'react-dom';
import EventSearchResultCard from '../../js/components/EventSearchResultCard';
import EventList from '../../js/components/EventList';
import SearchTable from '../../js/components/SearchTable';
import EventCalendar from '../../js/components/EventCalendar';
import './css/_event_list_page.scss';

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
    ]}
    filterTypes={[{
      name: 'CIGI Sponsored',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI Sponsored',
      }],
    }, {
      name: 'Cinema Series',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Cinema Series',
      }],
    }, {
      name: 'Community Event',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Community Event',
      }],
    }, {
      name: 'Conference',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Conference',
      }],
    }, {
      name: 'Global Policy Forum',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Global Policy Forum',
      }],
    }, {
      name: 'Noon Lecture Series',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Noon Lecture Series',
      }],
    }, {
      name: 'Panel Discussion',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Panel Discussion',
      }],
    }, {
      name: 'Publication Launch',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Publication Launch',
      }],
    }, {
      name: 'Round Table',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Round Table',
      }],
    }, {
      name: 'Seminar',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Seminar',
      }],
    }, {
      name: 'Signature Lecture',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Signature Lecture',
      }],
    }, {
      name: 'Virtual Event',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Virtual Event',
      }],
    }, {
      name: 'Workshop',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Workshop',
      }],
    }]}
    containerClass={['custom-theme-table', 'table-events']}
    RowComponent={EventSearchResultCard}
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
      },
      {
        colSpan: 3,
        colTitle: 'Topic',
      },
      {
        colSpan: 2,
        colTitle: 'Location',
      },
      {
        colSpan: 1,
        colTitle: '',
      },
    ]}
  />,
  document.getElementById('events-search-table'),
);

ReactDOM.render(
  <EventCalendar />,
  document.getElementById('event-list-calendar'),
);

const allEvents = JSON.parse(document.getElementById('all-events').dataset.allEvents);

ReactDOM.render(
  <EventList meta={allEvents.meta} items={allEvents.items} />,
  document.getElementById('event-list'),
);
