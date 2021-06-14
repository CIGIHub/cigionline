import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide2Content = ({ body, title }) => (
  <div className="container">
    <div className="row justify-content-center">
      <div className="col-md-10 col-lg-8 slide-2">
        {title && <h1>{title}</h1>}
        {body &&
          body.map((block, i) => {
            if (block.type === 'text') {
              return (
                <div
                  key={i}
                  dangerouslySetInnerHTML={{ __html: block.value }}
                />
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
    </div>
  </div>
);
TwentiethPageSlide2Content.propTypes = {};

export default TwentiethPageSlide2Content;
