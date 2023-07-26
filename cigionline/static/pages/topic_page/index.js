/* global topicId */
import React from 'react';
import ReactDOM from 'react-dom';
import SearchResultCard from '../../js/components/SearchResultCard';
import SearchTable from '../../js/components/SearchTable';

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
      'image_poster_url',
      'image_hero_url',
      'image_hero_wide_url',
      'pdf_download',
      'publishing_date',
      'topics',
      'event_access',
      'time_zone_label',
      'event_format_string',
      'event_end',
    ]}
    containerClass={['custom-theme-table']}
    filterTypes={[
      {
        name: 'Event',
        params: [
          {
            name: 'contenttype',
            value: 'Event',
          },
        ],
      },
      {
        name: 'Publication',
        params: [
          {
            name: 'contenttype',
            value: 'Publication',
          },
        ],
      },
      {
        name: 'Multimedia',
        params: [
          {
            name: 'contenttype',
            value: 'Multimedia',
          },
        ],
      },
      {
        name: 'Opinion',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Opinion',
          },
        ],
      },
      {
        name: 'Op-Eds',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Op-Eds',
          },
        ],
      },
      {
        name: 'CIGI in the News',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'CIGI in the News',
          },
        ],
      },
      {
        name: 'News Releases',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'News Releases',
          },
        ],
      },
    ]}
    RowComponent={SearchResultCard}
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
        colClass: 'title',
      },
      {
        colSpan: 3,
        colTitle: 'Type',
        colClass: 'type',
      },
      {
        colSpan: 2,
        colTitle: 'Expert',
        colClass: 'authors',
      },
      {
        colSpan: 3,
        colTitle: 'Topic',
        colClass: 'topics',
      },
      {
        colSpan: 1,
        colTitle: 'PDF',
        colClass: 'more',
      },
    ]}
  />,
  document.getElementById('topic-search-table'),
);

const topicsExpand = document.getElementById('topics-expand');
const topTopicsUl = document.getElementById('top-topics-list-ul');

topicsExpand.addEventListener('click', function() {
  topicsExpand.classList.toggle('expanded');
  topTopicsUl.classList.toggle('expanded');
});
