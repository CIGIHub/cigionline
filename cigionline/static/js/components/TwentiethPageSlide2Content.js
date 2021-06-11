import React from 'react';
import PropTypes from 'prop-types';

const TwentiethPageSlide2Content = ({ body, title }) => (
  <div className="col slide-2">
    {title && <h1>{title}</h1>}
    {body &&
      body.map((block, i) => {
        if (block.type === 'text') {
          return (
            <div key={i} dangerouslySetInnerHTML={{ __html: block.value }} />
          );
        }
        return <div key={i}>{block.value}</div>;
      })}
  </div>
);
TwentiethPageSlide2Content.propTypes = {};

export default TwentiethPageSlide2Content;
