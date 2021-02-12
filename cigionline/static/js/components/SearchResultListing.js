import PropTypes from 'prop-types';
import React from 'react';

function SearchResultListing(props) {
  const { row } = props;

  return (
    <div>
      {row.title}
    </div>
  );
}

SearchResultListing.propTypes = {
  row: PropTypes.shape({
    title: PropTypes.string,
  }).isRequired,
};

export default SearchResultListing;
