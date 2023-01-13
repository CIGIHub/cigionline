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
    },
    Multimedia: {
      icon: 'fa-play',
    },
    'Multimedia Series': {
      icon: 'fa-play',
    },
    Audio: {
      icon: 'fa-headphones',
    },
    Publication: {
      icon: 'fa-file-alt',
    },
    'Publication Series': {
      icon: 'fa-file-alt',
    },
    Person: {
      icon: 'fa-user',
    },
    Topic: {
      icon: 'fa-tag',
    },
    Activity: {
      icon: 'fa-clipboard-list',
    },
    Opinion: {
      icon: 'fa-comment-alt',
    },
    'Opinion Series': {
      icon: 'fa-comment-alt',
    },
  };

  /* eslint-disable react/no-danger */
  return (
    <tr className="search-result-listing">
      <td className="search-table__results__row__title">
        <div>
          <i
            className={`fal ${
              contentTypes.includes(row.contenttype)
                ? iconClasses[row.contenttype]?.icon
                : 'fa-file'
            }`}
          />
          <div>
            <a href={row.url}>
              {row.title}
              {row.elevated && <i className="fal fa-bookmark elevate-bookmark" />}
            </a>
            {row.publishing_date && (
              <div className="search-table__results__row__date">
                {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_MED)}
              </div>
            )}
          </div>
        </div>
      </td>
      <td className="search-table__results__row__content-type">
        {row.contentsubtype && (
          <>{row.contentsubtype}</>
        )}
        {!row.contentsubtype && row.contenttype && (
          <>{row.contenttype}</>
        )}
      </td>
      <td className="search-table__results__row__authors">
        {row.authors && (
          <ul className="custom-text-list">
            {row.authors.map((author) => (
              <li key={`${row.id}-author-${author.id}`}>
                <a href={author.url}>{author.title}</a>
              </li>
            ))}
          </ul>
        )}
      </td>
      <td className="search-table__results__row__topics">
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
      <td className="search-table__results__row__download">
        {row.pdf_download && (
          <a href={row.pdf_download} className="download">
            <i className="fal fa-arrow-to-bottom" />
          </a>
        )}
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
    pdf_download: PropTypes.string,
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
