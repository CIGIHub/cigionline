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
      param: 'article_type',
      value: 'news_release',
    }, {
      name: 'CIGI in the News',
      param: 'article_type',
      value: 'cigi_in_the_news',
    }, {
      name: 'Op-Eds',
      param: 'article_type',
      value: 'op_ed',
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
