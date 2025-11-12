/* eslint-disable react/prop-types */
import React, { useState } from 'react';
import TwentiethPageSlide1Content from './TwentiethPageSlide1Content';
import TwentiethPageSlide2Content from './TwentiethPageSlide2Content';
import TwentiethPageSlide3Content from './TwentiethPageSlide3Content';
import TwentiethPageSlide4Content from './TwentiethPageSlide4Content';
import TwentiethPageSlide5Content from './TwentiethPageSlide5Content';

function TwentiethPageSlide({ slide, changeSlide }) {
  const styles = {};
  if (slide.background && slide.slide_number !== 1) {
    styles.backgroundImage = `url(${slide.background})`;
  }
  const [touchStart, setTouchStart] = useState(NaN);
  const [touchEnd, setTouchEnd] = useState(NaN);

  function handleTouchStart(e) {
    setTouchStart(e.targetTouches[0].clientY);
  }

  function handleTouchMove(e) {
    setTouchEnd(e.targetTouches[0].clientY);
  }

  function handleTouchEnd() {
    const touchDiff = touchStart - touchEnd;
    if (touchDiff > 150 && slide.next_slide) {
      changeSlide(slide.next_slide);
    }

    if (touchDiff < -150 && slide.prev_slide) {
      changeSlide(slide.prev_slide);
    }
    setTouchStart(NaN);
    setTouchEnd(NaN);
  }

  return (
    <div
      className={`slide-${slide.slide_number}`}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div
        className={`background-image ${
          slide.background_colour ? `background-${slide.background_colour}` : ''
        }`}
        style={styles}
      >
        {slide.theme === 'SLIDE-1' && (
          <TwentiethPageSlide1Content slide={slide} />
        )}
        {slide.theme === 'SLIDE-2' && (
          <TwentiethPageSlide2Content slide={slide} />
        )}
        {slide.theme === 'SLIDE-3' && (
          <TwentiethPageSlide3Content slide={slide} />
        )}
        {slide.theme === 'SLIDE-4' && (
          <TwentiethPageSlide4Content slide={slide} />
        )}
        {slide.theme === 'SLIDE-5' && (
          <TwentiethPageSlide5Content slide={slide} />
        )}
      </div>
    </div>
  );
}

TwentiethPageSlide.propTypes = {};

export default TwentiethPageSlide;
