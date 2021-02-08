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
      // 'contenttype',
      // 'contentsubtype',
      'pdf_download',
      // 'publication_type(title,url)',
      'publishing_date',
      // 'title',
      'topics',
      // 'url',
    ]}
    filterTypes={[{
      name: 'Books',
      param: 'contentsubtype',
      value: 'Books',
    }, {
      name: 'CIGI Papers',
      param: 'contentsubtype',
      value: 'CIGI Papers',
    }, {
      name: 'Conference Reports',
      param: 'contentsubtype',
      value: 'Conference Reports',
    }, {
      name: 'Essay Series',
      param: 'contentsubtype',
      value: 'Essay Series',
    }, {
      name: 'Policy Briefs',
      param: 'contentsubtype',
      value: 'Policy Briefs',
    }, {
      name: 'Policy Memos',
      param: 'contentsubtype',
      value: 'Policy Memos',
    }, {
      name: 'Special Reports',
      param: 'contentsubtype',
      value: 'Special Reports',
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
