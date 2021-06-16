import React from 'react';
import ReactDOM from 'react-dom';
import SearchResultListing from '../../js/components/SearchResultListing';
import SearchTable from '../../js/components/SearchTable';
import './css/search_page.scss';

ReactDOM.render(
  <SearchTable
    blockListing
    isSearchPage
    showCount
    showSearch
    sortOptions={[{
      default: true,
      name: 'Relevance',
      value: 'relevance',
    }, {
      name: 'Date',
      value: 'date',
    }]}
    fields={[
      'authors',
      'contenttype',
      'contentsubtype',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'search-result-row',
    ]}
    filterTypes={[{
      name: 'Event',
      params: [{
        name: 'contenttype',
        value: 'Event',
      }],
    }, {
      name: 'Private',
      parent: 'Event',
      params: [{
        name: 'contentsubtype',
        value: 'Private',
      }],
    }, {
      name: 'Public',
      parent: 'Event',
      params: [{
        name: 'contentsubtype',
        value: 'Public',
      }],
    }, {
      name: 'Multimedia',
      params: [{
        name: 'contenttype',
        value: 'Multimedia',
      }],
    }, {
      name: 'Video',
      parent: 'Multimedia',
      params: [{
        name: 'contentsubtype',
        value: 'Video',
      }],
    }, {
      name: 'Podcast',
      alias: 'Audio',
      parent: 'Multimedia',
      params: [{
        name: 'contentsubtype',
        value: 'Audio',
      }],
    }, {
      name: 'Publication',
      params: [{
        name: 'contenttype',
        value: 'Publication',
      }],
    }, {
      name: 'Books',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'Books',
      }],
    }, {
      name: 'Conference Reports',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'Conference Reports',
      }],
    }, {
      name: 'Essay Series',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'Essay Series',
      }],
    }, {
      name: 'Papers',
      alias: 'CIGI Papers',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI Papers',
      }],
    }, {
      name: 'Policy Briefs',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'Policy Briefs',
      }],
    }, {
      name: 'Policy Memos',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'Policy Memos',
      }],
    }, {
      name: 'Special Reports',
      parent: 'Publication',
      params: [{
        name: 'contentsubtype',
        value: 'Special Reports',
      }],
    }, {
      name: 'Staff/Expert',
      alias: 'people.PersonPage',
      aggregationField: 'content_types',
      params: [{
        name: 'content_type',
        value: 'people.PersonPage',
      }],
    }, {
      name: 'Opinion',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Opinion',
      }],
    }, {
      name: 'CIGI In the News',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI In the News',
      }],
    }, {
      name: 'News Releases',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'News Releases',
      }],
    }, {
      name: 'Op-Eds',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Op-Eds',
      }],
    }].sort((a, b) => a.name.localeCompare(b.name))}
    RowComponent={SearchResultListing}
  />,
  document.getElementById('search-table'),
);
