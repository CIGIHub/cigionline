import PropTypes from 'prop-types';
import React, { useEffect, useState, useRef } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import StrategicPlanTitleSlide from './StrategicPlanTitleSlide';
import StrategicPlanRegularSlide from './StrategicPlanRegularSlide';
import StrategicPlanTOCSlide from './StrategicPlanTOCSlide';
import AnnualReportNav from '../AnnualReportNav';
import AnnualReportHamburgerMenu from '../AnnualReportHamburgerMenu';
import StrategicPlanFrameworkSlide from './StrategicPlanFrameworkSlide';
import StrategicPlanTimelineSlide from './StrategicPlanTimelineSlide';
import StrategicPlanVerticalTitle from './StrategicPlanVerticalTitle';

const slideComponents = {
  title: StrategicPlanTitleSlide,
  regular: StrategicPlanRegularSlide,
  toc: StrategicPlanTOCSlide,
  framework: StrategicPlanFrameworkSlide,
  timeline: StrategicPlanTimelineSlide,
};

const getGradientClass = (alignment) => {
  switch (alignment) {
    case 'left':
      return 'left';
    case 'right':
      return 'right';
    case 'full':
      return 'full';
    case 'none':
    default:
      return 'none';
  }
};

const StrategicReportSlide = ({ slides, basePath }) => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [isScrolling, setIsScrolling] = useState(false);
  const [contentVisible, setContentVisible] = useState(false);

  const currentIndex = slides.findIndex((slide) => slide.slug === slug);
  const gradientClass = getGradientClass(slides[currentIndex].alignment);

  if (currentIndex === -1) {
    return <Navigate to={`/${slides[0].slug}`} replace />;
  }

  const prevSlide = currentIndex > 0 ? slides[currentIndex - 1] : null;
  const nextSlide =
    currentIndex < slides.length - 1 ? slides[currentIndex + 1] : null;

  const canScrollRef = useRef(true);

  useEffect(() => {
    const checkScrollCondition = () => window.innerWidth >= 992;

    canScrollRef.current = checkScrollCondition();

    const handleNavigation = (direction) => {
      if (!canScrollRef.current || isScrolling) return;
      setIsScrolling(true);
      setTimeout(() => setIsScrolling(false), 600);

      if (direction === 'next' && nextSlide) {
        navigate(`${basePath}/${nextSlide.slug}`);
      } else if (direction === 'prev' && prevSlide) {
        navigate(`${basePath}/${prevSlide.slug}`);
      }
    };

    let scrollTimeout = null;

    const handleScroll = (event) => {
      if (!canScrollRef.current || isScrolling) return;
      const SCROLL_THRESHOLD = 75;

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
      <AnnualReportHamburgerMenu slides={slides} basePath={basePath} />
      <AnimatePresence mode="sync">
        <motion.div
          key={`bg-${slug}-${slides[currentIndex].slide_type}`}
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
            className={`background-image ${gradientClass} columns-${slides[currentIndex].slide_content.columns?.length}`}
            style={{
              backgroundImage: `url(${slides[currentIndex].background_image}),url(${slides[currentIndex].background_image_thumbnail})`,
            }}
          />
          <video
            autoPlay
            loop
            muted
            playsInline
            className="background-video"
            src={slides[currentIndex].background_video}
          />
        </motion.div>
      </AnimatePresence>
      <div
        key={`content-${slug}-${slides[currentIndex].slide_type}`}
        className={`slide-wrapper ${slides[currentIndex].background_colour}`}
      >
        <AnnualReportNav
          slides={slides}
          basePath={basePath}
          currentIndex={currentIndex}
        />
        {contentVisible && (
          <div
            key={`content-${slug}-${slides[currentIndex].slide_type}`}
            className="ar-slide-content"
          >
            <div className="container">
              <div className="annual-report-slide">
                {currentSlide.slide_type === 'toc' && (
                  <SlideComponent
                    slides={slides}
                    currentIndex={currentIndex}
                    basePath={basePath}
                  />
                )}
                {['title', 'regular', 'framework', 'timeline'].includes(
                  currentSlide.slide_type,
                ) && <SlideComponent slide={currentSlide} />}
              </div>
            </div>
          </div>
        )}
      </div>
      {['regular', 'framework', 'timeline'].includes(
        currentSlide.slide_type,
      ) && (
        <StrategicPlanVerticalTitle
          currentIndex={currentIndex}
          slide={slides[currentIndex]}
        />
      )}
    </>
  );
};

StrategicReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default StrategicReportSlide;
