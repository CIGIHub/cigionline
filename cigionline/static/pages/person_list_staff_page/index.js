import React from 'react';
import ReactDOM from 'react-dom';
import StaffListing from '../../js/components/StaffListing';
import StaffListingHeading from '../../js/components/StaffListingHeading';
import SearchTable from '../../js/components/SearchTable';
import './css/person_list_staff_page.scss';

ReactDOM.render(
  <SearchTable
    blockListing
    contentType="people.PersonPage"
    persontypes={['Staff']}
    limit={50}
    fields={[
      'email',
      'last_name',
      'phone_number',
      'position',
      'title',
      'url',
      'id',
    ]}
    RowComponent={StaffListing}
    paginateAlphabetically
    BlockListingHeading={StaffListingHeading}
  />,
  document.getElementById('staff-list'),
);
