import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide = (props) => {
  const { slide } = props;
  return (
    <div className={`slide-${slide.slide}`}>
      <div
        className="background-image"
        style={
          slide.background && {
            backgroundImage: `url(${slide.background})`,
          }
        }
      >
        <div className="container">
          <div className="row justify-content-center">
            <div className="col">
              {slide.title && <h1>{slide.title}</h1>}
              {slide.body && <p>{slide.body}</p>}
              {slide.embed && <p>{slide.embed}</p>}
              {/* {currentSlide.timeline && <h1>{currentSlide.timeline}</h1>} */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

TwentiethPageSlide.propTypes = {};

export default TwentiethPageSlide;
