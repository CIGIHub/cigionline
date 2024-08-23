/* eslint-disable no-unused-vars */

import React from 'react';
import ReactDOM from 'react-dom';
import OpinionListing from '../../js/components/OpinionListing';
import SearchTable from '../../js/components/SearchTable';

import './css/article_landing_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={['Opinion']}
    contentsubtypes={['Interviews', 'Op-Eds', 'Opinion', 'Essays']}
    fields={['authors', 'publishing_date', 'topics']}
    containerClass={['custom-theme-table', 'table-opinions']}
    RowComponent={OpinionListing}
    searchPlaceholder="Search all opinions"
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
      },
      {
        colSpan: 3,
        colTitle: 'Author',
      },
      {
        colSpan: 3,
        colTitle: 'Topic',
      },
    ]}
  />,
  document.getElementById('opinions-search-table'),
);
