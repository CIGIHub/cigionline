import PropTypes from 'prop-types';
import React from 'react';

function ResearchContentListing(props) {
  const { row } = props;

  return (
    <article className="card__container card--small card--small--poster">
      <div className="card__image">
        <a href={row.url} className="feature-content-image">
          <div className="img-wrapper">
            <img alt={row.image_alt} src={row.image_poster_url} />
          </div>
        </a>
      </div>
      <div className="card__text">
        <h3 className="card__text__title {{ additional_classes }}">
          <a href={row.url}>{row.title}</a>
        </h3>
        <div className="card__text__meta">
          <div>
            <ul className="custom-text-list card__text__people">
              {row.authors.map((author) => (
                <li key={`${row.id}-author-${author.id}`}>
                  <a href={author.url}>{author.title}</a>
                </li>
              ))}
            </ul>
            <ul className="card__text__topics custom-text-list {{ additional_class_names }} {% if topics|length > 2 %}hide-topics{% endif %}">
              {row.topics &&
                row.topics.map((topic) => (
                  <li key={`${row.id}-topic-${topic.id}`}>
                    <a href={topic.url}>{topic.title}</a>
                  </li>
                ))}
            </ul>
          </div>
          <button type="button" className="card__text__more">
            <a href="{{ url }}">
              <i className="far fa-ellipsis-h" />
            </a>
          </button>
        </div>
      </div>
    </article>
  );
}

ResearchContentListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contentsubtype: PropTypes.string,
    contenttype: PropTypes.string,
    id: PropTypes.number,
    pdf_download: PropTypes.string,
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    url: PropTypes.string.isRequired,
    image_poster_url: PropTypes.string,
    image_alt: PropTypes.string,
  }).isRequired,
};

export default ResearchContentListing;
