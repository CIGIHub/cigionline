import PropTypes from 'prop-types';
import React from 'react';

function ExpertListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="3">
        <div className="table-mobile-text">
          Name
        </div>
        <div className="table-infos-wrapper">
          <a href={row.url} className="table-thumbnail-photo">
            <div className="img-wrapper" style={{ backgroundImage: `url(${row.image_square_url})` }} />
          </a>
          <div className="table-infos">
            <a href={row.url} className="table-title-link">
              {row.title}
            </a>
            <div className="table-infos-function">
              {row.position}
            </div>
          </div>
        </div>
      </td>
      <td colSpan="4">
        <div className="table-mobile-text">
          Expertise
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.expertise.map((expertiseItem) => (
              <li key={`${row.id}-${expertiseItem}`} className="table-list-item">
                {expertiseItem}
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td colSpan="4">
        <div className="table-mobile-text">
          Recent Activity
        </div>
        <div className="table-content">
          {row.latest_activity && (
            <div className="table-recent-activity">
              {row.latest_activity.contenttype === 'Event' && (
                <span className="table-icon icon-event">
                  <i className="fal fa-calendar-alt" />
                </span>
              )}
              {row.latest_activity.contenttype === 'Multimedia' && row.latest_activity.contentsubtype === 'Video' && (
                <span className="table-icon icon-multimedia">
                  <i className="fal fa-play" />
                </span>
              )}
              {row.latest_activity.contenttype === 'Multimedia' && row.latest_activity.contentsubtype === 'Audio' && (
                <span className="table-icon icon-multimedia">
                  <i className="fal fa-headphones" />
                </span>
              )}
              {row.latest_activity.contenttype === 'Publication' && (
                <span className="table-icon icon-publication">
                  <i className="fal fa-file-alt" />
                </span>
              )}
              {row.latest_activity.contenttype === 'Essay Series' && (
                <span className="table-icon icon-opinion">
                  <i className="fal fa-comment-dots" />
                </span>
              )}
              {row.latest_activity.contenttype === 'Opinion' && ['Opinion', 'Interviews', 'Op-Eds', 'Essays'].includes(row.latest_activity.contentsubtype) && (
                <span className="table-icon icon-opinion">
                  <i className="fal fa-comment-dots" />
                </span>
              )}
              {row.latest_activity.contenttype === 'Opinion' && ['CIGI in the News', 'News Releases'].includes(row.latest_activity.contentsubtype) && (
                <span className="table-icon icon-media">
                  <i className="fal fa-bullhorn" />
                </span>
              )}
              <a href={row.latest_activity.url} className="table-title-link">
                {row.latest_activity.title}
              </a>
            </div>
          )}
        </div>
      </td>
    </tr>
  );
}

ExpertListing.propTypes = {
  row: PropTypes.shape({
    expertise: PropTypes.arrayOf(PropTypes.string),
    id: PropTypes.number,
    image_square_url: PropTypes.string,
    latest_activity: PropTypes.any,
    position: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
};

export default ExpertListing;
