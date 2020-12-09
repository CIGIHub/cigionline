import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListing from './js/components/PublicationListing';
import SearchTable from './js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    endpoint="/publications"
    fields={[
      'authors',
      'pdf_downloads',
      'publishing_date',
      'title',
      'topics(title,url)',
      'url',
    ]}
    containerClass={[
      'custom-theme-table',
      'table-publications',
    ]}
    RowComponent={PublicationListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 2,
      colTitle: 'Topic',
    }, {
      colSpan: 3,
      colTitle: 'Expert',
    }, {
      colSpan: 0,
      colTitle: 'PDF',
    }]}
  />,
  document.getElementById('publications-search-table'),
);
