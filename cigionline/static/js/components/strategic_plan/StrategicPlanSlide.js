import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import StrategicPlanTitleSlide from './StrategicPlanTitleSlide';
import StrategicPlanRegularSlide from './StrategicPlanRegularSlide';
import StrategicPlanTOCSlide from './StrategicPlanTOCSlide';
import AnnualReportNav from '../AnnualReportNav';
import AnnualReportHamburgerMenu from '../AnnualReportHamburgerMenu';
import StrategicPlanFrameworkSlide from './StrategicPlanFrameworkSlide';
import StrategicPlanTimelineSlide from './StrategicPlanTimelineSlide';

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

  useEffect(() => {
    const MIN_SCREEN_WIDTH = 1024;

    const checkScrollCondition = () => {
      const contentHeight =
        document.querySelector('.slide-wrapper')?.scrollHeight || 0;
      const viewportHeight = window.innerHeight;
      const isLargeScreen = window.innerWidth >= MIN_SCREEN_WIDTH;

      return isLargeScreen && contentHeight <= viewportHeight;
    };

    let canScroll = checkScrollCondition();

    const handleNavigation = (direction) => {
      if (!canScroll || isScrolling) return;
      setIsScrolling(true);
      setTimeout(() => setIsScrolling(false), 600);

      if (direction === 'next' && nextSlide) {
        navigate(`${basePath}/${nextSlide.slug}`);
      } else if (direction === 'prev' && prevSlide) {
        navigate(`${basePath}/${prevSlide.slug}`);
      }
    };

    const handleScroll = (event) => {
      if (!canScroll) return;
      if (event.deltaY > 0) {
        handleNavigation('next');
      } else if (event.deltaY < 0) {
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

    window.addEventListener('wheel', handleScroll);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener(
      'resize',
      () => (canScroll = checkScrollCondition()),
    );

    return () => {
      window.removeEventListener('wheel', handleScroll);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener(
        'resize',
        () => (canScroll = checkScrollCondition()),
      );
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
    </>
  );
};

StrategicReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default StrategicReportSlide;
