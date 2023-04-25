import { DateTime } from 'luxon';
import React, { useState, useEffect } from 'react';

import '../../css/components/EventListingCard.scss';

const EventListingCard = (props) => {
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
    <div className="col col-12 col-md-8">
      {/* <div>
        Current Time: {Date().toLocaleString()}
        start time: {row.time}
        end time: {row.end_time}
      </div> */}
      <article className={`card__container card--medium card--medium--event card--event ${row.event_access === 'Private' && 'is_private'}`}>
        <div className="row card--event__top">
          <div className="col-md-8">
            {today < row.date && (
              <div className="card--event--upcoming-label">
                Upcoming Event -
                {' '}
                {row.date}
              </div>
            )}
            {
              isLive
                ? (
                  <div className="card__text__title card--event__title card--event--live-label">
                    <i className="fas fa-podcast"></i>
                    <a href={row.url}>{row.title}</a>
                  </div>
                )
                : (
                  <h3 className="card__text__title card--event__title">
                    <a href={row.url}>{row.title}</a>
                  </h3>
                )
            }
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
          <div className="d-none d-md-block col-md-4 card--event__calendar-date">
            <div className="card--event__date">{row.date_singular}</div>
            <div className="card--event__month">{row.month}</div>
          </div>
        </div>
        <div className="row g-3 g-md-5 card--event__bottom">
          <div className="col-md-6 d-flex align-items-end">
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
          <div className="col-md-6 text-center">
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
                )
            }
          </div>
        </div>
      </article>
    </div>
  );
};

export default EventListingCard;
