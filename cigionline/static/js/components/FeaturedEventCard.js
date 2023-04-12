import { DateTime } from 'luxon';
import React, { useState, useEffect } from 'react';

import '../../css/components/FeaturedEventCard.scss';

const FeaturedEventCard = (props) => {
  const { row } = props;
  const today = DateTime.now();

  const evaluateLive = (start, end) => {
    return Date.now() / 1000 >= start && Date.now() / 1000 <= end;
  };
  const [isLive, setIsLive] = useState(evaluateLive(row.start_utc, row.end_utc));

  useEffect(() => {
    const interval = setInterval(() => {
      setIsLive(evaluateLive(row.start_utc, row.end_utc));
    }, 1000);
    return () => {
      clearInterval(interval);
    };
  }, [isLive]);

  return (
    <div className="swiper-slide">
      <div className="col col-12">
        <article className={`card__container card--large card--large--event--landing card--event ${row.event_access === 'Private' && 'is_private'}`}>
          <div className="row card--event__container">
            <div className="col-md-4">
              <div className="card__text">
                <div className="row card--event__top">
                  {today < row.date && (
                    <div className="card--event--upcoming-label">
                      Upcoming Event -
                      {' '}
                      {row.date}
                    </div>
                  )}
                  {
                    isLive && (
                      <div className="card--event--live-label">
                        <i className="fas fa-podcast"></i>Live
                      </div>
                    )
                  }
                  <h3 className="card__text__title card--event__title">
                    <a href={row.url}>{row.title}</a>
                  </h3>
                  <div className="card--event__info">
                    <time dateTime="" className="card--event__time">
                      <div>{ row.date }</div>
                      <div>
                        {row.time }
                        {row.end_date && ` - ${row.end_time}`}
                        {' '}
                        {row.time_zone_label}
                      </div>
                    </time>
                    <div className="card--event__type">
                      {row.event_access ? 'Public ' : 'Private '}
                      Event
                      {row.event_type && (
                        <span>
                          :
                          {' '}
                          {row.event_type}
                        </span>
                      )}
                      {row.event_format && (
                        <span>
                          {' '}
                          (
                          {row.event_format}
                          )
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="card--event__bottom">
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
                    <div className="card__cta">
                      {row.event_access === 'Private'
                        ? (
                          <button type="button" className="card--event__button--register button--rounded is_private" disabled>
                            Private Event
                          </button>
                        )
                        : isLive
                          ? (
                            <button type="button" className="card--event__button--register button--rounded">
                              Watch Now
                              <i className="fas fa-angle-right" />
                            </button>
                          )
                          : (
                            <button type="button" className="card--event__button--register button--rounded">
                              Register Now
                              <i className="fas fa-angle-right" />
                            </button>
                          )}
                      <div className="card__text__more__container dropup">
                        <button type="button" className="card__text__more dropdown-toggle" data-bs-toggle="dropdown">
                          <i className="far fa-ellipsis-h"></i>
                        </button>
                        <div className="dropdown-menu dropdown-menu-end">
                          <button className="dropdown-item copy-text-button" type="button">
                            <i className="fas fa-link"></i>
                            Copy Link
                          </button>
                          <input type="text" value={row.url} className="copyText"></input>
                          <a className="dropdown-item" href={`https://twitter.com/share?text=${row.title}&amp;url=${row.url}`} target="_blank" rel="noopener noreferrer">
                            <i className="fab fa-twitter"></i>
                            Share on Twitter
                          </a>
                          <a className="dropdown-item" href={`https://www.linkedin.com/shareArticle?mini=true&amp;url=${row.url}&amp;title=${row.title}`} target="_blank" rel="noopener noreferrer">
                            <i className="fab fa-linkedin-in"></i>
                            Share on Linkedin
                          </a>
                          <a className="dropdown-item" data-url={row.url} target="_blank" rel="noopener noreferrer">
                            <i className="fab fa-facebook-f"></i>
                            Share on Facebook
                          </a>
                          <a className="dropdown-item" href={row.registration_url} onClick="ga('send', 'event', 'Event Registration', 'Click' );">
                            <i className="fal fa-check-square"></i>
                            Register
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-8 card__image__container">
              <div className="card__image">
                <a href={row.url} className="feature-content-image">
                  {
                    row.vimeo_url
                      ? (
                        <div className="video--wrapper">
                          <iframe src={row.vimeo_url}></iframe>
                        </div>
                      )
                      : row.image_src && (
                        <div className="img-wrapper">
                          <img alt={row.image_alt} src={`https://www.cigionline.org${row.image_src}`}></img>
                        </div>
                      )
                  }
                </a>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  );
};

export default FeaturedEventCard;
