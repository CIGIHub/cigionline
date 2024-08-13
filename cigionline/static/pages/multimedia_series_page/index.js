import './css/multimedia_series_page.scss';

import React from 'react';
import ReactDOM from 'react-dom';
import MultimediaListingSeries from '../../js/components/MultimediaListingSeries';
import SearchTable from '../../js/components/SearchTable';

const multimediaSeriesId = document.getElementById('multimedia-list').getAttribute('data-multimedia-series-id');
const endpointParams = [];
if (multimediaSeriesId) {
  endpointParams.push({
    paramName: 'multimediaseriesid',
    paramValue: multimediaSeriesId,
  });
}

ReactDOM.render(
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
  document.getElementById('multimedia-list'),
);
