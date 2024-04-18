import React from 'react';
import '../../css/components/CookieConsent.scss';
import CookieConsentContent from './CookieConsentContent';
import CookieConsentChoices from './CookieConsentChoices';

class CookieConsent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      consentClicked: false,
      consentComplete: false,
      consentFade: false,
      consentPage: 'content',
      consentState: {
        analytics_storage: 'granted',
        ad_storage: 'granted',
      },
    };

    this.handleConsent = this.handleConsent.bind(this);
    this.pageChange = this.pageChange.bind(this);
  }

  handleConsent(choice) {
    if (choice === 'all') {
      this.setState(
        {
          consentState: {
            analytics_storage: 'granted',
            ad_storage: 'granted',
          },
        },
        () => {
          const { consentState } = this.state;
          window.gtag('consent', 'update', consentState);
          localStorage.setItem('consentMode', JSON.stringify(consentState));
        },
      );
    } else {
      this.setState(
        {
          consentState: choice,
        },
        () => {
          const { consentState } = this.state;
          window.gtag('consent', 'update', consentState);
          localStorage.setItem('consentMode', JSON.stringify(consentState));
        },
      );
    }
    this.setState({
      consentClicked: true,
    });
    setTimeout(() => {
      this.setState({
        consentFade: true,
      });
    }, 3000);
    setTimeout(() => {
      this.setState({
        consentComplete: true,
      });
    }, 4000);
  }

  pageChange(page) {
    this.setState({
      consentPage: page,
    });
  }

  render() {
    const {
      consentClicked,
      consentFade,
      consentComplete,
      consentPage,
      consentState,
    } = this.state;

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
              {consentPage === 'content' && (
                <CookieConsentContent
                  consentClicked={consentClicked}
                  consentCopy={consentCopy}
                  handleConsent={this.handleConsent}
                  pageChange={this.pageChange}
                />
              )}
              {consentPage === 'choices' && (
                <CookieConsentChoices
                  consentClicked={consentClicked}
                  pageChange={this.pageChange}
                  handleConsent={this.handleConsent}
                  consentState={consentState}
                />
              )}
              {consentClicked && (
                <div className="cigi-cookie-consent-thank-you">
                  <p>Thank You</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default CookieConsent;
