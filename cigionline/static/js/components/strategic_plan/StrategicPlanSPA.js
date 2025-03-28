import 'regenerator-runtime/runtime';
import React from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter as Router } from 'react-router-dom';
import '../../../css/components/AnnualReportSPA.scss';
import '../../../css/components/StrategicPlanSPA.scss';
import StrategicPlan from './StrategicPlan';

const StrategicPlanSPA = ({ strategicPlanSPAId, basePath }) => (
  <Router>
    <StrategicPlan strategicPlanSPAId={strategicPlanSPAId} basePath={basePath} />
  </Router>
);

StrategicPlanSPA.propTypes = {
  strategicPlanSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default StrategicPlanSPA;
