import PropTypes from 'prop-types';
import React from 'react';
import '../../../css/components/annual_reports/AnnualReportRegularSlide.scss';

function AnnualReportRegularSlide({ slide, lang }) {
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
              <h1 aria-live="assertive">
                {lang === 'fr' ? slide.slide_title_fr : slide.slide_title}
              </h1>
            </div>
          </div>
          <div className="row">
            {slide.slide_content.columns?.map((column, index) => (
              <div
                key={index}
                className="slide-content-block col-12 col-md-6"
                dangerouslySetInnerHTML={{
                  __html:
                    lang === 'fr' ? column.fr : column.en,
                }}
              />
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
