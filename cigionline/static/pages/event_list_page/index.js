import React from 'react';
import ReactDOM from 'react-dom';
import EventListing from '../../js/components/EventListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/events"
    fields={[
      'event_access',
      'location_city',
      'location_country',
      'multimedia_url',
      'publishing_date',
      'registration_url',
      'title',
      'topics(title,url)',
      'url',
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
