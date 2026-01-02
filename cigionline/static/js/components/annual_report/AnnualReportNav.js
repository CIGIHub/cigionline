import PropTypes from 'prop-types';
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../../../css/components/annual_reports/AnnualReportNav.scss';

const slideTypeBackgrounds = {
  chairs_message: 'white',
  presidents_message: 'white',
  outputs_and_activities: 'white',
  financials: 'white',
};

function AnnualReportNav({
  slides,
  basePath,
  currentIndex,
  fadeableClass,
  lang,
  setHoverNav,
  lightHeaderClass,
}) {
  const navigate = useNavigate();

  const prevSlide = slides[currentIndex - 1] || null;
  const nextSlide = slides[currentIndex + 1] || null;

  const handleNavigation = (slide) => {
    if (slide) {
      navigate(`${basePath}/${lang}/${slide.slug}`);
    }
  };
  const backgroundClass = `background-${
    slideTypeBackgrounds[slides[currentIndex].slide_type] || 'black'
  }`;

  return (
    <div className={`annual-report-nav ${backgroundClass} ${fadeableClass} ${lightHeaderClass}`}>
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
      <div className={`dot-nav d-none d-lg-block ${backgroundClass} ${lightHeaderClass}`}>
        {slides.map((slide, index) => (
          <div key={slide.slug}>
            {currentIndex === index ? (
              <li
                className="current-item"
                onMouseLeave={() => setHoverNav(false)}
              >
                <div className="dot-nav-tooltip">
                  <span
                    dangerouslySetInnerHTML={{
                      __html:
                        lang === 'fr'
                          ? slide.slide_title_fr
                          : slide.slide_title,
                    }}
                  />
                </div>
                <div className="current-page">
                  <div className="dot-circle" />
                </div>
              </li>
            ) : (
              <li
                className="link-item"
                onMouseEnter={() => setHoverNav(true)}
                onMouseLeave={() => setHoverNav(false)}
              >
                <div className="dot-nav-tooltip">
                  <span
                    dangerouslySetInnerHTML={{
                      __html:
                        lang === 'fr'
                          ? slide.slide_title_fr
                          : slide.slide_title,
                    }}
                  />
                </div>
                <Link
                  to={`${basePath}/${lang}/${slide.slug}`}
                  className="link-dot"
                >
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
  lang: PropTypes.string.isRequired,
  setHoverNav: PropTypes.func.isRequired,
  lightHeaderClass: PropTypes.string.isRequired,
};

export default AnnualReportNav;
