import React from 'react';
import PropTypes from 'prop-types';

const CardTextMore = (props) => {
  const { type, url, registrationUrl, pdfDownload, eventAccess, title } = props;

  const toSocialString = (str) => {
    const socialString = str.replace(/[^a-zA-Z0-9 ]/g, '');
    return socialString.replace(/ /g, '%20');
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
        <button className="dropdown-item copy-text-button" type="button">
          <i className="fas fa-link" />
          Copy Link
        </button>
        <input type="text" value={url} className="copyText" />
        <a
          className="dropdown-item"
          href={`https://twitter.com/share?text=${toSocialString(
            title,
          )}&amp;url=${url.slice(0, -1)}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <i className="fab fa-twitter" />
          Share on Twitter
        </a>
        <a
          className="dropdown-item"
          href={`https://www.linkedin.com/shareArticle?mini=true&amp;url=${url.slice(
            0,
            -1,
          )}&amp;title=${toSocialString(title)}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <i className="fab fa-linkedin-in" />
          Share on Linkedin
        </a>
        <a
          className="dropdown-item"
          data-url={url.slice(0, -1)}
          target="_blank"
          rel="noopener noreferrer"
        >
          <i className="fab fa-facebook-f" />
          Share on Facebook
        </a>
        {type === 'event' && eventAccess === 'Public' && (
          <a
            className="dropdown-item"
            href={registrationUrl}
            onClick="ga('send', 'event', 'Event Registration', 'Click' );"
          >
            <i className="fal fa-check-square" />
            Register
          </a>
        )}
        {type === 'publication' && pdfDownload && (
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
