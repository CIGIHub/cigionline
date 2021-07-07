import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/SearchResultListing.scss';

function SearchResultListing(props) {
  const { row } = props;

  /* eslint-disable react/no-danger */
  return (
    <article className="search-result-listing">
      {row.contenttype === 'Event' && (
        <span className="table-icon icon-event">
          <i className="fal fa-calendar-alt" />
        </span>
      )}
      {row.contenttype === 'Multimedia' && row.contentsubtype === 'Video' && (
        <span className="table-icon icon-multimedia">
          <i className="fal fa-play" />
        </span>
      )}
      {row.contenttype === 'Multimedia Series'
        && row.contentsubtype === 'Multimedia Series' && (
        <span className="table-icon icon-multimedia">
          <i className="fal fa-play" />
        </span>
      )}
      {row.contenttype === 'Multimedia' && row.contentsubtype === 'Audio' && (
        <span className="table-icon icon-multimedia">
          <i className="fal fa-headphones" />
        </span>
      )}
      {row.contenttype === 'Publication'
        || (row.contenttype === 'Publication Series' && (
          <span className="table-icon icon-publication">
            <i className="fal fa-file-alt" />
          </span>
        ))}
      {row.contenttype === 'Person' && (
        <span className="table-icon icon-person">
          <i className="fal fa-user" />
        </span>
      )}
      {row.contenttype === 'Topic' && (
        <span className="table-icon icon-topic">
          <i className="fal fa-copy" />
        </span>
      )}
      {['Opinion', 'CIGI in the News', 'Op-Eds', 'News Releases'].includes(
        row.contenttype,
      ) && (
        <span className="table-icon icon-opinion">
          <i className="fal fa-comment-dots" />
        </span>
      )}
      <div className="search-result-content">
        <ul className="topics custom-text-list feature-content-topic-list">
          {row.topics
            && row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
        </ul>
        <h2 className="search-result-title">
          <a href={row.url}>
            {row.title}
            {row.elevated && <i className="fal fa-bookmark elevate-bookmark" />}
          </a>
        </h2>
        {row.publishing_date && (
          <div className="search-result-meta">
            {DateTime.fromISO(row.publishing_date).toLocaleString(
              DateTime.DATE_FULL,
            )}
          </div>
        )}
        {row.contentsubtype && (
          <div className="search-result-meta">{row.contentsubtype}</div>
        )}
        {row.authors && (
          <ul className="custom-text-list search-result-meta">
            {row.authors.map((author) => (
              <li key={`${row.id}-author-${author.id}`}>
                <a href={author.url}>{author.title}</a>
              </li>
            ))}
          </ul>
        )}
        {row.highlights && (
          <p className="search-result-highlight">
            {row.highlights.map((highlight, index) => (
              <span
                key={`${row.id}-highlight-${index}`}
                dangerouslySetInnerHTML={{ __html: highlight }}
              />
            ))}
          </p>
        )}
      </div>
    </article>
  );
}

SearchResultListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contentsubtype: PropTypes.string,
    contenttype: PropTypes.string,
    elevated: PropTypes.bool,
    highlights: PropTypes.arrayOf(PropTypes.string),
    id: PropTypes.number,
    publishing_date: PropTypes.string,
    title: PropTypes.string,
    topics: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    url: PropTypes.string,
  }).isRequired,
};

export default SearchResultListing;
