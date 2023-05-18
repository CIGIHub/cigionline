import React from 'react';
import PropTypes from 'prop-types';

const PublicationSearchResultCard = (props) => {
  const { row } = props;
  return (
    <article className="card__container card--small card--small--publication">
      <div className="card__image">
        <a href={row.url}>
          <div className="img-wrapper">
            <img alt="" src={row.image_poster_url} />
          </div>
        </a>
      </div>
      <div className="card__text">
        {row.topics && (
          <ul className="card__text__topics custom-text-list">
            {row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
          </ul>
        )}
        <h3 className="card__text__title">
          <a href={row.url}>{row.title}</a>
        </h3>
        <div className="card__text__meta">
          <div>
            <ul className="custom-text-list card__text__people">
              {row.authors.slice(0, 3).map((author) => (
                <li key={`${row.id}-author-${author.id}`}>
                  <a href={author.url}>{author.title}</a>
                </li>
              ))}
              {row.authors.length > 3 && (
                <li key={`${row.id}-author-more`}>And more</li>
              )}
            </ul>
          </div>
          <button type="button" className="card__text__more">
            <a href={row.url}>
              <i className="far fa-ellipsis-h" />
            </a>
          </button>
        </div>
      </div>
    </article>
  );
};

PublicationSearchResultCard.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contentsubtype: PropTypes.string,
    id: PropTypes.number,
    image_poster_url: PropTypes.string,
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
  }).isRequired,
};

export default PublicationSearchResultCard;
