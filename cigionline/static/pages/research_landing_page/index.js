import React from 'react';
import ReactDOM from 'react-dom';
import ResearchContentListing from '../../js/components/ResearchContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/research_landing_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/content"
    fields={[
      'authors(author(title,url))',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'title',
      'topics(title,url)',
      'url',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      endpoint: '/events',
      name: 'Event',
    }, {
      endpoint: '/publications',
      name: 'Publication',
    }, {
      endpoint: '/multimedia',
      name: 'Multimedia',
    }, {
      endpoint: '/opinions',
      name: 'Opinion',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'Opinion',
    }, {
      endpoint: '/opinions',
      name: 'Op-Eds',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'Op-Eds',
    }, {
      endpoint: '/media_articles',
      name: 'CIGI in the News',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'CIGI in the News',
    }, {
      endpoint: '/media_articles',
      name: 'News Releases',
      param: 'article_type',
      typeEndpoint: '/article_types',
      typeValue: 'News Releases',
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
