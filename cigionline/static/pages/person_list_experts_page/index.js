import React from 'react';
import { createRoot } from 'react-dom/client';
import SearchTableExperts from '../../js/components/SearchTableExperts';
import './css/person_list_experts_page.scss';

const revisionDate = document.getElementById('experts-search-table').dataset.revisionDate;

const root = createRoot(document.getElementById('experts-search-table'));
root.render(
  <SearchTableExperts revisionDate={revisionDate} />,
);
