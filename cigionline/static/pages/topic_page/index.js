/* global topicId */
import React from 'react';
import ReactDOM from 'react-dom';
import SearchTable from '../../js/components/SearchTable';
import TopicContentListing from '../../js/components/TopicContentListing';

import './css/topic_page.scss';

const endpointParams = [];
if (topicId) {
  endpointParams.push({
    paramName: 'topic',
    paramValue: topicId,
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    hideTopicDropdown
    endpointParams={endpointParams}
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'Event',
      param: 'contenttype',
      value: 'Event',
    }, {
      name: 'Publication',
      param: 'contenttype',
      value: 'Publication',
    }, {
      name: 'Multimedia',
      param: 'contenttype',
      value: 'Multimedia',
    }, {
      name: 'Opinion',
      param: 'contentsubtype',
      value: 'Opinion',
    }, {
      name: 'Op-Eds',
      param: 'contentsubtype',
      value: 'Op-Eds',
    }, {
      name: 'CIGI in the News',
      param: 'contentsubtype',
      value: 'CIGI in the News',
    }, {
      name: 'News Releases',
      param: 'contentsubtype',
      value: 'News Releases',
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
