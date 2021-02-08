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
    // filterTypes={[{
    //   name: 'Books',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'Books',
    // }, {
    //   name: 'CIGI Papers',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'CIGI Papers',
    // }, {
    //   name: 'Conference Reports',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'Conference Reports',
    // }, {
    //   name: 'Essay Series',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'Essay Series',
    // }, {
    //   name: 'Policy Briefs',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'Policy Briefs',
    // }, {
    //   name: 'Policy Memos',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'Policy Memos',
    // }, {
    //   name: 'Special Reports',
    //   param: 'publication_type',
    //   typeEndpoint: '/publication_types',
    //   typeValue: 'Special Reports',
    // }]}
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
