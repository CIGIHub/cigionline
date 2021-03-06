import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/ArticleSeriesListing.scss';

function ArticleSeriesListing(props) {
  const { row } = props;

  /* eslint-disable react/no-danger */
  return (
    <article className="article-series-row">
      <div className="article-series-content">
        <ul className="custom-text-list article-series-topic-list">
          {row.topics.map((topic) => (
            <li key={topic.id}>
              <a href={topic.url} className="table-content-link">
                {topic.title}
              </a>
            </li>
          ))}
        </ul>
        <h2 className="article-series-title">
          <a href={row.url}>{row.title}</a>
        </h2>
        <div className="article-series-short-description" dangerouslySetInnerHTML={{ __html: row.short_description }} />
        <div className="article-series-contributors">
          <h3>Contributors</h3>
          <ul>
            {row.series_contributors.map((person) => (
              <li key={person.id}>
                <a href={person.url}>
                  {person.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <a href={row.url} className="article-series-image">
        <img src={row.image_poster_url} alt={row.image_poster_title} width="672" height="895" />
      </a>
    </article>
  );
}

ArticleSeriesListing.propTypes = {
  row: PropTypes.shape({
    image_poster_title: PropTypes.string,
    image_poster_url: PropTypes.string,
    series_contributors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    short_description: PropTypes.string,
    title: PropTypes.string,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string,
  }).isRequired,
};

export default ArticleSeriesListing;
