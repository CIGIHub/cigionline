import PropTypes from 'prop-types';
import React, { useMemo, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '../../../css/components/annual_reports/AnnualReportsFinancialsSlide.scss';
import { faDownload } from '@fortawesome/pro-light-svg-icons';

function AnnualReportsFinancialsSlide({ slide, lang }) {
  const navigate = useNavigate();
  const { subSlug } = useParams();
  const tabs = useMemo(
    () => slide?.slide_content.auditor_reports || [],
    [slide],
  );

  console.log(slide);
  console.log(tabs);

  useEffect(() => {
    if (!subSlug && tabs.length > 0) {
      const tabSlug = lang === 'fr' ? `${tabs[0].slug_fr}/fr` : tabs[0].slug_en;
      navigate(tabSlug, { replace: true });
    }
  }, [subSlug, tabs, navigate]);

  const activeSlug =
    subSlug || (lang === 'fr' && tabs[0].slug_fr) || tabs[0].slug_en;
  const activeTab =
    tabs.find((t) => {
      if (lang === 'fr') {
        return t.slug_fr === activeSlug;
      }
      return t.slug_en === activeSlug;
    }) || null;

  console.log(activeSlug);
  console.log(activeTab);

  return (
    <div className="annual-report-slide">
      <div className="background-row financials-background d-none d-md-block" />
      <div className="financials">
        <div className="container">
          <div className="row">
            <div className="col">
              <h1>{lang === 'en' ? 'Financials' : 'Financières'}</h1>
            </div>
          </div>
          <div className="row">
            <div className="col financials-container">
              <div className="row">
                <div className="col">
                  <div className="financials-menu d-flex align-items-center">
                    {tabs.map((t, idx) => {
                      const tabSlug = lang === 'fr' ? t.slug_fr : t.slug_en;
                      const isActive = tabSlug === activeSlug;
                      const tabTitle = lang === 'fr' ? t.title_fr : t.title_en;
                      return (
                        <React.Fragment key={tabSlug}>
                          {isActive ? (
                            tabTitle
                          ) : (
                            <Link
                              to={tabSlug}
                              className={`financials-tab-link ${
                                isActive ? 'is-active' : ''
                              }`}
                              aria-current={isActive}
                            >
                              <span className={isActive ? '' : 'underline'}>
                                {tabTitle}
                              </span>
                            </Link>
                          )}
                          {idx < tabs.length - 1 && (
                            <span className="menu-break mx-2">/</span>
                          )}
                        </React.Fragment>
                      );
                    })}

                    <div className="download-button ms-3">
                      <a
                        href={slide.downloadPdfLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="d-flex align-items-center"
                      >
                        <FontAwesomeIcon icon={faDownload} size="lg" />
                        <span className="underline ms-2">
                          {lang === 'en' ? 'Download PDF' : 'Télécharger PDF'}
                        </span>
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div className="financials-content row">
                {activeTab &&
                  activeTab.columns.map((col, idx) => (
                    <div key={idx} className="col col-md-6">
                      {lang === 'fr'
                        ? col.fr.map((html, hIdx) => (
                            <React.Fragment key={hIdx}>
                              {typeof html === 'string' ? (
                                <div
                                  key={hIdx}
                                  dangerouslySetInnerHTML={{ __html: html }}
                                />
                              ) : (
                                <div key={hIdx} className="auditor-signature">
                                  <img
                                    src={html.signature}
                                    alt="auditor signature"
                                    width="105"
                                    height="18"
                                  />
                                  <p
                                    dangerouslySetInnerHTML={{
                                      __html: html.signature_text,
                                    }}
                                  />
                                </div>
                              )}
                            </React.Fragment>
                          ))
                        : col.en.map((html, hIdx) => (
                            <React.Fragment key={hIdx}>
                              {typeof html === 'string' ? (
                                <div
                                  key={hIdx}
                                  dangerouslySetInnerHTML={{ __html: html }}
                                />
                              ) : (
                                <div key={hIdx} className="auditor-signature">
                                  <img
                                    src={html.signature}
                                    alt="auditor signature"
                                    width="105"
                                    height="18"
                                  />
                                  <p
                                    dangerouslySetInnerHTML={{
                                      __html: html.signature_text,
                                    }}
                                  />
                                </div>
                              )}
                            </React.Fragment>
                          ))}
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

AnnualReportsFinancialsSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
};

export default AnnualReportsFinancialsSlide;
