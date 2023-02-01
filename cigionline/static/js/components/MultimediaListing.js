import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/MultimediaListing.scss';

function MultimediaListing(props) {
  const { row } = props;

  return (
    <div className="col multimedia-list-col">
      <article className="card__container card--small--multimedia card--small--multimedia--wide">
        <div className="card__image">
          <a href={row.url} className="feature-content-image">
            <div className="img-wrapper">
              <img src={row.image_hero_wide_url} alt={row.title} />
            </div>
          </a>
          <div className="card__image__play-icon">
            {row.contentsubtype === 'Audio' ? (
              <i className="fal fa-microphone" />
            ) : (
              <i className="fas fa-play" />
            )}
          </div>
          <div className="card__image__mm-length">{row.length}</div>
        </div>
        <div className="card__text">
          <h3 className="card__text__title {{ additional_classes }}">
            <a href={row.url}>{row.title}</a>
          </h3>
          <div className="card__text__meta">
            <div>
              <ul className="custom-text-list card__text__people">
                {row.authors.slice(0, 3).map((author) => (
                  <li key={`${row.id}-author-${author.id}`}>
                    <a href={author.url}>{author.title}</a>
                  </li>
                ))}
                {row.authors.length > 3 && (
                  <li key={`${row.id}-author-more`}>And more</li>
                )}
              </ul>
              <ul className="card__text__topics custom-text-list">
                {row.topics.map((topic) => (
                  <li key={`${row.id}-topic-${topic.id}`}>
                    <a href={topic.url} className="table-content-link">
                      {topic.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            <button type="button" className="card__text__more">
              <a href="{{ url }}">
                <i className="far fa-ellipsis-h" />
              </a>
            </button>
          </div>
        </div>
      </article>
    </div>
  );
}

MultimediaListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contentsubtype: PropTypes.string,
    id: PropTypes.number,
    image_hero_wide_url: PropTypes.string,
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    length: PropTypes.string,
    url: PropTypes.string.isRequired,
  }).isRequired,
};

export default MultimediaListing;
