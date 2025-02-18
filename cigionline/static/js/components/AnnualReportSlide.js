import PropTypes from 'prop-types';
import React from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import '../../css/components/AnnualReportSlide.scss';

const AnnualReportSlide = ({ slides, basePath }) => {
  const { slug } = useParams();
  const navigate = useNavigate();

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

  return (
    <div className="annual-report-slide">
      <div>{slides[currentIndex].id}</div>
      <h1>{slides[currentIndex].slide_title}</h1>
      <div
        dangerouslySetInnerHTML={{ __html: slides[currentIndex].slide_content }}
      />

      <div>
        <button
          type="button"
          onClick={() => navigate(`${basePath}/${prevSlide.slug}`)}
          disabled={!prevSlide}
        >
          Previous
        </button>

        <button
          type="button"
          onClick={() => navigate(`${basePath}/${nextSlide.slug}`)}
          disabled={!nextSlide}
        >
          Next
        </button>
      </div>
    </div>
  );
};

AnnualReportSlide.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSlide;
