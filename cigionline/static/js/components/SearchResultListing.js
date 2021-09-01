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
      {row.contenttype === 'Multimedia' && row.contentsubtype !== 'Audio' && (
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
      {['Publication', 'Publication Series'].includes(row.contenttype) && (
        <span className="table-icon icon-publication">
          <i className="fal fa-file-alt" />
        </span>
      )}
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
      {row.contenttype === 'Opinion Series' && (
        <span className="table-icon icon-opinion-series">
          <i className="fal fa-comments" />
        </span>
      )}
      {row.contenttype === 'Activity' && (
        <span className="table-icon icon-activity">
          <i className="fal fa-file-search" />
        </span>
      )}
      {!row.contenttype && !row.contentsubtype && (
        <span className="table-icon icon-basic-page">
          <i className="fal fa-file" />
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
        {!row.contentsubtype && row.contenttype && (
          <div className="search-result-meta">{row.contenttype}</div>
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
        {row.highlights.length > 0 && (
          <p className="search-result-highlight">
            {row.highlights
              .reduce((acc, curr, i, arr) => {
                const accLength = [...acc, curr].reduce((a, b) => a + b.length, 0);
                if (accLength > 350) {
                  arr.splice(1);
                  return [...acc, curr.substring(0, accLength - 350)];
                }
                return [...acc, curr];
              }, [])
              .map((highlight, index) => (
                <span
                  key={`${row.id}-highlight-${index}`}
                  dangerouslySetInnerHTML={{ __html: highlight }}
                />
              ))}
          </p>
        )}
        {row.highlights.length === 0 && row.snippet && (
          <p className="search-result-highlight" maxLength="100">
            <span>{row.snippet}</span>
          </p>
        )}
        {row.search_result_description ? (
          <p className="search-result-highlight">
            {row.search_result_description}
          </p>
        ) : row.contenttype === 'Topic' ? (
          <p className="search-result-highlight">
            View results related to this topic.
          </p>
        ) : ''}
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
    snippet: PropTypes.string,
    contentsubtype: PropTypes.string,
    contenttype: PropTypes.string,
    elevated: PropTypes.bool,
    highlights: PropTypes.arrayOf(PropTypes.string),
    id: PropTypes.number,
    publishing_date: PropTypes.string,
    search_result_description: PropTypes.string,
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
