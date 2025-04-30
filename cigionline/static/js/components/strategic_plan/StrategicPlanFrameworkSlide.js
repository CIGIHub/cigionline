import PropTypes from 'prop-types';
import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';

const StrategicPlanFrameworkSlide = ({ slide }) => (
  <div className={`strategic-plan-slide framework-slide ${slide.alignment}`}>
    <div>
      <div className={`row`}>
        <motion.div
          className={`col regular-slide__title`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
        >
          {slide.slide_title && (
            <h1 aria-live="assertive">{slide.slide_title}</h1>
          )}
          {slide.slide_subtitle && <p>{slide.slide_subtitle}</p>}
        </motion.div>
      </div>

      <div className="columns-row">
        {slide.slide_content.framework_blocks
          ?.slice(0, 3)
          .map((content, index) => (
            <React.Fragment key={`framework-block-${index}`}>
              <motion.div
                key={`column-title-${index}`}
                className={`column-title column-item ${content.colour} column-${
                  index + 1
                } row-1`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{
                  duration: 0.5,
                  ease: 'easeInOut',
                  delay: 1 + index,
                }}
              >
                <h2>{content.title}</h2>
                <p>
                  <em>{content.subtitle}</em>
                </p>
                <hr />
              </motion.div>
              {content.content.map((item, itemIndex) => (
                <motion.div
                  key={`framework-item-${index}-${itemIndex}`}
                  className={`framework-slide__content__item column-item ${
                    content.colour
                  } column-${index + 1} row-${itemIndex + 2}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{
                    duration: 0.5,
                    ease: 'easeInOut',
                    delay: 1 + index,
                  }}
                >
                  <div dangerouslySetInnerHTML={{ __html: item }} />
                  {index === 0 && itemIndex !== content.content.length - 1 && (
                    <div className="arrows">
                      <i className="fa-light fa-arrow-up" />
                      <i className="fa-light fa-arrow-down" />
                    </div>
                  )}
                </motion.div>
              ))}
            </React.Fragment>
          ))}
      </div>
      {slide.slide_content.framework_blocks?.slice(3).map((content, index) => (
        <div className="row" key={`column-bottom-${index}`}>
          <motion.div
            className={`framework-slide__content__column col ${content.colour}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 4 + index,
            }}
          >
            <div className="column-title">
              <h2>{content.title}</h2>
              <p>
                <em>{content.subtitle}</em>
              </p>
            </div>
          </motion.div>
        </div>
      ))}
      <motion.div
        className="row row-hr"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{
          duration: 0.5,
          ease: 'easeInOut',
          delay: 5,
        }}
      >
        <hr />
      </motion.div>
    </div>
  </div>
);

StrategicPlanFrameworkSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanFrameworkSlide;
