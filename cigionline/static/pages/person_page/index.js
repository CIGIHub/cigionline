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
      colClass: 'title',
    }, {
      colSpan: 3,
      colTitle: 'Topic',
      colClass: 'topics',
    }, {
      colSpan: 2,
      colTitle: 'Type',
      colClass: 'content-type',
    }, {
      colSpan: 1,
      colTitle: 'More',
      colClass: 'more',
    }]}
    showSidebar={false}
    allowDisplayToggle={false}
    displayMode="list"
  />,
  document.getElementById('expert-search-table'),
);
