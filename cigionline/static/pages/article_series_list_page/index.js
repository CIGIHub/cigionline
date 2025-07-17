import React from 'react';
import { createRoot } from 'react-dom/client';
import ArticleSeriesListing from '../../js/components/ArticleSeriesListing';
import SearchTable from '../../js/components/SearchTable';

const root = createRoot(document.getElementById('article-series-search-table'));
root.render(
  <SearchTable
    blockListing
    contenttypes={[
      'Essay Series',
    ]}
    limit={5}
    fields={[
      'image_poster_caption',
      'image_poster_url',
      'series_pdf',
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
);
