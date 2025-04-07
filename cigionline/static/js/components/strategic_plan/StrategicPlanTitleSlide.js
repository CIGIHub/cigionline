import PropTypes from 'prop-types';
import React from 'react';
import { motion } from 'framer-motion';

const StrategicPlanTitleSlide = ({ slide }) => (
  <div className="strategic-plan-slide title-slide">
    <div className="row">
      <div className="col-9 col-md-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
        >
          <a href="/">
            <svg className="large-logo" viewBox="0 0 129.4 37.8">
              <title>Centre for International Governance Innovation</title>
              <path d="M7.6,14v1.6a4,4,0,0,0-2.5-1,3.1,3.1,0,0,0-2.4,1,3.63,3.63,0,0,0,0,5,3.1,3.1,0,0,0,2.4,1,4.3,4.3,0,0,0,1.2-.2A4.35,4.35,0,0,0,7,21a4.23,4.23,0,0,1,.7-.5v1.7a5.53,5.53,0,0,1-2.5.7,4.76,4.76,0,0,1-3.4-1.4A4.72,4.72,0,0,1,1.6,15a4.8,4.8,0,0,1,3.7-1.7A4.76,4.76,0,0,1,7.6,14Zm6.8,6.1H10.2a1.61,1.61,0,0,0,.5,1.1,1.5,1.5,0,0,0,1.1.4,1.88,1.88,0,0,0,.8-.2,3.11,3.11,0,0,0,.7-.9l1.1.6a4.17,4.17,0,0,1-.6.8,2.65,2.65,0,0,1-.6.5c-.2.1-.5.2-.7.3a2.49,2.49,0,0,1-.8.1A3.23,3.23,0,0,1,9.6,22a3.49,3.49,0,0,1-.8-2.2,3,3,0,0,1,.8-2.2,2.17,2.17,0,0,1,2-.8,2.79,2.79,0,0,1,2,.8,2.93,2.93,0,0,1,.7,2.2ZM13,19a1.3,1.3,0,0,0-1.3-1,.9.9,0,0,0-.5.1.76.76,0,0,0-.4.2l-.3.3a.76.76,0,0,0-.2.5Zm2.9-2.1h1.4v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6H19.6V19.5a2.54,2.54,0,0,0-.2-1.2.92.92,0,0,0-.9-.3,1.28,1.28,0,0,0-1,.4,4,4,0,0,0-.3,1.5v2.8H15.9ZM24,18.2v4.6H22.7V18.2h-.6V17h.6V14.9H24V17h1v1.2Zm2-1.3h1.3v.5a1.79,1.79,0,0,1,.7-.5.88.88,0,0,1,.7-.1,1.5,1.5,0,0,1,1.1.4l-.6,1.2a1.14,1.14,0,0,0-.8-.3c-.7,0-1.1.6-1.1,1.7v3H26Zm9.8,3.2H31.6a1.61,1.61,0,0,0,.5,1.1,1.5,1.5,0,0,0,1.1.4,1.88,1.88,0,0,0,.8-.2,3.11,3.11,0,0,0,.7-.9l1.1.6a4.17,4.17,0,0,1-.6.8,2.65,2.65,0,0,1-.6.5c-.2.1-.5.2-.7.3a2.49,2.49,0,0,1-.8.1,2.88,2.88,0,0,1-2.1-.9,3.43,3.43,0,0,1,0-4.4,3,3,0,0,1,4.1,0,2.93,2.93,0,0,1,.7,2.2ZM34.4,19A1.25,1.25,0,0,0,33,18a.9.9,0,0,0-.5.1.76.76,0,0,0-.4.2l-.3.3a.76.76,0,0,0-.2.5Zm8-.8v4.6H41V18.2h-.5V17H41V14.8a2.4,2.4,0,0,1,.4-1.6,1.72,1.72,0,0,1,1.5-.6,2.92,2.92,0,0,1,.9.2v1.4l-.1-.2a1.85,1.85,0,0,0-.7-.2.55.55,0,0,0-.5.3,1.73,1.73,0,0,0-.1,1V17h1.5v1.2Zm2.1,1.6a2.72,2.72,0,0,1,.9-2.1,3.11,3.11,0,1,1,4.4,4.4,3.14,3.14,0,0,1-4.4,0A3.52,3.52,0,0,1,44.5,19.8Zm1.4,0a1.87,1.87,0,0,0,.5,1.4,1.75,1.75,0,0,0,2.5,0,2.25,2.25,0,0,0,0-2.7,1.75,1.75,0,0,0-2.5,0,1.3,1.3,0,0,0-.5,1.3Zm6.2-2.9h1.3v.5a1.79,1.79,0,0,1,.7-.5.88.88,0,0,1,.7-.1,1.5,1.5,0,0,1,1.1.4l-.6,1.2a1.14,1.14,0,0,0-.8-.3c-.7,0-1.1.6-1.1,1.7v3H52.1Zm10-3.4v9.2H60.7V13.5Zm2,3.4h1.3v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6H67.8V19.5a2.54,2.54,0,0,0-.2-1.2.86.86,0,0,0-.9-.3,1,1,0,0,0-.9.4,4,4,0,0,0-.3,1.5v2.8H64.1Zm8.1,1.3v4.6H70.9V18.2h-.6V17h.6V14.9h1.3V17h1v1.2Zm7.3,1.9H75.3a1.61,1.61,0,0,0,.5,1.1,1.5,1.5,0,0,0,1.1.4,1.88,1.88,0,0,0,.8-.2,3.11,3.11,0,0,0,.7-.9l1.1.6c-.2.3-.4.5-.6.8a2.65,2.65,0,0,1-.6.5c-.2.1-.5.2-.7.3a2.49,2.49,0,0,1-.8.1,3.23,3.23,0,0,1-2.1-.8,3,3,0,0,1-.7-2.3,3,3,0,0,1,.8-2.2,3,3,0,0,1,4.1,0,2.93,2.93,0,0,1,.7,2.2ZM78.2,19a1.33,1.33,0,0,0-1.4-1,.9.9,0,0,0-.5.1.76.76,0,0,0-.4.2l-.3.3a.76.76,0,0,0-.2.5ZM81,16.9h1.3v.5a1.79,1.79,0,0,1,.7-.5.88.88,0,0,1,.7-.1,1.5,1.5,0,0,1,1.1.4l-.6,1.2a1.14,1.14,0,0,0-.8-.3c-.7,0-1.1.6-1.1,1.7v3H81Zm5,0h1.3v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6H89.7V19.5a2.54,2.54,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1,1,0,0,0-.9.4,4,4,0,0,0-.3,1.5v2.8H86Zm10.8,0h1.3v5.8H96.8v-.6a2.53,2.53,0,0,1-3.6,0l-.1-.1a3.42,3.42,0,0,1,0-4.4,2.52,2.52,0,0,1,2-.9,2.34,2.34,0,0,1,1.8.8Zm-3.2,2.9a2.3,2.3,0,0,0,.4,1.4,1.69,1.69,0,0,0,2.4,0,2.25,2.25,0,0,0,0-2.7,1.66,1.66,0,0,0-1.2-.5,1.85,1.85,0,0,0-1.2.5A2,2,0,0,0,93.6,19.8Zm7.7-1.6v4.6H100V18.2h-.6V17h.6V14.9h1.3V17h1v1.2Zm2-3.7a.9.9,0,0,1,.9-.9.71.71,0,0,1,.6.3.86.86,0,0,1,.3.6.71.71,0,0,1-.3.6.86.86,0,0,1-.6.3.71.71,0,0,1-.6-.3A.71.71,0,0,1,103.3,14.5Zm1.5,2.4v5.8h-1.3V16.9Zm1.2,2.9a2.72,2.72,0,0,1,.9-2.1,3.11,3.11,0,1,1,4.4,4.4,3.14,3.14,0,0,1-4.4,0A3.52,3.52,0,0,1,106,19.8Zm1.4,0a1.87,1.87,0,0,0,.5,1.4,1.75,1.75,0,0,0,2.5,0,2.25,2.25,0,0,0,0-2.7,1.75,1.75,0,0,0-2.5,0,1.54,1.54,0,0,0-.5,1.3Zm6.2-2.9h1.3v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6h-1.3V19.5a2.54,2.54,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1,1,0,0,0-.9.4,4,4,0,0,0-.3,1.5v2.8h-1.3Zm11,0h1.3v5.8h-1.3v-.6a2.53,2.53,0,0,1-3.6,0l-.1-.1a3.42,3.42,0,0,1,0-4.4,2.52,2.52,0,0,1,2-.9,2.34,2.34,0,0,1,1.8.8Zm-3.2,2.9a2.3,2.3,0,0,0,.4,1.4,1.69,1.69,0,0,0,2.4,0,2.25,2.25,0,0,0,0-2.7A1.66,1.66,0,0,0,123,18a1.85,1.85,0,0,0-1.2.5A2,2,0,0,0,121.4,19.8Zm7.6-7.2V22.7h-1.3V12.6ZM5.6,32.6H9.4v.3a11,11,0,0,1-.2,1.8,3.92,3.92,0,0,1-.8,1.4,3.77,3.77,0,0,1-3.3,1.4,4.37,4.37,0,0,1-3.3-1.4,4.77,4.77,0,0,1,0-6.8A4.94,4.94,0,0,1,5.2,28a4.48,4.48,0,0,1,2,.4A6.23,6.23,0,0,1,9,29.8l-1,1a3.45,3.45,0,0,0-6.3,2,3.25,3.25,0,0,0,1.1,2.5,3.1,3.1,0,0,0,2.2.9,2.41,2.41,0,0,0,1.8-.7,2.59,2.59,0,0,0,.9-1.7H5.6Zm5,1.9a3.1,3.1,0,0,1,.9-2.2,3.11,3.11,0,0,1,4.4,4.4,3.1,3.1,0,0,1-5.3-2.2Zm1.3,0a1.87,1.87,0,0,0,.5,1.4,1.9,1.9,0,0,0,1.3.5,2.11,2.11,0,0,0,1.3-.5,2.25,2.25,0,0,0,0-2.7,1.75,1.75,0,0,0-2.5,0,2,2,0,0,0-.6,1.3Zm6.8-2.9,1.5,3.3,1.5-3.3h1.5l-3,6.2-3-6.2Zm10.5,3.2H25a1.85,1.85,0,0,0,.5,1.2,1.5,1.5,0,0,0,1.1.4,1.88,1.88,0,0,0,.8-.2,3.11,3.11,0,0,0,.7-.9l1.1.6a4.17,4.17,0,0,1-.6.8,2.65,2.65,0,0,1-.6.5c-.2.1-.5.2-.7.3a2.49,2.49,0,0,1-.8.1,3.23,3.23,0,0,1-2.1-.8,3.49,3.49,0,0,1-.8-2.2,3,3,0,0,1,.8-2.2,3,3,0,0,1,4.1,0,2.93,2.93,0,0,1,.7,2.2Zm-1.4-1.1a1.32,1.32,0,0,0-1.4-1.1.9.9,0,0,0-.5.1.76.76,0,0,0-.4.2l-.3.3a.76.76,0,0,0-.2.5Zm2.9-2.1H32v.5a1.79,1.79,0,0,1,.7-.5.88.88,0,0,1,.7-.1,1.5,1.5,0,0,1,1.1.4L33.9,33a1.14,1.14,0,0,0-.8-.3c-.7,0-1.1.6-1.1,1.7v3H30.7Zm4.7,0h1.3v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6H39.1V34.2a5,5,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1.28,1.28,0,0,0-1,.4,4,4,0,0,0-.3,1.5v2.8H35.4Zm11,0h1.3v5.8H46.4v-.6a2.53,2.53,0,0,1-3.6,0l-.1-.1a3.43,3.43,0,0,1,0-4.4,2.52,2.52,0,0,1,2-.9,2.34,2.34,0,0,1,1.8.8Zm-3.2,2.9a1.87,1.87,0,0,0,.5,1.4,1.69,1.69,0,0,0,2.4,0,2.25,2.25,0,0,0,0-2.7,1.66,1.66,0,0,0-1.2-.5,1.85,1.85,0,0,0-1.2.5A1.9,1.9,0,0,0,43.2,34.5Zm6.3-2.9h1.3v.5a2.36,2.36,0,0,1,1.6-.7A2.27,2.27,0,0,1,54,32a2.73,2.73,0,0,1,.5,1.8v3.6H53.1V34.2a5,5,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1.28,1.28,0,0,0-1,.4,4,4,0,0,0-.3,1.5v2.8H49.4V31.6Zm11.2.2v1.8a3,3,0,0,0-.8-.8,2.35,2.35,0,0,0-.8-.2,1.71,1.71,0,0,0-1.8,1.8,1.9,1.9,0,0,0,.5,1.3,1.46,1.46,0,0,0,1.2.5,1.88,1.88,0,0,0,.8-.2,3,3,0,0,0,.8-.8V37a3.17,3.17,0,0,1-1.6.4,3.34,3.34,0,0,1-2.3-.9,3.14,3.14,0,0,1,0-4.4,3.17,3.17,0,0,1,2.3-.9A16.19,16.19,0,0,1,60.7,31.8Zm7,3H63.5A1.85,1.85,0,0,0,64,36a1.5,1.5,0,0,0,1.1.4,1.88,1.88,0,0,0,.8-.2,3.11,3.11,0,0,0,.7-.9l1.1.6a4.17,4.17,0,0,1-.6.8,2.65,2.65,0,0,1-.6.5c-.2.1-.5.2-.7.3a2.49,2.49,0,0,1-.8.1,3.23,3.23,0,0,1-2.1-.8,3.49,3.49,0,0,1-.8-2.2,3,3,0,0,1,.8-2.2,3,3,0,0,1,4.1,0,2.93,2.93,0,0,1,.7,2.2Zm-1.4-1.1A1.38,1.38,0,0,0,65,32.6a.9.9,0,0,0-.5.1.76.76,0,0,0-.4.2l-.3.3a.76.76,0,0,0-.2.5Zm8.5-5.5v9.2H73.4V28.2Zm1.9,3.4H78v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6H80.4V34.2a5,5,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1,1,0,0,0-.9.4,4,4,0,0,0-.3,1.5v2.8H76.8l-.1-5.8Zm6.6,0h1.3v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6H87V34.2a5,5,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1,1,0,0,0-.9.4,4,4,0,0,0-.3,1.5v2.8H83.4l-.1-5.8Zm6.2,2.9a3.1,3.1,0,0,1,.9-2.2,3.11,3.11,0,0,1,4.4,4.4,3.1,3.1,0,0,1-5.3-2.2Zm1.4,0a1.87,1.87,0,0,0,.5,1.4,1.75,1.75,0,0,0,2.5,0,2.25,2.25,0,0,0,0-2.7,1.75,1.75,0,0,0-2.5,0,1.9,1.9,0,0,0-.5,1.3Zm6.7-2.9,1.5,3.3,1.5-3.3h1.5l-3,6.2-3-6.2Zm9.6,0h1.3v5.8h-1.3v-.6a2.53,2.53,0,0,1-3.6,0l-.1-.1a3.42,3.42,0,0,1,0-4.4,2.52,2.52,0,0,1,2-.9,2.34,2.34,0,0,1,1.8.8ZM104,34.5a2.3,2.3,0,0,0,.4,1.4,1.69,1.69,0,0,0,2.4,0,2.25,2.25,0,0,0,0-2.7,1.66,1.66,0,0,0-1.2-.5,1.85,1.85,0,0,0-1.2.5A2.5,2.5,0,0,0,104,34.5Zm7.7-1.7v4.6h-1.3V32.8h-.6V31.5h.6V29.4h1.3v2.1h1v1.2Zm2.1-3.6a.9.9,0,0,1,.9-.9.71.71,0,0,1,.6.3.86.86,0,0,1,.3.6.71.71,0,0,1-.3.6.86.86,0,0,1-.6.3.71.71,0,0,1-.6-.3A.6.6,0,0,1,113.8,29.2Zm1.5,2.4v5.8H114V31.6Zm1.2,2.9a3.1,3.1,0,0,1,.9-2.2,3.11,3.11,0,0,1,4.4,4.4,3.1,3.1,0,0,1-5.3-2.2Zm1.4,0a1.87,1.87,0,0,0,.5,1.4,1.75,1.75,0,0,0,2.5,0,2.25,2.25,0,0,0,0-2.7,1.75,1.75,0,0,0-2.5,0,1.54,1.54,0,0,0-.5,1.3Zm6.2-2.9h1.3v.5a2.36,2.36,0,0,1,1.6-.7,2.27,2.27,0,0,1,1.6.6,2.73,2.73,0,0,1,.5,1.8v3.6h-1.3V34.2a2.54,2.54,0,0,0-.2-1.2.83.83,0,0,0-.8-.3,1,1,0,0,0-.9.4,4,4,0,0,0-.3,1.5v2.8h-1.3ZM0,0H129.4V3.6H0Z" />
            </svg>
          </a>
          <div className="title-slide__title">
            <h1 aria-live="assertive">{slide.slide_title}</h1>
            <p>{slide.slide_subtitle}</p>
          </div>
        </motion.div>
        <motion.div
          className="navigation-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 1, 0] }}
          transition={{
            duration: 8,
            ease: 'easeInOut',
            times: [0, 0.2, 0.8, 1],
            delay: 0.5,
          }}
        >
          <div>
            <svg width="16px" height="59px" viewBox="0 0 16 59" version="1.1">
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
          <p>Use the mouse or keyboard to navigate</p>
        </motion.div>
      </div>
    </div>
  </div>
);

StrategicPlanTitleSlide.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default StrategicPlanTitleSlide;
