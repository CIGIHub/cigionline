/* global FB */
import React from 'react';
import PropTypes from 'prop-types';

const CardTextMore = (props) => {
  const { type, url, registrationUrl, pdfDownload, eventAccess, title } = props;

  const toSocialString = (str) => {
    const socialString = str.replace(/[^a-zA-Z0-9 ]/g, '');
    return socialString.replace(/ /g, '+');
  };
  const shareTitle = toSocialString(title);
  const shareUrl = `https://${window.location.host}${url.slice(0, -1)}`;
  const shareOnFacebook = (fbShareUrl) => {
    const href = fbShareUrl;
    FB.ui(
      {
        method: 'share',
        href,
      },
      function (/* response */) {},
    );
  };

  return (
    <div className="card__text__more__container dropup">
      <button
        type="button"
        className="card__text__more dropdown-toggle"
        data-bs-toggle="dropdown"
      >
        <i className="far fa-ellipsis-h" />
      </button>
      <div className="dropdown-menu dropdown-menu-end">
        <button
          className="dropdown-item copy-text-button"
          type="button"
          onClick={() =>
            navigator.clipboard.writeText(`${window.location.host}${url}`)
          }
        >
          <i className="fas fa-link" />
          Copy Link
        </button>
        <input type="text" value={url} className="copyText" readOnly />
        <a
          className="dropdown-item"
          href={`https://twitter.com/share?text=${shareTitle}&amp;url=${shareUrl}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <i className="fab fa-twitter" />
          Share on Twitter
        </a>
        <a
          className="dropdown-item"
          href={`https://www.linkedin.com/shareArticle?mini=true&amp;url=${shareUrl}&amp;title=${shareTitle}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <i className="fab fa-linkedin-in" />
          Share on Linkedin
        </a>
        <button
          className="dropdown-item facebook-share-link"
          type="button"
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => shareOnFacebook(shareUrl)}
        >
          <i className="fab fa-facebook-f" />
          Share on Facebook
        </button>
        {type === 'Event' && eventAccess && registrationUrl && (
          <a
            className="dropdown-item"
            href={registrationUrl}
            onClick="ga('send', 'event', 'Event Registration', 'Click' );"
          >
            <i className="fal fa-check-square" />
            Register
          </a>
        )}
        {type === 'Publication' && pdfDownload && (
          <a
            className="dropdown-item"
            href={pdfDownload}
            target="_blank"
            rel="noopener noreferrer"
          >
            <i className="fal fa-file-pdf" />
            Download PDF
          </a>
        )}
      </div>
    </div>
  );
};

CardTextMore.propTypes = {
  url: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  registrationUrl: PropTypes.string,
  pdfDownload: PropTypes.string,
  eventAccess: PropTypes.string,
};

CardTextMore.defaultProps = {
  registrationUrl: '',
  pdfDownload: '',
  eventAccess: '',
};

export default CardTextMore;
