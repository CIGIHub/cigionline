/* eslint-disable react/prop-types */
import React from 'react';
import Portal from './Portal';

function TwentiethPageNavArrows({ changeSlide, slide }) {
  function prevSlide() {
    changeSlide(slide.prev_slide);
  }

  function nextSlide() {
    changeSlide(slide.next_slide);
  }

  return (
    <Portal>
      {slide.prev_slide && (
        <button className="prev-slide" type="button" onClick={prevSlide} aria-label="Previous Slide">
          <i className="fal fa-angle-up" />
        </button>
      )}
      {slide.next_slide && (
        <button className="next-slide" type="button" onClick={nextSlide} aria-label="Next Slide">
          <i className="fal fa-angle-down" />
        </button>
      )}
    </Portal>
  );
}

export default TwentiethPageNavArrows;
