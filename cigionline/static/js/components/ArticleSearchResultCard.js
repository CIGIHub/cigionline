import React from 'react';
import PropTypes from 'prop-types';
import { DateTime } from 'luxon';
import CardTextMore from './CardTextMore';

const ArticleSearchResultCard = (props) => {
  const { row } = props;
  return (
    <article className="card__container card--small card--small--landscape card--small--article">
      <div className="card__image">
        <a href={row.url}>
          <div className="img-wrapper">
            <img alt="" src={row.image_hero_url} />
          </div>
        </a>
      </div>
      <div className="card__text">
        <div>
          {row.publishing_date && (
            <time dateTime={row.publishing_date} className="card__text__date">
              {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_MED)}
            </time>
          )}
          <h3 className="card__text__title">
            <a href={row.url}>{row.title}</a>
          </h3>
        </div>
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
            <ul className="card__text__topics custom-text-list">
              {row.topics.map((topic) => (
                <li key={`${row.id}-topic-${topic.id}`}>
                  <a href={topic.url} className="table-content-link">
                    {topic.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <CardTextMore
            title={row.title}
            url={row.url}
            type="Opinion"
          />
        </div>
      </div>
    </article>
  );
};

ArticleSearchResultCard.propTypes = {
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
    image_hero_url: PropTypes.string,
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

export default ArticleSearchResultCard;
