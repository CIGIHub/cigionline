import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/SearchResultListing.scss';

function SearchResultListing(props) {
  const { row } = props;

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
      {row.contenttype === 'Multimedia' && row.contentsubtype === 'Audio' && (
        <span className="table-icon icon-multimedia">
          <i className="fal fa-headphones" />
        </span>
      )}
      {row.contenttype === 'Publication' && (
        <span className="table-icon icon-publication">
          <i className="fal fa-file-alt" />
        </span>
      )}
      {['Opinion', 'CIGI in the News', 'Op-Eds', 'News Releases'].includes(row.contenttype) && (
        <span className="table-icon icon-opinion">
          <i className="fal fa-comment-dots" />
        </span>
      )}
      <div className="search-result-content">
        <ul className="topics custom-text-list feature-content-topic-list">
          {row.topics.map((topic) => (
            <li key={topic.id}>
              <a href={topic.url} className="table-content-link">
                {topic.title}
              </a>
            </li>
          ))}
        </ul>
        <h2 className="search-result-title">
          <a href={row.url}>{row.title}</a>
        </h2>
      </div>
    </article>
  );
}

SearchResultListing.propTypes = {
  row: PropTypes.shape({
    contentsubtype: PropTypes.string,
    contenttype: PropTypes.string,
    title: PropTypes.string,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string,
  }).isRequired,
};

export default SearchResultListing;
