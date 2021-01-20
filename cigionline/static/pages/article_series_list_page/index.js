import React from 'react';
import ReactDOM from 'react-dom';
import ArticleSeriesListing from '../../js/components/ArticleSeriesListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    endpoint="/article_series"
    limit={5}
    fields={[
      'image_poster_title',
      'image_poster_url',
      'series_contributors',
      'short_description',
      'title',
      'topics(title,url)',
      'url',
    ]}
    containerClass={[
      'articles-series-row',
    ]}
    RowComponent={ArticleSeriesListing}
  />,
  document.getElementById('article-series-search-table'),
);
