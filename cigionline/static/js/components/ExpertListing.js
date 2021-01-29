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
            <div className="img-wrapper" style={{ backgroundImage: `url('${row.image_square_url}')` }} />
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
            {row.expertise_list.map((expertise) => (
              <li className="table-list-item" key={expertise.replace(' ', '_')}>
                {expertise}
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
          {row.latest_activity_json && (
            <div className="table-recent-activity">
              {['Opinion', 'Op-Ed', 'Interview'].includes(row.latest_activity_json.contenttype) && (
                <span className="table-icon icon-opinion">
                  <i className="fal fa-comment-dots" />
                </span>
              )}
              {['News Release', 'CIGI in the News'].includes(row.latest_activity_json.contenttype) && (
                <span className="table-icon icon-media">
                  <i className="fal fa-bullhorn" />
                </span>
              )}
              {row.latest_activity_json.contenttype === 'Publication' && (
                <span className="table-icon icon-publication">
                  <i className="fal fa-file-alt" />
                </span>
              )}
              {row.latest_activity_json.contenttype === 'Multimedia' && (
                <span className="table-icon icon-multimedia">
                  {row.latest_activity_json.contentsubtype === 'Video' && (
                    <i className="fal fa-play" />
                  )}
                  {row.latest_activity_json.contentsubtype === 'Audio' && (
                    <i className="fal fa-headphones" />
                  )}
                </span>
              )}
              {row.latest_activity_json.contenttype === 'Event' && (
                <span className="table-icon icon-event">
                  <i className="fal fa-calendar-alt" />
                </span>
              )}
              <a href={row.latest_activity_json.url} className="table-title-link">
                {row.latest_activity_json.title}
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
    expertise_list: PropTypes.arrayOf(PropTypes.string),
    id: PropTypes.number,
    image_square_url: PropTypes.string,
    latest_activity_json: PropTypes.shape({
      contentsubtype: PropTypes.string,
      contenttype: PropTypes.string,
      title: PropTypes.string,
      url: PropTypes.string,
    }),
    position: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
};

export default ExpertListing;
