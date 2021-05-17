import React from 'react';
import ReactDOM from 'react-dom';
import MultimediaListing from '../../js/components/MultimediaListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
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
      param: 'contentsubtype',
      value: 'Video',
    }, {
      name: 'Audio',
      param: 'contentsubtype',
      value: 'Audio',
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
  document.getElementById('multimedia-search-table'),
);
