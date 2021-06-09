import PropTypes from 'prop-types';
import React, { useState } from 'react';

const TwentiethPage = (props) => {
  const { slides } = props;
  const [currentSlide, setCurrentSlide] = useState(slides[0]);

  return (
    <>
      <div>
        Current Slide:
        {currentSlide.slide}
      </div>
      <div className="slides">
        <div className="controls d-flex">
          {slides.map((slide) => (
            <div className="" key={slide.slide}>
              <button type="button" onClick={() => setCurrentSlide(slide)}>
                {slide.slide}
              </button>
            </div>
          ))}
        </div>
        <div className={`slide-${currentSlide.slide}`}>
          <div
            className="background-image"
            style={
              currentSlide.background && {
                backgroundImage: `url(${currentSlide.background})`,
              }
            }
          >
            {currentSlide.title && <h1>{currentSlide.title}</h1>}
            {currentSlide.body && <p>{currentSlide.body}</p>}
            {currentSlide.embed && <p>{currentSlide.embed}</p>}
            {/* {currentSlide.timeline && <h1>{currentSlide.timeline}</h1>} */}
          </div>
        </div>
      </div>
    </>
  );
};

export default TwentiethPage;
