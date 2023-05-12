import React from 'react';
import Calendar from 'react-calendar';
import Popover from 'bootstrap/js/dist/popover';
// import 'bootstrap/dist/js/bootstrap.bundle';

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
   * Render popover if a date has event.
   * */
  tileContent = ({ date }) => {
    const eventsOnThisDate = this.filterEvents(date);
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
        onMouseEnter={this.showPopover}
        onMouseLeave={this.hidePopover}
        onClick={this.togglePopover}
        onKeyPress={this.togglePopover}
        data-container="body"
        data-bs-toggle="popover"
        data-bs-placement="bottom"
        data-bs-html="true"
        data-bs-content={popOverHtml}
        data-bs-trigger="manual"
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
    console.log(e.target)
    const popOver = new Popover(e.target);
    popOver.show();
    e.addeventlistener('mouseleave', () => {
      popOver.hide();
    });
    // $(e.target).popover();
    // $(e.target).popover('show');
    // $('.popover').on('mouseleave', function() {
    //   $(e.target).popover('hide');
    // });
  }

  hidePopover = (e) => {
    setTimeout(function() {
      if (!$('.popover:hover').length) {
        $(e.target).popover('hide');
      }
    }, 100);
  }

  // Toggle popover for mobile devices
  togglePopover = (e) => {
    $(e.target).popover();
    $(e.target).popover('toggle');
  }

  tileClassName = ({ date }) => {
    const eventsOnThisDate = this.filterEvents(date);
    if (eventsOnThisDate.length) {
      return 'react-calendar__tile--has-event';
    }
    return null;
  }

  /**
   * Format weekdays to their initials.
   * E.g. Sunday -> S
   * */
  formatShortWeekday = (locale, date) => date.toLocaleString(locale, { weekday: 'narrow' })

  onActiveStartDateChange = ({ activeStartDate }) => {
    this.fetchEvents(activeStartDate);
  }

  /**
   * Filter event by date
   * @param {Date} date
   * @returns {Object|undefined}
   * */
  filterEvents(date) {
    const { events } = this.state;
    return events.filter((e) => {
      const eventDate = new Date(e.publishing_date);
      return eventDate.getDate() === date.getDate() && eventDate.getMonth() === date.getMonth();
    });
  }

  render() {
    // Remount tile renderers when events change.
    // This ensures that the events are displayed on calendar even if
    // it loads after the calendar renders.
    const { events, isLoading } = this.state;
    const tileContent = events.length ? this.tileContent : null;
    const tileClassName = events.length ? this.tileClassName : null;
    return (
      <div className="events-calendar">
        <Calendar
          calendarType="US"
          minDetail="month"
          maxDetail="month"
          nextLabel="›"
          prevLabel="‹"
          next2Label={null}
          prev2Label={null}
          formatShortWeekday={this.formatShortWeekday}
          onActiveStartDateChange={this.onActiveStartDateChange}
          tileContent={tileContent}
          tileClassName={tileClassName}
        />
        {isLoading
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
