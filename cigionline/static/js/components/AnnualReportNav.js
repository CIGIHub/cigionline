import PropTypes from 'prop-types';
import React from 'react';
import { useNavigate } from 'react-router-dom';

const AnnualReportNav = ({ basePath, prevSlide, nextSlide }) => {
  const navigate = useNavigate();

  return (
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
  );
};

AnnualReportNav.propTypes = {
  basePath: PropTypes.string.isRequired,
  prevSlide: PropTypes.shape({
    slug: PropTypes.string,
  }),
  nextSlide: PropTypes.shape({
    slug: PropTypes.string,
  }),
};

AnnualReportNav.defaultProps = {
  prevSlide: null,
  nextSlide: null,
};

export default AnnualReportNav;
