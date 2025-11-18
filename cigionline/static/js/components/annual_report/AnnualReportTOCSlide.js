import PropTypes from 'prop-types';
import React, { useState, useEffect, useMemo } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import '../../../css/components/annual_reports/AnnualReportTOCSlide.scss';

function AnnualReportTOCSlide({
  slides,
  basePath,
  currentIndex,
  lang,
  isComponent,
  fadeableClass,
  revealableClass,
  dimUI,
}) {
  const [searchParams, setSearchParams] = useSearchParams();
  const acknowledgementsParam = searchParams.get('acknowledgements');
  const personIdParam = searchParams.get('personId');
  const [showAcknowledgementsTab, setShowAcknowledgementsTab] = useState(
    acknowledgementsParam === 'true',
  );
  const slidesOnToc = useMemo(
    () => slides.filter((slide) => slide.include_on_toc),
    [slides],
  );
  const slidesCount = slidesOnToc.length;
  const slidesLeftColumn = slidesOnToc.slice(0, Math.ceil(slidesCount / 2));
  const slidesRightColumn = slidesOnToc.slice(Math.ceil(slidesCount / 2));

  useEffect(() => {
    const next = new URLSearchParams(searchParams);
    next.set('acknowledgements', showAcknowledgementsTab ? 'true' : 'false');
    if (!showAcknowledgementsTab) next.delete('personId');
    setSearchParams(next, { replace: true });
  }, [showAcknowledgementsTab]);

  const selectedMember = useMemo(() => {
    if (!personIdParam) return null;
    const boards = slides[currentIndex]?.slide_content?.boards || {};
    const allMembers = Object.values(boards).flat();
    return (
      allMembers.find((m) => String(m.id) === String(personIdParam)) || null
    );
  }, [personIdParam, slides, currentIndex]);

  return (
    <>
      <div
        className={`annual-report-slide toc-slide ${
          isComponent ? 'component-mode' : ''
        }`}
      >
        <div className="background-row background-table-of-contents">
          <div
            className={`background-image ${slides[
              currentIndex
            ].slide_type.replace('_', '-')}-background-img ${revealableClass}`}
            style={{
              backgroundImage: `url(${slides[currentIndex].background_image}),url(${slides[currentIndex].background_image_thumbnail})`,
            }}
          />
          <div>
            <div
              className={`${revealableClass} hover-reveal-gradient-${slides[currentIndex].background_gradient_position}`}
            >
              {slides[currentIndex].background_quote && (
                <div
                  className={`quote quote-${slides[currentIndex].background_quote_position}`}
                >
                  <h3
                    className={`hover-reveal-quote ${
                      dimUI ? 'is-revealed' : ''
                    }`}
                    dangerouslySetInnerHTML={{
                      __html:
                        lang === 'fr'
                          ? slides[currentIndex].background_quote_fr
                          : slides[currentIndex].background_quote,
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
        </div>
        <div className={`ar-slide-content table-of-contents ${fadeableClass}`}>
          <div className="container">
            <div className="row">
              <div className="col">
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
                        {lang === 'en'
                          ? 'Table of Contents'
                          : 'Table des matières'}
                      </button>
                    ) : (
                      <span className="acknowledgements-label">
                        {lang === 'en'
                          ? 'Table of Contents'
                          : 'Table des matières'}
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
                    <div className="row toc-list">
                      <div className="col-md-6">
                        {slidesLeftColumn.map((slide, slideIndex) => (
                          <div className="toc-item slide-link" key={slide.slug}>
                            <p className="slide-number">
                              {String(slideIndex + 1).padStart(2, '0')}
                            </p>
                            <Link
                              to={`${basePath}/${lang}/${slide.slug}/`}
                              dangerouslySetInnerHTML={{
                                __html:
                                  lang === 'en'
                                    ? slide.slide_title
                                    : slide.slide_title_fr,
                              }}
                            />
                          </div>
                        ))}
                      </div>
                      <div className="col-md-6">
                        {slidesRightColumn.map((slide, slideIndex) => (
                          <div className="toc-item slide-link" key={slide.slug}>
                            <p className="slide-number">
                              {String(
                                slideIndex + 1 + slidesLeftColumn.length,
                              ).padStart(2, '0')}
                            </p>
                            <Link
                              to={`${basePath}/${lang}/${slide.slug}/`}
                              dangerouslySetInnerHTML={{
                                __html:
                                  lang === 'en'
                                    ? slide.slide_title
                                    : slide.slide_title_fr,
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="row">
                        <div className="col">
                          {lang === 'en' ? (
                            slides[currentIndex].slide_content
                              .credits_message && (
                              <p className="credits-message">
                                {
                                  slides[currentIndex].slide_content
                                    .credits_message.en
                                }
                              </p>
                            )
                          ) : (
                            <p className="credits-message">
                              {
                                slides[currentIndex].slide_content
                                  .credits_message.fr
                              }
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
                                  {boardKey === 'executive' && (
                                    <span>Executive</span>
                                  )}
                                </h4>
                                <div className="row credits-block">
                                  {slides[currentIndex].slide_content.boards[
                                    boardKey
                                  ].map((member, memberIndex) => (
                                    <div
                                      key={`member-${memberIndex}`}
                                      className="col-6 col-md-4 col-lg-3 mb-2"
                                    >
                                      <h5 className="member-name">
                                        <button
                                          type="button"
                                          onClick={() => {
                                            const next = new URLSearchParams(
                                              searchParams,
                                            );
                                            next.set(
                                              'acknowledgements',
                                              'true',
                                            );
                                            next.set(
                                              'personId',
                                              String(member.id),
                                            );
                                            setSearchParams(next);
                                          }}
                                        >
                                          {member.name}
                                        </button>
                                      </h5>
                                      <h6 className="member-title">
                                        {lang === 'en'
                                          ? member.title
                                          : member.title_fr}
                                        <br />
                                        {lang === 'en'
                                          ? member.title_line_2
                                          : member.title_line_2_fr}
                                      </h6>
                                    </div>
                                  ))}
                                </div>
                                {index === 0 && (
                                  <div className="credits-border" />
                                )}
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
        </div>
      </div>
      {selectedMember && (
        <div className="acknowledgements-person-overlay">
          <div className="acknowledgements-person-container">
            <div className="acknowledgements-bio">
              <div className="container">
                <div className="row">
                  <div className="col">
                    <div className="person-heading">
                      {selectedMember.image && (
                        <img
                          src={selectedMember.image}
                          alt={selectedMember.name}
                        />
                      )}
                      <div className="person-info">
                        <h2 className="bio-name">{selectedMember.name}</h2>
                        <div className="person-title">
                          {lang === 'fr'
                            ? selectedMember.title_fr
                            : selectedMember.title}
                        </div>
                        {(selectedMember.title_line_2 ||
                          selectedMember.title_line_2_fr) && (
                          <div className="person-title">
                            {lang === 'fr'
                              ? selectedMember.title_line_2_fr
                              : selectedMember.title_line_2}
                          </div>
                        )}
                        <div className="cigi-red-line" />
                      </div>
                    </div>

                    {((lang === 'fr'
                      ? selectedMember.bio_fr
                      : selectedMember.bio_en) ||
                      '') && (
                      <p
                        className="person-summary"
                        dangerouslySetInnerHTML={{
                          __html:
                            lang === 'fr'
                              ? selectedMember.bio_fr
                              : selectedMember.bio_en,
                        }}
                      />
                    )}

                    {selectedMember.link && (
                      <a
                        href={selectedMember.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="full-bio-link"
                      >
                        <div className="float-left full-bio-link-icon">
                          <i className="fas fa-user" />
                        </div>
                        <span className="underline">
                          {lang === 'fr'
                            ? 'Lire la biographie'
                            : 'Read full bio'}
                        </span>
                      </a>
                    )}
                    <button
                      type="button"
                      className="clearfix back-link"
                      onClick={() => {
                        const next = new URLSearchParams(searchParams);
                        next.delete('personId');
                        setSearchParams(next);
                      }}
                    >
                      <div className="float-left back-link-icon publication">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="0.22in"
                          height="0.19in"
                          viewBox="0 0 16 14"
                        >
                          <defs>
                            <clipPath id="clip-a">
                              <rect
                                x="257"
                                y="317"
                                width="16"
                                height="14"
                                transform="translate(-256.98 -317)"
                              />
                            </clipPath>
                          </defs>
                          <g className="b" style={{ clipPath: 'url(#a)' }}>
                            <path
                              d="M262.73,317.19a.69.69,0,0,1,.55-.19.81.81,0,0,1,.5.23.7.7,0,0,1,.2.52v2.5a14.77,14.77,0,0,1,6.38,1.16,4.83,4.83,0,0,1,2.63,4.66,5.53,5.53,0,0,1-.78,2.75,6.23,6.23,0,0,1-1.81,2.06.56.56,0,0,1-.45.11.6.6,0,0,1-.37-.23.43.43,0,0,1,0-.44,6,6,0,0,0,.28-3.48,2.82,2.82,0,0,0-1.91-1.8,12.18,12.18,0,0,0-3.91-.53v2.75a.7.7,0,0,1-.2.52.8.8,0,0,1-.5.23.7.7,0,0,1-.55-.19l-5.5-4.75a.76.76,0,0,1,0-1.12Z"
                              transform="translate(-256.98 -317)"
                            />
                          </g>
                        </svg>
                      </div>
                      <p>
                        <span className="underline">
                          {lang === 'fr' ? 'Page précédente' : 'Back'}
                        </span>
                      </p>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

AnnualReportTOCSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  lang: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
  isComponent: PropTypes.bool,
  fadeableClass: PropTypes.string.isRequired,
  revealableClass: PropTypes.string.isRequired,
  dimUI: PropTypes.bool.isRequired,
};

AnnualReportTOCSlide.defaultProps = {
  isComponent: false,
};

export default AnnualReportTOCSlide;
