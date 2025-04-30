import './css/publication_series_list_page.scss';
import React from 'react';
import { createRoot } from 'react-dom/client';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

const root = createRoot(document.getElementById('publications-list'));
root.render(
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
);
