import React from 'react';
import ReactDOM from 'react-dom';
import StaffList from '../../js/components/StaffList';
import './css/person_list_staff_page.scss';

ReactDOM.render(
  <StaffList />,
  // <SearchTable
  //   blockListing
  //   contentType="people.PersonPage"
  //   persontypes={['Staff']}
  //   limit={50}
  //   fields={[
  //     'email',
  //     'last_name',
  //     'phone_number_clean',
  //     'position',
  //     'title',
  //     'url',
  //     'id',
  //   ]}
  //   RowComponent={StaffListing}
  //   paginateAlphabetically
  //   BlockListingHeading={StaffListingHeading}
  // />,
  document.getElementById('staff-list'),
);
