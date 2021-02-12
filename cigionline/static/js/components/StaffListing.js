import PropTypes from 'prop-types';
import React from 'react';

function StaffListing(props) {
  const { row } = props;

  return (
    <article className="staff-listing">
      <div class="name-container">
        <a class="name" href="{ row.url }">{ row.title }</a>
        <div class="position">{ row.position }</div>
      </div>
      <p className="article-type">{row.contentsubtype}</p>
      <h2 className="article-title"><a href={row.url}>{row.title}</a></h2>
      <p className="article-date">
        {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
      </p>
      <p className="article-authors">
        {row.authors.map((author) => (
          <a key={`${row.id}-${author.id}`} href={author.url}>
            {author.title}
          </a>
        ))}
      </p>
    </article>
  );
}

StaffListing.propTypes = {
  row: PropTypes.shape({
    email: PropTypes.string,
    phone_number: PropTypes.string,
    position: PropTypes.string,
    title: PropTypes.string.isRequired,
    url: PropTypes.string,
    id: PropTypes.number,
  }).isRequired,
};

export default StaffListing;
