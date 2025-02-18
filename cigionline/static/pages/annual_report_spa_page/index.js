import './css/annual_report_spa_page.scss';
import React from 'react';
import ReactDOM from 'react-dom';
import AnnualReportSPA from '../../js/components/AnnualReportSPA';

const normalizeBasePath = (path) => {
  const url = new URL(path, window.location.origin);
  return url.pathname.replace(/\/$/, '');
};

const annualReportSPAId =
  document.getElementById('annual-report-spa').dataset.annualReportId;
const BASE_PATH = document
  .getElementById('annual-report-spa')
  .dataset.basePath.replace(/\/$/, '');
const basePath = normalizeBasePath(BASE_PATH);
ReactDOM.render(
  <AnnualReportSPA annualReportSPAId={annualReportSPAId} basePath={basePath} />,
  document.getElementById('annual-report-spa'),
);
