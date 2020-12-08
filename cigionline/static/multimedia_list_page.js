import React from 'react';
import ReactDOM from 'react-dom';
import MultimediaListing from './js/components/MultimediaListing';
import SearchTable from './js/components/SearchTable';

ReactDOM.render(
  <SearchTable endpoint="/multimedia" limit={18} fields="title,url,publishing_date,topics(title,url),image_hero_url,speakers" containerClass={['row', 'row-cols-1', 'row-cols-sm-2', 'row-cols-md-3', 'multimedia-list-row']} RowComponent={MultimediaListing} />,
  document.getElementById('multimedia-search-table'),
);
