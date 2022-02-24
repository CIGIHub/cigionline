import React from 'react';
import ReactDOM from 'react-dom';
import SearchTableExperts from '../../js/components/SearchTableExperts';
import './css/person_list_experts_page.scss';

const revisionDate = document.getElementById('experts-search-table').dataset.revisionDate;

ReactDOM.render(
  <SearchTableExperts revisionDate={revisionDate} />,
  document.getElementById('experts-search-table'),
);
