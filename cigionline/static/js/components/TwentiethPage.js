/* eslint-disable react/prop-types */
import React, { useState, useEffect } from 'react';
import {
  Route,
  useNavigate,
  useLocation,
  Navigate,
} from 'react-router-dom';
import { CSSTransition } from 'react-transition-group';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';

function Slide({ slug, slides, changeSlide }) {
  const routeSlide = slides.filter((slide) => slide.slug === slug)[0];

  return (
    <>
      <TwentiethPageSlide slide={routeSlide} changeSlide={changeSlide} />
      <TwentiethPageNavArrows
        changeSlide={changeSlide}
        slide={routeSlide}
      />
    </>
  );
}

function TwentiethPage({ slides, pageUrl, initialSlideSlug }) {
  const navigate = useNavigate();
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
    (slide) => slide.slug === initialSlideSlug,
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

  const changeSlide = React.useCallback((slideNumber) => {
    const slide = slides.filter(
      (element) => element.slide_number === slideNumber,
    )[0];
    const slug = slide.slug;
    navigate(`${pageUrl}${slug}`);
  }, [slides, navigate, pageUrl]);

  function handleWheel(e) {
    if (!allowScroll) return;
    setAllowScroll(false);
    setTimeout(function() {
      setAllowScroll(true);
    }, 2000);
    if (e.deltaY > 0 && currentSlide.next_slide) {
      changeSlide(currentSlide.next_slide);
    }
    if (e.deltaY < 0 && currentSlide.prev_slide) {
      changeSlide(currentSlide.prev_slide);
    }
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
        <Navigate to={`${pageUrl}${slides[0].slug}`} />
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
              <Slide slug={slug} slides={slides} changeSlide={changeSlide} />
            </CSSTransition>
          )}
        </Route>
      ))}
    </div>
  );
}

export default TwentiethPage;
