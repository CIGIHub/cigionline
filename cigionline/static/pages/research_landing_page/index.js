import React from 'react';
import ReactDOM from 'react-dom';
import ResearchContentListing from '../../js/components/ResearchContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/research_landing_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'Event',
      param: 'contenttype',
      value: 'Event',
    }, {
      name: 'Publication',
      param: 'contenttype',
      value: 'Publication',
    }, {
      name: 'Multimedia',
      param: 'contenttype',
      value: 'Multimedia',
    }, {
      name: 'Opinion',
      param: 'contentsubtype',
      value: 'Opinion',
    }, {
      name: 'Op-Eds',
      param: 'contentsubtype',
      value: 'Op-Eds',
    }, {
      name: 'CIGI in the News',
      param: 'contentsubtype',
      value: 'CIGI in the News',
    }, {
      name: 'News Releases',
      param: 'contentsubtype',
      value: 'News Releases',
    }]}
    RowComponent={ResearchContentListing}
    tableColumns={[{
      colSpan: 4,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Expert',
    }, {
      colSpan: 2,
      colTitle: 'Topic',
    }, {
      colSpan: 2,
      colTitle: 'Type',
    }, {
      colSpan: 1,
      colTitle: 'PDF',
    }]}
  />,
  document.getElementById('research-search-table'),
);
