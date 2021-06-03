import React from 'react';
import Calendar from 'react-calendar';
import 'bootstrap/dist/js/bootstrap.bundle';

export default class EventCalendar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      events: [
        // { title: 'Event Name', url: '/url/for/event/', publishing_date: '2021-01-01T00:00:00' }]
      ],
      isLoading: true,
    };
  }

  componentDidMount() {
    // fetch events for current month.
    this.fetchEvents(new Date());
  }

  /**
     * Get event by date
     * @param {Date} date
     * @returns {Object|undefined}
     * */
  getEvent(date) {
    return this.state.events.find((e) => {
      const eventDate = new Date(e.publishing_date);
      return eventDate.getDate() === date.getDate() && eventDate.getMonth() === date.getMonth();
    });
  }

    /**
     * Render popover if a date has event.
     * */
    tileContent = ({ date }) => {
      const eventOnThisDate = this.getEvent(date);
      if (!eventOnThisDate) {
        return null;
      }
      const popOverHtml = `<a href="${eventOnThisDate.url}">${eventOnThisDate.title}</a>`;
      return (
        <div
          className="react-calendar__tile__overlay"
          onMouseEnter={this.showPopover}
          onMouseLeave={this.hidePopover}
          onClick={this.togglePopover}
          data-container="body"
          data-toggle="popover"
          data-placement="bottom"
          data-html="true"
          data-content={popOverHtml}
          data-trigger="manual"
          data-animation="false"
        />
      );
    }

    fetchEvents = (date) => {
      this.setState({ events: [], isLoading: true });
      fetch(`/api/events/?month=${date.getMonth() + 1}&year=${date.getFullYear()}`)
        .then((res) => res.json())
        .then((res) => {
          this.setState({ events: res.items, isLoading: false });
        });
    }

    // Prevent popover from abruptly closing when user tries to hover on the event link.
    showPopover = (e) => {
      $(e.target).popover();
      $(e.target).popover('show');
      $('.popover').on('mouseleave', function() {
        $(e.target).popover('hide');
      });
    }

    hidePopover = (e) => {
      setTimeout(function() {
        if (!$('.popover:hover').length) {
          $(e.target).popover('hide');
        }
      }, 500);
    }

    // Toggle popover for mobile devices
    togglePopover = (e) => {
      $(e.target).popover();
      $(e.target).popover('toggle');
    }

    tileClassName = ({ date }) => {
      const eventOnThisDate = this.getEvent(date);
      if (eventOnThisDate) {
        return 'react-calendar__tile--has-event';
      }
    }

    /**
     * Format weekdays to their initials.
     * E.g. Sunday -> S
     * */
    formatShortWeekday = (locale, date) => date.toLocaleString(locale, { weekday: 'narrow' })

    onActiveStartDateChange = ({ activeStartDate }) => {
      this.fetchEvents(activeStartDate);
    }

    render() {
      // Remount tile renderers when events change.
      // This ensures that the events are displayed on calendar even if
      // it loads after the calendar renders.
      const tileContent = this.state.events.length ? this.tileContent : null;
      const tileClassName = this.state.events.length ? this.tileClassName : null;
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
            formatShortWeekday={this.formatShortWeekday}
            onActiveStartDateChange={this.onActiveStartDateChange}
            tileContent={tileContent}
            tileClassName={tileClassName}
          />
          {this.state.isLoading
            ? (
              <div className="events-calendar__loader">
                <img
                  src="/static/assets/loader_spinner.gif"
                  alt="Loading..."
                  className="loading-spinner"
                />
              </div>
            )
            : null}
        </div>
      );
    }
}
