import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function PublicationListingSimple(props) {
  const { row } = props;

  return (
    <article className="simple-listing">
      <p className="article-type">{row.publication_type.title}</p>
      <h2 className="article-title"><a href={row.url}>{row.title}</a></h2>
      <p className="article-date">
        {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
      </p>
      <p className="article-authors">
        {row.authors.map((author) => (
          <a key={`${row.id}-${author.author.id}`} href={author.author.url}>
            {author.author.title}
          </a>
        ))}
      </p>
    </article>
  );
}

PublicationListingSimple.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      type: PropTypes.string,
      value: PropTypes.any,
    })),
    id: PropTypes.number,
    publication_type: PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
    }),
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    url: PropTypes.string,
  }).isRequired,
};

export default PublicationListingSimple;
