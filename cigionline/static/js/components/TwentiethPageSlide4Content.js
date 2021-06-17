import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide4Content = ({ slide }) => (
  <div className="col slide-4">
    {slide.title && <h1>{slide.title}</h1>}
    {slide.body &&
      slide.body.map((block, i) => {
        if (block.type === 'text') {
          return (
            <div key={i} dangerouslySetInnerHTML={{ __html: block.value }} />
          );
        }

        if (block.type === 'embed') {
          return (
            <div key={i} className="video-responsive">
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
        return <div key={i}>{block.value}</div>;
      })}
  </div>
);
TwentiethPageSlide4Content.propTypes = {};

export default TwentiethPageSlide4Content;
