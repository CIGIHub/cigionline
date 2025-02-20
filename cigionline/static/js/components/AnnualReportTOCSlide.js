import PropTypes from 'prop-types';
import React from 'react';
import { Link } from 'react-router-dom';

const AnnualReportTOCSlide = ({ slides, basePath, currentIndex }) => (
  <div className="table-of-contents">
    <h1 aria-live="assertive">{slides[currentIndex].slide_title}</h1>
    <ul>
      {slides.map(
        (slide) => slide.include_on_toc
          && (
            <li key={slide.slug}>
              <Link to={`${basePath}/${slide.slug}`}>{slide.slide_title}</Link>
            </li>
          ),
      )}
    </ul>
  </div>
);

AnnualReportTOCSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  prevSlide: PropTypes.shape({
    slug: PropTypes.string,
  }),
  nextSlide: PropTypes.shape({
    slug: PropTypes.string,
  }),
  currentIndex: PropTypes.number.isRequired,
};

AnnualReportTOCSlide.defaultProps = {
  prevSlide: null,
  nextSlide: null,
};

export default AnnualReportTOCSlide;
