import React from 'react';
import PropTypes from 'prop-types';

const ExpertSearchResultCard = (props) => {
  const { row } = props;
  return (
    <article className="card__container card--small card--small--expert card--expert">
      <div className="card--small--expert__top">
        <div className="d-flex align-items-center pb-3">
          <div className="card__image card__image--portrait--circle">
            <a href="{{ url }}">
              <div className="img-wrapper">
                <img alt="" src={row.image_square_url} />
              </div>
            </a>
          </div>
          <div>
            <h3 className="card__text__title">
              <a href={row.url}>{row.title}</a>
            </h3>
            {row.board_position && (
              <div className="card--expert__board-position">
                {row.board_position}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card--small--expert__bottom meta__text">
        <h4>Expertise</h4>
        <ul className="card--expert__bottom__expertise-list">
          {row.expertise_list.length > 0
            && row.expertise_list.map((expertise) => (
              <li key={expertise}>{expertise}</li>
            ))}
        </ul>
        <div className="card--expert__social">
          <ul>
            {row.twitter_username && (
              <li>
                <div>Twitter</div>
                <a
                  href={`https://twitter.com/${row.twitter_username}`}
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  {row.twitter_username}
                </a>
              </li>
            )}

            {row.linkedin_username && (
              <li>
                <div>linkedin</div>
                <a
                  href={`https://linkedin.com/${row.linkedin_username}`}
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  {row.linkedin_username}
                </a>
              </li>
            )}
          </ul>
        </div>
      </div>
    </article>
  );
};

ExpertSearchResultCard.propTypes = {
  row: PropTypes.shape({
    id: PropTypes.number,
    image_square_url: PropTypes.string,
    title: PropTypes.string.isRequired,
    board_position: PropTypes.string,
    expertise_list: PropTypes.arrayOf(PropTypes.string),
    twitter_username: PropTypes.string,
    linkedin_username: PropTypes.string,
    url: PropTypes.string.isRequired,
  }).isRequired,
};

export default ExpertSearchResultCard;
