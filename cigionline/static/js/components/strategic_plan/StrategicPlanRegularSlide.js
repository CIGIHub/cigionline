import PropTypes from 'prop-types';
import React from 'react';

const StrategicPlanRegularSlide = ({ slide }) => {
  const columnClasses = {
    1: 'col-10',
    2: 'col-4',
    3: 'col-4',
  };
  const columnClass = columnClasses[slide.columns];

  return (
    <div className={`regular-slide ${columnClass}`}>
      <div>
        <div className="regular-slide__title">
          {slide.slide_title && (
            <h1 aria-live="assertive">{slide.slide_title}</h1>
          )}
          {slide.slide_subtitle && <p>{slide.slide_subtitle}</p>}
        </div>
        <div className="regular-slide__content__columns">
          {slide.slide_content.columns?.map((content, index) => (
            <div
              key={index}
              className="regular-slide__content__column"
              dangerouslySetInnerHTML={{ __html: content }}
            />
          ))}
        </div>
      </div>
      {slide.slide_content.acknowledgements?.map((content, index) => (
        <div
          key={index}
          className="regular-slide__content__acknowledgement"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      ))}
    </div>
  );
};

StrategicPlanRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanRegularSlide;
