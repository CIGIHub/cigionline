import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import '../../css/components/AnnualReportSlide.scss';
import AnnualReportRegularSlide from './AnnualReportRegularSlide';
import AnnualReportTOCSlide from './AnnualReportTOCSlide';

const AnnualReportSlide = ({ slides, basePath }) => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [isScrolling, setIsScrolling] = useState(false); // Cooldown state

  if (!slides || slides.length === 0) {
    return <div>Loading slides...</div>;
  }

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
      setTimeout(() => setIsScrolling(false), 1000); // Cooldown

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

  return (
    <div className="annual-report-slide">
      <div
        className="ar-slide-background-image"
        style={{
          backgroundImage: `url(${slides[currentIndex].background_image})`,
        }}
      />
      <div
        className={`ar-slide-background-colour ${slides[currentIndex].background_colour}`}
      />

      <div className="ar-slide-content">
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
      </div>
    </div>
  );
};

AnnualReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSlide;
