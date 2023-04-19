import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/ArticleSeriesListing.scss';
import CardTextMore from './CardTextMore';

function ArticleSeriesListing(props) {
  const { row } = props;

  /* eslint-disable react/no-danger */
  return (
    <article
      className={`card__container card--large card--large--article-series card--large--article-series--full ${row.theme}`}
    >
      <div className="card__image">
        <a href={row.url} className="feature-content-image">
          <div className="img-wrapper poster">
            <img alt="" src={row.image_poster_url} />
          </div>
        </a>
      </div>
      <div className="card__text">
        <div>
          <h3 className="card__text__title">
            <a href={row.url}>{row.title}</a>
          </h3>
          <div className="card__text__description">
            <div dangerouslySetInnerHTML={{ __html: row.short_description }} />
          </div>
          <hr />
          <div className="card__text__contributors">
            <h4>Contributors</h4>
            <ul>
              {row.series_contributors.map((person) => (
                <li key={`${row.id}-contributor-${person.id}`}>
                  <a href={person.url}>
                    <span>{person.title}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div className="card__text__meta">
            <div>
              <ul className="card__text__topics custom-text-list">
                {row.topics.map((topic) => (
                  <li key={`${row.id}-topic-${topic.id}`}>
                    <a href={topic.url}>{topic.title}</a>
                  </li>
                ))}
              </ul>
            </div>
            <CardTextMore
              title={row.title}
              url={row.url}
              type="Opinion Series"
            />
          </div>
        </div>
      </div>
    </article>
  );
}

ArticleSeriesListing.propTypes = {
  row: PropTypes.shape({
    id: PropTypes.number,
    image_poster_caption: PropTypes.string,
    image_poster_url: PropTypes.string,
    series_contributors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    short_description: PropTypes.string,
    title: PropTypes.string,
    theme: PropTypes.string,
    topics: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    url: PropTypes.string,
  }).isRequired,
};

export default ArticleSeriesListing;
