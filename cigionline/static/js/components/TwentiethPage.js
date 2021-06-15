import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';

const TwentiethPage = (props) => {
  const { slides } = props;
  const slidesCount = slides.length;
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const topBar = document.getElementsByClassName('cigi-top-bar')[0];
  useEffect(() => {
    if (!topBar.classList.contains('scrolled-nav')) {
      if (currentSlideIndex > 0) {
        topBar.classList.add('scrolled-nav');
      }
    } else if (currentSlideIndex === 0) {
      topBar.classList.remove('scrolled-nav');
    }
  });

  return (
    <>
      <div className="slides">
        <TwentiethPageSlide
          slide={slides[currentSlideIndex]}
          key={currentSlideIndex}
        />
      </div>
      <TwentiethPageNavArrows
        currentSlideIndex={currentSlideIndex}
        setCurrentSlideIndex={setCurrentSlideIndex}
        slidesCount={slidesCount}
      />
    </>
  );
};

TwentiethPage.propTypes = {};

export default TwentiethPage;
