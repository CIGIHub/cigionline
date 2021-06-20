import React from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide2Content from './TwentiethPageSlide2Content';
import TwentiethPageSlide3Content from './TwentiethPageSlide3Content';
import TwentiethPageSlide4Content from './TwentiethPageSlide4Content';
import TwentiethPageSlide5Content from './TwentiethPageSlide5Content';

const TwentiethPageSlide = ({ slide, pageBody, topBar }) => {
  // if (slide.slide_number !== 1) {
  //   topBar.classList.add('scrolled-nav');
  // } else topBar.classList.remove('scrolled-nav');

  topBar.classList.add('scrolled-nav');

  const styles = {};
  if (slide.background) {
    styles.backgroundImage = `url(${slide.background})`;
  }
  if (slide.background_colour) {
    styles.backgroundColor = slide.background_colour;
  }

  return (
    <div className={`slide-${slide.slide_number}`}>
      <div className="background-image" style={styles}>
        {slide.theme === 'Slide-2' && <TwentiethPageSlide2Content slide={slide} />}
        {slide.theme === 'Slide-3' && <TwentiethPageSlide3Content slide={slide} />}
        {slide.theme === 'Slide-4' && <TwentiethPageSlide4Content slide={slide} />}
        {slide.theme === 'Slide-5' && <TwentiethPageSlide5Content slide={slide} />}
      </div>
    </div>
  );
};

TwentiethPageSlide.propTypes = {};

export default TwentiethPageSlide;
