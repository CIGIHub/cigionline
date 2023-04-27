import { DateTime } from 'luxon';
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import '../../css/components/EventSearchResultCard.scss';

const EventSearchResultCard = (props) => {
  const { row } = props;
  const today = DateTime.now();
  const startDate = DateTime.fromISO(row.publishing_date);
  const startDateTs = row.event_start_time_utc_ts * 1000;
  const startDayDayOfWeek = startDate.weekdayLong;
  const startDateDay = startDate.day;
  const startDateMonth = startDate.monthLong;
  const startDateYear = startDate.year;
  const startDateHour = startDate.hour > 12 ? startDate.hour - 12 : startDate.hour;
  const startDateAmPm = startDate.toFormat('a');
  const endDate = DateTime.fromISO(row.event_end) || null;
  const endDateTs = row.event_end_time_utc_ts * 1000 || null;
  const endDateHour = endDate.hour > 12 ? endDate.hour - 12 : endDate.hour;
  const endDateAmPm = endDate.toFormat('a');

  const evaluateLive = (start, end) => {
    return today >= start && today <= end;
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

  return (
    <article className={`card__container card--small card--small--event card--event ${!row.event_access === 'Private' && 'is_private'}`}>
      <div className="card--event--small__top">
        <div className="card--event__title card__text__title">
          {today < startDateTs && (
            <div className="card--event--upcoming-label">
              Upcoming Event -
              {' '}
              {`${startDateMonth} ${startDateDay}`}
            </div>
          )}
          {
            isLive
              ? (
                <h3 className="card--event--live-label">
                  <i className="fas fa-podcast"></i>
                  <a href={row.url}>{row.title}</a>
                </h3>
              )
              : (
                <h3>
                  <a href={row.url}>{row.title}</a>
                </h3>
              )
          }
        </div>
        <div className="card--event__info">
          <time dateTime="" className="card--event__time">
            <div>{`${startDayDayOfWeek}, ${startDateMonth} ${startDateDay}, ${startDateYear}`}</div>
            <div>
              {`${startDateHour} ${startDateAmPm}`}
              {endDate && ` - ${endDateHour} ${endDateAmPm}`}
              {' '}
              {row.time_zone_label}
            </div>
          </time>
          <div className="card--event__type">
            {row.event_access ? 'Public ' : 'Private '}
            Event
            {row.contentsubtype && (
              <span>
                :
                {' '}
                {row.contentsubtype}
              </span>
            )}
            {row.event_format_string && (
              <span>
                {' '}
                (
                {row.event_format_string}
                )
              </span>
            )}
          </div>
        </div>
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
        <div className="card__text__more__container dropup">
          <button type="button" className="card__text__more dropdown-toggle" data-bs-toggle="dropdown">
            <i className="far fa-ellipsis-h" />
          </button>
          <div className="dropdown-menu dropdown-menu-end">
            <button className="dropdown-item copy-text-button" type="button">
              <i className="fas fa-link" />
              Copy Link
            </button>
            <input type="text" value={row.url} className="copyText" />
            <a className="dropdown-item" href={`https://twitter.com/share?text=${row.title}&amp;url=${row.url}`} target="_blank" rel="noopener noreferrer">
              <i className="fab fa-twitter" />
              Share on Twitter
            </a>
            <a className="dropdown-item" href={`https://www.linkedin.com/shareArticle?mini=true&amp;url=${row.url}&amp;title=${row.title}`} target="_blank" rel="noopener noreferrer">
              <i className="fab fa-linkedin-in" />
              Share on Linkedin
            </a>
            <button className="dropdown-item" type="button" data-url={row.url} target="_blank" rel="noopener noreferrer">
              <i className="fab fa-facebook-f" />
              Share on Facebook
            </button>
            {row.event_access !== 'Private' && (
              <a className="dropdown-item" href={row.registration_url} onClick="ga('send', 'event', 'Event Registration', 'Click' );">
                <i className="fal fa-check-square" />
                Register
              </a>
            )}
          </div>
        </div>
      </div>
    </article>
  );
};

EventSearchResultCard.propTypes = {
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
    event_access: PropTypes.string,
    event_end: PropTypes.string,
    event_type: PropTypes.string,
    event_format_string: PropTypes.string,
    registration_url: PropTypes.string,
    time_zone_label: PropTypes.string,
  }).isRequired,
};

export default EventSearchResultCard;
