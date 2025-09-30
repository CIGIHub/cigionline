import PropTypes from 'prop-types';
import React from 'react';
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
import '../../../css/components/annual_reports/AnnualReportRegularSlide.scss';

function AnnualReportRegularSlide({ slide, lang }) {
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

  return (
    <div className="annual-report-slide">
      <div
        className={`ar-slide-content regular-slide ${slide.slide_type.replace(
          '_',
          '-',
        )}`}
      >
        <div className="container">
          <div className="row">
            <div className="col">
              <div className="slide-title">
                <h1
                  aria-live="assertive"
                  key={lang}
                >
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
                    dangerouslySetInnerHTML={{
                      __html: lang === 'fr' ? column.fr : column.en,
                    }}
                  />
                )}
                {column.content && (
                  <>
                    <div className="content-links">
                      {column.content.map((contentBlock, idx) => (
                        <a
                          key={idx}
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
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

AnnualReportRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
};

export default AnnualReportRegularSlide;
