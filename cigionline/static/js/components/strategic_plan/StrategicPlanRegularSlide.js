import PropTypes from 'prop-types';
import React from 'react';

const columnClasses = {
  small: 'col-4',
  large: 'col-10',
};
const alignmentClasses = {
  left: 'justify-content-start text-start',
  right: 'justify-content-end text-end',
  full: 'justify-content-start text-start',
};
const getTitleColumnClass = (columnSize, columnCount) => {
  console.log(columnSize, columnCount);
  if (columnSize === 'small' && columnCount === 1) {
    return 'col-4';
  }
  if (columnSize === 'small' && columnCount >= 2) {
    return 'col-8';
  }
  return 'col-10';
};
const StrategicPlanRegularSlide = ({ slide }) => {
  const columnClass = columnClasses[slide.column_size];
  const alignmentClass = alignmentClasses[slide.alignment];

  return (
    <div className={`strategic-plan-slide regular-slide ${slide.alignment}`}>
      <div>
        <div className={`${alignmentClass} row`}>
          <div
            className={`regular-slide__title ${getTitleColumnClass(
              slide.column_size,
              slide.slide_content.columns.length,
            )}`}
          >
            {slide.slide_title && (
              <h1 aria-live="assertive">{slide.slide_title}</h1>
            )}
            {slide.slide_subtitle && <p>{slide.slide_subtitle}</p>}
          </div>
        </div>
        <div className={`${alignmentClass} row`}>
          {slide.slide_content.columns?.map((content, index) => (
            <div
              key={index}
              className={`${columnClass} regular-slide__content__column`}
              dangerouslySetInnerHTML={{ __html: content }}
            />
          ))}
        </div>
      </div>
      <div className={`${alignmentClass} row`}>
        {slide.slide_content.acknowledgements?.map((content, index) => (
          <div
            key={index}
            className={`${columnClass} regular-slide__content__acknowledgement`}
            dangerouslySetInnerHTML={{ __html: content }}
          />
        ))}
      </div>
    </div>
  );
};

StrategicPlanRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanRegularSlide;
