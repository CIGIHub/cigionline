import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide = ({ slide }) => {
  console.log(slide);
  return (
    <div className={`slide-${slide.slide_number}`}>
      <div
        className="background-image"
        style={
          slide.background
            ? {
                backgroundImage: `url(${slide.background})`,
              }
            : {}
        }
      >
        {slide.theme !== 'Slide-3' && <div className="slide-content"></div>}

        {slide.theme === 'Slide-3' && <div className="slide-content"></div>}
      </div>
    </div>
  );
};

TwentiethPageSlide.propTypes = {};

export default TwentiethPageSlide;
