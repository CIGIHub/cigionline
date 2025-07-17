import React from 'react';
import { createRoot } from 'react-dom/client';
import MediaListing from '../../js/components/MediaListing';
import SearchTable from '../../js/components/SearchTable';
import './css/media_landing_page.scss';

const root = createRoot(document.getElementById('media-search-table'));
root.render(
  <SearchTable
    showSearch
    contenttypes={[
      'Opinion',
    ]}
    contentsubtypes={[
      'CIGI in the News',
      'News Releases',
      'Op-Eds',
    ]}
    fields={[
      'cigi_people_mentioned',
      'contentsubtype',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'News Releases',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'News Releases',
      }],
    }, {
      name: 'CIGI in the News',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI in the News',
      }],
    }, {
      name: 'Op-Eds',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Op-Eds',
      }],
    }]}
    RowComponent={MediaListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 1,
      colTitle: 'Expert',
    }, {
      colSpan: 1,
      colTitle: 'Type',
    }, {
      colSpan: 4,
      colTitle: 'Topic',
    }]}
  />,
);
