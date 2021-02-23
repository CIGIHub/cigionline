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
      <td colSpan="4" />
      <td colSpan="4" />
    </tr>
  );
}

ExpertListing.propTypes = {
  row: PropTypes.shape({
    id: PropTypes.number,
    image_square_url: PropTypes.string,
    position: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
};

export default ExpertListing;
