/* global publicationTypeId */
import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (publicationTypeId) {
  endpointParams.push({
    paramName: 'publicationtypeid',
    paramValue: publicationTypeId,
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
      'publishing_date',
    ]}
    RowComponent={PublicationListingSimple}
  />,
  document.getElementById('publications-list'),
);
