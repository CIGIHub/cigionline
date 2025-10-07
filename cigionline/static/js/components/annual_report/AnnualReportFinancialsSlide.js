import PropTypes from 'prop-types';
import React, { useMemo, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '../../../css/components/annual_reports/AnnualReportsFinancialsSlide.scss';
import { faDownload } from '@fortawesome/pro-light-svg-icons';

function AnnualReportsFinancialsSlide({ slide, lang }) {
  const navigate = useNavigate();
  const { slug } = useParams();
  const tabs = useMemo(
    () => slide?.slide_content.auditor_reports || [],
    [slide],
  );

  console.log(slide);
  console.log(tabs);

  useEffect(() => {
    if (!slug && tabs.length > 0) {
      const tabSlug = lang === 'fr' ? `${tabs[0].slug_fr}/fr` : tabs[0].slug_en;
      navigate(tabSlug, { replace: true });
    }
  }, [slug, tabs, navigate]);

  const activeSlug =
    slug || (lang === 'fr' && tabs[0].slug_fr) || tabs[0].slug_en;
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
                          <Link
                            to={tabSlug}
                            className={`financials-tab-link ${
                              isActive ? 'is-active' : ''
                            }`}
                            aria-current={isActive ? 'page' : undefined}
                          >
                            <span className={isActive ? '' : 'underline'}>
                              {tabTitle}
                            </span>
                          </Link>
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

              <div className="financials-content mt-4">
                {activeTab ? (
                  typeof activeTab.content === 'string' ? (
                    <div
                      dangerouslySetInnerHTML={{ __html: activeTab.content }}
                    />
                  ) : (
                    activeTab.content
                  )
                ) : (
                  <p className="text-muted">
                    {lang === 'en'
                      ? 'No content available.'
                      : 'Aucun contenu disponible.'}
                  </p>
                )}
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
