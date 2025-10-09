import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faTimes } from '@fortawesome/pro-light-svg-icons';
import '../../../css/components/annual_reports/AnnualReportTimelineSlide.scss';

const BEGINNING_OF_YEAR = new Date('2023-08-01'); // match Ember
const DAYS_IN_YEAR = 365;
const RADIUS = 5;
const TIMELINE_MIDDLE = 300; // px, matches Ember's 300

function getNodeDate(node) {
  // node.published_date || node.event_date (ISO)
  return new Date(node.published_date || node.event_date);
}

function getThumbnailUrl(node) {
  // Replace if you have a service for this like Ember's backgroundImage.getNodeBackgroundImage
  return node.thumbnailUrl || '';
}

function canDrawCircle(matrix, x, y, r) {
  /* mirrors Ember _canDrawCircle */
  for (let i = x - r; i <= x + r; i += 1) {
    let x2 = i;
    if (x2 === x - r) x2 = x - r + 0.5;
    else if (x2 === x + r) x2 = x + r - 0.5;
    const y2 = Math.sqrt(r ** 2 - (x2 - x) ** 2) + y;
    const h = Math.ceil(Math.abs(y2 - y));
    for (let j = y - h; j <= y + h; j += 1) {
      if (matrix[i]?.[j]) return false;
    }
  }
  return true;
}

function drawCircle(matrix, x, y, r, remove = false) {
  /* mirrors Ember _drawCircle */
  for (let i = x - r; i <= x + r; i += 1) {
    let x2 = i;
    if (x2 === x - r) x2 = x - r + 0.5;
    else if (x2 === x + r) x2 = x + r - 0.5;
    const y2 = Math.sqrt(r ** 2 - (x2 - x) ** 2) + y;
    const h = Math.ceil(Math.abs(y2 - y));
    for (let j = y - h; j <= y + h; j += 1) {
      if (matrix[i]) matrix[i][j] = !remove;
    }
  }
}

function layoutNodes(nodes, width) {
  if (!width || width <= 0) return [];

  const daysWidth = width / DAYS_IN_YEAR;
  const matrix = Array(Math.floor(width) + 1)
    .fill(null)
    .map(() => Array(TIMELINE_MIDDLE * 2 + 1).fill(false));

  return nodes.map((node, ind) => {
    // base x by days from BEGINNING_OF_YEAR
    const numDays = Math.floor(
      (getNodeDate(node) - BEGINNING_OF_YEAR) / 86400000,
    );
    let cx = Math.floor(numDays * daysWidth);
    if (cx < RADIUS) cx = RADIUS + 1;
    if (cx > width - RADIUS) cx = width - RADIUS - 1;

    // base y midline; then seek a free arc as Ember does
    let cy = TIMELINE_MIDDLE;
    for (let i = 0; i < TIMELINE_MIDDLE - RADIUS; i += 1) {
      let placed = false;
      for (let j = 0; j < i; j += 1) {
        if (
          ind <= nodes.length / 2 &&
          canDrawCircle(matrix, cx + j, cy - i + j, RADIUS)
        ) {
          cx += j;
          cy = cy - i + j;
          placed = true;
          break;
        } else if (
          ind > nodes.length / 2 &&
          canDrawCircle(matrix, cx - j, cy - i - j, RADIUS)
        ) {
          cx -= j;
          cy = cy - i - j;
          placed = true;
          break;
        }
      }
      if (placed) break;
    }

    drawCircle(matrix, cx, cy, RADIUS);

    return {
      ...node,
      cx,
      cy,
      r: RADIUS,
    };
  });
}

