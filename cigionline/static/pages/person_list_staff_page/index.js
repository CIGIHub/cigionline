import React from 'react';
import { createRoot } from 'react-dom/client';
import StaffList from '../../js/components/StaffList';
import './css/person_list_staff_page.scss';

const root = createRoot(document.getElementById('staff-list'));
root.render(<StaffList />);
