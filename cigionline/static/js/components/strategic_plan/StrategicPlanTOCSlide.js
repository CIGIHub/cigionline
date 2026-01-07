import PropTypes from 'prop-types';
import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

function StrategicPlanTOCSlide({ slides, basePath, currentIndex }) {
  return (
    <div className="strategic-plan-slide table-of-contents">
      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        aria-live="assertive"
      >
        {slides[currentIndex].slide_title}
      </motion.h1>
      <motion.ol
        start="2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.5, ease: 'easeInOut', delay: 0.75 }}
      >
        {slides.map(
          (slide) => slide.include_on_toc && (
            <li key={slide.slug}>
              <Link to={`${basePath}/${slide.slug}`}>
                {slide.slide_title.replace('.', '')}
              </Link>
            </li>
          ),
        )}
      </motion.ol>
    </div>
  );
}

StrategicPlanTOCSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
};

export default StrategicPlanTOCSlide;
