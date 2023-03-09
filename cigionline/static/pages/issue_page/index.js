/* global issueId */
import React from 'react';
import ReactDOM from 'react-dom';
import SearchResultCard from '../../js/components/SearchResultCard';
import SearchTable from '../../js/components/SearchTable';

import './css/issue_page.scss';

const endpointParams = [];
if (issueId) {
  endpointParams.push({
    paramName: 'issue',
    paramValue: issueId,
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    hideissueDropdown
    endpointParams={endpointParams}
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'image_poster_url',
      'image_hero_url',
      'pdf_download',
      'publishing_date',
      'topics',
      'event_access',
      'time_zone_label',
      'event_format_string',
      'event_end',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'Event',
      params: [{
        name: 'contenttype',
        value: 'Event',
      }],
    }, {
      name: 'Publication',
      params: [{
        name: 'contenttype',
        value: 'Publication',
      }],
    }, {
      name: 'Multimedia',
      params: [{
        name: 'contenttype',
        value: 'Multimedia',
      }],
    }, {
      name: 'Opinion',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Opinion',
      }],
    }, {
      name: 'Op-Eds',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Op-Eds',
      }],
    }, {
      name: 'CIGI in the News',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI in the News',
      }],
    }, {
      name: 'News Releases',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'News Releases',
      }],
    }]}
    RowComponent={SearchResultCard}
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
  document.getElementById('issue-search-table'),
);
