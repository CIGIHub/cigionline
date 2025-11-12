import 'regenerator-runtime/runtime';
import React from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter as Router } from 'react-router-dom';
import '../../../css/components/annual_reports/AnnualReportSPA.scss';
import AnnualReport from './AnnualReport';

function AnnualReportSPA({ annualReportSPAId, basePath }) {
  return (
    <Router>
      <AnnualReport annualReportSPAId={annualReportSPAId} basePath={basePath} />
    </Router>
  );
}

AnnualReportSPA.propTypes = {
  annualReportSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSPA;
