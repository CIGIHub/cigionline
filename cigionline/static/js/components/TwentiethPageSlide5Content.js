import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide5Content = ({ slide }) => {
  return (
    <div className="slide-content">
      <div className="container">
        <div className="row justify-content-center text-center">
          <div className="col-md-10 col-lg-8 slide-3">
            <h1>{slide.title}</h1>
            <div className="feed-background">
              <iframe
                allowFullScreen
                id="wallsio-iframe"
                src="https://my.walls.io/v3jmb?nobackground=1&amp;show_header=0"
                style={{ border: 0, height: 100 + '%', width: 100 + '%' }}
                loading="lazy"
                title="My social wall"
              ></iframe>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

TwentiethPageSlide5Content.propTypes = {};

export default TwentiethPageSlide5Content;
