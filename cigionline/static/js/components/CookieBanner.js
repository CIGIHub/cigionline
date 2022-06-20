import React from 'react';
import '../../css/components/CookieBanner.scss';

class CookieBanner extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bannerClicked: false,
      bannerComplete: false,
      bannerFade: false,
    };

    this.handleBanner = this.handleBanner.bind(this);
  }

  handleBanner() {
    document.cookie = `cigionline.accept.banner=1; path=/; expires=${new Date(2147483647 * 1000).toUTCString()}`;
    this.setState({
      bannerClicked: true,
    });
    setTimeout(() => {
      this.setState({
        bannerFade: true,
      });
    }, 1500);
    setTimeout(() => {
      this.setState({
        bannerComplete: true,
      });
    }, 1500);
  }

  render() {
    const { bannerClicked, bannerFade, bannerComplete } = this.state;

    const bannerCopy = `
      Win one of three $100 Visa cards by participating in CIGI's feedback survey - take the survey, click <a href="https://google.ca">here</a>.
    `;

    /* eslint-disable react/no-danger */
    return (
      <div className={['cigi-cookie-banner', bannerFade && 'banner-fade', bannerComplete && 'banner-complete'].join(' ')}>
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="cigi-cookie-banner-content">
                <p className={['cigi-cookie-banner-notice', bannerClicked && 'accepted-banner'].join(' ')}>
                  Win one of three $100 Visa cards by participating in CIGI&apos;s feedback survey -
                  take the survey, click&nbsp;
                  <a href="https://google.ca" target="_blank" rel="noopener noreferrer" onClick={() => this.handleBanner()}>here</a>
                  .
                </p>
                <button
                  type="button"
                  className={['cigi-cookie-banner-notice', bannerClicked && 'accepted-banner'].join(' ')}
                  onClick={() => this.handleBanner()}
                >
                  <i className="fal fa-times" />
                </button>
                {bannerClicked && (
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

export default CookieBanner;
