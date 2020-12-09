import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function PublicationListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="6">
        <div className="table-mobile-text">
          Title
        </div>
        <div className="table-infos-wrapper">
          <span className="table-icon">
            <i className="fal fa-file-alt" />
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
      <td colSpan="2">
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
      <td colSpan="3">
        <div className="table-mobile-text">
          Expert
        </div>
      </td>
      <td colSpan="0">
        <div className="table-mobile-text">
          PDF
        </div>
      </td>
    </tr>
  );
}

PublicationListing.propTypes = {
  row: PropTypes.shape({
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

export default PublicationListing;
