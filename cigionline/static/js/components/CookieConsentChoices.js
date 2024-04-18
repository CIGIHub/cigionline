import React, { useState } from 'react';

const CookieConsentChoices = (props) => {
  const { handleConsent, pageChange, consentClicked } = props;
  const [consentChoices, setConsentChoices] = useState({
    analytics_storage: 'granted',
    ad_storage: 'granted',
  });
  const [analyticsChecked, setAnalyticsChecked] = useState(true);
  const [adChecked, setAdChecked] = useState(true);

  const handleChoice = (e) => {
    const { name, checked } = e.target;
    setConsentChoices({
      ...consentChoices,
      [name]: checked ? 'granted' : 'denied',
    });
    if (name === 'analytics_storage') {
      setAnalyticsChecked(checked);
    }
    if (name === 'ad_storage') {
      setAdChecked(checked);
    }
  };
  return (
    <div
      className={[
        'cigi-cookie-consent-content',
        consentClicked && 'accepted-consent',
      ].join(' ')}
    >
      <div className="cigi-cookie-consent-notice">
        <h2>Cookie choices</h2>
        <p>
          Please select the cookies you would like to enable on the CIGI
          website:
        </p>
        <ul className="cigi-cookie-consent-choices">
          <li className="cigi-cookie-consent-notice">
            <input
              type="checkbox"
              name="analytics_storage"
              value="google-analytics"
              checked={analyticsChecked}
              onChange={(e) => handleChoice(e)}
            />
            <p>
              Google Analytics: CIGI uses cookies on our website to gather
              analytics data, helping us understand how visitors interact with
              our site to enhance user experience and optimize site
              functionality.
            </p>
          </li>
          <li className="cigi-cookie-consent-notice">
            <input
              type="checkbox"
              name="ad_storage"
              value="google-ads"
              checked={adChecked}
              onChange={(e) => handleChoice(e)}
            />
            <p>
              Google Ads: Although we do not host ads on our site, Google Ads
              cookies are utilized to improve the relevance of CIGI ads you may
              see elsewhere, enhancing targeting and efficiency.
            </p>
          </li>
        </ul>
      </div>
      <div className="cigi-cookie-consent-content-buttons">
        <button
          type="button"
          className="cigi-cookie-consent-notice"
          onClick={() => handleConsent(consentChoices)}
        >
          <span>Save</span>
          <i className="fa fa-check" />
        </button>
        <button
          type="button"
          className="cigi-cookie-consent-notice"
          onClick={() => pageChange('content')}
        >
          <span>Back</span>
          <i className="fa fa-arrow-turn-down-left" />
        </button>
      </div>
    </div>
  );
};

export default CookieConsentChoices;
