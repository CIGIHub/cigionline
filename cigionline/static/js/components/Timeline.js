import React from 'react';

const Timeline = ({ slide }) => ( // eslint-disable-line no-unused-vars
  <>
    <div className="timeline-container show-for-large">
      <div className="grid-container">
        <div className="grid-x grid-margin-x">
          <div className="cell medium-8">
            <h1>Explore Timeline</h1>
          </div>
          <div className="cell medium-4">
            <div className="grid-x">
              <div className="cell clearfix opinions-label">
                <div className="timeline-bubble-preview opinion float-right" />
                <span className="timeline-bubble-label float-right">
                  Opinions
                </span>
              </div>
            </div>
            <div className="grid-x">
              <div className="cell clearfix publications-label">
                <div className="timeline-bubble-preview publication float-right" />
                <span className="timeline-bubble-label float-right">
                  Publications
                </span>
              </div>
            </div>
            <div className="grid-x">
              <div className="cell clearfix events-label">
                <div className="timeline-bubble-preview event float-right" />
                <span className="timeline-bubble-label float-right">Events</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div className="timeline-search-container show-for-large">
      <div className="grid-container">
        <div className="grid-x grid-margin-x">
          <div className="cell medium-4 timeline-search">
            <svg
              viewBox="0 0 512 512"
              xmlns="http://www.w3.org/2000/svg"
              role="img"
              focusable="false"
              aria-hidden="true"
              data-icon="search"
              data-prefix="fal"
              className="svg-inline--fa fa-search fa-w-16 fa-sm"
            >
              <path
                fill="currentColor"
                d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"
              />
            </svg>
            <input placeholder="Search" type="text" />
          </div>
        </div>
      </div>
    </div>
    <div className="timeline-container hide-for-large mobile">
      <div className="grid-container">
        <div className="grid-x grid-margin-x">
          <div className="cell medium-8">
            <h1>Explore Timeline</h1>
            <p>
              The interactive timeline cannot be displayed on your mobile
              device. For the best experience, please view on a desktop
              browser.
            </p>
          </div>
        </div>
      </div>
    </div>
    <div className="show-for-large">
      <div>
        <div className="timeline show-for-large">
          <p className="date-marker date-marker-beg">2019</p>
          <p className="date-marker date-marker-end">2020</p>
          <div className="timeline-line line-start" />
          <div className="ticks">
            <div className="tick">AUG</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">SEP</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">OCT</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">NOV</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">DEC</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">JAN</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">FEB</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">MAR</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">APR</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">MAY</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">JUN</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick line">JUL</div>
            <div className="tick line">&nbsp;</div>
            <div className="tick">AUG</div>
          </div>
          <div className="timeline-line line-end" />
          <div
            className="timeline-bubble node-15400 opinion search-match"
            style={{ left: 1, top: 294 }}
          >
            <div className="preview">
              <div className="preview-image-container">
                <div className="preview-image timeline-15400-thumbnail" />
              </div>
              <div className="preview-line" />
              <div className="preview-text preview-text-right">
                <h6>Opinion</h6>
                <h5>What You Need to Know about Libra</h5>
                <h6 className="pub-date">August 1, 2019</h6>
              </div>
            </div>
          </div>

          <div
            className="timeline-bubble node-15400 publication search-match"
            style={{ left: 12, top: 384 }}
          >
            <div className="preview">
              <div className="preview-image-container">
                <div className="preview-image timeline-15400-thumbnail" />
              </div>
              <div className="preview-line" />
              <div className="preview-text preview-text-right">
                <h6>Opinion</h6>
                <h5>What You Need to Know about Libra</h5>
                <h6 className="pub-date">August 1, 2019</h6>
              </div>
            </div>
          </div>

          <div
            className="timeline-bubble node-15400 event search-match"
            style={{ left: 23, top: 594 }}
          >
            <div className="preview">
              <div className="preview-image-container">
                <div className="preview-image timeline-15400-thumbnail" />
              </div>
              <div className="preview-line" />
              <div className="preview-text preview-text-right">
                <h6>Opinion</h6>
                <h5>What You Need to Know about Libra</h5>
                <h6 className="pub-date">August 1, 2019</h6>
              </div>
            </div>
          </div>

          <div
            className="timeline-bubble node-15400 event search-match"
            style={{ left: 41, top: 214 }}
          >
            <div className="preview">
              <div className="preview-image-container">
                <div className="preview-image timeline-15400-thumbnail" />
              </div>
              <div className="preview-line" />
              <div className="preview-text preview-text-right">
                <h6>Opinion</h6>
                <h5>What You Need to Know about Libra</h5>
                <h6 className="pub-date">August 1, 2019</h6>
              </div>
            </div>
          </div>

          <div
            className="timeline-bubble node-15400 opinion search-match"
            style={{ left: 34, top: 194 }}
          >
            <div className="preview">
              <div className="preview-image-container">
                <div className="preview-image timeline-15400-thumbnail" />
              </div>
              <div className="preview-line" />
              <div className="preview-text preview-text-right">
                <h6>Opinion</h6>
                <h5>What You Need to Know about Libra</h5>
                <h6 className="pub-date">August 1, 2019</h6>
              </div>
            </div>
          </div>
          <div
            className="timeline-bubble node-15400 opinion search-match"
            style={{ left: 45, top: 494 }}
          >
            <div className="preview">
              <div className="preview-image-container">
                <div className="preview-image timeline-15400-thumbnail" />
              </div>
              <div className="preview-line" />
              <div className="preview-text preview-text-right">
                <h6>Opinion</h6>
                <h5>What You Need to Know about Libra</h5>
                <h6 className="pub-date">August 1&#125;&#125; 2019</h6>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="timeline-search-container">
        <div className="grid-container">
          <div className="grid-x grid-margin-x">
            <div className="cell" />
          </div>
        </div>
      </div>
    </div>
  </>
);

export default Timeline;
