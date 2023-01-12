import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/SearchResultListingRow.scss';

function SearchResultListingRow(props) {
  const { row } = props;
  const highlights = row.highlights.reduce((acc, curr, i, arr) => {
    const accLength = [...acc, curr].reduce((a, b) => a + b.length, 0);
    if (accLength > 350) {
      arr.splice(1);
      return [...acc, curr.substring(0, accLength - 350)];
    }
    return [...acc, curr];
  }, []);
  const contentTypes = [
    'Opinion',
    'Opinion Series',
    'Publication',
    'Publication Series',
    'Multimedia',
    'Multimedia Series',
    'Event',
    'Activity',
    'Person',
    'Topic',
  ];
  const iconClasses = {
    Event: {
      icon: 'fa-calendar-alt',
      className: 'icon-event',
    },
    Multimedia: {
      icon: 'fa-play',
      className: 'icon-multimedia',
    },
    'Multimedia Series': {
      icon: 'fa-play',
      className: 'icon-multimedia',
    },
    Audio: {
      icon: 'fa-headphones',
      className: 'icon-multimedia',
    },
    Publication: {
      icon: 'fa-file-alt',
      className: 'icon-publication',
    },
    'Publication Series': {
      icon: 'fa-file-alt',
      className: 'icon-publication',
    },
    Person: {
      icon: 'fa-user',
      className: 'icon-person',
    },
    Topic: {
      icon: 'fa-tag',
      className: 'icon-topic',
    },
    Activity: {
      icon: 'fa-clipboard-list',
      className: 'icon-activity',
    },
    Opinion: {
      icon: 'fa-comment-alt',
      className: 'icon-opinion',
    },
    'Opinion Series': {
      icon: 'fa-comment-alt',
      className: 'icon-opinion',
    },
  };

  /* eslint-disable react/no-danger */
  return (
    <tr className="search-result-listing">
      <td>
        <span
          className={`table-icon ${
            contentTypes.includes(row.contenttype)
              ? iconClasses[row.contenttype]?.className
              : 'icon-basic-page'
          }`}
        >
          <i
            className={`fal ${
              contentTypes.includes(row.contenttype)
                ? iconClasses[row.contenttype]?.icon
                : 'fa-file'
            }`}
          />
        </span>
        <a href={row.url}>
          {row.title}
          {row.elevated && <i className="fal fa-bookmark elevate-bookmark" />}
        </a>
      </td>
      <td>
        {row.contentsubtype && (
          <div className="search-result-meta">{row.contentsubtype}</div>
        )}
        {!row.contentsubtype && row.contenttype && (
          <div className="search-result-meta">{row.contenttype}</div>
        )}
      </td>
      <td>
        {row.authors && (
          <ul className="custom-text-list search-result-meta">
            {row.authors.map((author) => (
              <li key={`${row.id}-author-${author.id}`}>
                <a href={author.url}>{author.title}</a>
              </li>
            ))}
          </ul>
        )}
      </td>
      <td>
        <ul className="topics custom-text-list feature-content-topic-list">
          {row.topics &&
            row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
        </ul>
      </td>
    </tr>
  );
}

SearchResultListingRow.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      })
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
      })
    ),
    url: PropTypes.string,
  }).isRequired,
};

export default SearchResultListingRow;
