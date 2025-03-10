import PropTypes from 'prop-types';
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../../css/components/AnnualReportNav.scss';

const AnnualReportNav = ({ slides, basePath }) => {
  const location = useLocation();
  const filteredSlides = slides.filter((slide) => slide.include_on_toc);

  return (
    <div className="slide-nav">
      {filteredSlides.map((slide) => (
        <Link
          key={slide.slug}
          to={`${basePath}/${slide.slug}`}
          className={`nav-circle ${
            location.pathname.includes(slide.slug) ? 'active' : ''
          }`}
        >
          <span />
        </Link>
      ))}
    </div>
  );
};

AnnualReportNav.propTypes = {
  slides: PropTypes.array.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportNav;
