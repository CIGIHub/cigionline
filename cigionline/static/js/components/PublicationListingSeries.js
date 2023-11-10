import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/PublicationListingSeries.scss';

function PublicationListingSeries(props) {
  const { row } = props;

  /* eslint-disable react/no-danger */
  return (
    <article className="publication-listing-series simple-listing">
      <ul className="topics custom-text-list feature-content-topic-list">
        {row.topics.map((topic) => (
          <li key={`${row.id}-topic-${topic.id}`}>
            <a href={topic.url} className="table-content-link">
              {topic.title}
            </a>
          </li>
        ))}
      </ul>
      <h3><a href={row.url}>{row.title}</a></h3>
      {row.short_description && (
        <p className="short-description" dangerouslySetInnerHTML={{ __html: row.short_description }} />
      )}
      <p className="article-authors">
        {row.authors.map((author) => (
          <a key={`${row.id}-author-${author.id}`} href={author.url}>
            {author.title}
          </a>
        ))}
      </p>
      {row.publishing_date && (
        <p className="date">
          {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
        </p>
      )}
      {row.pdf_download && (
        <a href={row.pdf_download} className="button-action button-square track-cta" data-cta="pub-pdf">
          <i className="fa fas fa-download" />
        </a>
      )}
    </article>
  );
}

PublicationListingSeries.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      type: PropTypes.string,
      value: PropTypes.any,
    })),
    id: PropTypes.number,
    pdf_download: PropTypes.string,
    publishing_date: PropTypes.string,
    short_description: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string,
  }).isRequired,
};

export default PublicationListingSeries;
