import React from 'react';
import MobileDetect from 'mobile-detect';
import {
  getLanguage,
} from './AnnualReportUtils';

const HomeSlide = ({ year }) => {
  const language = getLanguage();
  const md = new MobileDetect(window.navigator.userAgent);
  const isMobile = md.mobile();

  return (
    <div className="liquid-container" style={{}}>
      <div
        className="liquid-child"
        style={{ top: 0, left: 0 }}
      >
        <div className="background-row show-for-medium">
          <div className="background-image background-index" />
        </div>
        <div className="home-page">
          {language === 'en' ? (
            <div className="intro-logo">
              <span className="year">{year}</span>
              <>
                <span className="text" style={isMobile ? { display: 'inherit' } : {}}>
                  <span className="annual">Annual</span>
                  <br />
                  <span className="report">Report</span>
                </span>
              </>
            </div>
          ) : (
            <div className="intro-logo">
              <>
                <span className="text" style={isMobile ? { display: 'inherit' } : {}}>
                  <span className="report">Rapport</span>
                  <br />
                  <span className="annual">Annuel</span>
                </span>
              </>
              <span className="year">{year}</span>
            </div>
          )}
          <div className="navigation-section">
            <p>Use the mouse or keyboard to navigate</p>
            <svg
              width="16px"
              height="59px"
              viewBox="0 0 16 59"
              version="1.1"
              xmlns="http://www.w3.org/2000/svg"
              xmlnsXlink="http://www.w3.org/1999/xlink"
            >
              <g
                id="IN-PROGRESS"
                stroke="none"
                strokeWidth="1"
                fill="none"
                fillRule="evenodd"
              >
                <g
                  id="Artboard-2-Copy-6"
                  transform="translate(-736.000000, -863.000000)"
                >
                  <g
                    id="Group-2-Copy"
                    transform="translate(736.000000, 864.000000)"
                  >
                    <path
                      id="Line-2"
                      d="M8,57.1376812 L12.5,48.1376812 L3.5,48.1376812 L8,57.1376812 Z M7.5,42.5 L7.5,48.6376812 L7.5,49.1376812 L8.5,49.1376812 L8.5,48.6376812 L8.5,42.5 L8.5,42 L7.5,42 L7.5,42.5 Z"
                      fill="#FFFFFF"
                      fillRule="nonzero"
                    />
                    <path
                      id="Line-2"
                      d="M8,-0.166666667 L3.5,8.83333333 L12.5,8.83333333 L8,-0.166666667 Z M8.5,13.5 L8.5,8.33333333 L8.5,7.83333333 L7.5,7.83333333 L7.5,8.33333333 L7.5,13.5 L7.5,14 L8.5,14 L8.5,13.5 Z"
                      fill="#FFFFFF"
                      fillRule="nonzero"
                    />
                    <g id="Group" transform="translate(0.000000, 13.000000)">
                      <rect
                        id="Rectangle-5"
                        stroke="#FFFFFF"
                        x="0.5"
                        y="0.5"
                        width="15"
                        height="29"
                        rx="7.5"
                      />
                      <rect
                        id="Rectangle-5"
                        fill="#FFFFFF"
                        x="7.11111111"
                        y="9"
                        width="1.77777778"
                        height="5"
                        rx="0.888888889"
                      />
                    </g>
                  </g>
                </g>
              </g>
            </svg>
            <svg
              className="up-down-icon"
              width="29px"
              height="60px"
              viewBox="0 0 29 60"
              version="1.1"
              xmlns="http://www.w3.org/2000/svg"
              xmlnsXlink="http://www.w3.org/1999/xlink"
            >
              <g
                id="IN-PROGRESS"
                stroke="none"
                strokeWidth="1"
                fill="none"
                fillRule="evenodd"
              >
                <g
                  id="Artboard-2-Copy-7"
                  transform="translate(-751.000000, -861.000000)"
                >
                  <g id="Group-5" transform="translate(751.000000, 861.000000)">
                    <polygon
                      id="Triangle-Copy"
                      fill="#FFFFFF"
                      points="14.1111111 48.3116883 11 43.6363636 17.2222222 43.6363636"
                    />
                    <polygon
                      id="Triangle-Copy-4"
                      fill="#FFFFFF"
                      transform="translate(14.111111, 14.025974) rotate(-180.000000) translate(-14.111111, -14.025974) "
                      points="14.1111111 16.3636364 11 11.6883117 17.2222222 11.6883117"
                    />
                    <rect
                      id="Rectangle-8-Copy"
                      stroke="#FFFFFF"
                      x="0.611111111"
                      y="31.6688312"
                      width="27.7777778"
                      height="27.8311688"
                      rx="4"
                    />
                    <rect
                      id="Rectangle-8-Copy-3"
                      stroke="#FFFFFF"
                      x="0.611111111"
                      y="0.5"
                      width="27.7777778"
                      height="27.8311688"
                      rx="4"
                    />
                  </g>
                </g>
              </g>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomeSlide;
