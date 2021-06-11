import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide4Content = ({ body, title, embed }) => (
  <div className="col slide-4">
    {title && <h1>{title}</h1>}
    {body && <p dangerouslySetInnerHTML={{ __html: body }} />}
    {embed && (
      <div>
        <iframe
          width="853"
          height="480"
          src={`https://www.youtube.com/embed/${embed}`}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="Embedded youtube"
        />
      </div>
    )}
  </div>
);
TwentiethPageSlide4Content.propTypes = {};

export default TwentiethPageSlide4Content;
