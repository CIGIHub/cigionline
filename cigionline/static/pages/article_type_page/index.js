/* global articleTypeId */
import React from 'react';
import { createRoot } from 'react-dom/client';
import ArticleListingSimple from '../../js/components/ArticleListingSimple';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (articleTypeId) {
  endpointParams.push({
    paramName: 'articletypeid',
    paramValue: articleTypeId,
  });
}

const root = createRoot(document.getElementById('articles-list'));
root.render(
  <SearchTable
    blockListing
    endpoint="/articles"
    endpointParams={endpointParams}
    limit={10}
    fields={['authors', 'publishing_date']}
    RowComponent={ArticleListingSimple}
  />,
);
