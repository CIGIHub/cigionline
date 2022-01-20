/* eslint-disable no-unused-vars */
/* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
import React, { Fragment, useState } from 'react';
import queryString from 'query-string';

const Timeline = ({ slide, slides }) => {
  const timelineData = slides.find((item) => item.type === 'outputsandactivitiesslidepage');
  const originUrl = window.location.origin;
  const currentPath = window.location.pathname;
  const params = queryString.parse(window.location.search);
  const id = params.id ? params.id : null;
  const [itemId, setItemId] = useState(id);
  let itemObject = null;
  if (id != null) {
    itemObject = timelineData.value.publications.items.find((obj) => obj.id === parseInt(id, 10));
    if (itemObject == null) {
      itemObject = timelineData.value.opinions.items.find((obj) => obj.id === parseInt(id, 10));
    }
    if (itemObject == null) {
      itemObject = timelineData.value.events.items.find((obj) => obj.id === parseInt(id, 10));
    }
  }

  function calleft(val, mappedItem) {
    const months = ['aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul'];
    const monthIndex = months.findIndex(
      (mon) => mappedItem.publishing_date.toLocaleLowerCase().indexOf(mon) > -1,
    );
    const leftVal = val === 0 ? 1 : 1 + (((val) % 8) * 11);
    return leftVal + (85 * monthIndex) + monthIndex;
  }

  function calTop(val, mappedItem) {
    return val === 0 ? 294 : 294 - (parseInt((val + 1) / 8, 10) * 11);
  }

  function monthData(val) {
    const pubMonth = timelineData.value.publications.items.filter(
      (item) => item.publishing_date.toLocaleLowerCase().indexOf(val) > -1,
    );
    pubMonth.map((item) => { item.art_type = 'publication'; return item; });
    const opMonth = timelineData.value.opinions.items.filter(
      (item) => item.publishing_date.toLocaleLowerCase().indexOf(val) > -1,
    );
    opMonth.map((item) => { item.art_type = 'opinion'; return item; });
    const eventsMonth = timelineData.value.events.items.filter(
      (item) => item.event_date.toLocaleLowerCase().indexOf(val) > -1,
    );
    eventsMonth.map((item) => { item.art_type = 'event'; item.publishing_date = item.event_date; return item; });
    const monthDataUnsorted = [...pubMonth,
      ...opMonth,
      ...eventsMonth];
    return monthDataUnsorted.sort(
      (a, b) => Date.parse(a.publishing_date) - Date.parse(b.publishing_date),
    );
  }

  function loadContent() {
    const months = ['aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul'];

    return months.map(function(item) {
      const monthMappedData = monthData(item);
      return monthMappedData.map(function(mappedItem, index) {
        return (
          <>
            <div
              className={`timeline-bubble node-15400 ${mappedItem.art_type} search-match`}
              style={{ left: calleft(index, mappedItem), top: calTop(index, mappedItem) }}
              onClick={(e) => {
                e.preventDefault();
                setItemId(mappedItem.id);
                window.history.pushState({}, '', `${originUrl}${currentPath}?id=${mappedItem.id}`);
              }}
            >
              <div className="preview">
                <div className="preview-image-container">
                  <div className="preview-image timeline-15400-thumbnail" style={{ backgroundImage: `url(${originUrl}${mappedItem.image})` }} />
                </div>
                <div className="preview-line" />
                <div className="preview-text preview-text-right">
                  <h6>{ mappedItem.type }</h6>
                  <h5>{ mappedItem.title }</h5>
                  <h6 className="pub-date">{ mappedItem.publishing_date ? mappedItem.publishing_date : mappedItem.event_date }</h6>
                </div>
              </div>
            </div>
          </>
        );
      });
    });
  }

  function loadItemDetail() {
    return (
      <div className="outputs-activities-overlay background-image" style={{ backgroundImage: `url(${originUrl}${itemObject.image})` }}>
        <div className="outputs-activities-overlay-container">
          <div className="grid-container">
            <div className="grid-x grid-margin-x">
              <div className="cell medium-10">
                <button
                  className="clearfix back-link"
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    setItemId(null);
                    window.history.pushState({}, '', `${originUrl}${currentPath}`);
                  }}
                >
                  <div className="float-left back-link-icon publication">
                    <svg xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink" width="0.22in" height="0.19in" viewBox="0 0 16 14">
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
                    <span className="underline">Back</span>
                  </p>
                </button>
              </div>
            </div>
            <div className="grid-x grid-margin-x">
              <div className="cell medium-10">
                <h2>{ itemObject.title }</h2>
              </div>
            </div>
            <div className="grid-x grid-margin-x">
              <div className="cell medium-10">
                <div className="cigi-red-line">&nbsp;</div>
              </div>
            </div>
            <div className="grid-x grid-margin-x">
              <div className="cell medium-10">
                <h6 className="pub-date">
                  { itemObject.authors.length === 0
                    ? itemObject.speakers.join(', ') : itemObject.authors.join(', ') }
                  <br />
                  { itemObject.publishing_date
                    ? itemObject.publishing_date : itemObject.event_date }
                </h6>
                <p className="publication-summary">{ itemObject.summary }</p>
              </div>
            </div>
            <div className="grid-x grid-margin-x">
              <div className="cell medium-10">
                <a className="clearfix read-link" href={itemObject.url_landing_page} target="_blank" rel="noopener noreferrer">
                  <div className="float-left read-link-icon">
                    <svg viewBox="0 0 384 512" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" aria-hidden="true" data-icon="file-alt" data-prefix="fal" id="ember1580" className="svg-inline--fa fa-file-alt fa-w-12 fa-lg ember-view">
                      <path fill="currentColor" d="M369.9 97.9L286 14C277 5 264.8-.1 252.1-.1H48C21.5 0 0 21.5 0 48v416c0 26.5 21.5 48 48 48h288c26.5 0 48-21.5 48-48V131.9c0-12.7-5.1-25-14.1-34zm-22.6 22.7c2.1 2.1 3.5 4.6 4.2 7.4H256V32.5c2.8.7 5.3 2.1 7.4 4.2l83.9 83.9zM336 480H48c-8.8 0-16-7.2-16-16V48c0-8.8 7.2-16 16-16h176v104c0 13.3 10.7 24 24 24h104v304c0 8.8-7.2 16-16 16zm-48-244v8c0 6.6-5.4 12-12 12H108c-6.6 0-12-5.4-12-12v-8c0-6.6 5.4-12 12-12h168c6.6 0 12 5.4 12 12zm0 64v8c0 6.6-5.4 12-12 12H108c-6.6 0-12-5.4-12-12v-8c0-6.6 5.4-12 12-12h168c6.6 0 12 5.4 12 12zm0 64v8c0 6.6-5.4 12-12 12H108c-6.6 0-12-5.4-12-12v-8c0-6.6 5.4-12 12-12h168c6.6 0 12 5.4 12 12z" />
                    </svg>
                  </div>
                  <p>
                    <span className="underline">
                      Read this publication
                    </span>
                  </p>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
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
          <div className="timeline" style={{ top: (itemObject ? '40px' : '50%') }}>
            <p className="date-marker date-marker-beg">2020</p>
            <p className="date-marker date-marker-end">2021</p>
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
            { loadContent() }
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
      { itemId ? loadItemDetail() : '' }
    </>
  );
};

export default Timeline;
