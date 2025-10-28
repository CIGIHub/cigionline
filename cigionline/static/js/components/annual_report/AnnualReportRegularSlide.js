import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faFileLines,
  faFilm,
  faPodcast,
  faCalendarDays,
  faNewspaper,
  faUser,
  faEnvelope,
  faHeadphones,
  faMagnifyingGlass,
  faMessageLines,
} from '@fortawesome/pro-light-svg-icons';
import { motion, AnimatePresence } from 'framer-motion';
import '../../../css/components/annual_reports/AnnualReportRegularSlide.scss';

function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) setMatches(media.matches);
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);
  return matches;
}

const variants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeInOut' },
  },
};

function AnnualReportRegularSlide({
  slide,
  lang,
  fadeableClass,
  revealableClass,
  dimUI,
}) {
  const contentIcons = {
    publication: faFileLines,
    opinion: faMessageLines,
    video: faFilm,
    podcast: faPodcast,
    event: faCalendarDays,
    essay_series: faNewspaper,
    media: faNewspaper,
    news_release: faNewspaper,
    experts: faUser,
    subscribe: faEnvelope,
    listen: faHeadphones,
    explore: faMagnifyingGlass,
  };

  const isLarge = useMediaQuery('(min-width: 992px)');

  return (
    <AnimatePresence mode="sync">
      <motion.div
        className="annual-report-slide"
        key={slide.id}
        variants={isLarge ? variants : {}}
        initial={isLarge ? 'initial' : false}
        animate={isLarge ? 'animate' : false}
      >
        <div
          className={`background-row ${slide.slide_type.replace(
            '_',
            '-',
          )}-background d-none d-lg-block`}
        >
          <div
            className={`background-image ${slide.slide_type.replace(
              '_',
              '-',
            )}-background-img ${
              slide.slide_type === 'chairs_message' ||
              slide.slide_type === 'presidents_message'
                ? revealableClass
                : ''
            }`}
            style={{
              backgroundImage: `url(${slide.background_image}),url(${slide.background_image_thumbnail})`,
            }}
          />
          <div>
            <div
              className={`${revealableClass} hover-reveal-gradient-${slide.background_gradient_position}`}
            >
              {slide.background_quote && (
                <div
                  className={`quote quote-${slide.background_quote_position}`}
                >
                  <h3
                    className={`hover-reveal-quote ${
                      dimUI ? 'is-revealed' : ''
                    }`}
                    dangerouslySetInnerHTML={{
                      __html:
                        lang === 'fr'
                          ? slide.background_quote_fr
                          : slide.background_quote,
                    }}
                  />
                  <div
                    className={`hover-reveal-quote-line ${
                      dimUI ? 'is-revealed' : ''
                    }`}
                  />
                </div>
              )}
            </div>
          </div>
          {slide.background_video && (
            <video
              className="background-video"
              autoPlay
              loop
              muted
              playsInline
              src={slide.background_video}
            />
          )}
          {slide.slide_type === 'standard' && (
            <>
              <div className={`background-overlay ${fadeableClass}`} />
              <div className={`background-gradient-overlay ${fadeableClass}`} />
            </>
          )}
        </div>
        <div
          className={`ar-slide-content regular-slide ${fadeableClass} ${slide.slide_type.replace(
            '_',
            '-',
          )}`}
          key={`${slide.slug}-${lang}`}
        >
          <div className="container">
            <div className="row">
              <div className="col">
                <div className="slide-title" key={lang}>
                  <h1 aria-live="assertive">
                    {lang === 'fr' ? slide.slide_title_fr : slide.slide_title}
                  </h1>
                </div>
              </div>
            </div>
            <div className="row">
              {slide.slide_content.columns?.map((column, index) => (
                <div className="col-12 col-lg-6" key={index}>
                  {column.en && (
                    <div
                      className="paragraphs"
                      key={lang}
                      dangerouslySetInnerHTML={{
                        __html: lang === 'fr' ? column.fr : column.en,
                      }}
                    />
                  )}
                  {column.content && (
                    <div className="content-links" key={`content-${lang}`}>
                      <div>
                        {column.content.map((contentBlock, idx) => (
                          <a
                            key={`content-${idx}-${lang}`}
                            className="content-link d-none d-lg-block"
                            href={contentBlock.link}
                            aria-label={
                              contentBlock.label || 'Related content link'
                            }
                          >
                            <div className="float-left content-link-icon">
                              <FontAwesomeIcon
                                icon={contentIcons[contentBlock.type]}
                              />
                            </div>
                            <div className="content-copy">
                              <h4>{contentBlock.type}</h4>
                              <p>
                                <span className="underline">
                                  {lang === 'fr'
                                    ? contentBlock.title_fr
                                    : contentBlock.title_en}
                                </span>
                              </p>
                            </div>
                          </a>
                        ))}
                      </div>
                      <div className="content-links-mobile d-lg-none">
                        {column.content.map((contentBlock, idx) => (
                          <a
                            key={`mobile-${idx}`}
                            className="clearfix content-link-mobile"
                            href={contentBlock.link}
                            aria-label={
                              contentBlock.label || 'Related content link'
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {lang === 'fr'
                              ? contentBlock.title_fr
                              : contentBlock.title_en}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

AnnualReportRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
  fadeableClass: PropTypes.string.isRequired,
  revealableClass: PropTypes.string.isRequired,
  dimUI: PropTypes.bool.isRequired,
};

export default AnnualReportRegularSlide;
