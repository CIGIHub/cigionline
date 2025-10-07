import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import '../../../css/components/annual_reports/AnnualReportHamburgerMenu.scss';
import PropTypes from 'prop-types';

function AnnualReportHamburgerMenu({
  slides,
  basePath,
  currentLang,
  currentSlug,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const toEn = `${basePath}/en/${currentSlug}`;
  const toFr = `${basePath}/fr/${currentSlug}`;

  return (
    <>
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
          <button
            type="button"
            className={`lang-btn ${currentLang === 'fr' ? 'active' : ''}`}
            aria-pressed={currentLang === 'fr'}
            onClick={() => navigate(toFr)}
          >
            FR
          </button>
        </div>
        <button
          className="hamburger-btn"
          type="button"
          onClick={() => setIsOpen(!isOpen)}
        >
          <AnimatePresence mode="sync">
            {isOpen ? (
              <motion.div
                key="close"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2, ease: 'easeInOut' }}
              >
                <i className="fal fa-times" />
              </motion.div>
            ) : (
              <motion.span
                key="bars"
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
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              className="menu-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              onClick={() => setIsOpen(false)}
            />

            <div className="menu-content">
              <div className="container">
                <div className="row justify-content-center align-items-center">
                  <div className="col">
                    <motion.h2
                      className="menu-title"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, transition: { delay: 0 } }}
                      transition={{ delay: 0.3, duration: 0.5 }}
                    >
                      {`Annual Report ${slides[0].year}`}
                    </motion.h2>

                    <motion.div
                      className="slide-list"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, transition: { delay: 0 } }}
                      transition={{ delay: 0.8, duration: 0.5 }}
                    >
                      <div className="toc-menu">
                        toc menu
                      </div>
                      <hr />
                      <ol>
                        {slides.map((slide, index) => (
                          <li key={slide.slug} className="slide-link row">
                            <p className="col-1 slide-number">
                              {`0${index + 1}`.slice(-2)}
                            </p>
                            <div className="col">
                              <Link
                                to={`${basePath}/${slide.slug}${
                                  currentLang === 'fr' ? '/fr' : ''
                                }`}
                                onClick={() => setIsOpen(false)}
                              >
                                {slide.slide_title}
                              </Link>
                            </div>
                          </li>
                        ))}
                      </ol>
                    </motion.div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

AnnualReportHamburgerMenu.propTypes = {
  slides: PropTypes.arrayOf(PropTypes.object).isRequired,
  basePath: PropTypes.string.isRequired,
  currentLang: PropTypes.string.isRequired,
  currentSlug: PropTypes.string.isRequired,
};

export default AnnualReportHamburgerMenu;
