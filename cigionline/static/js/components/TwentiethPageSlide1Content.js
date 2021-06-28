import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { v4 as uuidv4 } from 'uuid';

const TwentiethPageSlide2Content = ({ slide }) => {
  function playVideo() {
    const videoBg = document.getElementById('video-bg');
    videoBg.play();
  }

  function pauseVideo() {
    const videoBg = document.getElementById('video-bg');
    videoBg.pause();
  }

  return (
    <>
      <video
        className="video-bg"
        autoPlay
        muted
        playsInline
        id="video-bg"
        poster={slide.background}
      >
        <source
          src="/static/assets/20th Drone Loop_logo_s.mp4"
          type="video/mp4"
        />
      </video>
      <div className="opacity-gradient" />
      <div className="slide-1-buttons">
        <div className="container">
          <div className="row justify-content-center text-center">
            <div className="col slide-1 d-flex justify-content-between">
              <div className="bg-controls-buttons-left">
                <button type="button" className="pause" onClick={pauseVideo}>
                  <i className="fas fa-pause" />
                </button>
                <button type="button" className="play" onClick={playVideo}>
                  <i className="fas fa-play" />
                </button>
              </div>
              <div className="bg-controls-buttons-right">
                <button type="button" className="pause">
                  <i className="fas fa-share-alt" />
                </button>
                <button type="button" className="play">
                  <i className="fas fa-camera" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
TwentiethPageSlide2Content.propTypes = {};

export default TwentiethPageSlide2Content;
