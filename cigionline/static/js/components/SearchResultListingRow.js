import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/SearchResultListingRow.scss';

function SearchResultListingRow(props) {
  const { row } = props;
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
      icon: 'fa-comment-alt-lines',
    },
    'Opinion Series': {
      icon: 'fa-comment-alt',
    },
  };

  return (
    <tr className="search-result-listing">
      <td className="search-table__results__row__title">
        <div className="search-table__results__row__title--mobile">Title</div>
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
              {row.elevated && (
                <i className="fal fa-bookmark elevate-bookmark" />
              )}
            </a>
            {row.publishing_date && (
              <time
                dateTime={row.publishing_date}
                className="search-table__results__row__date"
              >
                {DateTime.fromISO(row.publishing_date).toLocaleString(
                  DateTime.DATE_MED,
                )}
              </time>
            )}
          </div>
        </div>
      </td>
      <td className="search-table__results__row__type">
        <div className="search-table__results__row__title--mobile">
          Content Type
        </div>
        {row.contentsubtype && <>{row.contentsubtype}</>}
        {!row.contentsubtype && row.contenttype && <>{row.contenttype}</>}
      </td>
      <td className="search-table__results__row__authors">
        <div className="search-table__results__row__title--mobile">Author</div>
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
        <div className="search-table__results__row__title--mobile">Topic</div>
        <ul className="search-table__results__row__topics__list">
          {row.topics &&
            row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  <button type="button" className="button--topic button--rounded">
                    {topic.title}
                  </button>
                </a>
              </li>
            ))}
        </ul>
      </td>
      {row.pdf_download && (
        <td className="search-table__results__row__download">
          <>
            <div className="search-table__results__row__title--mobile">PDF</div>
            <a href={row.pdf_download} className="download">
              <i className="fal fa-arrow-to-bottom" />
            </a>
          </>
        </td>
      )}
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
      }),
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
      }),
    ),
    url: PropTypes.string,
  }).isRequired,
};

export default SearchResultListingRow;
