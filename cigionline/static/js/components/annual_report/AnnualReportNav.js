import PropTypes from 'prop-types';
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../../../css/components/annual_reports/AnnualReportNav.scss';

function AnnualReportNav({ slides, basePath, currentIndex, fadeableClass }) {
  const navigate = useNavigate();

  const prevSlide = slides[currentIndex - 1] || null;
  const nextSlide = slides[currentIndex + 1] || null;

  const handleNavigation = (slide) => {
    if (slide) {
      navigate(`${basePath}/${slide.slug}`);
    }
  };

  return (
    <div
      className={`annual-report-nav background-${slides[currentIndex].background_colour} ${fadeableClass}`}
    >
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
      <div
        className={`dot-nav d-none d-lg-block background-${slides[currentIndex].background_colour}`}
      >
        {slides.map((slide, index) => (
          <div key={slide.slug}>
            {currentIndex === index ? (
              <li className="current-item">
                <div className="dot-nav-tooltip">
                  <span>{slide.slide_title}</span>
                </div>
                <div className="current-page">
                  <div className="dot-circle" />
                </div>
              </li>
            ) : (
              <li className="link-item">
                <div className="dot-nav-tooltip">
                  <span>{slide.slide_title}</span>
                </div>
                <Link to={`${basePath}/${slide.slug}`} className="link-dot">
                  <div className="dot-circle" />
                </Link>
              </li>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

AnnualReportNav.propTypes = {
  slides: PropTypes.array.isRequired,
  basePath: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
  fadeableClass: PropTypes.string.isRequired,
};

export default AnnualReportNav;
