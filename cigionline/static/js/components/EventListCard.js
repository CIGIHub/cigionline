import React from 'react';

const EventListCard = (props) => {
  const { row } = props;
  return (
    <div className="col col-12 col-md-8">
      <article className="card__container card--medium card--medium--event card--event { event_access == 'Private' }is_private">
        <div className="row card--event__top">
          <div className="col-md-8">
            <div className="card--event--upcoming-label">Upcoming Event</div>
            {% include 'includes/cards/card_text_title.html' with additional_classes='card--event__title' %}
            <div className="card--event__info">
              <time datetime="" className="card--event__time">
                <div>{ row.date }</div>
                <div>
                  { row.date }
                  { end_date && end_date !== null && (
                    - 
                  )
                    
                  }
                    { row.date < row.end_date }
                    { row.date === row.end_date }
                        { row.end_date }
                    { else }
                        { end_date|date:"l, F j, Y g:i A" }
                  {{ time_zone_label }}
                </div>
              </time>
              <div className="card--event__type">
                {{ event_access }} 
                Even{ if event_type|length > 1 }: {{ event_type }{ endif }
                {{ event_format }}
              </div>
            </div>
          </div>
          <div className="d-none d-md-block col-md-4 card--event__calendar-date">
            <div className="card--event__date">{{ date|date:"j" }}</div>
            <div className="card--event__month">{{ date|date:"F" }}</div>
          </div>
        </div>
        <div className="row g-3 g-md-5 card--event__bottom">
          <div className="col-md-6 d-flex align-items-end">
            <div className="card__text__meta">
              <div>
              { include 'includes/cards/card_text_people.html' }
              { include 'includes/cards/card_text_topics.html' }
              </div>
            { include 'includes/cards/card_text_more.html' with type='event' }
            </div>
          </div>
          <div className="col-md-6 text-center">
          { if event_access == 'Private' }
              <button type="button" className="card--event__button--register button--rounded is_private" disabled>
                Private Event
              </button>
          { else }
              <a href="{{ registration_url }}" onclick="ga('send', 'event', 'Event Registration', 'Click' );">
                <button type="button" className="card--event__button--register button--rounded">
                  Register Now
                  <i className="fas fa-angle-right"></i>
                </button>
              </a>
          { endif }
          </div>
        </div>
    </div>
  );
}

export default EventListCard;
