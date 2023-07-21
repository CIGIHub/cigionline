import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';
import CardTextMore from './CardTextMore';

function MediaListing(props) {
  const { row } = props;

  return (
    <tr>
      <td className="search-table__results__row__title">
        <div className="table-mobile-text search-table__results__row__title--mobile">
          Title
        </div>
        <div className="table-infos-wrapper">
          <span className="table-icon icon-opinion">
            <i className="fal fa-bullhorn" />
          </span>
          <div className="table-infos">
            <a href={row.url} className="table-title-link">
              {row.title}
            </a>
            {row.publishing_date && (
              <div className="table-infos-meta">
                {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
              </div>
            )}
          </div>
        </div>
      </td>
      <td className="search-table__results__row__authors">
        <div className="table-mobile-text">
          Author
        </div>
        <div className="table-content">
          <ul className="custom-text-list author-list">
            {row.cigi_people_mentioned.map((author) => (
              <li key={`${row.id}-author-${author.id}`}>
                <a href={author.url} className="table-content-link table-content-link-black">
                  {author.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td className="search-table__results__row__type">
        <div className="table-mobile-text">
          Type
        </div>
        <div className="table-content">
          {row.contentsubtype}
        </div>
      </td>
      <td className="search-table__results__row__topics">
        <div className="table-mobile-text">
          Topic
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td className="search-table__results__row__more">
        <div className="table-mobile-text">
          {' '}
        </div>
        <CardTextMore
          title={row.title}
          type="Opinion"
          url={row.url}
        />
      </td>
    </tr>
  );
}

MediaListing.propTypes = {
  row: PropTypes.shape({
    cigi_people_mentioned: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    contentsubtype: PropTypes.string,
    id: PropTypes.number,
    publishing_date: PropTypes.string,
    title: PropTypes.string,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string,
  }).isRequired,
};

export default MediaListing;
