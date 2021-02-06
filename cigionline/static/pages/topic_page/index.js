/* global topicId */
import React from 'react';
import ReactDOM from 'react-dom';
import SearchTable from '../../js/components/SearchTable';
import TopicContentListing from '../../js/components/TopicContentListing';

const endpointParams = [];
if (topicId) {
  endpointParams.push({
    paramName: 'topics',
    paramValue: topicId,
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    hideTopicDropdown
    endpoint="/content"
    endpointParams={endpointParams}
    fields={[
      'authors(author(title,url))',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'title',
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
    RowComponent={TopicContentListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Expert',
    }, {
      colSpan: 2,
      colTitle: 'Type',
    }, {
      colSpan: 1,
      colTitle: 'PDF',
    }]}
  />,
  document.getElementById('topic-search-table'),
);
