import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { v4 as uuidv4 } from 'uuid';

const TwentiethPageSlide2Content = ({ slide }) => {
  const [showBg, setShowBg] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const socialString = JSON.parse(
    document.getElementById('social-string').textContent
  );
  const absoluteUrl = JSON.parse(
    document.getElementById('absolute-url').textContent
  );
  function playVideo() {
    const videoBg = document.getElementById('video-bg');
    videoBg.play();
  }

  function pauseVideo() {
    const videoBg = document.getElementById('video-bg');
    videoBg.pause();
  }

  function handleBgToggle() {}

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
      <div className={`opacity-gradient ${showBg ? 'show-bg' : ''}`} />
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
                <ul
                  className={`social-share-list ${showShare ? 'open' : ''}`}
                  id="social-share-list-bottom"
                >
                  <li className="facebook">
                    <a className="facebook-share-link" data-url={absoluteUrl}>
                      <i className="fab fa-facebook-f fa-sm icon" />
                    </a>
                  </li>
                  <li className="twitter">
                    <a
                      className="twitter-share-link"
                      href={`https://twitter.com/share?text=${socialString}&amp;url=${absoluteUrl}`}
                    >
                      <i className="fab fa-twitter fa-sm icon" />
                    </a>
                  </li>
                  <li className="linkedin">
                    <a
                      className="linkedin-share-link"
                      href={`https://www.linkedin.com/shareArticle?mini=true&amp;url=${absoluteUrl}&amp;title=${socialString}`}
                    >
                      <i className="fab fa-linkedin-in fa-sm icon" />
                    </a>
                  </li>
                </ul>
                <button
                  type="button"
                  className="share"
                  onClick={() => setShowShare(!showShare)}
                >
                  <span className={!showShare ? 'icon-opened' : 'icon-closed'}>
                    <i className="far fa-arrow-right" />
                  </span>
                  <span className={showShare ? 'icon-opened' : 'icon-closed'}>
                    <i className="fas fa-share-alt" />
                  </span>
                </button>
                <button
                  type="button"
                  className="camera"
                  onMouseEnter={() => setShowBg(true)}
                  onMouseLeave={() => setShowBg(false)}
                >
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
