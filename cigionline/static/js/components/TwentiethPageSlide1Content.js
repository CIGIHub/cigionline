/* eslint-disable jsx-a11y/anchor-is-valid */
/* eslint-disable react/prop-types */
import React, { useState } from 'react';

const TwentiethPageSlide2Content = ({ slide }) => {
  const [showShare, setShowShare] = useState(false);
  const [playing, setPlaying] = useState(true);
  const socialString = JSON.parse(
    document.getElementById('social-string').textContent,
  );
  const absoluteUrl = JSON.parse(
    document.getElementById('absolute-url').textContent,
  );
  function playVideo() {
    const videoBg = document.getElementById('video-bg');
    videoBg.play();
    setPlaying(true);
  }

  function pauseVideo() {
    const videoBg = document.getElementById('video-bg');
    videoBg.pause();
    setPlaying(false);
  }

  return (
    <>
      <video
        className="video-bg"
        autoPlay
        muted
        playsInline
        loop
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
              <div className="bg-controls-buttons-right">
                <ul
                  className={`social-share-list ${showShare ? 'open' : ''}`}
                  id="social-share-list-bottom"
                >
                  <li className="twitter">
                    <a
                      className="twitter-share-link"
                      href={`https://twitter.com/share?text=${socialString}&amp;url=${absoluteUrl}`}
                    >
                      <i className="fa-brands fa-x-twitter fa-sm icon" />
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
                <button type="button" className={`pause ${!playing ? 'hide' : ''}`} onClick={pauseVideo}>
                  <i className="fas fa-pause" />
                </button>
                <button type="button" className={`play ${playing ? 'hide' : ''}`} onClick={playVideo}>
                  <i className="fas fa-play" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default TwentiethPageSlide2Content;
