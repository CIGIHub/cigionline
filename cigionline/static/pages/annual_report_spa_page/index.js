import './css/annual_report_spa_page.scss';
import React from 'react';
import { createRoot } from 'react-dom/client';
import AnnualReportSPA from '../../js/components/annual_report/AnnualReportSPA';

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

const root = createRoot(document.getElementById('annual-report-spa'));
root.render(
  <AnnualReportSPA annualReportSPAId={annualReportSPAId} basePath={basePath} />,
);
