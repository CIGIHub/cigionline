import React, { useState, useEffect, useCallback } from 'react';
import Calendar from 'react-calendar';
import 'bootstrap/dist/js/bootstrap.bundle';

function EventCalendar() {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEvents = useCallback((date) => {
    setEvents([]);
    setIsLoading(true);
    fetch(`/api/events/?month=${date.getMonth() + 1}&year=${date.getFullYear()}`)
      .then((res) => res.json())
      .then((res) => {
        setEvents(res.items);
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchEvents(new Date());
  }, [fetchEvents]);

  const filterEvents = useCallback((date) => events.filter((e) => {
    const eventDate = new Date(e.publishing_date);
    return eventDate.getDate() === date.getDate() && eventDate.getMonth() === date.getMonth();
  }), [events]);

  const showPopover = (e) => {
    $(e.target).popover();
    $(e.target).popover('show');
    $('.popover').on('mouseleave', function() {
      $(e.target).popover('hide');
    });
  };

  const hidePopover = (e) => {
    setTimeout(function() {
      if (!$('.popover:hover').length) {
        $(e.target).popover('hide');
      }
    }, 100);
  };

  const togglePopover = (e) => {
    $(e.target).popover();
    $(e.target).popover('toggle');
  };

  const tileContent = ({ date }) => {
    const eventsOnThisDate = filterEvents(date);
    if (!eventsOnThisDate.length) {
      return null;
    }
    const borderClass = eventsOnThisDate.length > 4 ? 5 : eventsOnThisDate.length + 1;
    const eventLinks = eventsOnThisDate.map((eventOnThisDate) => `<a href="${eventOnThisDate.url}">${eventOnThisDate.title}</a>`).join('');
    const popOverHtml = `<div class="react-calendar__tile__popover">${eventLinks}</div>`;
    return (
      <div
        className={`react-calendar__tile__overlay border-${borderClass}`}
        role="menuitem"
        aria-label="Events"
        tabIndex="0"
        onMouseEnter={showPopover}
        onMouseLeave={hidePopover}
        onClick={togglePopover}
        onKeyPress={togglePopover}
        data-container="body"
        data-toggle="popover"
        data-placement="bottom"
        data-html="true"
        data-content={popOverHtml}
        data-trigger="manual"
        data-animation="false"
      />
    );
  };

  const tileClassName = ({ date }) => {
    const eventsOnThisDate = filterEvents(date);
    if (eventsOnThisDate.length) {
      return 'react-calendar__tile--has-event';
    }
    return null;
  };

  const formatShortWeekday = (locale, date) => date.toLocaleString(locale, { weekday: 'narrow' });

  const onActiveStartDateChange = ({ activeStartDate }) => {
    fetchEvents(activeStartDate);
  };

  return (
    <div className="events-calendar">
      <Calendar
        calendarType="US"
        minDetail="month"
        maxDetail="month"
        nextLabel="››"
        prevLabel="‹‹"
        next2Label={null}
        prev2Label={null}
        formatShortWeekday={formatShortWeekday}
        onActiveStartDateChange={onActiveStartDateChange}
        tileContent={events.length ? tileContent : null}
        tileClassName={events.length ? tileClassName : null}
      />
      {isLoading && (
        <div className="events-calendar__loader">
          <img
            src="/static/assets/loader_spinner.gif"
            alt="Loading..."
            className="loading-spinner"
          />
        </div>
      )}
    </div>
  );
}

export default EventCalendar;
