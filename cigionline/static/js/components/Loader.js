import React, { useState, useEffect } from 'react';
import '../../css/components/Loader.scss';
import PropTypes from 'prop-types';

function Loader({ isLoading }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isLoading) return;

    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += Math.round(Math.random() * 10);
      if (currentProgress >= 100) {
        clearInterval(interval);
      }
      setProgress(Math.min(currentProgress, 100));
    }, 50);

    () => clearInterval(interval);
  }, [isLoading]);

  return (
    <div className={`loading-container ${isLoading ? 'visible' : 'hidden'}`}>
      <div className="loading">
        <div className="progress-icon">
          <svg
            version="1.1"
            id="Layer_1"
            xmlns="http://www.w3.org/2000/svg"
            xmlnsXlink="http://www.w3.org/1999/xlink"
            viewBox="0 0 45.9 25.6"
            style={{ enableBackground: 'new 0 0 45.9 25.6' }}
            xmlSpace="preserve"
          >
            <mask id="mask">
              <rect width="100%" height="100%" x="0%" y="0" fill="#fff" />
            </mask>
            <g mask="url(#mask)">
              <rect className="background-progress" />
            </g>
            <g mask="url(#mask)">
              <rect
                id="loading-progress"
                className={`progress update-${progress}`}
              />
            </g>
            <svg
              version="1.1"
              id="Layer_1"
              xmlns="http://www.w3.org/2000/svg"
              xmlnsXlink="http://www.w3.org/1999/xlink"
              viewBox="0 0 45.9 25.6"
              style={{ enableBackground: 'new 0 0 45.9 25.6' }}
              xmlSpace="preserve"
            >
              <path
                d="M47,26.4H-0.7V-1H47V26.4z M7.7,10.5c-2.4,0-4.4,0.9-5.9,2.7c-1.2,1.5-1.8,3.1-1.8,5c0,2.1,0.7,3.8,2.2,5.3
                c1.5,1.5,3.3,2.2,5.3,2.2c1.4,0,2.7-0.4,4-1.1v-2.7c-0.4,0.3-0.7,0.6-1,0.8c-0.3,0.2-0.6,0.4-0.9,0.5c-0.5,0.3-1.2,0.4-2,0.4
                c-1.5,0-2.8-0.5-3.8-1.6c-1-1.1-1.5-2.3-1.5-3.9c0-1.5,0.5-2.9,1.5-3.9c1-1.1,2.3-1.6,3.8-1.6c1.4,0,2.7,0.5,3.9,1.6v-2.6
                C10.3,10.8,9,10.5,7.7,10.5z M16.7,10.7v14.6h2.2V10.7H16.7z M32.3,19.8h3.6c-0.1,1-0.6,1.9-1.4,2.6c-0.9,0.7-1.8,1.1-2.9,1.1
                c-1.3,0-2.5-0.5-3.5-1.5c-1.2-1.1-1.7-2.4-1.7-4c0-1.6,0.5-2.9,1.6-3.9c1-1.1,2.3-1.6,3.9-1.6c1.7,0,3.2,0.8,4.4,2.4l1.6-1.5
                c-0.9-1-1.8-1.8-2.8-2.3c-1-0.5-2.1-0.7-3.2-0.7c-2.1,0-3.9,0.7-5.4,2.2c-1.5,1.5-2.2,3.3-2.2,5.4c0,2.1,0.7,3.8,2.2,5.3
                c1.5,1.5,3.2,2.2,5.2,2.2c2.1,0,3.8-0.8,5.2-2.3c0.6-0.7,1-1.4,1.3-2.2c0.3-0.8,0.4-1.8,0.4-2.9v-0.5h-6V19.8z M43.6,10.7v14.6h2.2
                V10.7H43.6z M45.9,0H0v3.6h45.9V0z"
              />
            </svg>
          </svg>
        </div>
        <p>
          {progress}
          %
        </p>
      </div>
    </div>
  );
}

Loader.propTypes = {
  isLoading: PropTypes.bool.isRequired,
};

export default Loader;
