import PropTypes from 'prop-types';
import React from 'react';

const StrategicPlanRegularSlide = ({ slide }) => {
  const columnClasses = {
    1: 'col-10',
    2: 'col-3',
    3: 'col-3',
  };
  const columnClass = columnClasses[slide.columns];

  return (
    <div className={`regular-slide ${slide} col-9`}>
      <div>
        <div className="title-slide__title">
          {slide.slide_title && (
            <h1 aria-live="assertive">{slide.slide_title}</h1>
          )}
          {slide.slide_subtitle && <p>{slide.slide_subtitle}</p>}
        </div>
      </div>
      <div
        className="title-slide__content"
        dangerouslySetInnerHTML={{ __html: slide.slide_content }}
      />
    </div>
  );
};

StrategicPlanRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanRegularSlide;
