import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide3Content = ({ timeline, title }) => (
  <div className="col slide-3">
    {title && <h1>{title}</h1>}
    {timeline &&
      timeline.map((year) => (
        <div className="timeline-slide" key={year.year}>
          <h2 className="timeline-year">{year.year}</h2>
          <p
            className="timeline-body"
            dangerouslySetInnerHTML={{ __html: year.body }}
          />
        </div>
      ))}
  </div>
);
TwentiethPageSlide3Content.propTypes = {};

export default TwentiethPageSlide3Content;
