import { DateTime } from 'luxon';
import React, { useState, useEffect } from 'react';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types';
import CardTextMore from './CardTextMore';

const FeaturedEventCard = (props) => {
  const { row } = props;
  const startDate = DateTime.fromISO(row.start_time);
  const startDateTs = row.start_utc_ts * 1000;
  const startDayDayOfWeek = startDate.weekdayLong;
  const startDateDay = startDate.day;
  const startDateMonth = startDate.monthLong;
  const startDateYear = startDate.year;
  const startDateHour = startDate.hour > 12 ? startDate.hour - 12 : startDate.hour;
  const startDateMinute = startDate.minute.toString().padStart(2, '0');
  const startDateAmPm = startDate.toFormat('a');
  const endDate = DateTime.fromISO(row.end_time) || null;
  const endDateTs = row.end_utc_ts * 1000;
  const endDateHour = endDate.hour > 12 ? endDate.hour - 12 : endDate.hour;
  const endDateMinute = endDate.minute.toString().padStart(2, '0');
  const endDateAmPm = endDate.toFormat('a');

  function embedUrl(str) {
    if (str.substr(-1) === '/') {
      str = str.substr(0, str.length - 1);
    }
    const splitArr = str.split('/');
    return 'https://player.vimeo.com/video/'.concat(splitArr[splitArr.length - 2], '?h=', splitArr[splitArr.length - 1], '&amp;app_id=122963');
  }

  function livestreamUrl(str) {
    if (str.includes('/event/')) {
      if (str.substr(-1) === '/') {
        str = str.substr(0, str.length - 1);
      }
      const lastIndex = str.lastIndexOf('/');
      return str.substr(0, lastIndex).concat('/embed', str.substr(lastIndex));
    }
    return embedUrl(str);
  }

  const evaluateLive = (start, end) => Date.now() >= start && Date.now() <= end;
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

  const videoPageUrl = isLive && row.livestream_url
    ? row.url
    : row.vimeo_url
      ? row.mm_page_url
      : row.livestream_url
        ? row.url
        : null;

  return (
    <div className="swiper-slide">
      <div className="col col-12">
        <article className={`card__container card--large card--large--event--landing card--event ${row.event_access === 'Private' && 'is_private'}`}>
          <div className="row card--event__container">
            <div className="col-lg-4">
              <div className="card__text">
                <div className="row card--event__top">
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
                          <i className="fas fa-podcast" />
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
                      {row.event_access === 'Public' ? 'Public ' : 'Private '}
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
                    <div className="card__text__meta__left card__text__bottom">
                      <div className="card__cta">
                        {(Date.now() < startDateTs) && !isLive
                          ? (row.event_access === 'Private'
                            ? (
                              <button type="button" className="card--event__button--register cta__button is_private" disabled>
                                Private Event
                              </button>
                            )
                            : row.registration_url && (
                              <a className="card--event__button--register cta__button" href={row.registration_url} onClick={handleClick}>
                                Register Now
                                <i className="fas fa-angle-right" />
                              </a>
                            ))
                          : (videoPageUrl
                            ? (
                              <a className="card--event__button--register cta__button" href={videoPageUrl}>
                                Watch Now
                                <i className="fas fa-angle-right" />
                              </a>
                            )
                            : (row.event_access === 'Private' && (
                              <button type="button" className="card--event__button--register cta__button is_private" disabled>
                                Private Event
                              </button>
                            )))}
                      </div>
                      {row.authors.length > 0 && (
                        <ul className="custom-text-list card__text__people">
                          {row.authors.slice(0, 3).map((author) => (
                            <li key={`${row.id}-author-${author.id}`}>
                              <a href={author.url}>{author.title}</a>
                            </li>
                          ))}
                          {row.authors.length > 3 && (
                            <li key={`${row.id}-author-more`}>and more</li>
                          )}
                        </ul>
                      )}
                    </div>
                    <CardTextMore
                      title={row.title}
                      url={row.url}
                      type="Event"
                      registrationUrl={row.registration_url}
                      eventAccess={row.event_access}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="col-lg-8 card__image__container">
              <div className="card__image">
                <a href={row.url} className="feature-content-image">
                  {row.vimeo_url
                    ? (
                      <div className="video--wrapper">
                        <iframe src={embedUrl(row.vimeo_url)} title={row.title} />
                      </div>
                    )
                    : row.livestream_url
                      ? (
                        <div className="video--wrapper">
                          <iframe src={livestreamUrl(row.livestream_url)} title={row.title} />
                        </div>
                      )
                      : row.image_hero_url && (
                        <div className="img-wrapper">
                          <img alt="" src={row.image_hero_url} />
                        </div>
                      )}
                </a>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  );
};

FeaturedEventCard.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    event_access: PropTypes.string,
    event_format: PropTypes.string,
    event_type: PropTypes.string,
    id: PropTypes.number,
    image_hero_url: PropTypes.string,
    livestream_url: PropTypes.string,
    mm_page_url: PropTypes.string,
    registration_url: PropTypes.string,
    time_zone_label: PropTypes.string,
    title: PropTypes.string,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string,
    vimeo_url: PropTypes.string,
  }).isRequired,
};

export default FeaturedEventCard;
