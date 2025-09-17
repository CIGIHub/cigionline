import PropTypes from 'prop-types';
import React, { useEffect, useState, useRef } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import AnnualReportRegularSlide from './AnnualReportRegularSlide';
import AnnualReportTOCSlide from './AnnualReportTOCSlide';
import AnnualReportTextSlide from './AnnualReportTextSlide';
import AnnualReportQuoteSlide from './AnnualReportQuoteSlide';
import AnnualReportTitleSlide from './AnnualReportTitleSlide';
import AnnualReportNav from './AnnualReportNav';
import AnnualReportHeader from './AnnualReportHeader';
import AnnualReportVerticalTitle from './AnnualReportVerticalTitle';
import '../../../css/components/annual_reports/AnnualReportSlide.scss';

const slideComponents = {
  title: AnnualReportTitleSlide,
  toc: AnnualReportTOCSlide,
  regular: AnnualReportRegularSlide,
  text: AnnualReportTextSlide,
  quote: AnnualReportQuoteSlide,
};

const loadedImages = new Set();

const preloadImage = (src) => {
  if (!src || loadedImages.has(src)) return;

  const img = new Image();
  img.onload = () => loadedImages.add(src);
  img.onerror = () => {};
  img.src = src;
};

function AnnualReportSlide({ slides, basePath }) {
  const { slug, lang } = useParams();
  const currentLang = lang === 'fr' ? 'fr' : 'en';
  const navigate = useNavigate();
  const [isScrolling, setIsScrolling] = useState(false);
  const [contentVisible, setContentVisible] = useState(false);

  const currentIndex = slides.findIndex((slide) => slide.slug === slug);

  if (currentIndex === -1) {
    return (
      <Navigate
        to={`${basePath}/${slides[0].slug}${currentLang === 'fr' ? '/fr' : ''}`}
        replace
      />
    );
  }

  const prevSlide = currentIndex > 0 ? slides[currentIndex - 1] : null;
  const nextSlide =
    currentIndex < slides.length - 1 ? slides[currentIndex + 1] : null;

  const canScrollRef = useRef(true);

  const checkScrollCondition = () => {
    if (typeof document === 'undefined') return false;

    const wrapper = document.querySelector('.slide-wrapper');
    if (!wrapper) return false;

    const isLargeScreen = window.innerWidth >= 992;
    const contentOverflows = wrapper.scrollHeight > window.innerHeight;

    return isLargeScreen && !contentOverflows;
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
      setTimeout(() => setIsScrolling(false), 600);

      if (direction === 'next' && nextSlide) {
        navigate(
          `${basePath}/${nextSlide.slug}${currentLang === 'fr' ? '/fr' : ''}`,
        );
      } else if (direction === 'prev' && prevSlide) {
        navigate(
          `${basePath}/${prevSlide.slug}${currentLang === 'fr' ? '/fr' : ''}`,
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
      }, 700);

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
    setContentVisible(false);
  }, [slug]);

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
      />
      <div
        className={`persistent-video-layer ${slides[currentIndex].slide_type} ${
          [0, 2, 3, 9].includes(Number(currentIndex)) ? 'visible' : ''
        } ${currentIndex}`}
      >
        {slides.map((slide, index) => (
          <React.Fragment key={`bg-${slide.slug}`}>
            {slide.background_video ? (
              <video
                src={slide.background_video}
                autoPlay
                loop
                muted
                playsInline
                preload="auto"
                className={`background-video ${
                  index === currentIndex ? 'visible' : ''
                } bg-${index}`}
              />
            ) : null}
          </React.Fragment>
        ))}
      </div>
      <AnimatePresence mode="sync">
        <motion.div
          key={currentSlide.id || currentSlide.slug}
          className={`slide-background ${slides[currentIndex].slide_type}`}
          initial={{ opacity: 0.1, y: 0 }}
          animate={{ opacity: 1, y: -20 }}
          exit={{ opacity: 0, y: -20, transition: { delay: 1 } }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          onAnimationComplete={() => setContentVisible(true)}
        >
          <div
            className={`background-colour ${slides[currentIndex].background_colour}`}
          />
          <div
            className="background-image"
            style={{
              backgroundImage: `url(${slides[currentIndex].background_image}),url(${slides[currentIndex].background_image_thumbnail})`,
            }}
          />
        </motion.div>
      </AnimatePresence>
      <div
        key={`content-${slug}-${slides[currentIndex].slide_type}`}
        className={`slide-wrapper ${slides[currentIndex].slide_type} ${slides[currentIndex].background_colour}`}
      >
        <AnnualReportNav
          slides={slides}
          basePath={basePath}
          currentIndex={currentIndex}
        />
        {contentVisible && (
          <>
            {currentSlide.slide_type === 'toc' && (
              <SlideComponent
                slides={slides}
                currentIndex={currentIndex}
                basePath={basePath}
                lang={currentLang}
              />
            )}
            {['title', 'regular', 'framework', 'timeline'].includes(
              currentSlide.slide_type,
            ) && <SlideComponent slide={currentSlide} lang={currentLang} />}
          </>
        )}
      </div>
      <AnnualReportVerticalTitle
        currentIndex={currentIndex}
        slide={slides[currentIndex]}
        lang={currentLang}
      />
    </>
  );
}

AnnualReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSlide;
