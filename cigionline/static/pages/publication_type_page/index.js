/* global publicationTypeId */
import React from 'react';
import { createRoot } from 'react-dom/client';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (publicationTypeId) {
  endpointParams.push({
    paramName: 'publicationtypeid',
    paramValue: publicationTypeId,
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
      'publishing_date',
    ]}
    RowComponent={PublicationListingSimple}
  />,
);
