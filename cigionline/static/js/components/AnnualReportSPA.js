import 'regenerator-runtime/runtime';
import React from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter as Router } from 'react-router-dom';
import '../../css/components/AnnualReportSlide.scss';
import AnnualReport from './AnnualReport';

const AnnualReportSPA = ({ annualReportSPAId, basePath }) => (
  <Router>
    <AnnualReport annualReportId={annualReportSPAId} basePath={basePath} />
  </Router>
);

AnnualReportSPA.propTypes = {
  annualReportSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSPA;
