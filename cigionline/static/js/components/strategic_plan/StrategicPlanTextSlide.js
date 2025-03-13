import PropTypes from 'prop-types';
import React from 'react';

const AnnualReportTextSlide = ({
  slides,
  basePath,
  prevSlide,
  nextSlide,
  currentIndex,
}) => (
  <div className="regular-slide">
    <div
      dangerouslySetInnerHTML={{ __html: slides[currentIndex].slide_content }}
    />
    <AnnualReportNav
      basePath={basePath}
      prevSlide={prevSlide}
      nextSlide={nextSlide}
    />
  </div>
);

AnnualReportTextSlide.propTypes = {
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

AnnualReportTextSlide.defaultProps = {
  prevSlide: null,
  nextSlide: null,
};

export default AnnualReportTextSlide;
