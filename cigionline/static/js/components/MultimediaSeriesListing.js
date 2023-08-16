import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/MultimediaSeriesListing.scss';

function MultimediaSeriesListing(props) {
  const { row } = props;

  /* eslint-disable react/no-danger */
  return (
    <article className="multimedia-listing-series multimedia-list-col simple-listing">
      <a href={row.url} className="multimedia-card-image">
        <div className="img-wrapper" style={{ backgroundImage: `url(${row.image_hero_url})` }} />
        <div className="multimedia-image-type">
          {row.contentsubtype === 'Audio'
            ? <i className="fas fa-volume-up" />
            : <i className="fas fa-play" />}
        </div>
      </a>
      <div>
        <ul className="topics custom-text-list feature-content-topic-list">
          {row.topics.map((topic) => (
            <li key={`${row.id}-topic-${topic.id}`}>
              <a href={topic.url} className="table-content-link">
                <button type="button" className="button--rounded">
                  {topic.title}
                </button>
              </a>
            </li>
          ))}
        </ul>
        <h3><a href={row.url}>{row.title}</a></h3>
        {row.subtitle && (
          <p className="short-description" dangerouslySetInnerHTML={{ __html: row.subtitle }} />
        )}
        <p className="article-authors">
          {row.authors.map((author) => (
            <a key={`${row.id}-author-${author.id}`} href={author.url}>
              {author.title}
            </a>
          ))}
        </p>
        {row.publishing_date && (
          <p className="date">
            {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
          </p>
        )}
      </div>
    </article>
  );
}

MultimediaSeriesListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      type: PropTypes.string,
      value: PropTypes.any,
    })),
    contentsubtype: PropTypes.string,
    id: PropTypes.number,
    image_hero_url: PropTypes.string,
    publishing_date: PropTypes.string,
    subtitle: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string,
  }).isRequired,
};

export default MultimediaSeriesListing;
