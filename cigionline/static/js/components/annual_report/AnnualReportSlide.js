import PropTypes from 'prop-types';
import React, { useEffect, useState, useRef, useMemo } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import AnnualReportRegularSlide from './AnnualReportRegularSlide';
import AnnualReportTOCSlide from './AnnualReportTOCSlide';
import AnnualReportTitleSlide from './AnnualReportTitleSlide';
import AnnualReportNav from './AnnualReportNav';
import AnnualReportHeader from './AnnualReportHeader';
import AnnualReportVerticalTitle from './AnnualReportVerticalTitle';
import AnnualReportFooter from './AnnualReportFooter';
import '../../../css/components/annual_reports/AnnualReportSlide.scss';
import AnnualReportTimelineSlide from './AnnualReportTimelineSlide';
import AnnualReportsFinancialsSlide from './AnnualReportFinancialsSlide';
import AnnualReportOutputsSlide from './AnnualReportOutputsSlide';
import AnnualReportTOC from './AnnualReportTOC';

const slideComponents = {
  title: AnnualReportTitleSlide,
  toc: AnnualReportTOCSlide,
  standard: AnnualReportRegularSlide,
  chairs_message: AnnualReportRegularSlide,
  presidents_message: AnnualReportRegularSlide,
  timeline: AnnualReportTimelineSlide,
  financials: AnnualReportsFinancialsSlide,
  outputs_and_activities: AnnualReportOutputsSlide,
};

const backgroundStyles = {
  chairs_message: { backgroundColor: 'white' },
  presidents_message: { backgroundColor: 'white' },
  outputs_and_activities: { backgroundColor: 'white' },
  financials: { backgroundColor: 'white' },
};

const loadedImages = new Set();

const preloadImage = (src) => {
  if (!src || loadedImages.has(src)) return;

  const img = new Image();
  img.onload = () => loadedImages.add(src);
  img.onerror = () => {};
  img.src = src;
};

const shareRoute = 'cigionline.org';

