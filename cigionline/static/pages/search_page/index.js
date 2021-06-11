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
      param: 'content_type',
      value: 'events.EventPage',
      subtypes: ['Private', 'Public']
    }, {
      name: 'Multimedia',
      param: 'content_type',
      value: 'multimedia.MultimediaPage',
      subtypes: ['Video', 'Podcast']
    }, {
      name: 'Opinion',
      param: 'content_type',
      value: 'articles.ArticlePage',
    }, {
      name: 'Publication',
      param: 'content_type',
      value: 'publications.PublicationPage',
      subtypes: ['Books', 'Conference Reports', 'Essay Series', 'Papers', 'Policy Briefs', 'Policy Memos', 'Special Reports']
    }, {
      name: 'Staff/Expert',
      param: 'content_type',
      value: 'people.PersonPage',
    }]}
    RowComponent={SearchResultListing}
  />,
  document.getElementById('search-table'),
);
