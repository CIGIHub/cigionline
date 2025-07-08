import './css/opinion_series_list_page.scss';
import React from 'react';
import { createRoot } from 'react-dom/client';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

const root = createRoot(document.getElementById('opinion-series-list'));
root.render(
  <SearchTable
    blockListing
    contenttypes={[
      'Opinion Series',
    ]}
    limit={10}
    fields={[
      'series_authors',
      'publishing_date',
    ]}
    RowComponent={PublicationListingSimple}
  />,
);
