import PropTypes from 'prop-types';
import React, { useMemo, useEffect, useState } from 'react';
import { Link, useParams, useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '../../../css/components/annual_reports/AnnualReportsOutputsSlide.scss';
import { faFileAlt } from '@fortawesome/pro-light-svg-icons';

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const backLinkIconClass = (type) => {
  switch (type) {
    case 'Publication':
      return 'publication';
    case 'Event':
      return 'event';
    case 'Opinion':
      return 'article';
    default:
      return 'default';
  }
};

function AnnualReportOutputsSlide({ slide, lang }) {
  const navigate = useNavigate();
  const { subSlug } = useParams();
  const { pathname } = useLocation();
  const [page, setPage] = useState(null);
  const currentLang = lang === 'fr' ? 'fr' : 'en';
  const tabs = useMemo(
    () => slide.slide_content.outputs_and_activities || [],
    [slide],
  );
  const outputTitles = tabs.map((output) => output.title);

  const base = React.useMemo(() => {
    const trimmed = pathname.replace(/\/+$/, '');
    return subSlug ? trimmed.replace(/\/[^/]+$/, '') : trimmed;
  }, [pathname, subSlug]);

  useEffect(() => {
    if (!subSlug && tabs.length > 0) {
      const tabSlug = tabs[0].slug;
      navigate(tabSlug, { replace: true });
    }
  }, [subSlug, tabs, navigate]);

  const activeSlug = subSlug || tabs[0].slug;
  const activeTab = tabs.find((t) => t.slug === activeSlug) || null;

  return (
    <div className="anual-report-slide">
      <div className="background-row background-outputs-activities" />
      <div className="outputs-activities">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <h1
                aria-live="assertive"
                dangerouslySetInnerHTML={{
                  __html:
                    lang === 'fr' ? slide.slide_title_fr : slide.slide_title,
                }}
              />
            </div>
          </div>
          <div className="row outputs-activities-content">
            <div className="col-12">
              <div className="outputs-activities-header clearfix">
                <div className="publications-menu">
                  {outputTitles.map((title, index) => (
                    <React.Fragment key={`title-${index}`}>
                      {activeTab.slug === tabs[index].slug ? (
                        <span>{title}</span>
                      ) : (
                        <Link key={title} to={`${base}/${tabs[index].slug}`}>
                          <button
                            type="button"
                            key={title}
                            className={`view-publications-btn${
                              index === 0 ? ' is-active' : ''
                            }`}
                          >
                            {title}
                          </button>
                        </Link>
                      )}
                      {index < outputTitles.length - 1 && (
                        <span className="separator">/</span>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <div
            className="row outputs-activities-content outputs-activities-content-items"
            key={subSlug}
          >
            {activeTab.pages.map((p, index) => (
              <div className="col-12 col-md-3" key={`${p.id}-${index}`}>
                <a
                  className="outputs-activities-listing d-lg-none"
                  href={p.link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <h6>
                    {formatDate(p.date)}
                    <span>|</span>
                    {p.type}
                  </h6>
                  <h5>
                    <span className="underline">{p.title}</span>
                  </h5>
                </a>
                <button
                  type="button"
                  className="outputs-activities-listing d-none d-lg-flex"
                  onClick={() => setPage(p)}
                >
                  <h6>
                    {formatDate(p.date)}
                    <span>|</span>
                    {p.type}
                  </h6>
                  <h5>
                    <span className="underline">{p.title}</span>
                  </h5>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
      {page && (
        <div
          className="outputs-activities-overlay background-image"
          style={{
            backgroundImage: `url(${page.image}),url(${page.image_thumbnail})`,
          }}
        >
          <div className="outputs-activities-overlay-container">
            <div className="container">
              <div className="row">
                <div className="col-md-10">
                  <button
                    type="button"
                    className="clearfix back-link"
                    onClick={() => setPage(null)}
                  >
                    <div
                      className={`float-left back-link-icon ${backLinkIconClass(
                        page.type,
                      )}`}
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="0.22in"
                        height="0.19in"
                        viewBox="0 0 16 14"
                      >
                        <defs>
                          <clipPath
                            id="a"
                            transform="translate(-256.98 -317)"
                            style={{ fill: 'none' }}
                          >
                            <rect
                              className="a"
                              x="257"
                              y="317"
                              width="16"
                              height="14"
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
                      <span className="underline">Back</span>
                    </p>
                  </button>
                </div>
              </div>
              <div className="row">
                <div className="col-md-10">
                  <h2>{page.title}</h2>
                </div>
              </div>
              <div className="row">
                <div className="col-md-10">
                  <div className="cigi-red-line" />
                </div>
              </div>
              <div className="row">
                <div className="col-md-10">
                  <h6 className="pub-date">
                    {page.authors.join(', ')}
                    <br />
                    {formatDate(page.date)}
                  </h6>
                  <div
                    className="publication-summary"
                    dangerouslySetInnerHTML={{ __html: page.description }}
                  />
                </div>
              </div>
              <div className="row">
                <div className="col-md-10">
                  <a
                    className="clearfix read-link"
                    href={page.link}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <div className="float-left read-link-icon">
                      <FontAwesomeIcon icon={faFileAlt} size="lg" />
                    </div>
                    <p>
                      <span className="underline">
                        {page.type === 'Publication' && <>Read publication</>}
                        {page.type === 'Event' && (
                          <>Learn more about the event</>
                        )}
                        {page.type === 'Opinion' && <>Read opinion</>}
                      </span>
                    </p>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnnualReportOutputsSlide;
AnnualReportOutputsSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
};
