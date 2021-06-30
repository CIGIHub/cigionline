import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { v4 as uuidv4 } from 'uuid';

const TwentiethPageSlide2Content = ({ slide }) => {
  const [hideVideo, setHideVideo] = useState(true);

  return (
    <div className="slide-content">
      <div className="container">
        <div className="row justify-content-center text-center">
          <div className="col-md-10 col-lg-8 slide-2">
            {slide.title && (
              <h1 dangerouslySetInnerHTML={{ __html: slide.title }} />
            )}
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

                if (block.type === 'video') {
                  return (
                    <div
                      key={uuidv4()}
                      className="video-responsive"
                      onClick={() => setHideVideo(false)}
                    >
                      <div className="img-wrapper">
                        <img src={block.value.video_image} alt="" />
                      </div>
                      <button type="button">
                        <i className="fas fa-play" />
                      </button>
                      <iframe
                        width="853"
                        height="480"
                        className={hideVideo ? 'hidden' : ''}
                        src={`https://www.youtube-nocookie.com/embed/${
                          block.value.video_url
                        }${hideVideo ? '' : '?autoplay=1'}`}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        title="Embedded youtube"
                      />
                    </div>
                  );
                }

                if (block.type === 'separator') {
                  return <hr key={uuidv4()} />;
                }
                return <div key={uuidv4()}>{block.value}</div>;
              })}
          </div>
        </div>
      </div>
    </div>
  );
};
TwentiethPageSlide2Content.propTypes = {};

export default TwentiethPageSlide2Content;
