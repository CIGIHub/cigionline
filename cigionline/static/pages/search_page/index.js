import React from 'react';
import ReactDOM from 'react-dom';
import SearchResultListing from '../../js/components/SearchResultListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    isSearchPage
    showSearch
    fields={[
      'authors',
      'contenttype',
      'contentsubtype',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'search-result-row',
    ]}
    RowComponent={SearchResultListing}
  />,
  document.getElementById('search-table'),
);
