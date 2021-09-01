import PropTypes from 'prop-types';
import React from 'react';
import '../../css/components/StaffListing.scss';

function StaffListing(props) {
  const { row } = props;

  return (
    <article className="staff-listing">
      <div className="name-container">
        {row.has_bio ? (
          <a className="name" href={row.url}>{row.title}</a>
        ) : (
          <div className="name">{row.title}</div>
        )}
        <div className="position">{row.position}</div>
      </div>
      <div className="contact-container">
        {row.phone_number && (
          <div>
            <i className="fas fa-phone" />
            <span>{row.phone_number}</span>
          </div>
        )}
        {row.email && (
          <div>
            <i className="fas fa-envelope" />
            <span><a href={`mailto:${row.email}`}>{row.email}</a></span>
          </div>
        )}
      </div>
    </article>
  );
}

StaffListing.propTypes = {
  row: PropTypes.shape({
    email: PropTypes.string,
    has_bio: PropTypes.bool,
    phone_number: PropTypes.string,
    position: PropTypes.string,
    title: PropTypes.string.isRequired,
    url: PropTypes.string,
    id: PropTypes.number,
  }).isRequired,
};

export default StaffListing;
