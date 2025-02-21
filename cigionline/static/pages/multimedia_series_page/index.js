import './css/multimedia_series_page.scss';

/* global multimediaSeriesId */
import React from 'react';
import { createRoot } from 'react-dom/client';
import MultimediaListingSeries from '../../js/components/MultimediaListingSeries';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (multimediaSeriesId) {
  endpointParams.push({
    paramName: 'multimediaseriesid',
    paramValue: multimediaSeriesId,
  });
}

const root = createRoot(document.getElementById('multimedia-list'));
root.render(
  <SearchTable
    blockListing
    endpointParams={endpointParams}
    limit={10}
    fields={[
      'authors',
      'contentsubtype',
      'image_hero_url',
      'publishing_date',
      'subtitle',
      'topics',
    ]}
    RowComponent={MultimediaListingSeries}
  />,
);
