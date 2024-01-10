import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function MediaListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="6">
        <div className="table-mobile-text">
          Title
        </div>
        <div className="table-infos-wrapper">
          <span className="table-icon icon-media">
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
      <td colSpan="1">
        <div className="table-mobile-text">
          Expert
        </div>
        <div className="table-content">
          <ul className="custom-text-list author-list">
            {row.cigi_people_mentioned.map((person) => (
              <li key={`${row.id}-person-${person.id}`}>
                <a href={person.url} className="table-content-link table-content-link-black">
                  {person.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td colSpan="1">
        <div className="table-mobile-text">
          Type
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            <li key={`${row.id}-contentsubtype`} className="table-infos-meta">
              {row.contentsubtype}
            </li>
          </ul>
        </div>
      </td>
      <td colSpan="4">
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
