import React from 'react';
import ReactDOM from 'react-dom';
import SearchResultListingRow from '../../js/components/SearchResultListingRow';
import SearchResultCard from '../../js/components/SearchResultCard';
import SearchTable from '../../js/components/SearchTable';
import './css/search_page.scss';

const livePageCount = Number(document.getElementById('search-table').dataset.livePageCount).toLocaleString('en-US');
ReactDOM.render(
  <SearchTable
    isSearchPage
    RowComponent={SearchResultCard}
    RowComponentList={SearchResultListingRow}
    showCount
    showSearch
    showExpertDropDown
    searchPlaceholder={`Explore ${livePageCount} pages of CIGI research and analysis`}
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
      'board_position',
      'contenttype',
      'contentsubtype',
      'expertise_list',
      'image_poster_url',
      'image_hero_url',
      'image_hero_wide_url',
      'image_square_url',
      'publishing_date',
      'search_result_description',
      'theme_name',
      'linkedin_username',
      'twitter_username',
      'topics',
      'event_access',
      'time_zone_label',
      'event_format_string',
      'event_end',
      'registration_url',
      'event_access',
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
    }, {
      name: 'Op-Eds',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Op-Eds',
      }],
    }, {
      name: 'Research Project',
      alias: 'research.ProjectPage',
      aggregationField: 'content_types',
      params: [{
        name: 'content_type',
        value: 'research.ProjectPage',
      }],
    }].sort((a, b) => a.name.localeCompare(b.name))}
  />,
  document.getElementById('search-table'),
);
