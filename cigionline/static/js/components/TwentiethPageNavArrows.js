import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageNavArrows = ({ changeSlide, slide }) => (
  <>
    {slide.prev_slide && (
      <button
        className="prev-slide"
        type="button"
        onClick={() => changeSlide(slide.prev_slide)}
      >
        <i className="fal fa-angle-up" />
      </button>
    )}
    {slide.next_slide && (
      <button
        className="next-slide"
        type="button"
        onClick={() => changeSlide(slide.next_slide)}
      >
        <i className="fal fa-angle-down" />
      </button>
    )}
  </>
);

TwentiethPageNavArrows.propTypes = {};

export default TwentiethPageNavArrows;
