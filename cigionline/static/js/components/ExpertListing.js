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
            <div className="img-wrapper" style={{ 'background-image': `url('${row.image_square_url}')` }} />
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
          <div className="table-recent-activity">
            <span className="table-icon icon-opinion">
              <i className="fal fa-comment-dots" />
            </span>
            <a href="#" className="table-title-link">
              Can the Digital Economy Survive in a Splinternet?
            </a>
          </div>
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
    position: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
};

export default ExpertListing;
