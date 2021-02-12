import React from 'react';
import ReactDOM from 'react-dom';
import SearchResultListing from '../../js/components/SearchResultListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    isSearchPage
    showSearch
    fields={[]}
    containerClass={[
      'search-result-row',
    ]}
    RowComponent={SearchResultListing}
  />,
  document.getElementById('search-table'),
);
