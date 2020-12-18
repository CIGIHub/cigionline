import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListing from '../../js/components/PublicationListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/publications"
    fields={[
      'authors',
      'pdf_downloads',
      'publishing_date',
      'title',
      'topics(title,url)',
      'url',
    ]}
    filterTypes={[{
      name: 'Books',
      param: 'publication_type',
      value: 'books',
    }, {
      name: 'CIGI Papers',
      param: 'publication_type',
      value: 'cigi_papers',
    }, {
      name: 'Conference Reports',
      param: 'publication_type',
      value: 'conference_reports',
    }, {
      name: 'Essay Series',
      param: 'publication_type',
      value: 'essay_series',
    }, {
      name: 'Policy Briefs',
      param: 'publication_type',
      value: 'policy_briefs',
    }, {
      name: 'Policy Memos',
      param: 'publication_type',
      value: 'policy_memos',
    }, {
      name: 'Special Reports',
      param: 'publication_type',
      value: 'special_reports',
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
