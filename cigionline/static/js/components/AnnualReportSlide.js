import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import '../../css/components/AnnualReportSlide.scss';
import AnnualReportNav from './AnnualReportNav';
import AnnualReportSlideList from './AnnualReportSlideList';

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
      <div>{slides[currentIndex].id}</div>
      <h1 aria-live="assertive">{slides[currentIndex].slide_title}</h1>
      <div
        dangerouslySetInnerHTML={{ __html: slides[currentIndex].slide_content }}
      />
      <AnnualReportSlideList slides={slides} basePath={basePath} />
      <AnnualReportNav
        basePath={basePath}
        prevSlide={prevSlide}
        nextSlide={nextSlide}
      />
    </div>
  );
};

AnnualReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSlide;
