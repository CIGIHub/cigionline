import PropTypes from 'prop-types';
import React from 'react';
import AnnualReportNav from './AnnualReportNav';
import AnnualReportSlideList from './AnnualReportSlideList';

function AnnualReportQuoteSlide({
  slides,
  basePath,
  prevSlide,
  nextSlide,
  currentIndex,
}) {
  return (
    <div className="regular-slide">
      <h1 aria-live="assertive">{slides[currentIndex].slide_title}</h1>
      <div
        dangerouslySetInnerHTML={{ __html: slides[currentIndex].slide_content }}
      />
      <AnnualReportSlideList slides={slides} basePath={basePath} />
      <AnnualReportNav
        basePath={basePath}
        prevSlide={prevSlide}
        nextSlide={nextSlide}
      />
    </div>
  );
}

AnnualReportQuoteSlide.propTypes = {
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

AnnualReportQuoteSlide.defaultProps = {
  prevSlide: null,
  nextSlide: null,
};

export default AnnualReportQuoteSlide;
