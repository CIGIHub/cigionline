import React from 'react';
import { createRoot } from 'react-dom/client';
import ResearchContentListing from '../../js/components/ResearchContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/research_landing_page.scss';

const root = createRoot(document.getElementById('research-search-table'));
root.render(
  <SearchTable
    showSearch
    contenttypes={[
      'Publication',
      'Opinion',
      'Event',
      'Multimedia',
      'Activity',
    ]}
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
      name: 'Essays',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Essays',
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
    },
    {
      name: 'Research Project',
      alias: 'research.ProjectPage',
      aggregationField: 'content_types',
      params: [{
        name: 'content_type',
        value: 'research.ProjectPage',
      }],
    }]}
    exclusions={['working-papers', 'unofficial-publications']}
    RowComponent={ResearchContentListing}
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
