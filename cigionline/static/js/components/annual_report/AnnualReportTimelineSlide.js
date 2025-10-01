import React, { useState } from 'react';
import PropTypes from 'prop-types';
import '../../../css/components/annual_reports/AnnualReportTimelineSlide.scss';

// Dummy translation function
const t = (key) => key;

// Dummy FaIcon component
function FaIcon({ icon, prefix, size }) {
  return <i className={`fa ${prefix} fa-${icon} fa-${size}`} />;
}

// Dummy Input component
function Input({ placeholder, value, onChange }) {
  return (
    <input
      type="text"
      className="form-control"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
    />
  );
}

// Dummy FooterPhoto component
function FooterPhoto() {
  return <div className="footer-photo" />;
}

// Dummy CigiTimeline component
function CigiTimeline({ nodes, nodeId, search }) {
  return <div className="timeline" />;
}

function AnnualReportTimelineSlide({
  nodes,
  nodeId,
  search: initialSearch,
  node,
  overlayStyle,
  isEvent,
  isArticle,
  isPublication,
  onClearSearch,
  onPreviousNode,
  onNextNode,
  onCloseNode,
}) {
  const [search, setSearch] = useState(initialSearch || '');

  return (
    <>
      <div className="background-row timeline-background" />
      <div className="timeline-container d-none d-lg-block">
        <div className="container">
          <div className="row">
            <div className="col-md-8">
              <h1>{slide.title}</h1>
            </div>
            <div className="col-md-4">
              <div className="row">
                <div className="col clearfix opinions-label">
                  <div className="timeline-bubble-preview opinion float-end" />
                  <span className="timeline-bubble-label float-end">{t('opinions')}</span>
                </div>
              </div>
              <div className="row">
                <div className="col clearfix publications-label">
                  <div className="timeline-bubble-preview publication float-end" />
                  <span className="timeline-bubble-label float-end">{t('publications')}</span>
                </div>
              </div>
              <div className="row">
                <div className="col clearfix events-label">
                  <div className="timeline-bubble-preview event float-end" />
                  <span className="timeline-bubble-label float-end">{t('events')}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="timeline-search-container d-none d-lg-block">
        <div className="container">
          <div className="row">
            <div className="col-md-4 timeline-search d-flex align-items-center">
              <FaIcon icon="search" prefix="fal" size="sm" />
              <Input
                placeholder={t('timeline.search')}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            {search && (
              <div className="col-md-2">
                <button
                  type="button"
                  className="clear-button btn btn-link"
                  onClick={() => {
                    setSearch('');
                    if (onClearSearch) onClearSearch();
                  }}
                >
                  <FaIcon icon="times" prefix="fal" size="sm" />
                  {t('clear')}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="timeline-container d-lg-none mobile">
        <div className="container">
          <div className="row">
            <div className="col-md-8">
              <h1>{t('timeline.title')}</h1>
              <p>{t('timeline.cannotBeDisplayed')}</p>
            </div>
          </div>
        </div>
      </div>
      <div className="d-none d-lg-block">
        <CigiTimeline nodes={nodes} nodeId={nodeId} search={search} />
        <div className="timeline-search-container">
          <div className="container">
            <div className="row">
              <div className="col" />
            </div>
          </div>
        </div>
        <FooterPhoto />
        {node && (
          <div className="timeline-overlay background-image" style={overlayStyle}>
            <div className="timeline-overlay-container">
              <div className="container">
                <div className="row">
                  <div className="col-md-10">
                    <h2>{node.title}</h2>
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
                      {!isEvent && (
                        <>
                          {node.author_str}
                          <br />
                        </>
                      )}
                      {node.date_str}
                    </h6>
                    <p className="node-summary">{node.summary}</p>
                  </div>
                </div>
                <div className="row">
                  <div className="col-md-10">
                    <a
                      className="clearfix read-link"
                      href={node.url_landing_page}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <div className="float-start read-link-icon">
                        <FaIcon icon="file-alt" prefix="fal" size="lg" />
                      </div>
                      <p>
                        <span className="underline">
                          {isArticle && t('outputsAndActivities.opinionLink')}
                          {isEvent && t('outputsAndActivities.eventLink')}
                          {isPublication && t('outputsAndActivities.publicationLink')}
                        </span>
                      </p>
                    </a>
                  </div>
                </div>
              </div>
            </div>
            <div className="timeline-nav">
              <div className="container">
                <div className="row">
                  <div className="col-md-8">
                    <button
                      type="button"
                      className="previous scroll-arrow scroll-arrow-left btn btn-link"
                      onClick={onPreviousNode}
                    />
                    <button
                      type="button"
                      className="next scroll-arrow scroll-arrow-right btn btn-link"
                      onClick={onNextNode}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="timeline-back">
              <div className="container">
                <div className="row">
                  <div className="col-md-8">
                    <button
                      type="button"
                      className="clearfix back-link btn btn-link"
                      onClick={onCloseNode}
                    >
                      <div className={`float-start back-link-icon ${node.type}`}>
                        {/* SVG remains unchanged */}
                        <svg xmlns="http://www.w3.org/2000/svg" width="0.22in" height="0.19in" viewBox="0 0 16 14">
                          <defs>
                            <clipPath id="a" transform="translate(-256.98 -317)" style={{ fill: 'none' }}>
                              <rect className="a" x="257" y="317" width="16" height="14" />
                            </clipPath>
                          </defs>
                          <g className="b" style={{ clipPath: 'url(#a)' }}>
                            <path d="M262.73,317.19a.69.69,0,0,1,.55-.19.81.81,0,0,1,.5.23.7.7,0,0,1,.2.52v2.5a14.77,14.77,0,0,1,6.38,1.16,4.83,4.83,0,0,1,2.63,4.66,5.53,5.53,0,0,1-.78,2.75,6.23,6.23,0,0,1-1.81,2.06.56.56,0,0,1-.45.11.6.6,0,0,1-.37-.23.43.43,0,0,1,0-.44,6,6,0,0,0,.28-3.48,2.82,2.82,0,0,0-1.91-1.8,12.18,12.18,0,0,0-3.91-.53v2.75a.7.7,0,0,1-.2.52.8.8,0,0,1-.5.23.7.7,0,0,1-.55-.19l-5.5-4.75a.76.76,0,0,1,0-1.12Z" transform="translate(-256.98 -317)" />
                          </g>
                        </svg>
                      </div>
                      <p>
                        <span className="underline">{t('timeline.back')}</span>
                      </p>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

AnnualReportTimelineSlide.propTypes = {
  nodes: PropTypes.array,
  nodeId: PropTypes.any,
  search: PropTypes.string,
  node: PropTypes.object,
  overlayStyle: PropTypes.object,
  isEvent: PropTypes.bool,
  isArticle: PropTypes.bool,
  isPublication: PropTypes.bool,
  onClearSearch: PropTypes.func,
  onPreviousNode: PropTypes.func,
  onNextNode: PropTypes.func,
  onCloseNode: PropTypes.func,
};

export default AnnualReportTimelineSlide;
