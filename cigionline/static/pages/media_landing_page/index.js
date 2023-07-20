import React from 'react';
import ReactDOM from 'react-dom';
import MediaListing from '../../js/components/MediaListing';
import SearchTable from '../../js/components/SearchTable';
import './css/media_landing_page.scss';

import SearchResultCard from '../../js/components/SearchResultCard';

ReactDOM.render(
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
    RowComponent={SearchResultCard}
    RowComponentList={MediaListing}
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
      colClass: 'title',
    }, {
      colSpan: 1,
      colTitle: 'Expert',
      colClass: 'authors',
    }, {
      colSpan: 1,
      colTitle: 'Type',
      colClass: 'type',
    }, {
      colSpan: 4,
      colTitle: 'Topic',
      colClass: 'topics',
    },
    {
      colSpan: 1,
      colTitle: 'More',
      colClass: 'more',
    }]}
  />,
  document.getElementById('media-search-table'),
);
