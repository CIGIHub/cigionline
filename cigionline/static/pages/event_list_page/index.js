import React from 'react';
import ReactDOM from 'react-dom';
import EventListing from '../../js/components/EventListing';
import SearchTable from '../../js/components/SearchTable';
import EventCalendar from '../../js/components/EventCalendar';
import './css/_event_list_page.scss';

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={['Event']}
    fields={[
      'event_access',
      'location_city',
      'location_country',
      'multimedia_url',
      'publishing_date',
      'registration_url',
      'topics',
    ]}
    filterTypes={[{
      name: 'CIGI Sponsored',
      aggregationField: 'contentsubtypes',
      alias: 'Cigi_Sponsored',
      params: [{
        name: 'contentsubtype',
        value: 'Cigi_Sponsored',
      }],
    }, {
      name: 'Cinema Series',
      aggregationField: 'contentsubtypes',
      alias: 'Cinema_Series',
      params: [{
        name: 'contentsubtype',
        value: 'Cinema_Series',
      }],
    }, {
      name: 'Community Event',
      aggregationField: 'contentsubtypes',
      alias: 'Community_Event',
      params: [{
        name: 'contentsubtype',
        value: 'Community_Event',
      }],
    }, {
      name: 'Conference',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Conference',
      }],
    }, {
      name: 'Global Policy Forum',
      aggregationField: 'contentsubtypes',
      alias: 'Global_Policy_Forum',
      params: [{
        name: 'contentsubtype',
        value: 'Global_Policy_Forum',
      }],
    }, {
      name: 'Noon Lecture Series',
      aggregationField: 'contentsubtypes',
      alias: 'Noon_Lecture_Series',
      params: [{
        name: 'contentsubtype',
        value: 'Noon_Lecture_Series',
      }],
    }, {
      name: 'Panel Discussion',
      aggregationField: 'contentsubtypes',
      alias: 'Panel_Discussion',
      params: [{
        name: 'contentsubtype',
        value: 'Panel_Discussion',
      }],
    }, {
      name: 'Publication Launch',
      aggregationField: 'contentsubtypes',
      alias: 'Publication_Launch',
      params: [{
        name: 'contentsubtype',
        value: 'Publication_Launch',
      }],
    }, {
      name: 'Roundtable',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Roundtable',
      }],
    }, {
      name: 'Seminar',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Seminar',
      }],
    }, {
      name: 'Signature Lecture',
      aggregationField: 'contentsubtypes',
      alias: 'Signature_Lecture',
      params: [{
        name: 'contentsubtype',
        value: 'Signature_Lecture',
      }],
    }, {
      name: 'Virtual Event',
      aggregationField: 'contentsubtypes',
      alias: 'Virtual_Event',
      params: [{
        name: 'contentsubtype',
        value: 'Virtual_Event',
      }],
    }, {
      name: 'Workshop',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Workshop',
      }],
    }]}
    containerClass={['custom-theme-table', 'table-events']}
    RowComponent={EventListing}
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
      },
      {
        colSpan: 3,
        colTitle: 'Topic',
      },
      {
        colSpan: 2,
        colTitle: 'Location',
      },
      {
        colSpan: 1,
        colTitle: '',
      },
    ]}
  />,
  document.getElementById('events-search-table'),
);

ReactDOM.render(
  <EventCalendar />,
  document.getElementById('event-list-calendar'),
);
