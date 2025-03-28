import './css/publication_series_page.scss';

/* global publicationSeriesId */
import React from 'react';
import { createRoot } from 'react-dom/client';
import PublicationListingSeries from '../../js/components/PublicationListingSeries';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (publicationSeriesId) {
  endpointParams.push({
    paramName: 'publicationseriesid',
    paramValue: publicationSeriesId,
  });
}

const root = createRoot(document.getElementById('publications-list'));
root.render(
  <SearchTable
    blockListing
    endpointParams={endpointParams}
    limit={10}
    fields={[
      'authors',
      'pdf_download',
      'publishing_date',
      'short_description',
      'topics',
    ]}
    RowComponent={PublicationListingSeries}
  />,
);
