import React from 'react';

import Paginator from './Paginator';
import EventListingCard from './EventListingCard';

class EventListing extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      currentPage: 1,
      pages: [],
      pageCount: null,
      loading: true,
      rows: [],
    };
  }

  componentDidMount() {
    this.fetchEvents();
  }

  setPage(page) {
    const { pages } = this.state;
    this.setState(() => ({
      currentPage: page,
      rows: pages[page - 1],
    }));
  }

  fetchEvents() {
    const uri = '/api/all_events';
    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        const pages = data.meta.total_page_count;
        const rows = data.items;

        this.setState(() => ({
          rows: rows[0],
          pages: rows,
          pageCount: pages,
        }));
      });
  }

  render() {
    const { rows, currentPage, pageCount } = this.state;

    return (
      <>
        <div className="event-items">
          {rows &&
            rows.map((row) => <EventListingCard row={row} key={row.id} />)}
        </div>
        <Paginator
          currentPage={currentPage}
          setPage={(page) => this.setPage(page)}
          totalPages={pageCount}
        />
      </>
    );
  }
}

export default EventListing;
