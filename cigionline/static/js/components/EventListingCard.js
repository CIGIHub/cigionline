import { DateTime } from 'luxon';
import React, { useState, useEffect } from 'react';
import ReactGA from 'react-ga';

import '../../css/components/EventListingCard.scss';

const EventListingCard = (props) => {
  const { row } = props;
  const startDate = DateTime.fromISO(row.start_time);
  const startDateTs = row.start_utc_ts * 1000;
  const startDayDayOfWeek = startDate.weekdayLong;
  const startDateDay = startDate.day;
  const startDateMonth = startDate.monthLong;
  const startDateYear = startDate.year;
  const startDateHour = startDate.hour > 12 ? startDate.hour - 12 : startDate.hour;
  const startDateMinute = startDate.minute;
  const startDateAmPm = startDate.toFormat('a');
  const endDate = DateTime.fromISO(row.end_time) || null;
  const endDateTs = row.end_utc_ts * 1000;
  const endDateHour = endDate.hour > 12 ? endDate.hour - 12 : endDate.hour;
  const endDateMinute = endDate.minute;
  const endDateAmPm = endDate.toFormat('a');

  const evaluateLive = (start, end) => {
    return Date.now() >= start && Date.now() <= end;
  };
  const [isLive, setIsLive] = useState(evaluateLive(startDateTs, endDateTs));

  useEffect(() => {
    const interval = setInterval(() => {
      setIsLive(evaluateLive(startDateTs, endDateTs));
    }, 1000);
    return () => {
      clearInterval(interval);
    };
  }, [isLive]);

  const handleClick = () => {
    ReactGA.event({
      category: 'Button',
      action: 'Click',
      label: 'Event Registration',
    });
  };

  return (
    <div className="col col-12 col-md-8">
      <article className={`card__container card--medium card--medium--event card--event ${row.event_access === 'Private' && 'is_private'}`}>
        <div className="row card--event__top">
          <div className="col-md-8">
            {Date.now() < startDateTs && (
              <div className="card--event--upcoming-label">
                Upcoming Event -
                {' '}
                {`${startDateMonth} ${startDateDay}`}
              </div>
            )}
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
                <div>{`${startDayDayOfWeek}, ${startDateMonth} ${startDateDay}, ${startDateYear}`}</div>
                <div>
                  {`${startDateHour}:${startDateMinute} ${startDateAmPm}`}
                  {endDate && ` - ${endDateHour}:${endDateMinute} ${endDateAmPm}`}
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
            <div className="card--event__date">{startDateDay}</div>
            <div className="card--event__month">{startDateMonth}</div>
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
                  {row.event_access !== 'Private' && row.registration_url && (
                    <a className="dropdown-item" href={row.registration_url} onClick={handleClick}>
                      <i className="fal fa-check-square"></i>
                      Register
                    </a>
                  )}
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
                : Date.now() < startDateTs && (
                  <a className="card--event__button--register button--rounded" onClick={handleClick}>
                    Register Now
                    <i className="fas fa-angle-right" />
                  </a>
                )
            }
          </div>
        </div>
      </article>
    </div>
  );
};

export default EventListingCard;
