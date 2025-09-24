import PropTypes from 'prop-types';
import React from 'react';
import AnnualReportNav from '../annual_report/AnnualReportNav';

function AnnualReportTextSlide({
  slides,
  basePath,
  prevSlide,
  nextSlide,
  currentIndex,
}) {
  return (
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
}

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
