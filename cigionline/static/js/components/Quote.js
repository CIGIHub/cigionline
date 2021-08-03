/* eslint-disable react/no-danger */
import React from 'react';
import { lightBackgroundSlugs, backgroundLessSlideTypes } from './AnnualReportConstants';

const Quote = ({ slide, contentOpacity }) => {
  const originUrl = window.location.origin;
  let bgImageUrl = (slide.value.background_image?.original || '');
  if (backgroundLessSlideTypes.includes(slide.type) && contentOpacity) {
    bgImageUrl = '';
  }

  const bgVideoUrl = (slide.value.background_video?.original || '');
  return (
    <div
      className={
        `background-row show-for-medium${
          lightBackgroundSlugs.includes(slide.type)
            ? ' background-white'
            : ''}`
      }
    >
      <div
        className="background-image"
        style={{
          backgroundImage: bgImageUrl ? `url(${originUrl}${bgImageUrl})` : '',
        }}
      >
        <div
          className="hover-reveal hover-reveal-gradient-right"
          style={{ opacity: contentOpacity ? 0 : 1 }}
        >
          <div
            className="quote quote-right"
            style={{ opacity: contentOpacity ? 0 : 1 }}
          >
            <h3
              className="hover-reveal-quote"
              style={{ opacity: contentOpacity ? 0 : 1 }}
              dangerouslySetInnerHTML={{
                __html: slide.value.quote ? slide.value.quote.message : '',
              }}
            />
            <h4
              className="hover-reveal-quote-source"
              style={{ visibility: contentOpacity ? 'hidden' : 'visible' }}
              dangerouslySetInnerHTML={{
                __html: slide.value.quote ? slide.value.quote.subtitle : '',
              }}
            />
            <div
              className="hover-reveal-quote-line"
              style={{ width: contentOpacity ? 0 : 100 }}
            />
          </div>
        </div>
      </div>
      <div>
        {bgVideoUrl.length ? (
          <video
            playsInline
            autoPlay
            muted
            loop
            id="background-video"
            className="video-background"
            key={bgVideoUrl}
          >
            <source
              src={`${originUrl}${bgVideoUrl}`}
              type="video/mp4"
            />
          </video>
        ) : (
          ''
        )}
      </div>
      {lightBackgroundSlugs.indexOf(slide.type) > -1 ? (
        ''
      ) : (
        <>
          <div className="background-overlay hover-reveal-hide" />
          <div className="background-gradient-overlay hover-reveal-hide" />
        </>
      )}
    </div>
  );
};

export default Quote;
