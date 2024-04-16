import React from 'react';
import '../../css/components/CookieConsent.scss';

class CookieConsent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      consentClicked: false,
      consentComplete: false,
      consentFade: false,
    };

    this.handleConsent = this.handleConsent.bind(this);
  }

  handleConsent(choice) {
    if (choice === 'none') {
      document.cookie = `cigionline.accept.privacy.notice=2; path=/; expires=${new Date(
        2147483647 * 1000,
      ).toUTCString()}`;
    }
    if (choice === 'all') {
      document.cookie = `cigionline.accept.privacy.notice=1; path=/; expires=${new Date(
        2147483647 * 1000,
      ).toUTCString()}`;
    }
    if (choice === 'google') {
      const consentMode = {
        'analytics_storage': 'granted',
      };
      window.gtag('consent', 'update', consentMode);
      localStorage.setItem('consentMode', JSON.stringify(consentMode));
    }
    this.setState({
      consentClicked: true,
    });
    setTimeout(() => {
      this.setState({
        consentFade: true,
      });
    }, 1500);
    setTimeout(() => {
      this.setState({
        consentComplete: true,
      });
    }, 2000);
  }

  render() {
    const { consentClicked, consentFade, consentComplete } = this.state;

    const consentCopy = `
      This site uses cookies to provide the best online experience. By using
      this site, you agree to the use of cookies and collection of personal
      information per our <a href="/privacy-policy">Privacy Notice</a>. To
      alter or disable the use of cookies, adjust your browser settings.
    `;

    /* eslint-disable react/no-danger */
    return (
      <div
        className={[
          'cigi-cookie-consent',
          consentFade && 'consent-fade',
          consentComplete && 'consent-complete',
        ].join(' ')}
      >
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="cigi-cookie-consent-content">
                <p
                  className={[
                    'cigi-cookie-consent-notice',
                    consentClicked && 'accepted-consent',
                  ].join(' ')}
                  dangerouslySetInnerHTML={{ __html: consentCopy }}
                />
                <button
                  type="button"
                  className={[
                    'cigi-cookie-consent-notice',
                    consentClicked && 'accepted-consent',
                  ].join(' ')}
                  onClick={() => this.handleConsent('all')}
                >
                  <span>OK</span>
                  <i className="fa fa-check" />
                </button>
                <button
                  type="button"
                  className={[
                    'cigi-cookie-consent-notice',
                    consentClicked && 'accepted-consent',
                  ].join(' ')}
                  onClick={() => this.handleConsent('none')}
                >
                  <span>none</span>
                  <i className="fa fa-check" />
                </button>
                <button
                  type="button"
                  className={[
                    'cigi-cookie-consent-notice',
                    consentClicked && 'accepted-consent',
                  ].join(' ')}
                  onClick={() => this.handleConsent('google')}
                >
                  <span>google</span>
                  <i className="fa fa-check" />
                </button>
                {consentClicked && (
                  <div className="cigi-cookie-consent-thank-you">
                    <p>Thank You</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default CookieConsent;
