import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';
import TwentiethPageSlide2Content from './TwentiethPageSlide2Content';

import { Switch, Route, Link, useHistory, useParams } from 'react-router-dom';

const TwentiethPage = ({ slides, initialSlide, pageUrl }) => {
  const slidesCount = slides.length;
  const topBar = document.getElementsByClassName('cigi-top-bar')[0];
  const history = useHistory();

  function changeSlide(slideNumber) {
    const slug = slides.filter((slide) => slide.slide_number === slideNumber)[0].slug;
    history.push(`${pageUrl}${slug}`);
  }

  function Slide() {
    const { slug } = useParams();
    const currentSlide = slides.filter((slide) => slide.slug === slug)[0];
    return (
      <>
        <TwentiethPageSlide slide={currentSlide} />
        <TwentiethPageNavArrows
          changeSlide={changeSlide}
          slide={currentSlide}
        />
      </>
    );
  }

  useEffect(() => {
    // if (!topBar.classList.contains('scrolled-nav')) {
    //   if (currentSlideIndex > 0) {
    //     topBar.classList.add('scrolled-nav');
    //   }
    // } else if (currentSlideIndex === 0) {
    //   topBar.classList.remove('scrolled-nav');
    // }

    return history.listen((location) => {
      if (history.action === 'PUSH' || history.action === 'POP') {
        const slug = location.pathname;
        console.log(`current location: ${location}`);
      }
    });
  });

  return (
    <>
      <div className="slides">
        <Switch>
          <Route path={`${pageUrl}:slug`}>
            <Slide />
          </Route>
        </Switch>
        <div className="d-flex">
          <Link className="nav" to="/about/twentieth-page-3/slide-1">
            slide1
          </Link>
          <Link className="nav" to="/about/twentieth-page-3/slide-2">
            slide2
          </Link>
          <Link className="nav" to="/about/twentieth-page-3/slide-3">
            slide3
          </Link>
        </div>
      </div>
    </>
  );
};

TwentiethPage.propTypes = {};

export default TwentiethPage;
