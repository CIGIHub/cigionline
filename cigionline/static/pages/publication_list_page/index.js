import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListing from '../../js/components/PublicationListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={[
      'Publication',
    ]}
    fields={[
      'authors',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    filterTypes={[{
      name: 'Books',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Books',
      }]
    }, {
      name: 'Papers',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI Papers',
      }]
    }, {
      name: 'Conference Reports',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Conference Reports',
      }]
    }, {
      name: 'Essay Series',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Essay Series',
      }]
    }, {
      name: 'Policy Briefs',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Policy Briefs',
      }]

    }, {
      name: 'Policy Memos',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Policy Memos',
      }]

    }, {
      name: 'Special Reports',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Special Reports',
      }]
    }]}
    containerClass={[
      'custom-theme-table',
      'table-publications',
    ]}
    RowComponent={PublicationListing}
    searchPlaceholder="Search all publications"
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
