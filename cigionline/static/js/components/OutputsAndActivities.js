/* eslint-disable no-unused-vars, jsx-a11y/anchor-is-valid */
import React, { Fragment, useState } from 'react';
import queryString from 'query-string';

const OutputsAndActivities = ({ slide, setOutputDetail }) => { // eslint-disable-line no-unused-vars
  const itemsPerPage = 1;
  const originUrl = window.location.origin;
  const currentPath = window.location.pathname;
  const params = queryString.parse(window.location.search);
  const oatype = params.type ? params.type : 'publications';
  const pageNum = params.page ? params.page : '1';
  const id = params.id ? params.id : null;
  const [pageType, setPageType] = useState(oatype);
  const [currentPage, setCurrentPage] = useState(pageNum);
  const [itemId, setItemId] = useState(id);
  let pageObjects = [];
  if (pageType === 'publications') {
    pageObjects = slide.value.publications.items;
  } else if (pageType === 'opinions') {
    pageObjects = slide.value.opinions.items;
  } else if (pageType === 'events') {
    pageObjects = slide.value.events.items;
  }

  const selectedItem = id ? pageObjects.find((obj) => obj.id === parseInt(id, 10)) : null;
  const [itemObject, setItemObject] = useState(selectedItem);

  function findNumberOfPages() {
    return Math.ceil(pageObjects.length / itemsPerPage);
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
                    setOutputDetail(false);
                    window.history.pushState({}, '', `${originUrl}${currentPath}?type=${pageType}&page=${currentPage}`);
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
                  { currentPage === 'events' ? itemObject.speakers.join(', ') : itemObject.authors.join(', ') }
                  <br />
                  { currentPage === 'events' ? itemObject.event_date : itemObject.publishing_date }
                </h6>
                <p className="publication-summary">{ itemObject.title }</p>
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

  function getFromIndex(pageNo, perPage, totalLength) {
    return (
      +pageNo
      && +pageNo <= Math.ceil(totalLength / perPage)
      && perPage * (pageNo - 1)
    );
  }

  function setOffset(value) {
    setCurrentPage(value);
    window.history.pushState({}, '', `${originUrl}${currentPath}?type=${pageType}&page=${value}`);
  }

  function renderPageNumbers() {
    const numberOfPages = findNumberOfPages();
    const pages = [];
    for (let i = 1; i <= numberOfPages; i++) {
      if (currentPage === i) {
        pages.push(
          <span className="page-number current">
            {i}
          </span>,
        );
      } else {
        pages.push(
          <button
            className="page-number"
            type="button"
            onClick={() => setOffset(parseInt(i, 10))}
          >
            {i}
          </button>,
        );
      }
    }
    return pages;
  }

  function renderPrevButton() {
    return (
      <>
        {currentPage > 1 ? (
          <button
            className="page-arrow page-arrow-previous "
            type="button"
            onClick={() => setOffset(parseInt(currentPage, 10) - 1)}
          >
            <svg viewBox="0 0 256 512" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" aria-hidden="true" data-icon="chevron-left" data-prefix="fal" id="ember1186" className="svg-inline--fa fa-chevron-left fa-w-8 fa-sm ember-view">
              <path fill="currentColor" d="M238.475 475.535l7.071-7.07c4.686-4.686 4.686-12.284 0-16.971L50.053 256 245.546 60.506c4.686-4.686 4.686-12.284 0-16.971l-7.071-7.07c-4.686-4.686-12.284-4.686-16.97 0L10.454 247.515c-4.686 4.686-4.686 12.284 0 16.971l211.051 211.05c4.686 4.686 12.284 4.686 16.97-.001z" />
            </svg>
          </button>
        ) : (
          <button
            className="page-arrow page-arrow-previous disabled"
            type="button"
          >
            <svg viewBox="0 0 256 512" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" aria-hidden="true" data-icon="chevron-left" data-prefix="fal" id="ember18" className="svg-inline--fa fa-chevron-left fa-w-8 fa-sm ember-view">
              <path fill="currentColor" d="M238.475 475.535l7.071-7.07c4.686-4.686 4.686-12.284 0-16.971L50.053 256 245.546 60.506c4.686-4.686 4.686-12.284 0-16.971l-7.071-7.07c-4.686-4.686-12.284-4.686-16.97 0L10.454 247.515c-4.686 4.686-4.686 12.284 0 16.971l211.051 211.05c4.686 4.686 12.284 4.686 16.97-.001z" />
            </svg>
          </button>
        )}
      </>
    );
  }

  function renderNextButton() {
    return (
      <>
        {currentPage < findNumberOfPages() ? (
          <button
            className="page-arrow page-arrow-next "
            type="button"
            onClick={() => setOffset(parseInt(currentPage, 10) + 1)}
          >
            <svg viewBox="0 0 256 512" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" aria-hidden="true" data-icon="chevron-right" data-prefix="fal" id="ember23" className="svg-inline--fa fa-chevron-right fa-w-8 fa-sm ember-view">
              <path fill="currentColor" d="M17.525 36.465l-7.071 7.07c-4.686 4.686-4.686 12.284 0 16.971L205.947 256 10.454 451.494c-4.686 4.686-4.686 12.284 0 16.971l7.071 7.07c4.686 4.686 12.284 4.686 16.97 0l211.051-211.05c4.686-4.686 4.686-12.284 0-16.971L34.495 36.465c-4.686-4.687-12.284-4.687-16.97 0z" />
            </svg>
          </button>
        ) : (
          <button className="page-arrow page-arrow-next disabled" type="button">
            <svg viewBox="0 0 256 512" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" aria-hidden="true" data-icon="chevron-right" data-prefix="fal" id="ember23" className="svg-inline--fa fa-chevron-right fa-w-8 fa-sm ember-view">
              <path fill="currentColor" d="M17.525 36.465l-7.071 7.07c-4.686 4.686-4.686 12.284 0 16.971L205.947 256 10.454 451.494c-4.686 4.686-4.686 12.284 0 16.971l7.071 7.07c4.686 4.686 12.284 4.686 16.97 0l211.051-211.05c4.686-4.686 4.686-12.284 0-16.971L34.495 36.465c-4.686-4.687-12.284-4.687-16.97 0z" />
            </svg>
          </button>
        )}
      </>
    );
  }

  function onClickDetail(item) {
    return function(e) {
      e.preventDefault();
      setItemId(item.id);
      setOutputDetail(true);
      setItemObject(item);
      window.history.pushState({}, '', `${originUrl}${currentPath}?type=${pageType}&page=${currentPage}&id=${item.id}`);
    };
  }

  function loadContent() {
    const startIndex = currentPage === 1 ? 0 : (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentPageObjectItems = pageObjects.slice(startIndex, endIndex);
    return currentPageObjectItems.map(function(item) {
      return (
        <>
          <div className="cell small-12 medium-3">
            <a
              className="outputs-activities-listing show-for-small-only"
              href="#"
              target="_blank"
              rel="noopener noreferrer"
              onClick={onClickDetail(item)}
            >
              <h6>
                { currentPage === 'events' ? item.event_date : item.publishing_date }
                <span>|</span>
                { item.type }
              </h6>
              <h5>
                <span className="underline">{item.title}</span>
              </h5>
            </a>
            <button
              className="outputs-activities-listing show-for-medium"
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setItemId(item.id);
                setOutputDetail(true);
                setItemObject(item);
                window.history.pushState({}, '', `${originUrl}${currentPath}?type=${pageType}&page=${currentPage}&id=${item.id}`);
              }}
            >
              <h6>
                { currentPage === 'events' ? item.event_date : item.publishing_date }
                <span>|</span>
                { item.type }
              </h6>
              <h5>
                <span className="underline">{item.title}</span>
              </h5>
            </button>
          </div>
        </>
      );
    });
  }

  return (itemId
    ? loadItemDetail()
    : (
      <div className="outputs-activities">
        <div className="grid-container">
          <div className="grid-x grid-margin-x">
            <div className="cell">
              <h1>Outputs and Activities</h1>
            </div>
          </div>
          <div className="grid-x grid-margin-x outputs-activities-content">
            <div className="cell">
              <div className="outputs-activities-header clearfix">
                <div className="publications-menu">
                  { pageType === 'publications' ? 'Publications'
                    : (
                      <button
                        className="view-publications-btn"
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          setPageType('publications');
                          setCurrentPage('1');
                          window.history.pushState({}, '', `${originUrl}${currentPath}?type=publications`);
                        }}
                      >
                        Publications
                      </button>
                    )}
                  <span>/</span>
                  { pageType === 'opinions' ? 'Opinions'
                    : (
                      <button
                        className="view-opinions-btn"
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          setPageType('opinions');
                          setCurrentPage('1');
                          window.history.pushState({}, '', `${originUrl}${currentPath}?type=opinions`);
                        }}
                      >
                        Opinions
                      </button>
                    )}
                  <span>/</span>
                  { pageType === 'events' ? 'Events'
                    : (
                      <button
                        className="view-events-btn"
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          setPageType('events');
                          setCurrentPage('1');
                          window.history.pushState({}, '', `${originUrl}${currentPath}?type=events`);
                        }}
                      >
                        Events
                      </button>
                    )}
                </div>
                <div className="outputs-activities-pagination">
                  {renderPrevButton()}
                  {renderPageNumbers()}
                  {renderNextButton()}
                </div>
              </div>
            </div>
          </div>
          <div className="grid-x grid-margin-x outputs-activities-content">
            {loadContent()}
          </div>
          <div className="grid-x outputs-activities-content">
            <div className="cell">
              <p className="page-count">
                Page
                {currentPage}
                of
                {findNumberOfPages()}
              </p>
            </div>
          </div>
        </div>
      </div>
    ));
};

export default OutputsAndActivities;
