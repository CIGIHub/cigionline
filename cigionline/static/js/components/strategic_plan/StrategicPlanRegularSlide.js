import PropTypes from 'prop-types';
import React from 'react';
import { motion } from 'framer-motion';

const columnClasses = {
  small: 'col-lg-4',
  large: 'col-lg-10',
};
const alignmentClasses = {
  left: 'justify-content-start text-start',
  right: 'justify-content-end text-end',
  full: 'justify-content-start text-start',
};
const getTitleColumnClass = (columnSize, columnCount) => {
  console.log(columnSize, columnCount);
  if (columnSize === 'small' && columnCount === 1) {
    return 'col-lg-4';
  }
  if (columnSize === 'small' && columnCount >= 2) {
    return 'col-lg-8';
  }
  return 'col-lg-10';
};
const StrategicPlanRegularSlide = ({ slide }) => {
  const columnClass = columnClasses[slide.column_size];
  const alignmentClass = alignmentClasses[slide.alignment];

  return (
    <div className={`strategic-plan-slide regular-slide ${slide.alignment}`}>
      <div>
        <div className={`${alignmentClass} row`}>
          <motion.div
            className={`regular-slide__title ${getTitleColumnClass(
              slide.column_size,
              slide.slide_content.columns.length,
            )}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          >
            {slide.slide_title && (
              <h1 aria-live="assertive">{slide.slide_title}</h1>
            )}
            {slide.slide_subtitle && (
              <p class="subtitle">{slide.slide_subtitle}</p>
            )}
          </motion.div>
        </div>

        <motion.div
          className={`${alignmentClass} row`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.5, ease: 'easeInOut', delay: 0.75 }}
        >
          {slide.slide_content.columns?.map((content, index) => (
            <div
              key={index}
              className={`${columnClass} regular-slide__content__column`}
            >
              <div dangerouslySetInnerHTML={{ __html: content }} />
              {slide.slide_content.board && (
                <>
                  <h2>Board</h2>
                  <div className="regular-slide__content__board">
                    {slide.slide_content.board[0].map((member, index) => (
                      <div
                        key={`board-member-${index}`}
                        className="regular-slide__content__board__member"
                      >
                        <div className="member-name">{member.name}</div>
                        <div className="member-title">{member.title}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </motion.div>
      </div>
      <motion.div
        className={`${alignmentClass} row`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.5, ease: 'easeInOut', delay: 0.75 }}
      >
        {slide.slide_content.acknowledgements?.map((content, index) => (
          <div
            key={index}
            className={`${columnClass} regular-slide__content__acknowledgement`}
            dangerouslySetInnerHTML={{ __html: content }}
          />
        ))}
      </motion.div>
    </div>
  );
};

StrategicPlanRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanRegularSlide;
