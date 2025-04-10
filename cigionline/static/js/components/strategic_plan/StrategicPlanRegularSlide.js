import PropTypes from 'prop-types';
import React from 'react';
import { motion } from 'framer-motion';

const columnClasses = {
  small: 'col-lg-5',
  large: 'col-lg-10',
};
const alignmentClasses = {
  left: 'justify-content-start text-start',
  right: 'justify-content-end text-end',
  full: 'justify-content-start text-start',
};
const getTitleColumnClass = (columnSize, columnCount) => {
  if (columnSize === 'small' && columnCount === 1) {
    return 'col-lg-5';
  }
  if (columnSize === 'small' && columnCount >= 2) {
    return 'col-lg-8';
  }
  return 'col-lg-10';
};

const getColumnClass = (columnSize, columnCount) => {
  if (columnSize === 'small' && columnCount === 1) {
    return 'col-lg-5';
  }
  if (columnSize === 'small' && columnCount >= 2) {
    return 'col-lg-4';
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
              <p className="subtitle">{slide.slide_subtitle}</p>
            )}
          </motion.div>
        </div>

        {slide.slide_content.framework_blocks ? (
          <div
            className={`${alignmentClass} row`}
          >
            {slide.slide_content.framework_blocks.map((content, index) => (
              <motion.div
                key={index}
                className={`${getColumnClass(
                  slide.column_size,
                  slide.slide_content.columns.length,
                )} regular-slide__content__column ${content.colour} framework-block`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.5, ease: 'easeInOut', delay: 1 + index }}
              >
                {content.content.map((content, index) => (
                  <div dangerouslySetInnerHTML={{ __html: content }} />
                ))}
              </motion.div>
            ))}
          </div>
        ) : (
          <motion.div
            className={`${alignmentClass} row`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.5, ease: 'easeInOut', delay: 1 }}
          >
            {slide.slide_content.columns?.map((content, index) => (
              <div
                key={index}
                className={`${getColumnClass(
                  slide.column_size,
                  slide.slide_content.columns.length,
                )} regular-slide__content__column`}
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
        )}
        {slide.slide_title === 'Thank You.' && (
          <motion.div
            className={`${alignmentClass} row`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.5, ease: 'easeInOut', delay: 1.5 }}
          >
            <div className="col">
              <ul className="social-links">
                <li>
                  <a
                    href="https://x.com/cigionline"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Link to CIGI's X profile"
                  >
                    <i className="fa-brands fa-x-twitter"></i>
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.linkedin.com/company/cigionline/"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Link to CIGI's LinkedIn profile"
                  >
                    <i className="fa-brands fa-linkedin-in"></i>
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.youtube.com/user/cigivideos"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Link to CIGI's Youtube channel"
                  >
                    <i className="fa-brands fa-youtube"></i>
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.instagram.com/cigionline/"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Link to CIGI's Instagram Profile"
                  >
                    <i className="fa-brands fa-instagram"></i>
                  </a>
                </li>
                <li>
                  <a
                    href="https://cigionlineorg.substack.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Link to CIGI's Substack page"
                  >
                    <svg
                      width="800px"
                      height="800px"
                      viewBox="0 0 48 48"
                      id="a"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <defs>
                        <style>
                          .b&#123;stroke-linecap:round;stroke-linejoin:round;&#125;
                        </style>
                      </defs>
                      <path
                        className="b"
                        d="m40.0248,10.0817v-4.5814c-.3229,0-.7411-.0004-1.6553-.0004l-28.9669.0004c-.9142,0-1.318,0-1.6553,0v4.5814c.2164,0,.7411.0005,1.6553.0005l28.9669-.0005c.9142,0,1.4122,0,1.6553,0Z"
                      />
                      <path
                        className="b"
                        d="m40.0248,18.3503v-4.5814H9.4025c-.9142,0-1.3777,0-1.6553,0v4.5814c.2646,0,.7411,0,1.6553,0h30.6223Z"
                      />
                      <path
                        className="b"
                        d="m40.2557,42.4999v-20.1821c0-.1633-.9724-.1077-1.8866-.1077H9.4022c-.9142,0-1.6553-.0555-1.6553.1077v19.8878c.2814-.1622,15.3415-8.2118,16.1691-8.5978.5156.2972,13.6461,7.3385,16.3406,8.8914l-.0008.0007Z"
                      />
                    </svg>
                  </a>
                </li>
                <li>
                  <a
                    href="https://medium.com/centre-for-international-governance-innovation"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Link to CIGI's Medium page"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      version="1.1"
                      viewBox="0 0 1633.77 1150.51"
                    >
                      <defs>
                        <style>
                          .cls-1 &#123; fill: none; &#125; .cls-3 &#123;
                          display: none; &#125;
                        </style>
                      </defs>
                      <g>
                        <g id="Background" className="cls-3">
                          <rect width="1633.77" height="1150.07" />
                        </g>
                        <g id="Symbol">
                          <g>
                            <g>
                              <path
                                className="cls-2"
                                d="M883.45,576.26c0,163.67-131.78,296.35-294.33,296.35s-294.33-132.68-294.33-296.35,131.78-296.35,294.33-296.35,294.33,132.68,294.33,296.35"
                              />
                              <path
                                className="cls-2"
                                d="M1206.34,576.26c0,154.07-65.89,278.96-147.17,278.96s-147.17-124.9-147.17-278.96,65.89-278.96,147.17-278.96,147.17,124.9,147.17,278.96"
                              />
                              <path
                                className="cls-2"
                                d="M1338.41,576.26c0,138.04-23.17,249.94-51.76,249.94s-51.76-111.9-51.76-249.94,23.17-249.94,51.76-249.94,51.76,111.9,51.76,249.94"
                              />
                            </g>
                            <path
                              className="cls-1"
                              d="M1633.77,0h-296.29v.25H296.29v-.25H0v1150.07h119.51v.44h1410.41v-.44h103.85V0ZM1337.48,296.54v557.67H296.29V296.54h1041.19Z"
                            />
                          </g>
                        </g>
                      </g>
                    </svg>
                  </a>
                </li>
              </ul>
            </div>
          </motion.div>
        )}
      </div>
      <motion.div
        className={`${alignmentClass} row`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.5, ease: 'easeInOut', delay: 1 }}
      >
        {slide.slide_content.acknowledgements?.map((content, index) => (
          <div
            key={index}
            className={`${getColumnClass(
              slide.column_size,
              slide.slide_content.columns.length,
            )} regular-slide__content__acknowledgement`}
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
