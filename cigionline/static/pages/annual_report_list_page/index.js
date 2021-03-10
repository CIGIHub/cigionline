import React from 'react';
import ReactDOM from 'react-dom';
import AnnualReportListing from '../../js/components/AnnualReportListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    showSearch
    limit={10}
    fields={[
      'year',
      'report_english',
      'report_financial',
      'report_french',
      'report_interactive',
    ]}
    filterTypes={[{
      name: 'Year',
      param: 'year',
      value: 'Year',
    }]}
    RowComponent={AnnualReportListing}
  />,
  document.getElementById('annual-reports-search-table'),
);
