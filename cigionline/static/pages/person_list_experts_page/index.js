import React from 'react';
import ReactDOM from 'react-dom';
import ExpertListing from '../../js/components/ExpertListing';
import SearchTable from '../../js/components/SearchTable';

ReactDOM.render(
  <SearchTable
    showSearch
    endpoint="/experts"
    limit={100}
    fields={[
      'expertise_list',
      'image_square_url',
      'latest_activity_json',
      'position',
      'title',
      'url',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    orderTypes={[{
      default: true,
      name: 'Last Name',
      value: 'last_name',
    }, {
      name: 'First Name',
      value: 'first_name',
    }]}
    RowComponent={ExpertListing}
    searchPlaceholder="Search experts"
    tableColumns={[{
      colSpan: 3,
      colTitle: 'Name',
    }, {
      colSpan: 4,
      colTitle: 'Expertise',
    }, {
      colSpan: 4,
      colTitle: 'Recent Activity',
    }]}
  />,
  document.getElementById('experts-search-table'),
);
