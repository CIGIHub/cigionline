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

const TwentiethPage = ({ slides, pageUrl }) => {
  const history = useHistory();
  const pageBody = document.getElementsByClassName('twentieth-page')[0];
  const topBar = document.getElementsByClassName('cigi-top-bar')[0];

  function changeSlide(slideNumber) {
    const slide = slides.filter(
      (slide) => slide.slide_number === slideNumber
    )[0];
    const slug = slide.slug;
    history.push(`${pageUrl}${slug}`);
  }

  function Slide() {
    const { slug } = useParams();
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

  useEffect(() => {});

  return (
    <>
      <Route
        render={({ location }) => (
          <TransitionGroup className="slides">
            <CSSTransition key={location.key} timeout={300} classNames="fade">
              <Switch location={location}>
                <Route path={`${pageUrl}:slug`}>
                  <Slide />
                </Route>
              </Switch>
            </CSSTransition>
          </TransitionGroup>
        )}
      />
    </>
  );
};

TwentiethPage.propTypes = {};

export default TwentiethPage;
