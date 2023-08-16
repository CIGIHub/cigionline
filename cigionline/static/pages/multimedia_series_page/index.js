import './css/multimedia_series_page.scss';

/* global multimediaSeriesId */
import React from 'react';
import ReactDOM from 'react-dom';
import MultimediaSeriesListing from '../../js/components/MultimediaSeriesListing';
import SearchTable from '../../js/components/SearchTable';

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
    RowComponent={MultimediaSeriesListing}
  />,
  document.getElementById('multimedia-list'),
);
