import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Switch,
  Route,
  Link,
  useHistory,
  useParams,
  useLocation,
} from 'react-router-dom';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';

const TwentiethPage = ({ slides, pageUrl, initialSlide }) => {
  const history = useHistory();
  const location = useLocation();

  const pageBody = document.getElementsByClassName('twentieth-page')[0];
  const topBar = document.getElementsByClassName('cigi-top-bar')[0];
  const currentSlide = slides.filter((slide) => slide.slug === initialSlide);

  const routes = slides.map((slide) => ({
    slug: `${slide.slug}`,
    slide,
  }));

  if (currentSlide.background_colour === '#FFFFFF') {
    pageBody.classList.add('dark');
  }

  function changeSlide(slideNumber) {
    const slide = slides.filter(
      (slide) => slide.slide_number === slideNumber
    )[0];
    const slug = slide.slug;
    history.push(`${pageUrl}${slug}`);
  }

  function handleRouteChange(previousRoute, nextRoute) {
    // const currentSlide = slides.filter((slide) => slide.slug === slug)[0];
    // if (currentSlide.background_colour === '#FFFFFF') {
    //   pageBody.classList.add('dark');
    // } else {
    //   pageBody.classList.remove('dark');
    // }
  }

  function Slide({ slug }) {
    const currentSlide = slides.filter((slide) => slide.slug === slug)[0];

    return (
      <>
        <TwentiethPageSlide
          slide={currentSlide}
          pageBody={pageBody}
          topBar={topBar}
        />
        <TwentiethPageNavArrows
          changeSlide={changeSlide}
          slide={currentSlide}
        />
      </>
    );
  }

  useEffect(() => {
    const pathArray = location.pathname.split('/').filter(slug => slug);
    const currentSlug = pathArray[pathArray.length - 1];
    const currentSlide = slides.filter(
      (slide) => slide.slug === currentSlug
    )[0];

    if (currentSlide.background_colour === '#FFFFFF') {
      pageBody.classList.add('dark');
    } else {
      pageBody.classList.remove('dark');
    }
  });

  return (
    <div className="slides">
      {routes.map(({ slug }) => (
        <Route
          key={slug}
          exact
          path={`${pageUrl}${slug}`}
          onChange={handleRouteChange}
        >
          {({ match }) => (
            <CSSTransition
              in={match != null}
              timeout={500}
              classNames="fade"
              unmountOnExit
            >
              <Slide slug={slug} />
            </CSSTransition>
          )}
        </Route>
      ))}
    </div>
  );
};

TwentiethPage.propTypes = {};

export default TwentiethPage;
