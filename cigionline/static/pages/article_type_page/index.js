/* global articleTypeId */
import React from 'react';
import ReactDOM from 'react-dom';
import ArticleListingSimple from '../../js/components/ArticleListingSimple';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (articleTypeId) {
  endpointParams.push({
    paramName: 'articletypeid',
    paramValue: articleTypeId,
  });
}

ReactDOM.render(
  <SearchTable
    blockListing
    endpoint="/articles"
    endpointParams={endpointParams}
    limit={10}
    fields={[
      'authors',
      'publishing_date',
    ]}
    RowComponent={ArticleListingSimple}
  />,
  document.getElementById('articles-list'),
);