function AnnualReportSlide({ slides, basePath }) {
  const [showTOC, setShowTOC] = useState(false);
  const { slug, lang } = useParams();
  const currentLang = lang === 'fr' ? 'fr' : 'en';
  const navigate = useNavigate();
  const [isScrolling, setIsScrolling] = useState(false);
  const [dimUI, setDimUI] = useState(false);
  const [hoverNav, setHoverNav] = useState(false);
  const defaultImage = slides[1]?.background_image || '';
  const defaultImageThumbnail = slides[1]?.background_image_thumbnail || '';
  const [lightHeader, setLightHeader] = useState(false);

  const currentIndex = slides.findIndex((slide) => slide.slug === slug);

  if (currentIndex === -1) {
    return (
      <Navigate
        to={`${basePath}${currentLang === 'fr' ? '/fr' : '/en'}/${
          slides[0].slug
        }`}
        replace
      />
    );
  }

  const fadeableClass = useMemo(
    () => `hover-reveal-hide${dimUI ? ' is-dimmed' : ''}`,
    [dimUI],
  );

  const revealableClass = useMemo(
    () => `hover-reveal${dimUI ? ' is-revealed' : ''}`,
    [dimUI],
  );

  const lightHeaderClass = useMemo(
    () => (lightHeader ? ' light-header' : ''),
    [lightHeader],
  );

  const prevSlide = currentIndex > 0 ? slides[currentIndex - 1] : null;
  const nextSlide =
    currentIndex < slides.length - 1 ? slides[currentIndex + 1] : null;

  const canScrollRef = useRef(true);

  const checkScrollCondition = () => {
    if (typeof document === 'undefined') return false;
    const isLargeScreen = window.innerWidth >= 992;
    return isLargeScreen;
  };

  useEffect(() => {
    if (nextSlide?.background_image) {
      preloadImage(nextSlide.background_image);
    }
  }, [currentIndex, nextSlide]);

  useEffect(() => {
    if (prevSlide?.background_image) {
      preloadImage(prevSlide.background_image);
    }
  }, [currentIndex, prevSlide]);

  useEffect(() => {
    canScrollRef.current = checkScrollCondition();

    const handleNavigation = (direction) => {
      if (!canScrollRef.current || isScrolling) return;
      setIsScrolling(true);
      setTimeout(() => setIsScrolling(false), 2000);

      if (direction === 'next' && nextSlide) {
        navigate(
          `${basePath}/${currentLang === 'fr' ? 'fr' : 'en'}/${nextSlide.slug}`,
        );
      } else if (direction === 'prev' && prevSlide) {
        navigate(
          `${basePath}/${currentLang === 'fr' ? 'fr' : 'en'}/${prevSlide.slug}`,
        );
      }
    };

    let scrollTimeout = null;

    const handleScroll = (event) => {
      if (!canScrollRef.current || isScrolling) return;
      const SCROLL_THRESHOLD = 60;

      if (Math.abs(event.deltaY) < SCROLL_THRESHOLD) return;

      if (scrollTimeout) return;

      scrollTimeout = setTimeout(() => {
        scrollTimeout = null;
      }, 2000);

      if (event.deltaY > 0) {
        handleNavigation('next');
      } else {
        handleNavigation('prev');
      }
    };

    const handleKeyDown = (event) => {
      if (['ArrowDown', 'PageDown'].includes(event.key)) {
        handleNavigation('next');
      } else if (['ArrowUp', 'PageUp'].includes(event.key)) {
        handleNavigation('prev');
      }
    };

    const handleResize = () => {
      canScrollRef.current = checkScrollCondition();
    };

    window.addEventListener('wheel', handleScroll);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('wheel', handleScroll);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('resize', handleResize);
    };
  }, [currentIndex, navigate, isScrolling, slides]);

  useEffect(() => {
    setHoverNav(false);
    setLightHeader(false);
  }, [currentIndex]);

  const currentSlide = slides[currentIndex];
  const SlideComponent =
    slideComponents[slides[currentIndex].slide_type] ||
    (() => <div>Slide type not found</div>);

  return (
    <>
      <AnnualReportHeader
        slides={slides}
        basePath={basePath}
        currentLang={currentLang}
        currentSlug={slug}
        currentIndex={currentIndex}
        fadeableClass={fadeableClass}
        showTOC={showTOC}
        setShowTOC={setShowTOC}
        lightHeaderClass={lightHeaderClass}
      />
      <div
        key={currentSlide.id || currentSlide.slug}
        className={`slide-background background-row d-lg-none background-${
          currentSlide.background_colour || 'black'
        }`}
      >
        <div
          className="background-image"
          style={
            backgroundStyles[currentSlide.slide_type] || {
              backgroundImage: `url(${slides[currentIndex].background_image}),url(${slides[currentIndex].background_image_thumbnail})`,
            }
          }
        />
        {currentSlide.slide_type === 'standard' && (
          <div className="background-overlay hover-reveal-hide" />
        )}
      </div>
      <AnnualReportNav
        slides={slides}
        basePath={basePath}
        currentIndex={currentIndex}
        fadeableClass={fadeableClass}
        lang={currentLang}
        setHoverNav={setHoverNav}
        lightHeaderClass={lightHeaderClass}
      />

      {currentSlide.slide_type === 'toc' ? (
        <SlideComponent
          className={fadeableClass}
          slides={slides}
          currentIndex={currentIndex}
          basePath={basePath}
          lang={currentLang}
          fadeableClass={fadeableClass}
          revealableClass={revealableClass}
          dimUI={dimUI}
        />
      ) : (
        <SlideComponent
          className={fadeableClass}
          slide={currentSlide}
          basePath={basePath}
          lang={currentLang}
          fadeableClass={fadeableClass}
          revealableClass={revealableClass}
          setDimUI={setDimUI}
          dimUI={dimUI}
          defaultImage={defaultImage}
          defaultImageThumbnail={defaultImageThumbnail}
          setLightHeader={setLightHeader}
        />
      )}

      <div className={`lightbox ${showTOC ? 'is-visible' : ''}`}>
        {showTOC && (
          <AnnualReportTOC
            slides={slides}
            currentIndex={currentIndex}
            basePath={basePath}
            lang={currentLang}
            fadeableClass={fadeableClass}
            setShowTOC={setShowTOC}
          />
        )}
      </div>

      <AnnualReportFooter
        slide={currentSlide}
        shareRoute={shareRoute}
        onHoverChange={setDimUI}
        dimUI={dimUI}
      />
      <div className={fadeableClass}>
        <AnnualReportVerticalTitle
          currentIndex={currentIndex}
          slide={slides[currentIndex]}
          lang={currentLang}
        />
      </div>
      <motion.div
        className="overlay"
        initial={false}
        animate={hoverNav ? 'open' : 'closed'}
        variants={{
          open: {
            opacity: 1,
            zIndex: 3,
            pointerEvents: 'auto',
            transition: { duration: 0.25, ease: 'easeOut' },
          },
          closed: {
            opacity: 0,
            pointerEvents: 'none',
            transition: { duration: 0.25, ease: 'easeIn' },
            transitionEnd: { zIndex: -1 },
          },
        }}
      />
    </>
  );
}

AnnualReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSlide;
