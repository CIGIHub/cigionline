import './css/publication_series_list_page.scss';
import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    contenttypes={[
      'Publication Series',
    ]}
    limit={10}
    fields={[
      'series_authors',
      'publishing_date',
    ]}
    RowComponent={PublicationListingSimple}
  />,
  document.getElementById('publications-list'),
);
