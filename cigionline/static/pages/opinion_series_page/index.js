import './css/opinion_series_page.scss';

/* global opinionSeriesId */
import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListingSeries from '../../js/components/PublicationListingSeries';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (opinionSeriesId) {
  endpointParams.push({
    paramName: 'opinionseriesid',
    paramValue: opinionSeriesId,
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
  document.getElementById('opinions-list'),
);
