import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import '../../../css/components/annual_reports/AnnualReportHamburgerMenu.scss';
import PropTypes from 'prop-types';

function AnnualReportHamburgerMenu({
  slides,
  basePath,
  currentLang,
  currentSlug,
  currentIndex,
  showTOC,
  setShowTOC,
}) {
  const navigate = useNavigate();
  const toEn = `${basePath}/en/${currentSlug}`;
  const toFr = `${basePath}/fr/${currentSlug}`;

  return (
    <div className="annual-report-hamburger-menu">
      <div className="ar-lang-toggle" role="group" aria-label="Language">
        <button
          type="button"
          className={`lang-btn ${currentLang === 'en' ? 'active' : ''}`}
          aria-pressed={currentLang === 'en'}
          onClick={() => navigate(toEn)}
        >
          EN
        </button>
        {slides[currentIndex]?.french_slide ? (
          <button
            type="button"
            className={`lang-btn ${currentLang === 'fr' ? 'active' : ''} ${
              !slides[currentIndex]?.french_slide ? 'disabled' : ''
            }`}
            aria-pressed={currentLang === 'fr'}
            onClick={() => navigate(toFr)}
          >
            FR
          </button>
        ) : (
          <span className="intl-disabled">FR</span>
        )}
      </div>
      <button
        className="hamburger-btn"
        type="button"
        onClick={() => setShowTOC(!showTOC)}
      >
        <AnimatePresence mode="sync">
          {showTOC ? (
            <motion.span
              key="close"
              className="close-icon"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2, ease: 'easeInOut' }}
            >
              <i className="fal fa-times" />
            </motion.span>
          ) : (
            <motion.span
              key="bars"
              className="bars-icon"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2, ease: 'easeInOut' }}
            >
              <i className="fal fa-bars" />
            </motion.span>
          )}
        </AnimatePresence>
      </button>
    </div>
  );
}

AnnualReportHamburgerMenu.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  currentLang: PropTypes.string.isRequired,
  currentSlug: PropTypes.string.isRequired,
  currentIndex: PropTypes.number.isRequired,
  showTOC: PropTypes.bool.isRequired,
  setShowTOC: PropTypes.func.isRequired,
};

export default AnnualReportHamburgerMenu;
