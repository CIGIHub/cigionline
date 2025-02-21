/* global projectId */
/* global hasTaggedPages */
import React from 'react';
import { createRoot } from 'react-dom/client';
import ProjectContentListing from '../../js/components/ProjectContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/project_page.scss';

const endpointParams = [];
if (projectId) {
  endpointParams.push({
    paramName: 'project',
    paramValue: projectId,
  });
}

if (hasTaggedPages) {
  const root = createRoot(document.getElementById('project-search-table'));
  root.render(
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
      RowComponent={ProjectContentListing}
      tableColumns={[{
        colSpan: 4,
        colTitle: 'Title',
      }, {
        colSpan: 3,
        colTitle: 'Expert',
      }, {
        colSpan: 2,
        colTitle: 'Topic',
      }, {
        colSpan: 2,
        colTitle: 'Type',
      }, {
        colSpan: 1,
        colTitle: 'PDF',
      }]}
    />,
  );
}
