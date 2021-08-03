/* eslint-disable react/no-danger */
import React, { Fragment, useState } from 'react';
import queryString from 'query-string';
import {
  getLanguage,
  getSiteUrl,
} from './AnnualReportUtils';

const TableOfContents = ({
  slide, slides, isOpen, contentOpacity, navigateToSlide,
}) => {
  const originUrl = window.location.origin;
  const currentPath = window.location.pathname;
  const params = queryString.parse(window.location.search);
  const isAcknowledgementsval = !!(params.acknowledgements === 'true' || params.remerciements === 'true');
  const [isAcknowledgements, setIsAcknowledgements] = useState(isAcknowledgementsval);
  const language = getLanguage();
  const siteUrl = getSiteUrl();

  function loadAcknowledgements() {
    return slide.value.acknowledgement.groups.map(function(group) {
      return (
        <Fragment key={group.id}>
          <div className="grid-x credits-content">
            <div className="cell full">
              <h4 className="credits-title">{group.value.title}</h4>
            </div>
          </div>
          <div className="grid-x credits-content">
            {group.value.people.map(function(person) {
              return (
                <div key={person.id} className="cell medium-3 small-4 credits-block">
                  <h5>{person.value.title}</h5>
                  <h6>{person.value.position}</h6>
                  <div />
                </div>
              );
            })}
          </div>
          <div className="grid-x credits-content credits-border">
            {group.value.people.map(function(person) {
              return (
                <div key={person.id} className="cell small-4 credits-block show-for-small-only">
                  <h5>{person.value.title}</h5>
                  <h6>{person.value.position}</h6>
                  <div />
                </div>
              );
            })}
          </div>
        </Fragment>
      );
    });
  }

  function firstHalfSlides() {
    const slidesExceptTOC = slides.filter(function(iterslide) {
      return iterslide.value.slug !== slide.value.slug;
    });
    const firstHalf = (slidesExceptTOC.length - 1) % 2 === 0
      ? slidesExceptTOC.length / 2
      : slidesExceptTOC.length / 2 + 1;
    return slidesExceptTOC.map(function(slideIter, index) {
      const hrefUrl = `${siteUrl}/${language}/${slideIter.value.slug}/`;
      return index < firstHalf ? (
        <div key={slideIter.id} className="grid-x slide-link">
          <div className="cell small-1 medium-1">
            <p className="slide-number ">{index + 1}</p>
          </div>
          <div className="cell small-11 medium-11">
            <a
              href={hrefUrl}
              onClick={(e) => { e.preventDefault(); navigateToSlide(index + 1); }}
            >
              {slideIter.value.title}
            </a>
          </div>
        </div>
      ) : (
        ''
      );
    });
  }

  const secondHalfSlides = () => {
    const slidesExceptTOC = slides.filter(function(iterslide) {
      return iterslide.value.slug !== slide.value.slug;
    });
    const firstHalf = (slidesExceptTOC.length - 1) % 2 === 0
      ? slidesExceptTOC.length / 2
      : slidesExceptTOC.length / 2 + 1;
    return slidesExceptTOC.map(function(slideIter, index) {
      const hrefUrl = `${siteUrl}/${language}/${slideIter.value.slug}/`;
      return index > firstHalf ? (
        <div key={slideIter.id} className="grid-x slide-link">
          <div className="cell small-1 medium-1">
            <p className="slide-number ">{index + 1}</p>
          </div>
          <div className="cell small-11 medium-11">
            <a
              href={hrefUrl}
              onClick={(e) => { e.preventDefault(); navigateToSlide(index + 1); }}
            >
              {slideIter.value.title}
            </a>
          </div>
        </div>
      ) : (
        ''
      );
    });
  };

  return (
    <div
      className="table-of-contents"
      style={{ opacity: contentOpacity ? 1 : 0 }}
    >
      <div className="grid-container">
        <div
          className="grid-x grid-margin-x hover-reveal-hide"
          style={{ opacity: 1 }}
        >
          <div className="cell">
            <h1>
              {window.annualReport.value[language].title}
            </h1>
          </div>
        </div>
        <div
          className="grid-x grid-margin-x hover-reveal-hide"
          style={{ opacity: 1 }}
        >
          <div className="cell">
            <div className="toc-content">
              {isAcknowledgements ? (
                <div className="toc-menu">
                  <a
                    className="hide-acknowledgements-btn"
                    type="button"
                    href={originUrl + currentPath}
                    onClick={(e) => {
                      e.preventDefault();
                      setIsAcknowledgements(!isAcknowledgements);
                      if (!isOpen) {
                        window.history.pushState({}, '', `${originUrl}${currentPath}`);
                      }
                    }}
                  >
                    {slide.value.title}
                  </a>
                  <span>/</span>
                  {language === 'en' ? 'Acknowledgements' : 'Remerciements'}
                </div>
              ) : (
                <div className="toc-menu">
                  {slide.value.title}
                  <span>/</span>
                  {language === 'en' ? (
                    <a
                      className="show-acknowledgements-btn"
                      type="button"
                      href="?acknowledgements=true"
                      onClick={(e) => {
                        e.preventDefault();
                        setIsAcknowledgements(!isAcknowledgements);
                        if (!isOpen) {
                          window.history.pushState({}, '', `${originUrl}${currentPath}?acknowledgements=true`);
                        }
                      }}
                    >
                      Acknowledgements
                    </a>
                  ) : (
                    <a
                      className="show-acknowledgements-btn"
                      type="button"
                      href="?remerciements=true"
                      onClick={(e) => {
                        e.preventDefault();
                        setIsAcknowledgements(!isAcknowledgements);
                        if (!isOpen) {
                          window.history.pushState({}, '', `${originUrl}${currentPath}?remerciements=true`);
                        }
                      }}
                    >
                      Remerciements
                    </a>
                  )}
                </div>
              )}
              {isAcknowledgements ? (
                <>
                  <div className="grid-x credits-content credits-border">
                    <div className="cell full">
                      <p
                        className="credits-message"
                        dangerouslySetInnerHTML={{
                          __html: slide.value.acknowledgement.message[0].value,
                        }}
                      />
                    </div>
                  </div>
                  {loadAcknowledgements()}
                </>
              ) : (
                <div className="grid-x slide-content">
                  <div className="cell medium-5">{firstHalfSlides()}</div>
                  <div className="cell medium-2" />
                  <div className="cell medium-5">{secondHalfSlides()}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TableOfContents;
