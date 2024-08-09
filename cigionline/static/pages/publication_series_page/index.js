import './css/publication_series_page.scss';

import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListingSeries from '../../js/components/PublicationListingSeries';
import SearchTable from '../../js/components/SearchTable';

const publicationSeriesId = document.getElementById('publications-list').getAttribute('data-publication-series-id');
const endpointParams = [];
if (publicationSeriesId) {
  endpointParams.push({
    paramName: 'publicationseriesid',
    paramValue: publicationSeriesId,
  });
}

ReactDOM.render(
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
  document.getElementById('publications-list'),
);
