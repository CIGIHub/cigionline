import { DateTime } from 'luxon';
import React, { useState, useEffect } from 'react';
import ReactGA from 'react-ga';

const FeaturedEventCard = (props) => {
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

  return (
    <div className="swiper-slide">
      <div className="col col-12">
        <article className={`card__container card--large card--large--event--landing card--event ${row.event_access === 'Private' && 'is_private'}`}>
          <div className="row card--event__container">
            <div className="col-md-4">
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
                <div className="card--event__bottom">
                  <div className="card__text__meta">
                    <div className="card__text__meta__left">
                      <div className="card__cta">
                        {row.event_access === 'Private'
                          ? (
                            <button type="button" className="card--event__button--register button--rounded is_private" disabled>
                              Private Event
                            </button>
                          )
                          : (Date.now() < startDateTs) && !isLive
                            ? (
                              <a className="card--event__button--register button--rounded" href={row.registration_url} onClick={handleClick}>
                                Register Now
                                <i className="fas fa-angle-right" />
                              </a>
                            )
                            : isLive && (row.livestream_url !== '')
                              ? (
                                <a className="card--event__button--register button--rounded" href={row.livestream_url}>
                                  Watch Now
                                  <i className="fas fa-angle-right" />
                                </a>
                              )
                              : row.vimeo_url !== '' && (
                                <a className="card--event__button--register button--rounded" href={row.vimeo_url}>
                                  Watch Now
                                  <i className="fas fa-angle-right" />
                                </a>
                              )}
                      </div>
                      {row.authors.length > 0 && (
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
                      )}
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
                        <a className="dropdown-item" href={`https://twitter.com/share?text=${row.title}&url=${row.url}`} target="_blank" rel="noopener noreferrer">
                          <i className="fab fa-twitter"></i>
                          Share on Twitter
                        </a>
                        <a className="dropdown-item" href={`https://www.linkedin.com/shareArticle?mini=true&url=${row.url}&title=${row.title}`} target="_blank" rel="noopener noreferrer">
                          <i className="fab fa-linkedin-in"></i>
                          Share on Linkedin
                        </a>
                        <a className="dropdown-item" data-url={row.url} target="_blank" rel="noopener noreferrer">
                          <i className="fab fa-facebook-f"></i>
                          Share on Facebook
                        </a>
                        {row.event_access !== 'Private' && Date.now() < startDateTs && !isLive && (
                          <a class="dropdown-item" href={`/events/feed.ics?id=${row.id}`}>
                            <i class="fas fa-plus"></i>
                            Add to Calendar
                          </a>
                        )}
                        {row.event_access !== 'Private' && row.registration_url && Date.now() < startDateTs && !isLive && (
                          <a className="dropdown-item" href={row.registration_url} onClick={handleClick}>
                            <i className="fal fa-check-square"></i>
                            Register
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-8 card__image__container">
              <div className="card__image">
                <a href={row.url} className="feature-content-image">
                  {row.livestream_url
                    ? (
                      <div className="video--wrapper">
                        <iframe src={livestreamUrl(row.livestream_url)}></iframe>
                      </div>
                    )
                    : row.vimeo_url
                      ? (
                        <div className="video--wrapper">
                          <iframe src={embedUrl(row.vimeo_url)}></iframe>
                        </div>
                      )
                      : row.image_hero_url && (
                        <div className="img-wrapper">
                          <img alt="" src={row.image_hero_url}></img>
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

export default FeaturedEventCard;
