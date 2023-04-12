import React from 'react';
import FeaturedEventCard from './FeaturedEventCard';

function FeaturedEventListing(props) {
  const { meta, items } = props;

  return (
    <>
      {
        items
          && items.map((row) => (
            <FeaturedEventCard row={row} key={row.id} />
          ))
      }
    </>
  );
}

export default FeaturedEventListing;
