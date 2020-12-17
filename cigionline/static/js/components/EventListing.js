import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function EventListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="6">
        <div className="table-mobile-text">
          Title
        </div>
        <div className="table-infos-wrapper">
          <span className="table-icon icon-event">
            <i className="fal fa-calendar-alt" />
          </span>
          <div className="table-infos">
            <a href={row.url} className="table-title-link">
              {row.title}
            </a>
            <div className="table-infos-meta">
              {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
            </div>
          </div>
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
      <td colSpan="2">
        <div className="table-mobile-text">
          Location
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {!!row.location_city && (
              <li className="table-infos-meta">{row.location_city}</li>
            )}
            {!!row.location_country && (
              <li className="table-infos-meta">{row.location_country}</li>
            )}
          </ul>
        </div>
      </td>
    </tr>
  );
}

EventListing.propTypes = {
  row: PropTypes.shape({
    id: PropTypes.number,
    location_city: PropTypes.string,
    location_country: PropTypes.string,
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

export default EventListing;
