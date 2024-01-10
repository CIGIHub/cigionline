import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/MultimediaListing.scss';

function MultimediaListing(props) {
  const { row } = props;

  return (
    <div className="col multimedia-list-col">
      <a href={row.url} className="multimedia-card-image">
        <div className="img-wrapper" style={{ backgroundImage: `url(${row.image_hero_url})` }} />
        <div className="multimedia-image-type">
          {row.contentsubtype === 'Audio' ? (
            <i className="fas fa-volume-up" />
          ) : (
            <i className="fas fa-play" />
          )}
        </div>
      </a>
      <ul className="custom-text-list multimedia-card-topic-list">
        {row.topics.map((topic) => (
          <li key={`${row.id}-topic-${topic.id}`}>
            <a href={topic.url} className="table-content-link">
              {topic.title}
            </a>
          </li>
        ))}
      </ul>
      <p className="multimedia-card-title">
        <a href={row.url}>
          {row.title}
        </a>
      </p>
      <ul className="custom-text-list multimedia-card-speakers-list">
        {row.authors.slice(0, 3).map((author) => (
          <li key={`${row.id}-author-${author.id}`}>
            <a href={author.url}>
              {author.title}
            </a>
          </li>
        ))}
        {row.authors.length > 3 && (
          <li key={`${row.id}-author-more`}>And more</li>
        )}
      </ul>
      {row.publishing_date && (
        <p className="multimedia-card-date">
          {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
        </p>
      )}
    </div>
  );
}

MultimediaListing.propTypes = {
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
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string.isRequired,
  }).isRequired,
};

export default MultimediaListing;
