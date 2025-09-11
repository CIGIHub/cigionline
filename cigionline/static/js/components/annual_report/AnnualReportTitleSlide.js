import PropTypes from 'prop-types';
import React from 'react';

function AnnualReportTitleSlide({ slide }) {
  console.log(slide);
  return (
    <div className="regular-slide">
      <div />
    </div>
  );
}

AnnualReportTitleSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default AnnualReportTitleSlide;
