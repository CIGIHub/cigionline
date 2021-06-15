import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageNavArrows = ({
  currentSlideIndex,
  setCurrentSlideIndex,
  slidesCount,
}) => (
  <>
    {currentSlideIndex > 0 && (
      <button
        className="prev-slide"
        type="button"
        onClick={() => setCurrentSlideIndex(currentSlideIndex - 1)}
      >
        <i className="fal fa-angle-up" />
      </button>
    )}
    {currentSlideIndex < slidesCount - 1 && (
      <button
        className="next-slide"
        type="button"
        onClick={() => setCurrentSlideIndex(currentSlideIndex + 1)}
      >
        <i className="fal fa-angle-down" />
      </button>
    )}
  </>
);

TwentiethPageNavArrows.propTypes = {};

export default TwentiethPageNavArrows;
