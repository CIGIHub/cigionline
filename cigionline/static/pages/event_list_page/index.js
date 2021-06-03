import React from 'react';
import ReactDOM from 'react-dom';
import EventListing from '../../js/components/EventListing';
import SearchTable from '../../js/components/SearchTable';
import EventCalendar from '../../js/components/EventCalendar';
import './css/_event_list_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={[
      'Event',
    ]}
    fields={[
      'event_access',
      'location_city',
      'location_country',
      'multimedia_url',
      'publishing_date',
      'registration_url',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
      'table-events',
    ]}
    RowComponent={EventListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Topic',
    }, {
      colSpan: 2,
      colTitle: 'Location',
    }, {
      colSpan: 1,
      colTitle: '',
    }]}
  />,
  document.getElementById('events-search-table'),
);

ReactDOM.render(
  <EventCalendar />,
  document.getElementById('event-list-calendar'),
);
