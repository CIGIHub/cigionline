import { DateTime } from 'luxon';
import React from 'react';
import PropTypes from 'prop-types';

import '../../css/components/EventSearchResultCard.scss';

const EventSearchResultCard = (props) => {
  const { row } = props;
  const today = DateTime.now();
  const startDate = DateTime.fromISO(row.publishing_date);
  const startDayDayOfWeek = startDate.weekdayLong;
  const startDateDay = startDate.day;
  const startDateMonth = startDate.monthLong;
  const startDateYear = startDate.year;
  const startDateHour = startDate.hour > 12 ? startDate.hour - 12 : startDate.hour;
  const startDateAmPm = startDate.toFormat('a');
  const endDate = DateTime.fromISO(row.event_end) || null;
  const endDateHour = endDate.hour;
  const endDateAmPm = endDate.toFormat('a');

  return (
    <article className={`card__container card--small card--small--event card--event ${!row.event_access && 'is_private'}`}>
      <div className="card--event--small__top">
        {today < startDate && (
          <div className="card--event--upcoming-label">
            Upcoming Event -
            {' '}
            {`${startDateMonth} ${startDateDay}`}
          </div>
        )}
        <h3 className="card--event__title card__text__title">
          <a href={row.url}>{row.title}</a>
        </h3>
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
    time_zone_label: PropTypes.string,
  }).isRequired,
};

export default EventSearchResultCard;
