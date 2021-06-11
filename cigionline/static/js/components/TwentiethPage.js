import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';

const TwentiethPage = (props) => {
  const { slides } = props;
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const header = document.getElementsByTagName('header')[0];
  useEffect(() => {
    if (!header.classList.contains('minimized')) {
      if (currentSlideIndex > 0) {
        header.classList.add('minimized');
      }
    } else if (currentSlideIndex === 0) {
      header.classList.remove('minimized');
    }
  });

  return (
    <div className="slides">
      <div className="controls d-flex">
        {slides.map((slide) => (
          <div className="" key={slide.slide}>
            <button
              type="button"
              onClick={() => setCurrentSlideIndex(slide.slide - 1)}
            >
              {slide.slide}
            </button>
          </div>
        ))}
      </div>
      <TwentiethPageNavArrows
        currentSlideIndex={currentSlideIndex}
        setCurrentSlideIndex={setCurrentSlideIndex}
      />
      <TwentiethPageSlide
        slide={slides[currentSlideIndex]}
        key={currentSlideIndex}
      />
    </div>
  );
};

TwentiethPage.propTypes = {};

export default TwentiethPage;
