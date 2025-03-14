import React from 'react';
import { motion } from 'framer-motion';
import PropTypes from 'prop-types';

const StrategicPlanTimelineSlide = ({ slide }) => (
  <div className={`strategic-plan-slide timeline-slide`}></div>
);

StrategicPlanTimelineSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanTimelineSlide;
