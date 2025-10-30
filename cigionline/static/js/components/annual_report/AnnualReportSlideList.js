import PropTypes from 'prop-types';
import React from 'react';
import { Link } from 'react-router-dom';

function AnnualReportSlideList({ slides, basePath }) {
  return (
    <ul id="slide-list">
      {slides.map((slide) => (
        <li key={slide.slug}>
          <Link
            to={`${basePath}/${slide.slug}`}
            aria-label={`Go to ${slide.slide_title}`}
          >
            {slide.slide_title}
          </Link>
        </li>
      ))}
    </ul>
  );
}

AnnualReportSlideList.propTypes = {
  slides: PropTypes.arrayOf(
    PropTypes.shape({
      slug: PropTypes.string,
      slide_title: PropTypes.string,
    }),
  ).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSlideList;
