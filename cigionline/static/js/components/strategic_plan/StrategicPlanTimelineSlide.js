import React from 'react';
import { motion } from 'framer-motion';
import PropTypes from 'prop-types';

const timelineLabels = {
  1: {
    title: 'July to September 2024',
  },
  2: {
    title: 'September to January 2025',
  },
  3: {
    title: 'February to April 2025',
  },
};

const months = [
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
  'Jan',
  'Feb',
  'Mar',
  'Apr',
];

const StrategicPlanTimelineSlide = ({ slide }) => (
  <div className="strategic-plan-slide timeline-slide">
    <div className={`row`}>
      <motion.div
        className="regular-slide__title col"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
      >
        {slide.slide_title && (
          <h1 aria-live="assertive">{slide.slide_title}</h1>
        )}
      </motion.div>
    </div>
    <motion.div
      className="timeline-container"
      initial={{ opacity: 0, y: 0 }}
      animate={{ opacity: 1, y: -20 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5, delay: 1, ease: 'easeInOut' }}
    >
      <div className="position-relative d-flex justify-content-between align-items-end mt-4">
        {months.map((month, index) => (
          <div key={month} className="month-container text-center">
            <div
              className={`month-line mx-auto ${month.toLowerCase()} ${
                index === 0 || index === months.length - 1
                  ? 'long-line'
                  : 'short-line'
              }`}
            />
            <div className="mt-2">{month}</div>
          </div>
        ))}
        <motion.div
          className="timeline-bar timeline-bar-1"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.75, delay: 2, ease: 'easeInOut' }}
        />
        <motion.div
          className="timeline-bar timeline-bar-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.75, delay: 3, ease: 'easeInOut' }}
        />
        <motion.div
          className="timeline-bar timeline-bar-3"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.75, delay: 4, ease: 'easeInOut' }}
        />
      </div>
    </motion.div>
    <div className="slide-content">
      <div className="row">
        {slide.slide_content.columns?.map((content, index) => (
          <motion.div
            key={index}
            className={`col-lg-4`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{
              duration: 0.75,
              delay: 2 + index,
              ease: 'easeInOut',
            }}
          >
            <div
              className={`column-${index}`}
              dangerouslySetInnerHTML={{ __html: content }}
            />
          </motion.div>
        ))}
      </div>
    </div>
  </div>
);

StrategicPlanTimelineSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanTimelineSlide;
