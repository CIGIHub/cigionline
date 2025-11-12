import PropTypes from 'prop-types';
import React, { useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faShareNodes,
  faMessageQuote,
  faArrowRight,
} from '@fortawesome/pro-light-svg-icons';
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

function useShareLinks(slide) {
  const { pathname, search, hash } = useLocation();

  const origin =
    typeof window !== 'undefined' && window.location?.origin
      ? window.location.origin
      : 'https://www.cigionline.org';

  const absoluteUrl = useMemo(
    () => `${origin}${pathname}${search}${hash}`,
    [origin, pathname, search, hash],
  );

  const encodedUrl = encodeURIComponent(absoluteUrl);
  const text = encodeURIComponent(
    `${slide?.slide_title || 'CIGI Annual Report'} — ${
      slide.year
    } CIGI Annual Report`,
  );

  return {
    url: absoluteUrl,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    x: `https://x.com/intent/post?url=${encodedUrl}&text=${text}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
  };
}

function AnnualReportFooter({ slide, onHoverChange, dimUI }) {
  const handleEnter = () => onHoverChange?.(true);
  const handleLeave = () => onHoverChange?.(false);
  const [socialOpen, setSocialOpen] = useState(false);
  const share = useShareLinks(slide);

  return (
    <div
      className={`footer d-none d-lg-flex ${
        darkSlideTypes.includes(slide.slide_type) ? 'footer-dark' : ''
      }`}
    >
      {(slide.background_quote || slide.background_image) && (
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
      <div
        className={`cigi-social fadeable${dimUI ? ' is-dimmed' : ''} ${
          socialOpen ? ' open' : ''
        }`}
      >
        {socialOpen && (
          <div className="social-buttons">
            <a
              className="social-1-btn"
              href={share.facebook}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Share on Facebook"
            >
              <FontAwesomeIcon
                icon={faFacebookSquare}
                className="svg-inline--fa fa-facebook-square fa-lg"
              />
            </a>
            <a
              className="social-2-btn"
              href={share.x}
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
              href={share.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Share on LinkedIn"
            >
              <FontAwesomeIcon
                icon={faLinkedinIn}
                className="svg-inline--fa fa-linkedin-in fa-lg"
              />
            </a>
          </div>
        )}
        <button
          className="open-social-menu-btn"
          type="button"
          aria-label="More sharing options"
        >
          {socialOpen ? (
            <FontAwesomeIcon
              icon={faArrowRight}
              className="svg-inline--fa fa-arrow-right fa-lg"
              onClick={() => setSocialOpen(!socialOpen)}
            />
          ) : (
            <FontAwesomeIcon
              icon={faShareNodes}
              className="svg-inline--fa fa-share-nodes fa-lg"
              onClick={() => setSocialOpen(!socialOpen)}
            />
          )}
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
