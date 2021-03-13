import React from 'react';
import '../../css/components/CookieConsent.scss';

class CookieConsent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      consentClicked: false,
    };

    this.handleConsent = this.handleConsent.bind(this);
  }

  handleConsent() {
    this.setState({
      consentClicked: true,
    });
  }

  render() {
    const { consentClicked } = this.state;

    const bannerCopy = `
      This site uses cookies to provide the best online experience. By using
      this site, you agree to the use of cookies and collection of personal
      information per our <a href="/privacy-policy">Privacy Notice</a>. To
      alter or disable the use of cookies, adjust your browser settings.
    `;

    /* eslint-disable react/no-danger */
    return (
      <div className="cigi-cookie-banner">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="cigi-cookie-banner-content">
                {consentClicked ? (
                  <p>Thank You</p>
                ) : (
                  <>
                    <p dangerouslySetInnerHTML={{ __html: bannerCopy }} />
                    <button
                      type="button"
                      onClick={() => this.handleConsent()}
                    >
                      <span>OK</span>
                      <i className="fa fa-check" />
                    </button>
                  </>
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
