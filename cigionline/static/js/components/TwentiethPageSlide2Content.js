import React from 'react';
import PropTypes from 'prop-types';
import { v4 as uuidv4 } from 'uuid';

const TwentiethPageSlide2Content = ({ slide }) => (
  <div className="slide-content">
    <div className="container">
      <div className="row justify-content-center text-center">
        <div className="col-md-10 col-lg-8 slide-2">
          {slide.title && <h1 className="mb-1">{slide.title}</h1>}
        </div>
      </div>
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6 slide-2">
          {slide.body &&
            slide.body.map((block) => {
              if (block.type === 'text') {
                return (
                  <div
                    key={uuidv4()}
                    dangerouslySetInnerHTML={{ __html: block.value }}
                  />
                );
              }

              if (block.type === 'embed') {
                return (
                  <div key={uuidv4()} className="video-responsive">
                    <iframe
                      width="853"
                      height="480"
                      src={`https://www.youtube.com/embed/${block.value}`}
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      title="Embedded youtube"
                    />
                  </div>
                );
              }
              return <div key={uuidv4()}>{block.value}</div>;
            })}
        </div>
      </div>
    </div>
  </div>
);
TwentiethPageSlide2Content.propTypes = {};

export default TwentiethPageSlide2Content;
