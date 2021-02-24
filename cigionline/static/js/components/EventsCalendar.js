import PropTypes from 'prop-types';
import React from 'react';
import {
  format,
  addDays,
  addMonths,
  endOfMonth,
  endOfWeek,
  isSameDay,
  isSameMonth,
  subMonths,
  startOfWeek,
  startOfMonth,
} from 'date-fns';
import '../../css/components/EventsCalendar.scss';

class EventsCalendar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentMonth: new Date(),
      selectedDate: new Date(),
    };
  }

  nextMonth() {
    const { currentMonth } = this.state;
    this.setState({
      currentMonth: addMonths(currentMonth, 1),
    });
  }

  prevMonth() {
    const { currentMonth } = this.state;
    this.setState({
      currentMonth: subMonths(currentMonth, 1),
    });
  }

  renderDays() {
    const { currentMonth } = this.state;
    const dateFormat = 'EEEE';
    const days = [];
    const startDate = startOfWeek(currentMonth);

    for (let i = 0; i < 7; i += 1) {
      days.push(
        <div className="col col-center" key={i}>
          {format(addDays(startDate, i), dateFormat)}
        </div>,
      );
    }

    return <div className="days row">{days}</div>;
  }

  renderCells() {
    const { currentMonth, selectedDate } = this.state;
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);
    const dateFormat = 'd';
    const rows = [];
    let days = [];
    let day = startDate;
    let formattedDate = '';
    while (day <= endDate) {
      for (let i = 0; i < 7; i += 1) {
        formattedDate = format(day, dateFormat);
        const cloneDay = day;
        days.push(
          <div
            className={`col cell ${!isSameMonth(day, monthStart)
              ? 'disabled'
              : isSameDay(day, selectedDate) ? 'selected' : ''
            }`}
            key={day}
          >
            <span className="number">{formattedDate}</span>
            <span className="bg">{formattedDate}</span>
          </div>,
        );
        day = addDays(day, 1);
      }
      rows.push(
        <div className="row" key={day}>
          {days}
        </div>,
      );
      days = [];
    }

    return <div className="body">{rows}</div>;
  }

  render() {
    const dateFormat = 'MMMM yyyy';
    const { currentMonth } = this.state;

    return (
      <div>
        <div className="row">
          <div className="col">
            <button className="icon" type="button" onClick={this.prevMonth}>
              <i className="fa fa-chevron-left" />
            </button>
          </div>
          <div className="col">
            <span>
              {format(currentMonth, dateFormat)}
            </span>
          </div>
          <button className="col" type="button" onClick={this.nextMonth}>
            <i className="fa fa-chevron-right" />
          </button>
        </div>
        {this.renderDays()}
        {this.renderCells()}
      </div>
    );
  }
}

export default EventsCalendar;
