import './css/annual_report_spa_page.scss';
import React from 'react';
import ReactDOM from 'react-dom';
import App from '../../js/components/AnnualReportSPA';

const annualReportSPAId =
  document.getElementById('annual-report-spa').dataset.annualReportId;
console.log(annualReportSPAId);
ReactDOM.render(
  <App annualReportSPAId={annualReportSPAId} />,
  document.getElementById('annual-report-spa'),
);
