import PropTypes from 'prop-types';
import React from 'react';
import AnnualReportNav from './AnnualReportNav';

function AnnualReportTitleSlide({
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

AnnualReportTitleSlide.propTypes = {
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

AnnualReportTitleSlide.defaultProps = {
  prevSlide: null,
  nextSlide: null,
};

export default AnnualReportTitleSlide;
