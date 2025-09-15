import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../../../css/components/annual_reports/AnnualReportTOCSlide.scss';

function AnnualReportTOCSlide({ slides, basePath, currentIndex, lang }) {
  const [showAcknowledgementsTab, setShowAcknowledgementsTab] = useState(false);

  return (
    <div className="row">
      <div className="col">
        <div className="table-of-contents">
          <h1 aria-live="assertive">
            {lang === 'en'
              ? `${slides[0].year} Annual Report`
              : `Rapport Annuel ${slides[0].year}`}
          </h1>
          <div className="toc-content">
            <div className="toc-menu">
              {showAcknowledgementsTab ? (
                <button
                  type="button"
                  className="hide-acknowledgements-btn"
                  aria-pressed={!showAcknowledgementsTab}
                  onClick={() => setShowAcknowledgementsTab(false)}
                >
                  {lang === 'en' ? 'Table of Contents' : 'Table des matières'}
                </button>
              ) : (
                <span className="acknowledgements-label">
                  {lang === 'en' ? 'Table of Contents' : 'Table des matières'}
                </span>
              )}
              <span>/</span>
              {showAcknowledgementsTab ? (
                <span className="acknowledgements-label">
                  {lang === 'en' ? 'Acknowledgements' : 'Remerciements'}
                </span>
              ) : (
                <button
                  type="button"
                  className="show-acknowledgements-btn"
                  aria-pressed={showAcknowledgementsTab}
                  onClick={() => setShowAcknowledgementsTab(true)}
                >
                  {lang === 'en' ? 'Acknowledgements' : 'Remerciements'}
                </button>
              )}
            </div>
            {!showAcknowledgementsTab ? (
              <ul>
                {slides.map(
                  (slide) =>
                    slide.include_on_toc && (
                      <li key={slide.slug}>
                        <Link to={`${basePath}/${slide.slug}`}>
                          {slide.slide_title}
                        </Link>
                      </li>
                    ),
                )}
              </ul>
            ) : (
              <>
                <div className="row">
                  <div className="col">
                    {lang === 'en' ? (
                      slides[currentIndex].slide_content.credits_message && (
                        <p className="credits-message">
                          {
                            slides[currentIndex].slide_content.credits_message
                              .en
                          }
                        </p>
                      )
                    ) : (
                      <p className="credits-message">
                        {slides[currentIndex].slide_content.credits_message.fr}
                      </p>
                    )}
                    <div className="credits-border" />
                  </div>
                </div>
                <div className="row">
                  <div className="col">
                    <div className="credits-block">
                      {Object.keys(
                        slides[currentIndex].slide_content.boards,
                      ).map((boardKey, index) => (
                        <div key={boardKey} className="board">
                          <h4 className="credits-title">
                            {boardKey === 'board' && (
                              <span>
                                {lang === 'en'
                                  ? 'Board'
                                  : 'Conseil d’administration'}
                              </span>
                            )}
                            {boardKey === 'executive' && <span>Executive</span>}
                          </h4>
                          <div className="row credits-block">
                            {slides[currentIndex].slide_content.boards[
                              boardKey
                            ].map((member, memberIndex) => (
                              <div
                                key={`member-${memberIndex}`}
                                className="col-6 col-md-4 col-lg-3 mb-2"
                              >
                                <h5 className="member-name">{member.name}</h5>
                                <h6 className="member-title">
                                  {lang === 'en'
                                    ? member.title
                                    : member.title_fr}
                                </h6>
                              </div>
                            ))}
                          </div>
                          {index === 0 && <div className="credits-border" />}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

AnnualReportTOCSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  lang: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
};

export default AnnualReportTOCSlide;
