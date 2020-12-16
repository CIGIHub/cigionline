import React from 'react';
import ReactDOM from 'react-dom';
import OpinionListing from '../../js/components/OpinionListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/opinions"
    fields={[
      'authors',
      'publishing_date',
      'title',
      'topics(title,url)',
      'url',
    ]}
    containerClass={[
      'custom-theme-table',
      'table-opinions',
    ]}
    RowComponent={OpinionListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Author',
    }, {
      colSpan: 3,
      colTitle: 'Topic',
    }]}
  />,
  document.getElementById('opinions-search-table'),
);
