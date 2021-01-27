/* global publicationTypeId */
import React from 'react';
import ReactDOM from 'react-dom';
import PublicationListingSimple from '../../js/components/PublicationListingSimple';
import SearchTable from '../../js/components/SearchTable';

const endpointParams = [];
if (publicationTypeId) {
  endpointParams.push({
    paramName: 'publication_type',
    paramValue: publicationTypeId,
  });
}

ReactDOM.render(
  <SearchTable
    blockListing
    endpoint="/publications"
    endpointParams={endpointParams}
    limit={10}
    fields={[
      'authors(author(title,url))',
      'publication_type(title)',
      'publishing_date',
      'title',
      'url',
    ]}
    RowComponent={PublicationListingSimple}
  />,
  document.getElementById('publications-list'),
);
