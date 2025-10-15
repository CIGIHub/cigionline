import PropTypes from 'prop-types';
import React, { useMemo, useEffect } from 'react';
import { Link, useParams, useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '../../../css/components/annual_reports/AnnualReportsFinancialsSlide.scss';
import { faDownload } from '@fortawesome/pro-light-svg-icons';

function AnnualReportOutputsSlide({ slide, lang, fadeableClass }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const currentLang = lang === 'fr' ? 'fr' : 'en';

  return (
    <>
      <div className="background-row background-outputs-activities" />
      <div className="outputs-activities">
        <div className="grid-container">
          <div className="grid-x grid-margin-x">
            <div className="cell">
              {lang === 'fr' ? (
                <h1>{slide.title_fr}</h1>
              ) : (
                <h1>{slide.title_en}</h1>
              )}
            </div>
          </div>
          <div className="grid-x grid-margin-x outputs-activities-content">
            <div className="cell">
              <div className="outputs-activities-header clearfix">
                <div className="publications-menu">
                  theme 1 / theme 2 / theme 3
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default AnnualReportOutputsSlide;
AnnualReportOutputsSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
  fadeableClass: PropTypes.string.isRequired,
};
