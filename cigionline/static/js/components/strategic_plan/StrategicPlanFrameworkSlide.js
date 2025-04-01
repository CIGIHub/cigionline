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

      <div className="row">
        {slide.slide_content.framework_blocks
          ?.slice(0, 3)
          .map((content, index) => (
            <motion.div
              key={`column-${index}`}
              className={`framework-slide__content__column col-lg-4 ${content.colour}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{
                duration: 0.5,
                ease: 'easeInOut',
                delay: 1.25 + index,
              }}
            >
              <div className="column-title">
                <h2>{content.title}</h2>
                <p>
                  <em>{content.subtitle}</em>
                </p>
              </div>
              <hr />
              <div dangerouslySetInnerHTML={{ __html: content.content }} />
            </motion.div>
          ))}
      </div>
      {slide.slide_content.framework_blocks?.slice(3).map((content, index) => (
        <div className="row">
          <motion.div
            key={`column-bottom-${index}`}
            className={`framework-slide__content__column col ${content.colour}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{
              duration: 0.5,
              ease: 'easeInOut',
              delay: 4.25 + index,
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
          delay: 5.25,
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
