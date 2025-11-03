import PropTypes from 'prop-types';
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCameraRetro, faShareNodes, faMessageQuote } from '@fortawesome/pro-light-svg-icons';
import {
  faFacebookSquare,
  faXTwitter,
  faLinkedinIn,
} from '@fortawesome/free-brands-svg-icons';
import '../../../css/components/annual_reports/AnnualReportFooter.scss';

const darkSlideTypes = [
  'chairs_message',
  'presidents_message',
  'outputs-and-activities',
  'financials',
];

function AnnualReportFooter({ slide, onHoverChange, dimUI }) {
  const handleEnter = () => onHoverChange?.(true);
  const handleLeave = () => onHoverChange?.(false);

  return (
    <div
      className={`footer d-none d-lg-flex ${
        darkSlideTypes.includes(slide.slide_type) ? 'footer-dark' : ''
      }`}
    >
      {slide.background_quote && (
        <button
          className="footer-icon-btn"
          type="button"
          onMouseEnter={handleEnter}
          onMouseLeave={handleLeave}
          onFocus={handleEnter}
          onBlur={handleLeave}
        >
          <div className={`radial-progress ${dimUI ? ' is-dimmed' : ''}`}>
            <div className="circle">
              <div className="mask left">
                <div className="fill" />
              </div>
              <div className="mask right">
                <div className="fill" />
              </div>
            </div>
          </div>
          <FontAwesomeIcon
            icon={faMessageQuote}
            className="svg-inline--fa fa-camera-retro fa-lg"
            aria-hidden="true"
            focusable="false"
            role="img"
          />
        </button>
      )}
      <div className={`cigi-social fadeable${dimUI ? ' is-dimmed' : ''}`}>
        <button
          className="social-1-btn"
          type="button"
          aria-label="Share on Facebook"
        >
          <FontAwesomeIcon
            icon={faFacebookSquare}
            className="svg-inline--fa fa-facebook-square fa-lg"
          />
        </button>
        <a
          className="social-2-btn"
          href="https://twitter.com/intent/tweet?text=2024+CIGI+Annual+Report+https://www.cigionline.org/interactives/2024annualreport/en/table-of-contents"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Share on Twitter"
        >
          <FontAwesomeIcon
            icon={faXTwitter}
            className="svg-inline--fa fa-x-twitter fa-lg"
          />
        </a>
        <a
          className="social-3-btn"
          href="https://www.linkedin.com/shareArticle?mini=true&amp;url=https://www.cigionline.org/interactives/2024annualreport/en/table-of-contents"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Share on LinkedIn"
        >
          <FontAwesomeIcon
            icon={faLinkedinIn}
            className="svg-inline--fa fa-linkedin-in fa-lg"
          />
        </a>
        <button
          className="open-social-menu-btn"
          type="button"
          aria-label="More sharing options"
        >
          <FontAwesomeIcon
            icon={faShareNodes}
            className="svg-inline--fa fa-share-nodes fa-lg"
          />
        </button>
      </div>
    </div>
  );
}

AnnualReportFooter.propTypes = {
  slide: PropTypes.object.isRequired,
  onHoverChange: PropTypes.func.isRequired,
  dimUI: PropTypes.bool.isRequired,
};

export default AnnualReportFooter;
