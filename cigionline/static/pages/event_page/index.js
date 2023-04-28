import React from 'react';
import ReactDOM from 'react-dom';

import EventListingCard from '../../js/components/EventListingCard';

import './css/event_page.scss';

const eventData = JSON.parse(
  document.getElementById('event-data').dataset.eventData,
);
console.log(eventData);

ReactDOM.render(
  <EventListingCard row={eventData} key={eventData.id} />,
  document.getElementById('event-card'),
);
