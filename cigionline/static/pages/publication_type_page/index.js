import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

const publicationTypeId = document.getElementById('publications-list').getAttribute('data-publication-type-id');
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
      'publishing_date',
    ]}
    RowComponent={PublicationListingSimple}
  />,
  document.getElementById('publications-list'),
);
