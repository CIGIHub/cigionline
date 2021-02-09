/* global articleTypeId */
import React from 'react';
import ReactDOM from 'react-dom';
import ArticleListingSimple from '../../js/components/ArticleListingSimple';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (articleTypeId) {
  endpointParams.push({
    paramName: 'article_type',
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
      'authors(author(title,url))',
      'article_type(title)',
      'publishing_date',
      'title',
      'url',
    ]}
    RowComponent={ArticleListingSimple}
  />,
  document.getElementById('articles-list'),
);
