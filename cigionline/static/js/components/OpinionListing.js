import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function OpinionListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="6">
        <div className="table-mobile-text">
          Title
        </div>
        <div className="table-infos-wrapper">
          <span className="table-icon icon-opinion">
            <i className="fal fa-comment-dots" />
          </span>
          <div className="table-infos">
            <a href={row.url} className="table-title-link">
              {row.title}
            </a>
            <div className="table-infos-date">
              {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
            </div>
          </div>
        </div>
      </td>
      <td colSpan="3">
        <div className="table-mobile-text">
          Author
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.authors.map((author) => (
              <li key={`${row.id}-${author.author.id}`}>
                <a href={author.author.url} className="table-content-link table-content-link-black">
                  {author.author.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td colSpan="3">
        <div className="table-mobile-text">
          Topic
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.topics.map((topic) => (
              <li key={topic.id}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
    </tr>
  );
}

OpinionListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      type: PropTypes.string,
      value: PropTypes.any,
    })),
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

export default OpinionListing;
