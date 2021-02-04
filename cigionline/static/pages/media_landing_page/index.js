import React from 'react';
import ReactDOM from 'react-dom';
import MediaListing from '../../js/components/MediaListing';
import SearchTable from '../../js/components/SearchTable';
import './css/media_landing_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/media_articles"
    fields={[
      'article_type',
      'get_article_type_display',
      'cigi_people_mentioned',
      'publishing_date',
      'title',
      'topics(title,url)',
      'url',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'News Releases',
      typeEndpoint: '/article_types',
      typeValue: 'News Release',
    }, {
      name: 'CIGI in the News',
      typeEndpoint: '/article_types',
      typeValue: 'CIGI in the News',
    }, {
      name: 'Op-Eds',
      typeEndpoint: '/article_types',
      typeValue: 'Op-Ed',
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
