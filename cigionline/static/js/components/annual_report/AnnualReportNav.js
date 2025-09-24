import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import '../../../css/components/annual_reports/AnnualReportNav.scss';

function AnnualReportNav({ slides, basePath, currentIndex }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const prevSlide = slides[currentIndex - 1] || null;
  const nextSlide = slides[currentIndex + 1] || null;

  const handleNavigation = (slide) => {
    if (slide) {
      navigate(`${basePath}/${slide.slug}`);
    }
  };

  return (
    <>
      {prevSlide && (
        <button
          type="button"
          className="nav-arrow nav-arrow-top"
          onClick={() => handleNavigation(prevSlide)}
          aria-label="Previous Slide"
        >
          <span>Previous Slide</span>
        </button>
      )}
      {nextSlide && (
        <button
          type="button"
          className="nav-arrow nav-arrow-bottom"
          onClick={() => handleNavigation(nextSlide)}
          aria-label="Next Slide"
        >
          <span>Next Slide</span>
        </button>
      )}
      <div className="slide-nav">
        {slides.map((slide, index) => (
          <div
            key={slide.slug}
            className="nav-item-wrapper"
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <AnimatePresence>
              {hoveredIndex === index && (
                <motion.div
                  className="nav-tooltip"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                >
                  {slide.slide_title}
                </motion.div>
              )}
            </AnimatePresence>

            <Link
              to={`${basePath}/${slide.slug}`}
              className={`nav-circle ${
                location.pathname.includes(slide.slug) ? 'active' : ''
              }`}
            >
              <span />
            </Link>
          </div>
        ))}
      </div>
    </>
  );
}

AnnualReportNav.propTypes = {
  slides: PropTypes.array.isRequired,
  basePath: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
};

export default AnnualReportNav;
