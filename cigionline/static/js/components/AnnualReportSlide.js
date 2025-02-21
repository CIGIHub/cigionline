import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import '../../css/components/AnnualReportSlide.scss';
import AnnualReportRegularSlide from './AnnualReportRegularSlide';
import AnnualReportTOCSlide from './AnnualReportTOCSlide';

const AnnualReportSlide = ({ slides, basePath }) => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [isScrolling, setIsScrolling] = useState(false);
  const [contentVisible, setContentVisible] = useState(false);

  const currentIndex = slides.findIndex((slide) => slide.slug === slug);

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

  return (
    <div className="slide-wrapper">
      <AnimatePresence>
        <div className="annual-report-slide">
          <motion.div
            key={`bg-${slug}`}
            className={`slide-background ${slides[currentIndex].background_colour}`}
            style={{
              backgroundImage: `url(${slides[currentIndex].background_image})`,
            }}
            initial={{ opacity: 0, y: 0 }}
            animate={{ opacity: 1, y: -20 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6, ease: 'easeInOut' }}
            onAnimationComplete={() => setContentVisible(true)}
          />
          {contentVisible && (
            <motion.div
              key={`content-${slug}`}
              className="ar-slide-content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.6, ease: 'easeInOut' }}
            >
              <div className="container">
                <div className="row justify-content-center">
                  <div className="col-md-10 col-lg-8">
                    <div className="annual-report-slide">
                      {slides[currentIndex].slide_type === 'toc' ? (
                        <AnnualReportTOCSlide
                          slides={slides}
                          basePath={basePath}
                          currentIndex={currentIndex}
                        />
                      ) : (
                        <AnnualReportRegularSlide
                          slides={slides}
                          basePath={basePath}
                          currentIndex={currentIndex}
                          prevSlide={prevSlide}
                          nextSlide={nextSlide}
                        />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </AnimatePresence>
    </div>
  );
};

AnnualReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  isLoading: PropTypes.bool.isRequired,
};

export default AnnualReportSlide;
