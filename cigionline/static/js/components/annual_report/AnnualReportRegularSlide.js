import PropTypes from 'prop-types';
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faFileLines,
  faVideo,
  faPodcast,
  faCalendar,
  faNewspaper,
  faUser,
  faEnvelope,
  faHeadphones,
  faMagnifyingGlass,
} from '@fortawesome/pro-light-svg-icons';
import '../../../css/components/annual_reports/AnnualReportRegularSlide.scss';

function AnnualReportRegularSlide({ slide, lang }) {
  const contentIcons = {
    publication: faFileLines,
    video: faVideo,
    podcast: faPodcast,
    event: faCalendar,
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
              <h1 className="slide-title" aria-live="assertive">
                {lang === 'fr' ? slide.slide_title_fr : slide.slide_title}
              </h1>
            </div>
          </div>
          <div className="row">
            {slide.slide_content.columns?.map((column, index) => (
              <div className="col-12 col-md-6" key={index}>
                {column.en && (
                  <div
                    className="paragraphs"
                    dangerouslySetInnerHTML={{
                      __html: lang === 'fr' ? column.fr : column.en,
                    }}
                  />
                )}
                {column.content && (
                  <div>
                    {column.content.map((contentBlock, idx) => (
                      <a
                        key={idx}
                        className="content-link"
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
                      </a>
                    ))}
                  </div>
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
