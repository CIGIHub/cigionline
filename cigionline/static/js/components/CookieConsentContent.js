import React from 'react';

function CookieConsentContent(props) {
  const { consentClicked, consentCopy, handleConsent, pageChange } = props;
  return (
    <div
      className={[
        'cigi-cookie-consent-content',
        consentClicked && 'accepted-consent',
      ].join(' ')}
    >
      <div>
        <p
          className="cigi-cookie-consent-notice"
          dangerouslySetInnerHTML={{ __html: consentCopy }}
        />
      </div>
      <div className="cigi-cookie-consent-content-buttons">
        <button
          type="button"
          className="cigi-cookie-consent-notice"
          onClick={() => handleConsent('all')}
        >
          <span>OK</span>
          <i className="fa fa-check" />
        </button>
        <button
          type="button"
          className="cigi-cookie-consent-notice"
          onClick={() => pageChange('choices')}
        >
          <span>Opt Out</span>
          <i className="fa fa-x" />
        </button>
      </div>
    </div>
  );
}

export default CookieConsentContent;
