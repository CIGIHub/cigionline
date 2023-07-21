/* global projectId */
import React from 'react';
import ReactDOM from 'react-dom';
import ProjectContentListing from '../../js/components/ProjectContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/project_page.scss';
import SearchResultCard from '../../js/components/SearchResultCard';

const endpointParams = [];
if (projectId) {
  endpointParams.push({
    paramName: 'project',
    paramValue: projectId,
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    endpointParams={endpointParams}
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'topics',
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
    RowComponentList={ProjectContentListing}
    tableColumns={[{
      colSpan: 4,
      colTitle: 'Title',
      colClass: 'title',
    }, {
      colSpan: 3,
      colTitle: 'Author',
      colClass: 'authors',
    }, {
      colSpan: 2,
      colTitle: 'Topic',
      colClass: 'topics',
    }, {
      colSpan: 1,
      colTitle: 'More',
      colClass: 'more',
    }]}
  />,
  document.getElementById('project-search-table'),
);
