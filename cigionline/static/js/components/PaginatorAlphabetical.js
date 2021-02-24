import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/PaginatorAlphabetical.scss';

function PaginatorAlphabetical(props) {
  const { currentLetter, setLetter, letters } = props;

  return (
    <div className="pagination-links-alphabetical">
      {letters && letters.map((letter) => (
        letter === currentLetter ? (
          <li key={`letter-${letter}`} className="pagination-inactive">
            {letter === 'all' ? 'Show All' : letter}
          </li>
        ) : (
          <li key={`letter-${letter}`}>
            <button type="button" onClick={() => setLetter(letter)}>
              {letter === 'all' ? 'Show All' : letter}
            </button>
          </li>
        )
      ))}
    </div>
  );
}

PaginatorAlphabetical.propTypes = {
  currentLetter: PropTypes.string.isRequired,
  setLetter: PropTypes.func.isRequired,
  letters: PropTypes.array.isRequired,
};

export default PaginatorAlphabetical;
