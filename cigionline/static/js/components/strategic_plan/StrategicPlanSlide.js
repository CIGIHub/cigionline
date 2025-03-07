import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import StrategicPlanTitleSlide from './StrategicPlanTitleSlide';
import StrategicPlanRegularSlide from './StrategicPlanRegularSlide';
import StrategicPlanTOCSlide from './StrategicPlanTOCSlide';

const slideComponents = {
  title: StrategicPlanTitleSlide,
  regular: StrategicPlanRegularSlide,
  toc: StrategicPlanTOCSlide,
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
    const handleNavigation = (direction) => {
      if (isScrolling) return; // Prevent rapid navigation
      setIsScrolling(true);
      setTimeout(() => setIsScrolling(false), 600); // Cooldown

      if (direction === 'next' && nextSlide) {
        navigate(`${basePath}/${nextSlide.slug}`);
      } else if (direction === 'prev' && prevSlide) {
        navigate(`${basePath}/${prevSlide.slug}`);
      }
    };

    const handleScroll = (event) => {
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

    return () => {
      window.removeEventListener('wheel', handleScroll);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentIndex, navigate, isScrolling]);

  useEffect(() => {
    setContentVisible(false);
  }, [slug]);

  const currentSlide = slides[currentIndex];
  const SlideComponent =
    slideComponents[slides[currentIndex].slide_type] ||
    (() => <div>Slide type not found</div>);

  return (
    <div
      key={`content-${slug}-${slides[currentIndex].slide_type}`}
      className={`slide-wrapper ${slides[currentIndex].background_colour}`}
    >
      <AnimatePresence>
        <motion.div
          key={`bg-${slug}-${slides[currentIndex].slide_type}`}
          className={`slide-background ${slides[currentIndex].slide_type}`}
          initial={{ opacity: 0, y: 0 }}
          animate={{ opacity: 1, y: -20 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          onAnimationComplete={() => setContentVisible(true)}
        >
          <div
            className={`background-colour ${slides[currentIndex].background_colour}`}
          />
          <div
            className={`background-image ${gradientClass} columns-${slides[currentIndex].slide_content.columns?.length}`}
            style={{
              backgroundImage: `url(${slides[currentIndex].background_image})`,
            }}
          />
        </motion.div>
        {contentVisible && (
          <motion.div
            key={`content-${slug}-${slides[currentIndex].slide_type}`}
            className="ar-slide-content"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6, ease: 'easeInOut' }}
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
                {currentSlide.slide_type === 'title' && (
                  <SlideComponent slide={currentSlide} />
                )}
                {currentSlide.slide_type === 'regular' && (
                  <SlideComponent slide={currentSlide} />
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

StrategicReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default StrategicReportSlide;
