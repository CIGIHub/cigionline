import React from 'react';

import Paginator from './Paginator';
import EventListingCard from './EventListingCard';

class EventListing extends React.Component {
  constructor(props) {
    super(props);
    const { meta, items } = props;

    this.state = {
      currentPage: 1,
      pages: items,
      pageCount: meta.total_page_count,
      loading: true,
      rows: items[0],
    };
  }

  setPage(page) {
    const { pages } = this.state;
    this.setState(() => ({
      currentPage: page,
      rows: pages[page - 1],
    }));
  }

  render() {
    const {
      rows, 
      currentPage,
      pageCount,
      pages,
      loading,
    } = this.state;

    return (
      <>
        <div className="event-items">
          {
            rows
              && rows.map((row) => (
                <EventListingCard row={row} key={row.id} />
              ))
          }
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
