import PropTypes from 'prop-types';
import React from 'react';
import { Link } from 'react-router-dom';

const StrategicPlanTOCSlide = ({ slides, basePath, currentIndex }) => (
  <div className="strategic-plan-slide table-of-contents">
    <h1 aria-live="assertive">{slides[currentIndex].slide_title}</h1>
    <ol start="2">
      {slides.map(
        (slide) =>
          slide.include_on_toc && (
            <li key={slide.slug}>
              <Link
                to={`${basePath}/${slide.slug}`}
                replace={false}
                onClick={() => window.scrollTo(0, 0)}
              >
                {slide.slide_title}
              </Link>
            </li>
          ),
      )}
    </ol>
  </div>
);

StrategicPlanTOCSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
};

export default StrategicPlanTOCSlide;
