import 'regenerator-runtime/runtime';
import React from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter as Router } from 'react-router-dom';
import '../../../css/components/StrategicPlanSPA.scss';
import StrategicPlan from './StrategicPlan';

function StrategicPlanSPA({ strategicPlanSPAId, basePath }) {
  return (
    <Router>
      <StrategicPlan strategicPlanSPAId={strategicPlanSPAId} basePath={basePath} />
    </Router>
  );
}

StrategicPlanSPA.propTypes = {
  strategicPlanSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default StrategicPlanSPA;
