/* eslint-disable react/no-danger */
import React from 'react';

const MessageSlide = ({ slide, contentOpacity }) => {
  function firstHalfBody() {
    const half = Math.ceil(slide.value.body.length / 2);
    const firstHalf = slide.value.body.slice(0, half);
    return firstHalf
      .map(function(paragraph) {
        return paragraph.value;
      })
      .join('');
  }

  function secondHalfBody() {
    const half = Math.ceil(slide.value.body.length / 2);
    const secondHalf = slide.value.body.slice(-half);
    return secondHalf
      .map(function(paragraph) {
        return paragraph.value;
      })
      .join('');
  }

  return (
    <div className="chairs-message" style={{ opacity: contentOpacity ? 1 : 0 }}>
      <div className="grid-container">
        <div className="grid-x grid-margin-x hover-reveal-hide">
          <div className="cell">
            <h1>{slide.value.title}</h1>
          </div>
        </div>
        <div className="grid-x grid-margin-x">
          <div
            className="cell medium-6 hover-reveal-hide"
            dangerouslySetInnerHTML={{ __html: firstHalfBody() }}
          />
          <div
            className="cell medium-6 hover-reveal-hide"
            dangerouslySetInnerHTML={{ __html: secondHalfBody() }}
          />
          <div className="cell medium-6 hover-reveal-hide" />
          <div className="cell medium-6 hover-reveal-hide">
            <div className="cigi-red-line" />
            <p className="chair-name">
              <b>{slide.value.author.title}</b>
              <br />
              <em>{slide.value.author.position}</em>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageSlide;
