import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide2Content = ({ body, title, embed }) => (
  <div className="col slide-2">
    {title && <h1>{title}</h1>}
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
    {body && <p dangerouslySetInnerHTML={{ __html: body }} />}
  </div>
);
TwentiethPageSlide2Content.propTypes = {};

export default TwentiethPageSlide2Content;
