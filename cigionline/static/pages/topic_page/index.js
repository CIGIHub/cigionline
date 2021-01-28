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
      value: 'opinion',
    }, {
      endpoint: '/opinions',
      name: 'Op-Ed',
      param: 'article_type',
      value: 'op_ed',
    }, {
      endpoint: '/media_articles',
      name: 'CIGI in the News',
      param: 'article_type',
      value: 'cigi_in_the_news',
    }, {
      endpoint: '/media_articles',
      name: 'News Release',
      param: 'article_type',
      value: 'news_release',
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
