import React from 'react';
import { createRoot } from 'react-dom/client';
import MultimediaListing from '../../js/components/MultimediaListing';
import SearchTable from '../../js/components/SearchTable';

const root = createRoot(document.getElementById('multimedia-search-table'));
root.render(
  <SearchTable
    blockListing
    contenttypes={[
      'Multimedia',
    ]}
    showSearch
    limit={18}
    fields={[
      'authors',
      'contentsubtype',
      'image_hero_url',
      'publishing_date',
      'topics',
    ]}
    filterTypes={[{
      name: 'Video',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Video',
      }],
    }, {
      name: 'Audio',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Audio',
      }],
    }]}
    containerClass={[
      'row',
      'row-cols-1',
      'row-cols-sm-2',
      'row-cols-md-3',
      'multimedia-list-row',
    ]}
    RowComponent={MultimediaListing}
  />,
);
