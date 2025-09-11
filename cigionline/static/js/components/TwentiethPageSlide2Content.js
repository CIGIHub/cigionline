/* eslint-disable react/no-danger */
/* eslint-disable react/prop-types */
import React from 'react';
import { v4 as uuidv4 } from 'uuid';

function TwentiethPageSlide2Content({ slide }) {
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
            {slide.body
              && slide.body.map((block) => {
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
                    <div key={uuidv4()} className="video-responsive">
                      <iframe
                        width="853"
                        height="480"
                        src={`https://www.youtube-nocookie.com/embed/${block.value.video_url}`}
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
}

export default TwentiethPageSlide2Content;
