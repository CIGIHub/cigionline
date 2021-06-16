import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import TwentiethPageSlide from './TwentiethPageSlide';
import TwentiethPageNavArrows from './TwentiethPageNavArrows';
import TwentiethPageSlide2Content from './TwentiethPageSlide2Content';

import { Switch, Route, Link, useHistory } from 'react-router-dom';

const TwentiethPage = (props) => {
  const { slides, initialSlide } = props;
  const slidesCount = slides.length;
  const [currentSlideIndex, setCurrentSlideIndex] = useState(initialSlide);
  const topBar = document.getElementsByClassName('cigi-top-bar')[0];
  const history = useHistory();

  function changeSlide() {
    history.push(`/about/twentieth-page-3/${slides[currentSlideIndex].slug}`);
  }

  useEffect(() => {
    if (!topBar.classList.contains('scrolled-nav')) {
      if (currentSlideIndex > 0) {
        topBar.classList.add('scrolled-nav');
      }
    } else if (currentSlideIndex === 0) {
      topBar.classList.remove('scrolled-nav');
    }

    changeSlide();

    return history.listen((location) => {
      if (history.action === 'PUSH' || history.action === 'POP') {
        const slug = location.pathname;
        console.log(location);
      }
    });
  });

  return (
    <>
      <div className="slides">
        <Switch>
          <Route path="/about/twentieth-page-3/slide-1">
            <div className={`slide-${slides[0].slide}`}>
              <div
                className="background-image"
                style={
                  slides[0].background
                    ? {
                        backgroundImage: `url(${slides[0].background})`,
                      }
                    : {}
                }
              >
                <TwentiethPageSlide2Content
                  title={slides[0].title}
                  body={slides[0].body}
                />
              </div>
            </div>
          </Route>
          <Route path="/about/twentieth-page-3/slide-2">
            <div className={`slide-${slides[1].slide}`}>
              <div
                className="background-image"
                style={
                  slides[1].background
                    ? {
                        backgroundImage: `url(${slides[1].background})`,
                      }
                    : {}
                }
              >
                <TwentiethPageSlide2Content
                  title={slides[1].title}
                  body={slides[1].body}
                />
              </div>
            </div>
          </Route>
          <Route path="/about/twentieth-page-3/slide-3">
            <div className={`slide-${slides[2].slide}`}>
              <div
                className="background-image"
                style={
                  slides[2].background
                    ? {
                        backgroundImage: `url(${slides[2].background})`,
                      }
                    : {}
                }
              >
                <TwentiethPageSlide2Content
                  title={slides[2].title}
                  body={slides[2].body}
                />
              </div>
            </div>
          </Route>
          <Route path="/">
            <TwentiethPageSlide2Content
              title={slides[0].title}
              body={slides[0].body}
            />
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
      <TwentiethPageNavArrows
        currentSlideIndex={currentSlideIndex}
        changeSlide={changeSlide}
        slidesCount={slidesCount}
        setCurrentSlideIndex={setCurrentSlideIndex}
      />
    </>
  );
};

TwentiethPage.propTypes = {};

export default TwentiethPage;
