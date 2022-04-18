import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import AnnualReportPage from '../../js/components/AnnualReportPage';
import 'swiper/components/navigation/navigation.min.css';

import './css/styles.css';
import './css/vendor.css';
import './css/annual_report.css';

window.annualReport = JSON.parse(
  document.getElementById('annual-report-json').textContent,
);

const annualReport = JSON.parse(
  document.getElementById('annual-report-json').textContent,
);

ReactDOM.render(
  <Router>
    <AnnualReportPage
      annualReport={annualReport}
    />
  </Router>,
  document.getElementById('annual-report-interactives'),
);
