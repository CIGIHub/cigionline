import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

function StrategicPlanVerticalTitle({ currentIndex, slide }) {
  return (
    <>
      {slide.display_vertical_title && (
        <motion.div
          key={`vertical-title-${currentIndex}`}
          className="vertical-title-container"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.5, ease: 'easeInOut' }}
        >
          <svg
            className="hide-for-large"
            version="1.1"
            id="Layer_1"
            x="0px"
            y="0px"
            viewBox="0 0 45.9 25.6"
            enableBackground="new 0 0 45.9 25.6"
            xmlSpace="preserve"
          >
            <path d="M11.5,11.5v2.6c-1.3-1.1-2.6-1.6-3.9-1.6c-1.5,0-2.8,0.5-3.8,1.6S2.3,16.5,2.3,18s0.5,2.8,1.5,3.9s2.3,1.6,3.8,1.6c0.8,0,1.4-0.1,2-0.4c0.3-0.1,0.6-0.3,0.9-0.5c0.3-0.2,0.7-0.5,1-0.8v2.7c-1.3,0.7-2.6,1.1-4,1.1c-2.1,0-3.9-0.7-5.3-2.2C0.7,21.9,0,20.2,0,18.1c0-1.9,0.6-3.5,1.8-5c1.5-1.8,3.5-2.7,5.9-2.7C9,10.5,10.3,10.8,11.5,11.5z" />
            <path d="M18.9,10.7v14.6h-2.2V10.7H18.9z" />
            <path d="M32.3,17.7h6v0.5c0,1.1-0.1,2.1-0.4,2.9c-0.3,0.8-0.7,1.5-1.3,2.2c-1.4,1.5-3.1,2.3-5.2,2.3c-2,0-3.8-0.7-5.2-2.2c-1.5-1.5-2.2-3.3-2.2-5.3c0-2.1,0.7-3.9,2.2-5.4s3.3-2.2,5.4-2.2c1.1,0,2.2,0.2,3.2,0.7c0.9,0.5,1.9,1.2,2.8,2.3L36,15c-1.2-1.6-2.7-2.4-4.4-2.4c-1.5,0-2.8,0.5-3.9,1.6c-1,1-1.6,2.4-1.6,3.9c0,1.6,0.6,3,1.7,4s2.3,1.5,3.5,1.5c1.1,0,2.1-0.4,2.9-1.1c0.9-0.7,1.3-1.6,1.4-2.6H32v-2.2H32.3z" />
            <path d="M45.8,10.7v14.6h-2.2V10.7H45.8z" />
            <rect y="0" width="45.9" height="3.6" />
          </svg>
          <div className="vertical-line" />
          <div className="vertical-title">Strategic Plan</div>
          <div className="vertical-line" />
          <div className="page-num">{currentIndex - 1}</div>
        </motion.div>
      )}
    </>
  );
}

StrategicPlanVerticalTitle.propTypes = {
  currentIndex: PropTypes.number.isRequired,
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanVerticalTitle;
