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

  handleConsent() {
    document.cookie = `cigionline.accept.privacy.notice=1; expires=${new Date(2147483647 * 1000).toUTCString()}`;
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

    const bannerCopy = `
      This site uses cookies to provide the best online experience. By using
      this site, you agree to the use of cookies and collection of personal
      information per our <a href="/privacy-policy">Privacy Notice</a>. To
      alter or disable the use of cookies, adjust your browser settings.
    `;

    /* eslint-disable react/no-danger */
    return (
      <div className={['cigi-cookie-banner', consentFade && 'consent-fade', consentComplete && 'consent-complete'].join(' ')}>
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="cigi-cookie-banner-content">
                <p className={['cigi-cookie-banner-notice', consentClicked && 'accepted-consent'].join(' ')} dangerouslySetInnerHTML={{ __html: bannerCopy }} />
                <button
                  type="button"
                  className={['cigi-cookie-banner-notice', consentClicked && 'accepted-consent'].join(' ')}
                  onClick={() => this.handleConsent()}
                >
                  <span>OK</span>
                  <i className="fa fa-check" />
                </button>
                {consentClicked && (
                  <div className="cigi-cookie-banner-thank-you">
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
