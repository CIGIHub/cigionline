import React from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide2Content from './TwentiethPageSlide2Content';
import TwentiethPageSlide3Content from './TwentiethPageSlide3Content';
import TwentiethPageSlide4Content from './TwentiethPageSlide4Content';

const TwentiethPageSlide = (props) => {
  const { slide } = props;
  return (
    <div className={`slide-${slide.slide}`}>
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
        <div className="container">
          <div className="row justify-content-center">
            <div className="slide-content">
              {slide.slide !== 3 && (
                <TwentiethPageSlide2Content
                  title={slide.title}
                  body={slide.body}
                />
              )}

              {slide.slide === 3 && (
                <TwentiethPageSlide3Content
                  title={slide.title}
                  timeline={slide.timeline}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

TwentiethPageSlide.propTypes = {};

export default TwentiethPageSlide;
