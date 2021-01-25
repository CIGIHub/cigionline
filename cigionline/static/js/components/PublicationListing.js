import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function PublicationListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="6">
        <div className="table-mobile-text">
          Title
        </div>
        <div className="table-infos-wrapper">
          <span className="table-icon icon-publication">
            <i className="fal fa-file-alt" />
          </span>
          <div className="table-infos">
            <a href={row.url} className="table-title-link">
              {row.title}
            </a>
            <div className="table-infos-meta">
              {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
            </div>
          </div>
        </div>
      </td>
      <td colSpan="2">
        <div className="table-mobile-text">
          Topic
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.topics.map((topic) => (
              <li key={topic.id}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td colSpan="3">
        <div className="table-mobile-text">
          Expert
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.authors.map((author) => (
              <li key={`${row.id}-${author.author.id}`}>
                <a href={author.author.url} className="table-content-link table-content-link-black">
                  {author.author.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td colSpan="0">
        <div className="table-mobile-text">
          PDF
        </div>
        <div className="table-content">
          {!!row.pdf_downloads.length && (
            <a href={row.pdf_downloads[0].value.url} className="table-btn-icon">
              <i className="fa fas fa-download" />
            </a>
          )}
        </div>
      </td>
    </tr>
  );
}

PublicationListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      type: PropTypes.string,
      value: PropTypes.any,
    })),
    id: PropTypes.number,
    pdf_downloads: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string,
      type: PropTypes.string,
      value: PropTypes.shape({
        button_text: PropTypes.string,
        url: PropTypes.string,
      }),
    })),
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string.isRequired,
  }).isRequired,
};

export default PublicationListing;