function matchesSearch(node, search) {
  if (!search) return true;
  const s = search.toLowerCase();
  const fields = [
    node.title || '',
    (node.authors || []).join(', '),
    (node.subtype || []).join(', '),
    node.summary || '',
  ];
  return fields.some((v) => v.toLowerCase().includes(s));
}
function AnnualReportTimelineSlide({ slide, lang }) {
  const [search, setSearch] = useState('');
  const [nodeId, setNodeId] = useState(null);
  const [hoveredId, setHoveredId] = useState(null);

  const timelineRef = useRef(null);
  const [timelineWidth, setTimelineWidth] = useState(0);

  const nodes = slide?.slide_content?.nodes.items || [];
  console.log(nodes);

  const recalcWidth = useCallback(() => {
    if (timelineRef.current) {
      setTimelineWidth(Math.floor(timelineRef.current.clientWidth));
    }
  }, []);

  useEffect(() => {
    recalcWidth();
    window.addEventListener('resize', recalcWidth);
    return () => window.removeEventListener('resize', recalcWidth);
  }, [recalcWidth]);

  // compute positioned nodes (Ember drawTimeline up to assigning cx/cy/r)
  const positioned = useMemo(
    () => layoutNodes(nodes, timelineWidth),
    [nodes, timelineWidth],
  );

  // search classification like Ember's runSearch
  const classified = useMemo(
    () =>
      positioned.map((n) => ({
        ...n,
        isMatch: matchesSearch(n, search),
      })),
    [positioned, search],
  );

  // click behavior (Ember showNode)
  const onBubbleClick = (id) => {
    setNodeId(id);
    // the Ember code animates top with jQuery; here we toggle a class
    // You can add CSS to animate .timeline-top state.
  };
  return (
    <>
      <div className="background-row timeline-background" />
      <div className="timeline-container d-none d-lg-block">
        <div className="container">
          <div className="row">
            <div className="col-md-8">
              <h1>Explore Timeline</h1>
            </div>
            <div className="col-md-4">
              <div className="row">
                <div className="col clearfix type-label">
                  <span className="timeline-bubble-label">Opinions</span>
                  <div className="timeline-bubble-preview opinion" />
                </div>
              </div>
              <div className="row">
                <div className="col clearfix type-label">
                  <span className="timeline-bubble-label">Publications</span>
                  <div className="timeline-bubble-preview publication" />
                </div>
              </div>
              <div className="row">
                <div className="col clearfix type-label">
                  <span className="timeline-bubble-label">Events</span>
                  <div className="timeline-bubble-preview event" />
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
              <FontAwesomeIcon icon={faSearch} size="sm" />
              <input
                type="text"
                className="form-control"
                placeholder="Search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            {search && (
              <div className="col-md-2">
                <button
                  type="button"
                  className="clear-button"
                  onClick={() => {
                    setSearch('');
                  }}
                >
                  <FontAwesomeIcon icon={faTimes} size="sm" />
                  Clear
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
              <h1>Explore timeline</h1>
              <p>
                The interactive timeline cannot be displayed on your mobile
                device. For the best experience, please view on a desktop
                browser.
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="d-none d-lg-block">
        <div className="timeline d-none d-lg-block">
          <p className="date-marker date-marker-beg">2023</p>
          <p className="date-marker date-marker-end">2024</p>
          <div className="timeline-line line-start" />
          <div className="ticks">
            <div className="tick">August</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">September</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">October</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">November</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">December</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">January</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">February</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">March</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">April</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">May</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">June</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">July</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick">august</div>
          </div>
          <div className="timeline-line line-end" />
        </div>
        {/* Bubbles */}
        {classified.map((node) => {
          const top = node.cy - node.r;
          const left = node.cx - node.r;
          const typeClass =
            node.type === 'publication'
              ? 'publication'
              : node.type === 'article'
              ? 'opinion'
              : node.type === 'event'
              ? 'event'
              : '';

          const isHovered = hoveredId === node.id;
          const anyHovered = hoveredId !== null;
          const dimSiblings =
            anyHovered && hoveredId !== node.id && node.isMatch;

          return (
            <div
              key={node.id}
              className={`timeline-bubble node-${node.id} ${typeClass} ${
                node.isMatch ? 'search-match' : 'search-no-match'
              } ${isHovered ? 'hovered' : ''} ${dimSiblings ? 'dimmed' : ''}`}
              style={{ left, top }}
              onMouseEnter={() => setHoveredId(node.isMatch ? node.id : null)}
              onMouseLeave={() => setHoveredId(null)}
              onClick={() => node.isMatch && onBubbleClick(node.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && node.isMatch) onBubbleClick(node.id);
              }}
              aria-label={`${node.type}: ${node.title}`}
            >
              {/* Preview (mimics Ember) */}
              <div className="preview">
                <div className="preview-image-container">
                  <div
                    className={`preview-image timeline-${node.id}-thumbnail`}
                    style={{
                      backgroundImage: `url('${getThumbnailUrl(node)}')`,
                    }}
                  />
                </div>
                <div className="preview-line" />
                <div
                  className={`preview-text ${
                    node.cx >= timelineWidth * 0.75
                      ? 'preview-text-left'
                      : 'preview-text-right'
                  }`}
                >
                  <h6>{node.type === 'article' ? 'Opinion' : node.type}</h6>
                  <h5>
                    {Array.isArray(node.subtype) &&
                    node.subtype[0] === 'Books' ? (
                      <em>{node.title}</em>
                    ) : (
                      node.title
                    )}
                  </h5>
                  {node.date_str && (
                    <h6 className="pub-date">{node.date_str}</h6>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        {/* <div className="timeline-search-container">
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
                      <div className={`float-start back-link-icon $.type}`}>
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
        )} */}
      </div>
    </>
  );
}

AnnualReportTimelineSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
};

export default AnnualReportTimelineSlide;
