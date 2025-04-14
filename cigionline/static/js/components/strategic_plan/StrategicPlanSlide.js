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
import usePreloadSlideAssets from './usePreloadSlideAssets';

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

const getRandomIndex = (arrayLength, excludeIndex) => {
  if (arrayLength <= 1) return 0;

  let newIndex = excludeIndex;
  while (newIndex === excludeIndex) {
    newIndex = Math.floor(Math.random() * arrayLength);
  }
  return newIndex;
};

const StrategicReportSlide = ({ slides, basePath }) => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [isScrolling, setIsScrolling] = useState(false);
  const [contentVisible, setContentVisible] = useState(false);
  const [imageIndex, setImageIndex] = useState(0);

  const currentIndex = slides.findIndex((slide) => slide.slug === slug);
  const gradientClass = getGradientClass(slides[currentIndex].alignment);
  const timerRef = useRef(null);

  usePreloadSlideAssets(slides);

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

  useEffect(() => {
    const images = slides[currentIndex]?.background_images;
    if (!images || images.length <= 1) return;

    const firstIndex = getRandomIndex(images.length, -1);
    setImageIndex(firstIndex);

    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setImageIndex((prev) => getRandomIndex(images.length, prev));
    }, 4000);

    () => clearInterval(timerRef.current);
  }, [currentIndex]);

  const currentSlide = slides[currentIndex];
  const SlideComponent =
    slideComponents[slides[currentIndex].slide_type] ||
    (() => <div>Slide type not found</div>);

  useEffect(() => {
    slides.forEach((slide) => {
      const images = slide.background_images || [slide.background_image];
      images.forEach((src) => {
        const img = new Image();
        img.src = src;
      });
    });
  }, [slides]);

  const videoRef = useRef();

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const newSrc = slides[currentIndex]?.background_video;
    if (!newSrc || video.dataset.src === newSrc) return;

    video.pause();
    video.removeAttribute('src');
    video.load();

    video.src = newSrc;
    video.dataset.src = newSrc;

    video.load();
    setTimeout(() => {
      video.play().catch(() => {});
    }, 100);
  }, [currentIndex]);

  return (
    <>
      <AnnualReportHamburgerMenu slides={slides} basePath={basePath} />
      <AnimatePresence mode="sync">
        <motion.div
          key={`bg-${slug}-${slides[currentIndex].slide_type}`}
          className={`slide-background ${gradientClass} ${slides[currentIndex].slide_type}`}
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
          {slides[currentIndex].background_images && (
            <>
              {slides[currentIndex].background_images.map((image, index) => (
                <motion.div
                  key={`bg-image-${index}`}
                  className={`background-image background-images-${index}`}
                  style={{
                    backgroundImage: `url(${image})`,
                  }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: imageIndex === index ? 1 : 0 }}
                  transition={{ duration: 2 }}
                />
              ))}
            </>
          )}
          <video
            ref={videoRef}
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            className={`background-video ${gradientClass}`}
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
