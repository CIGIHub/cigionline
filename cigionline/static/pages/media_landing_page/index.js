import React from 'react';
import ReactDOM from 'react-dom';
import MediaListing from '../../js/components/MediaListing';
import SearchTable from '../../js/components/SearchTable';
import './css/media_landing_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    fields={[
      'cigi_people_mentioned',
      'contentsubtype',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'News Releases',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'News Releases',
    }, {
      name: 'CIGI in the News',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'CIGI in the News',
    }, {
      name: 'Op-Eds',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'Op-Eds',
    }]}
    RowComponent={MediaListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 1,
      colTitle: 'Expert',
    }, {
      colSpan: 1,
      colTitle: 'Type',
    }, {
      colSpan: 4,
      colTitle: 'Topic',
    }]}
  />,
  document.getElementById('media-search-table'),
);
