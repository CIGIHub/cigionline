import React from 'react';

import PaginatorAlphabetical from './PaginatorAlphabetical';
import StaffListing from './StaffListing';
import StaffListingHeading from './StaffListingHeading';
import SearchTableSkeleton from './SearchTableSkeleton';

class StaffList extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      currentLetter: 'all',
      letters: {},
      loading: true,
      rows: [],
    };
  }

  componentDidMount() {
    this.getRows();
  }

  getRows() {
    const uri = '/api/staff/';

    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        const rows = data.items;
        const letters = {
          all: rows,
        };
        rows.forEach((row) => {
          const letter = row.last_name[0].toUpperCase();
          if (!(letter in letters)) {
            letters[letter] = [];
          }

          letters[letter].push(row);
        });

        this.setState(() => ({
          letters,
          loading: false,
          rows: data.items,
        }));
      });
  }

  setLetter(letter) {
    const { letters } = this.state;
    this.setState(() => ({
      currentLetter: letter,
      rows: letters[letter],
    }));
  }

  render() {
    const {
      rows,
      currentLetter,
      letters,
      loading,
    } = this.state;

    return (
      <div className="staff-list">
        {loading
          ? <SearchTableSkeleton />
          : (
            <>
              <PaginatorAlphabetical
                currentLetter={currentLetter}
                setLetter={(letter) => this.setLetter(letter)}
                letters={Object.keys(letters)}
              />
              <StaffListingHeading />
              {rows.map((row) => (
                <StaffListing key={row.id} row={row} />
              ))}
            </>
          )}
      </div>
    );
  }
}

export default StaffList;
