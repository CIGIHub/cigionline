import React from 'react';
import ReactDOM from 'react-dom';
import ArticleSeriesListing from '../../js/components/ArticleSeriesListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    contenttypes={[
      'Opinion Series',
    ]}
    limit={5}
    fields={[
      'image_poster_caption',
      'image_poster_url',
      'series_contributors',
      'short_description',
      'topics',
    ]}
    containerClass={[
      'articles-series-row',
    ]}
    showSidebar={false}
    RowComponent={ArticleSeriesListing}
  />,
  document.getElementById('article-series-search-table'),
);
