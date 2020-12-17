import React from 'react';
import ReactDOM from 'react-dom';
import EventListing from '../../js/components/EventListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/events"
    fields={[
      'location_city',
      'location_country',
      'publishing_date',
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
    }]}
  />,
  document.getElementById('events-search-table'),
)
