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
            {row.publishing_date && (
              <div className="table-infos-meta">
                {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
              </div>
            )}
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
              <li key={`${row.id}-topic-${topic.id}`}>
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
              <li key={`${row.id}-city`} className="table-infos-meta">{row.location_city}</li>
            )}
            {!!row.location_country && (
              <li key={`${row.id}-country`} className="table-infos-meta">{row.location_country}</li>
            )}
          </ul>
        </div>
      </td>
      <td colSpan="1">
        <div className="table-mobile-text" />
        <div className="table-content">
          {row.event_access === 0
            ? (
              <button type="button" className="button-action disabled" disabled>
                Private
              </button>
            ) : (
              row.multimedia_url ? (
                <a href={row.multimedia_url} className="button-action" data-cta="event-watch">
                  <i className="fas fa-play" />
                  Watch
                </a>
              ) : (
                !!row.registration_url
                && DateTime.fromISO(row.publishing_date) > DateTime.local().startOf('day')
                && (
                  <a href={row.registration_url} className="button-action" data-cta="event-rsvp">
                    <i className="fal fa-calendar-alt" />
                    RSVP
                  </a>
                )
              )
            )}
        </div>
      </td>
    </tr>
  );
}

EventListing.propTypes = {
  row: PropTypes.shape({
    event_access: PropTypes.number,
    id: PropTypes.number,
    location_city: PropTypes.string,
    location_country: PropTypes.string,
    multimedia_url: PropTypes.string,
    publishing_date: PropTypes.string,
    registration_url: PropTypes.string,
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
