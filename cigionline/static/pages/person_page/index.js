/* global personId */
import React from 'react';
import { createRoot } from 'react-dom/client';
import ExpertContentListing from '../../js/components/ExpertContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/person_page.scss';

function readJsonScript(id) {
  const el = document.getElementById(id);
  if (!el) return null;

  const raw = (el.textContent || '').trim();
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

const additionalAuthoredPages = readJsonScript('additional-authored-pages');

const endpointParams = [];

if (Array.isArray(additionalAuthoredPages) && additionalAuthoredPages.length) {
  const ids = additionalAuthoredPages
    .map((p) => p?.id)
    .filter((id) => Number.isInteger(id) || (typeof id === 'string' && id));

  if (ids.length) {
    endpointParams.push({
      paramName: 'additional_authored_pages',
      paramValue: ids.join(','),
    });
  }
}

if (personId) {
  endpointParams.push({
    paramName: 'author',
    paramValue: personId,
  });
}

const root = createRoot(document.getElementById('expert-search-table'));
root.render(
  <SearchTable
    endpointParams={endpointParams}
    fields={[
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    containerClass={['custom-theme-table']}
    limit={14}
    RowComponent={ExpertContentListing}
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
        colTitle: 'Type',
      },
      {
        colSpan: 1,
        colTitle: 'PDF',
      },
    ]}
    showSidebar={false}
  />,
);
