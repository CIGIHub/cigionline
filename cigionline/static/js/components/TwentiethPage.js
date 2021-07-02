import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Redirect, Route, useHistory, useLocation } from 'react-router-dom';
import { CSSTransition } from 'react-transition-group';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';

const TwentiethPage = ({ slides, pageUrl, initialSlideSlug }) => {
  const history = useHistory();
  const location = useLocation();
  const [allowScroll, setAllowScroll] = useState(true);
  const pathArray = location.pathname.split('/').filter((slug) => slug);
  let currentSlug = pathArray[pathArray.length - 1];
  if (location.pathname === pageUrl) {
    currentSlug = slides[0].slug;
  }
  const currentSlide = slides.filter((slide) => slide.slug === currentSlug)[0];

  const pageBody = document.getElementsByClassName('twentieth-page')[0];
  const topBar = document.getElementsByClassName('cigi-top-bar')[0];
  const initialSlide = slides.filter(
    (slide) => slide.slug === initialSlideSlug
  )[0];

  const routes = slides.map((slide) => ({
    slug: `${slide.slug}`,
    slide,
  }));

  if (initialSlide.background_colour === 'WHITE') {
    pageBody.classList.add('dark');
  }
  if (initialSlide.slide_number !== 1) {
    topBar.classList.add('scrolled-nav');
  }

  function changeSlide(slideNumber) {
    const slide = slides.filter(
      (slide) => slide.slide_number === slideNumber
    )[0];
    const slug = slide.slug;
    history.push(`${pageUrl}${slug}`);
  }

  function handleWheel(e) {
    if (!allowScroll) return;
    setAllowScroll(false);
    setTimeout(function () {
      setAllowScroll(true);
    }, 2000);
    if (e.deltaY > 0 && currentSlide.next_slide) {
      changeSlide(currentSlide.next_slide);
    }
    if (e.deltaY < 0 && currentSlide.prev_slide) {
      changeSlide(currentSlide.prev_slide);
    }
  }

  function Slide({ slug }) {
    const currentSlide = slides.filter((slide) => slide.slug === slug)[0];

    return (
      <>
        <TwentiethPageSlide slide={currentSlide} changeSlide={changeSlide} />
        <TwentiethPageNavArrows
          changeSlide={changeSlide}
          slide={currentSlide}
        />
      </>
    );
  }

  useEffect(() => {
    if (currentSlide.background_colour === 'WHITE') {
      pageBody.classList.add('white-bg');
    } else if (currentSlide.background_colour === 'RED') {
      pageBody.classList.add('red-bg');
    } else {
      pageBody.classList.remove('white-bg', 'red-bg');
    }

    if (currentSlide.slide_number !== 1) {
      topBar.classList.add('scrolled-nav');
    } else topBar.classList.remove('scrolled-nav');
  }, [location]);

  return (
    <div className="slides" onWheel={handleWheel}>
      <Route exact path={`${pageUrl}`}>
        <Redirect to={`${pageUrl}${slides[0].slug}`} />
      </Route>
      {routes.map(({ slug }) => (
        <Route key={slug} exact path={`${pageUrl}${slug}`}>
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
