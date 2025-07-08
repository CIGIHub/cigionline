/* global countryId */
import React from 'react';
import { createRoot } from 'react-dom/client';
import SearchTable from '../../js/components/SearchTable';
import TopicContentListing from '../../js/components/TopicContentListing';

import './css/country_page.scss';

const endpointParams = [];
if (countryId) {
  endpointParams.push({
    paramName: 'country',
    paramValue: countryId,
  });
}

const root = createRoot(document.getElementById('country-search-table'));
root.render(
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
    RowComponent={TopicContentListing}
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
      },
      {
        colSpan: 3,
        colTitle: 'Expert',
      },
      {
        colSpan: 2,
        colTitle: 'Type',
      },
      {
        colSpan: 1,
        colTitle: 'PDF',
      },
    ]}
  />,
);
