/* global personId */
import React from 'react';
import ReactDOM from 'react-dom';
import ExpertContentListing from '../../js/components/ExpertContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/person_page.scss';

const endpointParams = [];
if (personId) {
  endpointParams.push({
    paramName: 'author',
    paramValue: personId,
  });
}

ReactDOM.render(
  <SearchTable
    endpointParams={endpointParams}
    fields={[
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    limit={14}
    RowComponent={ExpertContentListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Topic',
    }, {
      colSpan: 2,
      colTitle: 'Type',
    }, {
      colSpan: 1,
      colTitle: 'PDF',
    }]}
  />,
  document.getElementById('expert-search-table'),
);
