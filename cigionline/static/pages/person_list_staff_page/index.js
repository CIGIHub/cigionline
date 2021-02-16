import React from 'react';
import ReactDOM from 'react-dom';
import StaffListing from '../../js/components/StaffListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    blockListing
    contentType="people.PersonPage"
    persontypes={['Staff']}
    limit={50}
    fields={[
      'email',
      'phone_number',
      'position',
      'title',
      'url',
      'id',
    ]}
    RowComponent={StaffListing}
  />,
  document.getElementById('staff-list'),
);
