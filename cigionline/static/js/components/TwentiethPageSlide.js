import React from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide1Content from './TwentiethPageSlide1Content';
import TwentiethPageSlide2Content from './TwentiethPageSlide2Content';
import TwentiethPageSlide3Content from './TwentiethPageSlide3Content';
import TwentiethPageSlide4Content from './TwentiethPageSlide4Content';
import TwentiethPageSlide5Content from './TwentiethPageSlide5Content';

const TwentiethPageSlide = ({ slide }) => {
  const styles = {};
  if (slide.background && slide.slide_number !== 1) {
    styles.backgroundImage = `url(${slide.background})`;
  }

  return (
    <div className={`slide-${slide.slide_number}`}>
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
};

TwentiethPageSlide.propTypes = {};

export default TwentiethPageSlide;
